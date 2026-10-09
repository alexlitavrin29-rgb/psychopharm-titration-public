"""Supplied context must be transmitted and counted; no medical calculator."""
from pathlib import Path
from copy import deepcopy
import json,yaml
import verify_contracts
from phase_provenance import selected_phase
O=Path(__file__).resolve().parent
KINDS={'reported_context','reported_current_event','reported_source_information'}

def check(d,paths):
    errors=[]
    cases={c['case_id']:c for c in d['cases']}
    represented={p['full_example'] for p in paths}
    for c in d['cases']:
        optional={i['input_id'] for i in d['rules'][c['rule_id']]['inputs'] if i['requirement_predicate']['kind'] in KINDS}
        if c['branch_id'] is None and set(c['expected'].get('reason_ids',[]))&optional and c['case_id'] not in represented:errors.append('Context-sensitive full result excluded from paths: '+c['case_id'])
    for p in paths:
        c=cases[p['full_example']];r=d['rules'][p['rule_id']]
        optional={i['input_id']:i for i in r['inputs'] if i['requirement_predicate']['kind'] in KINDS}
        supplied=set(optional)&set(c['given'])
        for k in supplied:
            if k not in p['full_projected_given'] or p['full_projected_given'][k]!=c['given'][k]:errors.append('Supplied context lost: '+c['case_id']+'/'+k)
            if not any(f==k or f.startswith(k+'.') for f in p['required_independent_facts']):errors.append('Supplied context free: '+c['case_id']+'/'+k)
        for k in set(optional)-set(c['given']):
            if k not in p['full_projected_expected'].get('unassessed_context',[]) or k in p['full_projected_expected'].get('confirmed_negatives',[]):errors.append('Missing context silently negative: '+c['case_id']+'/'+k)
        for k in set(c['expected'].get('reason_ids',[]))&set(optional):
            if k not in p['full_projected_given']:errors.append('Expected reason lacks supplied cause: '+c['case_id']+'/'+k)
        if p['count']!=len(p['initial_selections'])+len(p['required_independent_facts']):errors.append('False path count: '+c['case_id'])
        if '--audit-final-minimal-routine' in c['case_id']:
            if supplied or c['expected'].get('clinical_clearance') is not False:errors.append('Minimal path contains supplied optional context or grants clearance: '+c['case_id'])
    for rid,r in d['rules'].items():
        for i in r['inputs']:
            if i['input_id']=='current_dose' and i['requirement_predicate']['kind']=='reported_context':
                if i.get('fact_semantics')!='reported_course_dose_without_current_use_confirmation':errors.append('Reported course dose falsely means actual current use: '+rid)
                c=dict(given=dict(current_dose=50),external_context=dict(treatment_phase='selected_mode'))
                if selected_phase(r,c)[0]=='ongoing':errors.append('Historical dose proves current phase: '+rid)
    return errors

def run():
    d=verify_contracts.collect();paths=json.loads((O/'actual_question_paths.json').read_text(encoding='utf-8'));errors=check(d,paths);mutations=[]
    for name in ['lost_positive_context','lost_negative_context','lost_unknown_context','free_reported_fact','missing_as_negative','false_count','historical_as_actual','excluded_context_result']:
        dd=deepcopy(d);pp=deepcopy(paths)
        if name.startswith('lost_'):
            state={'lost_positive_context':True,'lost_negative_context':False,'lost_unknown_context':'unknown'}[name]
            p=next(p for p in pp if any(i['requirement_predicate']['kind']=='reported_context' and p['full_projected_given'].get(i['input_id'])==state and type(p['full_projected_given'].get(i['input_id'])) is type(state) for i in dd['rules'][p['rule_id']]['inputs']))
            k=next(i['input_id'] for i in dd['rules'][p['rule_id']]['inputs'] if i['requirement_predicate']['kind']=='reported_context' and p['full_projected_given'].get(i['input_id'])==state and type(p['full_projected_given'].get(i['input_id'])) is type(state));p['full_projected_given'].pop(k)
        elif name=='free_reported_fact':
            p=next(p for p in pp if 'suicide_risk' in p['full_projected_given']);p['required_independent_facts'].remove('suicide_risk');p['count']-=1
        elif name=='missing_as_negative':
            p=next(p for p in pp if '--audit-final-minimal-routine' in p['full_example']);p['full_projected_expected']['confirmed_negatives'].append(p['full_projected_expected']['unassessed_context'][0])
        elif name=='false_count':pp[0]['count']-=1
        elif name=='historical_as_actual':next(i for i in dd['rules']['preg-taper-limit']['inputs'] if i['input_id']=='current_dose')['fact_semantics']='actually_taken_current_daily_dose'
        else:
            p=next(p for p in pp if cases_reason(dd,p));pp.remove(p)
        found=check(dd,pp);mutations.append(dict(mutation=name,rejected=bool(found),evidence=found[:1]))
        if not found:errors.append('Mutation escaped: '+name)
    report=dict(status='pass' if not errors else 'fail',paths=len(paths),negative_mutations=mutations,scope='Presence, counting and source-actor provenance only; expected medical result remains independently reviewed research data',errors=errors)
    (O/'reported_context_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(status=report['status'],paths=len(paths),mutations=len(mutations),errors=errors),ensure_ascii=False));return bool(errors)

def cases_reason(d,p):
    c=next(c for c in d['cases'] if c['case_id']==p['full_example'])
    optional={i['input_id'] for i in d['rules'][c['rule_id']]['inputs'] if i['requirement_predicate']['kind'] in KINDS}
    return c['branch_id'] is None and bool(set(c['expected'].get('reason_ids',[]))&optional)
if __name__=='__main__':raise SystemExit(run())
