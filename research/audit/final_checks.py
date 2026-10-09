import csv, hashlib, json, re
from pathlib import Path
from bs4 import BeautifulSoup
import yaml

A=Path(__file__).resolve().parent
P=A.parent
records=json.loads((A/'external_fetch_results.json').read_text(encoding='utf-8'))
for rec in records:
    if rec['source_id']=='RU-CITAL-LV' and rec.get('stored','').endswith('.html'):
        old=A/rec['stored']; new=old.with_suffix('.docx')
        if old.exists(): old.rename(new)
        rec['stored']=str(new.relative_to(A))
(A/'external_fetch_results.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')

renal=[]
for filename,divisor,key in [('renal_estimator.yaml',1,'serum_creatinine_umol_L'),('renal_estimator_archive.yaml',72,'serum_creatinine_mg_dL')]:
    obj=yaml.safe_load((P/filename).read_text(encoding='utf-8'))
    for c in obj['test_cases']:
        g=c['given']; exp=c['expected']
        if key not in g:
            renal.append(dict(file=filename,case_id=c['case_id'],review='не числовой полный пример; ограничение неверной единицы/формы подтверждено оригиналом',executed_calculator=False))
            continue
        factor=1.23 if divisor==1 else 1
        calculated=factor*(140-g['age_years'])*g['mass_kg']/(divisor*g[key])
        if g['source_sex_category']=='женщина по категории формулы': calculated*=0.85
        assert abs(calculated-exp['estimated_CLcr_mL_min'])<1e-9
        renal.append(dict(file=filename,case_id=c['case_id'],calculated=calculated,expected=exp['estimated_CLcr_mL_min'],arithmetic_matches=True,executed_calculator=False))
(A/'independent_renal_arithmetic.json').write_text(json.dumps(renal,ensure_ascii=False,indent=2),encoding='utf-8')
html=[]
for name in ['IR','XR']:
    original=P/'source_snapshots'/f'velaxin-{name}.html'
    fresh=A/'retrieved'/f'RU-VENLA-{name}.html'
    normalize=lambda f: BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser').get_text(' ',strip=True)
    html.append(dict(source='RU-VENLA-'+name,normalized_visible_text_equal=normalize(original)==normalize(fresh),
                     note='Текстовое совпадение не подтверждает последнюю утверждённую регистрацию'))
(A/'independent_html_comparison.json').write_text(json.dumps(html,ensure_ascii=False,indent=2),encoding='utf-8')

manifest=json.loads((A/'baseline_manifest.json').read_text(encoding='utf-8'))
changed=[];missing=[]
for entry in manifest:
    file=P/entry['file']
    if not file.exists(): missing.append(entry['file']); continue
    if hashlib.sha256(file.read_bytes()).hexdigest()!=entry['sha256']: changed.append(entry['file'])
current={str(x.relative_to(P)).replace('\\','/') for x in P.rglob('*') if x.is_file() and A not in x.parents}
baseline={x['file'].replace('\\','/') for x in manifest}
new=sorted(current-baseline)
original=json.loads((A/'original_acceptance_audit.json').read_text(encoding='utf-8'))
accept_sha=hashlib.sha256((P.parent/'psychopharm_codex_pack/ACCEPTANCE.md').read_bytes()).hexdigest()
acceptance_unchanged=accept_sha==original['acceptance_sha256']
preservation=dict(baseline_files=len(manifest),changed=changed,missing=missing,new_outside_audit=new,
                  original_acceptance_sha256=original['acceptance_sha256'],current_acceptance_sha256=accept_sha,acceptance_unchanged=acceptance_unchanged,
                  originals_preserved=not changed and not missing and not new and acceptance_unchanged)
(A/'preservation_check.json').write_text(json.dumps(preservation,ensure_ascii=False,indent=2),encoding='utf-8')
assert preservation['originals_preserved'],preservation

expected={'02_findings.csv':13,'03_source_verification.csv':30,'06_card_review.csv':38,'06_parameter_review.csv':195,'07_case_contract_review.csv':124}
for filename,count in expected.items():
    rows=list(csv.DictReader((A/filename).open(encoding='utf-8-sig')))
    assert len(rows)==count,(filename,len(rows),count)
criteria=json.loads((A/'independent_acceptance.json').read_text(encoding='utf-8'))
assert len(criteria['criteria'])==30
broken=[]
for f in A.glob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)',f.read_text(encoding='utf-8')):
        if '://' not in target and not (f.parent/target).exists(): broken.append(dict(file=f.name,target=target))
assert not broken,broken
result=dict(audit_artifact_counts=expected,acceptance_count=30,acceptance_status_counts=criteria['counts'],local_links_valid=True,
            originals_preserved=True,weighted_raw_score=6.275,capped_score=6.0,medical_execution_or_clinical_validation=False)
(A/'audit_artifact_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(preservation,ensure_ascii=False,indent=2))
