"""Independent source/expected spot checks; does not read the contract generator or calculate prescriptions."""
from pathlib import Path
import json,re,hashlib
import fitz
R=Path(__file__).resolve().parents[1];O=R/'remediation_round3'
S=json.loads((O/'sources.json').read_text(encoding='utf-8'))
cases={c['case_id']:c for c in json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))['cases']}
rows=[]
def page(sid,n):return ' '.join(fitz.open(R/S[sid]['local_file'])[n-1].get_text().split())
def check(cid,sid,n,source_fact,source_present,expected_predicate):
    c=cases.get(cid);ok=bool(c) and source_present and expected_predicate(c)
    rows.append(dict(case_id=cid,source_ref=sid,version=S[sid]['version_or_update_date'],physical_page=n,
        source_fact=source_fact,source_text_condition_confirmed=source_present,expected_agrees=ok,
        primary_sha256=hashlib.sha256((R/S[sid]['local_file']).read_bytes()).hexdigest(),
        nature='Manually authored fact/predicate compared directly to original and prepared expected; not generated from result_contract',calculator_executed=False))

t=page('RU-ESC',3)
check('esc-gad-start--current-clcr-30','RU-ESC',3,'Source defines strictly >30 and <30, leaves exact30 unassigned',
      'более 30 мл/мин' in t and 'менее 30 мл/мин' in t and 'менее или равно' not in t,
      lambda c:c['given']['renal']['value']==30 and c['expected']['result_type']=='clinician_choice' and c['expected']['total_daily_dose_mg'] is None)
check('esc-elderly-start--current-age-65','RU-ESC',3,'Special age is strictly older than65',
      'старше 65 лет' in t,lambda c:c['given']['age']==65 and c['expected']['result_type']=='clinician_choice')
check('esc-elderly-start--current-age-66','RU-ESC',3,'Special start5 and maximum10',
      '5 мг/сут' in t and '10 мг/сут' in t,lambda c:c['expected']['total_daily_dose_mg']==5 and c['expected']['maximum_mg']==10)
for cat in ['A','B']:
    check('esc-hepatic-start--current-hepatic-Child-Pugh_'+cat,'RU-ESC',3,'Child–Pugh A/B initial5 for two weeks, possible10 by response',
          'класс А или В' in t and 'первых двух недель' in t,
          lambda c:c['expected']['total_daily_dose_mg']==5 and c['expected']['initial_period_weeks']==2 and c['expected']['conditional_next_total_mg']==10)
check('esc-hepatic-start--current-hepatic-Child-Pugh_C','RU-ESC',3,'Class C close supervision, no numerical formula',
      'класс С' in t and 'пристальным контролем' in t,lambda c:c['expected']['result_type']=='clinician_choice' and c['expected']['total_daily_dose_mg'] is None)
check('esc-cyp2c19-start--current-branch-special','RU-ESC',3,'Known weak CYP initial5, two weeks, possible10',
      'слабой активностью' in t and 'первых двух недель' in t,lambda c:c['expected']['total_daily_dose_mg']==5 and c['expected']['initial_period_weeks']==2)
t=page('RU-ESC',2)
check('esc-panic-start--current-branch-usual','RU-ESC',2,'Panic first week5 then10; not a universal escalation step',
      'первой недели' in t and '5 мг/сут' in t and '10 мг/сут' in t,
      lambda c:[x['total_daily_mg'] for x in c['expected']['schedule']]==[5,10] and c['expected']['schedule'][1]['conditional'] is True)
for rid in ['esc-gad-start','esc-social-start']:
    check(rid+'--current-branch-usual','RU-ESC',2,'Usual10, maximum20; no fixed next increment/interval',
          '10 мг один раз в сутки' in t and '20 мг/сут' in t,
          lambda c:c['expected']['total_daily_dose_mg']==10 and c['expected']['maximum_mg']==20 and c['expected']['automatic_increment_mg'] is None)
