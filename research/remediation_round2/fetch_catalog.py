from pathlib import Path
import json,hashlib,requests
R=Path(__file__).resolve().parents[1]
old=json.loads((R/'minzdrav_catalog_snapshot.json').read_text(encoding='utf-8'))
resp=requests.post(old['endpoint'],json=old['query'],timeout=25)
resp.raise_for_status();raw=resp.content;data=resp.json()
(R/'remediation_round2/current_minzdrav_catalog.json').write_bytes(raw)
rows=[{k:r.get(k) for k in ['CodeVersion','Name','PublishDateStr','ApplyStatusCalculated','AgeCategory','Mkbs']} for r in data['Data'] if r['CodeVersion'] in {'457_3','456_3','455_3','301_3'}]
report=dict(accessed_on='2026-10-08',endpoint=old['endpoint'],method='POST read-only catalog query',query=old['query'],sha256=hashlib.sha256(raw).hexdigest(),selected_entries=rows,limitation='Catalog status verifies guideline listing, not latest registration revisions of medicinal product labels')
(R/'remediation_round2/catalog_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print([(r['CodeVersion'],r['ApplyStatusCalculated']) for r in rows])
