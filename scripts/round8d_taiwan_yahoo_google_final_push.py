#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter
from datetime import datetime
from pathlib import Path
ROOT=Path('/Users/johan/Documents/invest/msci_index_reviews'); PARSED=ROOT/'parsed'; STATE=ROOT/'research_state'; REPORTS=ROOT/'reports'
MAPPING=PARSED/'msci_us_taiwan_name_ticker_mapping_verified.csv'; EVENTS=PARSED/'msci_us_taiwan_events_flat_verified.csv'
MANUAL=STATE/'msci_taiwan_mapping_round8c_manual_unique.csv'; MANUAL_EVENTS=STATE/'msci_taiwan_mapping_round7_manual_events.csv'
OUT=STATE/'msci_taiwan_mapping_round8d_accepted.csv'; STILL=STATE/'msci_taiwan_mapping_round8d_manual_unique.csv'; SUMMARY=STATE/'msci_taiwan_mapping_round8d_summary.json'; REPORT=REPORTS/'msci_taiwan_mapping_round8d_completion_report.md'
SEEDS={
 'PHOENIXTEC POWER CO':('2411','Phoenixtec Power Co., Ltd. / 飛瑞','verified_tw_historical_round8d','MBAlib Taiwan Mid-Cap 100 table lists 2411 飛瑞 Phoenixtec Power; Eaton acquisition/delisting pages confirm Phoenixtec Power was listed and then acquired/delisted by Eaton.'),
 'DAHAN DEVELOPMENT CORP':('5530','Dahan Development Corp., later Lungyen Life Service Corp. / 大漢建設→龍巖','verified_tw_historical_round8d','Lungyen annual report states Stock code 5530 and formerly known as Dahan Development Corp.; MoneyDJ confirms 2011 rename to Lungyen.'),
 'KAI CHIEH INTL INV':('2721','Kai Chieh International Investment Ltd. / 楷捷-KY','verified_tw_yahoo_google_round8d','Cnyes and CSRHub pages show Kai Chieh International Investment Ltd. ticker/code 2721.'),
 'AVY PRECISION TECH':('5392','Abico AVY Co., Ltd., formerly AVY Precision Technology Inc. / 能率','verified_tw_yahoo_google_round8d','Yahoo Finance 5392.TWO and StockAnalysis/MarketScreener state Abico AVY was formerly AVY Precision Technology Inc.; ticker 5392.'),
 'UNIZYX HOLDING':('3704','Unizyx Holding Corporation / 合勤控','verified_tw_yahoo_google_round8d','Yahoo/CheckMan/CompanyInfoTW show Unizyx Holding Corporation stock symbol 3704.TW / code 3704.'),
 'SOLARTECH ENERGY CORP':('3561','Solartech Energy Corp. / 昇陽光電','verified_tw_historical_round8d','Yahoo Finance and MarketScreener show Solartech Energy Corp. 3561.TW; TWSE factbook delisting table lists Solartech Energy Corp. code 3561.'),
 'WONTEN TECHNOLOGY CO':('6190','Wontex/Wonten Technology Co., Ltd. / 萬泰科技','verified_tw_yahoo_google_round8d','Company investor page says stock code 6190; Yahoo/Google name variant maps Wonten/Wontex Technology to 萬泰科技.'),
 'INTEGRATED MEMORY LOGIC':('3638','Integrated Memory Logic Limited / F-IML','verified_tw_historical_round8d','PRNewswire/SEC acquisition release identifies Integrated Memory Logic Limited as iML TW:3638; later ceased trading after Exar acquisition.'),
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
   accepted.append({'country':'TAIWAN','company_name':name,'stock_code':c,'matched_name':matched,'mapping_status':status,'mapping_score':'0.95','mapping_source':'Round8d web/Yahoo/Google evidence: '+src,'verification_basis':'broader_web_yahoo_google_after_user_feedback','event_rows':evcnt[name]})
  else:
   still.append(m)
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
 summary={'task':'MSCI Taiwan Yahoo/Google broader completion Round 8d','updated_at_taipei':datetime.now().astimezone().isoformat(timespec='seconds'),'manual_before':len(manual),'accepted_unique_mappings':len(accepted),'manual_remaining':len(still),'outputs':{'accepted':str(OUT),'manual_remaining':str(STILL)}}
 SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
 REPORT.write_text('\n'.join(['# MSCI Taiwan Yahoo/Google broader completion — Round 8d','',f'- Manual before: {len(manual)}',f'- Accepted: {len(accepted)}',f'- Manual remaining: {len(still)}','','## Accepted']+[f"- {a['company_name']} -> {a['stock_code']} ({a['matched_name']})" for a in accepted]+['','## Remaining']+[f"- {m['company_name']}" for m in still])+'\n',encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
