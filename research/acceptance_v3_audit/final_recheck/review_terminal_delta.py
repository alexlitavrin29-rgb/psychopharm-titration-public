"""Independent finite causal/result checks using prior own same-SHA primary norms."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime
import json, yaml, sys, ast, hashlib, collections
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];R=ROOT/'research/remediation_round3'
OLD=ROOT/'research/acceptance_v3_audit/final_review'
SNAP=ROOT/'research/remediation_round3/v3_review1_snapshot/research/remediation_round3'
SHA='27ef14e77185b7b104d43199664a5b1ca42b73dd8b09f921ee539e97fae971f8'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
RULES={p.stem:yaml.safe_load(p.read_text(encoding='utf8')) for p in (R/'rules').glob('*.yaml')}
CON=yaml.safe_load((R/'result_contracts.yaml').read_text(encoding='utf8'))['rules']
CASES={c['case_id']:c for c in read(R/'full_scenarios.json')['cases']}
OLDCASES={c['case_id']:c for c in read(SNAP/'full_scenarios.json')['cases']}
PATHS={p['full_example']:p for p in read(R/'actual_question_paths.json')}
NORMS=read(ROOT/'research/acceptance_v2_audit/condition_completion/primary_norms.json')
N={(n['source_id'],n['condition_key'],n['source_sha256']):n for n in NORMS}
SOURCES=read(R/'sources.json')
sys.path.insert(0,str(R))
from bounded_source_exclusions import source_exclusion_scope,source_choice_scope,source_form_scope
from bounded_unselected_example import unselected_example_scope
functions={'not_applicable':source_exclusion_scope,'clinician_choice':source_choice_scope,'form_not_feasible':source_form_scope}
tree=ast.parse((OLD/'source_counterchecks.py').read_text(encoding='utf8'))
medical_code=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='medical_cause')
env={'datetime':datetime,'current_exclusions':{s:set(v) for s,v in {
 'RU-AGO':['strong_CYP1A2'],'RU-DULOX':['maoi','strong_CYP1A2'],
 'RU-ESC':['irreversible_maoi','pimozide','QT_prolonging'],'RU-SER':['maoi','pimozide'],
 'RU-FLUVOX':['maoi','astemizole','pimozide','terfenadine','cisapride','tizanidine','ramelteon'],
 'RU-PAROX':['maoi','pimozide','thioridazine'],'RU-VENLA-XR':['maoi']}.items()}}
exec(compile(ast.Module(body=[medical_code],type_ignores=[]),'own_previous_primary_exclusion_checks','exec'),env)
checked=[];errors=[];controls=[];records=[]
def ck(label,ok,cid=None,detail=None):
 x=dict(check=label,pass_=bool(ok),case_id=cid,detail=detail);checked.append(x)
 if not ok:errors.append(x)
def control(name,c,fn,mutate):
 x=deepcopy(c);mutate(x);ok=fn(RULES[x['rule_id']],x) is None
 controls.append(dict(case_id=c['case_id'],mutation=name,rejected=ok))
 ck('bounded cause countercheck',ok,c['case_id'],name)

expected_lists={x['case_id']:x for n in ['exclusion_scope_independent.json','choice_scope_candidates.json','choice_reason_scope_residue.json','form_scope_residue.json'] for x in read(OLD/n)['rows']}
cert_cases=[c for c in CASES.values() if c['expected'].get('terminal_source_certificate')]
ck('all finite old693 scopes have a current certificate',all(k in CASES and CASES[k]['expected'].get('terminal_source_certificate') for k in expected_lists))
for c in cert_cases:
 cid=c['case_id'];r=RULES[c['rule_id']];g=c['given'];e=c['expected'];x=c['external_context'];t=e['terminal_source_certificate'];sid=t['source_ref'];owner=t['source_owner_input'];key=t['source_condition_field']
 fn=functions[e['result_type']];scope=fn(r,c);p=PATHS.get(cid)
 ck('actual source/known cause and phase produce finite scope',scope is not None,cid)
 ck('all certified cases have their complete selected path',p is not None,cid)
 norms=[]
 for n in t['primary_norms']:
  own=N.get((n['source_id'],n['condition_key'],n['source_sha256']));norms.append(own)
  ck('certificate grounded in own previous primary norm and physical pages',own is not None and own['physical_pages']==n['physical_pages'] and own['independent_primary_norm']==n['independent_primary_norm'],cid,[n['source_id'],n['condition_key'],n['physical_pages']])
  ck('primary norm bytes still identical',hashlib.sha256((ROOT/n['source_file']).read_bytes()).hexdigest()==n['source_sha256'],cid)
 ck('actual source owner product/version/registration is explicit',g[owner]['source_id']==sid and g[owner]['source_version']==SOURCES[sid]['version_or_update_date'] and g[owner]['registration_number']==SOURCES[sid].get('registry_observation',{}).get('registration_number',SOURCES[sid].get('doi_or_registry_id')),cid)
 ck('certificate context no disguised unknown decision',all(x.get(k)==v for k,v in t['selected_context'].items()) and all(x.get(k)==v for k,v in t.get('required_phase_context',{}).items()),cid)
 ck('bounded result no individual numeric calendar or clinical clearance',e.get('total_daily_dose_mg') is None and not e.get('schedule') and e.get('clinical_clearance') is False and not e.get('target_start_allowed') and not e.get('target_source_start_mg') and not e.get('overlap_allowed_on_first_day_of_A_reduction'),cid)
 if e['result_type']=='not_applicable':ck('independent source-specific exclusion inequality/class/compound/clock',env['medical_cause'](t,c),cid,t['causal_values'])
 if e['result_type']=='form_not_feasible':
  a=t.get('arithmetic_source_reference')
  if a:
   organ=next(iter(t['causal_values'].values()));renal='metric' in organ
   ok=(organ['assessment']=='known' and organ.get('metric')=='absolute_GFR' and organ.get('unit')=='mL/min' and 10<=organ.get('value',-1)<=30) if renal else (organ['assessment']=='known' and organ['category'] in ['mild','moderate'])
   ck('own primary75/50%/37.5 wholeXR arithmetic cause',ok and a['published_start_mg']==75 and a['published_reduction_percent']==50 and a['arithmetic_total_mg']==37.5 and g[owner]['strengths_mg']==[75,150] and g[owner]['release']=='prolonged' and e.get('IR_substitution_allowed') is False,cid)
  else:
   field=key.split('.',1)[1] if '.' in key else 'release'
   own_release={'RU-AGO':'immediate','RU-DULOX':'enteric','RU-ESC':'immediate','RU-FLUVOX':'immediate','RU-PAROX':'immediate','RU-PREG':'immediate','RU-SER':'immediate','RU-VENLA-XR':'prolonged'}
   ck('actual known source-form mismatch, not an unknown form',field=='release' and g[owner].get(field) not in [None,'unknown','not_assessed'] and g[owner].get(field)!=own_release[sid],cid,[key,field])
 if scope is not None and p:
  used=set(scope['used_fields']);forms={i['input_id'] for i in r['inputs'] if i['data_type']=='structured_form'}
  ck('scope contains causal facts only plus actual optional supplied context',set(p['full_projected_given'])=={k for k in g if k in used or k in forms},cid)
  ck('all omitted nonused fields explicitly unassessed',all(i['input_id'] in p['full_projected_given'] or i['input_id'] in p['full_projected_expected']['unassessed_context'] for i in r['inputs']),cid)
 for cause in t['causal_values']:
  control('omitted causal '+cause,c,fn,lambda z,k=cause:z['given'].pop(k))
  if e.get('clarification_only'):control('known positive cannot reuse unknown clarification '+cause,c,fn,lambda z,k=cause:z['given'].update({k:True}))
  else:control('unknown causal '+cause,c,fn,lambda z,k=cause:z['given'].update({k:'unknown'}))
 if t.get('calculation_at'):
  control('missing source clock',c,fn,lambda z:z['external_context'].pop('calculation_at'))
 for k in t.get('required_phase_context',{}):control('unknown required own phase '+k,c,fn,lambda z,q=k:z['external_context'].update({q:'unknown'}))
 control('wrong own source id',c,fn,lambda z:z['given'][owner].update(source_id='RU-NONOWNER'))
 if e['result_type']=='clinician_choice' and e.get('source_actions'):
  phase_key='target_treatment_phase' if owner=='to_form' else 'treatment_phase'
  for v in ['unknown','not_started']:control('current action own phase '+v,c,fn,lambda z,v=v:z['external_context'].update({phase_key:v}))
  ck('current action keeps active currentdose when ongoing was derived',x.get('treatment_phase')!='selected_mode' or owner=='to_form' or 'current_dose' in t['causal_values'],cid)
 if key=='effective_contraception':ck('contraception causal compound kept',t['causal_values'].get('reproductive_population') is True and g.get('reproductive_population') is True,cid)
 if key=='medicines':
  ms=g['medicines'];ck('known source class comes with INN/status, no speculative MAOI fields',len(ms)==1 and ms[0].get('inn') and ms[0].get('status') in ['current','stopped'] and ms[0].get('interaction_class') not in ['unknown','not_assessed',None],cid)
  if ms[0]['interaction_class']=='duplicate_duloxetine_product':ck('duplicate requires actual independent extra-product fact',ms[0].get('additional_product') is True,cid)
 records.append(dict(case_id=cid,rule_id=c['rule_id'],result=e['result_type'],primary_norms=[dict(source_id=n['source_id'],condition_key=n['condition_key'],sha256=n['source_sha256'],physical_pages=n['physical_pages']) for n in t['primary_norms']],cause=t['causal_values'],phase=t.get('required_phase_context',{}),own_action=e.get('source_actions'),source_scope=scope))

# Source-only references do not set a child's/unknown patient's individual period.
TAPERS={'dulox-taper-limit','esc-taper-limit','fluvox-taper-limit','ser-taper-limit','venla-xr-taper-limit'}
taper_rows=[]
for rid in TAPERS:
 ck('five reference cards require only identified source form',CON[rid]['required_inputs']==['form'],rid)
 for c in CASES.values():
  if c['rule_id']!=rid:continue
  e=c['expected'];g=c['given']
  if e.get('adult_source_reference_only'):
   ck('adult source reference no individual interval/calendar',e.get('individual_duration_weeks') is None and e.get('individual_taper_schedule') is None and not e.get('schedule') and e.get('total_daily_dose_mg') is None and e.get('clinical_clearance') is False,c['case_id'])
   age=g.get('age');adult=type(age) in [int,float] and age>=18
   ck('population known only if actually adult',e.get('population_applicability')=='adult_source_population' if adult else e.get('population_applicability') in ['not_assessed','pediatric_plan_not_established','pediatric_withdrawal_plan_not_established'],c['case_id'],[age,e.get('population_applicability')])
   taper_rows.append(dict(case_id=c['case_id'],rule_id=rid,age=age,population=e.get('population_applicability'),source_constraint=e.get('duration_constraint')))
for c in CASES.values():
 scope=unselected_example_scope(RULES[c['rule_id']],c)
 if scope:
  e=c['expected'];g=c['given'];ck('known false/non40 selection only gives no-calendar',not e.get('complete_calendar') and not e.get('target_start_allowed') and e.get('total_daily_dose_mg') is None and not e.get('schedule'),c['case_id'])
  if g['example_selected'] is False:control('unknown example selection',c,unselected_example_scope,lambda z:z['given'].update(example_selected='unknown'))
  else:control('unknown current dose cannot disprove selected40',c,unselected_example_scope,lambda z:z['given'].update(current_dose='unknown'))

unknown_rows=[]
for c in CASES.values():
 e=c['expected'];sc=e.get('source_condition',{});g=c['given'];k=sc.get('input')
 if e.get('clarification_only'):
  ck('unknown source condition is clarification, not positive action',k in g and g[k] in [None,'unknown','not_assessed'] and k in e['missing_fields'] and k in e['unassessed_context'] and not e.get('source_actions') and 'clarification' in e['terminal_source_certificate']['scope'].lower(),c['case_id']);unknown_rows.append(c['case_id'])
save('terminal_scope_checks.json',dict(snapshot=SHA,certificate_cases=len(cert_cases),old_unique_scopes=len(expected_lists),assertions=len(checked),errors=errors,checks=checked,
 independent_scope='Same-SHA own primary norm reuse + each finite current certificate cause/source/actor/form/clock/arithmetic and supplied facts. Functions used only to test literal finite scope acceptance; no clinical selector/app execution.'))
save('terminal_scope_registry.json',records)
save('terminal_counterchecks.json',dict(controls=controls,all_rejected=all(x['rejected'] for x in controls),count=len(controls),medical_engine_executed=False))
save('source_reference_checks.json',dict(taper_rows=taper_rows,clarification_cases=unknown_rows,scope='Source-only adult references, known nonselected example and unknown event are bounded, not individual treatment.'))
print(json.dumps(dict(certificates=len(cert_cases),checks=len(checked),controls=len(controls),errors=len(errors),first_errors=errors[:12]),ensure_ascii=False))
