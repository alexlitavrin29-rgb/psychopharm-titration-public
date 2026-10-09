"""Проверка структуры исследовательского пакета. Не калькулятор медицинской дозы."""
from pathlib import Path
import csv
import json
import re
import sys
import yaml
import hashlib

ROOT = Path(__file__).resolve().parent
REQUIRED = [f'{i:02d}_{name}.md' for i, name in enumerate([
    'summary', 'scope_and_sources', 'rules', 'question_flows', 'switch_matrix',
    'gaps_and_conflicts', 'implementation_brief', 'acceptance'])]
REQUIRED += ['search_log.csv', 'sources.json', 'test_cases.yaml',
             'input_catalog.csv', 'question_counts.json', 'minzdrav_catalog_snapshot.json',
             'ru_source_policy.yaml', 'renal_estimator.yaml', 'reference_test_cases.yaml',
             '08_russian_priority_update.md', 'reference_rules/README.md']
REQUIRED += ['question_flows.yaml', 'switch_matrix.yaml', 'coverage.csv',
             'depression_dose_table.csv', 'finding_cases.yaml', 'renal_estimator_archive.yaml',
             '10_source_audit.md', 'source_transfer_audit.yaml', 'acceptance_audit.json']
errors = []

def check(condition, message):
    if not condition:
        errors.append(message)

for name in REQUIRED:
    check((ROOT / name).is_file(), f'Missing file: {name}')
sources = json.loads((ROOT / 'sources.json').read_text(encoding='utf-8'))
template = yaml.safe_load((ROOT.parent / 'psychopharm_codex_pack' / 'RULE_TEMPLATE.yaml').read_text(encoding='utf-8'))
rules = [yaml.safe_load(p.read_text(encoding='utf-8')) for p in sorted((ROOT / 'rules').glob('*.yaml'))]
references = [yaml.safe_load(p.read_text(encoding='utf-8')) for p in sorted((ROOT / 'reference_rules').glob('*.yaml'))]
findings = [yaml.safe_load(p.read_text(encoding='utf-8')) for p in sorted((ROOT / 'findings').glob('*.yaml'))]
policy = yaml.safe_load((ROOT / 'ru_source_policy.yaml').read_text(encoding='utf-8'))
check(policy['country'] == 'RU', 'Project country must be RU')
check(policy['foreign_numeric_fallback_allowed'] is False, 'Foreign numeric fallback must be disabled')
check(policy['foreign_reference_auto_selection_allowed'] is False, 'Foreign reference auto-selection must be disabled')
check(policy['active_rule_directory'] == 'rules' and policy['foreign_reference_directory'] == 'reference_rules', 'Profile directory mismatch')
for name in ['PROJECT_BRIEF.md', 'AGENTS.md']:
    check((ROOT.parent / name).is_file(), f'Missing project policy document: {name}')
ids = [r['rule_id'] for r in rules]
check(len(ids) == len(set(ids)), 'Duplicate rule_id')
check({'start', 'adjust', 'taper', 'switch'} <= {r['identity']['mode'] for r in rules}, 'Missing clinical mode')

