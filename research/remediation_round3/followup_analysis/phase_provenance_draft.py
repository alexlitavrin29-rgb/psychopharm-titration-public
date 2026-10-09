"""Source actor phase from explicit status or an actually consumed current dose."""
def consumed_current_dose(rule, given):
    i=next((i for i in rule['inputs'] if i['input_id']=='current_dose'),None)
    if not i or i.get('fact_semantics')!='actually_taken_current_daily_dose':return False
    p=i['requirement_predicate'];k=p['kind']
    active=k=='always' or k=='field_true' and given.get(p['field']) is True
    v=given.get('current_dose')
    return active and type(v) in (int,float) and v>0

def selected_phase(rule, case):
    phase=case['external_context'].get('treatment_phase','selected_mode')
    if phase in {'ongoing','not_started','unknown'}:
        return phase,'explicit_treatment_phase'
    if rule['identity']['mode']=='start':return 'not_started','first_start_selection'
    if consumed_current_dose(rule,case['given']):return 'ongoing','consumed_actual_current_dose'
    return 'unknown','selected_mode_does_not_establish_current_use'

def owns_selected_action(rule, expected):
    owner=next((i['source_refs'][0] for i in rule['inputs'] if i['input_id'] in {'from_form','form'}),None)
    return owner is not None and expected.get('stop_medication')==owner or any(a.get('medication_role')=='selected_or_A' for a in expected.get('source_actions',[]))
