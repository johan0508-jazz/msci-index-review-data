#!/usr/bin/env python3
"""Parse MSCI Global Standard/Small Cap public list PDFs for USA/Taiwan changes.

Outputs machine-readable event dicts plus flat audit tables. Ticker mapping is deliberately
conservative: keep MSCI company_name and mapped ticker in separate columns with source/status.
"""
from __future__ import annotations

import csv
import json
import re
import ssl
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "pdf"
OUT_DIR = ROOT / "parsed"
REPORT_DIR = ROOT / "reports"
OUT_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

PRODUCTS = {
    "standard": PDF_DIR / "stdindex",
    "small_cap": PDF_DIR / "smallcap",
}
COUNTRIES = {"USA": "MSCI USA INDEX", "TAIWAN": "MSCI TAIWAN INDEX"}
MONTHS = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}
MONTH_FULL = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1)}
STOP_RE = re.compile(r"^MSCI .+ INDEX$")
FOOTER_RE = re.compile(r"^(Page \d+|Notice and Disclaimer|•|©|Copyright|About MSCI|MSCI Standard Index Series|MSCI Global|Geneva,|This information|Morgan Stanley|The Information)")

CORP_WORDS = {
    "INC", "INCORPORATED", "CORP", "CORPORATION", "CO", "COMPANY", "LTD", "LIMITED", "PLC", "SA", "NV",
    "GROUP", "HOLDINGS", "HOLDING", "THE", "COMMON", "STOCK", "CLASS", "CL", "ORD", "NEW", "COM", "LP",
}
CLASS_WORDS = {"A", "B", "C"}
REF_INDEXES: dict[int, dict[str, list[int]]] = {}
REF_EXACT: dict[int, dict[str, int]] = {}
YAHOO_CACHE: dict[str, list[dict[str, Any]]] = {}


def http_json(url: str, *, user_agent: str = "MSCI research data prep", insecure: bool = False) -> Any:
    ctx = ssl._create_unverified_context() if insecure else None
    req = Request(url, headers={"User-Agent": user_agent, "Accept": "application/json,text/plain,*/*"})
    with urlopen(req, timeout=30, context=ctx) as r:
        return json.loads(r.read().decode("utf-8-sig"))


def parse_date_line(text: str) -> tuple[str | None, str | None]:
    # Geneva, May 12, 2026 / close of May 29, 2026
    issue = None
    effective = None
    m = re.search(r"Geneva,\s+([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})", text)
    if m:
        issue = datetime(int(m.group(3)), MONTH_FULL[m.group(1)], int(m.group(2))).date().isoformat()
    m = re.search(r"close of\s+([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})", text)
    if m:
        effective = datetime(int(m.group(3)), MONTH_FULL[m.group(1)], int(m.group(2))).date().isoformat()
    return issue, effective


def pdf_review_key(path: Path) -> str:
    m = re.search(r"MSCI_([A-Za-z]{3})(\d{2})_", path.name)
    if not m:
        return path.stem
    yy = int(m.group(2))
    year = 2000 + yy if yy < 80 else 1900 + yy
    return f"{year}-{MONTHS[m.group(1)]:02d}"


def extract_text(path: Path) -> str:
    # layout mode is important for older MSCI PDFs: normal extraction collapses the
    # two Additions/Deletions columns into ambiguous single-space strings.
    return "\n".join(page.extract_text(extraction_mode="layout") or "" for page in PdfReader(str(path)).pages)


def split_row(line: str) -> tuple[str, str]:
    if not line.strip() or line.strip() in {"None", "Additions                               Deletions", "Additions Deletions"}:
        return "", ""
    # Layout extraction preserves columns but all rows may be indented. Split first.
    parts = [p.strip() for p in re.split(r"[\s\u00a0]{2,}", line.rstrip()) if p.strip()]
    if len(parts) >= 2:
        left, right = parts[0], parts[-1]
    elif line.startswith(" ") and len(line) > 35:
        left, right = "", line.strip()
    else:
        left, right = line.strip(), ""
    if left == "None":
        left = ""
    if right == "None":
        right = ""
    if left.endswith(" None"):
        left = left[:-5].strip()
    if right.endswith(" None"):
        right = right[:-5].strip()
    return left, right


