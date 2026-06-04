# MSCI ticker mapping audit rounds

## Round 1 — inventory & data join（2026-05-24 00:34 Asia/Taipei）

### 已盤點檔案

- `parsed/msci_us_taiwan_name_ticker_mapping_verified.csv`：4312 rows / 7 cols
- `parsed/msci_us_taiwan_events_flat_verified.csv`：7748 rows / 15 cols
- `parsed/msci_us_taiwan_mapping_verify_candidates.csv`：281 rows / 6 cols
- `parsed/mapping_reference_usa.csv`：22947 rows，15972 unique tickers
- `parsed/mapping_reference_taiwan.csv`：10005 rows，2314 unique tickers

### 主要欄位確認

- mapping：`country, company_name, stock_code, matched_name, mapping_source, mapping_score, mapping_status`
- events_flat：`product, review, issue_date, announcement_date, effective_close_date, country, action, company_name, stock_code, mapping_status, mapping_score, matched_name, mapping_source, source_pdf, row_order`
- candidates：`country, company_name, candidate_stock_code, candidate_matched_name, candidate_score, candidate_source`

### Mapping 狀態統計（唯一公司名稱列）

| country | mapping_status | unique_name_rows |
| --- | --- | --- |
| TAIWAN | mapped_exact_normalized | 116 |
| TAIWAN | needs_review | 373 |
| TAIWAN | verified_tw_reference_fuzzy | 265 |
| USA | mapped_exact_normalized | 1511 |
| USA | needs_review | 2047 |

### Mapping 狀態統計（事件列）

| country | mapping_status | event_rows |
| --- | --- | --- |
| TAIWAN | mapped_exact_normalized | 249 |
| TAIWAN | needs_review | 788 |
| TAIWAN | verified_tw_reference_fuzzy | 511 |
| USA | mapped_exact_normalized | 2953 |
| USA | needs_review | 3247 |

### 本機美股可用 Close ticker universe

找到 `us_dayTradePortfolio`：`/Users/johan/Documents/invest/us_dayTrade_portfolio`。

已從以下 Close / adj_close parquet 欄位抽出 ticker union，共 `22321` 個：

- `/Users/johan/Documents/invest/us_dayTrade_portfolio/data/adjusted/stock_backtest/Close.parquet`：shape=[6607, 21758]，日期=2000-01-03 00:00:00 ~ 2026-04-10 00:00:00，non-all-NA columns=21758，last-row non-NA=6462
- `/Users/johan/Documents/invest/us_dayTrade_portfolio/data/adjusted/stock_live/Close.parquet`：shape=[553, 6633]，日期=2024-01-02 00:00:00 ~ 2026-03-17 00:00:00，non-all-NA columns=6633，last-row non-NA=6439
- `/Users/johan/Documents/invest/us_dayTrade_portfolio/data/finlab/us/us_price_adj_close.parquet`：shape=[2610, 8263]，日期=2016-01-04 00:00:00 ~ 2026-05-19 00:00:00，non-all-NA columns=8263，last-row non-NA=5350
- `/Users/johan/Documents/invest/us_dayTrade_portfolio/data/finlab/us/us_price_close.parquet`：shape=[2611, 8275]，日期=2016-01-04 00:00:00 ~ 2026-05-20 00:00:00，non-all-NA columns=8275，last-row non-NA=5366

輸出：`research_state/us_price_close_universe_tickers.csv`

### 台股 reference universe

使用既有 `parsed/mapping_reference_taiwan.csv`（來源含 FinLab company_basic_info、TWSE OpenAPI、TPEx OpenAPI），ticker-level 去重後 `2314` 個。

- by exchange：`{'TPEx': 887, 'TWSE': 1088, 'otc': 881, 'rotc': 352, 'sii': 1081}`
- by source：`{'FinLab company_basic_info:公司名稱': 2314, 'FinLab company_basic_info:公司簡稱': 2314, 'FinLab company_basic_info:英文簡稱': 2314, 'TPEx OpenAPI mopsfin_t187ap03_O:CompanyName': 887, 'TWSE OpenAPI t187ap03_L:公司名稱': 1088, 'TWSE OpenAPI t187ap03_L:公司簡稱': 1088}`
- 輸出：`research_state/taiwan_reference_universe_tickers.csv`

