"""Regression for reviewed source-action, reference and question-scope defects."""
from pathlib import Path
from copy import deepcopy
import json,re,yaml
import verify_contracts
from bounded_source_actions import source_action_scope
O=Path(__file__).resolve().parent
FORBIDDEN_STOP={'duration_constraint','maximum_mg','minimum_increase_interval_weeks','review_period_weeks','source_initial_mg','initial_days','source_next_mg','hold_if','recommended_mg','optional_increment_mg','minimum_interval_weeks','beyond_recommended_requires','target_source_start_mg','overlap_allowed_on_first_day_of_A_reduction','monitoring','published_option_mg','conditional_next_total_mg','initial_period_weeks'}

def check(d,paths):
 errors=[];stats=dict(source_stop_cases=0,bounded_action_cases=0,reference_cases=0,unknown_class_paths=0)
 def ck(ok,msg):
  if not ok:errors.append(msg)
 for c in d['cases']:
  e=c['expected'];rid=c['rule_id'];r=d['rules'][rid];con=d['contracts'][rid]
  if e['result_type']=='source_stop_action':
   stats['source_stop_cases']+=1
   ck(not FORBIDDEN_STOP.intersection(e),'Routine dose/taper/start metadata carried into source cessation: '+c['case_id'])
   ck(e.get('total_daily_dose_mg') is None and not e.get('schedule') and not e.get('clinical_clearance'),'Cessation contains individual future treatment: '+c['case_id'])
  scope=source_action_scope(r,con,c)
  if scope:
   stats['bounded_action_cases']+=1
   ck(scope['primary_cause']['input'] in scope['required_cause_fields'],'Unrequired cessation cause: '+c['case_id'])
   ck(set(scope['used_fields'])<=set(c['given']),'Cessation reads an absent patient fact: '+c['case_id'])
   if '--audit-final-bounded-action' in c['case_id']:
    ck(not set(scope['provided_context_fields']),'Sparse cessation silently receives prior context: '+c['case_id'])
    missing=set(i['input_id'] for i in r['inputs'])-set(c['given'])
    ck(missing<=set(e.get('unassessed_context',[])),'Sparse cessation normalizes omitted context: '+c['case_id'])
  if rid in {'switch-esc-ago','switch-parox-ago','switch-ser-ago'} and e['result_type']=='clinician_choice':
   stats['reference_cases']+=1
   ck(e.get('target_source_start_mg') is None and e.get('overlap_allowed_on_first_day_of_A_reduction') is None,'Published component is a patient start/overlap permission: '+c['case_id'])
   ck(e.get('no_automatic_target_start') is True and e.get('full_pair_calendar') is None,'Unproved pair calendar/start: '+c['case_id'])
 for p in paths:
  c=dict(rule_id=p['rule_id'],given=p['full_projected_given'],external_context=p['full_external_context'],expected=p['full_projected_expected'])
  r=d['rules'][p['rule_id']];con=d['contracts'][p['rule_id']]
  if p.get('bounded_source_action_scope'):
   scope=source_action_scope(r,con,c)
   ck(scope is not None,'Projected source cessation loses cause, source or phase: '+p['full_example'])
   ck(not FORBIDDEN_STOP.intersection(c['expected']),'Projected cessation retains routine future treatment: '+p['full_example'])
   missing=set(i['input_id'] for i in r['inputs'])-set(c['given'])
   ck(missing<=set(c['expected'].get('unassessed_context',[])),'Unasked stop-path context normalized: '+p['full_example'])
  meds=c['given'].get('medicines',[])
  if any(m.get('interaction_class')=='unknown' for m in meds if isinstance(m,dict)) and not any(m.get('interaction_class')=='maoi' for m in meds if isinstance(m,dict)):
   stats['unknown_class_paths']+=1
   ck(not any(f.startswith(('maoi_type.','maoi_stopped_at.')) for f in p['required_independent_facts']),'MAOI detail before class is established: '+p['full_example'])
   ck('maoi_type' not in c['given'] and 'maoi_stopped_at' not in c['given'],'Unconsumed unknown-class MAOI map: '+p['full_example'])
 for rid in ['switch-esc-ago','switch-parox-ago','switch-ser-ago','switch-esc-ser','switch-ser-esc','preg-taper-limit','phen-taper-limit']:
  ck(bool(d['contracts'][rid].get('qualitative_result_scope')),'Unbounded qualitative reference: '+rid)
 phen=next(i for i in d['rules']['phen-taper-limit']['inputs'] if i['input_id']=='form')
 ck('§4.2 физ.с.2' in phen['source_locator'],'PHEN form/method locator stale')
 selected=d['contracts']['switch-parox-ago-selected-example']['input_requirements']
 ck(selected['dementia']==dict(kind='field_true',field='elderly_population'),'Dementia question ignores primary elderly qualifier')
 for k in ['liver_injury_signs','transaminases_rising','mania_symptoms']:ck(selected[k]['kind']=='target_ongoing','B current condition borrows A phase: '+k)
 for k in ['ect','akathisia','glaucoma','qt_risk']:ck(selected[k]['kind']=='reported_context','Unjustified universal selected-cessation caution: '+k)
 return errors,stats

