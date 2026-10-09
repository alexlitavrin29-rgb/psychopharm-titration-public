"""Independent linkage and literal/actor checks of all used expected conditions.
No medical selector is executed; unknowns and unlinked causes are explicit.
"""
from pathlib import Path
import json,yaml,collections,sys
sys.dont_write_bytecode=True

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];R=ROOT/'research/remediation_round3'
def read(p):return json.loads(p.read_text('utf8'))
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
F=read(R/'full_scenarios.json')['cases'];S=read(R/'sources.json');C=yaml.safe_load((R/'result_contracts.yaml').read_text('utf8'))['rules'];RS={p.stem:yaml.safe_load(p.read_text('utf8')) for p in (R/'rules').glob('*.yaml')}
NORMS={(n['source_id'],n['condition_key']):{k:v for k,v in n.items() if k not in ['source_sha256','source_file','status']} for n in read(ROOT/'research/acceptance_v2_audit/condition_completion/primary_norms.json')}
def norms(sources,keys):
 out=[]
 for s in sources:
  for k in keys:
   n=NORMS.get((s,k))
   if n:out.append(dict(**n,source_sha256=S[s]['document_fingerprint']['sha256'],source_file='research/'+S[s]['local_file']))
 return out
def val(g,f):
 for k in f.split('.'):
  if not isinstance(g,dict):return None
  g=g.get(k)
 return g
AL={'transaminases':['ALT_ratio','AST_ratio','alt_ratio_uln','ast_ratio_uln'],'adult_indication_required':['age'],'indication_specific_age':['age'],'hepatic_insufficiency':['hepatic'],'cirrhosis':['hepatic'],'active_liver_disease':['hepatic'],'liver_disease_with_insufficiency':['hepatic'],'hepatic_impairment':['hepatic'],'severe_hepatic_impairment':['hepatic'],'mild':['hepatic'],'moderate':['hepatic'],'severe':['hepatic'],'renal_boundary':['renal_metric'],'source_age_branch':['age'],'CLcr_source_caution':['renal_metric'],'CLcr_exact30_source_gap':['renal_metric'],'hepatic_special_or_supervision':['hepatic'],'combined_modifiers_not_published':['age','hepatic','known_cyp2c19'],'redirect_to_source_special_branch_or_joint_modifiers':['age','hepatic','known_cyp2c19'],'current_maoi_standard_branch':['maoi'],'MAOI_interval':['maoi','maoi_stopped_at'],'moclobemide_at_least_one_day':['reversible_MAO_A'],'target_liver_test':['alt_ratio_uln','ast_ratio_uln'],'blood_pressure_review':['diastolic_BP'],'source_diastolic_BP_above100_stop':['diastolic_BP'],'контролируемые':['seizure_state'],'неконтролируемые':['seizure_state'],'новые приступы':['seizure_state']}
ACTION_KEYS={
 ('RU-PREG','immediately_discontinue_pregabalin'):['angioedema','severe_skin_reaction'],('RU-PREG','consider_alternative_treatment_if_needed'):['severe_skin_reaction'],
 ('RU-SER','discontinue_current_A'):['mania_symptoms'],('RU-AGO','discontinue_B_only_if_already_administered_otherwise_do_not_start'):['mania_symptoms'],
 ('RU-VENLA-XR','discontinue_selected_medication'):['diastolic_BP','current_allergic_reaction'],('RU-ESC','discontinue_ESC'):['arrhythmia_signs'],('RU-ESC','obtain_ECG'):['arrhythmia_signs','coronary_disease'],
 ('RU-ESC','immediately_discontinue_SSRI_and_current_serotonergic_drugs'):['serotonin_syndrome_signs','target_serotonin_syndrome_signs'],('RU-ESC','start_symptomatic_treatment_by_clinician'):['serotonin_syndrome_signs','target_serotonin_syndrome_signs'],('RU-ESC','discontinue_current_A'):['mania_symptoms'],
 ('RU-FLUVOX','discontinue_selected_medication'):['serotonin_syndrome_signs','new_or_increased_seizures','mania_symptoms','liver_injury_signs'],('RU-FLUVOX','start_symptomatic_treatment_by_clinician'):['serotonin_syndrome_signs'],
 ('RU-PHEN','discontinue_selected_medication'):['unusual_reactions'],('RU-PAROX','discontinue_selected_medication'):['serotonin_syndrome_signs','new_seizures','seizure_state'],('RU-PAROX','start_supportive_symptomatic_treatment_by_clinician'):['serotonin_syndrome_signs'],
 ('RU-ESC','discontinue_selected_medication'):['seizure_state','target_seizure_state','mania_symptoms','target_arrhythmia_signs','arrhythmia_signs','serotonin_syndrome_signs','target_serotonin_syndrome_signs'],('RU-SER','discontinue_selected_medication'):['new_seizures','target_new_seizures','mania_symptoms'],
 ('RU-SER','consider_discontinuation_of_sertraline'):['symptomatic_hyponatremia','target_symptomatic_hyponatremia'],('RU-SER','provide_appropriate_medical_care'):['symptomatic_hyponatremia','target_symptomatic_hyponatremia'],
 ('RU-PREG','consider_discontinuation_of_pregabalin'):['current_suicidal_thoughts_or_behavior'],('RU-PREG','consider_appropriate_treatment_and_seek_medical_care'):['current_suicidal_thoughts_or_behavior'],
 ('RU-DULOX','consider_dose_adjustment_or_gradual_discontinuation'):['persistent_BP_increase'],('RU-VENLA-XR','consider_dose_reduction_or_discontinuation_according_to_symptom_severity'):['suspected_serotonin_syndrome']}
