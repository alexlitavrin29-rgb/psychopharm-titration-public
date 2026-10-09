"""Targeted source recheck assertions; prepared expectations, no clinical engine."""
from pathlib import Path
from copy import deepcopy
import json, re, fitz
import verify_contracts

O=Path(__file__).resolve().parent
def check(d,paths):
    errors=[];C=d['contracts'];cases={c['case_id']:c for c in d['cases']}
    def ck(ok,msg):
        if not ok:errors.append(msg)
    for rid in ['parox-panic-kr','parox-taper-example','switch-parox-ago','switch-parox-ago-selected-example']:
        for i in d['rules'][rid]['inputs']:
            if 'RU-PAROX' in i['source_refs']:
                text=' '.join(str(i.get(k,'')) for k in ['question_ru','source_locator','why_needed','necessity_reason'])
                ck(not re.search(r'§4\.[2346]\s+с\.(?:1[6789]|2[012678])',text),'old PAROX page remains: '+rid+'/'+i['input_id'])
    for rid in ['preg-taper-limit','phen-taper-limit']:
        ck(all(b['expected_output'].get('prior_dose_resumption') is None for b in C[rid]['branches']),'unsupported prior dose resumption: '+rid)
    ck(not {'current_dose','duration_of_use','prior_withdrawal'} & set(C['preg-taper-limit']['required_inputs']),'qualitative preg taper requires numerical-plan operands')
    for rid,r in d['rules'].items():
        if rid.startswith('dulox-'):
            for i in r['inputs']:
                if i['input_id'] in {'mania','suicide_risk','bleeding_risk','hyponatremia_risk','diabetes','seizure_state'}:
                    ck('Подтверждённое значение' not in i['question_ru'],'stale DULOX question: '+rid+'/'+i['input_id'])
                if i['input_id']=='diabetes':ck(i['source_locator'].startswith('§4.8 с.11'),'DULOX diabetes cites unsupported §4.4 dose modifier')
    keys={'RU-SER':'symptomatic_hyponatremia','RU-PREG':'current_suicidal_thoughts_or_behavior','RU-DULOX':'persistent_BP_increase','RU-VENLA-XR':'suspected_serotonin_syndrome'}
    expected_actions={'RU-SER':{'consider_discontinuation_of_sertraline','provide_appropriate_medical_care'},'RU-PREG':{'consider_discontinuation_of_pregabalin','consider_appropriate_treatment_and_seek_medical_care'},'RU-DULOX':{'consider_dose_adjustment_or_gradual_discontinuation'},'RU-VENLA-XR':{'consider_dose_reduction_or_discontinuation_according_to_symptom_severity'}}
    for rid,con in C.items():
        for p in con.get('typed_source_conditions',[]):
            if p.get('input','').removeprefix('target_') not in keys.values():continue
            sid=p['source_ref'];k=p['input'];ck(p['action']=='clinician_choice' and set(p['source_actions'])==expected_actions[sid],'source consider/action semantics changed: '+rid+'/'+k)
            ck(con['input_requirements'][k]['kind']=='reported_current_event' and k not in con['required_inputs'],'event turned into a universal prerequisite: '+rid+'/'+k)
            for state in ['positive','negative','unknown','omitted']:
                case=cases.get(rid+'--audit-recheck-'+k+'-'+state)
                ck(case is not None,'reported event fixture missing: '+rid+'/'+k+'/'+state)
                if not case:continue
                e=case['expected']
                if state=='positive':
                    ck(e['result_type']=='clinician_choice' and e['total_daily_dose_mg'] is None and not e['schedule'] and set(a['action'] for a in e['source_actions'])==expected_actions[sid],'known event does not preserve source choice/action: '+case['case_id'])
                if state in {'omitted','unknown'}:
                    ck(k in e.get('unassessed_context',[]) and k not in e.get('confirmed_negatives',[]),'event unknown normalized to negative: '+case['case_id'])
                ck(e.get('clinical_clearance') is False,'event grants clinical clearance: '+case['case_id'])
            if k.startswith('target_'):
                for phase in ['not_started','unknown']:
                    case=cases[rid+'--audit-recheck-'+k+'-phase-'+phase]
                    ck(not case['expected'].get('source_actions') and not case['expected'].get('stop_medication'),'unstarted/unknown B gets cessation action: '+phase)
    for rid in ['switch-ser-esc','switch-esc-ser']:
        ck(any(g['source_ref']=='RU-SER' and 'strong_CYP3A4' in g.get('current_medicines_avoid_standard_combination',[]) for g in C[rid]['source_gates']),'SER interaction omitted from SSRI pair: '+rid)
    for rid in ['venla-xr-gad-start','venla-xr-social-start','venla-xr-panic-form-limit','venla-xr-taper-limit']:
        gate=next(g for g in C[rid]['source_gates'] if g['source_ref']=='RU-VENLA-XR')
        ck({'CYP2D6_inhibitor','CYP3A4_inhibitor','CNS_active','metoprolol'}<=set(gate['current_medicines_caution']),'XR caution classes incomplete: '+rid)
        ck({'QT_prolonging','serotonin_precursor','weight_loss_agent'}<=set(gate['current_medicines_avoid_standard_combination']),'XR avoidance classes incomplete: '+rid)
    for case in d['cases']:
        if case['given'].get('severe_skin_reaction') is True and case['expected'].get('stop_medication')=='RU-PREG':
            ck({'immediately_discontinue_pregabalin','consider_alternative_treatment_if_needed'}<=set(a['action'] for a in case['expected'].get('source_actions',[])),'SCAR conditional alternative action missing: '+case['case_id'])
    for rid in ['dulox-depression-start','dulox-gad-start','dulox-gad-adjust','dulox-taper-limit']:
        a=cases[rid+'--audit-recheck-duplicate-duloxetine-positive'];b=cases[rid+'--audit-recheck-duplicate-duloxetine-selected_product_only'];u=cases[rid+'--audit-recheck-duplicate-duloxetine-unknown_additional_product']
        ck(a['expected']['source_condition']['action']=='avoid_multiple_duloxetine_products' and a['given']['medicines'][0]['additional_product'] is True,'known DULOX duplicate not mapped: '+rid)
        ck(b['expected'].get('source_condition',{}).get('action')!='avoid_multiple_duloxetine_products','one current product inferred duplicate: '+rid)
        ck(u['expected']['result_type']=='insufficient_data','unconfirmed additional product inferred duplicate: '+rid)
    for p in paths:
        k=p['full_projected_expected'].get('source_condition',{}).get('input')
        ck(not k or k in p['full_projected_given'],'source reason uses unconsumed projected fact: '+p['full_example'])
        if 'duplicate-duloxetine' in p['full_example']:
            ck(any(f.endswith('.additional_product') for f in p['required_independent_facts']),'additional product fact hidden from count: '+p['full_example'])
    return errors

