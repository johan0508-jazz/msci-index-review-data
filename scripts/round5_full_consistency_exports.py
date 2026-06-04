#!/usr/bin/env python3
"""Round 5 MSCI ticker audit: consistency checks + backtest-ready exports.

No destructive writes; creates new audit/export files and updates state/report.
Uses only Python stdlib so it can run on the lightweight OpenClaw host.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/Users/johan/Documents/invest/msci_index_reviews')
PARSED = ROOT / 'parsed'
STATE_DIR = ROOT / 'research_state'
REPORTS = ROOT / 'reports'

MAPPING_IN = PARSED / 'msci_us_taiwan_name_ticker_mapping_verified.csv'
EVENTS_IN = PARSED / 'msci_us_taiwan_events_flat_verified.csv'
US_UNIVERSE_IN = STATE_DIR / 'us_price_close_universe_tickers.csv'
TW_UNIVERSE_IN = STATE_DIR / 'taiwan_reference_universe_tickers.csv'
STATE_IN = STATE_DIR / 'msci_ticker_audit_state.json'
REPORT_IN = REPORTS / 'msci_ticker_audit_rounds.md'

MAPPING_BT = PARSED / 'msci_us_taiwan_name_ticker_mapping_verified_backtest_ready.csv'
EVENTS_AUDIT = PARSED / 'msci_us_taiwan_events_flat_audit_verified.csv'
EVENTS_BT = PARSED / 'msci_us_taiwan_events_flat_backtest_ready.csv'
UNMAPPED = STATE_DIR / 'msci_ticker_audit_round5_unmapped_manual_review.csv'
EVIDENCE = STATE_DIR / 'msci_ticker_audit_round5_source_evidence_table.csv'
CHECKS = STATE_DIR / 'msci_ticker_audit_round5_consistency_checks.json'

VERIFIED_STATUSES = {
    'mapped_exact_normalized',
    'verified_tw_reference_fuzzy',
    'verified_us_web_high_confidence',
    'verified_tw_official_round3',
    'verified_conflict_round4',
    'verified_historical_round4',
}
MANUAL_STATUSES = {'needs_review', 'needs_manual_review', 'manual_review_round3', 'manual_review_round4'}

US_PRICE_WINDOWS = [
    {'source': 'adjusted_stock_backtest_Close', 'date_min': '2000-01-03', 'date_max': '2026-04-10'},
    {'source': 'adjusted_stock_live_Close', 'date_min': '2024-01-02', 'date_max': '2026-03-17'},
    {'source': 'finlab_us_price_adj_close', 'date_min': '2016-01-04', 'date_max': '2026-05-19'},
    {'source': 'finlab_us_price_close', 'date_min': '2016-01-04', 'date_max': '2026-05-20'},
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        for row in rows:
            w.writerow(row)


def ticker_norm(x: str) -> str:
    return (x or '').strip().upper()


def parse_date(s: str):
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], '%Y-%m-%d').date()
    except Exception:
        return None


def is_weekday_date(s: str) -> bool:
    d = parse_date(s)
    return bool(d and d.weekday() < 5)


def within_any_us_price_window(s: str) -> bool:
    d = parse_date(s)
    if not d:
        return False
    for win in US_PRICE_WINDOWS:
        if parse_date(win['date_min']) <= d <= parse_date(win['date_max']):
            return True
    return False


def in_us_universe(ticker: str, us_universe: set[str]) -> bool:
    t = ticker_norm(ticker)
    variants = {t, t.replace('.', '-'), t.replace('/', '-'), t.replace('-', '.')}
    return any(v in us_universe for v in variants if v)


def bool_str(v: bool) -> str:
    return 'true' if v else 'false'


def group_counts(rows, keys):
    c = Counter(tuple(r.get(k, '') for k in keys) for r in rows)
    out = []
    for key, n in sorted(c.items()):
        d = {k: v for k, v in zip(keys, key)}
        d['rows'] = n
        out.append(d)
    return out


def main() -> None:
    mapping = read_csv(MAPPING_IN)
    events = read_csv(EVENTS_IN)
    us_universe = {ticker_norm(r['ticker']) for r in read_csv(US_UNIVERSE_IN) if r.get('ticker')}
    tw_universe = {ticker_norm(r['ticker']) for r in read_csv(TW_UNIVERSE_IN) if r.get('ticker')}

    # Mapping-level coverage and ambiguity checks.
    for r in mapping:
        status = r.get('mapping_status', '')
        code = ticker_norm(r.get('stock_code', ''))
        country = r.get('country', '')
        r['is_verified_mapping'] = bool_str(status in VERIFIED_STATUSES and bool(code))
        if country == 'USA':
            r['universe_match'] = bool_str(in_us_universe(code, us_universe))
            r['universe_checked'] = 'us_dayTradePortfolio Close union'
        elif country == 'TAIWAN':
            r['universe_match'] = bool_str(code in tw_universe)
            r['universe_checked'] = 'FinLab/TWSE/TPEx ticker reference universe'
        else:
            r['universe_match'] = 'false'
            r['universe_checked'] = ''
        r['backtest_ready_mapping'] = bool_str(r['is_verified_mapping'] == 'true' and r['universe_match'] == 'true')

    name_to_tickers = defaultdict(set)
    ticker_to_names = defaultdict(set)
    for r in mapping:
        code = ticker_norm(r.get('stock_code', ''))
        if code:
            name_to_tickers[(r.get('country', ''), r.get('company_name', ''))].add(code)
            ticker_to_names[(r.get('country', ''), code)].add(r.get('company_name', ''))
    same_name_multi_ticker = [
        {'country': k[0], 'company_name': k[1], 'ticker_count': len(v), 'tickers': '|'.join(sorted(v))}
        for k, v in name_to_tickers.items() if len(v) > 1
    ]
    one_ticker_multi_name = [
        {'country': k[0], 'stock_code': k[1], 'name_count': len(v), 'company_names': '|'.join(sorted(v))}
        for k, v in ticker_to_names.items() if len(v) > 1
    ]

    mapping_lookup = {(r['country'], r['company_name']): r for r in mapping}

    audited_events = []
    unmapped_rows = []
    for r in events:
        row = dict(r)
        country = row.get('country', '')
        status = row.get('mapping_status', '')
        code = ticker_norm(row.get('stock_code', ''))
        m = mapping_lookup.get((country, row.get('company_name', '')), {})
        is_verified = status in VERIFIED_STATUSES and bool(code)
        if country == 'USA':
            universe_match = in_us_universe(code, us_universe)
            universe_checked = 'us_dayTradePortfolio Close union'
            price_window_ok = within_any_us_price_window(row.get('effective_close_date', ''))
        elif country == 'TAIWAN':
            universe_match = code in tw_universe
            universe_checked = 'FinLab/TWSE/TPEx ticker reference universe'
            # No Taiwan price matrix was available in this audit run; reference-universe presence + weekday is the gate.
            price_window_ok = True
        else:
            universe_match = False
            universe_checked = ''
            price_window_ok = False
        issue_weekday = is_weekday_date(row.get('issue_date', ''))
        announcement_weekday = is_weekday_date(row.get('announcement_date', ''))
        effective_weekday = is_weekday_date(row.get('effective_close_date', ''))
        tradable_date_ok = effective_weekday and price_window_ok
        backtest_ready = is_verified and universe_match and tradable_date_ok
        reasons = []
        if not is_verified:
            reasons.append(f'mapping_status={status or "blank"}')
        if not code:
            reasons.append('missing_stock_code')
        if is_verified and not universe_match:
            reasons.append('ticker_not_in_local_universe')
        if not effective_weekday:
            reasons.append('effective_close_date_not_weekday_or_invalid')
        if country == 'USA' and not price_window_ok:
            reasons.append('effective_close_date_outside_available_us_price_windows')
        row.update({
            'verified_mapping': bool_str(is_verified),
            'mapping_backtest_ready': m.get('backtest_ready_mapping', bool_str(is_verified and universe_match)),
            'universe_checked': universe_checked,
            'ticker_in_required_universe': bool_str(universe_match),
            'issue_date_weekday': bool_str(issue_weekday),
            'announcement_date_weekday': bool_str(announcement_weekday),
            'effective_close_date_weekday': bool_str(effective_weekday),
            'effective_close_date_price_window_ok': bool_str(price_window_ok),
            'event_date_tradable_gate': bool_str(tradable_date_ok),
            'backtest_ready': bool_str(backtest_ready),
            'not_backtest_ready_reason': ';'.join(reasons),
        })
        audited_events.append(row)
        if not backtest_ready:
            unmapped_rows.append(row)

    mapping_bt = [r for r in mapping if r['backtest_ready_mapping'] == 'true']
    events_bt = [r for r in audited_events if r['backtest_ready'] == 'true']

    # Source evidence table, combining applied audit rounds with current mapping status.
    ev = []
    for r in mapping:
        ev.append({
            'country': r['country'], 'company_name': r['company_name'], 'stock_code': r.get('stock_code',''),
            'mapping_status': r.get('mapping_status',''), 'matched_name': r.get('matched_name',''),
            'evidence_type': 'current_mapping_row', 'source_1': r.get('mapping_source',''), 'source_2': '', 'source_3': '',
            'confidence_or_score': r.get('mapping_score',''), 'notes': ''
        })
    # Round 2
    p = STATE_DIR / 'msci_ticker_audit_round2_us_web_verification.csv'
    if p.exists():
        for r in read_csv(p):
            ev.append({'country': r.get('country','USA'), 'company_name': r.get('msci_name',''), 'stock_code': r.get('web_ticker',''), 'mapping_status': r.get('audit_status',''), 'matched_name': r.get('web_company_name',''), 'evidence_type': 'round2_us_web', 'source_1': r.get('source_url',''), 'source_2': '', 'source_3': '', 'confidence_or_score': r.get('confidence',''), 'notes': r.get('notes','')})
    # Round 3
    p = STATE_DIR / 'msci_ticker_audit_round3_taiwan_official_verification.csv'
    if p.exists():
        for r in read_csv(p):
            ev.append({'country': 'TAIWAN', 'company_name': r.get('company_name',''), 'stock_code': r.get('verified_stock_code',''), 'mapping_status': r.get('verification_status',''), 'matched_name': r.get('matched_name',''), 'evidence_type': 'round3_taiwan_official', 'source_1': r.get('source_url',''), 'source_2': r.get('reference_sources',''), 'source_3': '', 'confidence_or_score': '', 'notes': r.get('notes','')})
    # Round 4
    p = STATE_DIR / 'msci_ticker_audit_round4_conflict_review.csv'
    if p.exists():
        for r in read_csv(p):
            ev.append({'country': r.get('country',''), 'company_name': r.get('company_name',''), 'stock_code': r.get('verified_ticker',''), 'mapping_status': r.get('status',''), 'matched_name': r.get('verified_name',''), 'evidence_type': 'round4_conflict_historical', 'source_1': r.get('source_1',''), 'source_2': r.get('source_2',''), 'source_3': r.get('source_3',''), 'confidence_or_score': '', 'notes': r.get('evidence_summary','') or r.get('unverifiable_reason','')})

    mapping_fields = list(mapping[0].keys())
    audited_event_fields = list(events[0].keys()) + [
        'verified_mapping', 'mapping_backtest_ready', 'universe_checked', 'ticker_in_required_universe',
        'issue_date_weekday', 'announcement_date_weekday', 'effective_close_date_weekday',
        'effective_close_date_price_window_ok', 'event_date_tradable_gate', 'backtest_ready', 'not_backtest_ready_reason'
    ]
    evidence_fields = ['country','company_name','stock_code','mapping_status','matched_name','evidence_type','source_1','source_2','source_3','confidence_or_score','notes']
    write_csv(MAPPING_BT, mapping_bt, mapping_fields)
    write_csv(EVENTS_AUDIT, audited_events, audited_event_fields)
    write_csv(EVENTS_BT, events_bt, audited_event_fields)
    write_csv(UNMAPPED, unmapped_rows, audited_event_fields)
    write_csv(EVIDENCE, ev, evidence_fields)

    event_status_counts = Counter((r['country'], r['mapping_status']) for r in audited_events)
    mapping_status_counts = Counter((r['country'], r['mapping_status']) for r in mapping)
    mapped_dist = Counter((r['country'], r['backtest_ready']) for r in audited_events)
    reasons = Counter(r['not_backtest_ready_reason'] for r in audited_events if r['backtest_ready'] != 'true')
    checks = {
        'task': 'MSCI ticker mapping audit R5 — full consistency checks & backtest-ready exports',
        'round': 5,
        'updated_at_taipei': datetime.now(timezone.utc).astimezone().isoformat(),
        'inputs': {k: str(v) for k, v in {
            'mapping_verified': MAPPING_IN, 'events_flat_verified': EVENTS_IN, 'us_universe': US_UNIVERSE_IN, 'taiwan_universe': TW_UNIVERSE_IN}.items()},
        'outputs': {k: str(v) for k, v in {
            'verified_mapping_backtest_ready': MAPPING_BT,
            'events_flat_audit_verified': EVENTS_AUDIT,
            'events_flat_backtest_ready': EVENTS_BT,
            'unmapped_manual_review': UNMAPPED,
            'source_evidence_table': EVIDENCE,
            'consistency_checks': CHECKS}.items()},
        'row_counts': {
            'mapping_unique_company_rows': len(mapping),
            'event_rows': len(events),
            'mapping_backtest_ready_rows': len(mapping_bt),
            'events_backtest_ready_rows': len(events_bt),
            'events_not_backtest_ready_rows': len(unmapped_rows),
            'source_evidence_rows': len(ev),
        },
        'mapping_status_counts_unique_company_rows': [dict(country=k[0], mapping_status=k[1], rows=v) for k, v in sorted(mapping_status_counts.items())],
        'event_status_counts': [dict(country=k[0], mapping_status=k[1], rows=v) for k, v in sorted(event_status_counts.items())],
        'mapped_unmapped_distribution_event_rows': [dict(country=k[0], backtest_ready=k[1], rows=v) for k, v in sorted(mapped_dist.items())],
        'coverage_by_country_product_action_backtest_ready': group_counts(audited_events, ['country','product','action','backtest_ready']),
        'same_company_name_multi_ticker_mapping_rows': same_name_multi_ticker,
        'one_ticker_multi_company_names_mapping_rows_top100': sorted(one_ticker_multi_name, key=lambda x: (-x['name_count'], x['country'], x['stock_code']))[:100],
        'ambiguity_counts': {
            'same_company_name_multi_ticker': len(same_name_multi_ticker),
            'one_ticker_multi_company_names': len(one_ticker_multi_name),
        },
        'usa_universe': {'ticker_count': len(us_universe), 'gate': 'ticker exists in us_dayTradePortfolio Close union'},
        'taiwan_universe': {'ticker_count': len(tw_universe), 'gate': 'ticker exists in FinLab/TWSE/TPEx reference universe'},
        'event_date_tradability': {
            'gate': 'effective_close_date is weekday; USA additionally inside at least one known local US Close data date window; Taiwan price matrix not loaded in R5 so reference-universe+weekday used',
            'non_tradable_effective_date_rows': sum(1 for r in audited_events if r['event_date_tradable_gate'] != 'true'),
        },
        'top_not_backtest_ready_reasons': [{'reason': k, 'rows': v} for k, v in reasons.most_common(30)],
        'limitations': [
            'No original files were deleted or overwritten except state/report append/update; exports are new files.',
            'USA price-date gate uses known parquet date windows from prior inventory, not per-ticker non-NaN availability because pandas/pyarrow are unavailable in this runtime.',
            'Taiwan gate confirms ticker in FinLab/TWSE/TPEx reference universe, but does not prove historical listing/trading status for delisted/merged names.',
        ],
    }
    CHECKS.write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding='utf-8')

    # Update cumulative state by merging Round 5 into existing json.
    state = {}
    if STATE_IN.exists():
        try:
            state = json.loads(STATE_IN.read_text(encoding='utf-8'))
        except Exception:
            state = {}
    state['task'] = checks['task']
    state['round'] = 5
    state['updated_at_taipei'] = checks['updated_at_taipei']
    state['round5_full_consistency_checks'] = checks
    STATE_IN.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')

    ready_by_country = Counter(r['country'] for r in events_bt)
    not_ready_by_country = Counter(r['country'] for r in unmapped_rows)
    report = f"""

