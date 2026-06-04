#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd

BASE = Path('/Users/johan/Documents/invest/msci_index_reviews')
STATE = BASE/'research_state/msci_ticker_audit_state.json'
MAP = BASE/'parsed/msci_us_taiwan_name_ticker_mapping_verified.csv'
EVENTS = BASE/'parsed/msci_us_taiwan_events_flat_verified.csv'
UNIVERSE = BASE/'research_state/us_price_close_universe_tickers.csv'
OUT = BASE/'research_state/msci_ticker_audit_round2_us_web_verification.csv'
REPORT = BASE/'reports/msci_ticker_audit_rounds.md'

rows = [
    dict(msci_name='GANNETT CO', country='USA', web_ticker='GCI', web_company_name='Gannett Co., Inc.', source_url='https://www.sec.gov/cgi-bin/browse-edgar?CIK=GCI&action=getcompany&owner=exclude', confidence=0.95, notes='SEC EDGAR identifies GCI issuer, formerly Gannett Co.; annual report excerpt shows common stock GCI on NYSE.'),
    dict(msci_name='BRIGHTCOVE', country='USA', web_ticker='BCOV', web_company_name='Brightcove Inc.', source_url='https://investor.brightcove.com/financial-information', confidence=0.98, notes='Company IR earnings release states Brightcove Inc. (Nasdaq: BCOV); 10-K excerpt confirms common stock BCOV on Nasdaq.'),
    dict(msci_name='COMMSCOPE HOLDING CO', country='USA', web_ticker='COMM', web_company_name='CommScope Holding Company, Inc.', source_url='https://commscopeholdingcompanyinc.gcs-web.com/news-releases/news-release-details/commscope-reports-fourth-quarter-and-full-year-2024-results', confidence=0.98, notes='Company IR/SEC annual report identify CommScope Holding Company, Inc. ticker COMM on Nasdaq.'),
    dict(msci_name='CUTERA', country='USA', web_ticker='CUTR', web_company_name='Cutera, Inc.', source_url='https://ir.cutera.com/news-releases/news-release-details/cuterar-announces-second-quarter-2024-financial-results', confidence=0.98, notes='Company IR release states Cutera, Inc. (Nasdaq: CUTR); later 2025 restructuring/delisting explains current-data absence risk.'),
    dict(msci_name='CHARLES RIVER LABS INTL', country='USA', web_ticker='CRL', web_company_name='Charles River Laboratories International, Inc.', source_url='https://ir.criver.com/shareholder-services/investor-faqs', confidence=0.99, notes='Company IR FAQ states it trades on NYSE under ticker symbol CRL.'),
    dict(msci_name='DICKS SPORTING GOODS', country='USA', web_ticker='DKS', web_company_name="DICK'S Sporting Goods, Inc.", source_url='https://investors.dicks.com/resources/investor-faqs/default.aspx', confidence=0.99, notes='Company IR FAQ lists Exchange & Ticker as NYSE: DKS.'),
    dict(msci_name='CONTAINER STORE GROUP', country='USA', web_ticker='TCS', web_company_name='The Container Store Group, Inc.', source_url='https://investor.containerstore.com/investor-kit/default.aspx', confidence=0.97, notes='Company IR page showed NYSE: TCS; 2024 10-K/IR materials corroborate.'),
    dict(msci_name='CHESAPEAKE ENERGY CORP', country='USA', web_ticker='CHK', web_company_name='Chesapeake Energy Corporation', source_url='https://www.sec.gov/Archives/edgar/data/895126/000110465924052466/tm244499d2_ars.pdf', confidence=0.98, notes='SEC annual report states common stock trading symbol CHK on Nasdaq; later merged into Expand Energy context should be handled historically.'),
    dict(msci_name='NUANCE COMMUNICATIONS', country='USA', web_ticker='NUAN', web_company_name='Nuance Communications, Inc.', source_url='https://www.sec.gov/Archives/edgar/data/1002517/000114036121017650/nt10023637x2_defm14a.htm', confidence=0.98, notes='SEC merger proxy says Nuance common stock listed on Nasdaq under symbol NUAN; acquired by Microsoft and delisted after close.'),
    dict(msci_name='ZIONS BANCORP', country='USA', web_ticker='ZION', web_company_name='Zions Bancorporation, N.A.', source_url='https://www.sec.gov/cgi-bin/browse-edgar?CIK=ZION&action=getcompany&owner=exclude', confidence=0.95, notes='SEC ticker lookup/issuer history supports ZION for Zions Bancorporation; MSCI abbreviation omits N.A.'),
    dict(msci_name='ALPHA NAT RESOURCES', country='USA', web_ticker='ANR', web_company_name='Alpha Natural Resources, Inc.', source_url='https://www.sec.gov/Archives/edgar/data/1301063/000130106315000048/anr8-k07x17x2015.htm', confidence=0.97, notes='SEC 8-K states NYSE commenced delisting proceedings for common stock symbol ANR, later OTC ANRZ.'),
    dict(msci_name='CHIMERIX', country='USA', web_ticker='CMRX', web_company_name='Chimerix, Inc.', source_url='https://ir.chimerix.com/?field_nir_sec_form_group_target_id%5B476%5D=476&field_nir_sec_date_filed_value=&items_per_page=50&promote=All&mobile=1&field_nir_event_start_date_value_2=now&sort_order=ASC&field_nir_event_start_date_value_1=-8%20hours&field_nir_sec_cik_target_id=&items_per_page_toggle=1&order=field_nir_sec_description&sort=asc&&&page=2%2C0%2C0', confidence=0.98, notes='Company IR FAQ states ticker CMRX, traded on Nasdaq Global Market; later Jazz acquisition noted separately.'),
    dict(msci_name='CELSIUS HLDGS', country='USA', web_ticker='CELH', web_company_name='Celsius Holdings, Inc.', source_url='https://ir.celsiusholdingsinc.com/overview/default.aspx', confidence=0.95, notes='Company IR overview confirms Celsius Holdings, Inc.; Nasdaq ticker CELH corroborated by current public listings/filings.'),
    dict(msci_name='FIRST HORIZON NATIONAL', country='USA', web_ticker='FHN', web_company_name='First Horizon National Corp. / First Horizon Corporation', source_url='https://www.nasdaq.com/press-release/first-horizon-announces-parent-company-name-change-2020-11-20', confidence=0.98, notes='Nasdaq-hosted company release states First Horizon National Corp. (NYSE: FHN) changed name to First Horizon Corporation; symbol remained FHN.'),
    dict(msci_name='ZOOMINFO TECH A', country='USA', web_ticker='ZI', web_company_name='ZoomInfo Technologies Inc.', source_url='https://www.sec.gov/Archives/edgar/data/1794515/000179451524000211/zi-20231231.htm', confidence=0.98, notes='SEC 2023 10-K/A states common stock trading symbol ZI on Nasdaq; company later changed ticker to GTM in 2025/2026, so use historical ZI for MSCI events through 2023.'),
    dict(msci_name='CYMABAY THERAPEUTICS', country='USA', web_ticker='CBAY', web_company_name='CymaBay Therapeutics, Inc.', source_url='https://www.sec.gov/Archives/edgar/data/1042074/000119312524031185/d791540dex991.htm', confidence=0.98, notes='SEC exhibit/joint release states CymaBay Therapeutics, Inc. (Nasdaq: CBAY); acquisition by Gilead announced 2024.'),
    dict(msci_name='CONTINENTAL RESOURCES', country='USA', web_ticker='CLR', web_company_name='Continental Resources, Inc.', source_url='https://www.sec.gov/Archives/edgar/data/732834/000095017023018882/R18.htm', confidence=0.94, notes='SEC filing documents 2022 take-private and NYSE delisting after transaction; historical ticker CLR supported by filing accession/taxonomy and issuer convention.'),
    dict(msci_name='COUPA SOFTWARE', country='USA', web_ticker='COUP', web_company_name='Coupa Software Incorporated', source_url='https://www.sec.gov/Archives/edgar/data/1385867/000119312523054081/d455192d8k.htm', confidence=0.99, notes='SEC 8-K lists common stock trading symbol COUP on Nasdaq and notes delisting after Thoma Bravo acquisition.'),
    dict(msci_name='SIGNATURE BANK', country='USA', web_ticker='SBNY', web_company_name='Signature Bank', source_url='https://www.nasdaq.com/press-release/signature-bank-releases-2022-form-10-k-2023-03-02', confidence=0.96, notes='Nasdaq-hosted company release states Signature Bank (Nasdaq: SBNY); FDIC source confirms March 2023 closure/receivership.'),
    dict(msci_name='COBALT INTERNATIONAL', country='USA', web_ticker='CIE', web_company_name='Cobalt International Energy, Inc.', source_url='https://www.sec.gov/Archives/edgar/data/1471261/000156459018004275/cie-10k_20171231.htm', confidence=0.55, notes='Source confirms Cobalt International Energy, Inc. common stock on NYSE, but extracted source did not explicitly show trading symbol; mark needs_manual_review rather than apply.'),
]

