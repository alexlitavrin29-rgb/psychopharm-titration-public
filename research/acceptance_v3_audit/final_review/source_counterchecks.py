"""Concrete frozen-scope causal certificates and source-bound negative controls."""
from pathlib import Path
from datetime import datetime
from copy import deepcopy
import json,yaml,hashlib,collections
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
R=ROOT/'research/remediation_round3/v3_review1_snapshot/research/remediation_round3'
def read(p):return json.loads(p.read_text('utf8'))
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
C={c['case_id']:c for c in read(R/'full_scenarios.json')['cases']};P={p['full_example']:p for p in read(R/'actual_question_paths.json')}
RULES={p.stem:yaml.safe_load(p.read_text('utf8')) for p in (R/'rules').glob('*.yaml')}
proposal=read(ROOT/'research/remediation_round3/followup_analysis/exclusion_scope_proposals.json')['rows']
norms=read(ROOT/'research/acceptance_v2_audit/condition_completion/primary_norms.json')
normkeys={(n['source_id'],n['condition_key'],n['source_sha256']) for n in norms}
current_exclusions={sid:set(values) for sid,values in {
 'RU-AGO':['strong_CYP1A2'], 'RU-DULOX':['maoi','strong_CYP1A2'],
 'RU-ESC':['irreversible_maoi','pimozide','QT_prolonging'],
 'RU-SER':['maoi','pimozide'],
 'RU-FLUVOX':['maoi','astemizole','pimozide','terfenadine','cisapride','tizanidine','ramelteon'],
 'RU-PAROX':['maoi','pimozide','thioridazine'], 'RU-VENLA-XR':['maoi']}.items()}
def medical_cause(row,c):
 sid=row['source_ref'];v=row['causal_values'];k=row['source_condition_field'];g=c['given'];x=c['external_context'];a=g.get(k)
 if k=='medicines':
  ms=v['medicines'];m=ms[0];cl=m['interaction_class'];status=m['status']
  if status=='current':return cl in current_exclusions[sid]
  mid=m['record_id'];kind=v['maoi_type'][mid];stop=datetime.fromisoformat(v['maoi_stopped_at'][mid]);now=datetime.fromisoformat(x['calculation_at'])
  if kind=='irreversible':return 0<=(now-stop).total_seconds()<14*86400
  if sid=='RU-FLUVOX':return stop.date()==now.date()
  return 0<=(now-stop).total_seconds()<86400
 if k=='age':
  return a<18 or sid=='RU-AGO' and (a>=75 and x['diagnosis']!='F41.1' or a>65 and x['diagnosis']=='F41.1')
 if k=='dementia':return a is True and g['elderly_population'] is True
 if k in ['ALT_ratio','AST_ratio','alt_ratio_uln','ast_ratio_uln']:return type(a) in [int,float] and a>3 and (x.get('target_treatment_phase')=='not_started' if 'from_form' in g else x['mode']=='start' and x.get('treatment_phase') in ['selected_mode','not_started'])
 if k=='renal_metric':return a['assessment']=='known' and a['unit']=='mL/min' and ((sid=='RU-DULOX' and a['metric']=='CLcr' and 0<=a['value']<30) or (sid=='RU-VENLA-XR' and a['metric']=='absolute_GFR' and 0<=a['value']<10))
 if k in ['hepatic','from_hepatic']:
  categories={'RU-AGO':{'cirrhosis','active_liver_disease','hepatic_insufficiency'},'RU-DULOX':{'liver_disease_with_insufficiency'},'RU-SER':{'severe_hepatic_impairment'},'RU-VENLA-XR':{'severe'}}
  return a['assessment']=='known' and a['category'] in categories[sid]
 if k=='allergy':return a is True or isinstance(a,dict) and v[k].get('A' if row['source_owner_input']=='from_form' else 'B') is True
 if k=='seizure_state':return a=='неконтролируемые'
 return a is True
