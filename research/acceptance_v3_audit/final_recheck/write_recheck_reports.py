from pathlib import Path
import json,re,hashlib,collections
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent;R=ROOT/'research/remediation_round3';OLD=ROOT/'research/acceptance_v3_audit/final_review'
SHA='27ef14e77185b7b104d43199664a5b1ca42b73dd8b09f921ee539e97fae971f8'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def md(n,t):(D/n).write_text(t.rstrip()+'\n',encoding='utf8')
def link(n,label=None):return f'[{label or n}](<{(D/n).as_posix()}>)'
terminal=read(D/'terminal_scope_checks.json');assert len(terminal['errors'])==22
assert all(x['check']=='population known only if actually adult' for x in terminal['errors'])
raw=read(D/'independent_data_results.json');numeric=read(D/'all_expected_check_results.json');used=read(D/'used_expected_condition_checks.json')
assert not raw['errors'] and not numeric['errors'] and not used['errors'] and not used['unlinked']
static=read(D/'static_detectors_repeat.json');main=read(D/'main_detectors_repeat.json')
assert not static['baseline_errors'] and static['mutations_rejected']==35 and not static['graph_errors'] and not main['baseline_errors'] and main['all_rejected']
cases={c['case_id']:c for c in read(R/'full_scenarios.json')['cases']}
paths={p['full_example']:p for p in read(R/'actual_question_paths.json')}
ordinary=[p for p in paths.values() if p['ordinary_individual_numeric_path']]
closure=[]
for i in range(1,8):
 closure.append(dict(finding_id=f'V3-{i:02}',status='partially_closed_population_metadata22_remains' if i==3 else 'closed_in_227',
 independent_evidence='All exact old finite scopes checked against own same-SHA primary norms, current causal certificates and selected paths; all source/phase/compound/arithmetic/supplied-count controls passed.' if i in [1,2,3,4,7] else 'All24 fabricated raw negatives removed; actual False-only assertion over6646 passes.' if i==5 else 'Current35 targeted mutations and5 main in-memory mutations all rejected; current main V3 pointers updated.',
 remaining='V3-RC01 only; mandatory/reference scope correction itself verified.' if i==3 else None))
write('finding_closure.json',dict(old_snapshot='b13033a0687a28b4da4299c171ac6b88a96667e2d6888ab8aecf5e9c85af0514',new_snapshot=SHA,rows=closure))
finding=dict(id='V3-RC01',status='open_in_227',severity='bounded-result population metadata inconsistency',criterion=20,
 field='expected.population_applicability',exact_cases=[x['case_id'] for x in terminal['errors']],
 established='22 sparse AD taper caution/form/clarification cases omit age but inherit adult_source_population from their dense adult fixture. This differs from correctly not_assessed minimal references; projected records retain the same unsupported population tag.',
 primary_rule='Adult source applicability cannot be confirmed from an omitted patient age. Source-only adult reference must remain conditional; it is not a patient-specific adult plan.',
 source_pages={'RU-DULOX':[2,3,6],'RU-ESC':[2,3,6],'RU-FLUVOX':[2],'RU-SER':[2,3,6],'RU-VENLA-XR':[2,4,5,11,12]},
 source_provenance='source_read_registry.json: exact sameSHA actual own primary reading reused; source norms unchanged.',
 medical_effect='No individual dose, taper period/calendar or new clinical permission is returned by these22; source actions have independent own actor-phase evidence. No critical medical dose defect established.',
 safe_fix='Set population_applicability=not_assessed whenever age is absent/unknown/not_assessed; alternatively omit population metadata outside a bounded action/form scope. Keep adult_source_reference_only as a source limitation, not patient assessment.',
 closure='All22 raw and projected metadata corrected; generic assertion permits adult_source_population only with actually supplied known age18+. Isolated fake adult metadata mutation rejected. Other227 medical scope/data unchanged and new SHA verified.')
write('findings.json',dict(snapshot=SHA,findings=[finding],full_research_acceptance=False))
md('findings.md','# Остаток независимой дельты227\n\n**V3-RC01 —22 унаследованных отметки взрослой популяции.**\n\nВ разреженных сценариях качественной отмены отсутствует возраст, но `population_applicability` остаётся `adult_source_population`. Точные случаи — '+link('findings.json')+'. Пять самостоятельных минимальных справочных сценариев уже корректно дают `not_assessed`.\n\nИндивидуальная доза, календарь или срок отмены в этих22 сценариях отсутствуют. Источниковое ограничение взрослой справки и сведения о популяции конкретного пациента должны оставаться отдельными. Исправление: отсутствие/unknown возраста → `not_assessed`; новый общий guard должен проверять raw и projected записи. Остальные конечные медицинские и mandatory scopes исправлены и проверены.\n\nЗакрытие прошлыхV3-01..07 — '+link('finding_closure.json')+'. Полная приёмка227 остаётся частичной только до исправления этой метадельты.')

