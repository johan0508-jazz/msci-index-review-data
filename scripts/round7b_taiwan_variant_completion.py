#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re, time, urllib.parse, urllib.request, difflib
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT=Path('/Users/johan/Documents/invest/msci_index_reviews')
PARSED=ROOT/'parsed'; STATE=ROOT/'research_state'; REPORTS=ROOT/'reports'
MAPPING=PARSED/'msci_us_taiwan_name_ticker_mapping_verified.csv'
EVENTS=PARSED/'msci_us_taiwan_events_flat_verified.csv'
TW_REF=PARSED/'mapping_reference_taiwan.csv'; TW_UNIVERSE=STATE/'taiwan_reference_universe_tickers.csv'
CACHE=STATE/'round7_yahoo_search_cache.json'
OUT=STATE/'msci_taiwan_mapping_round7b_accepted.csv'
MANUAL_UNIQUE=STATE/'msci_taiwan_mapping_round7_manual_unique.csv'
MANUAL_EVENTS=STATE/'msci_taiwan_mapping_round7_manual_events.csv'
SUMMARY=STATE/'msci_taiwan_mapping_round7b_summary.json'
REPORT=REPORTS/'msci_taiwan_mapping_round7_completion_report.md'

OVERRIDES={
 'LEE CHANG YUNG CHEM IND':('1704','LCY Chemical Corp. / 李長榮化學','verified_tw_current_round7b','Manual high-confidence: LCY Chemical Corp. is TWSE 1704; MSCI abbreviation Lee Chang Yung Chem Ind.'),
 'ASIA PACIFIC TELECOM CO':('3682','Asia Pacific Telecom Co., Ltd. / 亞太電信','verified_tw_historical_round7b','Manual high-confidence: TWSE delisted data lists 3682 亞太電; MSCI name Asia Pacific Telecom Co.'),
 'CHUNGHWA PICTURE TUBES':('2475','Chunghwa Picture Tubes, Ltd. / 中華映管','verified_tw_historical_round7b','Manual high-confidence: historical TWSE ticker 2475 for Chunghwa Picture Tubes; delisted.'),
}
CORP=set('INC INCORPORATED CORP CORPORATION CO COMPANY LTD LIMITED PLC SA NV AG THE COMMON STOCK ORDINARY SHARES CLASS NEW TAIWAN CAYMAN HOLDING HOLDINGS GROUP'.split())
GEN=set('TECHNOLOGY TECHNOLOGIES ELECTRONIC ELECTRONICS ELECTRIC INTERNATIONAL PHARMACEUTICALS PHARMA INDUSTRIAL INDUSTRY INDUSTRIES MATERIALS PRECISION ENTERPRISE ENTERPRISES SEMICONDUCTOR SEMICONDUCTORS COMMUNICATION COMMUNICATIONS FINANCIAL DEVELOPMENT COMPUTER COMPUTERS MANUFACTURING MANUFACTURE CHEMICAL PLASTICS PLASTIC OPTICAL OPTO NETWORKS NETWORK ADVANCED TAIWAN CHINA ASIA GLOBAL GENERAL SYSTEM SYSTEMS COMPONENTS COMPONENT STEEL IRON BUILDING TEXTILE FOODS FOOD BIO MEDICAL'.split())
EXP=[(' INTL ',' INTERNATIONAL '),(' INDL ',' INDUSTRIAL '),(' IND ',' INDUSTRY '),(' DEV ',' DEVELOPMENT '),(' DEPT ',' DEPARTMENT '),(' CHEM ',' CHEMICAL '),(' ELEC ',' ELECTRIC '),(' ELECTRS ',' ELECTRONICS '),(' ELECTR ',' ELECTRIC '),(' MFG ',' MANUFACTURING '),(' MACH ',' MACHINERY '),(' TECH ',' TECHNOLOGY '),(' TELECOM CO',' TELECOM'),(' INV HLDGS',' INVESTMENT HOLDINGS'),(' CONST ',' CONSTRUCTION '),(' AUTO PARTS INDL',' AUTO PARTS INDUSTRIAL'),(' SILICON PRO',' SILICON PRODUCTS')]
def read(p):
 with p.open(newline='',encoding='utf-8-sig') as f: return list(csv.DictReader(f))
def write(p,rows,fields):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(rows)
def code(s):
 s=str(s or '').strip().upper(); s=re.sub(r'\.(TW|TWO)$','',s); return s.zfill(4) if s.isdigit() and len(s)<=4 else s
def norm(s,drop=False):
 s=(s or '').upper().replace('&',' AND '); s=re.sub(r'\([^)]*\)',' ',s); s=re.sub(r'[^A-Z0-9 ]+',' ',s)
 return ' '.join(w for w in s.split() if w not in CORP and not(drop and w in GEN))
def sim(a,b):
 a=norm(a); b=norm(b)
 if not a or not b: return 0.0
 ta=set(a.split()); tb=set(b.split()); dice=2*len(ta&tb)/(len(ta)+len(tb)) if ta and tb else 0
 return max(dice,difflib.SequenceMatcher(None,a,b).ratio(),1.0 if (a in b or b in a) and min(len(a),len(b))>=5 else 0)
def ft(s):
 t=norm(s).split(); return t[0] if t else ''
