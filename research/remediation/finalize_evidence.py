"""Separate unreproduced historical claims and record protected-file/check evidence."""
from pathlib import Path
from copy import deepcopy
import json,hashlib,csv
import yaml
R=Path(__file__).resolve().parents[1];W=R.parent;O=R/'remediation'
def jw(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
S=json.loads((R/'sources.json').read_text(encoding='utf-8'));s=S['RU-ESC']
s.setdefault('historical_unreproduced_claim',dict(version=s['version_or_update_date'],locator=s['exact_locator'],fingerprint=deepcopy(s['document_fingerprint']),registry_read_part=s['registry_observation']['read_part']))
s['historical_unreproduced_claim'].setdefault('expert_stamp',s['registry_observation'].get('expert_stamp'))
s['historical_unreproduced_claim'].setdefault('document_name',s['registry_observation'].get('document_name'))
s['title']='Селектра (эсциталопрам), РУ ЛП-№(012351)-(РГ-RU), регистрация 05.11.2025; текущий полный оригинал недоступен'
s['registry_observation'].update(expert_stamp=None,document_name=None)
s['version_or_update_date']='Текущий полный оригинал недоступен; наблюдался РУ ЛП-№(012351)-(РГ-RU) 05.11.2025; прежние дата/штамп документа не воспроизведены'
s['document_fingerprint'].update(pages=None,sha256=None,verification='unavailable_current_original; former page/stamp claim retained separately as unreproduced history')
s['registry_observation']['read_part']='Текущая строка: название, РУ, дата регистрации и силы формы; полный документ/штамп/страницы независимо не получены. Историческое заявление вынесено отдельно.'
s['exact_locator']='Прежние заявленные разделы/страницы — historical_unreproduced_claim.locator; не текущий подтверждённый локатор'
s['dates'].update(download=None,download_attempt='2026-10-08')
jw(R/'sources.json',S)
for folder in ('rules','reference_rules','findings'):
    for p in (R/folder).glob('*.yaml'):
        r=yaml.safe_load(p.read_text(encoding='utf-8'));r['sources']=[S[x['source_id']] for x in r['sources']]
        p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
print('Current ESC provenance separated from unreproduced historical claims. Rebuild contracts and rerun checks before preservation/report capture.')
