"""Complete precisely identified source-condition witnesses; no dose engine."""
from pathlib import Path
from copy import deepcopy
import json,yaml
O=Path(__file__).resolve().parent.parent;A=O.parent/'acceptance_v2_audit/condition_completion'
assert not (O/'condition_case_repairs.json').exists(),'One-use correction'
rows=json.loads((A/'positive_expected_gaps_exact.json').read_text(encoding='utf-8'))['rows'];F=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'));R={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (O/'rules').glob('*.yaml')};C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'))['rules'];S=json.loads((O/'sources.json').read_text(encoding='utf-8'));new=[];journal=[];seen=set()
for row in rows:
    rid=row['rule_id'];sid=row['source_id'];lit=row['condition_literal'];actor=row['actor'];r=R[rid]
    medication='/current_medicines_' in row['contract_path'];kind=row['contract_path'].split('/')[-2]
    k='medicines' if medication else lit['input'] if isinstance(lit,dict) else lit
    value=lit.get('value') if isinstance(lit,dict) else None
    marker=(rid,sid,k,lit if isinstance(lit,str) else value)
    if marker in seen:continue
    seen.add(marker)
    base=next(c for c in F['cases'] if c['rule_id']==rid and c['branch_id']);c=deepcopy(base)
    label=lit if isinstance(lit,str) else k+'-'+str(value)
    c.update(case_id=rid+'--audit-final-primary-'+sid+'-'+label+'-positive',branch_id=None)
    c['fixture_scope']='Source-bound positive condition specification, with full typed given and actor context. A synthetic interaction-class witness is not execution of an INN classifier or a real patient record.'
    pages=row['physical_pages'];locator='Физ. с.'+','.join(map(str,pages));g=c['given']
    c['expected']=e={}
    if medication:
        g[k]=[dict(record_id='primary_class',inn='synthetic_class_fixture:'+lit,status='current',interaction_class=lit,classification_basis=dict(source_ref=sid,source_locator=locator))]
        if lit=='maoi':g['maoi_type']={'primary_class':'irreversible'};g['maoi_stopped_at']={}
    elif k=='hepatic':g[k].update(category=value,assessment='known')
    elif value is not None:g[k]=value
    else:g[k]=True
    is_stop=(k=='seizure_state' and value in {'новые приступы','первичные/участившиеся приступы'}) or sid=='RU-AGO' and k=='liver_injury_signs'
    phasekey='target_treatment_phase' if actor=='B' else 'treatment_phase'
    if is_stop:c['external_context'][phasekey]='ongoing'
    excluded=kind in {'exclusions','current_medicines_excluded'} or k=='hepatic' and sid=='RU-AGO'
    rt='source_stop_action' if is_stop else 'not_applicable' if excluded and actor!='A' else 'clinician_choice'
    e.update(result_type=rt,total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],missing_fields=[],clinical_clearance=False,source_actions=[],no_automatic_target_start=r['identity']['mode']=='switch',no_automatic_medication_change=not is_stop,reason_ids=[k])
    for f in ['stop_medication','published_option_mg','conditional_next_total_mg','automatic_combined_start','initial_period_weeks']:e.pop(f,None)
    e['source_condition']=dict(input=k,source_ref=sid,source_locator=locator,actor=actor,action='published_ongoing_cessation' if is_stop else 'source_excludes_standard_numeric_application' if excluded else 'source_caution_or_conditional_clinical_decision_without_numeric_coefficient',primary_norm=row['independent_primary_norm'])
    if medication:e['source_condition']['interaction_class']=lit
    if actor=='A' and excluded:e['source_condition']['cessation_scope']='Current contraindicated A combination requires physician assessment; no automatic abrupt A stop, pair continuation/overlap/start not granted. Published gradual cessation remains a separate source/physician plan.'
    if is_stop:
        e['stop_medication']=sid
        actions=['immediately_discontinue_agomelatine','monitor_liver_function_until_normalization'] if sid=='RU-AGO' else ['discontinue_selected_medication']
        e['source_actions']=[dict(action=a,medication_role='target_B' if actor=='B' else 'selected_or_A',source_ref=sid,source_locator=locator) for a in actions]
    basis=dict(source_id=sid,version=S[sid]['version_or_update_date'],locator=locator,sha256=row['source_sha256'])
    e['source_basis']=[basis]
    variants=[c]
    u=deepcopy(c);u['case_id']=c['case_id'].replace('-positive','-unknown')
    if medication:u['given']['medicines'][0]['interaction_class']='unknown'
    elif k=='hepatic':u['given'][k].update(category='unknown',assessment='unknown')
    else:u['given'][k]='unknown'
    ue=u['expected'];ue.update(result_type='insufficient_data' if C[rid]['input_requirements'][k]['kind']=='always' else 'clinician_choice',source_actions=[],total_daily_dose_mg=None,dose_per_administration_mg=None,administrations_per_day=None,schedule=[],missing_fields=['medicines.primary_class.interaction_class'] if medication else [k] if C[rid]['input_requirements'][k]['kind']=='always' else [],no_automatic_medication_change=True)
    if medication and 'maoi_type' in C[rid]['input_requirements']:
        u['given']['maoi_type']={'primary_class':'unknown'};ue['missing_fields'].append('maoi_type.primary_class')
    ue.pop('stop_medication',None);ue.pop('source_condition',None);ue['unassessed_context']=sorted(set(ue.get('unassessed_context',[]))|{k});variants.append(u)
    if is_stop:
        for phase in ['unknown','not_started']:
            n=deepcopy(c);n['case_id']=c['case_id'].replace('-positive','-phase-'+phase);n['external_context'][phasekey]=phase
            ne=n['expected'];ne.update(result_type='insufficient_data' if phase=='unknown' else 'clinician_choice',source_actions=[],no_automatic_medication_change=True,missing_fields=['external_context.'+phasekey] if phase=='unknown' else [])
            ne.pop('stop_medication',None);ne.pop('source_condition',None);ne['phase_clarification']='Current source cessation needs confirmed ongoing use of the indicated actor; a reported event with unknown/not-started phase receives physician assessment, no current medication change.';variants.append(n)
    for n in variants:
        ee=n['expected'];gg=n['given'];ee['confirmed_negatives']=[f for f,v in gg.items() if v is False]
        ee['unassessed_context']=sorted(set(ee.get('unassessed_context',[]))|{i['input_id'] for i in r['inputs'] if i['requirement_predicate']['kind'] in {'reported_context','reported_current_event','reported_source_information'} and gg.get(i['input_id']) in (None,'unknown','not_assessed')})
    new+=variants;journal.append(dict(record_ids=[x['record_id'] for x in rows if x['rule_id']==rid and x['source_id']==sid and x['condition_literal']==lit],rule_id=rid,source_id=sid,condition_literal=lit,new_cases=[n['case_id'] for n in variants],source_sha256=row['source_sha256'],physical_pages=pages,independent_medical_acceptance='pending'))
F['cases']+=new
(O/'full_scenarios.json').write_text(json.dumps(F,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'condition_case_repairs.json').write_text(json.dumps(dict(original_literal_occurrences=len(rows),unique_condition_scopes=len(journal),new_cases=len(new),rows=journal,no_calculator_execution=True),ensure_ascii=False,indent=2),encoding='utf-8')
print('Explicit primary condition witnesses',len(journal),'new cases',len(new),'independent medical acceptance pending')
