#!/usr/bin/env python3
"""Round 7: conservatively complete Taiwan MSCI name -> stock code mapping.

Uses official TWSE/TPEx delisted English data where available, plus Yahoo Finance
search only as a name-discovery aid for current listed/OTC names; any Yahoo hit
must resolve to a code present in the local TWSE/TPEx/FinLab Taiwan reference
universe before it is accepted.

Rows not accepted are exported for manual review.
"""
from __future__ import annotations

import csv
import difflib
import json
import re
import ssl
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path('/Users/johan/Documents/invest/msci_index_reviews')
PARSED = ROOT / 'parsed'
STATE = ROOT / 'research_state'
REPORTS = ROOT / 'reports'

MAPPING = PARSED / 'msci_us_taiwan_name_ticker_mapping_verified.csv'
EVENTS = PARSED / 'msci_us_taiwan_events_flat_verified.csv'
TW_REF = PARSED / 'mapping_reference_taiwan.csv'
TW_UNIVERSE = STATE / 'taiwan_reference_universe_tickers.csv'
YAHOO_CACHE = STATE / 'round7_yahoo_search_cache.json'
OUT_ACCEPTED = STATE / 'msci_taiwan_mapping_round7_accepted.csv'
OUT_MANUAL_UNIQUE = STATE / 'msci_taiwan_mapping_round7_manual_unique.csv'
OUT_MANUAL_EVENTS = STATE / 'msci_taiwan_mapping_round7_manual_events.csv'
OUT_SUMMARY = STATE / 'msci_taiwan_mapping_round7_summary.json'
REPORT = REPORTS / 'msci_taiwan_mapping_round7_completion_report.md'

CORP_SUFFIX = {
    'INC','INCORPORATED','CORP','CORPORATION','CO','COMPANY','LTD','LIMITED','PLC','SA','NV','AG','THE',
    'COMMON','STOCK','ORDINARY','SHARES','CLASS','NEW','TAIWAN','CAYMAN','HOLDING','HOLDINGS','GROUP'
}
GENERIC = {
    'TECHNOLOGY','TECHNOLOGIES','ELECTRONIC','ELECTRONICS','ELECTRIC','INTERNATIONAL','PHARMACEUTICALS',
    'PHARMA','INDUSTRIAL','INDUSTRY','INDUSTRIES','MATERIALS','PRECISION','ENTERPRISE','ENTERPRISES',
    'SEMICONDUCTOR','SEMICONDUCTORS','COMMUNICATION','COMMUNICATIONS','FINANCIAL','HOLDINGS','HOLDING',
    'DEVELOPMENT','COMPUTER','COMPUTERS','MANUFACTURING','MANUFACTURE','CHEMICAL','PLASTICS','PLASTIC',
    'OPTICAL','OPTO','NETWORKS','NETWORK','ADVANCED','TAIWAN','CHINA','ASIA','GLOBAL','GENERAL','SYSTEM',
    'SYSTEMS','COMPONENTS','COMPONENT','STEEL','IRON','BUILDING','TEXTILE','FOODS','FOOD','BIO','MEDICAL'
}