def distinct(a,b):
 return bool(set(norm(a,True).split()) & set(norm(b,True).split())) or norm(a)==norm(b) or ft(a)==ft(b)
def ok(a,b,best,second):
 return (norm(a)==norm(b) and distinct(a,b)) or ((norm(a) in norm(b) or norm(b) in norm(a)) and ft(a)==ft(b) and distinct(a,b)) or (best>=0.92 and distinct(a,b) and best-second>=0.035)
def variants(name):
 out=[name]
 s=' '+name+' '
 for old,new in EXP: s=s.replace(old,new)
 out.append(' '.join(s.split()))
 out.append(out[-1]+' Taiwan stock')
 # remove trailing generic company words for autocomplete
 out.append(re.sub(r'\b(CO|CORP|INC|LTD)\b','',out[-2]).strip())
 return list(dict.fromkeys([x for x in out if x]))
def fetch(q,cache):
 if q in cache: return cache[q]
 url='https://query1.finance.yahoo.com/v1/finance/search?'+urllib.parse.urlencode({'q':q,'quotesCount':8,'newsCount':0,'lang':'en-US','region':'US'})
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
  with urllib.request.urlopen(req,timeout=20) as r: quotes=json.load(r).get('quotes',[])
 except Exception as e: quotes=[{'error':repr(e)}]
 cache[q]=quotes; CACHE.write_text(json.dumps(cache,ensure_ascii=False,indent=2),encoding='utf-8'); time.sleep(0.08); return quotes

def main():
 mapping=read(MAPPING); events=read(EVENTS); manual=read(MANUAL_UNIQUE)
 tw_universe={code(r['ticker']) for r in read(TW_UNIVERSE) if r.get('ticker')}
 ref_by_code=defaultdict(list)
 for r in read(TW_REF): ref_by_code[code(r.get('ticker',''))].append(r)
 cache=json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
 evcnt=Counter(r['company_name'] for r in events if r.get('country')=='TAIWAN')
 accepted=[]; still=[]
 for m in manual:
  name=m['company_name']; decision=None
  if name in OVERRIDES:
   c,matched,status,src=OVERRIDES[name]; decision={'country':'TAIWAN','company_name':name,'stock_code':c,'matched_name':matched,'mapping_status':status,'mapping_score':'0.99','mapping_source':'Round7b '+src,'verification_basis':'manual_high_confidence_common_reference','event_rows':evcnt[name]}
  else:
   qhits=[]
   for q in variants(name):
    for x in fetch(q,cache):
     if not isinstance(x,dict) or x.get('error'): continue
     c=code(x.get('symbol','')); sym=str(x.get('symbol','')); exch=str(x.get('exchange') or '')
     if c not in tw_universe: continue
     if not (sym.endswith('.TW') or sym.endswith('.TWO') or exch in {'TAI','TWO'}): continue
     cname=str(x.get('longname') or x.get('shortname') or '')
     qhits.append((sim(name,cname),q,x,cname,c))
   qhits.sort(key=lambda z:z[0],reverse=True)
   if qhits:
    best=qhits[0]; second=qhits[1][0] if len(qhits)>1 else 0.0
    sc,q,x,cname,c=best
    if ok(name,cname,sc,second):
     refs=' | '.join(sorted({r.get('name','') for r in ref_by_code.get(c,[]) if r.get('name')})[:6])
     decision={'country':'TAIWAN','company_name':name,'stock_code':c,'matched_name':cname,'mapping_status':'verified_tw_current_round7b','mapping_score':f'{sc:.4f}','mapping_source':f'Round7b variant current-code discovery: Yahoo Finance search matched `{cname}`/{x.get("symbol")}; code exists in TWSE/TPEx/FinLab Taiwan reference universe. Local refs: {refs}','verification_basis':'variant_yahoo_name_match_plus_official_current_code_universe','event_rows':evcnt[name]}
  if decision: accepted.append(decision)
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
 af=['country','company_name','stock_code','matched_name','mapping_status','mapping_score','mapping_source','verification_basis','event_rows']; write(OUT,accepted,af)
 mf=list(manual[0].keys()) if manual else []; write(MANUAL_UNIQUE,still,mf)
 stillnames={m['company_name'] for m in still}; write(MANUAL_EVENTS,[e for e in events if e.get('country')=='TAIWAN' and e.get('company_name') in stillnames],list(events[0].keys()))
 summary={'task':'MSCI Taiwan mapping completion Round 7b','updated_at_taipei':datetime.now().astimezone().isoformat(timespec='seconds'),'manual_before':len(manual),'accepted_unique_mappings':len(accepted),'manual_remaining':len(still),'accepted_by_status':dict(Counter(a['mapping_status'] for a in accepted)),'outputs':{'accepted':str(OUT),'manual_unique':str(MANUAL_UNIQUE),'manual_events':str(MANUAL_EVENTS)}}
 SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
 with REPORT.open('a',encoding='utf-8') as f:
  f.write('\n\n## Round 7b — variant query補齊\n\n')
  f.write(f"- Manual before: {len(manual)}\n- Accepted: {len(accepted)}\n- Manual remaining: {len(still)}\n- Output: `{OUT}`\n- Updated manual list: `{MANUAL_UNIQUE}`\n")
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
