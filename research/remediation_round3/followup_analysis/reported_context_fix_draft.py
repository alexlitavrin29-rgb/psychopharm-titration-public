"""Prepared correction; apply only after preserving current independent completion."""
from pathlib import Path
from copy import deepcopy
import json,yaml
O=Path(__file__).resolve().parent.parent
assert not (O/'reported_context_repairs.json').exists(),'One-use correction'
p=O/'build_graphs.py';t=p.read_text(encoding='utf-8')
t=t.replace("if k in {'reported_current_event','reported_source_information'}:return i['input_id'] in g","if k in {'reported_context','reported_current_event','reported_source_information'}:return i['input_id'] in g")
a="or '--audit-final-' in c['case_id'])"
assert a in t
t=t.replace(a,"or '--audit-final-' in c['case_id'] or c['expected'].get('reason_ids'))")
p.write_text(t,encoding='utf-8')
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'))['rules'];rs={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')}
new=[]
semantics=[]
for rid,r in rs.items():
    for i in r['inputs']:
        if i['input_id']!='current_dose' or i['requirement_predicate']['kind']!='reported_context':continue
        i['fact_semantics']='reported_course_dose_without_current_use_confirmation'
        i['question_ru']='Какова сообщённая исходная/последняя суточная доза курса (мг/сут) для контекста риска отмены? Она не подтверждает фазу текущего приёма.'
        i['fact_origin']='Explicitly reported initial/last daily course dose for source withdrawal context; no assertion of ongoing use. Current-treatment source action needs a separately supplied counted treatment phase.'
        semantics.append(dict(rule_id=rid,input_id=i['input_id'],fact_semantics=i['fact_semantics']))
    (O/'rules'/(rid+'.yaml')).write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
for c in F['cases']:
    if not c['branch_id'] or c['expected']['result_type'] not in {'exact','selected_source_example'}:continue
    optional={i['input_id'] for i in rs[c['rule_id']]['inputs'] if i['requirement_predicate']['kind'] in {'reported_context','reported_current_event','reported_source_information'}}
    if not optional.intersection(c['given']):continue
    n=deepcopy(c);n['case_id']=c['case_id']+'--audit-final-minimal-routine';n['given']={k:v for k,v in n['given'].items() if k not in optional}
    e=n['expected'];e['unassessed_context']=sorted(set(e.get('unassessed_context',[]))|optional)
    e['confirmed_negatives']=[k for k in e.get('confirmed_negatives',[]) if k in n['given'] and n['given'][k] is False]
    e['clinical_clearance']=False
    n['fixture_scope']='Complete required input set for the same individual numerical branch; optional monitoring context explicitly not provided, never normal. Full reported-context cases remain separately counted.'
    new.append(n)
F['cases']+=new
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
schema=yaml.safe_load((O/'input_contracts.yaml').read_text(encoding='utf-8'))
schema['requirement_predicates']['reported_context']='Optional explicitly supplied source context: consumed and counted when present. Positive/negative/unknown supplied values are never free. Missing stays not_assessed and does not establish a negative or clinical clearance. If used in an expected reason, it must be included in the projected input.'
(O/'input_contracts.yaml').write_text(yaml.safe_dump(schema,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
policy=yaml.safe_load((O/'necessity_policy.yaml').read_text(encoding='utf-8'));policy['definitions']['reported_context']=schema['requirement_predicates']['reported_context']
(O/'necessity_policy.yaml').write_text(yaml.safe_dump(policy,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'reported_context_repairs.json').write_text(json.dumps(dict(new_minimal_numeric_cases=len(new),qualitative_course_dose_semantics=semantics,scope='All optional supplied context is consumed/counted; context-sensitive full positive reasons included in selected paths; no medical dose/condition removed or altered, no long ordinary case relabeled complex'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared-context transmission aligned; new complete minimal routine cases',len(new))
