#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter
from datetime import datetime
from pathlib import Path
ROOT=Path('/Users/johan/Documents/invest/msci_index_reviews'); PARSED=ROOT/'parsed'; STATE=ROOT/'research_state'; REPORTS=ROOT/'reports'
MAPPING=PARSED/'msci_us_taiwan_name_ticker_mapping_verified.csv'; EVENTS=PARSED/'msci_us_taiwan_events_flat_verified.csv'
MANUAL=STATE/'msci_taiwan_mapping_round8b_manual_unique.csv'; MANUAL_EVENTS=STATE/'msci_taiwan_mapping_round7_manual_events.csv'
OUT=STATE/'msci_taiwan_mapping_round8c_accepted.csv'; STILL=STATE/'msci_taiwan_mapping_round8c_manual_unique.csv'; SUMMARY=STATE/'msci_taiwan_mapping_round8c_summary.json'; REPORT=REPORTS/'msci_taiwan_mapping_round8c_completion_report.md'
SEEDS={
 'TAIWAN-ASIA SC CORP':('2340','Taiwan-Asia Semiconductor Corporation / 台亞半導體','verified_tw_yahoo_google_round8c','Company website states Stock Code 2340; StockAnalysis/FT confirm TPE:2340.'),
 'YUNG SHIN GLOBAL HOLDING':('3705','YungShin Global Holding Corporation / 永信','verified_tw_yahoo_google_round8c','Company PDF says Stock Code 3705; Yahoo Finance 3705.TW.'),
 'COSMOS BANK TAIWAN':('2837','Cosmos Bank Taiwan / 萬泰銀行','verified_tw_historical_round8c','Investing/Cosmos Bank historical pages show Cosmos Bank (2837); later acquired by CDF/KGI.'),
 'E-ONE MOLI ENERGY CORP':('3127','E-One Moli Energy Corp. / 能元科技','verified_tw_historical_round8c','Cnyes profile for E-ONE MOLI ENERGY CORP. shows code 3127; unlisted/ESB historical code.'),
 'POWER QUOTIENT INT\'L':('6145','Power Quotient International Co., Ltd. / 勁永國際','verified_tw_historical_round8c','PatSnap/Discovery profile shows TPE:6145 and stock symbol 6145.'),
 'TAIWAN LAND CORP':('2841','Taiwan Land Development Corporation / 台開','verified_tw_historical_round8c','CompanyInfoTW record shows stock code 2841 and English name Taiwan Land Development Corporation.'),
 'DAXON TECHNOLOGY':('8215','BenQ Materials Corp. formerly Daxon Technology Inc. / 明基材料','verified_tw_yahoo_google_round8c','BenQ Materials company history and Yahoo Finance say formerly Daxon Technology Inc.; ticker 8215.TW.'),
 'CHENMING MOLD INDUSTRY':('3013','Chenming Electronic Technology Corp. formerly Chenming Mold Ind. Corp. / 晟銘電','verified_tw_yahoo_google_round8c','Investing/Disfold/EODHD show Chenming Mold Industrial Corp. / former name, TWSE:3013.'),
 'CHIMEI MATERIALS TECH':('4960','Cheng Mei Materials Technology Corp. formerly Chi Mei Materials Technology / 誠美材','verified_tw_yahoo_google_round8c','Company site says stock code 4960; Cnyes says former name 奇美材料科技.'),
 'TAIWAN PULP & PAPER CO':('1902','Taiwan Pulp & Paper Corporation / 台紙','verified_tw_yahoo_google_round8c','Cnyes/MarketScreener show Taiwan Pulp & Paper Corporation code 1902.'),
 'ECHEM SOLUTIONS':('4749','Advanced Echem Materials Co., formerly eChem Solutions Corp. / 泓德能源? AEMC','verified_tw_yahoo_google_round8c','MarketScreener/CreditRiskMonitor say Advanced Echem Materials 4749, formerly eChem Solutions Corp.'),
 'CHINA HI MENT':('1103','Chia Hsin Cement Corporation / 嘉泥','verified_tw_yahoo_google_round8c','Google/Yahoo/Cnyes show Chia Hsin Cement Corporation code 1103; MSCI name appears abbreviated/misparsed.'),
 'TAIWAN PROSPERITY CHEMIC':('4725','Taiwan Prosperity Chemical Corporation / 台灣神隆? TPC','verified_tw_historical_round8c','TWSE factbook delisting table shows Taiwan Prosperity Chemical Corporation code 4725.'),
 'SOLELYTEX INDUSTRIAL':('1471','Solytech Enterprise Corporation / 首利','verified_tw_yahoo_google_round8c','Solytech annual report says Stock Code 1471; company profile confirms Solytech Enterprise Corp.'),
 'WELLYPOWER OPTRONICS':('3080','Wellypower Optronics Corp. / 威力盟','verified_tw_historical_round8c','PatSnap/Discovery and Taipei Times show Wellypower Optronics stock symbol 3080; historical OTC/TSE transfer.'),
 'ILI TECHNOLOGY CORP':('3598','ILI Technology Corp. / 奕力科技','verified_tw_historical_round8c','TEDC stock table lists ILI TECHNOLOGY CORP. as S3598 / 3598; company registry confirms English name.'),
 'SAN CHIH SEMICONDUCTOR':('3579','San Chih Semiconductor Co., Ltd. / 尚志半導體','verified_tw_historical_round8c','TEDC stock table lists San Chih Semiconductor as S3579; company site/EMIS confirm name.'),
 'YEONG GUAN ENERGY GROUP':('1589','Yeong Guan Energy Technology Group Co., Ltd. / 永冠-KY','verified_tw_yahoo_google_round8c','Reuters/ISIN pages show Yeong Guan Energy Technology Group code 1589 / 1589.TW.'),
 'PHARMALLY INTL HLDG':('6452','Pharmally International Holding Company Limited / 康友-KY','verified_tw_historical_round8c','TWSE factbook delisting table and GBI/Twincn show Pharmally code 6452.'),
 'HUNG POO REAL ESTATE DEV':('2536','Hong Pu / Hung Poo Real Estate Development Co., Ltd. / 宏普','verified_tw_yahoo_google_round8c','Yahoo/MarketScreener/TradingView show Hong Pu/Hung Poo Real Estate Development code 2536.'),
}
def read(p):
 with p.open(newline='',encoding='utf-8-sig') as f: return list(csv.DictReader(f))