### 初步 coverage

- USA verified mapped unique codes：1477；在任一美股 Close universe 找到：1466；缺口：11
- Taiwan verified mapped unique codes：359；在台股 reference universe 找到：359；缺口：0

### 上網查證來源設計清單

- US：SEC `company_tickers_exchange.json` / `company_tickers.json`；NasdaqTrader listed + other-listed symbol directory；本機 `us_dayTrade_portfolio` Close/adj_close 欄位作 tradable data universe。
- Taiwan：FinLab `data.get('company_basic_info')` 與 `price:收盤價`；TWSE 證券編碼公告 / ISIN code lists；TPEx Mainboard Companies / OpenAPI。
- 參考頁：TWSE 證券編碼公告、TPEx Mainboard Companies、FinLab data docs。

### Round 1 問題清單（不硬猜）

1. USA `needs_review` 仍高，歷史下市/併購/改名/縮寫/share class 是主要風險。
2. 已映射 USA ticker 和 Close universe 有缺口，下一輪需拆分：格式差異 vs 資料源不含 vs 舊 ticker。
3. 台股 fuzzy verified 仍需逐批用 TWSE/TPEx/FinLab official reference 交叉確認。
4. 台股 reference 多來源多名稱同 ticker，join 前必須 ticker 去重。
5. 目前 reference 多偏 current snapshot，正式回測前需處理歷史 survivorship bias。

### 下一輪待查

- 輸出 verified mapping × universe 的逐列 coverage / missing 清單。
- USA needs_review：設計歷史 symbol verifier，只接受高信心，不自動猜。
- Taiwan needs_review：用 TWSE/TPEx/FinLab alternate English name/abbr 字典，先處理事件次數高者。

### State

- `research_state/msci_ticker_audit_state.json`


## Round 2 — USA high-confidence web verification（2026-05-24 00:47:47 +0800 Asia/Taipei）

### 本輪範圍

- 讀取 state：`research_state/msci_ticker_audit_state.json`
- 針對 USA `needs_review` 中事件次數較高、且可由公司 IR / SEC / Nasdaq 等來源引用者做人工式 web 查證。
- 輸出逐筆查證 CSV：`research_state/msci_ticker_audit_round2_us_web_verification.csv`
- 只把 `confidence >= 0.90` 的公司寫回 `parsed/msci_us_taiwan_name_ticker_mapping_verified.csv` 與 `parsed/msci_us_taiwan_events_flat_verified.csv`；低信心列保留為 `needs_manual_review`。

### Coverage

- 本輪 audited unique USA names：20
- high-confidence verified：19 unique names
- needs_manual_review：1 unique names
- 更新 event rows：112
- high-confidence verified 中，web ticker 在 `us_dayTradePortfolio` Close universe 找到：17/19

### 查證結果（摘要）

