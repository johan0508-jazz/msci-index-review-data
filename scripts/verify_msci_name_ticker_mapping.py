#!/usr/bin/env python3
"""Second-stage verification for MSCI company-name -> ticker mapping.

Conservative verifier:
- preserves original MSCI company_name and existing exact mappings;
- maps unresolved names only when a local/official reference or Yahoo Finance result has high confidence;
- writes separate verified mapping, refreshed flat events, refreshed dict JSON, and a small report.
"""
from __future__ import annotations

import json
import re
import ssl
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARSED = ROOT / "parsed"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

CORP_WORDS = {
    "INC", "INCORPORATED", "CORP", "CORPORATION", "CO", "COMPANY", "LTD", "LIMITED", "PLC", "SA", "NV",
    "GROUP", "HOLDINGS", "HOLDING", "THE", "COMMON", "STOCK", "CLASS", "CL", "ORD", "NEW", "COM", "LP", "TRUST",
}
CLASS_WORDS = {"A", "B", "C"}
GENERIC_SINGLE_TOKENS = {"ASIA", "ADVANCED", "CHINA", "TAIWAN", "PHOENIX", "CHEM", "POWER", "ENERGY", "GLOBAL", "NATIONAL", "UNITED", "FIRST", "GENERAL", "CENTRAL", "CAPITAL", "PACIFIC", "AMERICAN", "NATURAL"}
BAD_SECURITY_WORDS = {"ETF", "FUND", "ETN", "PREFERRED", "PREFERENCE", "DEPOSITARY", "WARRANT", "RIGHT", "UNIT", "NOTE"}
US_EXCHANGES = {"NYQ", "NMS", "NGM", "NCM", "ASE", "PCX", "NYSE", "Nasdaq", "NASDAQ", "AMEX"}


def normalize_name(s: str) -> str:
    s = str(s or "").upper().replace("&", " AND ")
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"[^A-Z0-9 ]+", " ", s)
    words = [w for w in s.split() if w not in CORP_WORDS]
    if len(words) > 1 and words[-1] in CLASS_WORDS:
        words = words[:-1]
    return " ".join(words)


def tokens(s: str) -> set[str]:
    return {t for t in normalize_name(s).split() if len(t) >= 2}