def parse_country_section(text: str, country: str) -> tuple[list[str], list[str]]:
    header = COUNTRIES[country]
    pos = text.find(header)
    if pos < 0:
        return [], []
    lines = text[pos:].splitlines()[1:]
    adds, dels = [], []
    in_table = False
    for line in lines:
        raw = line.rstrip("\n")
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("Additions"):
            in_table = True
            continue
        if in_table and STOP_RE.match(stripped):
            break
        if not in_table:
            continue
        if FOOTER_RE.match(stripped):
            # Once we are inside a target country table, disclaimer/footer text means the table is over.
            if any(x in stripped for x in ["Notice", "Copyright", "This information", "The Information", "About MSCI"]):
                break
            continue
        # MSCI constituent names in these PDFs are uppercase; mixed-case prose is disclaimer text.
        if stripped in {"ASIA PACIFIC", "AMERICAS", "EUROPE, MIDDLE EAST AND AFRICA"}:
            break
        if re.search(r"[a-z]", stripped) or stripped in {"", "•"}:
            break
        left, right = split_row(raw)
        if left and left != "None":
            adds.append(left)
        if right and right != "None":
            dels.append(right)
    return adds, dels


def normalize_name(s: str) -> str:
    s = s.upper()
    s = s.replace("&", " AND ")
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"[^A-Z0-9 ]+", " ", s)
    words = [w for w in s.split() if w not in CORP_WORDS]
    # Drop terminal share-class shorthand only after keeping it available in raw name.
    if len(words) > 1 and words[-1] in CLASS_WORDS:
        words = words[:-1]
    return " ".join(words)


def ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()


def load_us_reference() -> pd.DataFrame:
    rows = []
    try:
        sec = http_json("https://www.sec.gov/files/company_tickers_exchange.json")
        fields = sec["fields"]
        for rec in sec["data"]:
            d = dict(zip(fields, rec))
            rows.append({"ticker": d["ticker"], "name": d["name"], "exchange": d.get("exchange"), "source": "SEC company_tickers_exchange"})
    except Exception as e:
        print(f"WARN SEC reference failed: {e}", file=sys.stderr)
    # NasdaqTrader has broader active symbol names. SSL verification can fail on macOS Python, so use unverified context.
    for url, source in [
        ("https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt", "NasdaqTrader nasdaqlisted"),
        ("https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt", "NasdaqTrader otherlisted"),
    ]:
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0 Johan MSCI research"})
            with urlopen(req, timeout=30, context=ssl._create_unverified_context()) as r:
                text = r.read().decode("utf-8", errors="replace")
            reader = csv.DictReader(text.splitlines(), delimiter="|")
            for rec in reader:
                if rec.get("Test Issue") == "Y" or rec.get("Symbol") == "File Creation Time":
                    continue
                sym = rec.get("Symbol") or rec.get("ACT Symbol")
                name = rec.get("Security Name") or rec.get("Security Name")
                exch = rec.get("Listing Exchange") or rec.get("Exchange")
                if sym and name:
                    rows.append({"ticker": sym, "name": name, "exchange": exch, "source": source})
        except Exception as e:
            print(f"WARN {source} failed: {e}", file=sys.stderr)
    df = pd.DataFrame(rows).drop_duplicates(subset=["ticker", "name"])
    df["norm"] = df["name"].map(normalize_name)
    return df


