# MSCI USA / Taiwan 名稱轉股票代號 verify 報告

- 產出時間：2026-05-22T20:22:57
- 目標：針對前一版 `needs_review` 的 MSCI 公司名稱做第二階段 ticker verify，並保留 `company_name` 與 `stock_code` 分欄。
- 原則：寧可保守，不硬猜；只有高信心來源才回填 ticker。

## 輸出檔案

- `parsed/msci_us_taiwan_name_ticker_mapping_verified.csv`
- `parsed/msci_us_taiwan_events_flat_verified.csv`
- `parsed/msci_us_taiwan_events_dict_verified.json`
- `parsed/msci_us_taiwan_mapping_verify_candidates.csv`

## Verify 方法

1. 保留前一版 exact-normalized mapping。
2. 對 `needs_review` 做 reference fuzzy verify：
   - USA：SEC `company_tickers_exchange` + NasdaqTrader listed/other-listed symbol directory。
   - Taiwan：FinLab company basic info + TWSE/TPEx company code reference。
3. USA 本輪不做 fuzzy/Yahoo 自動回填：歷史 delisted / merger / rename 太多，容易把舊公司誤配成現在同名或相似名 ticker；除前一版 exact-normalized 外，其餘維持 `needs_review`。
4. 無法高信心驗證者維持 `needs_review`，不進正式回測 universe。

## Mapping 狀態摘要（唯一公司名稱）

| country | mapping_status | unique_names |
| --- | --- | --- |
| TAIWAN | mapped_exact_normalized | 116 |
| TAIWAN | needs_review | 373 |
| TAIWAN | verified_tw_reference_fuzzy | 265 |
| USA | mapped_exact_normalized | 1511 |
| USA | needs_review | 2047 |

## Mapping 狀態摘要（事件列）

| country | mapping_status | event_rows |
| --- | --- | --- |
| TAIWAN | mapped_exact_normalized | 249 |
| TAIWAN | needs_review | 788 |
| TAIWAN | verified_tw_reference_fuzzy | 511 |
| USA | mapped_exact_normalized | 2953 |
| USA | needs_review | 3247 |

## 本輪新增 verified mapping 範例

