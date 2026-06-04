#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter
from datetime import datetime
from pathlib import Path
ROOT=Path('/Users/johan/Documents/invest/msci_index_reviews'); PARSED=ROOT/'parsed'; STATE=ROOT/'research_state'; REPORTS=ROOT/'reports'
MAPPING=PARSED/'msci_us_taiwan_name_ticker_mapping_verified.csv'; EVENTS=PARSED/'msci_us_taiwan_events_flat_verified.csv'
MANUAL=STATE/'msci_taiwan_mapping_round8d_manual_unique.csv'; MANUAL_EVENTS=STATE/'msci_taiwan_mapping_round7_manual_events.csv'
OUT=STATE/'msci_taiwan_mapping_round8e_accepted.csv'; STILL=STATE/'msci_taiwan_mapping_round8e_manual_unique.csv'; SUMMARY=STATE/'msci_taiwan_mapping_round8e_summary.json'; REPORT=REPORTS/'msci_taiwan_mapping_round8e_completion_report.md'
SEEDS={
 'KOBIN ENVIRONMNTL ENTER':('1808','Kobin / 國賓大地環保事業股份有限公司, later Ruentex Development / 潤隆建設','verified_tw_historical_round8e','MoneyDJ/MOPS material-info article states 國賓大地環保事業股份有限公司 changed name to 潤隆建設股份有限公司 and stock code remained 1808; web66/kobin.com.tw evidence links Kobin domain to 國賓大地環保事業股份有限公司.'),
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
   accepted.append({'country':'TAIWAN','company_name':name,'stock_code':c,'matched_name':matched,'mapping_status':status,'mapping_score':'0.95','mapping_source':'Round8e web/Google evidence: '+src,'verification_basis':'broader_web_google_after_user_feedback','event_rows':evcnt[name]})
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
 write(STILL,still,list(manual[0].keys()) if manual else ['country','company_name'])
 stillnames={m['company_name'] for m in still}; write(MANUAL_EVENTS,[e for e in events if e.get('country')=='TAIWAN' and e.get('company_name') in stillnames],list(events[0].keys()))
 summary={'task':'MSCI Taiwan Kobin final completion Round 8e','updated_at_taipei':datetime.now().astimezone().isoformat(timespec='seconds'),'manual_before':len(manual),'accepted_unique_mappings':len(accepted),'manual_remaining':len(still),'outputs':{'accepted':str(OUT),'manual_remaining':str(STILL)}}
 SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
 REPORT.write_text('\n'.join(['# MSCI Taiwan Kobin final completion — Round 8e','',f'- Manual before: {len(manual)}',f'- Accepted: {len(accepted)}',f'- Manual remaining: {len(still)}','','## Accepted']+[f"- {a['company_name']} -> {a['stock_code']} ({a['matched_name']})" for a in accepted]+['','## Remaining']+[f"- {m['company_name']}" for m in still])+'\n',encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
