from pathlib import Path
from collections import Counter
from decimal import Decimal
import datetime, hashlib, json, re, yaml
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]; O=ROOT/'research/remediation_round3'
def read(p):return json.loads(p.read_text('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def changed(rows):return [x['path'] for x in rows if not (ROOT/x['path']).is_file() or sha(ROOT/x['path'])!=x['sha256']]
init=read(OUT/'initial_manifest.json');core=read(O/'final_manifest.json')
snap=hashlib.sha256(json.dumps(core['files'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()
assert snap==init['snapshot']==core['snapshot_sha256']
assert not changed(core['files'])
accept=read(OUT/'acceptance_recheck.json'); score=read(OUT/'scoring.json'); rows=accept['criteria']
assert len(rows)==30 and Counter(x['status'] for x in rows)=={'выполнено':27,'частично':3}
assert [x['number'] for x in rows if x['status']=='частично']==[10,17,18]
assert [x['weight'] for x in score['dimensions']]==[25,30,20,15,10]
assert sum(Decimal(x['score'])*x['weight']/100 for x in score['dimensions'])==Decimal(score['uncapped_raw'])==Decimal('8.39')
assert score['final']==score['cap']=='6.0'
assert read(OUT/'requirements_diff.json')['changed_only']==[18]
checks=read(OUT/'independent_checks.json');extra=read(OUT/'additional_checks.json');r=read(OUT/'recheck3_checks.json'); pp=read(OUT/'independent_paths.json')
mut=checks['author_negative_mutations_reexecuted_isolated']+extra['author_extra_mutations']+r['author_final_mutations']+r['author_enum_mutations']
assert len(mut)==61 and all(x['rejected'] for x in mut)
assert all(x['rejected'] for x in checks['own_mutations']) and len(checks['own_mutations'])==12
assert all(x['pass_'] for x in r['own_phase_counterexamples']+r['population_primary_expected_checks']+r['par_qualitative_primary_expected_checks'])
assert not r['author_final_baseline_errors'] and not r['current_A_action_phase_errors'] and not r['projected_phase_errors'] and not r['dependency_order_errors'] and not r['parameter_objects_changed']
assert not checks['baseline_errors'] and not extra['author_repair_baseline_errors'] and not extra['version_SHA_errors'] and not extra['arithmetic_consistency_errors']
assert not read(OUT/'B_phase_check.json')['errors']
assert len(pp['paths'])==737 and not pp['graph_errors'] and not pp['projection_conflicts']
assert not read(OUT/'complete_given_consistency.json')['groups_with_different_expected']
assert all(x['pass'] for x in read(OUT/'primary_expected_checks.json')['checks'])
rules={p.stem:yaml.safe_load(p.read_text('utf8')) for p in (O/'rules').glob('*.yaml')}
cases={c['case_id']:c for c in read(O/'full_scenarios.json')['cases']}
classification_errors=[]
for p in pp['paths']:
    c=cases[p['case_id']];rule=rules[p['rule_id']];g=c['given'];ctx=c['external_context'];mode=rule['identity']['mode']
    modifiers=any(isinstance(m,dict) and m.get('interaction_class')=='maoi' for m in g.get('medicines',[])) or mode=='switch' or mode=='start' and ctx['treatment_phase']=='ongoing' or c['branch_id'] in {'renal_caution','renal_reduction','hepatic_reduction','joint_modifiers','organ_caution','repeat_tests','liver_caution'}
    if any(s['source_id']=='RU-ESC' for s in rule['sources']) and mode=='start' and (g.get('coronary_disease') is True or g.get('electrolyte_disturbance') is True):modifiers=True
    ordinary=c['expected']['result_type'] in {'exact','selected_source_example'} and not modifiers
    if ordinary!=p['ordinary']:classification_errors.append(p['case_id'])
assert not classification_errors
numeric_ordinary=[p for p in pp['paths'] if p['ordinary']]
hist=Counter(p['recomputed_count'] for p in numeric_ordinary)
assert len(numeric_ordinary)==40 and sum(p['recomputed_count']<=15 for p in numeric_ordinary)==29
assert not any(p['count_is_lower_bound'] for p in numeric_ordinary)
save('ordinary_path_check.json',dict(selected_ordinary_paths=40,within15=29,above15=11,counts=dict(sorted(hist.items())),classification_errors=classification_errors,lower_bound_ordinary=0,scope='All selected prepared paths, not exhaustive clinical combinations or proof of global minimum'))
archives=[]
for manifest_name,directory,count in [('final_manifest_review1.json','review1_snapshot',122),('final_manifest_recheck1.json','recheck1_snapshot',164),('final_manifest_recheck2.json','recheck2_snapshot',170)]:
    manifest=read(O/manifest_name)
    bad=[x['path'] for x in manifest['files'] if not (O/directory/x['path']).is_file() or sha(O/directory/x['path'])!=x['sha256']]
    assert len(manifest['files'])==count and not bad
    archives.append(dict(manifest=manifest_name,files=count,snapshot=manifest['snapshot_sha256'],changes=bad))
baseline=read(O/'baseline_manifest.json')['files']
protected=[x for x in baseline if x.get('protected')]
originals=[x for x in baseline if x['path'].replace('\\','/').startswith(('research/source_downloads/','research/source_snapshots/'))]
prior_changes=changed(init['prior_own_audit_files']);tracked_changes=changed(init['files'])
assert not prior_changes and not tracked_changes
# The human task authorized the current acceptance_final aggregator outside the frozen core.
# Preserve its pending text byte-for-byte; do not modify historical conclusions.
pointer=OUT.parent/'acceptance_final.md'; pointer_rel=str(pointer.relative_to(ROOT)).replace('\\','/')
pointer_before=pointer.read_bytes();(OUT/'previous_acceptance_final.txt').write_bytes(pointer_before)
pointer_text=f'''# Независимый окончательный итог по ТЗ V2

**Частичная приёмка: 27 выполнено / 3 частично (№10,17,18). Итог6,0/10; до ограничения8,39/10 (8,4).** Активный проверенный снимок `{snap}`,177 файлов.

Локальные фазовые, источниковые и причинные дефекты R2-01/03/04 и конкретные качественные контрпримеры R2-02 исправлены. Полная необходимость всех вопросов и обычные пути20/17/18/16 остаются открытыми; исчерпывающая самостоятельная медицинская проверка каждого уникального условия/expected не завершена. Полное ТЗ V2 и10/10 не подтверждены.

Доступен ограниченный технический перенос проверенных source-bound результатов, типов, блокировок и явно обозначенных решений врача/пробелов. Полный короткий ordinary интерфейс, универсальные парные календари и клинический допуск не подтверждены. Приложение не исполнялось; клиническая валидация не проведена.

[Текущий независимый итог](recheck3/summary.md) · [30 критериев](recheck3/acceptance_recheck.md) · [закрытие/остатки](recheck3/findings.md) · [источниковый охват](recheck3/coverage.md) · [допустимый перенос](recheck3/required_fixes.md)

Исторические выводы неизменны и относятся к прежним снимкам: [первая приёмка](summary.md), [recheck1](recheck1/summary.md), [recheck2](recheck2/summary.md). Проверка сохранности и точные manifests находятся в recheck3/.
'''
pointer.write_text(pointer_text,encoding='utf8')
prior_immutable=[x for x in init['prior_own_audit_files'] if x['path'].replace('\\','/')!=pointer_rel]
preserve=dict(status='pass',snapshot=snap,core_files=177,protected_files=len(protected),original_source_files=len(originals),prior_immutable_own_audit_files=len(prior_immutable),protected_changes=changed(protected),original_changes=changed(originals),core_changes=changed(core['files']),prior_immutable_changes=changed(prior_immutable),other_tracked_noncore_changes=changed(init['files']),archived_snapshots=archives,authorized_current_pointer_update=dict(path=pointer_rel,previous_sha256=hashlib.sha256(pointer_before).hexdigest(),new_sha256=sha(pointer),preserved_copy='research/acceptance_v2_audit/recheck3/previous_acceptance_final.txt',authorization='Current independent acceptance_final.md outside frozen core explicitly requested in recheck3 task'),write_scope='recheck3 outputs plus the expressly requested current acceptance_final.md aggregator',utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
assert all(not preserve[k] for k in ['protected_changes','original_changes','core_changes','prior_immutable_changes','other_tracked_noncore_changes'])
save('preservation_check.json',preserve)
bad_links=[]
for path in list(OUT.glob('*.md'))+[pointer]:
    for link in re.findall(r'\]\(([^)]+)\)',path.read_text('utf8')):
        if link.startswith(('http:','https:','#')):continue
        if not (path.parent/link.strip('<>').split('#',1)[0]).exists():bad_links.append(dict(file=str(path.relative_to(ROOT)),target=link))
assert not bad_links
parsed=[]
for p in sorted(OUT.glob('*.json')):
    if p.name!='final_manifest.json':read(p);parsed.append(p.name)
save('final_verification.json',dict(status='pass',snapshot=snap,criteria=30,met=27,partial=3,raw='8.39',final='6.0',author_negative_properties=61,own_rejection_properties=12,own_phase_counterexamples=7,ordinary_selected_paths=40,ordinary_above15=11,markdown_link_errors=bad_links,parsed_json_files=parsed,medical_calculator_executed=False,exhaustive_medical_review=False,clinical_validation=False))
files=[dict(path=str(p.relative_to(ROOT)).replace('\\','/'),sha256=sha(p),size=p.stat().st_size) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='final_manifest.json']
save('final_manifest.json',dict(audited_snapshot=snap,files=files,files_sha256=hashlib.sha256(json.dumps(files,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),current_aggregator=dict(path=pointer_rel,sha256=sha(pointer)),scope='Partial V2 research acceptance; finite primary and targeted repair review, not exhaustive medical/necessity review',utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
print('PASS:27/3;raw8.39;cap6.0;177current/575protected/17originals/'+str(len(prior_immutable))+'prior audits unchanged;old snapshots122/164/170 exact;current aggregator published')
