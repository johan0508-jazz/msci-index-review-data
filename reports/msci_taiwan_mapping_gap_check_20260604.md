# MSCI Taiwan mapping gap check — 2026-06-04

## Verdict
目前不是「全部台股 MSCI 名稱都有成功找到代碼」。backtest-ready 檔中的台股名稱都有代碼；但完整解析宇宙仍有缺口，尤其早期 small cap 與歷史下市/下櫃名稱。

## Counts
- Full Taiwan event rows: 1548
- Unique Taiwan MSCI names: 754
- Unique names with stock_code: 430
- Unique names missing stock_code: 324
- Unique names with at least one backtest-ready event row: 424
- Event rows backtest_ready=true: 924
- Event rows backtest_ready=false: 624
- Names with code but not in current local Taiwan reference universe, mostly delisted/historical: 6

## Unique mapping_status
- needs_review: 323
- verified_tw_reference_fuzzy: 264
- mapped_exact_normalized: 116
- verified_tw_official_round3: 41
- verified_historical_round4: 8
- manual_review_round4: 1
- verified_conflict_round4: 1

## Event-row mapping_status
- needs_review: 602
- verified_tw_reference_fuzzy: 507
- mapped_exact_normalized: 249
- verified_tw_official_round3: 159
- verified_historical_round4: 26
- verified_conflict_round4: 4
- manual_review_round4: 1

## Public delisted-source candidate probe
- Sources tested: TWSE English suspendListing RWD JSON; TPEx English deListed JSON by year 2005-2026; MOPS ajax_t51sb01_1 Chinese delisted summary.
- English delisted reference rows fetched: 264.
- Candidate rows for missing names at score >=0.86 from TWSE/TPEx English delisted sources: 41. These are candidates only; ambiguous fuzzy cases must be manually verified.

## Files
- Unique Taiwan mapping audit: `research_state/msci_taiwan_mapping_gap_unique_20260604.csv`
- Delisted-source fuzzy candidates: `research_state/msci_taiwan_delisted_source_candidates_20260604.csv`

