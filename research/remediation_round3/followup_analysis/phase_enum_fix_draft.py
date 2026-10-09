"""Prepared minimal correction; run only after the current frozen audit finishes."""
from pathlib import Path
import json,yaml

O=Path(__file__).resolve().parent.parent
assert not (O/'phase_enum_repair.json').exists(), 'One-use schema correction'
p=O/'input_contracts.yaml';s=yaml.safe_load(p.read_text(encoding='utf-8'))
old=s['external_context']['treatment_phase'].copy()
s['external_context']['treatment_phase']['allowed_values']=['selected_mode','not_started','ongoing','unknown']
s['external_context']['treatment_phase']['origin']='Explicit stage of selected/A product. start + selected_mode means first administration; not_started is the explicit same state; ongoing and explicitly unknown are separate supplied facts counted for start paths. unknown never confirms non-use or ongoing use and needs clarification for an ongoing source action. Never infer B phase from A.'
p.write_text(yaml.safe_dump(s,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
p=O/'verify_contracts.py';t=p.read_text(encoding='utf-8')
a="""        if 'target_treatment_phase' in c['external_context']:
            decl=d['schema']['external_context']['target_treatment_phase']
            ck(decl.get('data_type')=='enum' and 'unit' in decl and c['external_context']['target_treatment_phase'] in decl.get('allowed_values',[]),'target phase declaration/value not typed: '+c['case_id'])"""
b="""        for phase_key in ['treatment_phase','target_treatment_phase']:
            if phase_key in c['external_context']:
                decl=d['schema']['external_context'][phase_key]
                ck(decl.get('data_type')=='enum' and 'unit' in decl and c['external_context'][phase_key] in decl.get('allowed_values',[]),'phase declaration/value not typed: '+phase_key+'/'+c['case_id'])"""
assert a in t,'Current verifier context changed; inspect before applying'
p.write_text(t.replace(a,b),encoding='utf-8')
(O/'phase_enum_repair.json').write_text(json.dumps(dict(old=old,new=s['external_context']['treatment_phase'],scope='Schema/validator consistency for actual existing prepared phase states; no medical dose/action/fixture/count change'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Explicit A phase enum and A/B generic typing aligned; prepared medical results unchanged')