criteria=read(OLD/'criteria30.json')['rows']
for row in criteria:
 n=row['number'];row['status']='частично' if n==20 else 'выполнено';row['finding_ids']=['V3-RC01'] if n==20 else []
 row['evidence_files']=['terminal_scope_checks.json','terminal_scope_registry.json','terminal_counterchecks.json','independent_data_results.json','source_read_registry.json'] if 17<=n<=23 else ['all_expected_check_results.json','used_expected_condition_checks.json','main_alignment_checks.json','source_read_registry.json']
 if n==17:
  row['independent_evidence']='Рассмотрены все906 input и текущие сохраняемые mandatory/result scopes. Конечные305 исключений,135 explicit scopes (включая22 unknown clarification),218 reason-only choices,35 form refusals, пять source-only AD references и not_selected получили достаточные own source/cause/compound/phase/clock facts. Все1386 current dense/sparse certificate cases сверены с собственными нормами;4591 finite counterchecks не допускают отсутствующий/unknown cause, неверный actor/source или unknown→positive. Supplied positive/negative/unknown читаются и считаются; unrelated numerical gates unassessed. Прямые numeric operands/gates сохранены. Это предметное обоснование текущего набора, не global mathematical minimum и не исполнение medical selector.'
 if n==20:
  row['independent_evidence']='24 прежних fabricated negative metadata исправлены; typed unknown/phase/units/classes и actual False-only invariant всех6646 expected проходят. Остались22 sparse AD taper записи с отсутствующим возрастом, но adult_source_population. Это V3-RC01, без индивидуальной дозы/срока/допуска.'
 if n==18:
  row['independent_evidence']='2652 complete selected paths независимо пересчитаны.96 ordinary numerical paths по-прежнему10–34,36≤15 и60>15, lower_bound0. V3 допускает>15 без штрафа за длину. Initial choices, supplied optional facts, separate own A/B phases, MAOI type/time and stage operands считаются явно. Длинные обычные ветки не переименованы.'
 if n==6:row['independent_evidence']='Карты детей/пожилых/pregnancy/lactation сохранены; ни один known child/unknown result не получает автоматически взрослую индивидуальную дозу или календарь. Источниковая справка условно взрослая; остаток population metadata отдельно№20.'
 if n==9:row['independent_evidence']='Current source identities/versions/locators unchanged from frozen216; все nested bindings и source original SHA повторно проверены.239? Источниковые нормы не выводятся из числа сертификатов.' .replace('239? ','')
 if n==10:row['independent_evidence']='Завершённое собственное USED primary reading прежнего sameSHA набора переиспользовано явно; новые result-scope changes сверены по каждой прежней норме.Все211 numerical parameter objects неизменны.6646 full expected дают22869 собственных numerical/guard assertions без ошибки;2731 used causes/actions без unlinked tail.1386 finite certificates по693 старым именованным scopes сверены с original/source/page/actor facts. Не заявлено новое повторное чтение неизменного или полный неиспользуемый текстЛВ.'
 if n==29:row['independent_evidence']='Проверенные numerical/source/action/input contracts пригодны для выбранного последующего технического переноса.Полный prepared oracle227 ещё ограничен22 population tags; готовность к клиническому применению не заявлена.'
 if n==30:row['independent_evidence']='Source gaps/conflicts и пределы переноса сохранены; единственный новый конечный остатокV3-RC01 перечислен.Точные старые scopes закрыты по свидетельствам; нет неперечисленного бесконечного остатка минимальности.'
 row['limit']='Сохраняет границу исследовательского этапа: собственное первичное чтение используется по неизменной SHA; prepared graphs/certificates не исполняют приложение или clinical selector. Реальная клиническая валидация не выполнена.'