t=page('RU-ESC',8)
check('esc-gad-start--current-contra-QT_prolonging','RU-ESC',8,'Simultaneous QT-prolonging drug use contraindicated',
      'противопоказано одновременное применение' in t and 'удлиняющими интервал QT' in t,
      lambda c:c['expected']['result_type']=='not_applicable' and c['expected']['total_daily_dose_mg'] is None)
t=page('RU-ESC',6)
check('esc-gad-start--current-arrhythmia_signs-stop','RU-ESC',6,'Arrhythmia: stop therapy and obtain ECG',
      'прекратить' in t and 'ЭКГ' in t,
      lambda c:any(x['action']=='obtain_ECG' for x in c['expected'].get('source_actions',[])))
check('esc-gad-start--current-serotonin_syndrome_signs-stop','RU-ESC',6,'Serotonin syndrome: immediately stop SSRI and serotonergic drugs, start symptomatic treatment',
      'симптоматическое лечение' in t and 'серотонинергическими' in t,
      lambda c:{x['action'] for x in c['expected'].get('source_actions',[])}=={'immediately_discontinue_SSRI_and_current_serotonergic_drugs','start_symptomatic_treatment_by_clinician'})
check('esc-taper-limit--current-branch-source_limit','RU-ESC',6,'Several weeks/months according to state; 1–2 is not a hard ceiling',
      'нескольких недель или месяцев' in t,
      lambda c:c['expected']['duration_constraint']['hard_upper_limit_weeks'] is None and c['expected']['full_taper_calendar'] is None)
t=page('RU-SER',2)
check('ser-adult-adjust--round2-minimal-selected-action','RU-SER',2,'Selected increase100→150 follows +50; interval at least a week; unassessed monitoring retained',
      'с шагом 50 мг' in t and 'не менее одной недели' in t,
      lambda c:c['given']['current_dose']==100 and c['expected']['total_daily_dose_mg']==150 and c['expected']['unassessed_context'] and c['expected']['clinical_clearance'] is False)
t=page('RU-SER',4)
check('ser-adult-adjust--round2-active-mania-stop','RU-SER',4,'Active manic phase requires cessation, not a dose coefficient',
      'маниакальную фазу' in t and 'следует прекратить' in t,
      lambda c:c['expected']['result_type']=='source_stop_action' and c['expected']['stop_medication']=='RU-SER')
t=page('RU-AGO',3)
check('ago-depression-start--ALT_ratio-3.0' if 'ago-depression-start--ALT_ratio-3.0' in cases else 'ago-depression-start--ALT_ratio-3','RU-AGO',3,'Exactly3 is caution, greater3 excludes start; ALT and AST independent',
      'не более чем в 3 раза' in t and 'АЛТ и/или АСТ' in t,lambda c:c['expected']['result_type']=='clinician_choice')
t=page('RU-PAROX',3)
check('parox-panic-kr--branch-usual','RU-PAROX',3,'Panic initial10 independent of prior treatment response',
      'начинать с дозы 10 мг' in t,lambda c:c['expected']['total_daily_dose_mg']==10)
t=page('RU-PREG',6)
check('preg-taper-limit--stop-RU-PREG-angioedema','RU-PREG',6,'Angioedema requires immediate cessation',
      'немедленно прекратить' in t and 'ангионевротического' in t,
      lambda c:c['expected']['result_type']=='source_stop_action' and c['expected']['stop_medication']=='RU-PREG')
report=dict(status='pass' if all(r['expected_agrees'] for r in rows) else 'fail',checked_primary_cases=len(rows),
    scope='Independent key positive, boundary, contraindication and stop expectations; not exhaustive independent medical review',
    calculator_tests_executed=False,clinical_validation='not_performed',cases=rows)
(O/'primary_expected_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':len(rows),'failures':[r['case_id'] for r in rows if not r['expected_agrees']]},ensure_ascii=False))
raise SystemExit(report['status']!='pass')
