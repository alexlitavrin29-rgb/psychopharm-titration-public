"""Named known-positive cautions and form refusals from the finite independent residue."""
from pathlib import Path
from copy import deepcopy
import json,yaml,sys
O=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(O))
from bounded_source_exclusions import source_choice_scope,source_form_scope
assert not (O/'remaining_terminal_scope_repairs.json').exists(),'One-use correction'
R={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')}
N={(x['rule_id'],x['field']):x['primary_norms'] for x in json.loads((O.parent/'acceptance_v2_audit/condition_completion/scoped_input_conditions.json').read_text(encoding='utf-8'))}
F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));by_id={c['case_id']:c for c in F['cases']};rows=[];new=[]
for name in ['choice_reason_scope_residue','form_scope_residue']:
 P=json.loads((O.parent/'acceptance_v3_audit/final_review'/f'{name}.json').read_text(encoding='utf-8'))['rows']
 for p in P:
  c=by_id[p['case_id']];e=c['expected'];g=c['given'];r=R[c['rule_id']];ins={i['input_id']:i for i in r['inputs']};forms={k for k,i in ins.items() if i['data_type']=='structured_form'}
  assert e.get('total_daily_dose_mg') is None and not e.get('schedule') and not e.get('source_actions') and not e.get('published_options'),c['case_id']
  if name=='choice_reason_scope_residue':
   assert e['result_type']=='clinician_choice'
   if p.get('cause_kind')=='known_current_source_interaction_class':
    key='medicines';fields={key};sid=p['source_refs'][0];loc=p['source_locator'];assert g[key]==p['known_current_source_class_records'] and all(m['status']=='current' and m['interaction_class'] not in {None,'unknown'} for m in g[key])
   else:
    fields=set(p['known_positive_reason_fields']);assert all(g[k] is True for k in fields)
    assert len(fields)==1;key=next(iter(fields));bind=p['source_bindings'][0]
    sid=next((s for s in bind['source_refs'] if '--caution-'+s+'-' in c['case_id']),bind['source_refs'][0]);loc=bind['source_locator']
   ref={}
  else:
   assert e['result_type']=='form_not_feasible'
   if 'wrong-release' in c['case_id']:
    key=next((k for k in forms if k+'.release' in e.get('reason_ids',[])),next(iter(forms)) if len(forms)==1 else None);assert key
    fields={key};sid=ins[key]['source_refs'][0];loc=ins[key]['source_locator'];ref={}
   else:
    assert c['rule_id'] in {'venla-xr-gad-start','venla-xr-social-start'} and e.get('published_reduction_percent')==50 and e.get('arithmetic_total_mg')==37.5
    key='renal_metric';fields={key};sid='RU-VENLA-XR';loc='§4.2 физ.с.2–5: опубликованные 75 мг/сут; уменьшение50%; целые капсулы75/150 мг'
    assert g[key]['assessment']=='known' and g[key]['metric']=='absolute_GFR' and g[key]['unit']=='mL/min'
    ref=dict(published_start_mg=75,published_reduction_percent=50,arithmetic_total_mg=37.5,source_ref=sid,source_locator=loc,scope='Arithmetic form refusal only; not an executable individual dose')
  owner=next(k for k in forms if sid in ins[k]['source_refs']);assert g[owner]['source_id']==sid
  norms=[n for n in N[(c['rule_id'],key)] if n['source_id']==sid];assert norms,(c['case_id'],key,sid)
  cert=dict(result_type=e['result_type'],source_ref=sid,source_owner_input=owner,causal_values={k:deepcopy(g[k]) for k in sorted(fields)},fact_components={},source_condition_field=key,required_phase_context={},calculation_at=None,source_locator=loc,primary_norms=norms,selected_context={k:c['external_context'][k] for k in ['diagnosis','mode']},arithmetic_source_reference=ref,scope='Only the known primary caution/form refusal. No individual dose, clinical admission, medication change or automatic form substitution; other inputs unassessed',nature='Named finite prepared primary result witness, not clinical branch execution')
  removed={k:e.pop(k) for k in ['optional_stages_mg','maximum_mg','minimum_interval_weeks','minimum_increase_interval_weeks','automatic_increment'] if k in e}
  e['terminal_source_certificate']=cert;e.update(clinical_clearance=False,no_automatic_medication_change=True,no_automatic_target_start=True)
  fn=source_choice_scope if e['result_type']=='clinician_choice' else source_form_scope;assert fn(r,c) is not None
  n=deepcopy(c);n['case_id']+='--audit-final-known-terminal';n['branch_id']=None;n['given']={k:deepcopy(v) for k,v in g.items() if k in forms};n['given'].update(deepcopy(cert['causal_values']))
  n['expected']['confirmed_negatives']=[k for k,v in n['given'].items() if v is False];n['expected']['unassessed_context']=sorted(k for k in ins if k not in n['given'])
  n['external_context']['treatment_phase']='selected_mode';n['external_context'].pop('target_treatment_phase',None);n['fixture_scope']=cert['scope'];assert fn(r,n) is not None
  new.append(n);rows.append(dict(case_id=c['case_id'],certificate=cert,removed_unrelated_numeric_metadata=removed,new_sparse_case=n['case_id']))
F['cases']+=new
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'remaining_terminal_scope_repairs.json').write_text(json.dumps(dict(rows=rows,new_cases=[c['case_id'] for c in new],clinical_parameters_changed=False,scope='173 known-positive boolean cautions,45 known current source medication-class cautions and35 known form refusal scopes for independent review'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Remaining named terminals',len(rows),'sparse witnesses',len(new))
