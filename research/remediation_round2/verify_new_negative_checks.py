"""Isolated contract-detector mutations. The baseline and original reports stay unchanged."""
from copy import deepcopy
from pathlib import Path
import json
from verify_contracts import collect,validate
R=Path(__file__).resolve().parents[1]
base=collect();baseline=validate(base)
if baseline:raise RuntimeError('Baseline failed: '+str(baseline))
def scenario(d,cid):return next(c for c in d['cases'] if c['case_id']==cid)
def apply(d,kind):
    rs=d['rules'];cs=d['contracts']
    if kind=='static_branch_default':rs['dulox-gad-start']['output']['total_daily_dose']=30
    elif kind=='taper_ceiling':rs['ser-taper-limit']['clinical_parameters'][0]['upper']=2
    elif kind=='missing_ago_gate':cs['switch-parox-ago-selected-example']['required_inputs'].remove('dementia')
    elif kind=='unknown_permits_dose':scenario(d,'dulox-gad-start--renal_metric-unknown')['expected'].update(result_type='exact',total_daily_dose_mg=30)
    elif kind=='hidden_maoi_timestamp':next(i for i in rs['ser-panic-start']['inputs'] if i['input_id']=='maoi_stopped_at')['data_type']='medication_list'
    elif kind=='contradictory_dependency':rs['parox-taper-example']['verification']['ready_for_technical_implementation']=False
    elif kind=='copy_unbound':d['sources']['RU-AGO']['local_file']=None
    elif kind=='esc_exact30_dose':scenario(d,'esc-gad-start--current-clcr-30')['expected'].update(result_type='exact',total_daily_dose_mg=10)
    elif kind=='unsupported_currency_claim':d['sources']['RU-AGO']['latest_registration_revision_confirmed']=True
    elif kind=='gate_without_input':cs['ago-stop']['source_gates'][0]['exclusions']=['allergy']
    elif kind=='wrong_renal_metric':scenario(d,'dulox-gad-start--wrong-renal-metric-renal_metric')['expected'].update(result_type='exact',total_daily_dose_mg=30)
    elif kind=='hepatic_AB_owner':next(p for p in cs['switch-parox-ago-selected-example']['typed_source_conditions'] if p['input']=='hepatic').update(source_ref='RU-PAROX',action='clinician_choice')
    elif kind=='missing_seizure_stop':next(i for i in rs['ser-panic-start']['inputs'] if i['input_id']=='seizure_state')['allowed_values'].remove('новые приступы')
    elif kind=='missing_ongoing_liver_stop':d['cases']=[c for c in d['cases'] if c['case_id']!='ago-gad-start--ALT_ratio-ongoing-above3']
    elif kind=='undeclared_medication_provenance':d['schema']['structures']['medication_list']['entry_fields'].pop('classification_basis')
    elif kind=='missing_switch_identity':next(c for c in d['cases'] if c['rule_id']=='switch-parox-ago-selected-example')['external_context'].pop('to_drug')
    elif kind=='unknown_conditional_timestamp':scenario(d,'ser-panic-start--maoi_stopped_at-M1-unknown')['expected'].update(result_type='exact',total_daily_dose_mg=25)
    elif kind=='conditional_flag_collision':next(i for i in rs['ser-adult-adjust']['inputs'] if i['input_id']=='qt_risk')['required_for_individual_result']=True
    elif kind=='consistent_but_source_wrong_necessity':
        i=next(i for i in rs['ser-adult-adjust']['inputs'] if i['input_id']=='qt_risk');i.update(required_for_individual_result=True,requirement_predicate={'kind':'always'},input_role='required_selected_result_operand_or_source_gate',required_when='для каждого результата')
        cs['ser-adult-adjust']['required_inputs'].append('qt_risk');cs['ser-adult-adjust']['input_requirements']['qt_risk']={'kind':'always'}
    elif kind=='monitor_unknown_normal':scenario(d,'ser-adult-adjust--round2-minimal-selected-action')['expected']['unassessed_context']=[]
    elif kind=='keep_requires_increase':scenario(d,'ser-adult-adjust--round2-keep-without-increase-fields')['expected'].update(result_type='insufficient_data',total_daily_dose_mg=None)
    elif kind=='active_mania_removed':cs['ser-adult-adjust']['urgent_stop_predicates']=[]
    elif kind=='elderly65_special':scenario(d,'esc-elderly-start--current-age-65')['expected'].update(result_type='exact',total_daily_dose_mg=5)
    elif kind=='unknown_ESC_monitor_normal':scenario(d,'esc-gad-start--current-unassessed-monitoring-context')['expected']['unassessed_context']=[]
    elif kind=='uncompleted_ECG_permits_dose':scenario(d,'esc-gad-start--current-ecg_done-False')['expected'].update(result_type='exact',total_daily_dose_mg=10)
    elif kind=='moclobemide23h_permits_dose':scenario(d,'esc-gad-start--current-moclobemide-23h')['expected'].update(result_type='exact',total_daily_dose_mg=10)
    elif kind=='switch_A_mania_owner_lost':cs['switch-ser-ago']['urgent_stop_predicates']=[p for p in cs['switch-ser-ago']['urgent_stop_predicates'] if p['source_ref']!='RU-SER']
    elif kind=='ordinary_ESC_A_wrong_dose':scenario(d,'switch-esc-ser--current-branch-pair_gap')['given']['current_dose']=100
    elif kind=='ESC_nested_fixture_lost':d['cases']=[c for c in d['cases'] if c['case_id']!='esc-gad-start--round2-nested-renal-value-unknown']
    elif kind=='ESC_ECG_stop_action_lost':scenario(d,'esc-gad-start--current-arrhythmia_signs-stop')['expected']['source_actions']=[]
    elif kind=='ESC_serotonin_other_drugs_lost':scenario(d,'esc-gad-start--current-serotonin_syndrome_signs-stop')['expected']['source_actions']=[{'action':'start_symptomatic_treatment_by_clinician'}]
    elif kind=='SSRI_pair_A_B_owner':next(i for i in rs['switch-esc-ser']['inputs'] if i['input_id']=='current_dose')['source_refs']=['RU-SER']
    elif kind=='unknown_B_allergy_permits_calendar':scenario(d,'switch-parox-ago-selected-example--branch-selected40')['given']['allergy']['B']='unknown'
    elif kind=='switch_allergy_single_boolean':next(i for i in rs['switch-ser-ago']['inputs'] if i['input_id']=='allergy')['data_type']='boolean'
    elif kind=='target_stop_phase_lost':scenario(d,'switch-ser-ago--alt_ratio_uln-ongoing-above3')['external_context']['target_treatment_phase']='not_started'
