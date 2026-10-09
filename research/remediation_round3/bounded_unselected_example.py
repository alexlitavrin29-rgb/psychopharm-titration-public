"""No selected published example implies no patient calendar; not clinical gating."""
from bounded_source_actions import OPTIONAL

def unselected_example_scope(rule,case):
    if rule['rule_id']!='switch-parox-ago-selected-example':return None
    e=case['expected'];g=case['given']
    if e['result_type']!='clinician_choice' or e.get('total_daily_dose_mg') is not None or e.get('schedule') or e.get('source_actions') or e.get('stop_medication'):return None
    chosen=g.get('example_selected');dose=g.get('current_dose')
    fields={'from_form','to_form','example_selected'}
    if chosen is True and type(dose) in (int,float) and dose!=40:fields.add('current_dose')
    elif chosen is not False:return None
    if any(k not in g for k in fields):return None
    if g['from_form'].get('source_id')!='RU-PAROX' or g['to_form'].get('source_id')!='RU-AGO':return None
    inputs={i['input_id']:i for i in rule['inputs']}
    supplied={k for k,i in inputs.items() if k in g and i['requirement_predicate']['kind'] in OPTIONAL}
    if 'medicines' in supplied:
        for k in ['maoi_type','maoi_stopped_at']:
            if k in g and any(m.get('interaction_class')=='maoi' and (k=='maoi_type' or m.get('status')=='stopped') for m in g['medicines']):supplied.add(k)
    return dict(required_cause_fields=sorted(fields),provided_context_fields=sorted(supplied-fields),used_fields=sorted(fields|supplied),primary_cause=dict(input='example_selected',source_ref='RU-PAROX',source_locator='§4.2 физ.с.4; published 40 mg cessation example'),source_owner_input='from_form',actor_phase='No current medication action inferred',scope='Only absence of this selected published example; no dose/calendar, target start, clinical clearance or medication change')