def load_taiwan_reference() -> pd.DataFrame:
    rows = []
    # Local FinLab company table gives stable ticker universe and Chinese names.
    local = Path("/Users/johan/Documents/invest/tw_data/finlab/company_basic_info.pickle")
    if local.exists():
        try:
            df = pd.read_pickle(local)
            for _, r in df.iterrows():
                ticker = str(r.get("stock_id", "")).strip()
                if not ticker or ticker == "nan":
                    continue
                for col in ["公司簡稱", "公司名稱", "英文簡稱"]:
                    val = str(r.get(col, "")).strip()
                    if val and val != "nan":
                        rows.append({"ticker": ticker, "name": val, "exchange": r.get("市場別"), "source": f"FinLab company_basic_info:{col}"})
        except Exception as e:
            print(f"WARN local FinLab TW reference failed: {e}", file=sys.stderr)
    # Live official TWSE/TPEx company code lists; Chinese names are still useful audit sources.
    for url, source, code_col, name_cols in [
        ("https://openapi.twse.com.tw/v1/opendata/t187ap03_L", "TWSE OpenAPI t187ap03_L", "公司代號", ["公司名稱", "公司簡稱"]),
        ("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O", "TPEx OpenAPI mopsfin_t187ap03_O", "SecuritiesCompanyCode", ["CompanyName", "CompanyShortName"]),
    ]:
        try:
            data = http_json(url, user_agent="Mozilla/5.0 Johan MSCI research")
            for rec in data:
                ticker = str(rec.get(code_col, "")).strip()
                for col in name_cols:
                    val = str(rec.get(col, "")).strip()
                    if ticker and val:
                        rows.append({"ticker": ticker, "name": val, "exchange": source.split()[0], "source": f"{source}:{col}"})
        except Exception as e:
            print(f"WARN {source} failed: {e}", file=sys.stderr)
    df = pd.DataFrame(rows).drop_duplicates(subset=["ticker", "name", "source"])
    df["norm"] = df["name"].map(normalize_name)
    return df


def yahoo_search(query: str) -> list[dict[str, Any]]:
    if query in YAHOO_CACHE:
        return YAHOO_CACHE[query]
    url = "https://query1.finance.yahoo.com/v1/finance/search?" + urlencode({"q": query, "quotesCount": 10, "newsCount": 0})
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=6) as r:
            data = json.loads(r.read().decode("utf-8"))
        out = data.get("quotes", [])
    except Exception:
        out = []
    YAHOO_CACHE[query] = out
    return out


def build_ref_index(ref: pd.DataFrame) -> dict[str, list[int]]:
    idx: dict[str, list[int]] = defaultdict(list)
    token_sets = []
    for i, norm in enumerate(ref.get("norm", [])):
        toks = {tok for tok in str(norm).split() if len(tok) >= 2 and tok not in CORP_WORDS}
        token_sets.append(toks)
        for tok in toks:
            idx[tok].append(i)
    ref.attrs["token_sets"] = token_sets
    REF_EXACT[id(ref)] = {str(n): i for i, n in enumerate(ref.get("norm", [])) if str(n)}
    return idx


def best_fuzzy(name: str, ref: pd.DataFrame, min_score: float = 0.82) -> dict[str, Any]:
    target = normalize_name(name)
    if not target or ref.empty:
        return {"ticker": None, "score": 0.0, "matched_name": None, "source": None, "status": "needs_review"}
    tokens = [t for t in target.split() if len(t) >= 2]
    ref_index = REF_INDEXES.get(id(ref), {})
    exact = REF_EXACT.get(id(ref), {})
    if target in exact:
        best = ref.iloc[exact[target]]
        return {"ticker": best["ticker"], "score": 1.0, "matched_name": best["name"], "source": best["source"], "status": "mapped_fuzzy"}
    # Fast conservative mode: exact normalized match only. Non-exact names are kept
    # for review rather than guessed; this is safer for historical ticker work.
    return {"ticker": None, "score": 0.0, "matched_name": None, "source": None, "status": "needs_review"}
    best_i = None
    best_score = -1.0
    if best_i is not None:
        best = ref.iloc[best_i]
    else:
        best = None
    if best is not None and best_score >= min_score:
        return {"ticker": best["ticker"], "score": round(float(best_score), 4), "matched_name": best["name"], "source": best["source"], "status": "mapped_fuzzy"}
    return {"ticker": None, "score": round(float(best_score), 4), "matched_name": None if best is None else best["name"], "source": None if best is None else best["source"], "status": "needs_review"}


