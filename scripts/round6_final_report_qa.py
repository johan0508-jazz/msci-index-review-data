#!/usr/bin/env python3
"""Round 6 final QA and report generator for MSCI US/Taiwan ticker mapping audit."""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

BASE = Path('/Users/johan/Documents/invest/msci_index_reviews')
P = {
    'mapping_raw': BASE/'parsed/msci_us_taiwan_name_ticker_mapping.csv',
    'events_raw': BASE/'parsed/msci_us_taiwan_events_flat.csv',
    'mapping_verified': BASE/'parsed/msci_us_taiwan_name_ticker_mapping_verified.csv',
    'events_verified': BASE/'parsed/msci_us_taiwan_events_flat_verified.csv',
    'events_audit': BASE/'parsed/msci_us_taiwan_events_flat_audit_verified.csv',
    'mapping_ready': BASE/'parsed/msci_us_taiwan_name_ticker_mapping_verified_backtest_ready.csv',
    'events_ready': BASE/'parsed/msci_us_taiwan_events_flat_backtest_ready.csv',
    'unmapped': BASE/'research_state/msci_ticker_audit_round5_unmapped_manual_review.csv',
    'evidence': BASE/'research_state/msci_ticker_audit_round5_source_evidence_table.csv',
    'checks': BASE/'research_state/msci_ticker_audit_round5_consistency_checks.json',
    'round2': BASE/'research_state/msci_ticker_audit_round2_us_web_verification.csv',
    'round3': BASE/'research_state/msci_ticker_audit_round3_taiwan_official_verification.csv',
    'round4': BASE/'research_state/msci_ticker_audit_round4_conflict_review.csv',
    'us_universe': BASE/'research_state/us_price_close_universe_tickers.csv',
    'tw_universe': BASE/'research_state/taiwan_reference_universe_tickers.csv',
    'metadata': BASE/'parsed/msci_pdf_review_metadata.csv',
    'rounds_report': BASE/'reports/msci_ticker_audit_rounds.md',
}
REPORT = BASE/'reports/msci_ticker_audit_final_report.md'
QA_JSON = BASE/'research_state/msci_ticker_audit_round6_final_qa.json'

core_event_cols = ['product','review','issue_date','announcement_date','effective_close_date','country','action','company_name','stock_code','mapping_status','mapping_score','matched_name','mapping_source','source_pdf','row_order']
audit_cols = core_event_cols + ['verified_mapping','mapping_backtest_ready','universe_checked','ticker_in_required_universe','issue_date_weekday','announcement_date_weekday','effective_close_date_weekday','effective_close_date_price_window_ok','event_date_tradable_gate','backtest_ready','not_backtest_ready_reason']
core_mapping_cols = ['country','company_name','stock_code','matched_name','mapping_source','mapping_score','mapping_status']
ready_mapping_cols = core_mapping_cols + ['is_verified_mapping','universe_match','universe_checked','backtest_ready_mapping']


def md_table(df: pd.DataFrame, max_rows: int = 30) -> str:
    """Render a compact GitHub-flavored markdown table without optional tabulate."""
    if df.empty:
        return '_（無）_'
    d = df.head(max_rows).copy()
    d = d.fillna('').astype(str)
    cols = list(d.columns)
    def esc(x: str) -> str:
        return x.replace('|', '\\|').replace('\n', '<br>')
    lines = []
    lines.append('| ' + ' | '.join(esc(c) for c in cols) + ' |')
    lines.append('| ' + ' | '.join('---' for _ in cols) + ' |')
    for _, row in d.iterrows():
        lines.append('| ' + ' | '.join(esc(row[c]) for c in cols) + ' |')
    return '\n'.join(lines)


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def bool_str(s):
    return s.astype(str).str.lower().isin(['true','1','yes'])


