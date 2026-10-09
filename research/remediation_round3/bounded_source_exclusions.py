"""Finite prepared exclusion certificates, not a medical classification engine."""
from bounded_source_actions import OPTIONAL
from phase_provenance import selected_phase

def source_terminal_scope(rule,case,result_type):
    e=case['expected'];g=case['given'];cert=e.get('terminal_source_certificate')
    if e['result_type']!=result_type or not cert or cert.get('result_type','not_applicable')!=result_type:return None
    if e.get('total_daily_dose_mg') is not None or e.get('schedule') or e.get('clinical_clearance') is True:return None
    inputs={i['input_id']:i for i in rule['inputs']}
    if any(case['external_context'].get(k)!=v for k,v in cert['selected_context'].items()):return None
    if any(case['external_context'].get(k)!=v for k,v in cert.get('required_phase_context',{}).items()):return None
    if cert.get('calculation_at') is not None and case['external_context'].get('calculation_at')!=cert['calculation_at']:return None
    owner=cert['source_owner_input'];sid=cert['source_ref']
    if owner not in inputs or sid not in inputs[owner]['source_refs'] or not isinstance(g.get(owner),dict) or g[owner].get('source_id')!=sid:return None
    for k,v in cert['causal_values'].items():
        if k not in inputs or k not in g:return None
        if k in cert.get('fact_components',{}):
            if not isinstance(g[k],dict) or any(g[k].get(f.split('.',1)[1])!=v.get(f.split('.',1)[1]) for f in cert['fact_components'][k]):return None
        elif g[k]!=v:return None
    if result_type=='clinician_choice' and e.get('source_actions'):
        if owner=='to_form':
            if case['external_context'].get('target_treatment_phase')!='ongoing':return None
        elif selected_phase(rule,case)[0]!='ongoing':return None
    required=set(cert['causal_values'])|{owner}
    supplied={k for k,i in inputs.items() if k in g and i['requirement_predicate']['kind'] in OPTIONAL}
    for k in ['maoi_type','maoi_stopped_at']:
        if k in g and any(m.get('interaction_class')=='maoi' and (k=='maoi_type' or m.get('status')=='stopped') for m in g.get('medicines',[])):supplied.add(k)
    components={k:[k+'.'+field for field in g[k]] for k in cert.get('fact_components',{})}
    return dict(required_cause_fields=sorted(required),provided_context_fields=sorted(supplied-required),used_fields=sorted(required|supplied),fact_components=components,primary_cause=dict(input=cert['source_condition_field'],source_ref=sid,source_locator=cert['source_locator']),source_owner_input=owner,actor_phase=cert.get('actor_phase','No current-use/cessation inference: source exclusion only'),scope=cert['scope'])

def source_exclusion_scope(rule,case):return source_terminal_scope(rule,case,'not_applicable')
def source_choice_scope(rule,case):return source_terminal_scope(rule,case,'clinician_choice')
def source_form_scope(rule,case):return source_terminal_scope(rule,case,'form_not_feasible')
