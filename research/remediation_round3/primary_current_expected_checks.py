"""Manually selected new primary facts versus expected; independent of preparation scripts."""
from pathlib import Path
import hashlib,json,re,fitz,yaml
O=Path(__file__).resolve().parent;R=O.parent
S=json.loads((O/'sources.json').read_text(encoding='utf-8'))
F={c['case_id']:c for c in json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))['cases']}
rows=[]
def page(sid,n):
    text=' '.join(fitz.open(R/S[sid]['local_file'])[n-1].get_text().split())
    return re.sub(r'(?<=[А-Яа-яёЁ])-\s+(?=[А-Яа-яёЁ])','',text)
def check(cid,sid,n,fact,phrases,predicate):
    t=page(sid,n);c=F.get(cid);present=all(p in t for p in phrases)
    rows.append(dict(case_id=cid,source_ref=sid,source_version=S[sid]['version_or_update_date'],source_sha256=S[sid]['document_fingerprint']['sha256'],physical_page=n,fact=fact,source_condition_confirmed=present,prepared_expected_agrees=present and bool(c) and predicate(c),calculator_executed=False))
check('dulox-gad-start--branch-usual','RU-DULOX',2,'GAD initial30, not obligatory future calendar',['30 мг'],lambda c:c['expected']['total_daily_dose_mg']==30 and c['expected']['automatic_day_for_60'] is None)
check('dulox-gad-start--branch-comorbid','RU-DULOX',2,'Comorbid depression initial60',['60 мг','депресс'],lambda c:c['expected']['total_daily_dose_mg']==60)
check('dulox-gad-start--branch-elderly','RU-DULOX',3,'Elderly GAD30 for2 weeks before target60',['30 мг в сутки в течение 2 недель','60 мг'],lambda c:c['expected']['total_daily_dose_mg']==30)
check('dulox-taper-limit--branch-source_limit','RU-DULOX',6,'At least2 weeks in §4.4, no hard ceiling',['на протяжении не менее 2 недель'],lambda c:c['expected']['duration_constraint']['chosen_minimum_weeks']==2 and c['expected']['duration_constraint']['hard_upper_limit_weeks'] is None)
check('fluvox-depression-start--branch-selected50','RU-FLUVOX',1,'Current form explicitly permits equal doses; halves specified §4.2 p3',['разделить на равные дозы'],lambda c:c['given']['form']['strengths_mg']==[50,100] and c['expected']['total_daily_dose_mg']==50)
check('fluvox-depression-start--r3-serotonin_syndrome_signs-positive','RU-FLUVOX',5,'Cessation plus symptomatic treatment',['лечение флувоксамином должно быть прекращено','симптоматическое лечение'],lambda c:c['expected']['stop_medication']=='RU-FLUVOX' and {a['action'] for a in c['expected']['source_actions']}=={'discontinue_selected_medication','start_symptomatic_treatment_by_clinician'})
check('parox-panic-kr--branch-elderly','RU-PAROX',4,'Elderly max40; lower therapeutic range in severe renal/hepatic impairment',['40 мг в сутки'],lambda c:c['expected']['maximum_mg']==40)
check('parox-panic-kr--branch-usual','RU-PAROX',4,'20mg tablet half allows10mg',['делить таблетку пополам','10 мг'],lambda c:c['expected']['total_daily_dose_mg']==10 and c['given']['form']['strengths_mg']==[20])
check('preg-gad-start--r3-misuse_risk_assessment-unknown','RU-PREG',9,'Specific risk of misuse assessed before prescribing',['Перед назначением прегабалина следует тщательно оценить риск','злоупотребления'],lambda c:c['expected']['result_type']=='insufficient_data' and c['expected']['missing_fields']==['misuse_risk_assessment'])
check('preg-gad-start--r3-effective_contraception-negative','RU-PREG',12,'Effective contraception for reproductive population',['должны использовать эффективную контрацепцию'],lambda c:c['given']['reproductive_population'] is True and c['expected']['result_type']=='clinician_choice' and c['expected']['total_daily_dose_mg'] is None)
check('venla-xr-gad-start--branch-usual','RU-VENLA-XR',2,'GAD75; max225, minimum2 weeks for possible increase',['75 мг','225 мг','2 недели'],lambda c:c['expected']['total_daily_dose_mg']==75)
check('venla-xr-panic-form-limit--branch-form_limit','RU-VENLA-XR',5,'Whole capsules must not be divided',['Капсулы нельзя делить'],lambda c:c['expected']['result_type']=='form_not_feasible')
check('venla-xr-gad-start--r3-current_allergic_reaction-positive','RU-VENLA-XR',13,'Rash/urticaria/allergic reaction cessation',['крапивницы','прекратить'],lambda c:c['expected']['stop_medication']=='RU-VENLA-XR')
check('phen-taper-limit--r3-unusual_reactions-positive','RU-PHEN',4,'Unusual reactions require cessation; emergency numerical taper not specified',['лечение следует прекратить'],lambda c:c['expected']['result_type']=='source_stop_action' and c['expected']['total_daily_dose_mg'] is None)
check('phen-taper-limit--branch-source_limit','RU-PHEN',1,'Score is not intended for division',['не предназначена для разделения таблетки'],lambda c:c['expected']['full_taper_calendar'] is None)
report=dict(status='pass' if all(r['prepared_expected_agrees'] for r in rows) else 'fail',checked_primary_cases=len(rows),cases=rows,scope='New clinically material facts and expected independently of generator; not exhaustive all-condition review')
(O/'primary_current_expected_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(report['status'],'failures:',[r['case_id'] for r in rows if not r['prepared_expected_agrees']]);raise SystemExit(report['status']!='pass')
