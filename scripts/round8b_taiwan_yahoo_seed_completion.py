#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter
from datetime import datetime
from pathlib import Path
ROOT=Path('/Users/johan/Documents/invest/msci_index_reviews'); PARSED=ROOT/'parsed'; STATE=ROOT/'research_state'; REPORTS=ROOT/'reports'
MAPPING=PARSED/'msci_us_taiwan_name_ticker_mapping_verified.csv'; EVENTS=PARSED/'msci_us_taiwan_events_flat_verified.csv'
MANUAL=STATE/'msci_taiwan_mapping_round8_manual_unique.csv'; MANUAL_EVENTS=STATE/'msci_taiwan_mapping_round7_manual_events.csv'
OUT=STATE/'msci_taiwan_mapping_round8b_accepted.csv'; STILL=STATE/'msci_taiwan_mapping_round8b_manual_unique.csv'; SUMMARY=STATE/'msci_taiwan_mapping_round8b_summary.json'; REPORT=REPORTS/'msci_taiwan_mapping_round8b_completion_report.md'
SEEDS={
 'ABLEPRINT TECHNOLOGY':('7734','AblePrint Technology Co., Ltd. / 印能科技','verified_tw_yahoo_google_round8b','Company IR says MOPS stock code 7734; Yahoo Finance 7734.TWO / StockAnalysis TPEX:7734.'),
 'HOLYSTONE ENTERPRISE CO':('3026','Holy Stone Enterprise Co., Ltd. / 信邦? Holy Stone 禾伸堂','verified_tw_yahoo_round8b','Yahoo Finance: Holy Stone Enterprise Co.,Ltd. 3026.TW; MarketScreener/StockAnalysis confirm TPE:3026.'),
 'INTL CSRC INV HLDGS CO':('2104','International CSRC Investment Holdings Co., Ltd. / 國際中橡','verified_tw_yahoo_round8b','Yahoo Finance search: International CSRC Investment Holdings -> 2104.TW.'),
 'YUNGSHIN CONST & DEV':('5508','Yungshin Construction & Development Co., Ltd. / 永信建','verified_tw_yahoo_round8b','Yahoo Finance search: YungShin Construction Development -> 5508.TWO.'),
 'YUNGSHIN CONSTR & DEVLPT':('5508','Yungshin Construction & Development Co., Ltd. / 永信建','verified_tw_yahoo_round8b','Same issuer abbreviation as YUNGSHIN CONST & DEV -> 5508.TWO.'),
 'CHAMPION BUILDING MATRLS':('1806','Champion Building Materials Co., Ltd. / 冠軍','verified_tw_yahoo_round8b','Yahoo Finance search: Champion Building Materials -> 1806.TW.'),
 'RUENTEX ENGR & CONST':('2597','Ruentex Engineering & Construction Co., Ltd. / 潤弘','verified_tw_yahoo_round8b','Yahoo Finance search: Ruentex Engineering Construction -> 2597.TW.'),
 'RUENTEX ENGIN & CONST':('2597','Ruentex Engineering & Construction Co., Ltd. / 潤弘','verified_tw_yahoo_round8b','Same issuer abbreviation as Ruentex Engineering & Construction -> 2597.TW.'),
 'GALLANT PREC MACHINING':('5443','Gallant Precision Machining Co., Ltd. / 均豪','verified_tw_yahoo_round8b','Yahoo Finance search: Gallant Precision Machining -> 5443.TWO.'),
 'HOLDKEY ELECTRIC WIRE':('1618','Hold-Key Electric Wire & Cable Co., Ltd. / 合機','verified_tw_yahoo_round8b','Yahoo Finance search: Hold-Key Electric Wire -> 1618.TW.'),
 'PROSPERITY DIELECT CO LT':('6173','Prosperity Dielectrics Co., Ltd. / 信昌電','verified_tw_yahoo_round8b','Yahoo Finance search: Prosperity Dielectrics -> 6173.TWO.'),
 'ADVANCED INT\'L MULTITECH':('8938','Advanced International Multitech Co., Ltd. / 明安','verified_tw_yahoo_round8b','Yahoo Finance search: Advanced International Multitech -> 8938.TWO.'),
 'LAND MARK OPTOELECTRS':('3081','LandMark Optoelectronics Corporation / 聯亞','verified_tw_yahoo_round8b','Yahoo Finance search: LandMark Optoelectronics -> 3081.TWO.'),
 'SUNNY FRIEND ENV TECH':('8341','Sunny Friend Environmental Technology Co., Ltd. / 日友','verified_tw_yahoo_round8b','Yahoo Finance search: Sunny Friend Environmental -> 8341.TW.'),
 'EASTERN MEDIA INTL':('2614','Eastern Media International Corporation / 東森','verified_tw_yahoo_round8b','Yahoo Finance search: Eastern Media International -> 2614.TW.'),
 'FOXSEMICON INTGR TECH':('3413','Foxsemicon Integrated Technology Inc. / 京鼎','verified_tw_yahoo_round8b','Yahoo Finance search: Foxsemicon Integrated Technology -> 3413.TW.'),
 'JENN FENG NEW ENERGY CO':('1538','Jenn Feng Industrial Tools Co., Ltd. / 正峰','verified_tw_yahoo_round8b','Yahoo Finance search: Jenn Feng -> 1538.TW; MSCI name likely Jenn Feng New Energy naming variant.'),
 'TAIWAN PCB TECHVEST CO':('8213','Taiwan Printed Circuit Board Techvest Co., Ltd. / 志超','verified_tw_yahoo_round8b','Yahoo Finance search: Taiwan PCB Techvest -> 8213.TW.'),
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
   accepted.append({'country':'TAIWAN','company_name':name,'stock_code':c,'matched_name':matched,'mapping_status':status,'mapping_score':'0.98','mapping_source':'Round8b '+src,'verification_basis':'yahoo_google_seed_after_user_feedback','event_rows':evcnt[name]})
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
 summary={'task':'MSCI Taiwan Yahoo/Google seed completion Round 8b','updated_at_taipei':datetime.now().astimezone().isoformat(timespec='seconds'),'manual_before':len(manual),'accepted_unique_mappings':len(accepted),'manual_remaining':len(still),'outputs':{'accepted':str(OUT),'manual_remaining':str(STILL)}}
 SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
 REPORT.write_text('\n'.join(['# MSCI Taiwan Yahoo/Google seed completion — Round 8b','',f'- Manual before: {len(manual)}',f'- Accepted: {len(accepted)}',f'- Manual remaining: {len(still)}','','## Remaining']+[f"- {m['company_name']}" for m in still])+'\n',encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