## Round 5 — Full consistency checks & backtest-ready exports ({datetime.now().strftime('%Y-%m-%d %H:%M:%S %z')})

### Scope

- Full-table consistency audit over current verified mapping/events.
- Checks: unique company-name coverage, event-row coverage, same-name multi-ticker, one-ticker multi-name, USA ticker presence in `us_dayTradePortfolio` Close union, Taiwan ticker presence in FinLab/TWSE/TPEx reference universe, event-date tradability gate, mapped/unmapped distribution.
- Original raw/parser files were not deleted.

### Outputs

- Backtest-ready verified mapping: `{MAPPING_BT}`
- Event table with audit columns: `{EVENTS_AUDIT}`
- Backtest-ready event subset: `{EVENTS_BT}`
- Unmapped/manual-review/not-ready list: `{UNMAPPED}`
- Source evidence table: `{EVIDENCE}`
- Machine-readable checks: `{CHECKS}`

### Headline counts

- Unique company mapping rows: {len(mapping):,}; backtest-ready mapping rows: {len(mapping_bt):,}.
- Event rows: {len(events):,}; backtest-ready event rows: {len(events_bt):,}; not-ready rows: {len(unmapped_rows):,}.
- Backtest-ready events by country: USA {ready_by_country.get('USA',0):,}; Taiwan {ready_by_country.get('TAIWAN',0):,}.
- Not-ready events by country: USA {not_ready_by_country.get('USA',0):,}; Taiwan {not_ready_by_country.get('TAIWAN',0):,}.
- Same company-name mapped to multiple tickers: {len(same_name_multi_ticker):,} mapping rows/groups.
- One ticker mapped to multiple MSCI names: {len(one_ticker_multi_name):,} ticker groups (mostly legal-name variants / historical naming; see JSON top100).

### Backtest-ready gate used

`backtest_ready = verified mapping status + non-empty stock_code + ticker present in required local universe + effective_close_date tradable gate`.

- USA required universe: `research_state/us_price_close_universe_tickers.csv` from `us_dayTradePortfolio` Close/adj-close union.
- Taiwan required universe: `research_state/taiwan_reference_universe_tickers.csv` from FinLab/TWSE/TPEx reference universe.
- Event-date gate: effective close date must be a weekday; USA also must fall inside at least one known available US Close data date window. Taiwan historical per-ticker price matrix was not loaded in R5, so Taiwan date gate is weekday + code reference presence.

### Main not-ready reasons

"""
    for item in checks['top_not_backtest_ready_reasons'][:10]:
        report += f"- {item['rows']:,}: `{item['reason']}`\n"
    REPORT_IN.write_text(REPORT_IN.read_text(encoding='utf-8') + report, encoding='utf-8')

    print(json.dumps({
        'outputs': checks['outputs'],
        'row_counts': checks['row_counts'],
        'top_not_ready': checks['top_not_backtest_ready_reasons'][:10],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
