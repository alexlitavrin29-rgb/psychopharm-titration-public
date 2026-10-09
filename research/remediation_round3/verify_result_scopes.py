"""Causal prepared terminal scopes and adversarial scope regressions; no clinical engine."""
from pathlib import Path
from copy import deepcopy
import json
import verify_contracts
from bounded_source_exclusions import source_exclusion_scope,source_choice_scope,source_form_scope
from bounded_unselected_example import unselected_example_scope
O=Path(__file__).resolve().parent
TAPERS={'dulox-taper-limit','esc-taper-limit','fluvox-taper-limit','ser-taper-limit','venla-xr-taper-limit'}

def check(d,paths):
 errors=[];by_id={c['case_id']:c for c in d['cases']};pp={p['full_example']:p for p in paths}
 def ck(ok,msg):
  if not ok:errors.append(msg)
 for c in d['cases']:
  e=c['expected'];g=c['given'];rid=c['rule_id'];r=d['rules'][rid]
  ck(all(k in g and g[k] is False for k in e.get('confirmed_negatives',[])),'full negative lacks actual false: '+c['case_id'])
  if e.get('population_applicability')=='adult_source_population':ck(type(g.get('age')) in (int,float) and g['age']>=18,'adult applicability lacks known age: '+c['case_id'])
  cert=e.get('terminal_source_certificate')
  if not cert:continue
  fn={'not_applicable':source_exclusion_scope,'clinician_choice':source_choice_scope,'form_not_feasible':source_form_scope}[e['result_type']]
  scope=fn(r,c);ck(scope is not None,'certificate cause/source/actor mismatch: '+c['case_id'])
  if scope is None:continue
  ck(not e.get('schedule') and e.get('total_daily_dose_mg') is None and e.get('clinical_clearance') is False,'bounded terminal grants individual treatment: '+c['case_id'])
  p=pp.get(c['case_id']);ck(p is not None,'certified witness not exposed: '+c['case_id'])
  if p is None:continue
  ck(set(scope['required_cause_fields'])<=set(p['full_projected_given']),'cause omitted from path: '+c['case_id'])
  forms={i['input_id'] for i in r['inputs'] if i['data_type']=='structured_form'}
  ck(set(p['full_projected_given'])<=set(scope['used_fields'])|forms,'late numerical prerequisite after bounded terminal: '+c['case_id'])
  ck(all(i['input_id'] in p['full_projected_given'] or i['input_id'] in p['full_projected_expected']['unassessed_context'] for i in r['inputs']),'bounded omitted input silently assessed: '+c['case_id'])
  if any(x in c['case_id'] for x in ['--audit-final-source-exclusion','--audit-final-source-caution','--audit-final-known-terminal']):
   ck(set(g)<=set(scope['required_cause_fields'])|forms,'sparse witness has unrelated admission facts: '+c['case_id'])
   for k,components in scope.get('fact_components',{}).items():
    ck(all(f in p['required_independent_facts'] for f in components),'paired cause not counted: '+c['case_id'])
    ck(all(k+'.'+f in p['full_projected_expected']['unassessed_context'] for f in ['A','B'] if k+'.'+f not in components),'other allergy actor silently negative: '+c['case_id'])
 for rid in TAPERS:
  r=d['rules'][rid];contract=d['contracts'][rid]
  ck(contract['required_inputs']==['form'],'source reference still needs patient preflight: '+rid)
  refs=[c for c in d['cases'] if c['rule_id']==rid and '--audit-final-conditional-adult-reference' in c['case_id']]
  ck(bool(refs),'source-only taper witness absent: '+rid)
  for c in refs:
   ck(set(c['given'])=={'form'} and c['expected'].get('adult_source_reference_only') is True and c['expected'].get('individual_taper_schedule') is None,'reference grants individual taper: '+rid)
 for p in paths:
  c=by_id[p['full_example']];scope=unselected_example_scope(d['rules'][p['rule_id']],c)
  if p['full_projected_expected'].get('population_applicability')=='adult_source_population':ck(type(p['full_projected_given'].get('age')) in (int,float) and p['full_projected_given']['age']>=18,'projected adult applicability uses unasked age: '+c['case_id'])
  if scope:
   ck(set(scope['required_cause_fields'])<=set(p['full_projected_given']),'unselected example cause missing: '+c['case_id'])
   ck(not p['full_projected_expected'].get('schedule') and p['full_projected_expected'].get('total_daily_dose_mg') is None,'unselected example grants calendar: '+c['case_id'])
 return errors

