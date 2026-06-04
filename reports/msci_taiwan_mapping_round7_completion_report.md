# MSCI Taiwan mapping completion — Round 7

## 結論
- 本輪補齊前缺 code 的 Taiwan unique names：324
- 本輪保守接受並寫回：229
- 仍需人工檢查：95
- 寫回後仍缺 code 的 Taiwan unique names：95

## 驗證規則
- 下市/下櫃：優先採 TWSE/TPEx official English delisted tables；名稱需 exact / high-confidence 且避開 generic-token 假陽性。
- 現行上市櫃：Yahoo Finance search 只作名稱發現；代碼必須存在本地 TWSE/TPEx/FinLab Taiwan reference universe 才接受。
- 先前 R4 已人工查證的歷史案例，用 prior-evidence override 寫回。
- 其餘不硬猜，列入人工清單。

## 輸出檔
- Accepted mappings: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_taiwan_mapping_round7_accepted.csv`
- Manual unique list: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_taiwan_mapping_round7_manual_unique.csv`
- Manual event rows: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_taiwan_mapping_round7_manual_events.csv`
- Summary JSON: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_taiwan_mapping_round7_summary.json`

## Accepted by status
- verified_tw_current_round7: 188
- verified_tw_historical_round7: 41

## 人工清單前 80 筆
- PHOENIXTEC POWER CO（events=1）；top candidate 2341 Behavior Tech Computer Corp. score=0.4737
- LEE CHANG YUNG CHEM IND（events=3）；top candidate 2114 HSIN YUNG CHIEN CO.,LTD. score=0.6316
- NAN KANG RUBBER TIRE CO（events=3）；top candidate 9946 San Far Property Limited score=0.5
- FAR EAST DEPT STORES（events=2）；top candidate 5605 Far Eastern Air Transport Corporation score=0.5333
- FORMOSA INTL HOTELS（events=2）；top candidate 5492 MANZ INTECH MACHINES CO., LTD score=0.5128
- ASIA PACIFIC TELECOM CO（events=3）；top candidate 6107 SINO-AMERICAN ELECTRONICS CO., LTD score=0.4889
- SINOAMERICAN SILICON PRO（events=5）；top candidate 6107 SINO-AMERICAN ELECTRONICS CO., LTD score=0.6531
- CHINESE GAMER INT'L（events=3）；top candidate 6131 AC&C INT'L score=0.5455
- CHUNGHWA PICTURE TUBES（events=3）；top candidate 6022 Ta Chong Securities Co., Ltd. score=0.5366
- TAIWAN GLASS INDL CORP（events=2）；top candidate 4144 Coland Holdings Limited score=0.5
- INTL GAMES SYSTEM C（events=6）；top candidate 8105 GIANTPLUS TECHNOLOGY CO., LTD. score=0.4615
- AMBASSADOR HOTEL (THE)（events=2）；top candidate 6215 AUROTEK CORPORATION score=0.4348
- DEPO AUTO PARTS INDL CO（events=2）；top candidate 6438 Symtek Automation Asia Co., Ltd. score=0.4762
- SUNONWEALTH ELEC MACHINE（events=3）；top candidate 5492 MANZ INTECH MACHINES CO., LTD score=0.5909
- ABLEPRINT TECHNOLOGY（events=1）；top candidate 6243 ENE Technology Inc. score=0.7647
- HOLYSTONE ENTERPRISE CO（events=1）；top candidate 3229 CHEER TIME ENTERPRISE CO., LTD score=0.6829
- INTL CSRC INV HLDGS CO（events=1）；top candidate 6131 AC&C INT'L score=0.4848
- TAIWAN-ASIA SC CORP（events=1）；top candidate 1613 Tai-I score=0.5
- YUNG SHIN GLOBAL HOLDING（events=1）；top candidate 1408 CHUNG SHING TEXTILE CO.,LTD score=0.5714
- YUNGSHIN CONST & DEV（events=2）；top candidate 5519 LongDa Construction & Development Corporation score=0.5614
- A.G.V. PRODUCTS（events=2）；top candidate 6287 ADVANCED MICROELECTRONIC PRODUCTS,INC. score=0.4681
- COSMOS BANK TAIWAN（events=2）；top candidate 2847 TC Bank score=0.6667
- E-ONE MOLI ENERGY CORP（events=2）；top candidate 9157 Solargiga Energy Holdings Limited score=0.6061
- ORISE TECHNOLOGY CO（events=2）；top candidate 2396 PRODISC TECHNOLOGY INC. score=0.8235
- POWER QUOTIENT INT'L（events=3）；top candidate 3296 POWERTECH INDUSTRIAL CO., LTD. score=0.6
- TAIWAN LAND CORP（events=2）；top candidate 4144 Coland Holdings Limited score=0.8
- FUBON NO 1 REIT（events=1）；top candidate 4429 GFun Industrial Corporation score=0.4667
- SHIN KONG NO 1 REIT（events=1）；top candidate 2114 HSIN YUNG CHIEN CO.,LTD. score=0.4706
- ADV WIRELESS SEMICONDUC（events=2）；top candidate 5466 ThaiLin Semiconductor Corp. score=0.6364
- DAHAN DEVELOPMENT CORP（events=1）；top candidate 3266 Sunty Development Co., LTD score=0.7647
- DAXON TECHNOLOGY（events=1）；top candidate 6514 Radiation Technology, Inc. score=0.8333
- CATHAY NO 2 REIT（events=1）；top candidate 6024 Capital Futures Corp. score=0.4516
- CHENMING MOLD INDUSTRY（events=2）；top candidate 8925 WEI MON INDUSTRY CO.,LTD. score=0.7368
- CHIMEI MATERIALS TECH（events=2）；top candidate 3229 CHEER TIME ENTERPRISE CO., LTD score=0.5714
- MITAC INTERNATIONAL（events=1）；top candidate 5306 KMC (KUEI MENG) INTERNATIONAL INC. score=0.8889
- SKYMEDI（events=2）；top candidate 4803 VHQ MEDIA HOLDINGS LTD score=0.5
- KAI CHIEH INTL INV（events=2）；top candidate 6131 AC&C INT'L score=0.5
- YUFO ELECTRONIC CORP（events=1）；top candidate 8112 Supreme Electronics Co., Ltd. score=0.7059
- KOBIN ENVIRONMNTL ENTER（events=1）；top candidate 8476 TAIWAN ENVIRONMENT SCIENTIFIC CO., LTD. score=0.5333
- CANDO CORP（events=2）；top candidate 4144 Coland Holdings Limited score=0.7273
- JENN FENG NEW ENERGY CO（events=1）；top candidate 5521 KUNG SING ENGINEERING CORPORATION score=0.5405
- GALLOP NO 1 REIT（events=1）；top candidate 1469 LILONTEX score=0.4167
- KMC (KUEI MENG) INT'L（events=1）；top candidate 5306 KMC (KUEI MENG) INTERNATIONAL INC. score=0.6154
- AVY PRECISION TECH（events=2）；top candidate 5318 VERTEX PRECISION ELECTRONICS, INC. score=0.6087
- PAN JIT INTERNATIONAL（events=2）；top candidate 1566 JaBon International Co.,Ltd. score=0.8
- TAIWAN PULP & PAPER CO（events=2）；top candidate 9946 San Far Property Limited score=0.4667
- ADVANCED LITH ELCTROCHM（events=1）；top candidate 8261 Advanced Power Electronics Corp score=0.6939
- CHAMPION BUILDING MATRLS（events=2）；top candidate 8070 CHANG WAH ELECTRONMATERIALS INC. score=0.4706
- SHIHLIN ELECTRIC & ENGR（events=2）；top candidate 6152 Prime Electronics & Satellitics Inc. score=0.5517
- GENIUS ELECTR OPTICAL（events=2）；top candidate 8287 ENG ELECTRIC CO., LTD. score=0.6667
- GREEN ENERGY TECHNOLOGY（events=1）；top candidate 6243 ENE Technology Inc. score=0.7568
- E-TON SOLAR TECH（events=1）；top candidate 3562 TYNSOLAR CORPORATION score=0.5833
- TAIWAN PCB TECHVEST CO（events=1）；top candidate 5480 T-MAC TECHVEST PCB CO., LTD. score=0.6667
- CHUNG HSIN ELEC & MACH（events=2）；top candidate 1408 CHUNG SHING TEXTILE CO.,LTD score=0.6047
- LITE-ON SEMICONDUCTOR（events=2）；top candidate 5466 ThaiLin Semiconductor Corp. score=0.8095
- MARKETECH INTL CORP（events=1）；top candidate 3296 POWERTECH INDUSTRIAL CO., LTD. score=0.5882
- ITE TECHNOLOGY（events=2）；top candidate 6110 Everelite Technology Co.,Ltd. score=1.0
- UNIZYX HOLDING（events=3）；top candidate 2499 Unity score=0.7273
- OPTOTECH CORP（events=1）；top candidate 3164 GenMont Biotech Inc. score=0.6087
- RUENTEX ENGR & CONST（events=1）；top candidate 5384 GENUINE C&C INC. score=0.5405
- JIH SUN FINANCIAL（events=1）；top candidate 5820 JIHSUN FINANCIAL HOLDING CO., LTD. score=0.9697
- ECHEM SOLUTIONS（events=1）；top candidate 6164 LEDTECH ELECTRONICS CORP. score=0.5294
- GALLANT PREC MACHINING（events=2）；top candidate 5492 MANZ INTECH MACHINES CO., LTD score=0.5714
- KMC (KUEI MENG) INTL（events=1）；top candidate 5306 KMC (KUEI MENG) INTERNATIONAL INC. score=0.64
- CHINA HI MENT（events=1）；top candidate 1107 CHIEN TAI CEMENT CO., LTD. score=0.7586
- SOLARTECH ENERGY CORP（events=1）；top candidate 9157 Solargiga Energy Holdings Limited score=0.75
- WONTEN TECHNOLOGY CO（events=1）；top candidate 6243 ENE Technology Inc. score=0.8387
- RALINK TECHNOLOGY CORP（events=1）；top candidate 3369 TAK TECHNOLOGY CO., LTD score=0.8387
- HOLDKEY ELECTRIC WIRE（events=2）；top candidate 5349 BOARDTEK ELECTRONICS COR. score=0.6222
- CATHAY NO 1 REIT（events=1）；top candidate 6024 Capital Futures Corp. score=0.4516
- YUNGSHIN CONSTR & DEVLPT（events=1）；top candidate 5519 LongDa Construction & Development Corporation score=0.6557
- INTEGRATED MEMORY LOGIC（events=1）；top candidate 3416 WinMate Communication INC. score=0.4545
- PC HOME ONLINE（events=2）；top candidate 4965 PCHOMESTORE INC. score=0.64
- PROSPERITY DIELECT CO LT（events=2）；top candidate 4947 On-Bright Electronics Incorporated score=0.4762
- RUENTEX ENGIN & CONST（events=3）；top candidate 5384 GENUINE C&C INC. score=0.5263
- TAIWAN PROSPERITY CHEMIC（events=2）；top candidate 4722 QUALIPOLY CHEMICAL CORP. score=0.5714
- MAGLAYERS SCIENTIFIC TE（events=1）；top candidate 3068 MAG.LAYERS Scientific-Technics Co.,Ltd. score=0.8679
- SOLELYTEX INDUSTRIAL（events=1）；top candidate 1333 Entery Industrial Co., Ltd. score=0.7568
- WELLYPOWER OPTRONICS（events=1）；top candidate 8261 Advanced Power Electronics Corp score=0.6087
- ILI TECHNOLOGY CORP（events=2）；top candidate 3291 Feeling Technology Corp. score=0.8125


## Round 7b — variant query補齊

- Manual before: 95
- Accepted: 6
- Manual remaining: 89
- Output: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_taiwan_mapping_round7b_accepted.csv`
- Updated manual list: `/Users/johan/Documents/invest/msci_index_reviews/research_state/msci_taiwan_mapping_round7_manual_unique.csv`