def dice(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return 2 * len(a & b) / (len(a) + len(b))


def string_score(msci_name: str, ref_name: str) -> float:
    a = normalize_name(msci_name)
    b = normalize_name(ref_name)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    ta, tb = set(a.split()), set(b.split())
    sc = max(dice(ta, tb), SequenceMatcher(None, a, b).ratio())
    if b in a and len(b) >= 4:
        # MSCI often expands an official English abbreviation: ECLAT -> ECLAT TEXTILE COMPANY.
        sc = max(sc, min(0.96, 0.86 + len(b) / max(len(a), 1) * 0.10))
    if a in b and len(a) >= 4:
        sc = max(sc, min(0.96, 0.86 + len(a) / max(len(b), 1) * 0.10))
    if a.split() and b.split() and a.split()[0] == b.split()[0]:
        sc = min(1.0, sc + 0.03)
    return round(float(sc), 4)


def build_index(ref: pd.DataFrame) -> dict[str, set[int]]:
    idx: dict[str, set[int]] = defaultdict(set)
    for i, n in enumerate(ref["norm"].fillna("")):
        for tok in str(n).split():
            if len(tok) >= 2:
                idx[tok].add(i)
    return idx


def is_bad_security(row: pd.Series) -> bool:
    nm = normalize_name(row.get("name", ""))
    ticker = str(row.get("ticker", ""))
    return any(w in set(nm.split()) for w in BAD_SECURITY_WORDS) or bool(re.search(r"[-/]P", ticker))


def best_ref_match(name: str, ref: pd.DataFrame, idx: dict[str, set[int]], country: str) -> dict:
    tks = tokens(name)
    cand: set[int] = set()
    for tok in tks:
        cand |= idx.get(tok, set())
    if not cand:
        return {}
    # Evaluate at most the most relevant candidates; using token intersection rank is deterministic and fast.
    ranked = []
    ref_norms = ref["norm"].fillna("").tolist()
    for i in cand:
        rt = set(str(ref_norms[i]).split())
        ranked.append((len(tks & rt), i))
    ranked = sorted(ranked, reverse=True)[:300]
    best = None
    best_score = -1.0
    second = -1.0
    for _, i in ranked:
        r = ref.iloc[i]
        if country == "USA" and is_bad_security(r):
            continue
        sc = string_score(name, r["name"])
        if sc > best_score:
            second = best_score
            best_score = sc
            best = r
        elif sc > second:
            second = sc
    if best is None:
        return {}
    # Conservative thresholds. Prefer substring / multi-token agreement; never accept
    # one-token SequenceMatcher guesses like ASIA -> ASIA CEMENT or TONIX -> ONYX.
    accept = False
    status = "needs_review"
    target_norm = normalize_name(name)
    ref_norm = normalize_name(best["name"])
    tt = set(target_norm.split())
    rt = set(ref_norm.split())
    inter = len(tt & rt)
    substring = bool(ref_norm and target_norm and (ref_norm in target_norm or target_norm in ref_norm))
    single_ref_token = len(rt) == 1
    token_ambiguous = False
    if single_ref_token:
        tok = next(iter(rt)) if rt else ""
        # If the same English abbreviation maps to multiple tickers, do not auto-verify.
        tickers = set(ref.loc[ref["norm"].eq(tok), "ticker"].astype(str))
        token_ambiguous = len(tickers) > 1 or tok in GENERIC_SINGLE_TOKENS or len(tok) < 5
    first_match = bool(target_norm.split() and ref_norm.split() and target_norm.split()[0] == ref_norm.split()[0])
    if country == "TAIWAN":
        accept = (substring and len(ref_norm) >= 5 and not token_ambiguous) or (first_match and inter >= 2 and dice(tt, rt) >= 0.72)
        status = "verified_tw_reference_fuzzy"
    else:
        accept = (substring and len(ref_norm) >= 5 and not token_ambiguous) or (first_match and inter >= 2 and dice(tt, rt) >= 0.74)
        status = "verified_us_reference_fuzzy"
    # Require a small margin when confidence is not excellent.
    if accept and best_score < 0.92 and second > 0 and best_score - second < 0.04:
        accept = False
    if not accept:
        return {"candidate_stock_code": best["ticker"], "candidate_matched_name": best["name"], "candidate_score": best_score, "candidate_source": best["source"]}
    return {
        "stock_code": str(best["ticker"]),
        "matched_name": best["name"],
        "mapping_source": best["source"],
        "mapping_score": best_score,
        "mapping_status": status,
    }


def yahoo_search(query: str) -> list[dict]:
    url = "https://query1.finance.yahoo.com/v1/finance/search?" + urlencode({"q": query, "quotesCount": 8, "newsCount": 0})
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        with urlopen(req, timeout=8, context=ssl._create_unverified_context()) as r:
            return json.loads(r.read().decode("utf-8")).get("quotes", [])
    except Exception:
        return []


def best_yahoo_us(name: str, known_symbols: set[str]) -> dict:
    best = None
    best_score = 0.0
    for q in yahoo_search(name):
        sym = str(q.get("symbol") or "")
        if not sym or "." in sym or q.get("quoteType") != "EQUITY":
            continue
        exch = q.get("exchange") or q.get("exchDisp")
        if exch not in US_EXCHANGES and sym not in known_symbols:
            continue
        nm = q.get("longname") or q.get("shortname") or ""
        nn = normalize_name(nm)
        tn = normalize_name(name)
        first_match = bool(tn.split() and nn.split() and tn.split()[0] == nn.split()[0])
        substring = bool(tn and nn and (tn in nn or nn in tn))
        if not (first_match or substring):
            continue
        sc = string_score(name, nm)
        if sym in known_symbols:
            sc = min(1.0, sc + 0.03)
        if sc > best_score:
            best_score = sc
            best = q
    if best and best_score >= 0.82:
        return {
            "stock_code": best.get("symbol"),
            "matched_name": best.get("longname") or best.get("shortname"),
            "mapping_source": "Yahoo Finance search + US exchange/SEC symbol verification",
            "mapping_score": round(float(best_score), 4),
            "mapping_status": "verified_yahoo_us",
        }
    return {}


def rebuild_outputs(mapping: pd.DataFrame) -> None:
    flat = pd.read_csv(PARSED / "msci_us_taiwan_events_flat.csv", dtype=str)
    cols = ["country", "company_name"]
    replace_cols = ["stock_code", "mapping_status", "mapping_score", "matched_name", "mapping_source"]
    flat = flat.drop(columns=[c for c in replace_cols if c in flat.columns]).merge(mapping[cols + replace_cols], on=cols, how="left")
    # Keep stable column order.
    order = [
        "product", "review", "issue_date", "announcement_date", "effective_close_date", "country", "action",
        "company_name", "stock_code", "mapping_status", "mapping_score", "matched_name", "mapping_source", "source_pdf", "row_order",
    ]
    flat = flat[order]
    flat.to_csv(PARSED / "msci_us_taiwan_events_flat_verified.csv", index=False)

    nested: dict = {}
    for r in flat.itertuples(index=False):
        product = r.product
        review = r.review
        obj = nested.setdefault(product, {}).setdefault(review, {
            "issue_date": r.issue_date,
            "announcement_date": r.announcement_date,
            "effective_close_date": r.effective_close_date,
            "pdf_file": r.source_pdf,
            "countries": {},
        })
        chg = obj["countries"].setdefault(r.country, {"additions": [], "deletions": []})
        key = "additions" if r.action == "addition" else "deletions"
        def clean(x):
            return None if pd.isna(x) or str(x) == "nan" else x
        chg[key].append({
            "company_name": r.company_name,
            "stock_code": clean(r.stock_code),
            "mapping_status": clean(r.mapping_status),
            "mapping_score": None if pd.isna(r.mapping_score) else float(r.mapping_score),
            "matched_name": clean(r.matched_name),
            "mapping_source": clean(r.mapping_source),
        })
    (PARSED / "msci_us_taiwan_events_dict_verified.json").write_text(json.dumps(nested, ensure_ascii=False, indent=2), encoding="utf-8")


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "（空）"
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(out)


def write_report(before: pd.DataFrame, after: pd.DataFrame) -> None:
    flat = pd.read_csv(PARSED / "msci_us_taiwan_events_flat_verified.csv", dtype=str)
    summary_unique = after.groupby(["country", "mapping_status"]).size().reset_index(name="unique_names")
    summary_rows = flat.groupby(["country", "mapping_status"]).size().reset_index(name="event_rows")
    newly = after[(before["mapping_status"].eq("needs_review")) & (~after["mapping_status"].eq("needs_review"))].copy()
    still = after[after["mapping_status"].eq("needs_review")].copy()

    report = []
    report.append("# MSCI USA / Taiwan 名稱轉股票代號 verify 報告\n\n")
    report.append(f"- 產出時間：{datetime.now().isoformat(timespec='seconds')}\n")
    report.append("- 目標：針對前一版 `needs_review` 的 MSCI 公司名稱做第二階段 ticker verify，並保留 `company_name` 與 `stock_code` 分欄。\n")
    report.append("- 原則：寧可保守，不硬猜；只有高信心來源才回填 ticker。\n\n")
    report.append("## 輸出檔案\n\n")
    for fn in [
        "msci_us_taiwan_name_ticker_mapping_verified.csv",
        "msci_us_taiwan_events_flat_verified.csv",
        "msci_us_taiwan_events_dict_verified.json",
        "msci_us_taiwan_mapping_verify_candidates.csv",
    ]:
        report.append(f"- `parsed/{fn}`\n")
    report.append("\n## Verify 方法\n\n")
    report.append("1. 保留前一版 exact-normalized mapping。\n")
    report.append("2. 對 `needs_review` 做 reference fuzzy verify：\n")
    report.append("   - USA：SEC `company_tickers_exchange` + NasdaqTrader listed/other-listed symbol directory。\n")
    report.append("   - Taiwan：FinLab company basic info + TWSE/TPEx company code reference。\n")
    report.append("3. USA 本輪不做 fuzzy/Yahoo 自動回填：歷史 delisted / merger / rename 太多，容易把舊公司誤配成現在同名或相似名 ticker；除前一版 exact-normalized 外，其餘維持 `needs_review`。\n")
    report.append("4. 無法高信心驗證者維持 `needs_review`，不進正式回測 universe。\n\n")
    report.append("## Mapping 狀態摘要（唯一公司名稱）\n\n")
    report.append(md_table(summary_unique))
    report.append("\n\n## Mapping 狀態摘要（事件列）\n\n")
    report.append(md_table(summary_rows))
    report.append("\n\n## 本輪新增 verified mapping 範例\n\n")
    cols = ["country", "company_name", "stock_code", "matched_name", "mapping_status", "mapping_score", "mapping_source"]
    report.append(md_table(newly[cols].sort_values(["country", "company_name"]).head(80)))
    if len(newly) > 80:
        report.append(f"\n\n（只列前 80 筆；完整見 verified mapping CSV，共新增 {len(newly)} 個唯一名稱。）")
    report.append("\n\n## 仍需人工/歷史資料源確認\n\n")
    report.append(f"仍有 `{len(still)}` 個唯一名稱是 `needs_review`。這些多半是歷史下市、併購、改名、縮寫太重或 Taiwan 英文名不在目前 reference 中。\n\n")
    report.append(md_table(still[["country", "company_name"]].sort_values(["country", "company_name"]).head(80)))
    if len(still) > 80:
        report.append(f"\n\n（只列前 80 筆；完整見 verified mapping CSV。）")
    report.append("\n\n## 回測使用建議\n\n")
    report.append("- 第一版回測只使用 `mapping_status != needs_review` 的事件。\n")
    report.append("- 對 USA 舊名稱，很多需要 CRSP/Refinitiv/Compustat 或 historical symbol master 才能正確處理 delisting / merger；不要用 current Yahoo fuzzy 直接硬配。\n")
    report.append("- Taiwan 的剩餘項目建議補 TWSE/TPEX 英文公司名歷史表；目前只用 current reference，會有更名與下市 survivorship 問題。\n")
    (REPORTS / "msci_us_taiwan_mapping_verify_report.md").write_text("".join(report), encoding="utf-8")


def main() -> None:
    mapping = pd.read_csv(PARSED / "msci_us_taiwan_name_ticker_mapping.csv", dtype=str)
    before = mapping.copy()
    for c in ["stock_code", "matched_name", "mapping_source"]:
        mapping[c] = mapping[c].where(mapping[c].notna(), None)
    mapping["mapping_score"] = pd.to_numeric(mapping["mapping_score"], errors="coerce").fillna(0.0)

    refs = {
        "USA": pd.read_csv(PARSED / "mapping_reference_usa.csv", dtype=str),
        "TAIWAN": pd.read_csv(PARSED / "mapping_reference_taiwan.csv", dtype=str),
    }
    for ref in refs.values():
        ref["norm"] = ref["name"].map(normalize_name)
    indexes = {k: build_index(v) for k, v in refs.items()}
    known_us = set(refs["USA"]["ticker"].dropna().astype(str))

    candidates = []
    needs_idx = list(mapping[mapping["mapping_status"].eq("needs_review")].index)
    print(f"Reference fuzzy verify for {len(needs_idx)} names...", flush=True)
    for n, i in enumerate(needs_idx, 1):
        if n % 500 == 0:
            print(f"  ref {n}/{len(needs_idx)}", flush=True)
        row = mapping.loc[i]
        country = row["country"]
        name = row["company_name"]
        # Taiwan: FinLab/TWSE/TPEx English abbreviations are usable for conservative fuzzy verify.
        # USA: do NOT auto-verify historical fuzzy/Yahoo matches here; too many old delisted/renamed
        # names collide with current tickers. Keep them as candidates / needs_review unless exact.
        if country == "TAIWAN":
            result = best_ref_match(name, refs[country], indexes[country], country)
            if result and "stock_code" in result:
                for k, v in result.items():
                    mapping.at[i, k] = v
            elif result:
                candidates.append({"country": country, "company_name": name, **result})

    usa_left = list(mapping[(mapping["country"].eq("USA")) & (mapping["mapping_status"].eq("needs_review"))].index)
    print(f"USA remaining needs_review kept for historical-symbol verification: {len(usa_left)}", flush=True)

    mapping.to_csv(PARSED / "msci_us_taiwan_name_ticker_mapping_verified.csv", index=False)
    pd.DataFrame(candidates).to_csv(PARSED / "msci_us_taiwan_mapping_verify_candidates.csv", index=False)
    rebuild_outputs(mapping)
    write_report(before, mapping)

    print("Before:")
    print(before.groupby(["country", "mapping_status"]).size())
    print("After:")
    print(mapping.groupby(["country", "mapping_status"]).size())
    print(f"Wrote {PARSED / 'msci_us_taiwan_name_ticker_mapping_verified.csv'}")
    print(f"Wrote {REPORTS / 'msci_us_taiwan_mapping_verify_report.md'}")


if __name__ == "__main__":
    main()