| MSCI name | web ticker | DB match | confidence | source |
| --- | --- | --- | --- | --- |
| GANNETT CO | GCI | True | 0.95 | https://www.sec.gov/cgi-bin/browse-edgar?CIK=GCI&action=getcompany&owner=exclude |
| BRIGHTCOVE | BCOV | True | 0.98 | https://investor.brightcove.com/financial-information |
| COMMSCOPE HOLDING CO | COMM | True | 0.98 | https://commscopeholdingcompanyinc.gcs-web.com/news-releases/news-release-details/commscope-reports-fourth-quarter-and-full-year-2024-results |
| CUTERA | CUTR | False | 0.98 | https://ir.cutera.com/news-releases/news-release-details/cuterar-announces-second-quarter-2024-financial-results |
| CHARLES RIVER LABS INTL | CRL | True | 0.99 | https://ir.criver.com/shareholder-services/investor-faqs |
| DICKS SPORTING GOODS | DKS | True | 0.99 | https://investors.dicks.com/resources/investor-faqs/default.aspx |
| CONTAINER STORE GROUP | TCS | True | 0.97 | https://investor.containerstore.com/investor-kit/default.aspx |
| CHESAPEAKE ENERGY CORP | CHK | True | 0.98 | https://www.sec.gov/Archives/edgar/data/895126/000110465924052466/tm244499d2_ars.pdf |
| NUANCE COMMUNICATIONS | NUAN | True | 0.98 | https://www.sec.gov/Archives/edgar/data/1002517/000114036121017650/nt10023637x2_defm14a.htm |
| ZIONS BANCORP | ZION | True | 0.95 | https://www.sec.gov/cgi-bin/browse-edgar?CIK=ZION&action=getcompany&owner=exclude |
| ALPHA NAT RESOURCES | ANR | True | 0.97 | https://www.sec.gov/Archives/edgar/data/1301063/000130106315000048/anr8-k07x17x2015.htm |
| CHIMERIX | CMRX | True | 0.98 | https://ir.chimerix.com/?field_nir_sec_form_group_target_id%5B476%5D=476&field_nir_sec_date_filed_value=&items_per_page=50&promote=All&mobile=1&field_nir_event_start_date_value_2=now&sort_order=ASC&field_nir_event_start_date_value_1=-8%20hours&field_nir_sec_cik_target_id=&items_per_page_toggle=1&order=field_nir_sec_description&sort=asc&&&page=2%2C0%2C0 |
| CELSIUS HLDGS | CELH | True | 0.95 | https://ir.celsiusholdingsinc.com/overview/default.aspx |
| FIRST HORIZON NATIONAL | FHN | True | 0.98 | https://www.nasdaq.com/press-release/first-horizon-announces-parent-company-name-change-2020-11-20 |
| ZOOMINFO TECH A | ZI | True | 0.98 | https://www.sec.gov/Archives/edgar/data/1794515/000179451524000211/zi-20231231.htm |
| CYMABAY THERAPEUTICS | CBAY | True | 0.98 | https://www.sec.gov/Archives/edgar/data/1042074/000119312524031185/d791540dex991.htm |
| CONTINENTAL RESOURCES | CLR | True | 0.94 | https://www.sec.gov/Archives/edgar/data/732834/000095017023018882/R18.htm |
| COUPA SOFTWARE | COUP | True | 0.99 | https://www.sec.gov/Archives/edgar/data/1385867/000119312523054081/d455192d8k.htm |
| SIGNATURE BANK | SBNY | False | 0.96 | https://www.nasdaq.com/press-release/signature-bank-releases-2022-form-10-k-2023-03-02 |
| COBALT INTERNATIONAL | CIE | False | 0.55 | https://www.sec.gov/Archives/edgar/data/1471261/000156459018004275/cie-10k_20171231.htm |

### 疑點 / 下一輪注意

1. `CUTERA` → `CUTR` 來源高信心，但不在本機 Close union；疑似資料源缺口或 delisting/格式問題，需用 backtest/raw vendor symbol history 追查。
2. `SIGNATURE BANK` → `SBNY` 來源高信心，但本機 universe 僅見 `SBN/SBNA/SBNK1/SBNYW` 等相近代號，需查資料庫 vendor 是否改用 receivership/OTC 或舊代碼映射。
3. `COBALT INTERNATIONAL` → `CIE` 目前來源確認公司與 NYSE common stock，但未抓到明確 trading symbol 文字；保留 `needs_manual_review`，未寫回主 mapping。
4. `ZOOMINFO TECH A` 需採歷史 ticker `ZI`；公司 IR 目前顯示 `GTM`，不可用 current ticker 覆蓋舊 MSCI 事件。
5. `CHESAPEAKE ENERGY CORP`、`NUANCE`、`COUPA`、`CYMABAY`、`CONTINENTAL RESOURCES` 都有併購/下市/更名脈絡，回測時必須按事件日期使用當時 ticker，不可只用 current snapshot。

