from pathlib import Path
from copy import deepcopy
import json,yaml
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2'
D=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'));schema=yaml.safe_load((O/'input_contracts.yaml').read_text(encoding='utf-8'))
schema['external_context']['target_treatment_phase']=dict(type='enum: not_started | ongoing | unknown | not_assessed',origin='Explicit clinician-selected target treatment stage in current calculation; never inferred from global treatment_phase or from A dose',question_policy='If not already supplied and needed to distinguish B cessation from B start prohibition, request/count as one separate complex-branch fact; no permanent patient history')
for rid,con in C['rules'].items():
    if rid.startswith('switch') and any(g['source_ref']=='RU-AGO' for g in con['source_gates']):
        for cond in con.get('ongoing_stop_conditions',[]):cond['target_treatment_phase']='ongoing'
for c in D['cases']:
    rid=c['rule_id']
    if not rid.startswith('switch'):continue
    e=c['expected'];g=c['given'];ctx=c['external_context']
    # Synthetic target-stop cases explicitly represent an ongoing target treatment.
    ctx['target_treatment_phase']='ongoing' if e.get('stop_medication')=='RU-AGO' and e['result_type']=='source_stop_action' else 'not_started'
    if rid in ['switch-ser-ago','switch-esc-ago'] and g.get('mania_symptoms') is True:
        a='RU-SER' if rid=='switch-ser-ago' else 'RU-ESC'
        e.update(stop_medication=a,target_start_allowed=False,automatic_next_stage=False,
            source_actions=[dict(action='discontinue_current_A',source_ref=a,source_locator='§4.4 с.4'),dict(action='discontinue_B_only_if_already_administered_otherwise_do_not_start',source_ref='RU-AGO',source_locator='§4.4 с.5',condition='target_treatment_phase=ongoing for stop; otherwise no automatic start')])
        e['stop_medications']=[a,'RU-AGO'] if ctx['target_treatment_phase']=='ongoing' else [a]
        e['source_condition']=C['rules'][rid]['urgent_stop_predicates'][0]
(O/'input_contracts.yaml').write_text(yaml.safe_dump(schema,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'result_contracts.yaml').write_text(yaml.safe_dump(C,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(O/'full_scenarios.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
print('A/B treatment phases explicit; current mania stop A and conditional B source actions aligned.')