## Sample missing stock_code names
- A.G.V. PRODUCTS (2 event rows; status=needs_review)
- ABILITY ENTERPRISE CO (2 event rows; status=needs_review)
- ABILITY OPTO ELECTRONICS (3 event rows; status=needs_review)
- ABLEPRINT TECHNOLOGY (1 event rows; status=needs_review)
- ACES ELECTRONIC CO (2 event rows; status=needs_review)
- ACHEM TECHNOLOGY (2 event rows; status=needs_review)
- ACME ELECTRONICS CORP (2 event rows; status=needs_review)
- ACTRON TECHNOLOGY (3 event rows; status=needs_review)
- ADIMMUNE (4 event rows; status=needs_review)
- ADV LITHIUM ELECTROCHEM (1 event rows; status=needs_review)
- ADV WIRELESS SC (3 event rows; status=needs_review)
- ADV WIRELESS SEMICONDUC (2 event rows; status=needs_review)
- ADVANCED CERAMIC X CORP (2 event rows; status=needs_review)
- ADVANCED ENERGY SOLUTION (1 event rows; status=needs_review)
- ADVANCED INT'L MULTITECH (1 event rows; status=needs_review)
- ADVANCED LITH ELCTROCHM (1 event rows; status=needs_review)
- ALAR PHARMACEUTICALS (2 event rows; status=needs_review)
- ALEXANDER MARINE (1 event rows; status=needs_review)
- ALPHA NETWORKS (2 event rows; status=needs_review)
- AMBASSADOR HOTEL (THE) (2 event rows; status=needs_review)
- APEX BIOTECHNOLOGY CORP (2 event rows; status=needs_review)
- APEX DYNAMICS (1 event rows; status=needs_review)
- APEX INTERNATIONAL (2 event rows; status=needs_review)
- ASIA CEMENT CORP (2 event rows; status=needs_review)
- ASIA OPTICAL (2 event rows; status=needs_review)
- ASIA PACIFIC TELECOM CO (3 event rows; status=needs_review)
- ASIA POLYMER (3 event rows; status=needs_review)
- ASIA VITAL COMPONENTS (4 event rows; status=needs_review)
- ATEN INTERNATIONAL (1 event rows; status=needs_review)
- AVY PRECISION TECH (2 event rows; status=needs_review)
- BENQ MATERIALS CORP (3 event rows; status=needs_review)
- BIZLINK HOLDING (3 event rows; status=needs_review)
- BOARDTEK ELECTRONICS CO (2 event rows; status=needs_review)
- BORA PHARMACEUTICALS (1 event rows; status=needs_review)
- C-MEDIA ELECTRONICS (1 event rows; status=needs_review)
- CANDO CORP (2 event rows; status=needs_review)
- CAPELLA MICROSYS TAIWAN (2 event rows; status=needs_review)
- CASETEK HOLDINGS (3 event rows; status=needs_review)
- CATHAY NO 1 REIT (1 event rows; status=needs_review)
- CATHAY NO 2 REIT (1 event rows; status=needs_review)
- CATHAY REAL ESTATE DEV (2 event rows; status=needs_review)
- CENTURY IRON & STEEL (1 event rows; status=needs_review)
- CHAMPION BUILDING MATRLS (2 event rows; status=needs_review)
- CHANGS ASCENDING ENTERPR (2 event rows; status=needs_review)
- CHANNEL WELL TECH CO (4 event rows; status=needs_review)
- CHAROEN POKPHAND ENT (1 event rows; status=needs_review)
- CHAUN-CHOUNG TECH CORP (3 event rows; status=needs_review)
- CHC HEALTHCARE GROUP (2 event rows; status=needs_review)
- CHC RESOURCES CORP (1 event rows; status=needs_review)
- CHENMING ELECTRONIC TECH (1 event rows; status=needs_review)
- CHENMING MOLD INDUSTRY (2 event rows; status=needs_review)
- CHIA HSIN CEMENT (3 event rows; status=needs_review)
- CHILISIN ELECTRS CORP (1 event rows; status=needs_review)
- CHIMEI MATERIALS TECH (2 event rows; status=needs_review)
- CHINA CHEM & PHARM CO (1 event rows; status=needs_review)
- CHINA ECOTEK CORPORATION (2 event rows; status=needs_review)
- CHINA ELECTRIC MFG (1 event rows; status=needs_review)
- CHINA GENERAL PLASTICS (4 event rows; status=needs_review)
- CHINA HI MENT (1 event rows; status=needs_review)
- CHINA MAN-MADE FIBER (1 event rows; status=needs_review)