### Round 2 後 mapping 狀態（unique name rows）

| country | mapping_status | unique_name_rows |
| --- | --- | --- |
| TAIWAN | mapped_exact_normalized | 116 |
| TAIWAN | needs_review | 373 |
| TAIWAN | verified_tw_reference_fuzzy | 265 |
| USA | mapped_exact_normalized | 1511 |
| USA | needs_review | 2028 |
| USA | verified_us_web_high_confidence | 19 |

### Round 2 後 events 狀態（event rows）

| country | mapping_status | event_rows |
| --- | --- | --- |
| TAIWAN | mapped_exact_normalized | 249 |
| TAIWAN | needs_review | 788 |
| TAIWAN | verified_tw_reference_fuzzy | 511 |
| USA | mapped_exact_normalized | 2953 |
| USA | needs_review | 3135 |
| USA | verified_us_web_high_confidence | 112 |


## Round 3 — Taiwan FinLab/TWSE/TPEx official verification

- Output: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round3_taiwan_official_verification.csv`
- Audited unique Taiwan names: 51；verified: 41；conflict corrected: 1；manual_review: 9。
- Updated verified/conflict event rows: 163；tagged manual_review event rows: 27。
- Notable conflict: `SINCERE NAVIGATION` was previously fuzzy-mapped to 6721 (Sincere group / 信實保全); corrected to 2605 (新興航運 / SNC) based on FinLab + TWSE reference.
- Remaining manual_review examples: historical/delisted or ambiguous names such as EPISTAR, INOTERA, PRO MOS, WINTEK, CHINA LIFE, RICHTEK, WATERLAND FINANCIAL, EVERGREEN INTERNATIONAL.


## Round 4 — Conflict/manual review historical symbol check (2026-05-24)

Focus: prior `conflict` / `manual_review` USA and Taiwan items, with second-source checks for renames, mergers, delistings, share swaps, ADR/share-class ambiguity, and historical tickers. Output file: `research_state/msci_ticker_audit_round4_conflict_review.csv`.

### Results

- Reviewed 14 doubtful items.
- Mapped/confirmed 13 items with at least two corroborating sources.
- Remaining manual review: `PHOENIXTEC POWER CO` — evidence supports Phoenixtec/Eaton identity and acquisition context, but the only discovered ticker evidence (`2411`) is aggregator-level and not backed by a reliable TWSE/TPEx/security-master archive; left unmapped to avoid false historical mapping.
- Corrected/confirmed Taiwan historical tickers: Sincere Navigation `2605`, Evergreen International Storage & Transport `2607`, Waterland/IBF Financial `2889`, China Life Insurance Taiwan `2823`, Epistar `2448`, Inotera `3474`, ProMOS `5387`, Wintek `2384`, Richtek `6286`.
- Corrected/confirmed USA historical tickers: Cobalt International Energy `CIE`, Cutera `CUTR`, Signature Bank `SBNY`, ZoomInfo Class A `ZI` (changed to `GTM` only after 2025-05-13).

### Risk notes

- For US delisted names, do not join by current ticker alone: `CIE`, `SBNY`, `CUTR`, and renamed `ZI/GTM` require event-date-aware symbol history.
- Taiwan current reference files miss many delisted/absorbed companies; future rounds should add a Taiwan historical security master or TWSE/TPEx delisting archive extraction.
- Phoenixtec remains the main unresolved Round 4 gap.


## Round 5 — Full consistency checks & backtest-ready exports (2026-05-24 04:12:24 )

### Scope

- Full-table consistency audit over current verified mapping/events.
- Checks: unique company-name coverage, event-row coverage, same-name multi-ticker, one-ticker multi-name, USA ticker presence in `us_dayTradePortfolio` Close union, Taiwan ticker presence in FinLab/TWSE/TPEx reference universe, event-date tradability gate, mapped/unmapped distribution.
- Original raw/parser files were not deleted.

### Outputs

- Backtest-ready verified mapping: `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_name_ticker_mapping_verified_backtest_ready.csv`
- Event table with audit columns: `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat_audit_verified.csv`
- Backtest-ready event subset: `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat_backtest_ready.csv`
- Unmapped/manual-review/not-ready list: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_unmapped_manual_review.csv`
- Source evidence table: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_source_evidence_table.csv`
- Machine-readable checks: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_consistency_checks.json`

