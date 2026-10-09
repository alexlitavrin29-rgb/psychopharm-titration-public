"""Attach explicit sufficient-fact certificates and sparse same-exclusion witnesses."""
from pathlib import Path
from copy import deepcopy
import json,yaml,sys
O=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(O))
from bounded_source_exclusions import source_exclusion_scope
assert not (O/'source_exclusion_scope_repairs.json').exists(),'One-use correction'
P=json.loads((O/'followup_analysis/exclusion_scope_proposals.json').read_text(encoding='utf-8'));assert not P['missing']
R={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')};F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));by_id={c['case_id']:c for c in F['cases']};new=[];rows=[]
for p in P['rows']:
 c=by_id[p['case_id']];e=c['expected'];r=R[c['rule_id']]
 cert={k:deepcopy(p[k]) for k in ['source_ref','source_owner_input','causal_values','fact_components','source_condition_field','required_phase_context','calculation_at','scope']}
 cert.update(source_locator='Физ. с.'+','.join(str(n) for n in p['primary_norms'][0]['physical_pages']),primary_norms=p['primary_norms'],selected_context={k:c['external_context'][k] for k in ['diagnosis','mode']},nature='Explicit finite prepared primary-exclusion witness; literal fact agreement is not clinical branch execution')
 e['terminal_source_certificate']=cert;scope=source_exclusion_scope(r,c);assert scope is not None,c['case_id']
 rows.append(dict(case_id=c['case_id'],required_cause_fields=scope['required_cause_fields'],primary_norms=p['primary_norms']))
 n=deepcopy(c);n['case_id']+='--audit-final-source-exclusion';n['branch_id']=None
 forms={i['input_id'] for i in r['inputs'] if i['data_type']=='structured_form'}
 n['given']={k:v for k,v in c['given'].items() if k in forms}
 n['given'].update(deepcopy(cert['causal_values']))
 n['expected']['confirmed_negatives']=[k for k,v in n['given'].items() if v is False]
 n['expected']['unassessed_context']=sorted({i['input_id'] for i in r['inputs'] if i['input_id'] not in n['given']}|{k+'.'+field for k in cert['fact_components'] for field in ['A','B'] if k+'.'+field not in cert['fact_components'][k]})
 n['expected'].update(clinical_clearance=False,no_automatic_medication_change=True)
 # This is exclusion of a numerical result, never a current-use cessation.
 if 'treatment_phase' not in cert['required_phase_context']:n['external_context']['treatment_phase']='selected_mode'
 if 'target_treatment_phase' not in cert['required_phase_context']:n['external_context'].pop('target_treatment_phase',None)
 n['fixture_scope']='Same primary exclusion with source identity/known causal facts only. No additional dose/admission questionnaire; omitted facts unassessed. No source cessation or medication-change permission.'
 assert source_exclusion_scope(r,n) is not None,n['case_id'];new.append(n)
F['cases']+=new
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'source_exclusion_scope_repairs.json').write_text(json.dumps(dict(rows=rows,new_cases=[c['case_id'] for c in new],medical_values_changed=False,nature='Finite prepared source-exclusion scopes; primary causal sufficiency requires independent review'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Exclusion certificates',len(rows),'sparse same-exclusion witnesses',len(new))