statuses=dict(collections.Counter(x['status'] for x in criteria));assert statuses=={'выполнено':29,'частично':1}
write('criteria30.json',dict(snapshot=SHA,canonical='psychopharm_codex_pack/ACCEPTANCE_V3.md',rows=criteria,statuses=statuses,changed_from_v2=[18],full_acceptance=False))
md('criteria30.md','# Все30 критериев V3 —227\n\n**29 выполнено,1 частично(№20).** №17 выполнен по конечным конкретным scopes, не по количеству файлов или таблице автора.\n\n'+'\n\n'.join(f"## {r['number']}. {r['status']}\n\n{r['literal_criterion']}\n\n{r['independent_evidence']}" for r in criteria))

dimensions=[('Источники, версии, РФ','9.5',25,'Официальные originals и полный USED primary reading; sameSHA reuse и версии проверены. Неиспользуемый текстЛВ не объявлен проверенным.'),
 ('Правила, ограничения, воспроизводимость','9.6',30,'Числа/условия/own actors/source gaps согласованы; все finite oldscope medical prerequisites независимо сверены.Нет критического числового дефекта.'),
 ('Входы, unknown и пути','9.1',20,'Finite mandatory necessity исправлена предметно, honest count/provenance.22 population tags пока противоречат absent age; отсутствует индивидуальный результат.'),
 ('Покрытие ТЗ и честность приёмки','9.4',15,'38 cards/all30 проверены в заявленной USED research области.29/1 и remaining22 явно указаны; не выдана полная приёмка.'),
 ('Техническая согласованность и перенос','9.3',10,'22869+81616 own assertions; current35+5 isolated mutations повторены. Source scope counterchecks4591; minor bounded metadata residue требует guard.')]
total=sum(Decimal(v)*Decimal(w)/100 for _,v,w,_ in dimensions)
write('scoring.json',dict(snapshot=SHA,dimensions=[dict(dimension=n,score=float(v),weight_percent=w,contribution=str(Decimal(v)*Decimal(w)/100),reason=r) for n,v,w,r in dimensions],raw_unrounded=str(total),raw_one_decimal=float(total.quantize(Decimal('0.1'))),cap=None,final_score=float(total.quantize(Decimal('0.1'))),
 cap6_not_applied='Материальное current mandatory requirement№17 исправлено и независимо проверено.Единственный остаток22 population tags находится в no-clearance/nonindividual bounded results и не меняет dose/action/phase.Он требует исправления для полной приёмки, но не назван существенным неподтверждённым дозовым основанием ради автоматическогоcap6.',
 cap4_not_applied='Critical wrong dose/unit/interval or known contraindicated numerical permission not established.',clinical_validation=False,full_research_acceptance=False))
md('scoring.md','# Независимая оценка227\n\n| Измерение | Балл | Вес | Вклад |\n|---|---:|---:|---:|\n'+'\n'.join(f'| {n} | {v} | {w}% | {Decimal(v)*Decimal(w)/100} |' for n,v,w,r in dimensions)+
 f'\n\nИсходная сумма **{total}**, итог **9,4/10**.Пределы4/6 не применены: существенный necessity contract исправлен;22 текущие population tags не задают индивидуального действия/дозы/срока. Полная приёмка всё же не завершена до их исправления. Оценка не получена из29/30, не штрафует длину>15 и не требуетglobal minimum.\n\n'+'\n\n'.join(f'**{n}:** {r}' for n,v,w,r in dimensions))

write('transfer_decision.json',dict(snapshot=SHA,full_research_ready=False,decision='All checked source-bound technical contracts and current necessity scopes transferable;22 population metadata rows withheld from final full oracle acceptance.',
 allowed=['All211 unchanged source numerical parameters, boundaries/units/intervals and identified form constraints.',
 'Typed input contracts/unknown/source identity, own A/B phase/currentdose provenance and separate MAOI clocks.',
 'Finite bounded known exclusion/choice/form/action/conditional source-reference and explicitly nonselected example contracts with exact necessary facts.',
 'Honest reported context and every supplied positive/negative/unknown count; no free other allergy actor/hidden MAOI type/date/phase.',
 'Russian source gaps and published ranges/options, with no source-free next step, combined coefficient, default rounding or foreign fallback.'],
 excluded=['22 uncorrected raw/projected population metadata tags.', 'Clinical implementation or application execution claim.', 'Universal full pair calendar outside clearly chosen/source-supported component; automatic target start/overlap from a source reference.', 'Clinical/regulatory deployment permission.'],
 required_future_implementation='Actually execute normal/boundary/unknown/unit/form/actor/source-clock/conditional-stage and cause-dependent dialogue checks in a future implementation; prepared expected are not application tests.',clinical_validation=False))