def run():
    d=verify_contracts.collect();paths=json.loads((O/'actual_question_paths.json').read_text(encoding='utf-8'));errors=check(d,paths)
    guards=[('RU-SER',6,['симптоматической гипонатриемией','медицинскую помощь']),('RU-PREG',8,['рассмотреть вопрос о прекращении','медицинской помощью']),('RU-PREG',6,['немедленно отменить','альтернативное лечение']),('RU-DULOX',4,['стойком повышении АД','постепенной отмены']),('RU-DULOX',7,['избегать одновременного','препаратов, содержащих дулоксетин']),('RU-VENLA-XR',8,['тяжести симптомов','снижения дозы']),('RU-VENLA-XR',16,['ингибитора CYP3A4','активность изофермента CYP2D6']),('RU-VENLA-XR',17,['венлафаксина и метопролола','осторожность'])]
    primary=[]
    for sid,page,phrases in guards:
        source=d['sources'][sid];doc=fitz.open(O.parent/source['local_file']);text=re.sub(r'\s+',' ',re.sub(r'-\s*\n\s*(?=[а-яё])','',doc[page-1].get_text()));ok=all(s in text for s in phrases)
        primary.append(dict(source_id=sid,page=page,phrases=phrases,pass_=ok));doc.close()
        if not ok:errors.append('primary phrase guard: '+sid+'/'+str(page))
    mutations=[]
    for name in ['event_automatic_stop','missing_medical_help','missing_SER_pair_gate','missing_XR_CYP','false_duplicate','missing_SCAR_alternative','hidden_projection_reason']:
        changed=deepcopy(d);pp=deepcopy(paths)
        if name=='event_automatic_stop':
            p=next(p for p in changed['contracts']['ser-adult-adjust']['typed_source_conditions'] if p['input']=='symptomatic_hyponatremia');p['action']='source_stop_action'
        elif name=='missing_medical_help':next(c for c in changed['cases'] if c['case_id']=='ser-adult-adjust--audit-recheck-symptomatic_hyponatremia-positive')['expected']['source_actions'].pop()
        elif name=='missing_SER_pair_gate':changed['contracts']['switch-esc-ser']['source_gates']=[g for g in changed['contracts']['switch-esc-ser']['source_gates'] if g['source_ref']!='RU-SER']
        elif name=='missing_XR_CYP':next(g for g in changed['contracts']['venla-xr-gad-start']['source_gates'] if g['source_ref']=='RU-VENLA-XR')['current_medicines_caution'].remove('CYP3A4_inhibitor')
        elif name=='false_duplicate':next(c for c in changed['cases'] if c['case_id']=='dulox-gad-start--audit-recheck-duplicate-duloxetine-selected_product_only')['expected']['source_condition']=dict(action='avoid_multiple_duloxetine_products')
        elif name=='missing_SCAR_alternative':next(c for c in changed['cases'] if c['given'].get('severe_skin_reaction') is True and c['expected'].get('stop_medication')=='RU-PREG')['expected']['source_actions'].pop()
        else:next(p for p in pp if p['full_projected_expected'].get('source_condition',{}).get('input')=='medicines')['full_projected_given'].pop('medicines')
        caught=bool(check(changed,pp));mutations.append(dict(mutation=name,rejected=caught))
        if not caught:errors.append('negative mutation missed: '+name)
    report=dict(status='pass' if not errors else 'fail',primary_guards=primary,isolated_negative_mutations=mutations,scope='Targeted primary clauses and prepared contract/projection regression only; not exhaustive source transfer, medical engine execution or clinical validation',errors=errors)
    (O/'recheck_repair_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(status=report['status'],primary_guards=len(primary),negative_mutations=len(mutations),errors=errors),ensure_ascii=False));return bool(errors)
if __name__=='__main__':raise SystemExit(run())
