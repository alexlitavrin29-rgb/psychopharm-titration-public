from pathlib import Path
import csv, json
import fitz, yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
sources = json.loads((ROOT / 'sources.json').read_text(encoding='utf-8'))
rules = [yaml.safe_load(p.read_text(encoding='utf-8')) for p in sorted((ROOT / 'rules').glob('*.yaml'))]
(OUT / 'source_texts').mkdir(exist_ok=True)
used = sorted({s['source_id'] for r in rules for s in r['sources']})
inventory = []
for sid in used:
    s = sources[sid]
    path = ROOT / s['local_file'] if s.get('local_file') else None
    pages = None
    if path and path.suffix.lower() == '.pdf':
        with fitz.open(path) as doc:
            pages = len(doc)
            content = '\n'.join(f'\n=== PHYSICAL PAGE {n+1} ===\n{page.get_text()}' for n, page in enumerate(doc))
    elif path:
        content = path.read_text(encoding='utf-8-sig')
        if path.suffix.lower() == '.html':
            content = BeautifulSoup(content, 'html.parser').get_text('\n', strip=True)
    else:
        content = 'NO LOCAL ORIGINAL: review actual source access before making medical claims.'
    (OUT / 'source_texts' / f'{sid}.txt').write_text(content, encoding='utf-8')
    inventory.append(dict(source_id=sid, local_file=s.get('local_file'), pages=pages, title=s.get('title'), url=s.get('url'), rules=[r['rule_id'] for r in rules if sid in [x['source_id'] for x in r['sources']]]))
(OUT / 'source_inventory_initial.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding='utf-8')
fields=[]
for r in rules:
    for i in r['inputs']:
        fields.append(dict(rule_id=r['rule_id'],input_id=i['input_id'],question=i.get('question'),type=i.get('data_type'),role=i.get('input_role'),required=i.get('required_for_individual_result'),show=json.dumps(i.get('show_when'),ensure_ascii=False),required_when=json.dumps(i.get('required_when'),ensure_ascii=False),source_locator=i.get('source_locator'),source_ref=json.dumps(i.get('source_refs',i.get('source_ref')),ensure_ascii=False)))
with (OUT/'input_inventory_initial.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(fields[0]));writer.writeheader();writer.writerows(fields)
print(json.dumps({'sources':[(x['source_id'],x['pages']) for x in inventory],'cards':len(rules),'inputs':len(fields)},ensure_ascii=False))
