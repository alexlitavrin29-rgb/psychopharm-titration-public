"""Mutate in-memory copies; never change originals. These are contract-detector tests."""
from copy import deepcopy
from pathlib import Path
import json
from verify_contracts import collect,validate
R=Path(__file__).resolve().parents[1]
base=collect();baseline=validate(base)
if baseline:raise RuntimeError('Baseline failed: '+str(baseline))
def apply(d,kind):
    rs=d['rules'];cs=d['contracts']
    if kind=='static_branch_default':rs['dulox-gad-start']['output']['total_daily_dose']=30
    elif kind=='taper_ceiling':rs['ser-taper-limit']['clinical_parameters'][0]['upper']=2
    elif kind=='missing_ago_gate':cs['switch-parox-ago-selected-example']['required_inputs'].remove('dementia')
    elif kind=='unknown_permits_dose':
        c=next(c for c in d['cases'] if c['case_id']=='dulox-gad-start--renal_metric-unknown');c['expected'].update(result_type='exact',total_daily_dose_mg=30)
    elif kind=='hidden_maoi_timestamp':next(i for i in rs['ser-panic-start']['inputs'] if i['input_id']=='maoi_stopped_at')['data_type']='medication_list'
    elif kind=='contradictory_dependency':rs['parox-taper-example']['verification']['ready_for_technical_implementation']=False
    elif kind=='copy_unbound':d['sources']['RU-AGO']['local_file']=None
    elif kind=='esc_unverified_operator':rs['esc-gad-start']['logic']['source_blocker']['renal_boundary_operator']='<='
    elif kind=='unsupported_currency_claim':d['sources']['RU-AGO']['latest_registration_revision_confirmed']=True
    elif kind=='gate_without_input':cs['ago-stop']['source_gates'][0]['exclusions']=['allergy']
    elif kind=='wrong_renal_metric':
        c=next(c for c in d['cases'] if c['case_id']=='dulox-gad-start--wrong-renal-metric-renal_metric');c['expected'].update(result_type='exact',total_daily_dose_mg=30)
    elif kind=='hepatic_AB_owner':
        p=next(p for p in cs['switch-parox-ago-selected-example']['typed_source_conditions'] if p['input']=='hepatic');p.update(source_ref='RU-PAROX',action='clinician_choice')
    elif kind=='missing_seizure_stop':
        next(i for i in rs['ser-panic-start']['inputs'] if i['input_id']=='seizure_state')['allowed_values'].remove('новые приступы')
    elif kind=='missing_ongoing_liver_stop':d['cases']=[c for c in d['cases'] if c['case_id']!='ago-gad-start--ALT_ratio-ongoing-above3']
    elif kind=='undeclared_medication_provenance':d['schema']['structures']['medication_list']['entry_fields'].pop('classification_basis')
    elif kind=='missing_switch_identity':next(c for c in d['cases'] if c['rule_id']=='switch-parox-ago-selected-example')['external_context'].pop('to_drug')
    elif kind=='unknown_conditional_timestamp':
        c=next(c for c in d['cases'] if c['case_id']=='ser-panic-start--maoi_stopped_at-M1-unknown');c['expected'].update(result_type='exact',total_daily_dose_mg=25)
checks={
 'static_branch_default':'branch output has static default dose',
 'taper_ceiling':'minimum taper encoded as ceiling',
 'missing_ago_gate':'agomelatine missing source gate',
 'unknown_permits_dose':'missing field allows dose',
 'hidden_maoi_timestamp':'MAOI records/timestamps hidden',
 'contradictory_dependency':'composite readiness/dependency contradiction',
 'copy_unbound':'source copy without local_file',
 'esc_unverified_operator':'unconfirmed ESC predicate',
 'unsupported_currency_claim':'currency claimed without registry document comparison',
 'gate_without_input':'source gate without declared input',
 'wrong_renal_metric':'wrong renal metric permits dose',
 'hepatic_AB_owner':'target hepatic owner/action incorrect',
 'missing_seizure_stop':'sertraline seizure stop missing',
 'missing_ongoing_liver_stop':'ongoing transaminase stop missing',
 'undeclared_medication_provenance':'undeclared/incomplete medication entry',
 'missing_switch_identity':'switch identity context missing',
 'unknown_conditional_timestamp':'missing field allows dose'}
rows=[]
for kind,message in checks.items():
    d=deepcopy(base);apply(d,kind);errors=validate(d);matching=[e for e in errors if message in e]
    rows.append(dict(mutation=kind,rejected=bool(matching),matching_errors=matching))
report=dict(status='pass' if all(r['rejected'] for r in rows) else 'fail',isolated_baseline='pass',main_data_modified=False,
    nature='Static contract-detector negative checks; not medical or calculator validation',cases=rows)
(R/'remediation/new_negative_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(report['status']!='pass')