| country | company_name | stock_code | matched_name | mapping_status | mapping_score | mapping_source |
| --- | --- | --- | --- | --- | --- | --- |
| TAIWAN | ABLEREX ELECTRONICS CO | 3628 | ABLEREX | verified_tw_reference_fuzzy | 0.9268 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ACCTON TECHNOLOGY CORP | 2345 | ACCTON | verified_tw_reference_fuzzy | 0.9253 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ADDCN TECHNOLOGY | 5287 | ADDCN | verified_tw_reference_fuzzy | 0.9213 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ADLINK TECHNOLOGY | 6166 | ADLINK | verified_tw_reference_fuzzy | 0.9253 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ADVANCETEK ENTERPRISE CO | 1442 | ADVANCETEK | verified_tw_reference_fuzzy | 0.9376 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | AIRTAC INTERNATIONAL | 1590 | AIRTAC | verified_tw_reference_fuzzy | 0.92 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ALCHIP TECHNOLOGIES | 3661 | Alchip | verified_tw_reference_fuzzy | 0.9216 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ALL RING TECH | 6187 | ALL RING | verified_tw_reference_fuzzy | 0.9515 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ALLIED SUPREME CORP | 4702 | ALLIED | verified_tw_reference_fuzzy | 0.9329 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | AMAZING MICROELECTRONIC | 6411 | Amazing | verified_tw_reference_fuzzy | 0.9204 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | AMTRAN TECHNOLOGY CO | 2489 | AMTRAN | verified_tw_reference_fuzzy | 0.9253 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ANDES TECHNOLOGY | 6533 | ANDES | verified_tw_reference_fuzzy | 0.9213 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ANPEC ELECTRONICS CORP | 6138 | ANPEC | verified_tw_reference_fuzzy | 0.9194 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | AP MEMORY TECH | 6531 | AP Memory | verified_tw_reference_fuzzy | 0.9543 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ARCADYAN TECHNOLOGY CORP | 3596 | Arcadyan | verified_tw_reference_fuzzy | 0.9321 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ARIMA COMMUNICATION CORP | 8101 | Arima Comm. | verified_tw_reference_fuzzy | 0.9426 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ASIA PLASTIC RECYCLE | 1337 | Asia Plastic | verified_tw_reference_fuzzy | 0.95 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ASIA PLASTIC RECYCLING | 1337 | Asia Plastic | verified_tw_reference_fuzzy | 0.9445 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ASMEDIA TECHNOLOGY | 5269 | Asmedia | verified_tw_reference_fuzzy | 0.9289 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ASPEED TECHNOLOGY | 5274 | ASPEED | verified_tw_reference_fuzzy | 0.9253 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | AURAS TECHNOLOGY | 3324 | AURAS | verified_tw_reference_fuzzy | 0.9213 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | AVERMEDIA TECHNOLOGIES | 2417 | AVERMEDIA | verified_tw_reference_fuzzy | 0.9309 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | BAFANG YUNJI INTL | 2753 | Bafang | verified_tw_reference_fuzzy | 0.9253 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | BASSO INDUSTRY CORP | 1527 | BASSO | verified_tw_reference_fuzzy | 0.9257 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | BRIGHT LED ELECTRONICS | 3031 | BRIGHT | verified_tw_reference_fuzzy | 0.9173 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | BRIGHTON-BEST INTL | 8415 | Brighton-Best | verified_tw_reference_fuzzy | 0.9622 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | BROGENT TECHNOLOGIES | 5263 | BROGENT | verified_tw_reference_fuzzy | 0.925 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | C SUN MANUFACTURING | 2467 | C SUN | verified_tw_reference_fuzzy | 0.9163 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CALIWAY BIOPHARMA | 6919 | Caliway | verified_tw_reference_fuzzy | 0.9312 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CAREER TECHNOLOGY CO | 6153 | Career Tech. | verified_tw_reference_fuzzy | 0.9547 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CATCHER TECH CO | 2474 | CATCHER | verified_tw_reference_fuzzy | 0.9483 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CAYMAN ENGLEY INDL | 2239 | Cayman Engley | verified_tw_reference_fuzzy | 0.9622 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CENTER LABORATORIES | 4123 | Center Lab. | verified_tw_reference_fuzzy | 0.9426 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CENTRAL REINSURANCE | 2851 | Central Re | verified_tw_reference_fuzzy | 0.9426 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CHANG WAH ELECTROMTRLS | 8070 | CHANG WAH | verified_tw_reference_fuzzy | 0.9309 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CHANG WAH TECHNOLOGY | 8070 | CHANG WAH | verified_tw_reference_fuzzy | 0.935 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CHENBRO MICOM | 8210 | CHENBRO | verified_tw_reference_fuzzy | 0.9438 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CHICONY ELECTRONICS CO | 2385 | CHICONY | verified_tw_reference_fuzzy | 0.9268 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CHICONY POWER TECHNOLOGY | 6412 | Chicony Power | verified_tw_reference_fuzzy | 0.9442 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CHIEF TELECOM | 6561 | Chief | verified_tw_reference_fuzzy | 0.9285 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CHIEN KUO CONST CO | 5515 | CHIEN KUO | verified_tw_reference_fuzzy | 0.95 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CHIN-POON INDUSTRIAL CO | 2355 | CHIN-POON | verified_tw_reference_fuzzy | 0.935 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CHIPMOS TECHNOLOGIES | 8150 | ChipMOS | verified_tw_reference_fuzzy | 0.925 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CHLITINA HOLDING | 4137 | CHLITINA-KY | verified_tw_reference_fuzzy | 0.9627 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CHROMA ATE | 2360 | CHROMA | verified_tw_reference_fuzzy | 0.95 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CHUNG HUNG STEEL CORP | 2014 | CHUNG HUNG | verified_tw_reference_fuzzy | 0.9525 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CHUNG HWA PULP CORP | 4205 | CHUNG HWA | verified_tw_reference_fuzzy | 0.9543 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | COMPAL COMMUNICATIONS | 2324 | Compal | verified_tw_reference_fuzzy | 0.9186 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | COMPAL ELECTRONICS | 2324 | Compal | verified_tw_reference_fuzzy | 0.9233 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | COMPEQ MANUFACTURING CO | 2313 | COMPEQ | verified_tw_reference_fuzzy | 0.92 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CONTREL TECHNOLOGY | 8064 | CONTREL | verified_tw_reference_fuzzy | 0.9289 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | COXON PRECISE IND CO | 3607 | Coxon | verified_tw_reference_fuzzy | 0.9194 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | COXON PRECISE INDUSTRIAL | 3607 | Coxon | verified_tw_reference_fuzzy | 0.9108 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CREATIVE SENSOR | 7837 | Creative | verified_tw_reference_fuzzy | 0.9433 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CROWELL DEVELOPMENT | 2528 | CROWELL | verified_tw_reference_fuzzy | 0.9268 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CYBERPOWER SYSTEMS | 3617 | CyberPower | verified_tw_reference_fuzzy | 0.9456 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | CYBERTAN TECHNOLOGY | 3062 | CyberTAN | verified_tw_reference_fuzzy | 0.9321 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | DA-CIN CONSTRUCTION CO | 2535 | DA-CIN | verified_tw_reference_fuzzy | 0.9216 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | DA-LI CONSTRUCTION | 6177 | DA-LI CO.LTD. | verified_tw_reference_fuzzy | 0.9178 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | DARFON ELECTRONICS | 8163 | DARFON | verified_tw_reference_fuzzy | 0.9233 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | DARWIN PRECISIONS CORP | 6120 | DARWIN | verified_tw_reference_fuzzy | 0.9253 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | DAXIN MATERIALS | 5234 | DAXIN | verified_tw_reference_fuzzy | 0.9233 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | DELPHA CONSTRUCTION | 2530 | DELPHA | verified_tw_reference_fuzzy | 0.9216 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | DIAMOND FLOWER ELE INSTR | 6815 | Diamond | verified_tw_reference_fuzzy | 0.9192 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | DYACO INTERNATIONAL | 1598 | Dyaco | verified_tw_reference_fuzzy | 0.9163 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | DYNAPACK INTL TECH | 3211 | Dynapack | verified_tw_reference_fuzzy | 0.9344 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | E-LEAD ELECTRONIC CO | 2497 | E-LEAD | verified_tw_reference_fuzzy | 0.9253 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | E-LIFE MALL CORPORATION | 6281 | E-LIFE | verified_tw_reference_fuzzy | 0.9445 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ECLAT TEXTILE COMPANY | 1476 | ECLAT | verified_tw_reference_fuzzy | 0.9285 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | EMEMORY TECHNOLOGY | 3529 | eMemory | verified_tw_reference_fuzzy | 0.9289 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ENTIE COMMERCIAL BANK | 2849 | EnTie Bank | verified_tw_reference_fuzzy | 0.83 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ENTIRE TECHNOLOGY CO | 6775 | ENTIRE TECH | verified_tw_reference_fuzzy | 0.9547 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | EPISIL PRECISION | 3707 | EPISIL | verified_tw_reference_fuzzy | 0.9275 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | EPISIL TECHNOLOGIES | 3707 | EPISIL | verified_tw_reference_fuzzy | 0.9216 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | EPISIL TECHNOLOGIES INC | 3707 | EPISIL | verified_tw_reference_fuzzy | 0.9216 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ERIS TECHNOLOGY | 3675 | Eris Tech | verified_tw_reference_fuzzy | 0.95 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ETERNAL CHEMICAL CO | 1717 | ETERNAL | verified_tw_reference_fuzzy | 0.9337 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | ETRON TECHNOLOGY | 5351 | Etron | verified_tw_reference_fuzzy | 0.9213 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | EVER SUPREME BIO TECH | 6712 | Ever Supreme | verified_tw_reference_fuzzy | 0.9471 | FinLab company_basic_info:英文簡稱 |
| TAIWAN | FARGLORY DEVELOPERS CO | 5522 | Farglory | verified_tw_reference_fuzzy | 0.9321 | FinLab company_basic_info:英文簡稱 |

