from pathlib import Path
import json,hashlib,concurrent.futures
import requests
root=Path(__file__).resolve().parents[1]; out=Path(__file__).resolve().parent
(out/'retrieved').mkdir(exist_ok=True)
ss=json.loads((root/'sources.json').read_text(encoding='utf-8'))
def get(item):
 sid,s=item
 if sid=='RU-ESC': return {'source_id':sid,'status':'not_retried_token_access_failed_web','reason':'Реестр требует CAPTCHA; не обходить'}
 try:
  r=requests.get(s['url'],timeout=35)
  ext='.pdf' if r.content.startswith(b'%PDF') else '.html'
  p=out/'retrieved'/(sid+ext);p.write_bytes(r.content)
  return {'source_id':sid,'url':s['url'],'final_url':r.url,'status':r.status_code,'content_type':r.headers.get('Content-Type'),'bytes':len(r.content),'sha256':hashlib.sha256(r.content).hexdigest(),'stored':str(p.relative_to(out)),'equals_research_hash':hashlib.sha256(r.content).hexdigest()==s.get('document_fingerprint',{}).get('sha256')}
 except Exception as e:return {'source_id':sid,'url':s['url'],'status':'error','error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 rows=list(ex.map(get,ss.items()))
(out/'external_fetch_results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
for r in rows:print(r['source_id'],r['status'],r.get('bytes'),r.get('equals_research_hash'))
