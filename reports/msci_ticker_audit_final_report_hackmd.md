# MSCI ticker mapping audit final report — Round 6 QA signoff

###### tags: `MSCI` `台股` `美股` `ticker-mapping` `research`

Generated: 2026-05-24T04:34:13+08:00 Asia/Taipei  
Project root: `/Users/johan/Documents/invest/msci_index_reviews`

## 結論 / QA signoff

**結論：可交付，但只應先用 `backtest_ready=true` 的事件檔做回測。** 總事件列 7,748，backtest-ready 3,855（49.8%），not-ready 3,893。美股 ready 2,931、台股 ready 924；期間約 2006-05-31 至 2026-05-29，涵蓋 129 份 source PDF、129 個 product-review 批次。

Round 6 重新檢查輸出檔案可讀性、欄位一致性、ready subset 是否等於 audit table 中 `backtest_ready=true`，以及 ready rows 是否仍有空 ticker / 未驗證 / 不在本地 universe / event-date gate 未通過。QA 結果：

- all files readable: **True**
- event audit columns consistent: **True**
- event ready columns consistent: **True**
- mapping ready columns consistent: **True**
- ready subset count matches audit: **True**
- not-ready list count matches audit: **True**
- ready rows with missing ticker: **0**
- ready rows not verified: **0**
- ready rows ticker not in universe: **0**
- ready rows failing tradable gate: **0**