tz = timezone(timedelta(hours=8))
now = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %z')

uni = set(pd.read_csv(UNIVERSE)['ticker'].astype(str))
events = pd.read_csv(EVENTS)
mapdf = pd.read_csv(MAP)

audit = pd.DataFrame(rows)
# Context from events
ctx = events[(events['country']=='USA') & (events['mapping_status']=='needs_review')].copy()
agg = ctx.groupby('company_name').agg(
    event_rows=('company_name','size'),
    first_issue_date=('issue_date','min'),
    last_issue_date=('issue_date','max'),
    actions=('action', lambda s: ','.join(sorted(set(s.astype(str))))),
    products=('product', lambda s: ','.join(sorted(set(s.astype(str)))))
).reset_index()
audit = audit.merge(agg, left_on='msci_name', right_on='company_name', how='left').drop(columns=['company_name'])
audit['action/history context'] = audit.apply(lambda r: f"{int(r.event_rows) if pd.notna(r.event_rows) else 0} MSCI event rows; {r.products}; {r.actions}; issue {r.first_issue_date}..{r.last_issue_date}", axis=1)
audit['db_ticker_match'] = audit['web_ticker'].isin(uni)
audit['audit_status'] = audit['confidence'].apply(lambda x: 'verified_us_web_high_confidence' if x >= 0.9 else 'needs_manual_review')
cols = ['msci_name','country','action/history context','web_ticker','web_company_name','db_ticker_match','source_url','confidence','notes','audit_status']
audit[cols].to_csv(OUT, index=False)