## Sample delisted-source candidates
- ALAR PHARMACEUTICALS → 6497 ASLAN PHARMACEUTICALS LIMITED (TPEx EN deListed, delist=2020-08-25, score=0.9268)
- APEX INTERNATIONAL → 4927 Apex International Co., Ltd. (TPEx EN deListed, delist=2015-09-08, score=1.0)
- APEX INTERNATIONAL → 4987 GODEX INTERNATIONAL CO., LTD (TPEx EN deListed, delist=2026-05-29, score=0.8649)
- ATEN INTERNATIONAL → 4927 Apex International Co., Ltd. (TPEx EN deListed, delist=2015-09-08, score=0.8889)
- ATEN INTERNATIONAL → 1566 JaBon International Co.,Ltd. (TPEx EN deListed, delist=2019-07-31, score=0.8649)
- BOARDTEK ELECTRONICS CO → 5349 BOARDTEK ELECTRONICS COR. (TPEx EN deListed, delist=2020-11-04, score=0.9091)
- BORA PHARMACEUTICALS → 6472 Bora Pharmaceuticals Co., Ltd. (TPEx EN deListed, delist=2023-12-19, score=1.0)
- CASETEK HOLDINGS → 5264 Casetek Holdings Limited (TWSE EN suspendListing, delist=2021/01/15, score=1.0)
- CRYSTALWISE TECHNOLOGY → 4944 CRYSTALWISE TECHNOLOGY INC. (TPEx EN deListed, delist=2023-11-01, score=1.0)
- CUB ELECPARTS → 2231 CUB ELECPARTS INC. (TPEx EN deListed, delist=2010-11-19, score=1.0)
- DELSOLAR CO → 3599 DelSolar (TWSE EN suspendListing, delist=2013/05/31, score=1.0)
- EFUN TECHNOLOGY → 6243 ENE Technology Inc. (TPEx EN deListed, delist=2009-12-17, score=0.8966)
- ENE TECHNOLOGY CO → 6243 ENE Technology Inc. (TPEx EN deListed, delist=2009-12-17, score=1.0)
- ENG ELECTRIC CO → 8287 ENG ELECTRIC CO., LTD. (TPEx EN deListed, delist=2020-05-11, score=1.0)
- GINKO INTERNATIONAL → 8406 Ginko International Co., Ltd. (TPEx EN deListed, delist=2022-04-29, score=1.0)
- GLOBAL MIXED-MODE TECH → 8081 GLOBAL MIXED-MODE TECHNOLOGY INC (TPEx EN deListed, delist=2008-12-30, score=0.88)
- GREEN SEAL HOLDING → 1262 Green Seal Holding Limited (TWSE EN suspendListing, delist=2019/10/14, score=1.0)
- HERMES MICROVISION → 3658 Hermes Microvision Inc. (TPEx EN deListed, delist=2016-11-22, score=1.0)
- J TOUCH CORP → 3584 JTouch (TWSE EN suspendListing, delist=2016/08/03, score=0.9231)
- JIH SUN FINANCIAL → 5820 JIHSUN FINANCIAL HOLDING CO., LTD. (TPEx EN deListed, delist=2022-11-11, score=0.9697)
- KINGPAK TECHNOLOGY → 6238 Kingpak Technology Inc. (TPEx EN deListed, delist=2020-06-19, score=1.0)
- LI PENG ENTERPRISE CO → 4426 LI CHENG ENTERPRISE CO.,LTD. (TPEx EN deListed, delist=2011-12-16, score=0.9189)
- LITE-ON IT → 8008 LITE-ON IT (TWSE EN suspendListing, delist=2013/07/12, score=1.0)
- MAGLAYERS SCIENTIFIC TE → 3068 MAG.LAYERS Scientific-Technics Co.,Ltd. (TPEx EN deListed, delist=2018-06-13, score=0.8679)
- MICROLIFE CORP → 4103 MICROLIFE CORPORATION (TPEx EN deListed, delist=2018-11-13, score=1.0)
- MITAC INTERNATIONAL → 5306 KMC (KUEI MENG) INTERNATIONAL INC. (TPEx EN deListed, delist=2022-03-08, score=0.8889)
- NICHIDENBO → 3090 NICHIDENBO CORPORATION (TPEx EN deListed, delist=2007-12-31, score=1.0)
- PHARMAESSENTIA → 6446 PharmaEssentia Corp. (TPEx EN deListed, delist=2024-01-25, score=1.0)
- PORTWELL INC → 6105 Portwell, Inc. (TPEx EN deListed, delist=2017-10-17, score=1.0)
- POWERCHIP TECHNOLOGY → 5346 Powerchip Technology Corporation (TPEx EN deListed, delist=2012-12-11, score=1.0)
- PRINCO CORP → 8053 PRINCO CORP. (TPEx EN deListed, delist=2016-05-11, score=1.0)
- T3EX GLOBAL HOLDINGS → 2636 T3EX Global Holdings Corp. (TPEx EN deListed, delist=2016-12-22, score=1.0)
- TA CHONG SECURITIES CO → 6022 Ta Chong Securities Co., Ltd. (TPEx EN deListed, delist=2017-08-28, score=1.0)
- TAIWAN LIPOSOME → 4152 Taiwan Liposome Company, Ltd. (TPEx EN deListed, delist=2021-10-08, score=1.0)
- TAIWAN SEMICONDUCTOR CO → 5466 ThaiLin Semiconductor Corp. (TPEx EN deListed, delist=2015-06-17, score=0.878)
- THAILIN SEMICONDUCTOR → 5466 ThaiLin Semiconductor Corp. (TPEx EN deListed, delist=2015-06-17, score=1.0)
- TWI PHARMACEUTICALS → 4180 TWi Pharmaceuticals, Inc. (TPEx EN deListed, delist=2019-08-05, score=1.0)
- VIVOTEK INC → 3454 VIVOTEK INC. (TPEx EN deListed, delist=2011-07-22, score=1.0)
- WEI MON INDUSTRY CO → 8925 WEI MON INDUSTRY CO.,LTD. (TPEx EN deListed, delist=2016-06-27, score=1.0)
- XPEC ENTERTAINMENT → 3662 XPEC Entertainment Inc. (TPEx EN deListed, delist=2017-10-19, score=1.0)
