# MSCI Standard / Small Cap 美國與台灣增刪成分解析報告
- 產出時間：2026-05-22T19:29:15
- PDF 根目錄：`/Users/johan/Documents/invest/msci_index_reviews/pdf`
- 解析產品：Global Standard (`stdindex`) 與 Global Small Cap (`smallcap`)
- 解析範圍：只保留 `USA` 與 `TAIWAN` 的 additions / deletions
- PDF 數量：standard 82，small_cap 79
- 事件列數：7,748；唯一公司名稱：4,312

## 輸出檔案
- `parsed/msci_us_taiwan_events_dict.json`
- `parsed/msci_us_taiwan_events_flat.csv`
- `parsed/msci_us_taiwan_name_ticker_mapping.csv`
- `parsed/msci_pdf_review_metadata.csv`
- `parsed/mapping_reference_usa.csv`
- `parsed/mapping_reference_taiwan.csv`

## 欄位說明
- `issue_date`：PDF 第一行 Geneva 發行日。
- `announcement_date`：本資料集暫以 PDF 發行日作公告可得日；MSCI 通常公告日即該 PDF 日期。
- `effective_close_date`：PDF 文字 `as of the close of ...`，回測時應視為收盤後生效。
- `company_name`：MSCI PDF 原始公司名稱。
- `stock_code`：對應股票代號；美股為 ticker，台股為四碼/含字母代號。
- `mapping_status`：mapping 信心狀態；`needs_review` 不應直接進正式回測。

## 事件數摘要
| product | country | addition | deletion |
| --- | --- | --- | --- |
| small_cap | TAIWAN | 643 | 630 |
| small_cap | USA | 2974 | 2128 |
| standard | TAIWAN | 117 | 158 |
| standard | USA | 591 | 507 |

## Mapping 狀態摘要（事件列）
| country | mapping_status | rows |
| --- | --- | --- |
| TAIWAN | mapped_exact_normalized | 249 |
| TAIWAN | needs_review | 1299 |
| USA | mapped_exact_normalized | 2953 |
| USA | needs_review | 3247 |

## Mapping 狀態摘要（唯一公司名）
| country | mapping_status | unique_names |
| --- | --- | --- |
| TAIWAN | mapped_exact_normalized | 116 |
| TAIWAN | needs_review | 638 |
| USA | mapped_exact_normalized | 1511 |
| USA | needs_review | 2047 |