# Apply only high-confidence rows to mapping/event CSVs.
verified = audit[audit['audit_status']=='verified_us_web_high_confidence']
verify_map = {r.msci_name: r for r in verified.itertuples(index=False)}
changed_names=[]
for name, r in verify_map.items():
    mask = (mapdf['country']=='USA') & (mapdf['company_name']==name) & (mapdf['mapping_status'].isin(['needs_review','verified_us_web_high_confidence']))
    if mask.any():
        changed_names.append(name)
        mapdf.loc[mask, 'stock_code'] = r.web_ticker
        mapdf.loc[mask, 'matched_name'] = r.web_company_name
        mapdf.loc[mask, 'mapping_source'] = 'web_verified_round2:' + r.source_url
        mapdf.loc[mask, 'mapping_score'] = r.confidence
        mapdf.loc[mask, 'mapping_status'] = 'verified_us_web_high_confidence'
    emask = (events['country']=='USA') & (events['company_name']==name) & (events['mapping_status'].isin(['needs_review','verified_us_web_high_confidence']))
    if emask.any():
        events.loc[emask, 'stock_code'] = r.web_ticker
        events.loc[emask, 'matched_name'] = r.web_company_name
        events.loc[emask, 'mapping_source'] = 'web_verified_round2:' + r.source_url
        events.loc[emask, 'mapping_score'] = r.confidence
        events.loc[emask, 'mapping_status'] = 'verified_us_web_high_confidence'

mapdf.to_csv(MAP, index=False)
events.to_csv(EVENTS, index=False)

# Update state with round2 details and current counts.
state = json.loads(STATE.read_text())
state['task'] = 'MSCI ticker mapping audit R2 — US high-confidence web verification'
state['round'] = 2
state['updated_at_taipei'] = datetime.now(tz).isoformat(timespec='seconds')
state['round2_us_web_verification'] = {
    'output_csv': str(OUT),
    'audited_unique_names': int(len(audit)),
    'high_confidence_verified_names': int((audit['audit_status']=='verified_us_web_high_confidence').sum()),
    'needs_manual_review_names': int((audit['audit_status']=='needs_manual_review').sum()),
    'verified_event_rows_updated': int(events[(events['country']=='USA') & (events['mapping_status']=='verified_us_web_high_confidence')]['company_name'].isin(changed_names).sum()),
    'db_ticker_matches_among_verified': int(verified['db_ticker_match'].sum()),
    'db_ticker_mismatches_among_verified': verified.loc[~verified['db_ticker_match'], ['msci_name','web_ticker']].to_dict('records'),
    'manual_review': audit.loc[audit['audit_status']=='needs_manual_review', ['msci_name','web_ticker','notes','source_url']].to_dict('records'),
    'method': 'web_search/web_fetch-style source verification from company IR, SEC, Nasdaq; updated only >=0.90 confidence names; database match checked against us_price_close_universe_tickers.csv',
}
state['mapping_status_counts_unique_names_after_round2'] = mapdf.groupby(['country','mapping_status']).size().reset_index(name='unique_name_rows').to_dict('records')
state['mapping_status_counts_event_rows_after_round2'] = events.groupby(['country','mapping_status']).size().reset_index(name='event_rows').to_dict('records')
STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False))

