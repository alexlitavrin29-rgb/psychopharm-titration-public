"""Index every extracted occurrence, without assigning automatic VERIFIED statuses."""
from pathlib import Path
import json,yaml,collections,sys,re
sys.dont_write_bytecode=True
from primary_norms import NORMS
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];R=ROOT/'research/remediation_round3'
def read(p):return json.loads(p.read_text('utf8'))
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
O=read(OUT/'used_condition_occurrences.json');I=read(OUT/'scoped_input_conditions.json');L=read(OUT/'literal_contract_conditions.json');N=read(OUT/'numerical_conditions.json');G=read(OUT/'medical_prose_review.json');F=read(R/'full_scenarios.json')['cases'];P=read(OUT/'used_expected_condition_checks.json');A=read(OUT/'all_expected_check_results.json');S=read(R/'sources.json');RS={p.stem:yaml.safe_load(p.read_text('utf8')) for p in (R/'rules').glob('*.yaml')}
im={x['occurrence_path']:x for x in I};lm={x['raw_occurrence']:x for x in L};nm={(x['rule_id'],x['parameter']['parameter_id']):x for x in N};gm={o['id']:x for x in G for o in x['occurrences']};bycase={x['case_id']:x for x in F};checked=collections.defaultdict(list)
for x in A['rows']+P['rows']:checked[x['case_id']].append(x)
def source_norms(sources,keys):
 out=[]
 for s in sources:
  for k in keys:
   n=NORMS.get((s,k))
   if n:out.append(dict(**n,source_sha256=S[s]['document_fingerprint']['sha256'],source_file='research/'+S[s]['local_file']))
 return out
def parents(r,path):
 cur=r;out=[r]
 for k in path:
  try:cur=cur[int(k)] if isinstance(cur,list) else cur[k]
  except (KeyError,ValueError,TypeError,IndexError):break
  out.append(cur)
 return out
def parent_norms(o):
 path=o['path'].split('.yaml/',1)[-1].split('/');chain=parents(RS[o['rule_id']],path);sources=o['source_refs'];keys=[]
 for p in reversed(chain):
  if isinstance(p,dict):
   if p.get('source_ref'):sources=[p['source_ref']]
   keys=[p.get('input'),p.get('required_fact')]+p.get('fields',[])
   if any(keys):break
  keys=[]
 keys=[k for k in keys if k]
 if o['kind'].startswith('source_gate:'):
  keys=['medicines']
 if isinstance(o['claim'],str):
  keys+= [o['claim']] if any((s,o['claim']) in NORMS for s in sources) else []
  if o['claim']=='Гиперчувствительность':keys+=['allergy']
  if o['claim']=='known_cyp2c19 = известная слабая активность':keys+=['known_cyp2c19']
  if o['claim']=='hepatic = нарушена':keys+=['hepatic']
  if o['rule_id']=='parox-panic-kr' and 'ИМАО, тиоридазин, пимозид' in o['claim']:keys+=['maoi','thioridazine','pimozide']
 pathtext='/'.join(path)
 if 'applicability/pregnancy' in pathtext:keys+=['pregnancy']
 if 'applicability/lactation' in pathtext:keys+=['lactation']
 if 'applicability/population_description' in pathtext:keys+=['age']
 if 'applicability/renal_constraints' in pathtext:keys+=['renal_metric','renal','renal_state','clcr']
 if 'applicability/hepatic_constraints' in pathtext:keys+=['hepatic','ALT_ratio','AST_ratio']
 if '/age_constraints/' in pathtext:keys+=['age']
 if 'maoi' in pathtext:keys+=['maoi','maoi_type','maoi_stopped_at','last_dose_at']
 if 'liver_monitoring' in pathtext:keys+=['ALT_ratio','AST_ratio','transaminases_rising']
 if any(z in pathtext for z in ['formulation','form_split']):keys+=['form']
 if 'panic_discontinuation_context' in pathtext:sources=['RU-PANIC'];keys=['panic_discontinuation_context']
 if 'duration_constraint' in pathtext:keys+=['duration','current_withdrawal','withdrawal_severity']
 if o['rule_id']=='ago-stop' and pathtext=='logic/actions/0':keys+=['current_dose']
 if o['rule_id']=='dulox-taper-limit' and 'current_taper_texts' in pathtext:keys+=['duration']
 if '/schedule/' in pathtext:keys+=['current_dose','frequency','time_since_last_change','example_selected']
 if o['rule_id']=='preg-renal-start' and pathtext.startswith('logic/actions/'):keys+=['clcr']
 return source_norms(sources,keys)
