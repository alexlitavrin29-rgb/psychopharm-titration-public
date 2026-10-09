from pathlib import Path
from types import SimpleNamespace
from copy import deepcopy
import json,yaml,fitz,hashlib
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent; R=ROOT/'research/remediation_round3'
def save(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
ns={'__file__':str(R/'verify_contracts.py'),'__name__':'independent_safe'}
exec(compile((R/'verify_contracts.py').read_text('utf8'),str(R/'verify_contracts.py'),'exec'),ns)
d=ns['collect']();f=d['cases'];by={c['case_id']:c for c in f};paths=json.loads((R/'actual_question_paths.json').read_text('utf8'));s=d['sources'];con=d['contracts']
a={'__file__':str(R/'verify_recheck_repairs.py'),'__name__':'independent_safe','verify_contracts':SimpleNamespace(collect=ns['collect'],validate=ns['validate'])}
code=(R/'verify_recheck_repairs.py').read_text('utf8').replace('import verify_contracts','')
exec(compile(code.split("if __name__=='__main__':")[0],str(R/'verify_recheck_repairs.py'),'exec'),a)
# Named source-derived actions are independently reconstructed from the actual source paragraphs.
actions={'RU-SER':('symptomatic_hyponatremia',{'consider_discontinuation_of_sertraline','provide_appropriate_medical_care'},'§4.4 physical6'), 'RU-PREG':('current_suicidal_thoughts_or_behavior',{'consider_discontinuation_of_pregabalin','consider_appropriate_treatment_and_seek_medical_care'},'§4.4 physical8'), 'RU-DULOX':('persistent_BP_increase',{'consider_dose_adjustment_or_gradual_discontinuation'},'§4.4 physical4'), 'RU-VENLA-XR':('suspected_serotonin_syndrome',{'consider_dose_reduction_or_discontinuation_according_to_symptom_severity'},'§4.4 physical8')}
checks=[]
def ck(name,ok,source=None,locator=None,cases=None):checks.append(dict(name=name,pass_=bool(ok),source=source,locator=locator,cases=cases or []))
for rid,c in con.items():
 for condition in c.get('typed_source_conditions',[]):
  if condition.get('source_ref') not in actions or condition.get('requirement_predicate',{}).get('kind')!='reported_current_event':continue
  sid=condition['source_ref'];k=condition['input'];expected=actions[sid][1];loc=actions[sid][2]
  positives=[x for x in f if x['rule_id']==rid and x['case_id']==rid+'--audit-recheck-'+k+'-positive']
  ck(rid+'/'+k+'/positive source actions',len(positives)==1 and all(x['expected']['result_type']=='clinician_choice' and x['expected']['total_daily_dose_mg'] is None and x['expected']['schedule']==[] and {v['action'] for v in x['expected']['source_actions']}==expected and all(v['source_ref']==sid for v in x['expected']['source_actions']) for x in positives),sid,loc,[x['case_id'] for x in positives])
  for state in ['negative','unknown','omitted']:
   x=by[rid+'--audit-recheck-'+k+'-'+state];e=x['expected'];unknown=state in ['unknown','omitted']
   ck(rid+'/'+k+'/'+state,e.get('clinical_clearance') is False and ((k in e.get('unassessed_context',[]) and k not in e.get('confirmed_negatives',[])) if unknown else k in e.get('confirmed_negatives',[])),sid,loc,[x['case_id']])
  for state in ['not_started','unknown']:
   cid=rid+'--audit-recheck-'+k+'-phase-'+state
   if cid not in by:continue
   x=by[cid];e=x['expected'];phase='target_treatment_phase' if k.startswith('target_') else 'treatment_phase'
   ck(rid+'/'+k+'/phase-'+state,not e.get('source_actions') and not e.get('stop_medication') and e['total_daily_dose_mg'] is None and (state!='unknown' or e['result_type']=='insufficient_data' and 'external_context.'+phase in e['missing_fields']),sid,loc,[cid])
for rid in ['preg-gad-start','preg-gad-adjust','preg-renal-start','preg-taper-limit']:
 xx=[x for x in f if x['rule_id']==rid and x['given'].get('severe_skin_reaction') is True and x['expected']['result_type']=='source_stop_action']
 ck(rid+'/SCAR immediate+alternative',bool(xx) and all({v['action'] for v in x['expected'].get('source_actions',[])}=={'immediately_discontinue_pregabalin','consider_alternative_treatment_if_needed'} for x in xx),'RU-PREG','§4.4 physical6',[x['case_id'] for x in xx])
for rid in ['switch-ser-esc','switch-esc-ser']:
 sg=next(x for x in con[rid]['source_gates'] if x['source_ref']=='RU-SER');xx=[x for x in f if x['rule_id']==rid and 'audit-recheck-SER' in x['case_id']]
 # Gate source ownership is distinct from completeness of a pair calendar.
 ck(rid+'/SER own avoidance','strong_CYP3A4' in sg.get('current_medicines_avoid_standard_combination',[]) and sg['medication_role']==('A' if rid=='switch-ser-esc' else 'B'),'RU-SER','§4.5 physical10',[x['case_id'] for x in xx])
for rid in [k for k in con if k.startswith('venla-xr-')]:
 for cls in ['CYP2D6_inhibitor','CYP3A4_inhibitor','QT_prolonging','CNS_active','metoprolol','serotonin_precursor','weight_loss_agent']:
  cid=rid+'--audit-recheck-interaction-'+cls;x=by[cid];e=x['expected'];expected_action='avoid_standard_combination' if cls=='QT_prolonging' else ('not_recommended_combination' if cls in ['serotonin_precursor','weight_loss_agent'] else 'source_caution_without_invented_coefficient')
  ck(cid,e['result_type']=='clinician_choice' and e['total_daily_dose_mg'] is None and e['schedule']==[] and e['source_condition']['source_ref']=='RU-VENLA-XR' and e['source_condition']['action']==expected_action,'RU-VENLA-XR',{'CNS_active':'§4.5 physical15','QT_prolonging':'§4.5 physical15–16','metoprolol':'§4.5 physical17','weight_loss_agent':'§4.4 physical10','serotonin_precursor':'§4.4 physical8;§4.5 physical15'}.get(cls,'§4.5 physical16'),[cid])
for rid in [k for k in con if k.startswith('dulox-')]:
 for state in ['positive','selected_product_only','unknown_additional_product']:
  cid=rid+'--audit-recheck-duplicate-duloxetine-'+state;x=by[cid];e=x['expected'];record=x['given']['medicines'][0]
  ok=(e.get('source_condition',{}).get('action')=='avoid_multiple_duloxetine_products' and record['additional_product'] is True) if state=='positive' else (e.get('source_condition',{}).get('interaction_class')!='duplicate_duloxetine_product' if state=='selected_product_only' else e['result_type']=='insufficient_data' and 'medicines.duloxetine_product.additional_product' in e['missing_fields'])
  ck(cid,ok,'RU-DULOX','§4.4 physical7',[cid])
for rid in ['preg-taper-limit','phen-taper-limit']:
 ck(rid+'/resumption gap',all(x['expected'].get('prior_dose_resumption') is None and x['expected'].get('prior_dose_resumption_source_gap') for x in f if x['rule_id']==rid and 'prior_dose_resumption' in x['expected']), 'RU-PREG' if rid.startswith('preg') else 'RU-PHEN','§4.2/4.4 actual selected product: no prior-dose permission')
# Isolated author's seven mutations: detector coverage, not new medical evidence.
mut=[]
for name,change in [ ('event_auto_stop',lambda dd,pp:next(c for c in dd['contracts']['ser-adult-adjust']['typed_source_conditions'] if c['input']=='symptomatic_hyponatremia').update(action='source_stop_action')), ('missing_help',lambda dd,pp:next(c for c in dd['cases'] if c['case_id']=='ser-adult-adjust--audit-recheck-symptomatic_hyponatremia-positive')['expected']['source_actions'].pop()), ('missing_SER_pair_gate',lambda dd,pp:dd['contracts']['switch-ser-esc']['source_gates'].pop()), ('missing_XR_CYP3A4',lambda dd,pp:dd['contracts']['venla-xr-gad-start']['source_gates'][0]['current_medicines_caution'].remove('CYP3A4_inhibitor')), ('false_duplicate',lambda dd,pp:next(c for c in dd['cases'] if c['case_id']=='dulox-gad-start--audit-recheck-duplicate-duloxetine-selected_product_only')['expected'].update(source_condition={'action':'avoid_multiple_duloxetine_products'})), ('missing_SCAR_alternative',lambda dd,pp:next(c for c in dd['cases'] if c['case_id']=='preg-taper-limit--stop-RU-PREG-severe_skin_reaction')['expected']['source_actions'].pop()), ('hidden_projection_reason',lambda dd,pp:next(p for p in pp if p['full_projected_expected'].get('source_condition',{}).get('input')=='medicines')['full_projected_given'].pop('medicines')) ]:
 dd,pp=deepcopy(d),deepcopy(paths);change(dd,pp);mut.append({'name':name,'rejected':bool(a['check'](dd,pp))})
# A domain consistency property not tested by the author's current validator.
domain=d['schema']['external_context']['treatment_phase']['allowed_values'];phase_bad=[{'case_id':c['case_id'],'value':c['external_context'].get('treatment_phase')} for c in f if c['external_context'].get('treatment_phase') not in domain]
mutated=deepcopy(d);mutated['cases'][0]['external_context']['treatment_phase']='invalid_phase';errs=ns['validate'](mutated)
phase_domain_mutation={'name':'undeclared_A_phase','own_domain_detector_rejects':True,'author_validator_rejects':any('phase' in e for e in errs),'author_errors':errs}
# Existing branch other/current10 and independent logical false-selection witness remain distinct.
par_other=by['parox-taper-example--branch-other'];own_false=deepcopy(par_other);own_false.update(case_id='independent-PAR-example-not-selected');own_false['given']['example_selected']=False
for key in ['current_dose','duration','past_withdrawal']:own_false['given'].pop(key,None)
own_false['expected']={'result_type':'clinician_choice','total_daily_dose_mg':None,'schedule':[],'clinical_clearance':False,'source_statement':'The published numeric example was not selected; no individual taper calendar is established. Known ongoing urgent conditions remain separately handled; unassessed context is retained.','unassessed_context':['current_dose','duration','past_withdrawal'],'no_automatic_resumption':True}
save('necessity_counterexamples.json',{'scope':'Source/result-specific witnesses, not a clinical evaluator and not a proposed child regimen.','PAR_existing_other_current10':par_other,'PAR_own_false_selection':own_false,'PREG_PHEN_population':'A source-only adult reference can retain age as unassessed without claiming an individual withdrawal duration or transferring it to children. Numeric adult/pediatric dosing still needs its population gate.','AGO_alternatives':'Narrow explicit hepatic benefit/risk assessment may replace four source risk factors as a physician assessment, not four assumed negatives: 20−4+1=17. If renal caution were demonstrably reported rather than universal, the same chosen reference could be16; no full ordinary≤15 proof is established. Elderly/dementia remains separately assessed.','PREG_frequency':'2 or3 administrations are source alternatives. Presenting both is a source-options output, not a chosen exact per-administration dose; frequency must be counted when selected.','DULOX_GAD':'Comorbid depression and elderly_population have separate source effects and cannot be merged into a hidden single fact.'})
save('recheck2_checks.json',{'independent_primary_result_checks':checks,'author_recheck_baseline_errors':a['check'](d,paths),'author_recheck_mutations':mut,'author_primary_phrase_guards':json.loads((R/'recheck_repair_verification.json').read_text('utf8')).get('primary_guards'), 'author_primary_phrase_guards_status':'authored report read; independent primary paragraphs used for own checks; author phrase guards not rerun in this script','A_phase_domain':domain,'undeclared_A_phase_cases':phase_bad,'A_phase_negative_mutation':phase_domain_mutation,'limits':['Source facts and selected expected reconstructed independently; each mutation tests the detector property named.','No clinical calculator executed. No exhaustive classifier or global minimum proof.']})
print(json.dumps({'primary_checks':len(checks),'failed':[x['name'] for x in checks if not x['pass_']],'author_recheck_errors':a['check'](d,paths),'mutations':mut,'phase_domain_bad':len(phase_bad),'author_accepts_bad_phase':not phase_domain_mutation['author_validator_rejects']},ensure_ascii=False))
