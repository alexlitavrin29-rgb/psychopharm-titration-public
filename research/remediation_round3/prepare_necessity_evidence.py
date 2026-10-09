"""Expose per-question primary norms, actual result scopes and named witnesses."""
from pathlib import Path
import json,yaml,collections
O=Path(__file__).resolve().parent
def sj(name,value):(O/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
R={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')}
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'))['rules']
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))['cases'];P=json.loads((O/'actual_question_paths.json').read_text(encoding='utf-8'))
norm_file=O.parent/'acceptance_v2_audit/condition_completion/scoped_input_conditions.json'
N={(x['rule_id'],x['field']):x['primary_norms'] for x in json.loads(norm_file.read_text(encoding='utf-8'))}
rows=[];unmapped=[]
roles={
 'always':'Mandatory for the selected individual numeric/action branch: source identity, numeric operand, direct source applicability or required clinical action. See the named primary norm and reason; source-action/referral overrides below have their own sufficient facts.',
 'reported_context':'No universal prerequisite. Supplied positive/negative/unknown context is consumed and counted, absent context unassessed.',
 'reported_source_information':'Source reference/context only, not individual treatment admission. Supplied information counted; absent/unknown not a negative.',
 'reported_current_event':'Supplied current source event only. Its precise ongoing source actor must be known for a cessation action.',
 'outside_cessation_scope':'This start-applicability field is not a prerequisite for the selected cessation result; no new treatment clearance inferred.',
 'ongoing_selected_drug':'Current-treatment condition only when selected/A use is actually ongoing; prospective planned dose is not evidence.',
 'target_ongoing':'Current B condition only when B use is explicitly ongoing; A status cannot substitute for B.',
 'field_true':'Exact named controller must be true; other/unknown controller cannot establish that fact.',
 'all_equals':'All named values must match; no universal obligation outside this precise source-example branch.',
 'increase':'Only the listed selected increase/undecided actions; keep does not require a new increase interval.',
 'action_choice':'Only the listed undecided actions; no repeated clinical action selection after an explicit physician action.',
 'indication_action_choice':'Only the listed diagnosis/action states; other-diagnosis supplied context counted without borrowed mandatory prerequisite.',
 'ecg_if_cad':'Source pretreatment ECG only for known coronary disease; exact unknown controller remains unknown.',
 'correction_if_electrolytes':'Source pretreatment correction only for known electrolyte disturbance.',
 'maoi_record':'Each known MAOI record only. Unknown medication class must be clarified before requesting MAOI-specific type.',
 'stopped_maoi_record':'Each known stopped MAOI timestamp only; no generic inter-SSRI washout or clock for an empty history.'}
for rid,r in sorted(R.items()):
 cases=[c for c in F if c['rule_id']==rid];paths=[p for p in P if p['rule_id']==rid]
 for i in r['inputs']:
  k=i['input_id'];pred=i['requirement_predicate'];norms=N.get((rid,k),[])
  if not norms:unmapped.append([rid,k])
  missing=[c['case_id'] for c in cases if any(m.split('.')[0]==k for m in c['expected'].get('missing_fields',[]))]
  causes=[c['case_id'] for c in cases if c['expected'].get('source_condition',{}).get('input')==k]
  inactive=[p['full_example'] for p in paths if k not in p['full_projected_given'] and k in p['full_projected_expected'].get('unassessed_context',[])]
  scopes=collections.defaultdict(lambda:dict(required=False,consumed=False,unassessed=False,examples=[]))
  for p in paths:
   action=p.get('bounded_source_action_scope') or p.get('bounded_source_exclusion_scope') or p.get('bounded_source_choice_scope') or p.get('bounded_source_form_scope') or p.get('bounded_unselected_example_scope');scope=p['result_type']+('/cause='+action['primary_cause']['input'] if action else '')
   v=scopes[scope];v['required']|=bool(action and k in action['required_cause_fields']) or not action and pred['kind']=='always'
   v['consumed']|=k in p['full_projected_given'];v['unassessed']|=k in p['full_projected_expected'].get('unassessed_context',[])
   if len(v['examples'])<2:v['examples'].append(p['full_example'])
  rows.append(dict(rule_id=rid,input_id=k,question=i['question_ru'],current_predicate=pred,result_specific_reason=i['necessity_reason'],obligation_scope=roles[pred['kind']],source_refs=i['source_refs'],declared_locator=i['source_locator'],independently_read_primary_norms=norms,result_scopes=dict(scopes),missing_or_unknown_witnesses=missing[:4],known_cause_witnesses=causes[:4],inactive_unassessed_path_witnesses=inactive[:4],evidence_limit='Primary clauses are independently read; this requirement interpretation and prepared witnesses are author evidence for independent acceptance, not automatic proof of medical necessity or calculator execution.'))
assert not unmapped,unmapped
sj('necessity_evidence.json',dict(rows=rows,question_count=len(rows),primary_norm_origin='research/acceptance_v2_audit/condition_completion/scoped_input_conditions.json',source_sha_reuse='Norms reusable only for identical primary bytes; requirement interpretations are reviewed anew',unmapped=unmapped,global_minimum_claimed=False))
sj('ordinary_path_report.json',[dict(rule_id=rid,ordinary_counts=sorted({p['count'] for p in P if p['rule_id']==rid and p['ordinary_individual_numeric_path']}),maximum=max((p['count'] for p in P if p['rule_id']==rid and p['ordinary_individual_numeric_path']),default=None),examples=[p['full_example'] for p in P if p['rule_id']==rid and p['ordinary_individual_numeric_path']],acceptance_version=3,hard_maximum=None,necessity_evidence='necessity_evidence.json',global_minimum_claimed=False) for rid in R])
sj('current_candidate_metrics.json',dict(cards=len(R),prepared_cases=len(F),selected_complete_paths=len(P),question_rows=len(rows),per_result_ledger_rows=sum(len(r['inputs'])*len(C[rid]['branches']) for rid,r in R.items()),decision_count=len(json.loads((O/'necessity_decisions.json').read_text(encoding='utf-8'))['decisions']),ordinary_selected_paths=sum(p['ordinary_individual_numeric_path'] for p in P),ordinary_counts=sorted({p['count'] for p in P if p['ordinary_individual_numeric_path']}),hard_question_maximum=None,acceptance_version=3,clinical_validation='not_performed',calculator_implemented=False))
print('Per-question primary evidence exposed',len(rows),'rows; no unmapped question; necessity not automatically certified')