checks={
 'static_branch_default':'branch output has static default dose','taper_ceiling':'minimum taper encoded as ceiling',
 'missing_ago_gate':'agomelatine missing source gate','unknown_permits_dose':'missing field allows dose',
 'hidden_maoi_timestamp':'MAOI records/timestamps hidden','contradictory_dependency':'composite readiness/dependency contradiction',
 'copy_unbound':'source copy without local_file','esc_exact30_dose':'ESC exact30 source gap erased',
 'unsupported_currency_claim':'currency claimed without registry document comparison','gate_without_input':'source gate without declared input',
 'wrong_renal_metric':'wrong renal metric permits dose','hepatic_AB_owner':'target hepatic owner/action incorrect',
 'missing_seizure_stop':'sertraline seizure stop missing','missing_ongoing_liver_stop':'ongoing transaminase stop missing',
 'undeclared_medication_provenance':'undeclared/incomplete medication entry','missing_switch_identity':'switch identity context missing',
 'unknown_conditional_timestamp':'missing field allows dose','conditional_flag_collision':'conditional/unconditional collision',
 'consistent_but_source_wrong_necessity':'primary necessity decision violated','monitor_unknown_normal':'unasked monitoring context silently normal',
 'keep_requires_increase':'keep wrongly requires increase-only fields','active_mania_removed':'active sertraline mania stop missing',
 'elderly65_special':'ESC elderly strict age erased','unknown_ESC_monitor_normal':'unasked monitoring context silently normal',
 'uncompleted_ECG_permits_dose':'uncompleted ESC conditional source action permits dose',
 'moclobemide23h_permits_dose':'ESC moclobemide minimum day erased','switch_A_mania_owner_lost':'switch active mania A owner missing','ordinary_ESC_A_wrong_dose':'ordinary ESC current dose outside source range',
 'ESC_nested_fixture_lost':'ESC nested prepared case missing','ESC_ECG_stop_action_lost':'ESC arrhythmia ECG action missing','ESC_serotonin_other_drugs_lost':'ESC serotonin complete source action missing','SSRI_pair_A_B_owner':'SSRI pair A/B form/dose owner drift',
 'unknown_B_allergy_permits_calendar':'missing field allows dose','switch_allergy_single_boolean':'switch allergy A/B type/owner missing','target_stop_phase_lost':'target AGO stop without target ongoing phase'}
rows=[]
for kind,message in checks.items():
    d=deepcopy(base);apply(d,kind);errors=validate(d);matching=[e for e in errors if message in e]
    rows.append(dict(mutation=kind,rejected=bool(matching),matching_errors=matching[:4]))
report=dict(status='pass' if all(r['rejected'] for r in rows) else 'fail',isolated_baseline='pass',main_data_modified=False,nature='Static contract-detector negatives, not medical or calculator validation',cases=rows)
(R/'remediation_round2/new_negative_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':report['status'],'mutations':len(rows),'missed':[r['mutation'] for r in rows if not r['rejected']]},ensure_ascii=False));raise SystemExit(report['status']!='pass')
