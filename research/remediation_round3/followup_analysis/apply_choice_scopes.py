"""Finite named primary caution witnesses; no broad clinician-choice shortcut."""
from pathlib import Path
from copy import deepcopy
import json,yaml,sys
O=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(O))
from phase_provenance import selected_phase
from bounded_source_exclusions import source_choice_scope
assert not (O/'source_choice_scope_repairs.json').exists(),'One-use correction'
P=json.loads((O.parent/'acceptance_v3_audit/final_review/choice_scope_candidates.json').read_text(encoding='utf-8'))['rows']
R={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')}
N={(x['rule_id'],x['field']):x['primary_norms'] for x in json.loads((O.parent/'acceptance_v2_audit/condition_completion/scoped_input_conditions.json').read_text(encoding='utf-8'))}
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));by_id={c['case_id']:c for c in F['cases']};rows=[];new=[]
for p in P:
 c=by_id[p['case_id']];e=c['expected'];g=c['given'];r=R[c['rule_id']];sc=e['source_condition'];k=sc['input'];sid=sc['source_ref'];ins={i['input_id']:i for i in r['inputs']}
 assert e['result_type']=='clinician_choice' and e.get('total_daily_dose_mg') is None and not e.get('schedule') and not e.get('published_options'),c['case_id']
 owner=next(i['input_id'] for i in r['inputs'] if i['data_type']=='structured_form' and sid in i['source_refs']);assert g[owner]['source_id']==sid
 fields={k};phase={};actor='Known source caution; no current medication action inferred'
 if k=='effective_contraception':
  assert g.get('reproductive_population') is True;fields.add('reproductive_population')
 if e.get('source_actions'):
  if owner=='to_form':
   assert c['external_context'].get('target_treatment_phase')=='ongoing';phase={'target_treatment_phase':'ongoing'};actor='target_B ongoing'
  else:
   resolved,origin=selected_phase(r,c);assert resolved=='ongoing',(c['case_id'],resolved)
   if origin=='consumed_actual_current_dose':
    fields.add('current_dose');pred=ins['current_dose']['requirement_predicate']
    if pred['kind']=='field_true':fields.add(pred['field'])
   else:phase={'treatment_phase':'ongoing'}
   actor='selected/A ongoing; actual dose retained if it establishes this phase'
 norms=[n for n in N[(c['rule_id'],k)] if n['source_id']==sid];assert norms
 cert=dict(result_type='clinician_choice',source_ref=sid,source_owner_input=owner,causal_values={x:deepcopy(g[x]) for x in sorted(fields)},fact_components={},source_condition_field=k,required_phase_context=phase,calculation_at=None,source_locator=sc['source_locator'],primary_norms=norms,selected_context={x:c['external_context'][x] for x in ['diagnosis','mode']},actor_phase=actor,scope='Only this primary source caution/conditional physician action; no individual dose, treatment calendar, medication change or new treatment permission; unused dose/admission fields unassessed',nature='Finite prepared primary caution witness; literal certificate agreement is not execution of clinical branch logic')
 removed={x:e.pop(x) for x in ['optional_stages_mg','maximum_mg','minimum_interval_weeks','minimum_increase_interval_weeks','automatic_increment'] if x in e}
 e['terminal_source_certificate']=cert;e.update(clinical_clearance=False,no_automatic_medication_change=True,no_automatic_target_start=True)
 assert source_choice_scope(r,c) is not None
 n=deepcopy(c);n['case_id']+='--audit-final-source-caution';n['branch_id']=None
 forms={i['input_id'] for i in r['inputs'] if i['data_type']=='structured_form'}
 n['given']={x:deepcopy(v) for x,v in g.items() if x in forms};n['given'].update(deepcopy(cert['causal_values']))
 n['expected']['confirmed_negatives']=[x for x,v in n['given'].items() if v is False]
 n['expected']['unassessed_context']=sorted(i['input_id'] for i in r['inputs'] if i['input_id'] not in n['given'])
 if not e.get('source_actions'):n['external_context']['treatment_phase']='selected_mode'
 if 'target_treatment_phase' not in phase:n['external_context'].pop('target_treatment_phase',None)
 n['fixture_scope']='Same known primary caution/physician-only action with sufficient facts and its own current actor if applicable. No individual dose or clearance; absent facts unassessed.'
 assert source_choice_scope(r,n) is not None,n['case_id'];new.append(n)
 rows.append(dict(case_id=c['case_id'],certificate=cert,removed_unrelated_numeric_metadata=removed,new_sparse_case=n['case_id']))
F['cases']+=new
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'source_choice_scope_repairs.json').write_text(json.dumps(dict(rows=rows,new_cases=[c['case_id'] for c in new],clinical_parameters_changed=False,nature='Named finite primary cautions and action witnesses for independent sufficiency review; no clinical evaluator'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Known primary caution certificates',len(rows),'sparse witnesses',len(new))