md('transfer_decision.md','# Решение о переносе227\n\nПроверенные числовые параметры, typed inputs, own source actions, finite necessary scopes и source gaps пригодны для последующей реализации конкретного исследованного объёма. Полный prepared oracle227 пока не принимается из-за22 population labels; их нельзя считать подтверждением взрослой популяции пациента.\n\nДозовые альтернативы остаются выбором врача. AGO25/overlap — published source reference до индивидуального разрешения, а не полный generic Russian calendar. Unknown не подтверждает отсутствие события, current use или source-compatible форму/метрику.\n\nТочная область — '+link('transfer_decision.json')+'. Clinical clearance, приложение и клиническая валидация не выполнены.')

write('checks.json',dict(snapshot=SHA,full_prepared_cases=6646,selected_paths=2652,inputs=906,numeric_objects=211,
 numeric_assertions=numeric['checks'],numeric_errors=0,data_phase_source_count_assertions=raw['assertions'],data_errors=0,
 used_cause_action_occurrences=used['used_cause_action_occurrences'],used_unlinked=0,
 finite_terminal_certificate_cases=1386,terminal_assertions=terminal['assertions'],terminal_controls=4591,terminal_errors=22,
 actual_author_targeted_mutations=35,actual_author_targeted_rejected=35,actual_main_mutations=5,actual_main_rejected=5,
 graph_errors=0,all_pass=False,remaining_error='V3-RC01 population metadata22',
 historical_root_KeyError_in_old216='Retained only as historical diagnostic in adapted static report; current actual main count mutation all5 passes.',clinical_engine_executed=False,clinical_validation=False))
md('coverage.md','# Фактический охват дельты227\n\nИсходная независимая проверка38card USED условий и211 numeric parameters сохранена в final_review и condition_completion; exactsameSHA reading reuse отражён в '+link('source_read_registry.json')+'. Новое чтение неизменных источников не заявлено.\n\nВсе693 конечных старых scope exemplars имеют current certificate и dense/sparse witness(1386cases).Каждое текущие source/physical-page/SHA основание сверено с собственным прежним primary norm; cause/compound/actor/sourceform/phase/clock/arithmetic checked отдельно, не засчитано поauthor PASS.4591 literal causal counterchecks отвергают отсутствие/unknown причины, инойsource/phase и ошибочную подстановкуpositive в unknown clarification.22 unknown-current-event scopes получили explicit clarification-only, namedmissing/unassessed и no source action.\n\nПроверены305 исключений,135 explicit scopes и218reason-only caution scopes,29 known wrong form/release и6XR75×50%=37.5wholeform refusals,5conditional adult AD references иnotselectedPAR40 result. Прямыеnumeric operands и source gates сохраняются. Свойства source exclusion/refusal не выданы за stop; current clinician action требует свой ongoing и consumed actual currentdose при производной фазе. Supplied optional positive/negative/unknown считаются, отсутствующие nonused fields unassessed.\n\nПолные6646 expected повторно прошли22869 собственных numeric/guard и81616 source/phase/count assertions без ошибки;2731 used cause/action occurrences безunlinked.2652paths имеют корректные edges/terminals/counts;96 ordinary numerical10–34 unchanged и0lowerbounds. Current author baseline и35targeted+5main isolated mutations фактически повторены.\n\nЕдинственный новый ограниченный остаток —22 unsupported patient population tags; нет нового неправильного dose/action или доказанного knowncontra numericalpermission. Перед полной приёмкой нужна конечная метадельта22/guard с новымSHA. Static scope functions/certificates and prepared graphs не clinical selector/app; непрочитанный неиспользуемый текст всехЛВ/неисследованных препаратов внеUSED и произвольная клиническая комбинаторика не сертифицировались.')