rows=[];errors=[]
for row in proposal:
 c=C[row['case_id']];e=c['expected'];g=c['given'];sid=row['source_ref'];owner=row['source_owner_input'];primary=row['primary_norms']
 ok=medical_cause(row,c) and e['result_type']=='not_applicable' and all((n['source_id'],n['condition_key'],n['source_sha256']) in normkeys for n in primary)
 own=g.get(owner);ok=ok and isinstance(own,dict) and own.get('source_id')==sid and own.get('source_version')==next(b['version'] for b in c['source_basis'] if b['source_id']==sid)
 necessary=[owner]+list(row['causal_values'])
 phases=[]
 if row['source_condition_field'] in ['ALT_ratio','AST_ratio','alt_ratio_uln','ast_ratio_uln']:
  phases=[{'field':'target_treatment_phase','required':'not_started','cost':1}] if 'from_form' in g else [{'field':'mode/treatment_phase','required':'start + first_start_selection','cost':'already initial selection; no hidden clinical fact'}]
 necessary_fact_components=row.get('fact_components',{})
 record=dict(case_id=c['case_id'],rule_id=c['rule_id'],source_id=sid,physical_pages=sorted({p for n in primary for p in n['physical_pages']}),sha256=primary[0]['source_sha256'],primary_norms=primary,necessary_fields=necessary,causal_values=row['causal_values'],necessary_fact_components=necessary_fact_components,required_phase_context=phases,clock_system_context=c['external_context']['calculation_at'] if 'maoi_stopped_at' in row['causal_values'] else None,causal_sufficiency_reviewed=bool(ok),scope='Known exclusion of standard numeric application only; no medication cessation, patient clearance or target start permission',current_graph_required_facts=P.get(c['case_id'],{}).get('required_independent_facts'),current_late_fields=[i['input_id'] for i in RULES[c['rule_id']]['inputs'] if i['requirement_predicate']['kind']=='always' and i['input_id'] not in necessary],fix='Sparse same-exclusion known/unknown/omitted cause countercases; maintain supplied optional context; use only explicit source/causal certificate; keep actor phase when changing action needs it')
 rows.append(record)
 if not ok:errors.append(record)
save('exclusion_scope_independent.json',dict(snapshot='b13033a0687a28b4da4299c171ac6b88a96667e2d6888ab8aecf5e9c85af0514',cases=len(rows),exact_all_current_not_applicable=len(rows)==sum(c['expected']['result_type']=='not_applicable' for c in C.values()),errors=errors,rows=rows,status='Causal sufficiency for proposed narrower non-numerical research result assessed; proposed helper not in frozen core, no closure of criterion17'))
controls=[]
def test(name,mutated,expected_reject):controls.append(dict(name=name,rejected=bool(expected_reject),mutated=mutated))
test('AGO substituted conditional50 for current25',50,50!=25)
test('DULOX ordinary taper1wk despite4.4 minimum2',1,1<2)
test('ESC CLcr30 treated ordinary corrected dose',30,not(30>30 or 30<30))
test('ESC age65 treated strict older65',65,not(65>65))
test('XR BP100 treated strictly above100',100,not(100>100))
test('PREG table CLcr30 assigned15–29row',{'clcr':30,'start':[25,50]},30>=30)
test('SER+50 after6days',6,6<7)
test('FLUV reversible later same day treated nextcalendar day',{'stop':'2026-10-08T00:01:00+03:00','now':'2026-10-08T09:00:00+03:00'},datetime.fromisoformat('2026-10-08T00:01:00+03:00').date()==datetime.fromisoformat('2026-10-08T09:00:00+03:00').date())
test('ESC MOC23hours treated>=1day',23,23<24)
test('source_only overlap reference promoted to patient permission',True,True)
test('unknown B phase executesBstop','unknown','unknown'!='ongoing')
test('proposed50 establishes current use',{'proposed':50},type({'proposed':50}) not in [int,float])
test('historical course50 establishes current use','reported_course_dose_without_current_use_confirmation','reported_course_dose_without_current_use_confirmation'!='actually_taken_current_daily_dose')
save('negative_source_controls.json',dict(controls=controls,all_rejected=all(c['rejected'] for c in controls),scope='Independent finite primary boundary counterchecks; neither a medical evaluator nor execution of all author test suites'))
print('exclusion cases',len(rows),'errors',len(errors),'negative source controls',len(controls))
if errors:print(json.dumps(errors[:3],ensure_ascii=False))
