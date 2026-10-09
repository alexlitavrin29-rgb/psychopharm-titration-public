"""Finite source-action specification, not a dose or clinical decision engine."""
from phase_provenance import selected_phase
OPTIONAL={'reported_context','reported_current_event','reported_source_information','indication_action_choice'}

def matches(value,predicate):
    op=predicate.get('operator');v=predicate.get('value',predicate.get('equals'))
    if op in {'greater_than','>'}:return type(value) in (int,float) and type(v) in (int,float) and value>v
    if op in {'equals','category_equals'} or 'equals' in predicate:return value==v
    return value is True

def source_action_scope(rule,contract,case):
    e=case['expected'];g=case['given'];sc=e.get('source_condition',{})
    if e['result_type']!='source_stop_action' or not sc.get('input') or not sc.get('source_ref'):return None
    key=sc['input'];sid=sc['source_ref'];inputs={i['input_id']:i for i in rule['inputs']}
    if key not in inputs or sid not in inputs[key]['source_refs'] or key not in g:return None
    predicates=[p for p in contract.get('urgent_stop_predicates',[])+contract.get('typed_source_conditions',[]) if p.get('input')==key and p.get('source_ref')==sid and p.get('action','').startswith(('stop','source_stop'))]
    if sc.get('operator') or 'equals' in sc:predicates.append(sc)
    if not predicates:predicates=[dict(operator='equals',value=True)]
    if not any(matches(g[key],p) for p in predicates):return None
    forms={k:i for k,i in inputs.items() if i['data_type']=='structured_form'}
    owner=next((k for k,i in forms.items() if sid in i['source_refs']),None)
    if owner is None or not isinstance(g.get(owner),dict) or g[owner].get('source_id')!=sid:return None
    fields={key,owner};phase=case['external_context']
    if owner=='to_form':
        if phase.get('target_treatment_phase')!='ongoing':return None
    else:
        resolved,origin=selected_phase(rule,case)
        if resolved!='ongoing':return None
        if origin=='consumed_actual_current_dose':
            fields.add('current_dose')
            p=inputs['current_dose']['requirement_predicate']
            if p['kind']=='field_true':fields.add(p['field'])
    # Provided context remains acknowledged/counted. No negative is read for free.
    required=fields.copy()
    provided={k for k,i in inputs.items() if k in g and i['requirement_predicate']['kind'] in OPTIONAL}
    for key in ['maoi_type','maoi_stopped_at']:
        if key in inputs and key in g and any(m.get('interaction_class')=='maoi' and (key=='maoi_type' or m.get('status')=='stopped') for m in g.get('medicines',[]) if isinstance(m,dict)):provided.add(key)
    fields|=provided
    # The static source-action contract contains no future numeric treatment.
    return dict(required_cause_fields=sorted(required),provided_context_fields=sorted(provided-required),used_fields=sorted(fields),primary_cause=sc,source_owner_input=owner,actor_phase='target_B ongoing' if owner=='to_form' else 'selected/A ongoing',scope='Only this published current-treatment source action; other dose/planning gates are unassessed, no dose/calendar/target permission or clinical clearance')