### Headline counts

- Unique company mapping rows: 4,312; backtest-ready mapping rows: 1,941.
- Event rows: 7,748; backtest-ready event rows: 3,855; not-ready rows: 3,893.
- Backtest-ready events by country: USA 2,931; Taiwan 924.
- Not-ready events by country: USA 3,269; Taiwan 624.
- Same company-name mapped to multiple tickers: 0 mapping rows/groups.
- One ticker mapped to multiple MSCI names: 57 ticker groups (mostly legal-name variants / historical naming; see JSON top100).

### Backtest-ready gate used

`backtest_ready = verified mapping status + non-empty stock_code + ticker present in required local universe + effective_close_date tradable gate`.

- USA required universe: `research_state/us_price_close_universe_tickers.csv` from `us_dayTradePortfolio` Close/adj-close union.
- Taiwan required universe: `research_state/taiwan_reference_universe_tickers.csv` from FinLab/TWSE/TPEx reference universe.
- Event-date gate: effective close date must be a weekday; USA also must fall inside at least one known available US Close data date window. Taiwan historical per-ticker price matrix was not loaded in R5, so Taiwan date gate is weekday + code reference presence.

### Main not-ready reasons

- 3,713: `mapping_status=needs_review;missing_stock_code`
- 102: `effective_close_date_outside_available_us_price_windows`
- 59: `ticker_not_in_local_universe`
- 18: `mapping_status=needs_review;missing_stock_code;effective_close_date_outside_available_us_price_windows`
- 1: `mapping_status=manual_review_round4;missing_stock_code`


## Round 5 — Full consistency checks & backtest-ready exports (2026-06-04 10:02:19 )

### Scope

- Full-table consistency audit over current verified mapping/events.
- Checks: unique company-name coverage, event-row coverage, same-name multi-ticker, one-ticker multi-name, USA ticker presence in `us_dayTradePortfolio` Close union, Taiwan ticker presence in FinLab/TWSE/TPEx reference universe, event-date tradability gate, mapped/unmapped distribution.
- Original raw/parser files were not deleted.

### Outputs

- Backtest-ready verified mapping: `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_name_ticker_mapping_verified_backtest_ready.csv`
- Event table with audit columns: `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat_audit_verified.csv`
- Backtest-ready event subset: `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat_backtest_ready.csv`
- Unmapped/manual-review/not-ready list: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_unmapped_manual_review.csv`
- Source evidence table: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_source_evidence_table.csv`
- Machine-readable checks: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_consistency_checks.json`

### Headline counts

- Unique company mapping rows: 4,312; backtest-ready mapping rows: 2,139.
- Event rows: 7,748; backtest-ready event rows: 4,248; not-ready rows: 3,500.
- Backtest-ready events by country: USA 2,931; Taiwan 1,317.
- Not-ready events by country: USA 3,269; Taiwan 231.
- Same company-name mapped to multiple tickers: 0 mapping rows/groups.
- One ticker mapped to multiple MSCI names: 61 ticker groups (mostly legal-name variants / historical naming; see JSON top100).

### Backtest-ready gate used

`backtest_ready = verified mapping status + non-empty stock_code + ticker present in required local universe + effective_close_date tradable gate`.

- USA required universe: `research_state/us_price_close_universe_tickers.csv` from `us_dayTradePortfolio` Close/adj-close union.
- Taiwan required universe: `research_state/taiwan_reference_universe_tickers.csv` from FinLab/TWSE/TPEx reference universe.
- Event-date gate: effective close date must be a weekday; USA also must fall inside at least one known available US Close data date window. Taiwan historical per-ticker price matrix was not loaded in R5, so Taiwan date gate is weekday + code reference presence.

### Main not-ready reasons

- 3,269: `mapping_status=needs_review;missing_stock_code`
- 110: `ticker_not_in_local_universe`
- 102: `effective_close_date_outside_available_us_price_windows`
- 18: `mapping_status=needs_review;missing_stock_code;effective_close_date_outside_available_us_price_windows`
- 1: `mapping_status=manual_review_round4;missing_stock_code`


## Round 5 — Full consistency checks & backtest-ready exports (2026-06-04 10:05:06 )

### Scope

- Full-table consistency audit over current verified mapping/events.
- Checks: unique company-name coverage, event-row coverage, same-name multi-ticker, one-ticker multi-name, USA ticker presence in `us_dayTradePortfolio` Close union, Taiwan ticker presence in FinLab/TWSE/TPEx reference universe, event-date tradability gate, mapped/unmapped distribution.
- Original raw/parser files were not deleted.

### Outputs

- Backtest-ready verified mapping: `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_name_ticker_mapping_verified_backtest_ready.csv`
- Event table with audit columns: `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat_audit_verified.csv`
- Backtest-ready event subset: `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat_backtest_ready.csv`
- Unmapped/manual-review/not-ready list: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_unmapped_manual_review.csv`
- Source evidence table: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_source_evidence_table.csv`
- Machine-readable checks: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_consistency_checks.json`