Machine-readable QA: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round6_final_qa.json`

## 可直接用於回測的檔案

1. **事件主檔（建議回測入口）**  
   `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat_backtest_ready.csv`  
   - rows: 3,855
   - 欄位：原始事件欄位 + mapping/audit gate 欄位
   - 條件：`verified_mapping=true`、`stock_code` 非空、ticker 在本地 universe、`event_date_tradable_gate=true`

2. **完整事件檔 + audit 欄位（用於診斷 / 改 gate）**  
   `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat_audit_verified.csv`  
   - rows: 7,748
   - 包含 `backtest_ready` 與 `not_backtest_ready_reason`

3. **backtest-ready company mapping**  
   `/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_name_ticker_mapping_verified_backtest_ready.csv`  
   - rows: 1,941

4. **not-ready / manual review 清單**  
   `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_unmapped_manual_review.csv`  
   - rows: 3,893

5. **source evidence table**  
   `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_source_evidence_table.csv`  
   - rows: 4,397

## 方法

1. 從 MSCI public list PDFs 解析 Standard / Small Cap 的 USA / TAIWAN additions / deletions，保留 `issue_date`、`announcement_date`、`effective_close_date`、`product`、`review`、`country`、`action`、`company_name`、`source_pdf`。
2. 初始 name → ticker mapping 採保守 exact-normalized：
   - USA：SEC company tickers / NasdaqTrader 類 reference。
   - Taiwan：FinLab company_basic_info + TWSE/TPEx OpenAPI 類 reference。
3. 對 `needs_review`、高事件數、衝突與 manual-review 標的進行分輪 web / official / historical verification；只在有高信心或多來源佐證時寫回 ticker。
4. R5 產生 backtest-ready gate：verified mapping + non-empty ticker + ticker exists in required local universe + event-date tradability gate。
5. R6 只做最終 QA 與報告，不硬猜尚未驗證 ticker。

## 資料源

- MSCI public list PDFs：`/Users/johan/Documents/invest/msci_index_reviews/pdf`（本研究事件主體為 `stdindex` 與 `smallcap` 下 USA / TAIWAN rows）
- parser metadata：`/Users/johan/Documents/invest/msci_index_reviews/parsed/msci_pdf_review_metadata.csv`（rows: 161）
- USA reference：`/Users/johan/Documents/invest/msci_index_reviews/parsed/mapping_reference_usa.csv`；本地價格 universe：`/Users/johan/Documents/invest/msci_index_reviews/research_state/us_price_close_universe_tickers.csv`（tickers: 22,321）
- Taiwan reference：`/Users/johan/Documents/invest/msci_index_reviews/parsed/mapping_reference_taiwan.csv`；本地 reference universe：`/Users/johan/Documents/invest/msci_index_reviews/research_state/taiwan_reference_universe_tickers.csv`（tickers: 2,314）
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

| msci_name | web_ticker | db_ticker_match | confidence | audit_status | notes |
| --- | --- | --- | --- | --- | --- |
| CHARLES RIVER LABS INTL | CRL | True | 0.99 | verified_us_web_high_confidence | Company IR FAQ states it trades on NYSE under ticker symbol CRL. |
| COUPA SOFTWARE | COUP | True | 0.99 | verified_us_web_high_confidence | SEC 8-K lists common stock trading symbol COUP on Nasdaq and notes delisting after Thoma Bravo acquisition. |
| DICKS SPORTING GOODS | DKS | True | 0.99 | verified_us_web_high_confidence | Company IR FAQ lists Exchange & Ticker as NYSE: DKS. |
| BRIGHTCOVE | BCOV | True | 0.98 | verified_us_web_high_confidence | Company IR earnings release states Brightcove Inc. (Nasdaq: BCOV); 10-K excerpt confirms common stock BCOV on Nasdaq. |
| CHESAPEAKE ENERGY CORP | CHK | True | 0.98 | verified_us_web_high_confidence | SEC annual report states common stock trading symbol CHK on Nasdaq; later merged into Expand Energy context should be handled historically. |
| CHIMERIX | CMRX | True | 0.98 | verified_us_web_high_confidence | Company IR FAQ states ticker CMRX, traded on Nasdaq Global Market; later Jazz acquisition noted separately. |
| COMMSCOPE HOLDING CO | COMM | True | 0.98 | verified_us_web_high_confidence | Company IR/SEC annual report identify CommScope Holding Company, Inc. ticker COMM on Nasdaq. |
| CUTERA | CUTR | False | 0.98 | verified_us_web_high_confidence | Company IR release states Cutera, Inc. (Nasdaq: CUTR); later 2025 restructuring/delisting explains current-data absence risk. |

### Round 3 — Taiwan FinLab/TWSE/TPEx official verification

- audited 51 個 Taiwan names；verified 41、conflict corrected 1、manual_review 9。
- 重要修正：`SINCERE NAVIGATION` 由 fuzzy 誤配 6721 改為 2605。

### Round 4 — conflict/manual review historical symbol check

- reviewed 14 個疑點；13 個以至少兩個來源 mapped/confirmed。
- 剩餘 manual review：`PHOENIXTEC POWER CO`，不採 aggregator-only 2411 證據。

R4 抽樣 / 全部疑點摘要：

| country | company_name | decision | verified_ticker | status | risk_type | evidence_summary |
| --- | --- | --- | --- | --- | --- | --- |
| TAIWAN | SINCERE NAVIGATION | map | 2605 | verified_conflict_round4 | prior fuzzy conflict | Company investor FAQ lists TAIEX/TWSE 2605; market quote pages corroborate 2605.TW/TW0002605003. Prior 6721-style fuzzy conflict should stay corrected to 2605. |
| TAIWAN | EVERGREEN INTERNATIONAL | map | 2607 | verified_historical_round4 | abbreviated MSCI name | MSCI abbreviation likely drops Storage & Transport; FT/Yahoo/StockAnalysis all identify Evergreen International Storage & Transport as 2607 on Taiwan/TWSE. |
| TAIWAN | WATERLAND FINANCIAL | map | 2889 | verified_historical_round4 | renamed company | FT and MarketScreener state IBF Financial Holdings (2889) was formerly Waterland Financial Holdings; Investing.com URL retains waterland-fin slug for 2889. |
| TAIWAN | CHINA LIFE INSURANCE CO | map | 2823 | verified_historical_round4 | delisted after share swap; same-name China/HK risk | KGI Life/China Life company profile says listed on TWSE in 1995 and became CDF wholly owned subsidiary in 2021; Cbonds identifies Taiwan China Life ordinary share TW0002823002 ticker 2823; local press says 2823 delisted 2021-12-30. |
| TAIWAN | EPISTAR CORP | map | 2448 | verified_historical_round4 | share conversion / delisted into Ennostar | Ennostar company release identifies Epistar (TAIEX:2448); LEDinside notes former stock code 2448 and Ennostar listed as 3714 after share swap. |
| TAIWAN | INOTERA MEMORIES | map | 3474 | verified_historical_round4 | acquired/delisted | Prior source noted Inotera (TWSE:3474); Digitimes and CTIMES/Micron sources corroborate delisting/acquisition by Micron. |
| TAIWAN | PRO MOS TECHNOLOGIES | map | 5387 | verified_historical_round4 | OTC delisted | Focus Taiwan states ProMOS shares delisted from OTC March 26, 2012; MarketScreener inactive instrument lists ProMOS Technologies Inc. 5387 TW0005387005 on Taipei Exchange. |
| TAIWAN | WINTEK | map | 2384 | verified_historical_round4 | bankruptcy/delisted | TWSE fact book lists code 2384 WINTEK CORPORTION delisted 07/07; MarketScreener inactive instrument lists Wintek Corporation 2384 TW0002384005; other local company data retains 2384 勝華科技. |
| TAIWAN | RICHTEK TECHNOLOGY CORP | map | 6286 | verified_historical_round4 | acquired/delisted | MediaTek official release identifies Richtek Technology Corporation (TSE:6286) and acquisition plan; Digitimes says Richtek delisted from TSE on 2016-04-29; Richtek report says it became wholly owned by MediaTek. |
| TAIWAN | PHOENIXTEC POWER CO | manual_review |  | manual_review_round4 | weak historical symbol evidence | Multiple sources support Eaton acquisition and Phoenixtec identity; only one weak data aggregator surfaced stock symbol 2411/ROCO and no reliable TWSE/TPEx historical symbol page was found. Do not map to 2411 yet. |
| USA | COBALT INTERNATIONAL | map | CIE | verified_historical_round4 | historical US ticker / delisted; avoid current same-symbol reuse | SEC filings/press releases explicitly identify Cobalt International Energy, Inc. (NYSE:CIE); NYSE/SEC removal filing confirms Cobalt common stock delisting/removal in Jan 2018. |
| USA | CUTERA | map | CUTR | verified_historical_round4 | 2025 bankruptcy/delisting | Company release and SEC 8-K/Form 25 confirm Nasdaq ticker CUTR and 2025 delisting/suspension context; historical MSCI rows should remain CUTR, not post-bankruptcy OTC substitute. |
| USA | SIGNATURE BANK | map | SBNY | verified_historical_round4 | failed bank / delisted; OTC continuation risk | Nasdaq-hosted company release and FDIC closure/receiver sources confirm historical Signature Bank context; use SBNY for pre-failure MSCI history and avoid treating bridge/Flagstar successor as same equity. |
| USA | ZOOMINFO TECH A | map | ZI | verified_historical_round4 | ticker changed to GTM after MSCI window | SEC 2024 10-K supported ZI; SEC 2025 8-K/BusinessWire state Nasdaq symbol changed from ZI to GTM effective 2025-05-13. Historical MSCI events through 2023 should remain ZI. |

### Round 5 — full consistency checks & backtest-ready exports

- 完整事件列 7,748；backtest-ready 3,855；not-ready 3,893。
- same company-name mapped to multiple tickers：0。
- one ticker mapped to multiple MSCI names：57 groups，多為 legal-name variants / historical naming，但仍需回測前注意。
- 產出 ready event/mapping、audit event、not-ready、evidence、machine-readable consistency JSON。

### Round 6 — final QA signoff

- 重新讀取所有最終輸出，確認欄位一致與 counts 對齊。
- 抽樣檢查 high-confidence / conflict / manual-review 案例，未發現需要推翻 R5 gate 的新問題。
- 輸出本 final report 與 `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round6_final_qa.json`。

## Coverage 數字

### By country × backtest_ready

| country | backtest_ready | rows | pct_of_country |
| --- | --- | --- | --- |
| TAIWAN | false | 624 | 40.3 |
| TAIWAN | true | 924 | 59.7 |
| USA | false | 3269 | 52.7 |
| USA | true | 2931 | 47.3 |

### By country × product × action × backtest_ready

| country | product | action | backtest_ready | rows |
| --- | --- | --- | --- | --- |
| TAIWAN | small_cap | addition | false | 275 |
| TAIWAN | small_cap | addition | true | 368 |
| TAIWAN | small_cap | deletion | false | 278 |
| TAIWAN | small_cap | deletion | true | 352 |
| TAIWAN | standard | addition | false | 29 |
| TAIWAN | standard | addition | true | 88 |
| TAIWAN | standard | deletion | false | 42 |
| TAIWAN | standard | deletion | true | 116 |
| USA | small_cap | addition | false | 1596 |
| USA | small_cap | addition | true | 1378 |
| USA | small_cap | deletion | false | 1193 |
| USA | small_cap | deletion | true | 935 |
| USA | standard | addition | false | 245 |
| USA | standard | addition | true | 346 |
| USA | standard | deletion | false | 235 |
| USA | standard | deletion | true | 272 |

### Mapping status（unique company rows）

| country | mapping_status | unique_company_rows |
| --- | --- | --- |
| TAIWAN | manual_review_round4 | 1 |
| TAIWAN | mapped_exact_normalized | 116 |
| TAIWAN | needs_review | 323 |
| TAIWAN | verified_conflict_round4 | 1 |
| TAIWAN | verified_historical_round4 | 8 |
| TAIWAN | verified_tw_official_round3 | 41 |
| TAIWAN | verified_tw_reference_fuzzy | 264 |
| USA | mapped_exact_normalized | 1511 |
| USA | needs_review | 2027 |
| USA | verified_historical_round4 | 4 |
| USA | verified_us_web_high_confidence | 16 |

### Mapping status（event rows）

| country | mapping_status | event_rows |
| --- | --- | --- |
| TAIWAN | manual_review_round4 | 1 |
| TAIWAN | mapped_exact_normalized | 249 |
| TAIWAN | needs_review | 602 |
| TAIWAN | verified_conflict_round4 | 4 |
| TAIWAN | verified_historical_round4 | 26 |
| TAIWAN | verified_tw_official_round3 | 159 |
| TAIWAN | verified_tw_reference_fuzzy | 507 |
| USA | mapped_exact_normalized | 2953 |
| USA | needs_review | 3129 |
| USA | verified_historical_round4 | 23 |
| USA | verified_us_web_high_confidence | 95 |

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

- USA required universe：`us_dayTradePortfolio` Close/adj-close union，tickers **22,321**。
- Taiwan required universe：FinLab/TWSE/TPEx reference ticker universe，tickers **2,314**。
- ready events 中：missing ticker = 0、ticker not in required universe = 0、tradable gate fail = 0。
- not-ready 主要原因：

| not_backtest_ready_reason | rows |
| --- | --- |
| mapping_status=needs_review;missing_stock_code | 3713 |
| effective_close_date_outside_available_us_price_windows | 102 |
| ticker_not_in_local_universe | 59 |
| mapping_status=needs_review;missing_stock_code;effective_close_date_outside_available_us_price_windows | 18 |
| mapping_status=manual_review_round4;missing_stock_code | 1 |

## 風險與限制

1. **Historical delisting / rename / share class**：current snapshot reference 無法覆蓋全部歷史事件；必須以 event date 使用當時 ticker。
2. **Survivorship bias**：backtest-ready 只代表目前本地 universe / reference gate 通過，不等於完整 point-in-time security master。
3. **USA per-ticker availability**：R5 使用 known parquet date windows + ticker union，尚未逐 ticker 檢查 event date 是否 non-NaN；若價格矩陣可讀，回測前應補 per-ticker non-NaN gate。
4. **Taiwan historical availability**：台股已確認部分歷史 ticker，但本次未載入完整歷史價格矩陣驗證所有 delisted/merged names。
5. **One ticker multiple MSCI names**：57 groups，多數是縮寫/法名變化，但仍可能包含 genuine conflict；回測前若策略按 name 聚合，需用 ticker+date 維度處理。
6. **PDF parsing risk**：早期 PDF 版面與兩欄 additions/deletions 可能有 parsing error；本輪重點是 ticker mapping audit，不是逐 PDF OCR audit。

One-ticker multi-name sample：

| country | stock_code | name_count | company_names |
| --- | --- | --- | --- |
| TAIWAN | 3707 | 3 | EPISIL PRECISION\|EPISIL TECHNOLOGIES\|EPISIL TECHNOLOGIES INC |
| TAIWAN | 1337 | 2 | ASIA PLASTIC RECYCLE\|ASIA PLASTIC RECYCLING |
| TAIWAN | 1605 | 2 | WALSIN LIHWA CORP\|WALSIN TECHNOLOGY CORP |
| TAIWAN | 1702 | 2 | NAMCHOW CHEMICAL INDUST\|NAMCHOW HOLDINGS CO |
| TAIWAN | 1785 | 2 | NEO SOLAR POWER CORP\|SOLAR APPLIED MATRLS |
| TAIWAN | 2049 | 2 | HIWIN MIKROSYSTEM CORP\|HIWIN TECHNOLOGIES CORP |
| TAIWAN | 2324 | 2 | COMPAL COMMUNICATIONS\|COMPAL ELECTRONICS |
| TAIWAN | 2359 | 2 | SOLOMON TECH CORP\|SOLOMON TECHNOLOGY |
| TAIWAN | 2371 | 2 | TATUNG\|TATUNG FINE CHEMICAL CO |
| TAIWAN | 2408 | 2 | NANYA TECHNOLOGY\|NANYA TECHNOLOGY CORP |
| TAIWAN | 2428 | 2 | THINKING ELECTRONIC IND\|THINKING ELECTRONIC INDL |
| TAIWAN | 3176 | 2 | MEDIGEN BIOTECHNOLOGY\|MEDIGEN VACCINE |

## 仍需人工或付費資料源查證的清單

最直接清單：`/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_unmapped_manual_review.csv`（3,893 event rows）。建議優先順序：

1. USA `needs_review` 且事件次數高、看起來是當時大型公司或標準指數成分：需 CRSP / Refinitiv / Bloomberg / FactSet / Nasdaq historical symbol master。
2. 台股 historical delisting / merger：需 TWSE/TPEx 歷史證券編碼、下市公告、TEJ/CMoney/FinLab 歷史公司資料。
3. `PHOENIXTEC POWER CO`：目前唯一明確 unresolved R4 manual-review；不能只用 aggregator 2411。
4. `not_backtest_ready_reason=ticker_not_in_local_universe` 的已驗證 ticker：可能是本地資料庫缺資料、symbol 格式差異或 historical inactive ticker，需要逐筆比對 vendor symbol policy。

Round 4 remaining manual item：

| country | company_name | status | unverifiable_reason |
| --- | --- | --- | --- |
| TAIWAN | PHOENIXTEC POWER CO | manual_review_round4 | No reliable official/exchange or historical security-master source confirming Phoenixtec Power listed ticker; aggregator-only stock symbol not sufficient. |

## 欄位契約

### Event audit / ready files

`product, review, issue_date, announcement_date, effective_close_date, country, action, company_name, stock_code, mapping_status, mapping_score, matched_name, mapping_source, source_pdf, row_order, verified_mapping, mapping_backtest_ready, universe_checked, ticker_in_required_universe, issue_date_weekday, announcement_date_weekday, effective_close_date_weekday, effective_close_date_price_window_ok, event_date_tradable_gate, backtest_ready, not_backtest_ready_reason`

### Mapping verified / ready files

verified: `country, company_name, stock_code, matched_name, mapping_source, mapping_score, mapping_status`

ready: `country, company_name, stock_code, matched_name, mapping_source, mapping_score, mapping_status, is_verified_mapping, universe_match, universe_checked, backtest_ready_mapping`

## QA file-read summary

| name | exists | readable | rows | cols | path |
| --- | --- | --- | --- | --- | --- |
| mapping_raw | True | True | 4312.0 | 7.0 | /Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_name_ticker_mapping.csv |
| events_raw | True | True | 7748.0 | 15.0 | /Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat.csv |
| mapping_verified | True | True | 4312.0 | 7.0 | /Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_name_ticker_mapping_verified.csv |
| events_verified | True | True | 7748.0 | 15.0 | /Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat_verified.csv |
| events_audit | True | True | 7748.0 | 26.0 | /Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat_audit_verified.csv |
| mapping_ready | True | True | 1941.0 | 11.0 | /Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_name_ticker_mapping_verified_backtest_ready.csv |
| events_ready | True | True | 3855.0 | 26.0 | /Users/johan/Documents/invest/msci_index_reviews/parsed/msci_us_taiwan_events_flat_backtest_ready.csv |
| unmapped | True | True | 3893.0 | 26.0 | /Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_unmapped_manual_review.csv |
| evidence | True | True | 4397.0 | 11.0 | /Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_source_evidence_table.csv |
| checks | True | True |  |  | /Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round5_consistency_checks.json |
| round2 | True | True | 20.0 | 10.0 | /Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round2_us_web_verification.csv |
| round3 | True | True | 51.0 | 11.0 | /Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round3_taiwan_official_verification.csv |
| round4 | True | True | 14.0 | 12.0 | /Users/johan/Documents/invest/msci_index_reviews/research_state/msci_ticker_audit_round4_conflict_review.csv |
| us_universe | True | True | 22321.0 | 1.0 | /Users/johan/Documents/invest/msci_index_reviews/research_state/us_price_close_universe_tickers.csv |
| tw_universe | True | True | 2314.0 | 1.0 | /Users/johan/Documents/invest/msci_index_reviews/research_state/taiwan_reference_universe_tickers.csv |
| metadata | True | True | 161.0 | 6.0 | /Users/johan/Documents/invest/msci_index_reviews/parsed/msci_pdf_review_metadata.csv |
| rounds_report | True | True |  |  | /Users/johan/Documents/invest/msci_index_reviews/reports/msci_ticker_audit_rounds.md |