def write(p,rows,fields):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(rows)
def main():
 mapping=read(MAPPING); events=read(EVENTS); manual=read(MANUAL)
 evcnt=Counter(r['company_name'] for r in events if r.get('country')=='TAIWAN')
 accepted=[]; still=[]
 for m in manual:
  name=m['company_name']
  if name in SEEDS:
   c,matched,status,src=SEEDS[name]
   accepted.append({'country':'TAIWAN','company_name':name,'stock_code':c,'matched_name':matched,'mapping_status':status,'mapping_score':'0.95','mapping_source':'Round8c web/Yahoo/Google evidence: '+src,'verification_basis':'broader_web_yahoo_google_after_user_feedback','event_rows':evcnt[name]})
  else: still.append(m)
 by={a['company_name']:a for a in accepted}
 for r in mapping:
  a=by.get(r.get('company_name')) if r.get('country')=='TAIWAN' else None
  if a:
   for k in ['stock_code','matched_name','mapping_source','mapping_score','mapping_status']: r[k]=str(a[k])
 for r in events:
  a=by.get(r.get('company_name')) if r.get('country')=='TAIWAN' else None
  if a:
   for k in ['stock_code','matched_name','mapping_source','mapping_score','mapping_status']: r[k]=str(a[k])
 write(MAPPING,mapping,list(mapping[0].keys())); write(EVENTS,events,list(events[0].keys()))
 fields=['country','company_name','stock_code','matched_name','mapping_status','mapping_score','mapping_source','verification_basis','event_rows']; write(OUT,accepted,fields)
 write(STILL,still,list(manual[0].keys()) if manual else [])
 stillnames={m['company_name'] for m in still}; write(MANUAL_EVENTS,[e for e in events if e.get('country')=='TAIWAN' and e.get('company_name') in stillnames],list(events[0].keys()))
 summary={'task':'MSCI Taiwan Yahoo/Google broader completion Round 8c','updated_at_taipei':datetime.now().astimezone().isoformat(timespec='seconds'),'manual_before':len(manual),'accepted_unique_mappings':len(accepted),'manual_remaining':len(still),'outputs':{'accepted':str(OUT),'manual_remaining':str(STILL)}}
 SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
 REPORT.write_text('\n'.join(['# MSCI Taiwan Yahoo/Google broader completion — Round 8c','',f'- Manual before: {len(manual)}',f'- Accepted: {len(accepted)}',f'- Manual remaining: {len(still)}','','## Accepted']+[f"- {a['company_name']} -> {a['stock_code']} ({a['matched_name']})" for a in accepted]+['','## Remaining']+[f"- {m['company_name']}" for m in still])+'\n',encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
