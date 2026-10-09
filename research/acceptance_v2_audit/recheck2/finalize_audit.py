from pathlib import Path
from decimal import Decimal
from collections import Counter
import datetime, hashlib, json, re

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
R3 = ROOT / 'research/remediation_round3'

def read(path):
    return json.loads(path.read_text(encoding='utf8'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def changes(records):
    return [x['path'] for x in records
            if not (ROOT / x['path']).is_file()
            or digest(ROOT / x['path']) != x['sha256']]

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf8')

initial = read(OUT / 'initial_manifest.json')
core = read(R3 / 'final_manifest.json')
core_sha = hashlib.sha256(json.dumps(core['files'], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert core_sha == core['snapshot_sha256'] == initial['snapshot']
baseline = read(R3 / 'baseline_manifest.json')['files']
protected = [x for x in baseline if x.get('protected')]
originals = [x for x in baseline if x['path'].replace('\\', '/').startswith(
    ('research/source_downloads/', 'research/source_snapshots/'))]
preservation = dict(status='pass', snapshot=core_sha, protected_files=len(protected),
    original_source_files=len(originals), core_files=len(core['files']),
    prior_own_audit_files=len(initial['prior_own_audit_files']),
    protected_changes=changes(protected), original_changes=changes(originals),
    core_changes=changes(core['files']), prior_own_audit_changes=changes(initial['prior_own_audit_files']),
    other_tracked_noncore_changes=changes(initial['files']),
    own_write_scope='research/acceptance_v2_audit/recheck2 only',
    utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
assert all(not preservation[k] for k in ['protected_changes', 'original_changes',
    'core_changes', 'prior_own_audit_changes', 'other_tracked_noncore_changes'])
assert (len(protected), len(originals), len(core['files'])) == (575, 17, 170)
save('preservation_check.json', preservation)

acceptance = read(OUT / 'acceptance_recheck.json')
score = read(OUT / 'scoring.json')
findings = read(OUT / 'findings.json')
closures = read(OUT / 'finding_closure.json')
statuses = Counter(x['status'] for x in acceptance['criteria'])
assert len(acceptance['criteria']) == 30
assert statuses == {'выполнено': 23, 'частично': 7}
assert [x['number'] for x in acceptance['criteria'] if x['status'] == 'частично'] == [9, 10, 14, 15, 17, 18, 30]
assert [x['id'] for x in findings] == ['R2-01', 'R2-02', 'R2-03', 'R2-04', 'R2-05']
assert sum(x['weight'] for x in score['dimensions']) == 100
assert [x['weight'] for x in score['dimensions']] == [25, 30, 20, 15, 10]
raw = sum(Decimal(x['score']) * x['weight'] / 100 for x in score['dimensions'])
assert raw == Decimal(score['uncapped_raw']) == Decimal('8.05')
assert score['final'] == score['cap'] == '6.0'
assert read(OUT / 'requirements_diff.json')['changed_only'] == [18]
for finding_id in ['V2-08', 'V2-10', 'V2-11']:
    assert next(x for x in closures if x['id'] == finding_id)['status'].startswith('closed')
for finding_id in ['R1-01', 'R1-06']:
    assert next(x for x in closures if x['id'] == finding_id)['status'].startswith('partial')

checks = read(OUT / 'independent_checks.json')
extra = read(OUT / 'additional_checks.json')
current = read(OUT / 'recheck2_checks.json')
paths = read(OUT / 'independent_paths.json')
mutations = checks['author_negative_mutations_reexecuted_isolated'] + extra['author_extra_mutations'] + current['author_recheck_mutations']
assert len(mutations) == 55 and all(x['rejected'] for x in mutations)
assert len(checks['own_mutations']) == 12 and all(x['rejected'] for x in checks['own_mutations'])
assert not checks['baseline_errors'] and not extra['author_repair_baseline_errors'] and not current['author_recheck_baseline_errors']
assert not checks['graph_errors'] and not checks['projection_inconsistencies']
assert not paths['graph_errors'] and not paths['projection_conflicts']
assert len(paths['paths']) == 531
assert len(current['independent_primary_result_checks']) == 144
assert all(x['pass_'] for x in current['independent_primary_result_checks'])
assert len(current['undeclared_A_phase_cases']) == 18
assert len(read(OUT / 'A_phase_semantics.json')['positive_event_cases_with_undefined_nonstart_mapping']) == 9
assert len(read(OUT / 'dependency_order_check.json')['affected_paths']) == 21
assert current['A_phase_negative_mutation']['author_validator_rejects'] is False
assert extra['nested_basis_count'] == 11377
assert not extra['arithmetic_consistency_errors'] and not extra['version_SHA_errors']
assert read(OUT / 'numeric_inventory.json')['count'] == 211

parsed = []
for path in sorted(OUT.glob('*.json')):
    if path.name == 'final_manifest.json':
        continue
    read(path)
    parsed.append(path.name)
bad_links = []
for path in OUT.glob('*.md'):
    for link in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf8')):
        if link.startswith(('https:', 'http:', '#')):
            continue
        target = link.strip('<>').split('#', 1)[0]
        if not (path.parent / target).exists():
            bad_links.append(dict(file=path.name, target=target))
assert not bad_links
save('final_verification.json', dict(status='pass', snapshot=core_sha,
    manifest_file_digest_recomputed=True, parsed_json_files=parsed,
    criteria_count=30, status_counts=dict(statuses), finding_ids=[x['id'] for x in findings],
    weights=[x['weight'] for x in score['dimensions']], uncapped_raw=str(raw), final='6.0',
    safe_author_mutations_reexecuted=55, own_rejection_properties=12,
    declared_remaining_A_phase_counterexamples=18, undefined_nonstart_positive_A_phases=9,
    causal_order_affected_paths=21, markdown_link_errors=bad_links,
    clinical_validation=False, exhaustive_medical_review=False,
    utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
own_files = [dict(path=str(p.relative_to(ROOT)).replace('\\', '/'), sha256=digest(p), size=p.stat().st_size)
             for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'final_manifest.json']
save('final_manifest.json', dict(audited_snapshot=core_sha, files=own_files,
    files_sha256=hashlib.sha256(json.dumps(own_files, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
    audit_scope='Independent research recheck2; exhaustive review/clinical validation not claimed',
    utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
print('PASS: 170 core, 575 protected, 17 originals, 92 prior own files unchanged; 23/7; raw8.05 cap6.0')
