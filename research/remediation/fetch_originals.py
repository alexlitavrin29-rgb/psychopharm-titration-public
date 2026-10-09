"""Read-only public requests; no CAPTCHA, credentials, or alternate endpoints."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, hashlib, requests
R=Path(__file__).resolve().parents[1]
O=R/'remediation'
S=json.loads((R/'sources.json').read_text(encoding='utf-8'))
(O/'retrieved').mkdir(exist_ok=True)
ids=[k for k in S if k.startswith('RU-') and k not in {'RU-ESC-2025-JAN','RU-SER-2023','RU-PREG-RICHTER-ARCHIVE','RU-FLUOX-ARCHIVE','RU-CLOMI-IV-ARCHIVE'}]
def fetch(sid):
    s=S[sid]; row={'source_id':sid,'url':s['url'],'accessed_on':'2026-10-08'}
    try:
        r=requests.get(s['url'],timeout=15)
        row.update(http_status=r.status_code,final_url=r.url,content_type=r.headers.get('Content-Type'))
        is_doc=r.content.startswith(b'%PDF') or (sid=='RU-CITAL-LV' and r.content.startswith(b'PK'))
        if r.status_code==200 and (is_doc or sid.startswith('RU-VENLA')):
            suffix='.pdf' if r.content.startswith(b'%PDF') else '.docx' if sid=='RU-CITAL-LV' else '.html'
            p=O/'retrieved'/f'{sid}{suffix}';p.write_bytes(r.content)
            row.update(local_file=p.relative_to(R).as_posix(),sha256=hashlib.sha256(r.content).hexdigest(),same_bytes=hashlib.sha256(r.content).hexdigest()==s.get('document_fingerprint',{}).get('sha256'))
        else: row['access_status']='original_not_obtained; no_restriction_bypass'
    except requests.RequestException as e: row.update(access_status='request_failed',error=str(e))
    return row
with ThreadPoolExecutor(max_workers=4) as pool: rows=list(pool.map(fetch,ids))
(O/'fetch_results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
for r in rows: print(r['source_id'],r.get('http_status',r.get('access_status')),r.get('same_bytes','no_original'))
