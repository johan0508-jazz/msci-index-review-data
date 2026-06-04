#!/usr/bin/env python3
"""Retry downloader for additional MSCI public-list index review PDFs.
Keeps request count modest: quarterly months only, known candidate families only.
"""
from pathlib import Path
import urllib.request, urllib.error, json, time, subprocess, collections
from datetime import datetime

base=Path.home()/'Documents/invest/msci_index_reviews'
pdf_dir=base/'pdf'; manifest_dir=base/'manifest'; manifest_dir.mkdir(parents=True, exist_ok=True)
months=['Feb','May','Aug','Nov']; years=range(2006,2027)
families=[
 ('china_all_shares_std','stdindex','MSCI_{m}{yy}_ChinaAllShares_PublicList.pdf'),
 ('china_a','stdindex','MSCI_{m}{yy}_ChinaAPublicList_EN.pdf'),
 ('china_a_intl','stdindex','MSCI_{m}{yy}_ChinaAIntl_PublicList.pdf'),
 ('micro','stdindex','MSCI_{m}{yy}_MicroPublicList.pdf'),
 ('overseas_china','stdindex','MSCI_{m}{yy}_OVCPublicList.pdf'),
 ('frontier_markets','stdindex','MSCI_{m}{yy}_FM_PublicList.pdf'),
]
headers={
 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36',
 'Accept':'application/pdf,*/*',
 'Referer':'https://www.msci.com/index-review',
}

def pages(path):
    try:
        out=subprocess.check_output(['mdls','-raw','-name','kMDItemNumberOfPages',str(path)], text=True, stderr=subprocess.DEVNULL, timeout=5).strip()
        return None if not out or out=='(null)' else int(out)
    except Exception:
        return None

def readable(path):
    try:
        data=path.read_bytes()
        return data[:4]==b'%PDF' and (pages(path) or len(data)>1000)
    except Exception:
        return False

records=[]
for kind,urlfolder,tmpl in families:
    outdir=pdf_dir/kind; outdir.mkdir(parents=True, exist_ok=True)
    for y in years:
        yy=f'{y%100:02d}'
        for m in months:
            name=tmpl.format(m=m, yy=yy)
            url=f'https://app2.msci.com/eqb/gimi/{urlfolder}/{name}'
            path=outdir/name
            rec={'kind':kind,'url':url,'file':str(path),'checked_at':datetime.now().isoformat(timespec='seconds')}
            if path.exists() and path.stat().st_size>0:
                rec.update(status='exists', http_status=200, bytes=path.stat().st_size, readable=readable(path), pages_mdls=pages(path))
                records.append(rec); continue
            try:
                req=urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=25) as r:
                    status=r.status; ctype=r.headers.get('content-type',''); data=r.read()
                if status==200 and data[:4]==b'%PDF':
                    path.write_bytes(data)
                    rec.update(status='downloaded', http_status=status, content_type=ctype, bytes=len(data), readable=readable(path), pages_mdls=pages(path))
                    print('DL', kind, name, len(data), flush=True)
                else:
                    rec.update(status='not_pdf', http_status=status, content_type=ctype, bytes=len(data), error='not PDF response')
            except urllib.error.HTTPError as e:
                rec.update(status='missing_or_blocked', http_status=e.code, error=str(e))
            except Exception as e:
                rec.update(status='error', http_status=None, error=repr(e))
            records.append(rec)
            time.sleep(0.5)

summary=collections.defaultdict(lambda:{'downloaded_or_exists':0,'readable':0,'min_year':None,'max_year':None})
for p in sorted(pdf_dir.glob('*/*.pdf')):
    kind=p.parent.name
    import re
    mt=re.search(r'MSCI_[A-Z][a-z]{2}(\d{2})_', p.name)
    year=2000+int(mt.group(1)) if mt else None
    s=summary[kind]; s['downloaded_or_exists']+=1
    if readable(p): s['readable']+=1
    if year:
        s['min_year']=year if s['min_year'] is None else min(s['min_year'],year)
        s['max_year']=year if s['max_year'] is None else max(s['max_year'],year)
manifest={'generated_at':datetime.now().isoformat(timespec='seconds'),'records':records,'summary':dict(summary)}
(manifest_dir/'other_products_retry_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
print(json.dumps(manifest['summary'], ensure_ascii=False, indent=2))