（只列前 80 筆；完整見 verified mapping CSV，共新增 265 個唯一名稱。）

## 仍需人工/歷史資料源確認

仍有 `2420` 個唯一名稱是 `needs_review`。這些多半是歷史下市、併購、改名、縮寫太重或 Taiwan 英文名不在目前 reference 中。

| country | company_name |
| --- | --- |
| TAIWAN | A.G.V. PRODUCTS |
| TAIWAN | ABILITY ENTERPRISE CO |
| TAIWAN | ABILITY OPTO ELECTRONICS |
| TAIWAN | ABLEPRINT TECHNOLOGY |
| TAIWAN | ACES ELECTRONIC CO |
| TAIWAN | ACHEM TECHNOLOGY |
| TAIWAN | ACME ELECTRONICS CORP |
| TAIWAN | ACTRON TECHNOLOGY |
| TAIWAN | ADIMMUNE |
| TAIWAN | ADV LITHIUM ELECTROCHEM |
| TAIWAN | ADV WIRELESS SC |
| TAIWAN | ADV WIRELESS SEMICONDUC |
| TAIWAN | ADVANCED CERAMIC X CORP |
| TAIWAN | ADVANCED ENERGY SOLUTION |
| TAIWAN | ADVANCED INT'L MULTITECH |
| TAIWAN | ADVANCED LITH ELCTROCHM |
| TAIWAN | ALAR PHARMACEUTICALS |
| TAIWAN | ALEXANDER MARINE |
| TAIWAN | ALPHA NETWORKS |
| TAIWAN | AMBASSADOR HOTEL (THE) |
| TAIWAN | APEX BIOTECHNOLOGY CORP |
| TAIWAN | APEX DYNAMICS |
| TAIWAN | APEX INTERNATIONAL |
| TAIWAN | ASIA CEMENT CORP |
| TAIWAN | ASIA OPTICAL |
| TAIWAN | ASIA PACIFIC TELECOM CO |
| TAIWAN | ASIA POLYMER |
| TAIWAN | ASIA VITAL COMPONENTS |
| TAIWAN | ATEN INTERNATIONAL |
| TAIWAN | AVY PRECISION TECH |
| TAIWAN | BENQ MATERIALS CORP |
| TAIWAN | BIZLINK HOLDING |
| TAIWAN | BOARDTEK ELECTRONICS CO |
| TAIWAN | BORA PHARMACEUTICALS |
| TAIWAN | C-MEDIA ELECTRONICS |
| TAIWAN | CANDO CORP |
| TAIWAN | CAPELLA MICROSYS TAIWAN |
| TAIWAN | CAPITAL SECURITIES CORP |
| TAIWAN | CASETEK HOLDINGS |
| TAIWAN | CATHAY NO 1 REIT |
| TAIWAN | CATHAY NO 2 REIT |
| TAIWAN | CATHAY REAL ESTATE DEV |
| TAIWAN | CENTURY IRON & STEEL |
| TAIWAN | CHAMPION BUILDING MATRLS |
| TAIWAN | CHANGS ASCENDING ENTERPR |
| TAIWAN | CHANNEL WELL TECH CO |
| TAIWAN | CHAROEN POKPHAND ENT |
| TAIWAN | CHAUN-CHOUNG TECH CORP |
| TAIWAN | CHC HEALTHCARE GROUP |
| TAIWAN | CHC RESOURCES CORP |
| TAIWAN | CHENG SHIN RUBBER IND |
| TAIWAN | CHENG UEI PRECISION IND |
| TAIWAN | CHENMING ELECTRONIC TECH |
| TAIWAN | CHENMING MOLD INDUSTRY |
| TAIWAN | CHIA HSIN CEMENT |
| TAIWAN | CHILISIN ELECTRS CORP |
| TAIWAN | CHIMEI MATERIALS TECH |
| TAIWAN | CHINA AIRLINES |
| TAIWAN | CHINA CHEM & PHARM CO |
| TAIWAN | CHINA ECOTEK CORPORATION |
| TAIWAN | CHINA ELECTRIC MFG |
| TAIWAN | CHINA GENERAL PLASTICS |
| TAIWAN | CHINA HI MENT |
| TAIWAN | CHINA LIFE INSURANCE CO |
| TAIWAN | CHINA MAN-MADE FIBER |
| TAIWAN | CHINA METAL PRODUCTS CO |
| TAIWAN | CHINA MOTOR CORP |
| TAIWAN | CHINA PETROCHEMICAL DEV |
| TAIWAN | CHINA STEEL STRUCTURE CO |
| TAIWAN | CHINESE GAMER INT'L |
| TAIWAN | CHINESE MARITIME TRANSP |
| TAIWAN | CHUNG HSIN ELEC & MACH |
| TAIWAN | CHUNGHWA PICTURE TUBES |
| TAIWAN | CHUNGHWA PRECISION TEST |
| TAIWAN | CMC MAGNETICS CORP |
| TAIWAN | CO TECH DEVELOPMENT |
| TAIWAN | CONCORD SECURITIES CORP |
| TAIWAN | COSMOS BANK TAIWAN |
| TAIWAN | CRYSTALWISE TECHNOLOGY |
| TAIWAN | CUB ELECPARTS |

（只列前 80 筆；完整見 verified mapping CSV。）

## 回測使用建議

- 第一版回測只使用 `mapping_status != needs_review` 的事件。
- 對 USA 舊名稱，很多需要 CRSP/Refinitiv/Compustat 或 historical symbol master 才能正確處理 delisting / merger；不要用 current Yahoo fuzzy 直接硬配。
- Taiwan 的剩餘項目建議補 TWSE/TPEX 英文公司名歷史表；目前只用 current reference，會有更名與下市 survivorship 問題。
