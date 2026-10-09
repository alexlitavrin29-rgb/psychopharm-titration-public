"""Repair only the already isolated draft, preserving the frozen candidate."""
from pathlib import Path
import json,yaml
T=Path(__file__).resolve().parent/'staging_recheck'
for p in (T/'rules').glob('*.yaml'):
    r=yaml.safe_load(p.read_text(encoding='utf-8'));changed=False
    for i in r['inputs']:
        if 'RU-PAROX' in i['source_refs']:
            for k in ['why_needed','necessity_reason']:
                t=i[k].replace('§4.3 с.17–18','§4.3 с.4–5').replace('§4.3 с.17','§4.3 с.4');changed|=t!=i[k];i[k]=t
    if changed:p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
p=T/'full_scenarios.json';f=json.loads(p.read_text(encoding='utf-8'))
for c in f['cases']:
    if 'duplicate-duloxetine-selected_product_only' in c['case_id'] and c['rule_id'] in {'dulox-depression-start','dulox-gad-start'}:c['external_context']['treatment_phase']='ongoing'
p.write_text(json.dumps(f,ensure_ascii=False,indent=2),encoding='utf-8')
p=T/'build_graphs.py';t=p.read_text(encoding='utf-8').replace("ctx.get('treatment_phase')=='ongoing':init.append('ongoing_selected_drug_phase')","ctx.get('treatment_phase') in {'ongoing','unknown'}:init.append('selected_drug_treatment_phase')")
p.write_text(t,encoding='utf-8')
print('Isolated draft corrections applied; frozen candidate untouched.')