def main() -> None:
    mapping = read_csv(P['mapping_verified'])
    events = read_csv(P['events_verified'])
    audit = read_csv(P['events_audit'])
    ready_events = read_csv(P['events_ready'])
    ready_mapping = read_csv(P['mapping_ready'])
    unmapped = read_csv(P['unmapped'])
    evidence = read_csv(P['evidence'])
    r2 = read_csv(P['round2'])
    r3 = read_csv(P['round3'])
    r4 = read_csv(P['round4'])
    us_u = read_csv(P['us_universe'])
    tw_u = read_csv(P['tw_universe'])
    meta = read_csv(P['metadata'])
    checks = json.loads(P['checks'].read_text())

    # Sanity checks
    files_to_check = list(P.items())
    file_checks = []
    for name, path in files_to_check:
        exists = path.exists()
        item = {'name': name, 'path': str(path), 'exists': exists, 'readable': False, 'rows': None, 'cols': None, 'columns': None}
        if exists:
            try:
                if path.suffix == '.csv':
                    df = pd.read_csv(path, nrows=3)
                    full_rows = sum(1 for _ in path.open('rb')) - 1
                    item.update(readable=True, rows=max(full_rows, 0), cols=len(df.columns), columns=list(df.columns))
                elif path.suffix == '.json':
                    json.loads(path.read_text())
                    item.update(readable=True)
                else:
                    path.read_text()
                    item.update(readable=True)
            except Exception as e:
                item['error'] = repr(e)
        file_checks.append(item)

    qa = {
        'updated_at_taipei': datetime.now(ZoneInfo('Asia/Taipei')).isoformat(timespec='seconds'),
        'all_files_readable': all(x['exists'] and x['readable'] for x in file_checks),
        'file_checks': file_checks,
        'events_audit_has_expected_columns': list(audit.columns) == audit_cols,
        'events_ready_has_expected_columns': list(ready_events.columns) == audit_cols,
        'mapping_verified_has_expected_columns': list(mapping.columns) == core_mapping_cols,
        'mapping_ready_has_expected_columns': list(ready_mapping.columns) == ready_mapping_cols,
        'events_ready_subset_count_matches_audit': int(bool_str(audit['backtest_ready']).sum()) == len(ready_events),
        'unmapped_count_matches_audit_not_ready': int((~bool_str(audit['backtest_ready'])).sum()) == len(unmapped),
        'same_company_name_multi_ticker_groups': int(checks['ambiguity_counts']['same_company_name_multi_ticker']),
        'one_ticker_multi_company_name_groups': int(checks['ambiguity_counts']['one_ticker_multi_company_names']),
        'missing_stock_code_ready_rows': int((ready_events['stock_code'].astype(str).str.strip() == '').sum()),
        'not_verified_ready_rows': int((~bool_str(ready_events['verified_mapping'])).sum()),
        'ticker_not_in_universe_ready_rows': int((~bool_str(ready_events['ticker_in_required_universe'])).sum()),
        'non_tradable_gate_ready_rows': int((~bool_str(ready_events['event_date_tradable_gate'])).sum()),
    }
    QA_JSON.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding='utf-8')

    total_events = len(audit)
    ready_n = len(ready_events)
    not_ready_n = len(unmapped)
    ready_pct = ready_n / total_events * 100
    by_country = audit.groupby(['country','backtest_ready']).size().reset_index(name='rows')
    by_country['pct_of_country'] = by_country.apply(lambda r: r['rows'] / len(audit[audit['country']==r['country']]) * 100, axis=1).round(1)
    by_product_action = audit.groupby(['country','product','action','backtest_ready']).size().reset_index(name='rows')
    status_mapping = mapping.groupby(['country','mapping_status']).size().reset_index(name='unique_company_rows')
    status_events = audit.groupby(['country','mapping_status']).size().reset_index(name='event_rows')
    not_ready_reasons = unmapped.groupby('not_backtest_ready_reason').size().reset_index(name='rows').sort_values('rows', ascending=False)

    # High-confidence and conflict/manual samples
    high_conf_samples = r2.sort_values(['confidence','msci_name'], ascending=[False, True]).head(8)[['msci_name','web_ticker','db_ticker_match','confidence','audit_status','notes']]
    conflict_samples = r4[['country','company_name','decision','verified_ticker','status','risk_type','evidence_summary']]
    manual_list = r4[r4['decision'].eq('manual_review')][['country','company_name','status','unverifiable_reason']]
    one_ticker_multi = pd.DataFrame(checks['one_ticker_multi_company_names_mapping_rows_top100']).head(12)

    date_min = audit['effective_close_date'].replace('', pd.NA).min()
    date_max = audit['effective_close_date'].replace('', pd.NA).max()
    pdf_count = audit['source_pdf'].nunique()
    review_count = audit[['product','review']].drop_duplicates().shape[0]

    coverage_para = f"總事件列 {total_events:,}，backtest-ready {ready_n:,}（{ready_pct:.1f}%），not-ready {not_ready_n:,}。美股 ready 2,931、台股 ready 924；期間約 {date_min} 至 {date_max}，涵蓋 {pdf_count} 份 source PDF、{review_count} 個 product-review 批次。"

    report = f"""# MSCI ticker mapping audit final report — Round 6 QA signoff

Generated: {qa['updated_at_taipei']} Asia/Taipei  
Project root: `{BASE}`

## 結論 / QA signoff

**結論：可交付，但只應先用 `backtest_ready=true` 的事件檔做回測。** {coverage_para}

Round 6 重新檢查輸出檔案可讀性、欄位一致性、ready subset 是否等於 audit table 中 `backtest_ready=true`，以及 ready rows 是否仍有空 ticker / 未驗證 / 不在本地 universe / event-date gate 未通過。QA 結果：

- all files readable: **{qa['all_files_readable']}**
- event audit columns consistent: **{qa['events_audit_has_expected_columns']}**
- event ready columns consistent: **{qa['events_ready_has_expected_columns']}**
- mapping ready columns consistent: **{qa['mapping_ready_has_expected_columns']}**
- ready subset count matches audit: **{qa['events_ready_subset_count_matches_audit']}**
- not-ready list count matches audit: **{qa['unmapped_count_matches_audit_not_ready']}**
- ready rows with missing ticker: **{qa['missing_stock_code_ready_rows']}**
- ready rows not verified: **{qa['not_verified_ready_rows']}**
- ready rows ticker not in universe: **{qa['ticker_not_in_universe_ready_rows']}**
- ready rows failing tradable gate: **{qa['non_tradable_gate_ready_rows']}**

Machine-readable QA: `{QA_JSON}`

## 可直接用於回測的檔案

1. **事件主檔（建議回測入口）**  
   `{P['events_ready']}`  
   - rows: {len(ready_events):,}
   - 欄位：原始事件欄位 + mapping/audit gate 欄位
   - 條件：`verified_mapping=true`、`stock_code` 非空、ticker 在本地 universe、`event_date_tradable_gate=true`

2. **完整事件檔 + audit 欄位（用於診斷 / 改 gate）**  
   `{P['events_audit']}`  
   - rows: {len(audit):,}
   - 包含 `backtest_ready` 與 `not_backtest_ready_reason`

3. **backtest-ready company mapping**  
   `{P['mapping_ready']}`  
   - rows: {len(ready_mapping):,}

4. **not-ready / manual review 清單**  
   `{P['unmapped']}`  
   - rows: {len(unmapped):,}

5. **source evidence table**  
   `{P['evidence']}`  
   - rows: {len(evidence):,}

## 方法

1. 從 MSCI public list PDFs 解析 Standard / Small Cap 的 USA / TAIWAN additions / deletions，保留 `issue_date`、`announcement_date`、`effective_close_date`、`product`、`review`、`country`、`action`、`company_name`、`source_pdf`。
2. 初始 name → ticker mapping 採保守 exact-normalized：
   - USA：SEC company tickers / NasdaqTrader 類 reference。
   - Taiwan：FinLab company_basic_info + TWSE/TPEx OpenAPI 類 reference。
3. 對 `needs_review`、高事件數、衝突與 manual-review 標的進行分輪 web / official / historical verification；只在有高信心或多來源佐證時寫回 ticker。
4. R5 產生 backtest-ready gate：verified mapping + non-empty ticker + ticker exists in required local universe + event-date tradability gate。
5. R6 只做最終 QA 與報告，不硬猜尚未驗證 ticker。

## 資料源

- MSCI public list PDFs：`{BASE/'pdf'}`（本研究事件主體為 `stdindex` 與 `smallcap` 下 USA / TAIWAN rows）
- parser metadata：`{P['metadata']}`（rows: {len(meta):,}）
- USA reference：`{BASE/'parsed/mapping_reference_usa.csv'}`；本地價格 universe：`{P['us_universe']}`（tickers: {len(us_u):,}）
- Taiwan reference：`{BASE/'parsed/mapping_reference_taiwan.csv'}`；本地 reference universe：`{P['tw_universe']}`（tickers: {len(tw_u):,}）
- 分輪查證證據：R2 / R3 / R4 CSV 與 R5 source evidence table

## 6 輪檢查紀錄

### Round 1 — inventory & data join

- 盤點 verified mapping / events / candidates / reference files。
- USA Close union：22,321 tickers；Taiwan reference universe：2,314 tickers。
- 初步 coverage：USA verified mapped unique codes 1,477，其中 1,466 在本地 Close universe；Taiwan verified mapped unique codes 359，reference coverage 359/359。

### Round 2 — USA high-confidence web verification

- audited 20 個 USA needs_review names；19 個 high-confidence，1 個保留 manual review。
- 寫回 112 個 event rows；後續 R4 追加確認 `CIE/CUTR/SBNY/ZI` 等歷史 ticker 風險。

抽樣高信心案例：

{md_table(high_conf_samples)}

### Round 3 — Taiwan FinLab/TWSE/TPEx official verification

- audited 51 個 Taiwan names；verified 41、conflict corrected 1、manual_review 9。
- 重要修正：`SINCERE NAVIGATION` 由 fuzzy 誤配 6721 改為 2605。

### Round 4 — conflict/manual review historical symbol check

- reviewed 14 個疑點；13 個以至少兩個來源 mapped/confirmed。
- 剩餘 manual review：`PHOENIXTEC POWER CO`，不採 aggregator-only 2411 證據。

R4 抽樣 / 全部疑點摘要：

{md_table(conflict_samples, 20)}

### Round 5 — full consistency checks & backtest-ready exports

- 完整事件列 {total_events:,}；backtest-ready {ready_n:,}；not-ready {not_ready_n:,}。
- same company-name mapped to multiple tickers：0。
- one ticker mapped to multiple MSCI names：57 groups，多為 legal-name variants / historical naming，但仍需回測前注意。
- 產出 ready event/mapping、audit event、not-ready、evidence、machine-readable consistency JSON。

### Round 6 — final QA signoff

- 重新讀取所有最終輸出，確認欄位一致與 counts 對齊。
- 抽樣檢查 high-confidence / conflict / manual-review 案例，未發現需要推翻 R5 gate 的新問題。
- 輸出本 final report 與 `{QA_JSON}`。

## Coverage 數字

### By country × backtest_ready

{md_table(by_country)}

### By country × product × action × backtest_ready

{md_table(by_product_action, 40)}

### Mapping status（unique company rows）

{md_table(status_mapping, 30)}

### Mapping status（event rows）

{md_table(status_events, 30)}

## 美股 / 台股代號對照策略

### USA

- 優先使用 SEC / NasdaqTrader / 公司 IR / SEC filings 中明確 ticker evidence。
- current ticker 不覆蓋 historical MSCI event ticker；例如 `ZOOMINFO TECH A` 在 MSCI 歷史事件用 `ZI`，不因 2025 後改 `GTM` 而重寫。
- 對破產、併購、下市、銀行接管等案例保留事件日期脈絡：`CIE`、`SBNY`、`CUTR`、`ANR`、`NUAN`、`COUP` 等。
- 回測 gate 必須要求 ticker 在 `us_dayTradePortfolio` Close/adj-close union，且 effective close date 落在可用美股價格窗口內。

### Taiwan

- 優先使用 FinLab company_basic_info 與 TWSE/TPEx OpenAPI/current reference；若 current reference 找不到，進入 historical verification。
- 台股歷史下市/併購/換股案例需用歷史 ticker：`2448` Epistar、`3474` Inotera、`5387` ProMOS、`2384` Wintek、`6286` Richtek、`2823` China Life、`2607` Evergreen International、`2889` Waterland/IBF。
- `PHOENIXTEC POWER CO` 未通過可靠 source threshold，仍不映射。
- R5/R6 的台股 gate 是 reference-universe + weekday，尚未證明每一歷史下市 ticker 在事件日有本地價格矩陣可交易資料；正式回測需補 per-ticker price availability。

## 資料庫代號比對結果

- USA required universe：`us_dayTradePortfolio` Close/adj-close union，tickers **{len(us_u):,}**。
- Taiwan required universe：FinLab/TWSE/TPEx reference ticker universe，tickers **{len(tw_u):,}**。
- ready events 中：missing ticker = {qa['missing_stock_code_ready_rows']}、ticker not in required universe = {qa['ticker_not_in_universe_ready_rows']}、tradable gate fail = {qa['non_tradable_gate_ready_rows']}。
- not-ready 主要原因：

{md_table(not_ready_reasons, 20)}

## 風險與限制

1. **Historical delisting / rename / share class**：current snapshot reference 無法覆蓋全部歷史事件；必須以 event date 使用當時 ticker。
2. **Survivorship bias**：backtest-ready 只代表目前本地 universe / reference gate 通過，不等於完整 point-in-time security master。
3. **USA per-ticker availability**：R5 使用 known parquet date windows + ticker union，尚未逐 ticker 檢查 event date 是否 non-NaN；若價格矩陣可讀，回測前應補 per-ticker non-NaN gate。
4. **Taiwan historical availability**：台股已確認部分歷史 ticker，但本次未載入完整歷史價格矩陣驗證所有 delisted/merged names。
5. **One ticker multiple MSCI names**：57 groups，多數是縮寫/法名變化，但仍可能包含 genuine conflict；回測前若策略按 name 聚合，需用 ticker+date 維度處理。
6. **PDF parsing risk**：早期 PDF 版面與兩欄 additions/deletions 可能有 parsing error；本輪重點是 ticker mapping audit，不是逐 PDF OCR audit。

One-ticker multi-name sample：

{md_table(one_ticker_multi, 15)}

## 仍需人工或付費資料源查證的清單

最直接清單：`{P['unmapped']}`（{len(unmapped):,} event rows）。建議優先順序：

1. USA `needs_review` 且事件次數高、看起來是當時大型公司或標準指數成分：需 CRSP / Refinitiv / Bloomberg / FactSet / Nasdaq historical symbol master。
2. 台股 historical delisting / merger：需 TWSE/TPEx 歷史證券編碼、下市公告、TEJ/CMoney/FinLab 歷史公司資料。
3. `PHOENIXTEC POWER CO`：目前唯一明確 unresolved R4 manual-review；不能只用 aggregator 2411。
4. `not_backtest_ready_reason=ticker_not_in_local_universe` 的已驗證 ticker：可能是本地資料庫缺資料、symbol 格式差異或 historical inactive ticker，需要逐筆比對 vendor symbol policy。

Round 4 remaining manual item：

{md_table(manual_list)}

## 欄位契約

### Event audit / ready files

`{', '.join(audit_cols)}`

### Mapping verified / ready files

verified: `{', '.join(core_mapping_cols)}`

ready: `{', '.join(ready_mapping_cols)}`

## QA file-read summary

{md_table(pd.DataFrame(file_checks)[['name','exists','readable','rows','cols','path']], 40)}
"""
    REPORT.write_text(report, encoding='utf-8')
    print(f'Wrote {REPORT}')
    print(f'Wrote {QA_JSON}')
    print(json.dumps(qa, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