def source_refs(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == 'source_ref' and value:
                yield value
            elif key == 'source_refs':
                yield from value
            else:
                yield from source_refs(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from source_refs(value)

flattened_cases = []
for r in rules:
    rid = r['rule_id']
    identity = r['identity']
    check(bool(identity['formulation'] and identity['route'] and identity['diagnosis_code'] and r['applicability']['population_description']), f'{rid}: missing concrete applicability')
    check(bool(identity['drug_inn']) or (identity['mode'] == 'switch' and identity['from_drug_inn'] and identity['to_drug_inn']), f'{rid}: missing medicine identity')
    check(r['profile']['country'] == 'RU' and r['profile']['foreign_fallback_allowed'] is False, f'{rid}: incorrect RU profile')
    check(set(template) <= set(r), f'{rid}: missing template fields')
    for section in ['identity', 'applicability', 'logic', 'output', 'verification']:
        check(set(template[section]) <= set(r[section]), f'{rid}: missing {section} fields')
    local_sources = {s['source_id'] for s in r['sources']}
    check(local_sources <= set(sources), f'{rid}: unregistered source')
    check(all(s == sources.get(s['source_id']) for s in r['sources']), f'{rid}: stale source metadata')
    for ref in source_refs(r):
        check(ref in local_sources, f'{rid}: source absent from local sources: {ref}')
    pids = [p['parameter_id'] for p in r['clinical_parameters']]
    check(len(pids) == len(set(pids)), f'{rid}: duplicate clinical parameter')
    check(set(r['logic']['parameter_refs']) == set(pids), f'{rid}: parameter catalogue mismatch')
    for p in r['clinical_parameters']:
        check(sources.get(p['source_ref'], {}).get('jurisdiction') in ['RU', 'RU/EAEU'], f'{rid}: foreign clinical parameter in RU profile')
        check(p['source_ref'] != 'RU-SER-2023', f'{rid}: obsolete sertraline copy in active profile')
        check(bool(p['source_ref'] and p['source_locator'] and p['unit']), f'{rid}: unlocated parameter {p["parameter_id"]}')
        check(p['value'] is not None or p['lower'] is not None or p['upper'] is not None, f'{rid}: empty parameter')
        check(p['source_meaning'] in ['предписание', 'диапазон', 'пример', 'выбор врача'], f'{rid}: undefined meaning')
    iids = [i['input_id'] for i in r['inputs']]
    check(len(iids) == len(set(iids)), f'{rid}: duplicate input')
    for i in r['inputs']:
        check(bool(i['question_ru'] and i['why_needed'] and i['action_if_unknown'] and i['source_refs']), f'{rid}: incomplete input')
        if i['data_type'] in ['number', 'integer']:
            check(i['allowed_values'] == [], f'{rid}: numeric input has unrelated enum values')
        check(i['unknown_allowed'] is True, f'{rid}: unknown unsupported')
    v = r['verification']
    check(v['clinical_review'] == 'not_performed', f'{rid}: unsupported clinical review claim')
    check(v['product_clinical_validation'] == 'not_performed', f'{rid}: unsupported validation claim')
    check('calculator_not_implemented' in v['source_transfer_check'], f'{rid}: unsupported execution claim')
    if r['identity']['mode'] == 'switch':
        check(bool(r['identity']['from_drug_inn'] and r['identity']['to_drug_inn']), f'{rid}: missing direction')
        check(r['identity']['from_drug_inn'] != r['identity']['to_drug_inn'], f'{rid}: identical switch ends')
        if r.get('card_type') != 'selected_composite_source_example':
            check(v['ready_for_technical_implementation'] is False, f'{rid}: unresolved switch declared ready')
        else:
            check(r['output']['result_type'] == 'branch_selected' and any(b['expected_output']['result_type']=='selected_source_example' for b in r['output']['branches']) and r['logic']['composite_rule_dependencies'] == ['parox-taper-example', 'ago-depression-start'], f'{rid}: unjustified composite example')
            check(any(i['input_id'] == 'example_selected' for i in r['inputs']), f'{rid}: example lacks physician choice')
            check([st['medication_steps'][0]['total_daily_dose'] for st in r['output']['schedule']] == [30, 20, 0], f'{rid}: changed source taper example')
            check(all(st['medication_steps'][1]['total_daily_dose'] == 25 and st['condition_to_hold'] for st in r['output']['schedule']), f'{rid}: unconditional target escalation or missing hold')
    for c in r['test_cases']:
        check(c['synthetic'] is True and bool(c['expected'] and c['source_refs']), f'{rid}: incomplete synthetic case')
        flattened_cases.append({'rule_id': rid, **c})

finding_cases = []
for r in findings:
    check(r['verification']['ready_for_technical_implementation'] is False, f'{r["rule_id"]}: finding declared numeric-ready')
    check('not_dose_module' in r['profile']['selection_status'], f'{r["rule_id"]}: finding may enter dose routing')
    check(all(s == sources.get(s['source_id']) for s in r['sources']), f'{r["rule_id"]}: stale finding metadata')
    finding_cases.extend({'rule_id': r['rule_id'], **c} for c in r['test_cases'])
check(finding_cases == yaml.safe_load((ROOT / 'finding_cases.yaml').read_text(encoding='utf-8'))['cases'], 'Finding case index mismatch')

reference_cases = []
for r in references:
    rid = r['rule_id']
    check(r['profile']['selection_status'] == 'foreign_reference_only' and r['profile']['auto_select_allowed'] is False, f'{rid}: foreign reference can be auto-selected')
    check(r['verification']['ready_for_technical_implementation'] is False, f'{rid}: foreign comparison declared active-ready')
    local = {s['source_id'] for s in r['sources']}
    check(local <= set(sources), f'{rid}: unregistered reference source')
    check(all(ref in local for ref in source_refs(r)), f'{rid}: missing source in foreign comparison')
    reference_cases.extend({'rule_id': rid, **c} for c in r['test_cases'])
reference_index = yaml.safe_load((ROOT / 'reference_test_cases.yaml').read_text(encoding='utf-8'))
check(reference_index['profile'] == 'foreign_reference_excluded_from_RU', 'Incorrect reference case profile')
check(reference_cases == reference_index['cases'], 'Foreign case index mismatch')

by_rule = {r['rule_id']: r for r in rules}
for rid in ['switch-ser-esc', 'switch-esc-ser']:
    r = by_rule[rid]
    check('next_day' not in r['logic']['parameter_refs'], f'{rid}: foreign direct-switch parameter retained')
    check(r['output']['schedule'] == [] and r['output']['total_daily_dose'] is None, f'{rid}: incomplete RU switch returned a dose calendar')
    check(all(s['jurisdiction'] in ['RU', 'RU/EAEU'] for s in r['sources']), f'{rid}: foreign source in active switch')
    check(any(c['expected'].get('automatic_direct_switch') is False for c in r['test_cases']), f'{rid}: missing priority regression expectation')

estimator = yaml.safe_load((ROOT / 'renal_estimator.yaml').read_text(encoding='utf-8'))
check(estimator['country'] == 'RU' and estimator['source_ref'] == 'RU-PREG-RICHTER', 'Renal estimator must use separate RU original')
check(estimator['verification']['ready_for_clinical_automatic_use'] is False, 'Unreviewed renal estimator declared clinically ready')
check(estimator['verification']['clinical_review'] == 'not_performed', 'Unsupported renal review claim')
check(set(i['input_id'] for i in estimator['inputs']) == {'age_years', 'mass_kg', 'serum_creatinine_umol_L', 'source_sex_category'}, 'Renal input index mismatch')
check(all(p['source_ref'] == estimator['source_ref'] and p['source_locator'] and p['unit'] for p in estimator['parameters']), 'Missing RU provenance for renal coefficients')
check(all(i['question_ru'] and i['why_needed'] and i['action_if_unknown'] and i['unknown_allowed'] is True for i in estimator['inputs']), 'Incomplete renal input description')
check(estimator['output_unit'] == 'mL/min', 'Incorrect renal estimator output unit')
check(all(c['synthetic'] is True and c['source_refs'] == [estimator['source_ref']] for c in estimator['test_cases']), 'Incomplete auxiliary expectation')
check('1.23' in estimator['formula'] and 'serum_creatinine_umol_L' in estimator['formula'], 'Mixed renal formula version/units')
for c in estimator['test_cases']:
    g = c['given']
    if 'serum_creatinine_umol_L' in g:
        estimate = 1.23 * (140 - g['age_years']) * g['mass_kg'] / g['serum_creatinine_umol_L']
        if g['source_sex_category'] == 'женщина по категории формулы':
            estimate *= 0.85
        check(abs(estimate - c['expected']['estimated_CLcr_mL_min']) < 1e-9, f'{c["case_id"]}: incorrect arithmetic expectation')

counts = json.loads((ROOT / 'question_counts.json').read_text(encoding='utf-8'))
check({c['rule_id'] for c in counts} == set(ids), 'Question count profile mismatch')
check(all(c['clinical_input_entries'] == len(by_rule[c['rule_id']]['inputs']) and c['all_catalog_fields_count'] == c['clinical_input_entries'] + c['initial_selections'] for c in counts), 'Incorrect input catalogue count')
with (ROOT / 'input_catalog.csv').open(encoding='utf-8-sig', newline='') as f:
    input_rows = list(csv.DictReader(f))
expected_inputs = {(r['rule_id'], i['input_id']) for r in rules for i in r['inputs']}
expected_inputs |= {(estimator['rule_id'], i['input_id']) for i in estimator['inputs']}
expected_inputs |= {(r['rule_id'], i['input_id']) for r in findings for i in r['inputs']}
check({(i['rule_id'], i['input_id']) for i in input_rows} == expected_inputs, 'Input catalogue profile mismatch')
check(len(input_rows) == len(expected_inputs), 'Duplicate input catalogue row')

with (ROOT / 'coverage.csv').open(encoding='utf-8-sig', newline='') as f:
    coverage = list(csv.DictReader(f))
check(len(coverage) == len({r['inn'] for r in coverage}), 'Duplicate coverage INN')
for row in coverage:
    check(all(row[k] for k in ['inn', 'contexts', 'source_refs', 'locators', 'status', 'populations', 'missing', 'start', 'adjust', 'taper', 'switch']), f'{row["inn"]}: incomplete coverage')
    check(set(row['source_refs'].split(' | ')) <= set(sources), f'{row["inn"]}: unknown coverage source')
    covered_ids = set(row['rule_ids'].split(' | ')) if row['rule_ids'] else set()
    expected_ids = {r['rule_id'] for r in rules if row['inn'] in [r['identity']['drug_inn'], r['identity']['from_drug_inn'], r['identity']['to_drug_inn']]}
    check(covered_ids == expected_ids, f'{row["inn"]}: stale coverage rule index')
with (ROOT / 'depression_dose_table.csv').open(encoding='utf-8-sig', newline='') as f:
    depression_rows = list(csv.DictReader(f))
check(len(depression_rows) == 18 and len({r['inn'] for r in depression_rows}) == 18, 'Depression table row count mismatch')
check(all(r['source_ref'] == 'RU-DEP' and r['source_locator'] and r['routing_status'] == 'not_autonomous_dose_module' for r in depression_rows), 'Depression table wrongly routable or unlocated')

flows = yaml.safe_load((ROOT / 'question_flows.yaml').read_text(encoding='utf-8'))
check(flows['clinical_clearance_claimed'] is False and flows['calculator_implemented'] is False, 'Flow overstates clinical/product validation')
check(flows['question_count_policy']['unasked_is_normal'] is False and flows['question_count_policy']['universal_risk_confirmation_checkbox_allowed'] is False, 'Hidden or assumed clinical clearance')
for f in flows['flows']:
    check(f['rule_id'] in by_rule, f'{f["flow_id"]}: missing rule')
    check(5 <= f['count'] <= 10 and f['count'] == len(f['initial_questions']) + len(f['clinical_questions']), f'{f["flow_id"]}: hidden/incorrect ordinary question count')
    selected = f['clinical_questions'] + f['conditional_questions']
    check(len(selected) == len(set(selected)), f'{f["flow_id"]}: repeated input')
    check(set(selected) <= {i['input_id'] for i in by_rule[f['rule_id']]['inputs']}, f'{f["flow_id"]}: unknown flow field')
    check(f['ordinary_expected']['all_patient_safety_checks_completed'] is False, f'{f["flow_id"]}: unsupported clinical clearance claim')

matrix = yaml.safe_load((ROOT / 'switch_matrix.yaml').read_text(encoding='utf-8'))
directions = {(d['from_inn'], d['to_inn']): d for d in matrix['directions']}
check(len(directions) == len(matrix['directions']), 'Duplicate switch direction')
for (a, b), d in directions.items():
    check((b, a) in directions, f'{a}->{b}: reverse direction not investigated')
    check(d['from_form'] and d['to_form'] and d['source_locator'], f'{a}->{b}: incomplete matrix identity')
    check(d['complete_universal_calendar'] is False, f'{a}->{b}: unsupported universal calendar')
    check(all(sources[s]['jurisdiction'] in ['RU', 'RU/EAEU'] for s in d['source_refs']), f'{a}->{b}: foreign matrix fallback')
check(directions[('флувоксамин', 'агомелатин')]['overlap_status'] == 'contraindicated', 'Lost CYP1A2 contraindication')
check(directions[('агомелатин', 'флувоксамин')]['interval'] is None, 'Invented reverse washout')

audit = yaml.safe_load((ROOT / 'source_transfer_audit.yaml').read_text(encoding='utf-8'))
check({(a['rule_id'], a['parameter_id']) for a in audit['parameter_anchors']} == {(r['rule_id'], p['parameter_id']) for r in rules for p in r['clinical_parameters']}, 'Incomplete numeric anchor catalogue')
for a in audit['parameter_anchors']:
    p = next((p for p in by_rule[a['rule_id']]['clinical_parameters'] if p['parameter_id'] == a['parameter_id']), None)
    check(p is not None and all(p[k] == a[k] for k in ['value', 'lower', 'upper', 'unit', 'source_ref', 'source_locator']), f'{a["rule_id"]}/{a["parameter_id"]}: differs from manually reviewed source anchor')
for sid, s in sources.items():
    if s.get('local_file'):
        p = ROOT / s['local_file']
        check(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == s['document_fingerprint']['sha256'], f'{sid}: changed local original')

cases = yaml.safe_load((ROOT / 'test_cases.yaml').read_text(encoding='utf-8'))
check(cases['clinical_validation'] == 'not_performed', 'Unsupported global validation claim')
check(cases['case_conventions']['unlisted_inputs'].startswith('not_assessed_by_fragment'), 'Fragment cases assume omitted inputs normal')
check({c['case_id'] for c in flattened_cases} == {c['case_id'] for c in cases['cases']}, 'Case index mismatch')
check(len(cases['cases']) == len({c['case_id'] for c in cases['cases']}), 'Duplicate case id')
by_case = {c['case_id']: c for c in cases['cases']}
check(all(c == by_case[c['case_id']] for c in flattened_cases), 'Changed expected value in global case index')
acceptance = json.loads((ROOT / 'acceptance_audit.json').read_text(encoding='utf-8'))
acceptance_original = ROOT.parent / 'psychopharm_codex_pack/ACCEPTANCE.md'
original_criteria = re.findall(r'^- \[ \] (.+)$', acceptance_original.read_text(encoding='utf-8'), re.M)
check(hashlib.sha256(acceptance_original.read_bytes()).hexdigest() == acceptance['acceptance_sha256'], 'Acceptance criteria changed after audit')
check([r['original_criterion'] for r in acceptance['criteria']] == original_criteria, 'Acceptance audit omitted/reworded original criteria')
check(acceptance['criteria_count'] == len(original_criteria), 'Acceptance count mismatch')
check(acceptance['application_implemented'] is False and acceptance['clinical_validation'] == 'not_performed', 'Acceptance overstates implementation/clinical validation')
for name in REQUIRED:
    if name.endswith('.md') and (ROOT / name).exists():
        for target in re.findall(r'\]\(([^)]+)\)', (ROOT / name).read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'):
                continue
            if target == 'verification_report.json':
                continue  # This report is written at the end of this same invocation.
            doc_directory = (ROOT / name).parent
            check((doc_directory / target.split('#')[0]).exists(), f'{name}: broken local link {target}')
with (ROOT / 'search_log.csv').open(encoding='utf-8-sig', newline='') as f:
    log = list(csv.DictReader(f))
check(all(row['date'] and row['exact_query_or_request'] and row['read_part'] and row['reason'] for row in log), 'Incomplete log row')
report = {
    'status': 'pass' if not errors else 'fail',
    'nature': 'Structural consistency and provenance references only; not verification against a running calculator or clinical validation',
    'rule_cards': len(rules), 'synthetic_expectations': len(cases['cases']),
    'search_log_rows': len(log), 'source_records': len(sources),
    'country': policy['country'], 'foreign_fallback_allowed': policy['foreign_numeric_fallback_allowed'],
    'foreign_reference_cards': len(references), 'foreign_reference_expectations': len(reference_cases),
    'non_dose_findings': len(findings), 'finding_expectations': len(finding_cases),
    'ordinary_flows': len(flows['flows']), 'investigated_switch_directions': len(directions),
    'internal_parameter_anchors': len(audit['parameter_anchors']),
    'mapped_inns': len(coverage), 'depression_table_rows': len(depression_rows),
    'auxiliary_renal_expectations': len(estimator['test_cases']),
    'checks': ['required files', 'template fields', 'local source references', 'parameter/input identifiers',
               'parameter provenance presence', 'unknown handling descriptions', 'direction fields',
               'unresolved switch readiness', 'synthetic case index consistency', 'local document links',
               'honest clinical validation status', 'explicit RU source policy',
               'no foreign clinical parameters in active RU profile', 'foreign reference exclusion',
               'RU direct-switch priority expectations', 'separate Russian renal estimator provenance',
               'question count and input catalogue profile consistency', 'concrete medicine identity',
               'ordinary adaptive flow counts', 'both switch directions', 'source example composition',
               'local original hashes', 'internal numeric anchor consistency', 'renal arithmetic expectations',
               'complete medicine coverage index', 'non-routable depression table',
               'original acceptance criteria preserved', 'fragment fixtures do not assume normality'],
    'errors': errors,
    'not_checked': ['clinical efficacy', 'latest registration revision', 'patient safety validation',
                    'execution against calculator', 'full population applicability of incomplete rules']
}
(ROOT / 'verification_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
sys.exit(0 if not errors else 1)
