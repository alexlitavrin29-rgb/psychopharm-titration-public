"""Repair metadata migration while preserving intentional unknown/omitted negative fixtures."""
from pathlib import Path
from copy import deepcopy
import json,yaml
O=Path(__file__).resolve().parent;R=O.parent
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));old={c['case_id']:c for c in json.loads((R/'remediation_round2/full_scenarios.json').read_text(encoding='utf-8'))['cases']}
rs={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')};S=json.loads((O/'sources.json').read_text(encoding='utf-8'))
unknown=(None,'unknown','not_assessed','неизвестно','не исследовано')
repairs=[]
for c in F['cases']:
    g=c['given'];rid=c['rule_id'];ins={i['input_id']:i for i in rs[rid]['inputs']};e=c['expected']
    if c['case_id'] in old:
        og=old[c['case_id']]['given']
        for k,v in g.items():
            if isinstance(v,dict) and k in og and isinstance(og[k],dict) and ins[k]['data_type']=='structured_form':
                if 'source_version' not in og[k]:v.pop('source_version',None)
                elif og[k]['source_version'] in unknown:v['source_version']=og[k]['source_version']
                if 'registration_number' not in og[k]:v.pop('registration_number',None)
                if rid=='phen-taper-limit' and og[k].get('registration_number') is None and 'registration_number' in og[k]:v['registration_number']=S['RU-PHEN']['doi_or_registry_id']
    if e['result_type'] in {'exact','selected_source_example'}:
        e['unassessed_context']=sorted(i['input_id'] for i in ins.values() if i['requirement_predicate']['kind'] in {'reported_context','ongoing_selected_drug'} and (i['input_id'] not in g or not isinstance(g[i['input_id']],(dict,list)) and g[i['input_id']] in unknown))
        e['confirmed_negatives']=sorted(k for k,v in g.items() if v is False and not(ins[k]['requirement_predicate']['kind']=='ongoing_selected_drug' and c['external_context'].get('treatment_phase')!='ongoing'))
    if rid.startswith('preg-') and g.get('reproductive_population') is True and g.get('effective_contraception') is False:
        e['source_condition']=dict(input='effective_contraception',source_ref='RU-PREG',source_locator='§4.6 с.12')
    # Parent expected metadata must be recomputed from actual facts, not copied from another supplied state.
    if 'confirmed_negatives' in e:e['confirmed_negatives']=sorted(k for k,v in g.items() if v is False and not(ins[k]['requirement_predicate']['kind']=='ongoing_selected_drug' and c['external_context'].get('treatment_phase')!='ongoing'))
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
groups={}
for c in F['cases']:groups.setdefault(json.dumps([c['rule_id'],c['given'],c['external_context']],sort_keys=True,ensure_ascii=False),[]).append(c)
conflicts=[]
for cs in groups.values():
    if any(c['expected']!=cs[0]['expected'] for c in cs[1:]):
        keys=set().union(*(c['expected'] for c in cs))
        conflicts.append(dict(ids=[c['case_id'] for c in cs],different_fields=[k for k in keys if any(c['expected'].get(k)!=cs[0]['expected'].get(k) for c in cs[1:])]))
(O/'remaining_scenario_conflicts.json').write_text(json.dumps(conflicts,ensure_ascii=False,indent=2),encoding='utf-8')
print('Remaining conflicts:',conflicts)
