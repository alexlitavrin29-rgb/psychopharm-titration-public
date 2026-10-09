"""Promote synchronized research data; preserve previous audits and downloaded originals."""
from pathlib import Path
import json,yaml,csv,hashlib
O=Path(__file__).resolve().parent;R=O.parent
def sy(p,x):p.write_text(yaml.safe_dump(x,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
def sj(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['sources.json','renal_estimator.yaml']:(R/name).write_bytes((O/name).read_bytes())
rules=[]
for p in sorted((O/'rules').glob('*.yaml')):
    (R/'rules'/p.name).write_bytes(p.read_bytes());rules.append(yaml.safe_load(p.read_text(encoding='utf-8')))
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'))['rules']; P=json.loads((O/'actual_question_paths.json').read_text(encoding='utf-8'))
with (R/'input_catalog.csv').open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);cols=reader.fieldnames
    extra_rows=[x for x in reader if x['rule_id'] not in {r['rule_id'] for r in rules}]
with (R/'input_catalog.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
    for r in rules:
        for i in r['inputs']:
            x=dict(rule_id=r['rule_id'],**i);w.writerow({k:json.dumps(x[k],ensure_ascii=False) if isinstance(x.get(k),(dict,list)) else x.get(k,'') for k in cols})
    w.writerows(extra_rows)
idx=yaml.safe_load((R/'test_cases.yaml').read_text(encoding='utf-8'));idx['cases']=[dict(rule_id=r['rule_id'],**c) for r in rules for c in r['test_cases']];idx['complete_expected_ref']='remediation_round3/full_scenarios.json';sy(R/'test_cases.yaml',idx)
sj(R/'question_counts.json',[dict(rule_id=r['rule_id'],clinical_input_entries=len(r['inputs']),initial_selections=4 if r['identity']['mode']=='switch' else 3,ordinary_complete_counts=sorted(set(p['count'] for p in P if p['rule_id']==r['rule_id'] and p['ordinary_individual_numeric_path'])),full_paths_ref='remediation_round3/actual_question_paths.json',target=10,preferred_ordinary_maximum=15,ordinary_maximum=None,acceptance_version=3,count_includes_initial_choices=True,no_hidden_preliminary_questionnaire=True) for r in rules])
sy(R/'question_flows.yaml',dict(active_snapshot='remediation_round3/final_manifest.json',scope='Research graphs, no implemented dialogue',clinical_clearance_claimed=False,calculator_implemented=False,question_count_policy=dict(unasked_is_normal=False,universal_risk_confirmation_checkbox_allowed=False,target=10,preferred_ordinary_maximum=15,ordinary_maximum=None,acceptance_version=3,necessity_still_required=True),flows=[dict(rule_id=r['rule_id'],graph_ref='remediation_round3/question_graphs.yaml#'+r['rule_id'],input_contract_ref='remediation_round3/input_contracts.yaml',result_contract_ref='remediation_round3/result_contracts.yaml#rules/'+r['rule_id'],paths_ref='remediation_round3/actual_question_paths.json',required_inputs=C[r['rule_id']]['required_inputs'],input_requirements=C[r['rule_id']]['input_requirements']) for r in rules]))
matrix=yaml.safe_load((R/'switch_matrix.yaml').read_text(encoding='utf-8'));matrix['active_snapshot']='remediation_round3/final_manifest.json'
for d in matrix['directions']:d['source_currency_status']='Active product originals obtained; exact RU/edition/hash in remediation_round3/sources.json; pair gaps remain explicit'
sy(R/'switch_matrix.yaml',matrix)
a=yaml.safe_load((R/'source_transfer_audit.yaml').read_text(encoding='utf-8'));a['active_snapshot']='remediation_round3/final_manifest.json';a['parameter_anchors']=[dict(rule_id=r['rule_id'],**{k:p[k] for k in ['parameter_id','value','lower','upper','unit','source_ref','source_locator']}) for r in rules for p in r['clinical_parameters']];a['current_review_ref']='remediation_round3/primary_review_notes.md';a['independent_acceptance_ref']='acceptance_v3_audit/final_review/';sy(R/'source_transfer_audit.yaml',a)
S=json.loads((O/'sources.json').read_text(encoding='utf-8'))
sj(O/'version_inventory.json',[dict(source_id=s,registration=v.get('doi_or_registry_id'),version=v['version_or_update_date'],local_file=v.get('local_file'),sha256=v.get('document_fingerprint',{}).get('sha256'),latest_registration_revision_confirmed=v.get('latest_registration_revision_confirmed',False),own_read_scope=v.get('own_read_scope'),currency_evidence=v.get('latest_registry_document_comparison',v.get('current_guideline_status_evidence')),unread_content_not_claimed_verified=True) for s,v in S.items()])
sj(O/'coverage_map.json',[dict(rule_id=r['rule_id'],source_ids=[s['source_id'] for s in r['sources']],parameter_count=len(r['clinical_parameters']),input_count=len(r['inputs']),branch_ids=[b['branch_id'] for b in C[r['rule_id']]['branches']],source_review='primary_review_notes.md',necessity_decisions='necessity_decisions.json',per_result_input_ledger='input_necessity.csv',prepared_expected='full_scenarios.json',calculator_execution=False) for r in rules])
old=json.loads((O/'baseline_manifest.json').read_text(encoding='utf-8'));changes=[]
for row in old['files']:
    p=R.parent/row['path']
    if p.is_file():
        sha=hashlib.sha256(p.read_bytes()).hexdigest()
        if sha!=row['sha256']:changes.append(dict(path=row['path'],old_sha256=row['sha256'],new_sha256=sha,protected=row['protected']))
sj(O/'changes_manifest.json',changes)
print('Promoted current 38 cards/sources and synchronized indices. Historical audits, canonical criteria and old originals unchanged.')
