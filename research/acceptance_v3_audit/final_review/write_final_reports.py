from pathlib import Path
import json, re, hashlib, collections
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / 'research/acceptance_v3_audit/final_review'
S = ROOT / 'research/remediation_round3/v3_review1_snapshot'
R = S / 'research/remediation_round3'
SHA = 'b13033a0687a28b4da4299c171ac6b88a96667e2d6888ab8aecf5e9c85af0514'
def read(name): return json.loads((D / name).read_text(encoding='utf-8'))
def write(name, value): (D / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
def md(name, value): (D / name).write_text(value.rstrip() + '\n', encoding='utf-8')
def link(name, label=None): return f'[{label or name}](<{(D / name).as_posix()}>)'
def core(path, label=None): return f'[{label or path}](<{(S / path).as_posix()}>)'

counts = read('counts_independent.json')
ordinary = [x for x in counts if x['ordinary']]
count_summary = dict(selected_paths=len(counts), ordinary_numeric_selected_paths=len(ordinary),
    ordinary_min=min(x['count'] for x in ordinary), ordinary_max=max(x['count'] for x in ordinary),
    ordinary_count_distribution=dict(sorted(collections.Counter(x['count'] for x in ordinary).items())),
    ordinary_le15=sum(x['count'] <= 15 for x in ordinary), ordinary_gt15=sum(x['count'] > 15 for x in ordinary),
    lower_bounds=sum(x['lower_bound'] for x in counts), hard_upper_limit=False,
    exhaustive_patient_combination_claim=False)
write('path_summary.json', dict(snapshot=SHA, **count_summary))

scopes = {k: read(v)['rows'] for k, v in {
    'exclusions': 'exclusion_scope_independent.json', 'explicit_choices': 'choice_scope_candidates.json',
    'reason_choices': 'choice_reason_scope_residue.json', 'forms': 'form_scope_residue.json'}.items()}
assert [len(scopes[k]) for k in scopes] == [305, 135, 218, 35]
assert len({x['case_id'] for rows in scopes.values() for x in rows}) == 693
errors = read('independent_data_results.json')['errors']
assert len(errors) == 24
source_registry = read('source_read_registry.json')
source_by_id = {x['source_id']: x for x in source_registry}
def sources(ids, pages):
    return [dict(source_id=s, file=source_by_id[s]['file'], sha256=source_by_id[s]['sha256'],
                 version=source_by_id[s]['version'], physical_pages=pages[s]) for s in ids]

findings = [
 dict(id='V3-01', severity='material research-contract defect', criteria=[17], status='open_in_frozen216',
 title='Полный numerical questionnaire остаётся обязательным после известного источникового исключения',
 locations=['rules/*/inputs/requirement_predicate', 'question_graphs/*', 'necessity_evidence.json'],
 exact_list='exclusion_scope_independent.json#rows', case_count=305,
 representative='ago-depression-start--exclude-RU-AGO-allergy',
 established='Собственный первичный перечень подтверждает все305 known not_applicable причины. Для ограниченного отказа без чисел, индивидуального допуска или изменения других препаратов дальнейшие independent numerical gates не являются его предпосылками. Frozen граф всё ещё потребляет весь always набор.',
 primary_sources=sources(['RU-AGO','RU-ESC','RU-SER','RU-PAROX','RU-DULOX','RU-PREG','RU-FLUVOX','RU-VENLA-XR'],
 {'RU-AGO':[2,3,4,6],'RU-ESC':[2,3,4,6,7],'RU-SER':[2,3,4,7], 'RU-PAROX':[3,4,5,6], 'RU-DULOX':[2,3,4,7,9,10], 'RU-PREG':[2,3,4,10,11,12], 'RU-FLUVOX':[2,3,4,8], 'RU-VENLA-XR':[3,4,6,7,14,15]}),
 safe_fix='Для каждого именованного уже подтверждённого исключения ограничить scope фактически достаточными cause/source/actor/form/phase/clock facts. Чужие дозовые сведения оставить unassessed; любые реально сообщённые optional facts потреблять и считать. Не выводить missing/unknown в negative или противопоказание.',
 closure='Проверить все305 конечных сертификатов и sparse same-exclusion expected; ALT/AST first-start требует own phase, dementia требует elderly, MAOI требует известный класс/тип/время/clock, renal требует источник/метрику/единицу/значение. Нет новой дозы, start/overlap permission или stop другого actor.'),
 dict(id='V3-02', severity='material research-contract defect', criteria=[17], status='open_in_frozen216',
 title='Известное ограниченное clinician_choice сохраняет ненужные последующие numerical вопросы',
 locations=['rules/*/inputs', 'question_graphs/*', 'full_scenarios.json'],
 exact_lists=['choice_scope_candidates.json#rows','choice_reason_scope_residue.json#rows'],
 case_counts={'explicit_source_condition':135,'known_boolean_reason':173,'known_medicine_class_reason':45},
 representative='dulox-depression-start--condition-seizure_state-контролируемые',
 established='135 explicit condition и218 reason-only случаев имеют собственную известную источниковую причину и ограниченный nonnumerical результат, но читают unrelated always поля. Эти353 записи не являются353 различными медицинскими ошибками. Опубликованный числовой выбор/арифметика не входят в список.',
 primary_sources='Точная норма/owner/locator каждого случая сохранены в own primary_norms и source bindings соответствующих exact lists; та же SHA проверена в source_read_registry.json.',
 safe_fix='Именованный bounded choice требует источник и cause, при текущем событии own ongoing и его происхождение; производная ongoing требует сохранять активную фактически принимаемую current_dose. contraception=False требует reproductive_population=True. Известные meds требуют свой record INN/status/class. Снять только unrelated numerical/planning preconditions; supplied facts не читать бесплатно.',
 closure='Независимая сверка всех135+218 ограниченных сертификатов, own source action и unknown/phase countercases; null executable doses/planning/permission, счёт всех supplied positive/negative/unknown. Не переносить clinician_choice в индивидуальную схему.'),
 dict(id='V3-03', severity='material research-contract defect', criteria=[17], status='open_in_frozen216',
 title='Качественная выбранная отмена пяти антидепрессантов сохраняет universal current-event questionnaire',
 locations=['dulox-taper-limit','esc-taper-limit','fluvox-taper-limit','ser-taper-limit','venla-xr-taper-limit'],
 branch='source_limit (result_type clinician_choice)',
 exact_fields={'dulox-taper-limit':['withdrawal_severity'],
 'esc-taper-limit':['seizure_state','current_withdrawal','mania_symptoms','arrhythmia_signs','serotonin_syndrome_signs'],
 'fluvox-taper-limit':['withdrawal_severity','serotonin_syndrome_signs','new_or_increased_seizures','liver_injury_signs','mania_symptoms'],
 'ser-taper-limit':['seizure_state','current_withdrawal','mania_symptoms'],
 'venla-xr-taper-limit':['withdrawal_severity','diastolic_BP','current_allergic_reaction']},
 population_fields=['age on each of these five source-only cards'],
 established='17 current-event fields и5 age fields ещё universal always для source-only справки, которая не задаёт индивидуальный срок/шаг/дозу. Источник требует собственное действие при известном событии, но не универсальное отрицание каждого события для цитирования условной взрослой нормы постепенности.',
 primary_sources=sources(['RU-DULOX','RU-ESC','RU-FLUVOX','RU-SER','RU-VENLA-XR'],
 {'RU-DULOX':[3,4,6],'RU-ESC':[3,4,5,6],'RU-FLUVOX':[2,5,7], 'RU-SER':[3,4,6], 'RU-VENLA-XR':[4,5,9,11,12,13]}),
 safe_fix='Отдельный conditional adult-source reference, population_applicability not_assessed при unknown, known child без взрослого индивидуального интервала; no individual_schedule/duration/clinical_clearance. Сообщённые current symptoms/actions отдельно source-bound и считаются, actor ongoing подтверждён; known positive не получает обычную taper reference вместо срочного действия. Current/past dose не подтверждает текущий приём, если report-only.',
 closure='Omitted/unknown/positive/negative fixtures для17 полей и5 population scopes; сохранён собственный urgent action, отсутствие отрицания пропущенного факта, отсутствие AD действий у PREG/PHEN.'),
 dict(id='V3-04', severity='material research-contract defect', criteria=[17], status='open_in_frozen216',
 title='Не выбранный PAR40 пример всё ещё требует весь B-start профиль',
 locations=['switch-parox-ago-selected-example/branch-not_selected', 'inputs/requirement_predicate'],
 representative='switch-parox-ago-selected-example--branch-not_selected',
 established='Для bounded no-calendar при известном example_selected=False или подтверждённой несовместимой с selected40 дозе остаются27 always поля. No-calendar не утверждает возможность начала AGO. Unknown example choice нельзя читать как false; current dose требуется при выборе примера для проверки40.',
 primary_sources=sources(['RU-PAROX','RU-AGO'], {'RU-PAROX':[3,4], 'RU-AGO':[2,3,4]}),
 safe_fix='Сохранять источник обоих компонентов, явно известный выбор и необходимые current-dose facts; никакого индивидуального B разрешения/overlap/календаря. Снять B-number applicability preconditions только для такого no-calendar terminal; supplied contraindications/current events сохранять и считать.',
 closure='Причинный порядок choice→currentdose→selected40 operands; false/other/unknown variants без календаря/permission/ложной нормы.'),
 dict(id='V3-05', severity='full expected semantic inconsistency', criteria=[20], status='open_in_frozen216',
 title='24 полных ожидаемых результата называют неизвестные optional facts подтверждённо отрицательными',
 locations=['full_scenarios.json/cases/*/expected/confirmed_negatives'],
 exact_cases=[x['case_id'] for x in errors],
 affected_fields=['dementia','liver_injury_signs','transaminases_rising','mania_symptoms','ect','akathisia','glaucoma','qt_risk'],
 established='В selected PAR→AGO по8 полям×omitted/unknown/not_assessed значение не False, но raw confirmed_negatives сохраняет имя. Graph full_projected_expected уже очищает этот список; raw complete oracle остаётся несогласованным.',
 primary_sources='Дефект самого значения unknown/подтверждения, не новая первичная медицинская норма. Связанные условия A/B доступны в RU-PAROX physical4–9 и RU-AGO physical2–6; source ownership не исправляет ложную negative metadata.',
 safe_fix='confirmed_negatives только для действительно supplied False; unknown/omitted/not_assessed именовать unassessed. Не запрещать допустимый ограниченный source-only результат только ради universal negative.',
 closure='Все24 raw и projected expected имеют одинаковую честную unknown provenance; изолированная negative mutation обнаруживает fabricated negative.'),
 dict(id='V3-06', severity='technical/documentary reproducibility', criteria=[], status='open_in_frozen216',
 title='Старые V2 абзацы и две устаревшие отрицательные проверки',
 locations=['research/01_scope_and_sources.md:72','research/02_rules.md:79','research/08_russian_priority_update.md:13','research/08_russian_priority_update.md:15','verify_new_negative_checks.py/missing_ongoing_liver_stop','research/verify_negative_checks.py'],
 established='Read-only повтор: baseline0errors;34/35 мутаций отклонены. Удаление одного liver-stop witness не убирает действие из семейства, поэтому missed mutation не доказывает отсутствие stop. Старый root flow count mutation даёт KeyError(count). В main01/02/08 остались V2/до15/старый audit pointer.',
 primary_sources='Не изменение медицинской нормы. AGO ongoing ALT/AST stop до нормализации уже проверен по §4.4 physical3–4 и own positive/phase expected.',
 safe_fix='Устаревший fixture delete заменить удалением всего соответствующего positive own-action family в isolated copy; root mutation строить на actual_question_paths. Обновить только актуальные main V3 pointers, исторические выводы не переписывать.',
 closure='Повтор isolated negative checks и current main links/counts; scripts не должны утверждать PASS до корректного повторного запуска.'),
 dict(id='V3-07', severity='material research-contract defect', criteria=[17], status='open_in_frozen216',
 title='35 известных отказов формы требуют последующие unrelated clinical gates',
 exact_list='form_scope_residue.json#rows', case_count=35,
 subdivisions={'wrong_source_form_or_release':29,'XR_50percent_37_5_arithmetic':6},
 locations=['rules/*/inputs','question_graphs/*/form_not_feasible'],
 established='29 случаев имеют уже известную несовместимую форму/release;6XR случая требуют подтверждённую источник-совместимую органную арифметику75×50%=37.5 при whole75/150. Для bounded form refusal не нужен полный дальнейший профиль. Остальные145 form results не объявлены дефектными.',
 primary_sources=sources(['RU-AGO','RU-DULOX','RU-ESC','RU-FLUVOX','RU-PAROX','RU-PREG','RU-SER','RU-VENLA-XR'],
 {'RU-AGO':[1,2], 'RU-DULOX':[1,2,3], 'RU-ESC':[1,2,3], 'RU-FLUVOX':[1,2,3], 'RU-PAROX':[1,2,3], 'RU-PREG':[1,2,3,4], 'RU-SER':[1,2,3], 'RU-VENLA-XR':[1,2,3,4,5]}),
 safe_fix='Для29 оставить известную own source identity и несовместимую форму; для6 сохранить known renal/hepatic value/category, correct absoluteGFR metric+unit+assessment,75/50%/37.5/wholeunits. Нет округления, IR substitution или индивидуального допуска. Unknown form/metric/category не доказывает известную невозможность.',
 closure='Все35 sparse same-form results с causal source/form/arithmetic facts и known/unknown controls; no unrelated always questions.'),
]
write('findings.json', dict(snapshot=SHA, findings=findings, status_scope='Frozen216 only; live executor repairs not independently accepted here'))
parts=['# Независимые находки V3 — frozen216',f'Снимок `{SHA}`. Все перечисленные находки открыты в этом снимке. Исправления владельца в последующем живом наборе здесь не принимаются.']
for f in findings:
    parts += [f"## {f['id']} — {f['title']}", f"Статус: {f['status']}. Критерии: {', '.join(map(str,f['criteria'])) or 'техническая согласованность/оценка' }.", f['established'],
              'Локатор: ' + '; '.join(f.get('locations', [])), 'Исправление: ' + f['safe_fix'], 'Условие закрытия: ' + f['closure']]
    for k in ['exact_list','exact_lists']:
        if k in f:
            names = [f[k]] if isinstance(f[k],str) else f[k]
            parts += ['Точный список: ' + ', '.join(link(n.split('#')[0]) for n in names) + '.']
parts += ['Источники, страницы, SHA, точные случаи и поля каждого замечания — в ' + link('findings.json') + '. Это конечные классы недостатков данного снимка;693 непересекающихся case exemplars не являются693 независимыми медицинскими ошибками.']
md('findings.md','\n\n'.join(parts))

canonical=(S/'psychopharm_codex_pack/ACCEPTANCE_V3.md').read_text(encoding='utf-8-sig')
literal=re.findall(r'^- \[ \] (.+)$',canonical,re.M)
assert len(literal)==30
evidence={
1:'38 выбранных карточек используют диагноз и действие психиатра; PAR bipolar screen — источниковая узкая оценка, не повторная диагностика.',
2:'Российские КР GAD/PANIC/PHOB/DEP и регистрационные источники задают основной профиль; зарубежные сравнения не заполняют российский пробел.',
3:'Карточки дают source-bound дозовые действия выбранного препарата или явно ограниченный gap/choice, а не только рейтинг или прогноз концентрации.',
4:'Старт, коррекция, отмена и направления переключения представлены; отсутствующие российские calendars явно сохранены как gaps.',
5:'Топ-3 основан на линиях КР; собственной шкалы индивидуального превосходства нет.',
6:'Возрастные/детские, пожилые, pregnancy/lactation области присутствуют. Known child/unknown population не получают взрослую индивидуальную схему.',
7:'Генетика, ML, patient history database, стоимость, preference profiles и календарь визитов не обязательны. Лабораторные source monitoring сроки не выданы за визиты.',
8:'Main и round3 содержат38 идентичных активных карточек с INN/indication/code/mode/population/own product/form.906 active inputs отделены от26 дополнительных каталоговых зависимостей.',
9:'13503 nested source bindings соответствуют собственному owner/version/SHA; текущие originals и physical locators сверены. PHEN physical form locator, IR version, SER/ESC provenance исправлены. SHA, регистрация и редакция различаются.',
10:'Завершённый USED первичный инвентарь391 norm-key records/6241 old occurrences/906 bindings повторно привязан по той же SHA.211 numeric objects,249 prose groups и все уникальные используемые условия были первично прочитаны; текущие изменённые action/result scopes и1867 used causes/actions проверены. Непереносимые источник-пробелы не заполнены числами.',
11:'Диапазоны/physician options FLUV50or100, PREG25–50/frequencies и optional selectedPAR40 сохранены; пример не превращён в обязательный ladder.',
12:'20647 own prepared assertions проверяют total/per-administration/frequency, units/renal metric и формы. Нет автоматического IR/XR переноса, деления запрещённой формы или исполнения ошибочной printed renal unit.',
13:'Independent hepatic/renal/CYP adjustments не перемножены; DULOX combined modifiers и XR overlap остаются physician_choice/gap.',
14:'Own A/B forms, source clocks, direction и phase проверены.87 no-auto/source-reference guards сохраняют опубликованный AGO25/overlap как справку, не patient-specific permission. Selected PAR40 composition ограничена явно выбранным примером; полный generic calendar не заявлен.',
15:'Дозовой общий процент отмены не придуман. DULOX обычный минимум2weeks без потолка учитывает обе нормы; SSRI/XR variation и symptoms source actions сохранены, PREG/PHEN не заимствуют AD hold/restore/slower.',
16:'Ни monitoring scale, ни efficacy/PK data не создают coefficient без source rule.',
17:'906 полей и сохраняемые mandatory/result scopes рассмотрены по собственным первичным нормам. Для numeric outputs прямые source gates/operands сохранены. Но finite V3-01/02/03/04/07 показывают unrelated always после достаточного bounded cause/reference/refusal; таблица906 и witnesses не доказывают эти crossproducts.',
18:'Самостоятельно восстановлены1907 selected paths, в том числе96 обычных числовых10–34. Начальные выборы и supplied independent optional positive/negative/unknown считаются. Ни одного lower_bound; длинный обычный путь не переименован в сложный. V3 снимает upper limit; необходимость отдельный№17, длина сама не штрафуется.',
19:'Source-triggered CAD/electrolyte/MAOI/organ/switch complexity явна. Own actor, stages/day/dose/frequency и independent clocks считаются отдельно; счёт сложного пути не скрыт.',
20:'Typed unknown/units/phase/medicine classification в projected paths корректны. Однако24 raw expected в PAR→AGO сохраняют неизвестные optional поля в confirmed_negatives. Это конкретное несоответствие полных эталонов; нет нового подтверждённого критического numeric допуска.',
21:'Missing mandatory operands дают named request без unconditional dose. Unknown class запрашивает classification передMAOItype/time, own actor unknown/not_started не создаёт automatic stop/start.',
22:'Future stages имеют условия повторного выбора/оценки; stop/choice/gap не наследуют executable future dose/overlap/calendar. Печатный source reference отдельно от индивидуального действия.',
23:'Minimum interval, approximate laboratory monitoring и physician visit timing не смешаны.',
24:'Own actual primary reading receipts доступны.16 source registry records повторно SHA-checked; старое чтение same bytes зачтено как reuse, не заявлено новым чтением. Human registry originals/CAPTCHA evidence не приписаны самостоятельному сетевому скачиванию.',
25:'Российская применимость определена own current registered product/form и КР; иностранные руководства не заменяют её.',
26:'КР/label/expert composition/form policy/source reference/model/effectiveness study имеют разные статусы. PREG source table и model whole-form policy явно различены.',
27:'Efficacy не доказательство algorithmic dosage. DULOX diabetes adverse-reaction context не коэффициент; medication class fixtures не объявлены исполненным INN classifier.',
28:'Static checks, prepared expectations и graph traces не названы запуском приложения или клинической валидацией.',
29:'Допустимый технический перенос конкретно ограничен проверенными values/forms/conditions/contracts; patient deployment clearance и весь current mandatory dialogue не приняты.',
30:'Известные source conflicts/gaps и finite current necessity/metadata/technical остатки перечислены. Отсутствие найденного российского полного pair/taper protocol не объявлено его доказанным отсутствием.'}
findingmap={17:['V3-01','V3-02','V3-03','V3-04','V3-07'],20:['V3-05']}
rows=[]
for i,text in enumerate(literal,1):
    files = ['main_alignment_checks.json','source_read_registry.json'] if i<=9 else ['used_expected_condition_checks.json','all_expected_check_results.json','source_scope_review.json']
    if 17<=i<=23: files=['necessity_906_review.json','counts_independent.json','independent_data_results.json','findings.json']
    if i>=24: files=['source_read_registry.json','transfer_decision.json','findings.json']
    rows.append(dict(number=i,literal_criterion=text,status='частично' if i in (17,20) else 'выполнено',
        independent_evidence=evidence[i],evidence_files=files,finding_ids=findingmap.get(i,[]),
        limit='Приёмка используемых исследовательских контрактов; не clinical clearance, не исполнение медицинского selector/app, не exhaustive неиспользуемый текст всех ЛВ.' if i!=17 else 'Конечный обязательный остаток перечислен exact lists. Глобальный математический минимум не требуется и не заявлен.'))
statuses=dict(collections.Counter(x['status'] for x in rows));assert statuses=={'выполнено':28,'частично':2}
write('criteria30.json',dict(snapshot=SHA,canonical='psychopharm_codex_pack/ACCEPTANCE_V3.md',rows=rows,statuses=statuses,changed_from_v2=[18],full_acceptance=False))
md('criteria30.md','# Все30 критериев ТЗ V3\n\nСнимок `' + SHA + '`. **28 выполнено,2 частично(№17 и№20)**. №18 оценён в редакции V3 без жёсткого предела.\n\n' + '\n\n'.join(
    f"## {x['number']}. {x['status']}\n\n{x['literal_criterion']}\n\n{x['independent_evidence']}\n\nСвидетельства: " + ', '.join(link(p) for p in x['evidence_files']) + '.' for x in rows))

dimensions=[
 ('Источники, версии, применимость РФ',Decimal('9.5'),25,'Current official originals, sameSHA primary reading/precise owners; human registry provenance distinguished from own download. No source-unavailable active medical basis. Unused source/PIL text not certified.'),
 ('Правила, ограничения, воспроизводимость',Decimal('9.3'),30,'All active used numeric/condition norms checked; own boundary/actions/phase results coherent. Raw24 negative metadata and bounded-result/dialogue contract residue prevent full score.'),
 ('Входы, unknown и пути',Decimal('7.4'),20,'Honest complete independent counts/provenance; unknown no dose/phase/class invention. Exact finite mandatory crossproducts after decisive bound remain material. No penalty for >15.'),
 ('Покрытие ТЗ и честность приёмки',Decimal('8.8'),15,'All38 cards/all30 criteria examined, USED primary condition inventory complete.28 fulfilled/2 partial, explicit transfer and gaps; full accepted research not yet complete.'),
 ('Техническая согласованность и перенос',Decimal('8.2'),10,'Read-only baseline and graph assertions repeat; same-given coherent.24 raw metadata errors, stale V2 pointers,34/35 obsolete family mutation and legacy KeyError reduce reproducibility.')]
raw=sum(score*Decimal(weight)/Decimal(100) for _,score,weight,_ in dimensions)
scoredata=dict(snapshot=SHA,method='Independent expert dimensions, not fraction of fulfilled criteria',
 dimensions=[dict(dimension=n,score=float(v),weight_percent=w,contribution=float(v*Decimal(w)/Decimal(100)),reason=r) for n,v,w,r in dimensions],
 raw_unrounded=str(raw),raw_one_decimal=float(raw.quantize(Decimal('0.1'))),cap=6,
 cap_reason='Существенный незакрытый№17: finite V3-01/02/03/04/07 current mandatory/result scope defects. Не превышение15 и не отсутствие глобального математического минимума.',
 cap4_applied=False,cap4_reason='В фактически переносимых проверенных outputs не установлена критическая erroneous dose/unit/interval или однозначный known contraindicated numerical permission.',
 final_score=6.0,source_cap_method='INDEPENDENT_AUDIT_PROMPT.md; research/audit/04_scoring.md; V3 modifies only criterion18',clinical_validation=False)
write('scoring.json',scoredata)
md('scoring.md','# Независимая экспертная оценка frozen216\n\n' +
 '| Измерение | Балл | Вес | Вклад |\n|---|---:|---:|---:|\n' + '\n'.join(f'| {n} | {v} | {w}% | {v*Decimal(w)/Decimal(100)} |' for n,v,w,r in dimensions) +
 f'\n\nНеокруглённая сумма **{raw}**, с одним знаком **{scoredata["raw_one_decimal"]}/10**. Итог **6,0/10**: существенный незакрытый№17 ограничивает итог6. Предел4 не применён: подтверждённого критического изменения переносимой дозы/единицы/интервала или разрешения известного противопоказания не установлено.\n\nПревышение15 вопросов не штрафуется. Глобальный математический минимум не требовался. Баллы не получены из28/30, не скопированы из прошлой оценки и не означают клиническую валидацию.\n\n' + '\n\n'.join(f'**{n}:** {r}' for n,v,w,r in dimensions))

transfer=dict(snapshot=SHA,decision='partial research acceptance; full current research ready=false',
 allowed=['Source-bound checked numeric parameter values/units/frequencies/intervals and own registered form constraints of38 cards.',
 'Typed source identities, unknown/unit/classification requests, independent MAOI clocks and own actor phase rules.',
 '229 named positive source-stop actions with sufficient cause/source/ongoing evidence and5 AGO physician-selected no-mandatory-taper references.',
 'Published ranges/options/conditional future stages; no invented default inside range.',
 'Source gaps, current/form conflicts and clearly separated published switch component references without individual B permission.'],
 withheld=['Full current mandatory dialogue and claimed necessity for finite V3-01/02/03/04/07 scopes.',
 '24 raw false confirmed_negative complete expectations until metadata repair/recheck.',
 'Blanket full ready or all source-bound choice/refusal certificate acceptance for live repaired snapshot not reviewed here.',
 'Automatic full Russian switch calendar outside explicitly selected supported components, free A/B phase/contra conclusions, unsupported coefficient/rounding/IR substitution.'],
 selected_par40_limit='Only physician explicitly chosen published PAR40 taper component plus source AGO component. Not a universal full pair protocol or patient clinical clearance.',
 source_gap_limit='No discovered protocol means search gap, not proof none exists. No foreign numeric fallback.',
 implementation_next_checks=['Execute a future implementation on source-derived normal/boundary/missing/unknown/form/unit/A→B/B→A cases.',
 'Reproduce own source reasons, phase/provenance, question count and conditional future-step prohibition.',
 'Keep separate implementation verification, required clinical/regulatory process; neither performed by this research review.'],
 clinical_clearance=False,app_execution=False)
write('transfer_decision.json',transfer)
md('transfer_decision.md','# Допустимый технический перенос\n\n**Частичная приёмка исследовательских данных; весь текущий dialogue не принят.**\n\nРазрешён перенос в последующую реализацию подтверждённых source-bound values, ограничений формы, own source actions с достаточными фактами/фазой, typed unknown/units/MAOI clocks и честных source gaps. Опубликованные варианты и компонент AGO25/overlap остаются условными source references; они не разрешают индивидуальный стартB или полный generic pair calendar.\n\nНе переносить как окончательно обоснованный mandatory dialogue конечные scopes V3-01/02/03/04/07 и24 raw fabricated negative fixtures. Новое live исправление требует проверки собственного SHA/дельты. Точная область и ограничения — ' + link('transfer_decision.json') + '.\n\nПредстоящая реализация должна реально выполнить проверки единиц/формы/границ/unknown/actors/условных этапов. Подготовленные expected и graph traces её не исполняют. Клиническая валидация и индивидуальный медицинский допуск не выполнены.')

write('checks.json',dict(snapshot=SHA,medical_condition_reading='Actual prior complete USED primary reading reused after sameSHA verification; changed action/result scope rechecked',
 assertions=dict(numeric_expected=20647,data_count_source_phase_invariants=62056,changed_113_scopes=len(read('changed_condition_checks.json').get('checks',[])),main_alignment=len(read('main_alignment_checks.json').get('checks',[]))),
 independently_examined=dict(full_prepared_cases=5946,same_given_groups=5718,selected_paths=1907,inputs=906,numeric_objects=211,used_cause_action_occurrences=1867,changed_scopes=113,changed_cases=232,named_source_stop_scopes=229,source_choice_no_mandatory_taper=5),
 numerical_errors=0,same_given_clinical_conflicts=0,source_binding_errors=0,graph_count_errors=0,
 raw_expected_negative_errors=24,author_validate_errors=0,author_mutations_rejected=34,author_mutations_total=35,
 author_old_mutation_error="KeyError('count')",finite_own_source_counterchecks=13,
 all_pass_claim=False,app_execution=False,clinical_validation=False,
 scopes=dict(primary_counterchecks='Finite own source/boundary checks, not medical evaluator or entire negative test suite.',
 static_repeat='Actually executed read-only author validate and AST-extracted mutations in memory on archived frozen data, no author report side effects.',
 graph='Own edge/count/actor/projection checks on prepared traces, not execution of clinical selector.')))
write('necessity_residue.json',dict(snapshot=SHA,scope='Finite exact current result-specific defects; no global mathematical minimum requirement',
 exact_lists={'V3-01':'exclusion_scope_independent.json#rows(305)','V3-02a':'choice_scope_candidates.json#rows(135)',
 'V3-02b':'choice_reason_scope_residue.json#rows(218=173+45)','V3-07':'form_scope_residue.json#rows(35=29+6)'},
 exact_nonlist_scopes={'V3-03':findings[2]['exact_fields'],'V3-04':'switch-parox-ago-selected-example/branch-not_selected'},
 explicit_population_scope='Five AD source-only references may use conditional adult-only scope with population not_assessed; no individual child/unknown schedule.',
 unique_listed_cases=693,all_list_sets_disjoint=True,remaining_unbounded_or_unenumerated_tail_claim=False,
 retained_numeric_inputs='Numeric source identity/operands/direct gates remain source-bound. This review does not propose generic demotion of all organ/age/medication questions.',
 fixed_scope_countercases='Unknown/missing causal fact cannot confirm a cause. Current event needs own source actor ongoing; source certificate alone is not a clinical engine.'))
md('necessity_residue.md','# Конечный предметный остаток№17\n\nРассмотрены все906 inputs,355always и их текущие result scopes. Источниковая норма, обязательность full numeric result и достаточность bounded refusal/action/reference различались. Полный mathematical minimum не заявлен и не требуется.\n\n' +
 '\n'.join('- ' + text for text in [
 '305 known not_applicable: ' + link('exclusion_scope_independent.json') + '.',
 '135 explicit known source_condition clinician_choice: ' + link('choice_scope_candidates.json') + '.',
 '218 known reason-only clinician_choice (173Boolean+45medicines): ' + link('choice_reason_scope_residue.json') + '.',
 '35 form refusals (29wrongform/release+6XR source arithmetic): ' + link('form_scope_residue.json') + '.',
 'Пять source_limit branches качественной AD отмены:17 current-event operands и5 population scopes; точные поля вV3-03.',
 'selectedPAR→AGO branch-not_selected: no-calendar вывод при известном выборе/дозе; точные prerequisites вV3-04.']) +
 '\n\n693 списочных case exemplars не пересекаются, но это не693 различных медицинских дефекта. Нельзя закрыть остаток количеством source certificates или совпадением готовых expected: нужно проверить собственные cause/actor/phase/source facts, их unknown controls, отсутствие индивидуального дозового payload и реальное потребление/счёт supplied context.\n\nДля305 exclusions сохраняются source-specific compound facts: ALT/AST>3 и phase first-start/ownBnot_started (12 таких случаев); elderly+dementia; age+indication; renal metric/unit/category/value; hepatic category; current medicine INN/status/class; stoppedMAOItype/time/systemclock; own A/B allergy. Для current choice own ongoing либо consumed actual currentdose; contraceptionFalse нуждается в reproductive_populationTrue. Эти сведения нельзя удалить ради короткого пути.\n\nДля всех остальных current numeric/source conditions источниковое обоснование и applicable predicates рассмотрены по906 строкам в ' + link('necessity_906_review.json') + '. Дополнительный неперечисленный бесконечный хвост минимальности не предъявляется.')

md('required_fixes.md','# Конечные условия повторной приёмки\n\nИсправлять следующую версию, сохраняя frozen216 и этот вывод.\n\n' +
 '\n'.join(f"{i}. **{f['id']}** — {f['safe_fix']} Условие: {f['closure']}" for i,f in enumerate(findings,1)) +
 '\n\nСледующая проверка относится к новому точному SHA: закрытие этого конечного списка, изменённые source/action/result prerequisites, зависимости graph/count/unknown, согласованность всех30 статусов и итоговой оценки. Не требуется новый global minimum или перебор всех клинических комбинаций. SameSHA первичные нормы и211 неизменённых числовых объектов можно переиспользовать с явным provenance.')

md('coverage.md','# Фактический медицинский и технический охват\n\n' +
 'Проверены все38 active cards и все используемые ими source-bound числа/условия. Provenance: завершённое собственное USED reading в acceptance_v2_audit/condition_completion —6241 old occurrences(5987text+254nonstring),391 norm-key records,906 input bindings,211 numeric parameter objects,249 medical prose groups и900 literal condition groups.391 — число norm-key записей, включая aliases, не391 независимое клиническое исследование.0 unmapped/0auto_verified того inventory не превращены в автоматическую медицинскую валидацию.\n\n' +
 'Те же байты всех источников повторно проверены, старое фактическое чтение reused; новое чтение неизменённых страниц не заявлено. В этом проходе дополнительно непосредственно читались DULOX physical2–3, PAR physical3–4, GAD physical24. Связанные прошлые visual renal/form tables сохранены в own reading receipts. Реестр источников, version/file/SHA/physical pages и пределы — ' + link('source_read_registry.json') + '.\n\n' +
 'Current scope:5946 prepared full cases;20647 own numeric/guard assertions;5718 complete same-given/context groups без clinical payload conflicts;1867 used cause/action occurrences без unlinked medical tail;113 changed scopes/232 full source witnesses с own primary norms/unknown/actor result check;229 named source-stop и5AGO выбранных без обязательной отмены;13503 source bindings;906inputs/355always;1907complete paths/96ordinary numerical10–34 безlower_bound. Main alignment991 checks,38current cards/906active inputs (catalog932 includes26other declared dependencies).\n\n' +
 'Использованные нормы охватывают границы возраста/органов/единиц, source-specific doses/intervals/withdrawal conditions, формовую исполнимость, MAOI clocks/classes, A/B phases/owners, contraindications/cautions/current events и действия при известных событиях. Source-only adult references сохраняют unknown population; PREG/PHEN не используютADtaper protocol. Printed unit/source conflicts остаются blocked. Отрицательная class fixture не выдаётся за исполненный автоматическийINNclassifier.\n\n' +
 'Пределы: не читался с целью certification весь неиспользуемый текст каждой ЛВ/PIL и все непереносимые препараты; не перебирались все произвольные пациентские combinations; static scopes/готовые expected не исполняют medical selector. Registry user-download/version evidence оценено по доступным официальным original/stamp records, CAPTCHA заново не проходилась. Scope outsideUSED не скрыт и не требуется для этого исследовательского набора.\n\n' +
 'Остаток внутриUSED не неограниченный “недоказанный минимум”: точные mandatory-result prerequisites вV3-01/02/03/04/07,24fabricated negatives и техническиеV3-06. Их finite списки сохранены, source content по ним проверено; новая реализация сертификатов ещё не принята. Клиническая валидация не выполнена.')

summary='''# Независимая итоговая приёмка ТЗ V3 — frozen216

**Частичная приёмка:28 выполнено,2 частично(№17,№20). Итог6,0/10; исходная взвешенная оценка8,785(8,8/10).** Полная готовность всего текущего исследовательского набора ещё не подтверждена.

Проверен только снимок `{sha}`,216files, сохранённый вv3_review1_snapshot. Live core владелец затем менял; его исправления не подписаны этим отчётом. Все30 literal criteria оценены вV3; только№18 отличается отV2. Более15 само по себе не нарушение, глобальный mathematical minimum не требуется.

Подтверждены используемые medical values/conditions38cards по завершённому собственному sameSHA primary reading и новой сверке изменённых result/action scopes. Scope5946full expected,211numeric objects,906inputs,1867used cause/action occurrences,1907selected complete paths. Нормы391source-key records и6241old occurrences переиспользованы с проверкойSHA, не названы вновь прочитанными. Ordinary numerical96paths:10–34facts,36≤15/60>15,0lowerbounds. Нет подтверждённой критической ошибки переносимой дозы/единицы/интервала или однозначного permission известного противопоказания.

Существенный№17 остаётся открытым по конечным result-specific scopes:305known exclusions,135explicit conditions+218known reason-only choices,35form refusals, пять qualitativeADtaper references и selectedPAR→AGO not_selected. Их known primary cause позволяет ограниченный no-clearance/no-dose result, но current graphs ещё требуют unrelated numerical gates. Это не просьба удалить реальные contraindications ради краткости.№20partial:24raw complete expected называют unknown/omitted optionalfacts confirmednegative; projections уже очищены. Технические остатки:staleV2 paragraphs,34/35rejected obsolete liver fixture mutation и legacy rootcountKeyError.

Допустим последующий технический перенос подтверждённых values/forms/typedunknown/own source actions/sourcegaps и условных options. Не принят целиком mandatory dialogue перечисленных scopes и24raw metadata fixtures. Source reference AGO25/overlap не patient-specificBpermission; full genericRussian paircalendar не доказан и не выдуман. Clinicalclearance/app execution/clinicalvalidation не выполнены и не требовались как доказательство исследовательской корректности.

Материальный№17 применяет содержательныйcap6 по исходной методике;cap4 не применён. Длинаordinary и отсутствиеglobalminimum балл не снижают. После конечных конкретных исправлений нужна независимая delta-приёмка новогоSHA с повторной оценкой всех30; старый вывод сохраняется.
'''.format(sha=SHA)
summary += '\nАртефакты: ' + ', '.join(link(n) for n in ['criteria30.md','findings.md','scoring.md','coverage.md','necessity_residue.md','transfer_decision.md','required_fixes.md','final_verification.json']) + '.\n'
md('summary.md',summary)
md('acceptance_final.md',summary)

# Verify only the exact immutable archival core, never the concurrently repaired live core.
manifest_path=ROOT/'research/remediation_round3/final_manifest_v3_review1.json'
m=json.loads(manifest_path.read_text(encoding='utf-8'))
aggregate=hashlib.sha256(json.dumps(m['files'],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
archive_errors=[]
for row in m['files']:
    p=S/row['path']
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:archive_errors.append(row['path'])
assert m['snapshot_sha256']==SHA and aggregate==SHA and len(m['files'])==216 and not archive_errors
links=[]
for p in D.glob('*.md'):
    for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf-8')):
        if not Path(target).exists() and Path(target)!=D/'final_verification.json':links.append(dict(file=p.name,target=target))
assert not links,links
write('final_verification.json',dict(snapshot=SHA,manifest_aggregate_sha256=aggregate,archived_files_checked=216,
 archive_changes=archive_errors,all_archived216_unchanged=True,initial_live_and_archive_check='initial_preservation.json (216/0errors before live owner revisions)',
 final_live_core_checked_as_same_snapshot=False,reason='Owner explicitly repaired live files after exact216 archive preservation; final review signed archive only.',
 reviewed_core_edited_by_reviewer=False,reviewer_output_directory='research/acceptance_v3_audit/final_review',
 earlier_audits_edited_by_reviewer=False,source_originals_modified=False,
 old_protected_files_scope='Not asserting a new hash audit of every historical file outside216; reviewer wrote only own new final_review directory.',
 report_links_missing=links,criteria_total=30,statuses=statuses,scoring_arithmetic=str(raw),raw_one_decimal=8.8,final_score=6.0,
    full_research_acceptance=False,clinical_validation=False,app_execution=False))
assert (D/'final_verification.json').is_file()
print(json.dumps(dict(snapshot=SHA,criteria=statuses,raw=str(raw),final=6.0,archive_checked=216,archive_errors=0,report_missing_links=0),ensure_ascii=False))
