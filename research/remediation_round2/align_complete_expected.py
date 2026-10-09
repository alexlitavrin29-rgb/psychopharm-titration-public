from pathlib import Path
from copy import deepcopy
from collections import defaultdict
import json,yaml
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2'
D=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'))
def fix_actions(x):
    if isinstance(x,dict):
        if x.get('source_ref')=='RU-AGO' and (x.get('input')=='mania_symptoms' or x.get('action','').startswith('discontinue_B')):x['source_locator']='§4.4 с.4'
        for v in x.values():fix_actions(v)
    elif isinstance(x,list):
        for v in x:fix_actions(v)
fix_actions(C);fix_actions(D)
for p in (R/'rules').glob('*.yaml'):
    r=yaml.safe_load(p.read_text(encoding='utf-8'));fix_actions(r)
    for i in r['inputs']:
        if i['input_id']=='mania_symptoms' and 'RU-AGO' in i['source_refs']:
            i['source_locator']=i['source_locator'].replace('RU-AGO §4.4 с.5','RU-AGO §4.4 с.4')
            for key in ['source_locators','source_locators_by_ref']:
                if isinstance(i.get(key),dict) and 'RU-AGO' in i[key]:i[key]['RU-AGO']='§4.4 с.4'
    p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
groups=defaultdict(list)
for c in D['cases']:groups[json.dumps([c['rule_id'],c['given'],c['external_context']],sort_keys=True,ensure_ascii=False)].append(c)
aligned=[]
for group in groups.values():
    if len(group)<2:continue
    merged={}
    for c in group:
        for k,v in c['expected'].items():
            if k in merged and merged[k]!=v:raise RuntimeError('Conflicting clinical output '+c['case_id']+'/'+k)
            merged[k]=deepcopy(v)
    if any(c['expected']!=merged for c in group):
        aligned.append([c['case_id'] for c in group])
        for c in group:c['expected']=deepcopy(merged)
(O/'full_scenarios.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'result_contracts.yaml').write_text(yaml.safe_dump(C,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'expected_alignment.json').write_text(json.dumps(dict(aligned_groups=aligned,method='Union of nonconflicting source-reviewed output facts for identical typed given/context; existing unequal values abort instead of arbitrary precedence',new_medical_values_created=False),ensure_ascii=False,indent=2),encoding='utf-8')
print('Complete same-input expectations aligned:',len(aligned))