ACTION_KEYS.update({('RU-AGO','immediately_discontinue_agomelatine'):['liver_injury_signs'],('RU-AGO','monitor_liver_function_until_normalization'):['liver_injury_signs']})
rows=[];errors=[];unlinked=[]
def record(c,kind,literal,ns,tests):
 row=dict(case_id=c['case_id'],rule_id=c['rule_id'],kind=kind,literal=literal,primary_norms=ns,given=c['given'],external_context=c['external_context'],medical_expected=c['expected'],checks=tests,status='PRIMARY_NORM_LINKED_AND_LITERAL_CHECKED' if ns and all(t['pass'] for t in tests) else ('UNREVIEWED_NO_EXACT_NORM' if not ns else 'DEFECT'))
 rows.append(row)
 if not ns:unlinked.append(dict(case_id=c['case_id'],kind=kind,literal=literal))
 if any(not t['pass'] for t in tests):errors.append(row)
def test(name,b):return dict(check=name,**{'pass':bool(b)})
for c in F:
 g=c['given'];e=c['expected'];rid=c['rule_id'];sources=[x['source_id'] for x in c['source_basis'] if x['source_id'].startswith('RU-')];mode=RS[rid]['identity']['mode']
 sc=e.get('source_condition')
 if sc:
  s=sc.get('source_ref');f=sc.get('input');ks=[f] if f else []
  if not f:
   if 'metric' in sc or any('renal' in k or 'CLcr' in str(v) for k,v in sc.items()):ks=['renal_metric']
   elif any('hepatic' in k for k in sc):ks=['hepatic']
   elif sc.get('source_ref')=='RU-AGO':ks=['alt_ratio_uln','ast_ratio_uln']
   else:ks=['age','hepatic','known_cyp2c19']
  if f=='medicines':ks += [m.get('interaction_class') for m in g.get('medicines',[]) if isinstance(m,dict)]
  ns=norms([s] if s else sources,ks);tests=[test('no numeric dose without individual branch',e['result_type'] in ['exact','selected_source_example'] or e.get('total_daily_dose_mg') is None)]
  if f:
   v=val(g,f);op=sc.get('operator');want=sc.get('value')
   if sc.get('field') and isinstance(v,dict):v=v.get(sc['field'])
   if op=='category_equals' and isinstance(v,dict):v=v.get('category')
   if op in ['category_equals','equals','field_equals']:tests.append(test('literal equals complete given',v==want))
   if op in ['>','greater_than']:tests.append(test('strict source greater boundary',isinstance(v,(int,float)) and v>want))
   if not op and isinstance(v,bool) and f!='effective_contraception':tests.append(test('current source event actually positive',v is True))
   if f=='effective_contraception' and v is False:tests.append(test('negative required contraception not an automatic dose',e['result_type'] not in ['exact','selected_source_example']))
  record(c,'source_condition',sc,ns,tests)
 for reason in e.get('reason_ids',[]):
  key=reason.removeprefix('source_caution_');ks=AL.get(key,[key]);
  if key.endswith('.release'):ks=[key.split('.')[0]]
  if key in ['from_hepatic']:ks=['from_hepatic']
  ns=norms(sources,ks)
  tests=[test('reason not granted a fabricated coefficient',e.get('automatic_numeric_modifier') is None),test('reason does not grant clinical clearance',e.get('clinical_clearance') is False)]
  if isinstance(g.get(key),bool):tests.append(test('positive risk reason has complete positive fact',g[key] is True))
  if key in ['контролируемые','неконтролируемые','новые приступы']:tests.append(test('seizure category matches given',g.get('seizure_state')==key))
  record(c,'reason',reason,ns,tests)
 for action in e.get('source_actions',[]):
  s=action.get('source_ref');keys=ACTION_KEYS.get((s,action.get('action')),[])
  selected=[k for k in keys if g.get(k) is True or k==e.get('source_condition',{}).get('input') or (k=='seizure_state' and g.get(k) in ['новые приступы','первичные/участившиеся приступы']) or (k=='diastolic_BP' and isinstance(g.get(k),(int,float)) and g[k]>100)]
  ns=norms([s],selected or keys)
  record(c,'source_action',action,ns,[test('action own source identified',s in sources),test('action no unconditional future numeric calendar',e.get('unconditional_future_stages') is not True)])
save('used_expected_condition_checks.json',dict(snapshot='27ef14e77185b7b104d43199664a5b1ca42b73dd8b09f921ee539e97fae971f8',cases=len(F),used_cause_action_occurrences=len(rows),errors=errors,unlinked=unlinked,rows=rows,limit='All used cause/action occurrences are inventoried; source linkage and literal/actor properties do not by themselves execute or prove a selector. Primary semantic norms and source actions were independently read. Categorical absence of full positives is separately listed.'))
print('occurrences',len(rows),'errors',len(errors),'unlinked',len(unlinked))
print('unlinked literals',collections.Counter(str(x['literal']) for x in unlinked));print('errors',[(x['case_id'],x['literal'],x['checks']) for x in errors[:10]])
