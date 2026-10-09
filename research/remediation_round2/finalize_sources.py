from pathlib import Path
import json,hashlib
import yaml
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2'
S=json.loads((R/'sources.json').read_text(encoding='utf-8'));s=S['RU-SER']
cmp=json.loads((O/'zoloft_comparison.json').read_text(encoding='utf-8'))
assert cmp['documents'][0]['byte_identity_to_previously_read_original']
cmp['confirmation_pending']=None
cmp['confirmation']='Downloaded by the user in response to a specific request for the current official registry SmPC; filename and stamp match the previously observed registry edition. Complete bytes equal the read manufacturer original. Page1 visually verified again; initial registry date differs from current document stamp.'
(O/'zoloft_comparison.json').write_text(json.dumps(cmp,ensure_ascii=False,indent=2),encoding='utf-8')
s.update(latest_registration_revision_confirmed=True,latest_registry_document_comparison=cmp,evidence_limitations='Current registry original provided by the user after CAPTCHA; complete byte identity to the read manufacturer original verified. Current stamp, exact product and form visually checked. This is document-version evidence, not clinical validation.')
s['dates']=dict(initial_registration='2023-07-24',registration_stamp='2026-06-11',expert_report='2026-05-29',revision=None,approval=None,publication=None,download='2026-10-08',filename_dates_not_used=['21.04.26','24-apr-2025'])
for cp in s['document_copies']:cp['latest_registration_revision_confirmed']=True
for row in cmp['documents']:
    cp=dict(row,download_date='2026-10-08',latest_registration_revision_confirmed=True)
    if row['document_type']=='SmPC':cp.update(version=s['version_or_update_date'],byte_identity_to_primary_snapshot=True)
    else:cp['role']='Patient leaflet, separate from the dose basis'
    s['document_copies'].append(cp)
(R/'sources.json').write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8')
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'))
for folder in ['rules','findings','reference_rules']:
    for p in (R/folder).glob('*.yaml'):
        r=yaml.safe_load(p.read_text(encoding='utf-8'));r['sources']=[S[x['source_id']] for x in r['sources']]
        if folder=='rules':
            for i in r['inputs']:i['required_for_individual_result']=i['requirement_predicate']['kind']=='always'
            if not r['logic'].get('maoi_history_contract'):r['logic'].pop('maoi_history_contract',None)
        p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
print('SER current registry identity confirmed; all requirement flags are Boolean with independent predicates retained.')
