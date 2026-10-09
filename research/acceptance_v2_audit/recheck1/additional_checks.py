from pathlib import Path
from copy import deepcopy
from types import SimpleNamespace
import json,yaml,hashlib,re,fitz
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent; O=ROOT/'research/remediation_round3'
m={'__file__':str(O/'verify_contracts.py'),'__name__':'safe_read_only'}
exec(compile((O/'verify_contracts.py').read_text('utf-8'),str(O/'verify_contracts.py'),'exec'),m)
d=m['collect'](); paths=json.loads((O/'actual_question_paths.json').read_text('utf-8'))
a={'__file__':str(O/'verify_audit_repairs.py'),'__name__':'safe_read_only','verify_contracts':SimpleNamespace(collect=m['collect'],validate=m['validate'])}
s=(O/'verify_audit_repairs.py').read_text('utf-8').replace('import verify_contracts','')
exec(compile(s.split("if __name__=='__main__':")[0],str(O/'verify_audit_repairs.py'),'exec'),a)
checks=[
 ('wrong_source_version',lambda x,p:x['contracts']['venla-xr-panic-form-limit']['branches'][0]['source_basis'][0].update(version='wrong edition')),
 ('remove_PAR_screening',lambda x,p:x['contracts']['parox-panic-kr']['required_inputs'].remove('bipolar_risk_screening')),
 ('remove_SER_CYP3A4',lambda x,p:x['contracts']['ser-panic-start']['source_gates'][0].update(current_medicines_avoid_standard_combination=[])),
 ('remove_DULOX_CYP2D6',lambda x,p:x['contracts']['dulox-gad-start']['source_gates'][0]['current_medicines_caution'].remove('CYP2D6_substrate')),
 ('XR_inclusive100',lambda x,p:next(v for v in x['contracts']['venla-xr-gad-start']['urgent_stop_predicates'] if v['input']=='diastolic_BP').update(operator='greater_or_equal')),
 ('unasked_negative',lambda x,p:p[0]['full_projected_expected'].setdefault('confirmed_negatives',[]).append('audit_unasked_field')),
 ('missing_ESC_ECG',lambda x,p:next(c for c in x['cases'] if c['case_id']=='switch-esc-ago--audit-v2-arrhythmia_signs-positive')['expected'].update(source_actions=[])),
 ('missing_PAR_support',lambda x,p:next(c for c in x['cases'] if c['case_id']=='parox-panic-kr--audit-v2-serotonin_syndrome_signs-positive')['expected'].update(source_actions=[]))]
mut=[]
for name,change in checks:
 dd,pp=deepcopy(d),deepcopy(paths); change(dd,pp); mut.append({'name':name,'rejected':bool(a['check_pack'](dd,pp))})
primary=a['primary_guards'](d['sources'])
arithmetic=[]
for c in d['cases']:
 e=c['expected']; total=e.get('total_daily_dose_mg'); per=e.get('dose_per_administration_mg'); freq=e.get('administrations_per_day')
 if all(type(x) in (int,float) for x in (total,per,freq)) and abs(per*freq-total)>1e-8:arithmetic.append(c['case_id'])
version_errors=[]; basis_count=0
for owner, bases in [(rid+'/'+b['branch_id'],b['source_basis']) for rid,r in d['contracts'].items() for b in r['branches']]+[(c['case_id'],c['source_basis']) for c in d['cases']]:
 for v in bases:
  basis_count+=1; sid=v['source_id']; source=d['sources'][sid]
  if v['version']!=source['version_or_update_date'] or v['sha256']!=source['document_fingerprint']['sha256']:version_errors.append(owner+'/'+sid)
projection_cause_errors=[{'case_id':p['full_example'],'input':p['full_projected_expected']['source_condition']['input']} for p in paths if p['full_projected_expected'].get('source_condition',{}).get('input') and p['full_projected_expected']['source_condition']['input'] not in p['full_projected_given']]
report={'author_repair_validator_independently_run':True,'author_repair_baseline_errors':a['check_pack'](d,paths),'author_extra_mutations':mut,'author_primary_phrase_guards_independently_run':primary,'arithmetic_consistency_errors':arithmetic,'nested_basis_count':basis_count,'version_SHA_errors':version_errors,'own_projected_consumed_input_errors':projection_cause_errors,'medical_evaluator_executed':False}
(OUT/'additional_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['author_primary_phrase_guards_independently_run']},ensure_ascii=False))