# Append report.
counts_unique = mapdf.groupby(['country','mapping_status']).size().reset_index(name='unique_name_rows')
counts_events = events.groupby(['country','mapping_status']).size().reset_index(name='event_rows')
report = f'''

## Round 2 — USA high-confidence web verification（{now} Asia/Taipei）

### 本輪範圍

- 讀取 state：`research_state/msci_ticker_audit_state.json`
- 針對 USA `needs_review` 中事件次數較高、且可由公司 IR / SEC / Nasdaq 等來源引用者做人工式 web 查證。
- 輸出逐筆查證 CSV：`research_state/msci_ticker_audit_round2_us_web_verification.csv`
- 只把 `confidence >= 0.90` 的公司寫回 `parsed/msci_us_taiwan_name_ticker_mapping_verified.csv` 與 `parsed/msci_us_taiwan_events_flat_verified.csv`；低信心列保留為 `needs_manual_review`。

### Coverage

- 本輪 audited unique USA names：{len(audit)}
- high-confidence verified：{(audit['audit_status']=='verified_us_web_high_confidence').sum()} unique names
- needs_manual_review：{(audit['audit_status']=='needs_manual_review').sum()} unique names
- 更新 event rows：{int(events[(events['country']=='USA') & (events['mapping_status']=='verified_us_web_high_confidence')]['company_name'].isin(changed_names).sum())}
- high-confidence verified 中，web ticker 在 `us_dayTradePortfolio` Close universe 找到：{int(verified['db_ticker_match'].sum())}/{len(verified)}

### 查證結果（摘要）

| MSCI name | web ticker | DB match | confidence | source |
| --- | --- | --- | --- | --- |
'''
for r in audit.itertuples(index=False):
    report += f"| {r.msci_name} | {r.web_ticker} | {bool(r.db_ticker_match)} | {r.confidence:.2f} | {r.source_url} |\n"
report += '''
### 疑點 / 下一輪注意

1. `CUTERA` → `CUTR` 來源高信心，但不在本機 Close union；疑似資料源缺口或 delisting/格式問題，需用 backtest/raw vendor symbol history 追查。
2. `SIGNATURE BANK` → `SBNY` 來源高信心，但本機 universe 僅見 `SBN/SBNA/SBNK1/SBNYW` 等相近代號，需查資料庫 vendor 是否改用 receivership/OTC 或舊代碼映射。
3. `COBALT INTERNATIONAL` → `CIE` 目前來源確認公司與 NYSE common stock，但未抓到明確 trading symbol 文字；保留 `needs_manual_review`，未寫回主 mapping。
4. `ZOOMINFO TECH A` 需採歷史 ticker `ZI`；公司 IR 目前顯示 `GTM`，不可用 current ticker 覆蓋舊 MSCI 事件。
5. `CHESAPEAKE ENERGY CORP`、`NUANCE`、`COUPA`、`CYMABAY`、`CONTINENTAL RESOURCES` 都有併購/下市/更名脈絡，回測時必須按事件日期使用當時 ticker，不可只用 current snapshot。

### Round 2 後 mapping 狀態（unique name rows）

'''
def md_table(df):
    headers = list(df.columns)
    out = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---']*len(headers)) + ' |']
    for _, rr in df.iterrows():
        out.append('| ' + ' | '.join(str(rr[h]) for h in headers) + ' |')
    return '\n'.join(out)

report += md_table(counts_unique)
report += '\n\n### Round 2 後 events 狀態（event rows）\n\n'
report += md_table(counts_events)
report += '\n'
REPORT.write_text(REPORT.read_text() + report)
print(OUT)
print('verified_names', len(verified), 'changed_names', len(changed_names))
print('db_matches', int(verified['db_ticker_match'].sum()), '/', len(verified))
