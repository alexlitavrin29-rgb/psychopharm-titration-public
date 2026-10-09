"""Refresh derived indices and retain an explicit, limited source-review ledger."""
from pathlib import Path
import csv,json,hashlib
from copy import deepcopy
import yaml
R=Path(__file__).resolve().parents[1];O=R/'remediation'
S=json.loads((R/'sources.json').read_text(encoding='utf-8'))
def dump(p,x):p.write_text(yaml.safe_dump(x,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
def csvwrite(p,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rules=[]
for p in sorted((R/'rules').glob('*.yaml')):
    r=yaml.safe_load(p.read_text(encoding='utf-8'))
    # Unknown-state aliases are input metadata, not clinical normality.
    for i in r['inputs']:
        i.setdefault('value_aliases',{}).update({'неизвестно':'unknown','не исследовано':'not_assessed','не помню':'unknown'})
    r['verification']['source_transfer_check']='reviewed_available_original_sections_and_contract_consistency; calculator_not_implemented; latest_registration_revision_not_confirmed'
    r['verification']['transfer_scope']='Only explicitly source-bound branch contracts and prepared expectations; medical currency limits in sources.json remain open. No automatic clinical use.'
    if 'RU-ESC' in [s['source_id'] for s in r['sources']]:
        r['output'].update(result_type='source_unavailable',dose_per_administration=None,administrations_per_day=None,total_daily_dose=None,schedule=[])
        r['applicability']['indication_status_in_russia']='unverified_current_original'
        r['identity']['formulation_confirmation']='registry strengths observed; splitting and dose predicates unverified'
    dump(p,r);rules.append(r)
for folder in ('findings','reference_rules'):
    for p in (R/folder).glob('*.yaml'):
        r=yaml.safe_load(p.read_text(encoding='utf-8'));r['sources']=[S[s['source_id']] for s in r['sources']];dump(p,r)
findings=[yaml.safe_load(p.read_text(encoding='utf-8')) for p in sorted((R/'findings').glob('*.yaml'))]
refs=[yaml.safe_load(p.read_text(encoding='utf-8')) for p in sorted((R/'reference_rules').glob('*.yaml'))]
est=yaml.safe_load((R/'renal_estimator.yaml').read_text(encoding='utf-8'))
for name,rs in [('test_cases.yaml',rules),('finding_cases.yaml',findings),('reference_test_cases.yaml',refs)]:
    idx=yaml.safe_load((R/name).read_text(encoding='utf-8'));idx['cases']=[{'rule_id':r['rule_id'],**c} for r in rs for c in r['test_cases']];dump(R/name,idx)
with (R/'input_catalog.csv').open(encoding='utf-8-sig',newline='') as f:cols=csv.DictReader(f).fieldnames
cols+=['source_locator','required_for_individual_result','structure_ref','value_aliases','missing_states']
cols=list(dict.fromkeys(cols));rows=[]
for r in rules+findings+[est]:
    for i in r['inputs']:
        row={'rule_id':r['rule_id'],**i};rows.append({k:json.dumps(row.get(k),ensure_ascii=False) if isinstance(row.get(k),(dict,list)) else row.get(k,'') for k in cols})
csvwrite(R/'input_catalog.csv',rows)
counts=[]
for r in rules:
    extra=sum(2 for i in r['inputs'] if i['data_type']=='structured_renal')
    # A/B hypersensitivity is an OR input, but assessing both products costs two independent facts.
    allergy_extra=1 if r['identity']['mode']=='switch' and any(i['input_id']=='allergy' for i in r['inputs']) else 0
    initial=4 if r['identity']['mode']=='switch' else 3
    counts.append(dict(rule_id=r['rule_id'],clinical_input_entries=len(r['inputs']),initial_selections=initial,
        all_catalog_fields_count=len(r['inputs'])+initial,
        independent_renal_subfields_extra=extra,independent_A_B_allergy_extra=allergy_extra,
        required_known_branch_fields=sum(i.get('required_for_individual_result') is True for i in r['inputs'])+extra+allergy_extra+initial,
        conditional_maoi_record_count='one type + one stopped timestamp per relevant record; additional to medication list',
        count_meaning='Catalogue includes conditional fields; actual question paths and source/reference limits in question_flows.yaml. Independent renal metric/value/method counted; form metadata derived from identified source is not an extra patient question.'))
(R/'question_counts.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2),encoding='utf-8')
byrule={r['rule_id']:r for r in rules};flow=yaml.safe_load((R/'question_flows.yaml').read_text(encoding='utf-8'))
for f in flow['flows']:
    r=byrule[f['rule_id']];known=set(f['clinical_questions']);f['conditional_questions']=[i['input_id'] for i in r['inputs'] if i['input_id'] not in known]
    f['input_units']={i['input_id']:i['unit'] for i in r['inputs']}
    f['individual_result_required_fields']=[i['input_id'] for i in r['inputs'] if i.get('required_for_individual_result') is True]
    f['individual_result_count_without_maoi_history']=next(c['required_known_branch_fields'] for c in counts if c['rule_id']==r['rule_id'])
    f['maoi_history_count']='each relevant MAOI adds a type; each stopped MAOI also adds its timestamp; unknown prevents start'
    if f['rule_id']=='esc-gad-start':f['ordinary_expected']={'result_type':'source_unavailable','unconditional_dose':None,'all_patient_safety_checks_completed':False};f['if_complex']='F01/F02/F13 open; renal sign not confirmed; no individual dose';f['clinical_output']='blocked_source'
    elif f['rule_id'] not in {'ago-stop','parox-taper-example'}:
        f['clinical_output']='reference_only_source_scheme'
        f['ordinary_expected']['reference_only']=True;f['ordinary_expected']['individual_dose']=None
        f['if_complex']='Complete every required dose/applicability input; count them separately. Reference path is not sufficient for an individual numeric result.'
    if f['rule_id']=='ser-adjust-clinician-action':
        f['ordinary_expected']['given_time_at_dose_weeks']=1
        f['ordinary_expected'].pop('given_time_at_dose_days',None)
    f['ordinary_expected']['calculator_execution_tested']=False
flow['question_count_policy']['short_individual_path_proven_for_all_usual_rules']=False
flow['actual_path_assessment']='Some source displays fit 5–10; most individual start/adjust branches exceed 10 once all independent source gates are explicit. Criterion18 remains partial.'
flow['complex_flows']=[dict(rule_ids=[c['rule_id']],count_without_relevant_maoi_history=c['required_known_branch_fields'],
    reason='Independent source applicability inputs; no blanket clearance. MAOI history and renal operands counted separately.') for c in counts if c['required_known_branch_fields']>10]
dump(R/'question_flows.yaml',flow)
matrix=yaml.safe_load((R/'switch_matrix.yaml').read_text(encoding='utf-8'))
for d in matrix['directions']:
    d['source_currency_status']='latest_registration_revision_not_confirmed'
    if 'RU-ESC' in d['source_refs']:d['transfer_status']='blocked_current_RU_ESC_original';d['numeric_pair_result']=None
    else:d['transfer_status']='source_direction_constraint_only; pair calendar only selected explicitly justified example'
dump(R/'switch_matrix.yaml',matrix)
anchor=yaml.safe_load((R/'source_transfer_audit.yaml').read_text(encoding='utf-8'))
anchor['nature']='Internal consistency anchors only; their equality is not independent medical verification. Available-original review evidence is in remediation/parameter_review.csv; source currency remains separate.'
anchor['parameter_anchors']=[{'rule_id':r['rule_id'],**{k:p[k] for k in ['parameter_id','value','lower','upper','unit','source_ref','source_locator']}} for r in rules for p in r['clinical_parameters']]
dump(R/'source_transfer_audit.yaml',anchor)
review=[];cards=[];conds=[]
for r in rules:
    rid=r['rule_id'];blocked='RU-ESC' in [s['source_id'] for s in r['sources']]
    cards.append(dict(rule_id=rid,available_original_numeric_review='blocked_RU_ESC' if blocked else 'available original relevant sections reviewed',
        clinical_parameters=len(r['clinical_parameters']),source_current_revision='not independently confirmed for product labels',
        result_contract='result_contracts.yaml#rules/'+rid,full_scenarios='full_scenarios.json',clinical_validation='not_performed',
        transfer_limit='no current ESC result' if blocked else 'only source-bound branches; latest registration revision open'))
    for p in r['clinical_parameters']:
        sid=p['source_ref'];s=S[sid]
        note='Current original unavailable; no predicate verified' if sid=='RU-ESC' else 'Compared with primary document dose/form/age section; anchor equality is a separate technical check'
        if 'duration_semantics' in p:note+='; source duration operator separately reviewed, no 2-week hard ceiling'
        review.append(dict(rule_id=rid,parameter_id=p['parameter_id'],value=json.dumps(p['value'],ensure_ascii=False),lower=p['lower'],upper=p['upper'],unit=p['unit'],
            source_id=sid,version=s['version_or_update_date'],locator=p['source_locator'],local_file=s.get('local_file'),sha256=s.get('document_fingerprint',{}).get('sha256'),
            available_original_review='unverified' if sid=='RU-ESC' else 'confirmed relevant source statement',latest_registration_revision='not confirmed' if s['source_type']!='guideline' else 'current catalog entry separately recorded',note=note))
    for i in r['inputs']:
        conds.append(dict(rule_id=rid,input_id=i['input_id'],question=i['question_ru'],data_type=i['data_type'],unit=i['unit'],
            source_refs=' | '.join(i['source_refs']),locator=i.get('source_locator','see source exact_locator'),condition_contract='result_contracts.yaml#rules/'+rid,
            known_false='explicit boolean false, not missing' if i['data_type']=='boolean' else 'source-specific category/value',
            missing_result='insufficient_data; request specific applicable field; no individual dose',
            source_verification='unverified ESC dependency' if blocked else 'available original; latest revision separately unresolved'))
csvwrite(O/'card_review.csv',cards);csvwrite(O/'parameter_review.csv',review);csvwrite(O/'condition_review.csv',conds)
print('Synced indexes, honest question counts, matrix/source limits and review ledgers.')