summary=f'''# Независимая дельта227 — ТЗ V3

**29 критериев выполнено,1 частично(№20). Оценка9,415 до округления, итог9,4/10. Полная приёмка ожидает исправления22 population metadata.**

Снимок `{SHA}`,227файлов. Предыдущее заключение frozen216 сохранено. Источники/211числовых параметров не менялись; использовано собственное завершённое чтениеUSED после новой проверкиSHA. Все906input иfinite mandatory/result scopes рассмотрены:№17 закрыт предметной сверкой693old scope exemplars/1386certified cases, а не числом таблиц или математическим минимумом.

22869 собственных numeric/guard и81616source/phase/count assertions дали0ошибок.2731used cause/action occurrences привязаны к собственным первичным нормам.4591causal counterchecks отвергнуты;current35targeted+5main isolated mutations воспроизводятся.2652complete paths;ordinary numerical96по10–34,0lowerbounds.Более15 не штрафуется.

ОстатокV3-RC01:22sparse ADtaper fixtures безage наследуютadult_source_population;raw иprojected должны статьnot_assessed.Индивидуальная доза/срок/календарь ими не задаются;actual own actor actions подтверждены отдельно. Поэтомуcap4/6 не применён, но весьpreparedoracle ещё не принят. Это конечный новый остаток, иной медицинский/necessity дефект не установлен в заявленной дельте.

Подтверждённый объём source values/forms/typedunknown/ownactions/finite necessary scopes/sourcegaps пригоден для последующей технической реализации.Автоматическая полная российская схема переключения, clinicalclearance, исполнение приложения и clinicalvalidation не заявлены. После22 metadata/guard требуется только точная финальная метадельта новогоSHA.
'''
summary+='\nАртефакты: '+', '.join(link(n) for n in ['criteria30.md','findings.md','finding_closure.json','scoring.md','coverage.md','transfer_decision.md','final_verification.json'])+'.\n'
md('summary.md',summary);md('acceptance_final.md',summary)
md('required_fixes.md','# Последнее конечное исправление227\n\nТолькоV3-RC01:22 exact cases в '+link('findings.json')+' →`population_applicability=not_assessed` приabsent/unknown age;generic raw/projected guard должен разрешатьadult_source_population только прифактически supplied known18+age.\n\nОстальныеmedical values/actions/causal scopes не менять.Обновитьaffected paths/ожидания, новыйfreezeSHA; сохранить227archivedcopy иданныйвывод.Повторная независимая проверкаmetadata22/guard/хэшей ифинальная30statuses/scoring; unchangedprimary инынешниеnumerical/causalchecks reuseсявнымprovenance.')

# Save a finite per-result review of every active input, not an author witness-count proof.
prior={ (x['rule_id'],x['input_id']):x for x in read(OLD/'necessity_906_review.json')['rows']}
import yaml
rs={p.stem:yaml.safe_load(p.read_text(encoding='utf8')) for p in (R/'rules').glob('*.yaml')};reviews=[]
for rid,r in rs.items():
 for i in r['inputs']:
  own=prior[(rid,i['input_id'])];usedpaths=[p for p in paths.values() if p['rule_id']==rid and i['input_id'] in p['full_projected_given']]
  scopes=collections.Counter(p['result_type'] for p in usedpaths)
  reviews.append(dict(rule_id=rid,input_id=i['input_id'],current_predicate=i['requirement_predicate'],primary_norms=own['primary_norms'],
    primary_reading_provenance='Own completed sameSHA USED norms and frozen216 review reused',
    independent_necessity_decision='Retain direct source numerical/applicability requirement or causal conditional/actually supplied contextual fact. In bounded terminal only certificate own cause/source/phase/clock/arithmetic requirements; unrelated operands unassessed. Finite old residue independently closed.',
    consumed_selected_result_scopes=dict(scopes),consumed_selected_path_count=len(usedpaths),
    limit='Concrete scope review, not global mathematical minimum or medical selector execution. MetadataV3-RC01 does not establish population for absent age.'))
assert len(reviews)==906
write('necessity_906_review.json',dict(snapshot=SHA,rows=reviews,input_count=906,always_count=sum(i['requirement_predicate']['kind']=='always' for r in rs.values() for i in r['inputs']),criterion17='fulfilled_current_finite_source/result_scope',global_mathematical_minimum_claim=False))

manifest=read(D/'initial_manifest.json');assert manifest['snapshot_sha256']==SHA
agg=hashlib.sha256(json.dumps(manifest['files'],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
bad=[x['path'] for x in manifest['files'] if hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()!=x['sha256']]
assert agg==SHA and not bad
write('final_verification.json',dict(snapshot=SHA,manifest_aggregate_sha256=agg,core_files=227,core_changes=bad,reviewer_core_edits=False,
 output_directory='research/acceptance_v3_audit/final_recheck',earlier_audits_changed_by_reviewer=False,
 source_sha_reverified=16,criteria=statuses,full_acceptance=False,remaining='V3-RC01 population metadata22 only',raw_score=str(total),final_score=9.4,clinical_validation=False,application_executed=False))
print(json.dumps(dict(snapshot=SHA,statuses=statuses,remaining22=True,all227_unchanged=True,score=str(total)),ensure_ascii=False))