## 仍需人工/二次資料源確認的名稱
| country | company_name | matched_name | mapping_score | mapping_source |
| --- | --- | --- | --- | --- |
| TAIWAN | A.G.V. PRODUCTS | nan | 0.0 | nan |
| TAIWAN | ABILITY ENTERPRISE CO | nan | 0.0 | nan |
| TAIWAN | ABILITY OPTO ELECTRONICS | nan | 0.0 | nan |
| TAIWAN | ABLEPRINT TECHNOLOGY | nan | 0.0 | nan |
| TAIWAN | ABLEREX ELECTRONICS CO | nan | 0.0 | nan |
| TAIWAN | ACCTON TECHNOLOGY CORP | nan | 0.0 | nan |
| TAIWAN | ACES ELECTRONIC CO | nan | 0.0 | nan |
| TAIWAN | ACHEM TECHNOLOGY | nan | 0.0 | nan |
| TAIWAN | ACME ELECTRONICS CORP | nan | 0.0 | nan |
| TAIWAN | ACTRON TECHNOLOGY | nan | 0.0 | nan |
| TAIWAN | ADDCN TECHNOLOGY | nan | 0.0 | nan |
| TAIWAN | ADIMMUNE | nan | 0.0 | nan |
| TAIWAN | ADLINK TECHNOLOGY | nan | 0.0 | nan |
| TAIWAN | ADV LITHIUM ELECTROCHEM | nan | 0.0 | nan |
| TAIWAN | ADV WIRELESS SC | nan | 0.0 | nan |
| TAIWAN | ADV WIRELESS SEMICONDUC | nan | 0.0 | nan |
| TAIWAN | ADVANCED CERAMIC X CORP | nan | 0.0 | nan |
| TAIWAN | ADVANCED ENERGY SOLUTION | nan | 0.0 | nan |
| TAIWAN | ADVANCED INT'L MULTITECH | nan | 0.0 | nan |
| TAIWAN | ADVANCED LITH ELCTROCHM | nan | 0.0 | nan |
| TAIWAN | ADVANCETEK ENTERPRISE CO | nan | 0.0 | nan |
| TAIWAN | AIRTAC INTERNATIONAL | nan | 0.0 | nan |
| TAIWAN | ALAR PHARMACEUTICALS | nan | 0.0 | nan |
| TAIWAN | ALCHIP TECHNOLOGIES | nan | 0.0 | nan |
| TAIWAN | ALEXANDER MARINE | nan | 0.0 | nan |
| TAIWAN | ALL RING TECH | nan | 0.0 | nan |
| TAIWAN | ALLIED SUPREME CORP | nan | 0.0 | nan |
| TAIWAN | ALPHA NETWORKS | nan | 0.0 | nan |
| TAIWAN | AMAZING MICROELECTRONIC | nan | 0.0 | nan |
| TAIWAN | AMBASSADOR HOTEL (THE) | nan | 0.0 | nan |
| TAIWAN | AMTRAN TECHNOLOGY CO | nan | 0.0 | nan |
| TAIWAN | ANDES TECHNOLOGY | nan | 0.0 | nan |
| TAIWAN | ANPEC ELECTRONICS CORP | nan | 0.0 | nan |
| TAIWAN | AP MEMORY TECH | nan | 0.0 | nan |
| TAIWAN | APEX BIOTECHNOLOGY CORP | nan | 0.0 | nan |
| TAIWAN | APEX DYNAMICS | nan | 0.0 | nan |
| TAIWAN | APEX INTERNATIONAL | nan | 0.0 | nan |
| TAIWAN | ARCADYAN TECHNOLOGY CORP | nan | 0.0 | nan |
| TAIWAN | ARIMA COMMUNICATION CORP | nan | 0.0 | nan |
| TAIWAN | ASIA CEMENT CORP | nan | 0.0 | nan |
| TAIWAN | ASIA OPTICAL | nan | 0.0 | nan |
| TAIWAN | ASIA PACIFIC TELECOM CO | nan | 0.0 | nan |
| TAIWAN | ASIA PLASTIC RECYCLE | nan | 0.0 | nan |
| TAIWAN | ASIA PLASTIC RECYCLING | nan | 0.0 | nan |
| TAIWAN | ASIA POLYMER | nan | 0.0 | nan |
| TAIWAN | ASIA VITAL COMPONENTS | nan | 0.0 | nan |
| TAIWAN | ASMEDIA TECHNOLOGY | nan | 0.0 | nan |
| TAIWAN | ASPEED TECHNOLOGY | nan | 0.0 | nan |
| TAIWAN | ATEN INTERNATIONAL | nan | 0.0 | nan |
| TAIWAN | AURAS TECHNOLOGY | nan | 0.0 | nan |
| TAIWAN | AVERMEDIA TECHNOLOGIES | nan | 0.0 | nan |
| TAIWAN | AVY PRECISION TECH | nan | 0.0 | nan |
| TAIWAN | BAFANG YUNJI INTL | nan | 0.0 | nan |
| TAIWAN | BASSO INDUSTRY CORP | nan | 0.0 | nan |
| TAIWAN | BENQ MATERIALS CORP | nan | 0.0 | nan |
| TAIWAN | BIZLINK HOLDING | nan | 0.0 | nan |
| TAIWAN | BOARDTEK ELECTRONICS CO | nan | 0.0 | nan |
| TAIWAN | BORA PHARMACEUTICALS | nan | 0.0 | nan |
| TAIWAN | BRIGHT LED ELECTRONICS | nan | 0.0 | nan |
| TAIWAN | BRIGHTON-BEST INTL | nan | 0.0 | nan |
| TAIWAN | BROGENT TECHNOLOGIES | nan | 0.0 | nan |
| TAIWAN | C SUN MANUFACTURING | nan | 0.0 | nan |
| TAIWAN | C-MEDIA ELECTRONICS | nan | 0.0 | nan |
| TAIWAN | CALIWAY BIOPHARMA | nan | 0.0 | nan |
| TAIWAN | CANDO CORP | nan | 0.0 | nan |
| TAIWAN | CAPELLA MICROSYS TAIWAN | nan | 0.0 | nan |
| TAIWAN | CAPITAL SECURITIES CORP | nan | 0.0 | nan |
| TAIWAN | CAREER TECHNOLOGY CO | nan | 0.0 | nan |
| TAIWAN | CASETEK HOLDINGS | nan | 0.0 | nan |
| TAIWAN | CATCHER TECH CO | nan | 0.0 | nan |
| TAIWAN | CATHAY NO 1 REIT | nan | 0.0 | nan |
| TAIWAN | CATHAY NO 2 REIT | nan | 0.0 | nan |
| TAIWAN | CATHAY REAL ESTATE DEV | nan | 0.0 | nan |
| TAIWAN | CAYMAN ENGLEY INDL | nan | 0.0 | nan |
| TAIWAN | CENTER LABORATORIES | nan | 0.0 | nan |
| TAIWAN | CENTRAL REINSURANCE | nan | 0.0 | nan |
| TAIWAN | CENTURY IRON & STEEL | nan | 0.0 | nan |
| TAIWAN | CHAMPION BUILDING MATRLS | nan | 0.0 | nan |
| TAIWAN | CHANG WAH ELECTROMTRLS | nan | 0.0 | nan |
| TAIWAN | CHANG WAH TECHNOLOGY | nan | 0.0 | nan |

（只列前 80 筆；完整清單見 `parsed/msci_us_taiwan_name_ticker_mapping.csv`，共 2685 筆。）


## 重要限制與建議
- MSCI PDF 公司名常為縮寫，且 A/B/C share class 可能被寫在名稱尾端；目前 mapping 已保留原始名稱與 matched_name，方便反覆核對。
- 目前自動 mapping 採保守版：只接受 MSCI 名稱與 SEC/NasdaqTrader/FinLab/TWSE/TPEx 參考表的 normalized exact match；未精確對上的名稱一律保留 `needs_review`，避免同名、縮寫、share class 或歷史下市 ticker 被誤配。
- 後續應補第二階段 verifier：對 `needs_review` 使用 Yahoo Finance / 交易所英文公司名 / 歷史 symbol master 反覆驗證後再填入 `stock_code`。
- 正式回測前建議先排除 `needs_review` 與低分數 mapping，並針對同公司多 share class / 更名 / 下市歷史做 survivorship-bias 檢查。