### Headline counts

- Unique company mapping rows: 4,312; backtest-ready mapping rows: 2,142.
- Event rows: 7,748; backtest-ready event rows: 4,254; not-ready rows: 3,494.
- Backtest-ready events by country: USA 2,931; Taiwan 1,323.
- Not-ready events by country: USA 3,269; Taiwan 225.
- Same company-name mapped to multiple tickers: 0 mapping rows/groups.
- One ticker mapped to multiple MSCI names: 61 ticker groups (mostly legal-name variants / historical naming; see JSON top100).

### Backtest-ready gate used

`backtest_ready = verified mapping status + non-empty stock_code + ticker present in required local universe + effective_close_date tradable gate`.

- USA required universe: `research_state/us_price_close_universe_tickers.csv` from `us_dayTradePortfolio` Close/adj-close union.
- Taiwan required universe: `research_state/taiwan_reference_universe_tickers.csv` from FinLab/TWSE/TPEx reference universe.
- Event-date gate: effective close date must be a weekday; USA also must fall inside at least one known available US Close data date window. Taiwan historical per-ticker price matrix was not loaded in R5, so Taiwan date gate is weekday + code reference presence.

### Main not-ready reasons

- 3,254: `mapping_status=needs_review;missing_stock_code`
- 119: `ticker_not_in_local_universe`
- 102: `effective_close_date_outside_available_us_price_windows`
- 18: `mapping_status=needs_review;missing_stock_code;effective_close_date_outside_available_us_price_windows`
- 1: `mapping_status=manual_review_round4;missing_stock_code`


## Round 5 — Full consistency checks & backtest-ready exports (2026-06-04 10:25:43 )

### Scope

- Full-table consistency audit over current verified mapping/events.
- Checks: unique company-name coverage, event-row coverage, same-name multi-ticker, one-ticker multi-name, USA ticker presence in `us_dayTradePortfolio` Close union, Taiwan ticker presence in FinLab/TWSE/TPEx reference universe, event-date tradability gate, mapped/unmapped distribution.
- Original raw/parser files were not deleted.

### Outputs