MANUAL_OVERRIDES: dict[str, dict[str, str]] = {
    # Explicit historical evidence reviewed in prior rounds or common official references.
    'EPISTAR CORP': {'code':'2448','matched_name':'Epistar Corporation / 晶元光電','status':'verified_tw_historical_round7','source':'Prior R4 historical evidence: Ennostar official release identifies Epistar (TAIEX:2448); delisted after share conversion.'},
    'INOTERA MEMORIES': {'code':'3474','matched_name':'Inotera Memories, Inc. / 華亞科技','status':'verified_tw_historical_round7','source':'Prior R4 historical evidence: Micron/Digitimes/CTIMES sources identify Inotera historical ticker 3474; delisted after acquisition.'},
    'INOTERA MEMORIES (ATM)': {'code':'3474','matched_name':'Inotera Memories, Inc. / 華亞科技','status':'verified_tw_historical_round7','source':'Same issuer as INOTERA MEMORIES; ATM line mapped to historical ticker 3474 for MSCI event identity.'},
    'PRO MOS TECHNOLOGIES': {'code':'5387','matched_name':'ProMOS Technologies Inc. / 茂德科技','status':'verified_tw_historical_round7','source':'Prior R4 historical evidence: Focus Taiwan + MarketScreener inactive instrument list ProMOS 5387; OTC delisted.'},
    'WINTEK': {'code':'2384','matched_name':'Wintek Corporation / 勝華科技','status':'verified_tw_historical_round7','source':'Prior R4 historical evidence: TWSE fact book + MarketScreener inactive instrument list Wintek 2384; delisted.'},
    'CHINA LIFE INSURANCE CO': {'code':'2823','matched_name':'China Life Insurance Co., Ltd. / 中國人壽','status':'verified_tw_historical_round7','source':'Prior R4 historical evidence: KGI Life profile + TWSE delisting data identify China Life 2823; delisted 2021-12-30.'},
    'RICHTEK TECHNOLOGY CORP': {'code':'6286','matched_name':'Richtek Technology Corporation / 立錡科技','status':'verified_tw_historical_round7','source':'Prior R4 historical evidence: MediaTek official acquisition release identifies Richtek (TSE:6286); delisted 2016-04-29.'},
    'EVERGREEN INTERNATIONAL': {'code':'2607','matched_name':'Evergreen International Storage & Transport / 榮運','status':'verified_tw_historical_round7','source':'Prior R4 historical evidence: FT/Yahoo/StockAnalysis identify Evergreen International Storage & Transport as 2607 on TWSE.'},
    'WATERLAND FINANCIAL': {'code':'2889','matched_name':'IBF Financial Holdings / Waterland Financial / 國票金','status':'verified_tw_historical_round7','source':'Prior R4 historical evidence: FT/MarketScreener state IBF Financial Holdings 2889 was formerly Waterland Financial.'},
    'SINCERE NAVIGATION': {'code':'2605','matched_name':'Sincere Navigation Corporation / 新興航運','status':'verified_tw_historical_round7','source':'Prior R4 conflict review: company investor FAQ/TWSE quote sources identify 2605.'},
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader(); w.writerows(rows)


def clean_code(x: str) -> str:
    s = str(x or '').strip().upper()
    s = re.sub(r'\.(TW|TWO)$', '', s)
    return s.zfill(4) if s.isdigit() and len(s) <= 4 else s


def norm(s: str, *, drop_generic: bool = False) -> str:
    s = (s or '').upper().replace('&', ' AND ')
    s = re.sub(r'\([^)]*\)', ' ', s)
    s = re.sub(r'[^A-Z0-9 ]+', ' ', s)
    words = []
    for w in s.split():
        if w in CORP_SUFFIX: continue
        if drop_generic and w in GENERIC: continue
        words.append(w)
    return ' '.join(words)


def tokens(s: str, *, drop_generic: bool = False) -> set[str]:
    return set(norm(s, drop_generic=drop_generic).split())


def sim(a: str, b: str) -> float:
    na, nb = norm(a), norm(b)
    if not na or not nb: return 0.0
    ta, tb = set(na.split()), set(nb.split())
    dice = 2 * len(ta & tb) / (len(ta) + len(tb)) if ta and tb else 0.0
    seq = difflib.SequenceMatcher(None, na, nb).ratio()
    subset = 1.0 if (na in nb or nb in na) and min(len(na), len(nb)) >= 5 else 0.0
    return max(dice, seq, subset)


def first_token(s: str) -> str:
    t = norm(s).split()
    return t[0] if t else ''


def distinctive_ok(msci: str, cand: str) -> bool:
    mt, ct = tokens(msci, drop_generic=True), tokens(cand, drop_generic=True)
    if mt and ct and (mt & ct): return True
    # Allow exact acronym/short names like LITE ON IT only if full normalized strings align closely.
    return norm(msci) == norm(cand) or first_token(msci) == first_token(cand)


def acceptable(msci: str, cand_name: str, best_score: float, second_score: float) -> bool:
    nm, nc = norm(msci), norm(cand_name)
    if not nm or not nc: return False
    if nm == nc and distinctive_ok(msci, cand_name): return True
    if (nm in nc or nc in nm) and first_token(msci) == first_token(cand_name) and distinctive_ok(msci, cand_name): return True
    if best_score >= 0.94 and distinctive_ok(msci, cand_name) and best_score - second_score >= 0.04:
        return True
    return False


def fetch_json(url: str, *, context=None):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0', 'Accept':'application/json,text/plain,*/*'})
    with urllib.request.urlopen(req, timeout=25, context=context) as r:
        return json.load(r)


def load_delisted_refs() -> list[dict[str, str]]:
    ctx = ssl._create_unverified_context()
    refs: list[dict[str, str]] = []
    # TWSE official English delisted table.
    try:
        j = fetch_json('https://www.twse.com.tw/rwd/en/company/suspendListing?response=json', context=ctx)
        for r in j.get('data', []):
            if len(r) >= 3:
                refs.append({'source':'TWSE EN suspendListing official', 'code':clean_code(r[2]), 'name':str(r[1]).strip(), 'delist_date':str(r[0]).strip()})
    except Exception as e:
        print('WARN TWSE delisted fetch failed', repr(e))
    # TPEx official English delisted table by year.
    for y in range(2005, 2027):
        try:
            url = 'https://www.tpex.org.tw/www/en-us/company/deListed?' + urllib.parse.urlencode({'date':str(y), 'reason':'-1', 'code':''})
            j = fetch_json(url, context=ctx)
            for r in j.get('tables', [{}])[0].get('data', []):
                if len(r) >= 3:
                    refs.append({'source':'TPEx EN deListed official', 'code':clean_code(r[0]), 'name':str(r[1]).strip(), 'delist_date':str(r[2]).strip()})
        except Exception as e:
            print('WARN TPEx delisted fetch failed', y, repr(e))
            break
    return refs


def yahoo_search(q: str, cache: dict[str, object]) -> list[dict[str, object]]:
    if q in cache:
        return cache[q]  # type: ignore[return-value]
    url = 'https://query1.finance.yahoo.com/v1/finance/search?' + urllib.parse.urlencode({'q':q, 'quotesCount':8, 'newsCount':0, 'lang':'en-US', 'region':'US'})
    try:
        j = fetch_json(url)
        quotes = j.get('quotes', [])
    except Exception as e:
        quotes = [{'error': repr(e)}]
    cache[q] = quotes
    YAHOO_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
    time.sleep(0.08)
    return quotes  # type: ignore[return-value]


def main() -> None:
    mapping = read_csv(MAPPING)
    events = read_csv(EVENTS)
    tw_universe = {clean_code(r['ticker']) for r in read_csv(TW_UNIVERSE) if r.get('ticker')}
    ref_rows = read_csv(TW_REF)
    ref_by_code = defaultdict(list)
    for r in ref_rows:
        ref_by_code[clean_code(r.get('ticker',''))].append(r)

    event_count = Counter(r['company_name'] for r in events if r.get('country') == 'TAIWAN')
    existing_by_name = {r['company_name']: r for r in mapping if r.get('country') == 'TAIWAN'}
    targets = [r for r in mapping if r.get('country') == 'TAIWAN' and not (r.get('stock_code') or '').strip()]

    delisted_refs = load_delisted_refs()
    cache = json.loads(YAHOO_CACHE.read_text(encoding='utf-8')) if YAHOO_CACHE.exists() else {}

    accepted: list[dict[str, object]] = []
    manual: list[dict[str, object]] = []

    for r in targets:
        name = r['company_name']
        decision = None
        candidates: list[dict[str, object]] = []

        if name in MANUAL_OVERRIDES:
            o = MANUAL_OVERRIDES[name]
            decision = {
                'country':'TAIWAN','company_name':name,'stock_code':o['code'],'matched_name':o['matched_name'],
                'mapping_source':o['source'],'mapping_score':'0.99','mapping_status':o['status'],
                'verification_basis':'manual_override_prior_evidence','event_rows':event_count[name]
            }
        else:
            # Official delisted English references first.
            scored = sorted([(sim(name, d['name']), d) for d in delisted_refs], key=lambda x: x[0], reverse=True)
            if scored:
                best, second = scored[0], scored[1][0] if len(scored) > 1 else 0.0
                sc, d = best
                candidates.append({'candidate_source':d['source'], 'candidate_code':d['code'], 'candidate_name':d['name'], 'candidate_score':round(sc,4), 'candidate_note':f"delist_date={d.get('delist_date','')}"})
                if acceptable(name, d['name'], sc, second):
                    decision = {
                        'country':'TAIWAN','company_name':name,'stock_code':d['code'],'matched_name':d['name'],
                        'mapping_source':f"Round7 official historical delisted source: {d['source']} delist_date={d.get('delist_date','')}",
                        'mapping_score':f'{sc:.4f}','mapping_status':'verified_tw_historical_round7',
                        'verification_basis':'official_twse_tpex_delisted_english','event_rows':event_count[name]
                    }

        if decision is None:
            quotes = yahoo_search(name, cache)
            q_cands = []
            for q in quotes:
                if not isinstance(q, dict) or q.get('error'): continue
                sym = str(q.get('symbol',''))
                code = clean_code(sym)
                exch = str(q.get('exchange') or q.get('exchDisp') or '')
                if code not in tw_universe: continue
                if not (sym.endswith('.TW') or sym.endswith('.TWO') or exch in {'TAI','TWO','Taiwan','Taipei Exchange'}): continue
                cand_name = str(q.get('longname') or q.get('shortname') or '')
                sc = sim(name, cand_name)
                q_cands.append((sc, q, cand_name, code))
            q_cands.sort(key=lambda x: x[0], reverse=True)
            if q_cands:
                sc, q, cand_name, code = q_cands[0]
                second = q_cands[1][0] if len(q_cands) > 1 else 0.0
                candidates.append({'candidate_source':'Yahoo Finance search + current TW universe', 'candidate_code':code, 'candidate_name':cand_name, 'candidate_score':round(sc,4), 'candidate_note':str(q.get('symbol',''))})
                if acceptable(name, cand_name, sc, second):
                    # Enrich matched name with local reference names if possible.
                    refs = ref_by_code.get(code, [])
                    ref_names = ' | '.join(sorted({x.get('name','') for x in refs if x.get('name')} )[:6])
                    decision = {
                        'country':'TAIWAN','company_name':name,'stock_code':code,'matched_name':cand_name,
                        'mapping_source':f"Round7 current-code discovery: Yahoo Finance search matched `{cand_name}`/{q.get('symbol','')}; code exists in TWSE/TPEx/FinLab Taiwan reference universe. Local refs: {ref_names}",
                        'mapping_score':f'{sc:.4f}','mapping_status':'verified_tw_current_round7',
                        'verification_basis':'yahoo_name_match_plus_official_current_code_universe','event_rows':event_count[name]
                    }

        if decision:
            accepted.append(decision)
        else:
            top = candidates[0] if candidates else {}
            manual.append({
                'country':'TAIWAN','company_name':name,'event_rows':event_count[name],
                'current_mapping_status':r.get('mapping_status',''), 'current_matched_name':r.get('matched_name',''),
                'top_candidate_source':top.get('candidate_source',''), 'top_candidate_code':top.get('candidate_code',''),
                'top_candidate_name':top.get('candidate_name',''), 'top_candidate_score':top.get('candidate_score',''),
                'top_candidate_note':top.get('candidate_note',''),
                'manual_instruction':'Please verify historical TWSE/TPEx stock code from MOPS/TWSE/TPEx/company IR; fill stock_code if confirmed.'
            })

    # Apply accepted decisions.
    by_name = {a['company_name']: a for a in accepted}
    for r in mapping:
        a = by_name.get(r.get('company_name')) if r.get('country') == 'TAIWAN' else None
        if a:
            r.update({k:str(a[k]) for k in ['stock_code','matched_name','mapping_source','mapping_score','mapping_status']})
    for r in events:
        a = by_name.get(r.get('company_name')) if r.get('country') == 'TAIWAN' else None
        if a:
            r.update({k:str(a[k]) for k in ['stock_code','matched_name','mapping_source','mapping_score','mapping_status']})

    write_csv(MAPPING, mapping, list(mapping[0].keys()))
    write_csv(EVENTS, events, list(events[0].keys()))

    acc_fields = ['country','company_name','stock_code','matched_name','mapping_status','mapping_score','mapping_source','verification_basis','event_rows']
    man_fields = ['country','company_name','event_rows','current_mapping_status','current_matched_name','top_candidate_source','top_candidate_code','top_candidate_name','top_candidate_score','top_candidate_note','manual_instruction']
    write_csv(OUT_ACCEPTED, accepted, acc_fields)
    write_csv(OUT_MANUAL_UNIQUE, manual, man_fields)
    manual_names = {m['company_name'] for m in manual}
    manual_events = [e for e in events if e.get('country') == 'TAIWAN' and e.get('company_name') in manual_names]
    write_csv(OUT_MANUAL_EVENTS, manual_events, list(events[0].keys()))

    after_missing = [r for r in mapping if r.get('country') == 'TAIWAN' and not (r.get('stock_code') or '').strip()]
    summary = {
        'task':'MSCI Taiwan mapping completion Round 7',
        'updated_at_taipei':datetime.now().astimezone().isoformat(timespec='seconds'),
        'taiwan_unique_targets_missing_before':len(targets),
        'accepted_unique_mappings':len(accepted),
        'manual_unique_remaining':len(manual),
        'taiwan_unique_missing_after':len(after_missing),
        'accepted_by_status':Counter(str(a['mapping_status']) for a in accepted),
        'outputs':{
            'accepted':str(OUT_ACCEPTED),
            'manual_unique':str(OUT_MANUAL_UNIQUE),
            'manual_events':str(OUT_MANUAL_EVENTS),
            'summary':str(OUT_SUMMARY),
        },
        'method':'Conservative acceptance: official TWSE/TPEx English delisted exact/high-confidence match, manual prior-evidence overrides, or Yahoo Finance name discovery only when code exists in official/local current Taiwan reference universe. Remaining rows require human review.'
    }
    OUT_SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=lambda o: dict(o) if isinstance(o, Counter) else str(o)), encoding='utf-8')

    md = [
        '# MSCI Taiwan mapping completion — Round 7', '',
        '## 結論',
        f"- 本輪補齊前缺 code 的 Taiwan unique names：{len(targets)}",
        f"- 本輪保守接受並寫回：{len(accepted)}",
        f"- 仍需人工檢查：{len(manual)}",
        f"- 寫回後仍缺 code 的 Taiwan unique names：{len(after_missing)}",
        '',
        '## 驗證規則',
        '- 下市/下櫃：優先採 TWSE/TPEx official English delisted tables；名稱需 exact / high-confidence 且避開 generic-token 假陽性。',
        '- 現行上市櫃：Yahoo Finance search 只作名稱發現；代碼必須存在本地 TWSE/TPEx/FinLab Taiwan reference universe 才接受。',
        '- 先前 R4 已人工查證的歷史案例，用 prior-evidence override 寫回。',
        '- 其餘不硬猜，列入人工清單。',
        '',
        '## 輸出檔',
        f"- Accepted mappings: `{OUT_ACCEPTED}`",
        f"- Manual unique list: `{OUT_MANUAL_UNIQUE}`",
        f"- Manual event rows: `{OUT_MANUAL_EVENTS}`",
        f"- Summary JSON: `{OUT_SUMMARY}`",
        '',
        '## Accepted by status',
    ]
    for k, v in Counter(str(a['mapping_status']) for a in accepted).most_common():
        md.append(f'- {k}: {v}')
    md += ['', '## 人工清單前 80 筆']
    for m in manual[:80]:
        cand = f"；top candidate {m.get('top_candidate_code','')} {m.get('top_candidate_name','')} score={m.get('top_candidate_score','')}" if m.get('top_candidate_code') else ''
        md.append(f"- {m['company_name']}（events={m['event_rows']}）{cand}")
    REPORT.write_text('\n'.join(md) + '\n', encoding='utf-8')

    print(json.dumps(summary, ensure_ascii=False, indent=2, default=lambda o: dict(o) if isinstance(o, Counter) else str(o)))

if __name__ == '__main__':
    main()
