"""Material prepared cases missing from the restored ESC results; no calculator execution."""
from pathlib import Path
from copy import deepcopy
import json,yaml
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2'
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'));D=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))
schema=yaml.safe_load((O/'input_contracts.yaml').read_text(encoding='utf-8'))
def add(base,name,g,e):
    c=deepcopy(base);c.update(case_id=base['rule_id']+'--round2-'+name,branch_id=None,given=g,expected=e)
    if e['result_type']=='source_stop_action':c['external_context']['treatment_phase']='ongoing'
    D['cases'].append(c)
def empty(typ,**extra):return dict(result_type=typ,total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],missing_fields=[],unconditional_future_stages=False,clinical_clearance=False,**extra)
for p in sorted((R/'rules').glob('esc-*.yaml')):
    r=yaml.safe_load(p.read_text(encoding='utf-8'));rid=r['rule_id'];con=C['rules'][rid]
    base=next(c for c in D['cases'] if c['rule_id']==rid and '--current-branch-' in c['case_id'])
    for i in r['inputs']:
        if i['data_type'] not in ['structured_form','structured_renal','source_hepatic_category'] or i['input_id'] not in con['required_inputs']:continue
        k=i['input_id']
        for field in schema['structures'][i['data_type']]['fields']:
            for state in ['omitted','unknown','not_assessed']:
                g=deepcopy(base['given'])
                if state=='omitted':g[k].pop(field)
                else:g[k][field]=state
                e=empty('insufficient_data');e['missing_fields']=[k+'.'+field]
                add(base,'nested-'+k+'-'+field+'-'+state,g,e)
    # These source gates concern ordinary start/adjust, not permission to continue a contraindicated drug while withdrawing.
    if r['identity']['mode'] in ['start','adjust']:
        g=deepcopy(base['given']);g['allergy']=True;add(base,'allergy-positive',g,empty('not_applicable',reason_ids=['allergy'],source_condition={'source_ref':'RU-ESC','source_locator':'§4.3 с.4'}))
        for seizure in ['контролируемые','неконтролируемые','первичные/участившиеся приступы']:
            g=deepcopy(base['given']);g['seizure_state']=seizure
            typ='source_stop_action' if seizure=='первичные/участившиеся приступы' else 'not_applicable' if seizure=='неконтролируемые' else 'clinician_choice'
            e=empty(typ,source_condition={'source_ref':'RU-ESC','source_locator':'§4.4 с.4'})
            if typ=='source_stop_action':e['stop_medication']='RU-ESC'
            if seizure=='контролируемые':e['required_observation']='close seizure observation; no numerical coefficient'
            add(base,'seizure-'+seizure,g,e)
        for k in con['monitoring_context_fields']:
            if k in ['adherence','time_at_dose','known_cyp2c19']:continue
            g=deepcopy(base['given']);g[k]=True
            add(base,'reported-positive-'+k,g,empty('clinician_choice',reason_ids=['source_caution_'+k],source_condition={'source_ref':'RU-ESC','source_locator':next(i['source_locator'] for i in r['inputs'] if i['input_id']==k)},numerical_coefficient=None))
        if rid!='esc-cyp2c19-start':
            g=deepcopy(base['given']);g['known_cyp2c19']='известная слабая активность'
            add(base,'known-weak-cyp-in-ordinary-card',g,empty('clinician_choice',reason_ids=['redirect_to_source_special_branch_or_joint_modifiers'],automatic_coefficient=None,source_condition={'source_ref':'RU-ESC','source_locator':'§4.2 с.3'}))
        con['source_gates'][0]['cautions']=list(dict.fromkeys(con['source_gates'][0]['cautions']+[k for k in con['monitoring_context_fields'] if k not in ['adherence','time_at_dose','known_cyp2c19']]))
(O/'full_scenarios.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'result_contracts.yaml').write_text(yaml.safe_dump(C,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
print('Full ESC nested/contraindication/caution expectations prepared; total',len(D['cases']))
