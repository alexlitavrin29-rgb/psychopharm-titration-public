from pathlib import Path
import json,yaml
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2'
S=json.loads((R/'sources.json').read_text(encoding='utf-8'))
S['RU-ESC']['title']='Селектра (эсциталопрам), текущая официальная ОХЛП РУ ЛП-№(012351)-(РГ-RU), штамп 31.10.2025/0002'
S['RU-ESC']['historical_claim_status']='Earlier unverified claims are retained as historical evidence only; current sections read in round2 supersede them.'
for sid in ['RU-GAD','RU-PANIC','RU-PHOB','RU-DEP']:S[sid]['current_guideline_status_evidence']='remediation_round2/catalog_check.json; 08.10.2026; CodeVersion/ApplyStatusCalculated=1'
(R/'sources.json').write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8')
locs={'age':'§4.1 с.2; §4.2 с.3','form':'§3 с.1–2','from_form':'§3 с.1–2','to_form':'§3 с.1–2','pregnancy':'§4.6 с.10','lactation':'§4.6 с.10','medicines':'§4.3 с.4; §4.5 с.7–9','allergy':'§4.3 с.4','hepatic':'§4.2 с.3','from_hepatic':'§4.2 с.3','renal':'§4.2 с.3','mania':'§4.4 с.4','mania_symptoms':'§4.4 с.4','seizure_state':'§4.4 с.4','qt_risk':'§4.4 с.6','bleeding_risk':'§4.4 с.5','hyponatremia_risk':'§4.4 с.5','suicide_risk':'§4.4 с.4–5','akathisia':'§4.4 с.5','diabetes':'§4.4 с.4','glaucoma':'§4.4 с.7','known_cyp2c19':'§4.2 с.3','arrhythmia_signs':'§4.4 с.6','serotonin_syndrome_signs':'§4.4 с.5–6','coronary_disease':'§4.4 с.6','electrolyte_disturbance':'§4.4 с.6','ecg_done':'§4.4 с.6','electrolytes_corrected':'§4.4 с.6','maoi_type':'§4.5 с.7–8','maoi_stopped_at':'§4.5 с.7–8','current_dose':'§4.2 с.2–3','response':'§4.2 с.2–3','tolerability':'§4.2 с.3; §4.4 с.5–6','adherence':'§4.2 с.2–3; clinical decision, no numerical coefficient','time_at_dose':'§4.2 с.2–3; no fixed general increase interval','clinician_action':'§4.2 с.2–3; physician response-based choice','from_taper_plan':'§4.2 с.3; §4.4 с.6; physician-supplied stages, no published fixed ladder','duration_of_use':'§4.4 с.6','prior_withdrawal':'§4.4 с.6','current_withdrawal':'§4.4 с.6','withdrawal_severity':'§4.2 с.3; §4.4 с.6','duration':'§4.4 с.6','last_dose_time':'§4.2 с.3; §4.5 с.7; no fixed pair washout','withdrawal_symptoms':'§4.4 с.6','target_applicability':'§4.1–4.6 с.2–10; source-gap result grants no B clinical clearance'}
for folder in ['rules','findings','reference_rules']:
    for p in (R/folder).glob('*.yaml'):
        r=yaml.safe_load(p.read_text(encoding='utf-8'));r['sources']=[S[s['source_id']] for s in r['sources']]
        if folder=='rules':
            if any(s['source_id']=='RU-ESC' for s in r['sources']):
                r['verification'].update(primary_source_checked=True,all_clinical_parameters_have_sources=True,population_and_indication_checked=True)
                r['verification']['unresolved_items']=[x for x in r['verification'].get('unresolved_items',[]) if 'F01/F02/F13' not in x]
                r['verification']['unresolved_items']+=['CLcr exactly30 is not assigned by ESC source; no joint modifiers or invented general step/calendar.','F12: other active product edition currencies remain unresolved.' if r['identity']['mode']=='switch' else 'Clinical validation and calculator execution not performed.']
                r['profile']['selection_status']='source_bound_result_contract' if r['identity']['mode']!='switch' else 'directional_constraints_only_pair_calendar_unresolved'
                if r['identity']['mode']=='switch':
                    r['applicability']['renal_constraints']=['RU-ESC §4.2 с.3: CLcr >30 no correction; <30 caution; exactly30 unassigned. Other drug conditions remain separate.']
                for i in r['inputs']:
                    if 'RU-ESC' in i['source_refs']:
                        k=i['input_id'];loc=locs.get(k,'§4.2–4.6 с.2–10')
                        if len(i['source_refs'])==1:i['source_locator']=loc
                        elif 'historical_unreproduced_claim' in i.get('source_locator',''):i['source_locator']='RU-ESC '+loc+'; '+'; '.join(s+' '+S[s]['exact_locator'] for s in i['source_refs'] if s!='RU-ESC')
                        if 'source_locators' in i:i['source_locators']['RU-ESC']=loc
                    if i['data_type']=='source_hepatic_category':i['category_mapping_status']='source-specific categories explicit; clinical classification supplied by physician'
            r['input_contract_ref']='remediation_round2/input_contracts.yaml#fragment_bindings/'+r['rule_id']
        p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
print('Current availability/readiness, narrow ESC input locators and current contract links reconciled.')