def map_name(country: str, company_name: str, refs: dict[str, pd.DataFrame]) -> dict[str, Any]:
    if country == "USA":
        # First official reference fuzzy.
        m = best_fuzzy(company_name, refs["USA"], min_score=0.84)
        if m["ticker"]:
            m["status"] = "mapped_official_fuzzy"
            return m
        # Do not use per-name Yahoo fallback for the full US history by default: it is slow and
        # less auditable than SEC/NasdaqTrader. Unmatched names stay reviewable instead of guessed.
        return m
    else:
        # Local fuzzy catches English abbreviations and Chinese audit names cheaply; Yahoo handles MSCI English full names.
        local = best_fuzzy(company_name, refs["TAIWAN"], min_score=0.88)
        if local["ticker"]:
            local["status"] = "mapped_local_fuzzy"
            return local
        # Full-history per-name web search is intentionally not done inline; it is slow and can
        # be rerun from the saved mapping table for `needs_review` names. Keep the raw MSCI name.
        return local


def main() -> None:
    rows = []
    nested: dict[str, Any] = {}
    pdf_meta = []
    for product, folder in PRODUCTS.items():
        for path in sorted(folder.glob("MSCI_*PublicList.pdf")):
            text = extract_text(path)
            issue_date, effective_close_date = parse_date_line(text)
            review_key = pdf_review_key(path)
            pdf_meta.append({"product": product, "review": review_key, "pdf_file": str(path), "issue_date": issue_date, "announcement_date": issue_date, "effective_close_date": effective_close_date})
            nested.setdefault(product, {})[review_key] = {
                "issue_date": issue_date,
                "announcement_date": issue_date,
                "effective_close_date": effective_close_date,
                "pdf_file": str(path),
                "countries": {},
            }
            for country in COUNTRIES:
                adds, dels = parse_country_section(text, country)
                nested[product][review_key]["countries"][country] = {"additions": [], "deletions": []}
                for action, names in [("addition", adds), ("deletion", dels)]:
                    for i, name in enumerate(names, 1):
                        rec = {
                            "product": product,
                            "review": review_key,
                            "issue_date": issue_date,
                            "announcement_date": issue_date,
                            "effective_close_date": effective_close_date,
                            "country": country,
                            "action": action,
                            "company_name": name,
                            "source_pdf": str(path),
                            "row_order": i,
                        }
                        rows.append(rec)
                        nested[product][review_key]["countries"][country]["additions" if action == "addition" else "deletions"].append({"company_name": name})
    events = pd.DataFrame(rows)
    print(f"Parsed event rows: {len(events)}; unique names={events[['country','company_name']].drop_duplicates().shape[0]}")

    cached_usa = OUT_DIR / "mapping_reference_usa.csv"
    cached_tw = OUT_DIR / "mapping_reference_taiwan.csv"
    if cached_usa.exists() and cached_tw.exists():
        print("Loading cached mapping references...", flush=True)
        refs = {"USA": pd.read_csv(cached_usa, dtype=str), "TAIWAN": pd.read_csv(cached_tw, dtype=str)}
        refs["USA"]["norm"] = refs["USA"]["name"].map(normalize_name)
        refs["TAIWAN"]["norm"] = refs["TAIWAN"]["name"].map(normalize_name)
    else:
        refs = {"USA": load_us_reference(), "TAIWAN": load_taiwan_reference()}
    for k, v in refs.items():
        v.to_csv(OUT_DIR / f"mapping_reference_{k.lower()}.csv", index=False)
        REF_INDEXES[id(v)] = build_ref_index(v)
        print(f"Reference {k}: {len(v)} rows", flush=True)

    map_df = events[["country", "company_name"]].drop_duplicates().copy()
    map_df["norm"] = map_df["company_name"].map(normalize_name)
    ref_frames = []
    for country, ref in refs.items():
        tmp = ref[["ticker", "name", "source", "norm"]].dropna(subset=["norm"]).drop_duplicates(subset=["norm"]).copy()
        tmp["country"] = country
        ref_frames.append(tmp.rename(columns={"ticker": "stock_code", "name": "matched_name", "source": "mapping_source"}))
    ref_exact = pd.concat(ref_frames, ignore_index=True)
    map_df = map_df.merge(ref_exact, on=["country", "norm"], how="left")
    map_df["stock_code"] = map_df["stock_code"].where(map_df["stock_code"].isna(), map_df["stock_code"].astype(str))
    map_df["mapping_score"] = map_df["stock_code"].notna().astype(float)
    map_df["mapping_status"] = map_df["stock_code"].notna().map({True: "mapped_exact_normalized", False: "needs_review"})
    map_df = map_df.drop(columns=["norm"])
    print("Mapping table built", flush=True)

    out = events.merge(map_df, on=["country", "company_name"], how="left")
    print("Merged flat table", flush=True)
    out = out[[
        "product", "review", "issue_date", "announcement_date", "effective_close_date", "country", "action",
        "company_name", "stock_code", "mapping_status", "mapping_score", "matched_name", "mapping_source", "source_pdf", "row_order",
    ]]

    # Fill nested dict with mapped fields.
    by_key = {(r.product, r.review, r.country, r.action, r.company_name): r for r in out.itertuples(index=False)}
    print("Built nested lookup", flush=True)
    for product, reviews in nested.items():
        for review, obj in reviews.items():
            for country, chg in obj["countries"].items():
                for action_key, action in [("additions", "addition"), ("deletions", "deletion")]:
                    new_items = []
                    for item in chg[action_key]:
                        r = by_key[(product, review, country, action, item["company_name"])]
                        new_items.append({
                            "company_name": r.company_name,
                            "stock_code": None if pd.isna(r.stock_code) else r.stock_code,
                            "mapping_status": r.mapping_status,
                            "mapping_score": None if pd.isna(r.mapping_score) else float(r.mapping_score),
                            "matched_name": None if pd.isna(r.matched_name) else r.matched_name,
                            "mapping_source": None if pd.isna(r.mapping_source) else r.mapping_source,
                        })
                    chg[action_key] = new_items

    print("Nested dict filled", flush=True)
    out.to_csv(OUT_DIR / "msci_us_taiwan_events_flat.csv", index=False)
    map_df.to_csv(OUT_DIR / "msci_us_taiwan_name_ticker_mapping.csv", index=False)
    pd.DataFrame(pdf_meta).to_csv(OUT_DIR / "msci_pdf_review_metadata.csv", index=False)
    (OUT_DIR / "msci_us_taiwan_events_dict.json").write_text(json.dumps(nested, ensure_ascii=False, indent=2), encoding="utf-8")

    # Report
    summary = out.groupby(["product", "country", "action"]).size().unstack(fill_value=0).reset_index()
    status = out.groupby(["country", "mapping_status"]).size().reset_index(name="rows")
    unique_status = map_df.groupby(["country", "mapping_status"]).size().reset_index(name="unique_names")
    def md_table(df: pd.DataFrame) -> str:
        if df.empty:
            return "（空）\n"
        cols = list(df.columns)
        lines = ["| " + " | ".join(map(str, cols)) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
        for _, row in df.iterrows():
            lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
        return "\n".join(lines)

    report = []
    report.append("# MSCI Standard / Small Cap 美國與台灣增刪成分解析報告\n")
    report.append(f"- 產出時間：{datetime.now().isoformat(timespec='seconds')}\n")
    report.append(f"- PDF 根目錄：`{PDF_DIR}`\n")
    report.append(f"- 解析產品：Global Standard (`stdindex`) 與 Global Small Cap (`smallcap`)\n")
    report.append(f"- 解析範圍：只保留 `USA` 與 `TAIWAN` 的 additions / deletions\n")
    report.append(f"- PDF 數量：standard {len(list(PRODUCTS['standard'].glob('MSCI_*PublicList.pdf')))}，small_cap {len(list(PRODUCTS['small_cap'].glob('MSCI_*PublicList.pdf')))}\n")
    report.append(f"- 事件列數：{len(out):,}；唯一公司名稱：{map_df.shape[0]:,}\n\n")
    report.append("## 輸出檔案\n")
    for fn in ["msci_us_taiwan_events_dict.json", "msci_us_taiwan_events_flat.csv", "msci_us_taiwan_name_ticker_mapping.csv", "msci_pdf_review_metadata.csv", "mapping_reference_usa.csv", "mapping_reference_taiwan.csv"]:
        report.append(f"- `parsed/{fn}`\n")
    report.append("\n## 欄位說明\n")
    report.append("- `issue_date`：PDF 第一行 Geneva 發行日。\n")
    report.append("- `announcement_date`：本資料集暫以 PDF 發行日作公告可得日；MSCI 通常公告日即該 PDF 日期。\n")
    report.append("- `effective_close_date`：PDF 文字 `as of the close of ...`，回測時應視為收盤後生效。\n")
    report.append("- `company_name`：MSCI PDF 原始公司名稱。\n")
    report.append("- `stock_code`：對應股票代號；美股為 ticker，台股為四碼/含字母代號。\n")
    report.append("- `mapping_status`：mapping 信心狀態；`needs_review` 不應直接進正式回測。\n\n")
    report.append("## 事件數摘要\n")
    report.append(md_table(summary))
    report.append("\n\n## Mapping 狀態摘要（事件列）\n")
    report.append(md_table(status))
    report.append("\n\n## Mapping 狀態摘要（唯一公司名）\n")
    report.append(md_table(unique_status))
    needs = map_df[map_df["mapping_status"].eq("needs_review")].sort_values(["country", "company_name"])
    report.append("\n\n## 仍需人工/二次資料源確認的名稱\n")
    if needs.empty:
        report.append("目前沒有 `needs_review`。\n")
    else:
        report.append(md_table(needs[["country", "company_name", "matched_name", "mapping_score", "mapping_source"]].head(80)))
        if len(needs) > 80:
            report.append(f"\n\n（只列前 80 筆；完整清單見 `parsed/msci_us_taiwan_name_ticker_mapping.csv`，共 {len(needs)} 筆。）\n")
    report.append("\n\n## 重要限制與建議\n")
    report.append("- MSCI PDF 公司名常為縮寫，且 A/B/C share class 可能被寫在名稱尾端；目前 mapping 已保留原始名稱與 matched_name，方便反覆核對。\n")
    report.append("- 目前自動 mapping 採保守版：只接受 MSCI 名稱與 SEC/NasdaqTrader/FinLab/TWSE/TPEx 參考表的 normalized exact match；未精確對上的名稱一律保留 `needs_review`，避免同名、縮寫、share class 或歷史下市 ticker 被誤配。\n")
    report.append("- 後續應補第二階段 verifier：對 `needs_review` 使用 Yahoo Finance / 交易所英文公司名 / 歷史 symbol master 反覆驗證後再填入 `stock_code`。\n")
    report.append("- 正式回測前建議先排除 `needs_review` 與低分數 mapping，並針對同公司多 share class / 更名 / 下市歷史做 survivorship-bias 檢查。\n")
    (REPORT_DIR / "msci_us_taiwan_pdf_parse_report.md").write_text("".join(report), encoding="utf-8")
    print(f"Wrote outputs to {OUT_DIR}")
    print(f"Wrote report to {REPORT_DIR / 'msci_us_taiwan_pdf_parse_report.md'}")


if __name__ == "__main__":
    main()