def run():
 d=verify_contracts.collect();paths=json.loads((O/'actual_question_paths.json').read_text(encoding='utf-8'));errors=check(d,paths);mutations=[]
 def reject(name,c,fn,change):
  x=deepcopy(c);change(x);detected=fn(d['rules'][x['rule_id']],x) is None;mutations.append(dict(mutation=name,rejected=detected))
  if not detected:errors.append('scope mutation escaped: '+name)
 exclusions=[c for c in d['cases'] if c['expected'].get('terminal_source_certificate',{}).get('result_type','not_applicable')=='not_applicable' and c['expected'].get('terminal_source_certificate')]
 c=exclusions[0];key=c['expected']['terminal_source_certificate']['source_condition_field'];owner=c['expected']['terminal_source_certificate']['source_owner_input']
 reject('missing primary cause',c,source_exclusion_scope,lambda x:x['given'].pop(key))
 reject('unknown primary cause',c,source_exclusion_scope,lambda x:x['given'].update({key:'unknown'}))
 reject('wrong actual primary product',c,source_exclusion_scope,lambda x:x['given'][owner].update(source_id='RU-NONOWNER'))
 reject('exclusion becomes dose',c,source_exclusion_scope,lambda x:x['expected'].update(total_daily_dose_mg=999))
 alt=next(c for c in exclusions if c['expected']['terminal_source_certificate']['source_condition_field'] in {'ALT_ratio','AST_ratio','alt_ratio_uln','ast_ratio_uln'} and c['rule_id'].startswith('switch'))
 reject('B unknown cannot stand for first start',alt,source_exclusion_scope,lambda x:x['external_context'].update(target_treatment_phase='unknown'))
 reject('B already ongoing cannot stand for first start',alt,source_exclusion_scope,lambda x:x['external_context'].update(target_treatment_phase='ongoing'))
 dem=next(c for c in exclusions if c['expected']['terminal_source_certificate']['source_condition_field']=='dementia')
 reject('dementia without elderly category',dem,source_exclusion_scope,lambda x:x['given'].update(elderly_population='unknown'))
 maoi=next(c for c in exclusions if c['expected']['terminal_source_certificate'].get('calculation_at'))
 reject('stopped MAOI missing system clock',maoi,source_exclusion_scope,lambda x:x['external_context'].pop('calculation_at'))
 choice=next(c for c in d['cases'] if c['expected'].get('terminal_source_certificate',{}).get('result_type')=='clinician_choice' and c['expected'].get('source_actions') and c['external_context'].get('treatment_phase')=='ongoing')
 reject('current physician action without own ongoing actor',choice,source_choice_scope,lambda x:x['external_context'].update(treatment_phase='unknown'))
 birth=next(c for c in d['cases'] if c['expected'].get('terminal_source_certificate',{}).get('source_condition_field')=='effective_contraception')
 reject('contraception without reproductive category',birth,source_choice_scope,lambda x:x['given'].update(reproductive_population='unknown'))
 example=next(c for c in d['cases'] if c['case_id'].endswith('--audit-final-unselected-example-false'))
 reject('unknown selection normalized false',example,unselected_example_scope,lambda x:x['given'].update(example_selected='unknown'))
 dd=deepcopy(d);next(c for c in dd['cases'] if c['rule_id']=='switch-parox-ago-selected-example')['expected'].setdefault('confirmed_negatives',[]).append('audit_unasked')
 mutations.append(dict(mutation='full expected stale negative',rejected=bool(check(dd,paths))))
 if not mutations[-1]['rejected']:errors.append('stale negative mutation escaped')
 dd=deepcopy(d);c=next(c for c in dd['cases'] if '--audit-final-conditional-adult-reference' in c['case_id']);c['expected']['population_applicability']='adult_source_population'
 mutations.append(dict(mutation='absent age normalized adult',rejected=bool(check(dd,paths))))
 if not mutations[-1]['rejected']:errors.append('unknown population mutation escaped')
 report=dict(status='pass' if not errors else 'fail',prepared_cases=len(d['cases']),paths=len(paths),certificate_cases=sum(bool(c['expected'].get('terminal_source_certificate')) for c in d['cases']),negative_mutations=mutations,clinical_engine_executed=False,scope='Literal prepared primary-bound causal certificates, projection and actor regression; independent medical sufficiency is reviewed separately',errors=errors)
 (O/'result_scope_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(status=report['status'],certificate_cases=report['certificate_cases'],mutations=len(mutations),errors=errors[:20]),ensure_ascii=False));return bool(errors)
if __name__=='__main__':raise SystemExit(run())