def run():
 d=verify_contracts.collect();paths=json.loads((O/'actual_question_paths.json').read_text(encoding='utf-8'));errors,stats=check(d,paths);mutations=[]
 def test(name,x,pp):
  caught=bool(check(x,pp)[0]);mutations.append(dict(mutation=name,rejected=caught))
  if not caught:errors.append('Mutation not rejected: '+name)
 for name in ['stop_inherits_taper','reference_grants_overlap','hidden_unknown_maoi','PHEN_stale_locator','B_condition_uses_A_phase','dementia_without_elder_qualifier']:
  x=deepcopy(d);pp=deepcopy(paths)
  if name=='stop_inherits_taper':next(c for c in x['cases'] if c['expected']['result_type']=='source_stop_action')['expected']['duration_constraint']={'chosen_minimum_weeks':2}
  elif name=='reference_grants_overlap':next(c for c in x['cases'] if c['rule_id']=='switch-esc-ago' and c['expected']['result_type']=='clinician_choice')['expected']['overlap_allowed_on_first_day_of_A_reduction']=True
  elif name=='hidden_unknown_maoi':
   p=next(p for p in pp if any(m.get('interaction_class')=='unknown' for m in p['full_projected_given'].get('medicines',[]) if isinstance(m,dict)) and not any(m.get('interaction_class')=='maoi' for m in p['full_projected_given'].get('medicines',[]) if isinstance(m,dict)));p['full_projected_given']['maoi_type']={'unclassified':'unknown'}
  elif name=='PHEN_stale_locator':next(i for i in x['rules']['phen-taper-limit']['inputs'] if i['input_id']=='form')['source_locator']='§4.2 с.3'
  elif name=='B_condition_uses_A_phase':x['contracts']['switch-parox-ago-selected-example']['input_requirements']['liver_injury_signs']={'kind':'ongoing_selected_drug'}
  else:x['contracts']['switch-parox-ago-selected-example']['input_requirements']['dementia']={'kind':'always'}
  test(name,x,pp)
 sample=next(c for c in d['cases'] if '--audit-final-bounded-action' in c['case_id'] and source_action_scope(d['rules'][c['rule_id']],d['contracts'][c['rule_id']],c))
 scope=source_action_scope(d['rules'][sample['rule_id']],d['contracts'][sample['rule_id']],sample)
 for name in ['unknown_cause','wrong_source_owner','unknown_actor_phase']:
  c=deepcopy(sample)
  if name=='unknown_cause':c['given'][scope['primary_cause']['input']]='unknown'
  elif name=='wrong_source_owner':c['given'][scope['source_owner_input']]['source_id']='WRONG'
  elif scope['source_owner_input']=='to_form':c['external_context']['target_treatment_phase']='unknown'
  else:c['external_context']['treatment_phase']='unknown'
  caught=source_action_scope(d['rules'][c['rule_id']],d['contracts'][c['rule_id']],c) is None
  mutations.append(dict(mutation=name,rejected=caught))
  if not caught:errors.append('Source action accepted mutation: '+name)
 root=O.parents[1]
 criteria=lambda name:re.findall(r'^- \[ \] (.*)$',(root/'psychopharm_codex_pack'/name).read_text(encoding='utf-8'),re.M)
 v2=criteria('ACCEPTANCE_V2.md');v3=criteria('ACCEPTANCE_V3.md');diff=[i+1 for i,(a,b) in enumerate(zip(v2,v3)) if a!=b]
 if len(v2)!=30 or len(v3)!=30 or diff!=[18]:errors.append('Requirements changed outside #18')
 report=dict(status='pass' if not errors else 'fail',**stats,negative_mutations=mutations,criteria_changed=diff,scope='Finite primary source-action/referral and data-flow regression; no clinical engine, clinical validation or complete medical correctness proof',errors=errors)
 (O/'scope_repair_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(status=report['status'],counts=stats,mutations=len(mutations),errors=errors),ensure_ascii=False));return bool(errors)
if __name__=='__main__':raise SystemExit(run())