index=[];unmapped=[]
for o in O:
 x=dict(occurrence_id=o['occurrence_id'],rule_id=o['rule_id'],kind=o['kind'],path=o['path'],claim=o['claim'],review_status=None,evidence_links=[],primary_norms=[],scope=o['scope'])
 if o['kind']=='input':
  z=im[o['path']];x.update(review_status=z['primary_status'],primary_norms=z['primary_norms'],evidence_links=['scoped_input_conditions.json#'+z['record_id']],open_issue=z['transfer_status'] if z['transfer_status'].startswith('DEFECT') else None)
 elif o['kind']=='clinical_parameter':
  z=nm[(o['rule_id'],o['claim']['parameter_id'])];x.update(review_status=z['primary_status'],evidence_links=['numerical_conditions.json#'+z['record_id']],source_sha256=z['source_sha256'],physical_pages=z['physical_pages'])
 elif o['occurrence_id'] in lm:
  z=lm[o['occurrence_id']];x.update(review_status=z['status'],primary_norms=[z['primary_norm']] if z['primary_norm'] else [],expected_coverage=z['expected_coverage'],evidence_links=['literal_contract_conditions.json#'+z['record_id']])
 elif o['occurrence_id'] in gm:
  z=gm[o['occurrence_id']];x.update(review_status=z['review_status'],primary_norms=z['primary_norms'],evidence_links=['medical_prose_review.json#'+str(z['group_index'])],open_issue=z['open_issue'])
 elif o['kind'] in ['branch','full_expected_payload']:
  cases=o.get('all_case_ids',[o['representative_case']]);medical=[z for cid in cases for z in checked[cid] if 'primary_norms' in z]
  x.update(review_status='FULL_EXPECTED_STATIC_ORACLES_AND_USED_CAUSES_EXAMINED',representative_case=o['representative_case'],all_case_ids=cases,medical_condition_rows=[dict(case_id=z['case_id'],kind=z['kind'],literal=z['literal'],status=z['status']) for z in medical],evidence_links=['all_expected_check_results.json','used_expected_condition_checks.json','numerical_conditions.json'],review_limit='Every complete variant remains recorded. This review uses hand-written primary assertions and declared causes; it is not an executed dose selector, exhaustive medical combinations or proof that every required question is necessary.')
 elif o['kind'] in ['qualitative_population_scope','general_result_templates']:
  keys=['age','current_dose','time_since_last_change'];ns=source_norms(o['source_refs'],keys);x.update(review_status='BOUNDED_REFERENCE_OR_PUBLISHED_EXPRESSION_REVIEWED',primary_norms=ns,evidence_links=['recheck3/primary_expected_checks.json','all_expected_check_results.json'])
 else:
  ns=parent_norms(o)
  if ns:x.update(review_status='STRUCTURED_PARENT_PRIMARY_NORMS_LINKED',primary_norms=ns,evidence_links=['primary_norms.json','literal_contract_conditions.json','scoped_input_conditions.json'])
  else:
   t=o['claim'];path=o['path']
   technical=isinstance(t,str) and (not re.search('[А-Яа-яЁё]',t) or re.match(r'^(?:RU-[A-Z-]+ )?§',t) or any(z in path for z in ['representation','missing_data_behaviour','unsupported_case_behaviour','contraindicated_case_behaviour','individual_output_gate','evaluation_order','clinician_choices','clinician_decisions','warnings','mandatory_checks','rounding_or_formulation_rule','source_available','medication_inn']) or t.startswith(('All required','Версия копии','Применимость к указанному','Взрослые от 18','Последующие этапы','Неоценённое клиническое','Необходимость изменения','Не выдавать','КР определяет','insufficient_data','Назвать неприменимую','Не округлять','All required')))
   x.update(review_status='TECHNICAL_OR_REFERENCE_POINTER_NO_NEW_MEDICAL_NORM' if technical else 'UNREVIEWED_UNMAPPED_CLAIM',review_limit='Technical labels/source pointers/unknown-handling and source gaps are not counted as independently established medical norms. Related actual medical conditions remain in scoped/literal/numerical records.')
   if not technical:unmapped.append(x)
 index.append(x)
 if o['rule_id']=='esc-hepatic-start' and o['claim']=='hepatic = нарушена':x['open_issue']='CC05_LEGACY_PROSE_VALUE_USE_EXPLICIT_CHILD_PUGH_A_B_AND_SEPARATE_C'
# Values outside the string extractor: every non-null numeric/Boolean rule leaf is explicit.
def values(v,path):
 if isinstance(v,dict):
  for k,z in v.items():yield from values(z,path+'/'+str(k))
 elif isinstance(v,list):
  for k,z in enumerate(v):yield from values(z,path+'/'+str(k))
 elif isinstance(v,(bool,int,float)):yield path,v
extra=[]
for rid,r in RS.items():
 for kind in ['applicability','logic','output']:
  for path,value in values(r[kind],kind):
   if '/branches/' in path:continue
   o=dict(rule_id=rid,path='rules/'+rid+'.yaml/'+path,source_refs=[x['source_id'] for x in r['sources']],kind=kind+'_nonstring',claim=value);ns=parent_norms(o)
   extra.append(dict(**o,primary_norms=ns,review_status='PRIMARY_NORM_LINKED_USED_VALUE' if ns else 'TECHNICAL_FLAG_NO_NEW_MEDICAL_VALUE',review_limit='Values are source-scoped to the explicit norm and independently reviewed parameters/full expected. A true flag does not establish result-specific necessity.'))
save('complete_coverage_index.json',index);save('additional_used_values.json',extra);save('unmapped_claims.json',unmapped)
save('coverage_index_counts.json',dict(raw_occurrences=len(O),additional_nonstring_occurrences=len(extra),statuses=dict(collections.Counter(x['review_status'] for x in index)),unmapped_claims=len(unmapped),expected_case_variants=len(F),expected_payload_groups=sum(x['kind']=='full_expected_payload' for x in O),auto_verified_records=0))
print('index',len(index),'additional',len(extra),'unmapped',len(unmapped));print([(x['rule_id'],x['path'],x['claim']) for x in unmapped[:25]])
