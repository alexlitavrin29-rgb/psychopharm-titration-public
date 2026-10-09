"""Refresh current indices and trace links; earlier reports are read-only."""
from pathlib import Path
import yaml,json,csv
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2'
def dump(p,x):p.write_text(yaml.safe_dump(x,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def csvsave(p,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rules=[yaml.safe_load(p.read_text(encoding='utf-8')) for p in sorted((R/'rules').glob('*.yaml'))]
cons=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'))['rules']
S=json.loads((R/'sources.json').read_text(encoding='utf-8'))
idx=yaml.safe_load((R/'test_cases.yaml').read_text(encoding='utf-8'));idx['cases']=[{'rule_id':r['rule_id'],**c} for r in rules for c in r['test_cases']];dump(R/'test_cases.yaml',idx)
with (R/'input_catalog.csv').open(encoding='utf-8-sig',newline='') as f:
    rd=csv.DictReader(f);old=list(rd);cols=rd.fieldnames
ids={r['rule_id'] for r in rules};rows=[row for row in old if row['rule_id'] not in ids]
trace=[];cards=[]
for r in rules:
    rid=r['rule_id']
    for i in r['inputs']:
        raw={'rule_id':rid,**i};rows.append({k:json.dumps(raw[k],ensure_ascii=False) if isinstance(raw.get(k),(dict,list)) else raw.get(k,'') for k in cols})
        trace.append(dict(rule_id=rid,input_id=i['input_id'],question=i['question_ru'],data_type=i['data_type'],unit=i['unit'],source_refs=' | '.join(i['source_refs']),
            versions=' | '.join(S[s]['version_or_update_date'] for s in i['source_refs']),locator=i['source_locator'],predicate=json.dumps(i['requirement_predicate'],ensure_ascii=False),
            reason=i['necessity_reason'],fact_origin=i['fact_origin'],reused_fact_policy='Explicit current-calculation provenance only; no inferred normality',
            contract='result_contracts.yaml#rules/'+rid,full_expected='full_scenarios.json',review_depth='current ESC primary reviewed' if any(s['source_id']=='RU-ESC' for s in r['sources']) else 'SER/PREG cessation necessity reviewed' if rid.startswith('ser') or rid=='preg-taper-limit' else 'explicit full branch, minimum not asserted'))
    cards.append(dict(rule_id=rid,inputs=len(r['inputs']),parameters=len(r['clinical_parameters']),branches=len(cons[rid]['branches']),
        question_graph='question_graphs.yaml#'+rid,contract='result_contracts.yaml#rules/'+rid,full_expected='full_scenarios.json',clinical_validation='not_performed',
        source_currency=' | '.join(s['source_id']+': '+('current official edition verified' if S[s['source_id']].get('latest_registration_revision_confirmed') else 'product edition currency unresolved' if S[s['source_id']]['source_type']=='label' else 'current guideline separately checked') for s in r['sources'])))
csvsave(R/'input_catalog.csv',rows);csvsave(O/'input_necessity.csv',trace);csvsave(O/'card_review.csv',cards)
counts=json.loads((R/'question_counts.json').read_text(encoding='utf-8'))
for n in counts:
    r=next(r for r in rules if r['rule_id']==n['rule_id']);n['clinical_input_entries']=len(r['inputs']);n['all_catalog_fields_count']=len(r['inputs'])+n['initial_selections']
    n['required_known_branch_fields']=len(cons[n['rule_id']]['required_inputs'])+n.get('independent_renal_subfields_extra',0)+n.get('independent_A_B_allergy_extra',0)+n['initial_selections']
save(R/'question_counts.json',counts)
flows=yaml.safe_load((R/'question_flows.yaml').read_text(encoding='utf-8'))
for f in flows['flows']:
    r=next(r for r in rules if r['rule_id']==f['rule_id']);known=set(f['clinical_questions']);f['conditional_questions']=[i['input_id'] for i in r['inputs'] if i['input_id'] not in known]
    f['input_units']={i['input_id']:i['unit'] for i in r['inputs']}
    f['individual_result_required_fields']=cons[f['rule_id']]['required_inputs'];f['individual_result_count_without_maoi_history']=next(n['required_known_branch_fields'] for n in counts if n['rule_id']==f['rule_id'])
    if f['rule_id']=='esc-gad-start':f.update(clinical_output='reference_only_source_scheme',ordinary_expected={'reference_only':True,'individual_dose':None,'all_patient_safety_checks_completed':False,'calculator_execution_tested':False},if_complex='Current original verified; full source-specific applicability fields and CLcr exact30 gap remain explicit. Full path in round2 graph.')
dump(R/'question_flows.yaml',flows)
matrix=yaml.safe_load((R/'switch_matrix.yaml').read_text(encoding='utf-8'))
for d in matrix['directions']:
    if 'RU-ESC' in d['source_refs']:
        d['transfer_status']='source-specific directional constraints; no complete automatic pair calendar'
        d['source_currency_status']='Current RU-ESC edition verified; other used product editions checked separately'
        d['numeric_pair_result']=None
dump(R/'switch_matrix.yaml',matrix)
anchor=yaml.safe_load((R/'source_transfer_audit.yaml').read_text(encoding='utf-8'))
anchor['parameter_anchors']=[{'rule_id':r['rule_id'],**{k:p[k] for k in ['parameter_id','value','lower','upper','unit','source_ref','source_locator']}} for r in rules for p in r['clinical_parameters']]
dump(R/'source_transfer_audit.yaml',anchor)
print('Current input/fragment/parameter/matrix indices refreshed; 38 trace rows and all input necessity links prepared.')
