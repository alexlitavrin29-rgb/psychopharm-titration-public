"""Проверить, что аудит отвергает порчу данных; основной пакет не изменяется."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import yaml

ROOT = Path(__file__).resolve().parent


def dump(path, value):
    path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False), encoding='utf-8')


def mutate(root, kind):
    if kind in ['foreign_parameter', 'changed_anchor']:
        p = root / 'rules/ser-panic-start.yaml'
        data = yaml.safe_load(p.read_text(encoding='utf-8'))
        if kind == 'foreign_parameter':
            sources = json.loads((root / 'sources.json').read_text(encoding='utf-8'))
            foreign = next(s for s in sources.values() if s['jurisdiction'] not in ['RU', 'RU/EAEU'])
            data['clinical_parameters'][0]['source_ref'] = foreign['source_id']
            data['sources'].append(foreign)
        else:
            data['clinical_parameters'][0]['value'] = 999
    elif kind == 'unsupported_calendar':
        p = root / 'rules/switch-ser-esc.yaml'
        data = yaml.safe_load(p.read_text(encoding='utf-8'))
        data['output']['schedule'] = [{'day': 1, 'unsupported': True}]
    elif kind == 'hidden_question_count':
        p = root / 'remediation_round3/actual_question_paths.json'
        data = json.loads(p.read_text(encoding='utf-8'))
        data[0]['count'] -= 1
        p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        return p
    else:
        p = root / 'renal_estimator.yaml'
        data = yaml.safe_load(p.read_text(encoding='utf-8'))
        data['formula'] = 'CLcr = (140 - age_years) * mass_kg / (72 * serum_creatinine_mg_dL)'
    dump(p, data)
    return p


expected = {
    'foreign_parameter': 'foreign clinical parameter',
    'unsupported_calendar': 'incomplete RU switch returned a dose calendar',
    'hidden_question_count': 'hidden/incorrect full question count',
    'changed_anchor': 'differs from manually reviewed source anchor',
    'mixed_renal_units': 'Mixed renal formula version/units',
}
results = []
with tempfile.TemporaryDirectory(prefix='psychopharm-audit-') as temporary:
    workspace = Path(temporary)
    copied = workspace / 'research'
    shutil.copytree(ROOT, copied)
    shutil.copytree(ROOT.parent / 'psychopharm_codex_pack', workspace / 'psychopharm_codex_pack')
    for p in ROOT.parent.glob('*.md'):
        shutil.copy2(p, workspace / p.name)

    def run():
        return subprocess.run([sys.executable, '-X', 'utf8', str(copied / 'verify_research.py')], capture_output=True, text=True, encoding='utf-8')

    baseline = run()
    if baseline.returncode != 0:
        raise RuntimeError('Baseline isolated copy failed: ' + baseline.stdout + baseline.stderr)
    for kind, message in expected.items():
        changed = mutate(copied, kind)
        result = run()
        report = json.loads((copied / 'verification_report.json').read_text(encoding='utf-8'))
        detected = result.returncode == 1 and any(message in error for error in report['errors'])
        results.append({'mutation': kind, 'rejected': detected, 'matching_errors': [e for e in report['errors'] if message in e]})
        shutil.copy2(ROOT / changed.relative_to(copied), changed)

report = {'status': 'pass' if all(r['rejected'] for r in results) else 'fail', 'isolated_baseline': 'pass', 'main_data_modified': False, 'nature': 'Audit rejection checks; no calculator or clinical validation', 'cases': results}
(ROOT / 'verification_negative_checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
sys.exit(0 if report['status'] == 'pass' else 1)