- Backtest-ready verified mapping: `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_name_ticker_mapping_verified_backtest_ready.csv`
- Event table with audit columns: `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat_audit_verified.csv`
- Backtest-ready event subset: `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat_backtest_ready.csv`
- Unmapped/manual-review/not-ready list: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_unmapped_manual_review.csv`
- Source evidence table: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_source_evidence_table.csv`
- Machine-readable checks: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_consistency_checks.json`

### Headline counts

- Unique company mapping rows: 4,312; backtest-ready mapping rows: 2,182.
- Event rows: 7,748; backtest-ready event rows: 4,327; not-ready rows: 3,421.
- Backtest-ready events by country: USA 2,931; Taiwan 1,396.
- Not-ready events by country: USA 3,269; Taiwan 152.
- Same company-name mapped to multiple tickers: 0 mapping rows/groups.
- One ticker mapped to multiple MSCI names: 76 ticker groups (mostly legal-name variants / historical naming; see JSON top100).

### Backtest-ready gate used

`backtest_ready = verified mapping status + non-empty stock_code + ticker present in required local universe + effective_close_date tradable gate`.

- USA required universe: `research_state/us_price_close_universe_tickers.csv` from `us_dayTradePortfolio` Close/adj-close union.
- Taiwan required universe: `research_state/taiwan_reference_universe_tickers.csv` from FinLab/TWSE/TPEx reference universe.
- Event-date gate: effective close date must be a weekday; USA also must fall inside at least one known available US Close data date window. Taiwan historical per-ticker price matrix was not loaded in R5, so Taiwan date gate is weekday + code reference presence.

### Main not-ready reasons

- 3,111: `mapping_status=needs_review;missing_stock_code`
- 158: `ticker_not_in_local_universe`
- 102: `effective_close_date_outside_available_us_price_windows`
- 25: `mapping_status=verified_tw_yahoo_round8b`
- 18: `mapping_status=needs_review;missing_stock_code;effective_close_date_outside_available_us_price_windows`
- 5: `mapping_status=verified_tw_reit_round8`
- 2: `mapping_status=verified_tw_yahoo_round8`


## Round 5 — Full consistency checks & backtest-ready exports (2026-06-04 10:26:04 )

### Scope

- Full-table consistency audit over current verified mapping/events.
- Checks: unique company-name coverage, event-row coverage, same-name multi-ticker, one-ticker multi-name, USA ticker presence in `us_dayTradePortfolio` Close union, Taiwan ticker presence in FinLab/TWSE/TPEx reference universe, event-date tradability gate, mapped/unmapped distribution.
- Original raw/parser files were not deleted.

### Outputs

- Backtest-ready verified mapping: `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_name_ticker_mapping_verified_backtest_ready.csv`
- Event table with audit columns: `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat_audit_verified.csv`
- Backtest-ready event subset: `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat_backtest_ready.csv`
- Unmapped/manual-review/not-ready list: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_unmapped_manual_review.csv`
- Source evidence table: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_source_evidence_table.csv`
- Machine-readable checks: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_consistency_checks.json`

### Headline counts

- Unique company mapping rows: 4,312; backtest-ready mapping rows: 2,200.
- Event rows: 7,748; backtest-ready event rows: 4,354; not-ready rows: 3,394.
- Backtest-ready events by country: USA 2,931; Taiwan 1,423.
- Not-ready events by country: USA 3,269; Taiwan 125.
- Same company-name mapped to multiple tickers: 0 mapping rows/groups.
- One ticker mapped to multiple MSCI names: 76 ticker groups (mostly legal-name variants / historical naming; see JSON top100).

### Backtest-ready gate used

`backtest_ready = verified mapping status + non-empty stock_code + ticker present in required local universe + effective_close_date tradable gate`.

- USA required universe: `research_state/us_price_close_universe_tickers.csv` from `us_dayTradePortfolio` Close/adj-close union.
- Taiwan required universe: `research_state/taiwan_reference_universe_tickers.csv` from FinLab/TWSE/TPEx reference universe.
- Event-date gate: effective close date must be a weekday; USA also must fall inside at least one known available US Close data date window. Taiwan historical per-ticker price matrix was not loaded in R5, so Taiwan date gate is weekday + code reference presence.

### Main not-ready reasons

- 3,111: `mapping_status=needs_review;missing_stock_code`
- 163: `ticker_not_in_local_universe`
- 102: `effective_close_date_outside_available_us_price_windows`
- 18: `mapping_status=needs_review;missing_stock_code;effective_close_date_outside_available_us_price_windows`
