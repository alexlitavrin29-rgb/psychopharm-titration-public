"""Evidence-limited manual reacceptance of the unchanged research specification."""
from pathlib import Path
import json,yaml,csv,re,hashlib,shutil
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2';W=R.parent
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def csvsave(p,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
S=json.loads((R/'sources.json').read_text(encoding='utf-8'))
rules={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (R/'rules').glob('*.yaml')}
C=yaml.safe_load((O/'result_contracts.yaml').read_text(encoding='utf-8'))['rules']
cases=json.loads((O/'full_scenarios.json').read_text(encoding='utf-8'))['cases']
paths=json.loads((O/'actual_question_paths.json').read_text(encoding='utf-8'))
# The inventory is driven by actual dependencies, not every source in the bibliography.
used={s['source_id'] for r in rules.values() for s in r['sources']}
used.add(yaml.safe_load((R/'renal_estimator.yaml').read_text(encoding='utf-8'))['source_ref'])
used.update(s for d in yaml.safe_load((R/'switch_matrix.yaml').read_text(encoding='utf-8'))['directions'] for s in d['source_refs'])
inventory=[]
for sid in sorted(used):
    s=S[sid]
    if s['source_type']!='label':continue
    inventory.append(dict(source_id=sid,product=s['title'],registration=s['doi_or_registry_id'],version=s['version_or_update_date'],dates=s.get('dates'),primary_file=s.get('local_file'),primary_sha256=s.get('document_fingerprint',{}).get('sha256'),read_scope=s['exact_locator'],latest_edition_confirmed=s.get('latest_registration_revision_confirmed',False),official_comparison=s.get('latest_registry_document_comparison'),registry_identity=s.get('registry_observation'),copies=s.get('document_copies'),affected_cards=[rid for rid,r in rules.items() if sid in {x['source_id'] for x in r['sources']}],required_action=None if s.get('latest_registration_revision_confirmed') else 'Obtain current official SmPC for this exact RU/form and necessary change list; compare stamp/version and all affected medical sections, not just filename/date/SHA.'))
unconfirmed=[x['source_id'] for x in inventory if not x['latest_edition_confirmed']]
save(O/'version_inventory.json',dict(date='2026-10-08',scope='All active product bases, auxiliary renal estimator and switching dependencies',active_label_bases=len(inventory),current_confirmed_count=len(inventory)-len(unconfirmed),unconfirmed=unconfirmed,excluded='Foreign reference labels and RU-SER-2023/RU-ESC-JAN/PREG-RICHTER-ARCHIVE/CITAL/FLUOX/CLOMI archives are not current numeric bases',products=inventory))
# Re-evaluate parameter provenance; the inherited review is explicitly identified.
with (R/'remediation/parameter_review.csv').open(encoding='utf-8-sig',newline='') as f:old={(x['rule_id'],x['parameter_id']):x for x in csv.DictReader(f)}
rows=[]
for rid,r in sorted(rules.items()):
    for p in r['clinical_parameters']:
        sid=p['source_ref'];s=S[sid];prior=old[(rid,p['parameter_id'])]
        rows.append(dict(rule_id=rid,parameter_id=p['parameter_id'],value=p['value'],lower=p['lower'],upper=p['upper'],unit=p['unit'],source_id=sid,version=s['version_or_update_date'],locator=p['source_locator'],local_file=s.get('local_file'),sha256=s.get('document_fingerprint',{}).get('sha256'),review_origin='Round2 current original §1–4.6 reread; primary_expected_checks separate' if sid=='RU-ESC' else 'Prior primary review preserved; round2 key expected spot checks separate, not an exhaustive new medical review',available_original_review='confirmed current primary' if sid=='RU-ESC' else prior['available_original_review'],latest_edition='confirmed' if s.get('latest_registration_revision_confirmed') else 'guideline current catalog' if s['source_type']=='guideline' else 'unconfirmed; F12',meaning=p.get('duration_semantics') or p.get('meaning') or p['source_meaning']))
csvsave(O/'parameter_review.csv',rows)
# Findings are reassessed, retaining the prior closure rationale where unaffected.
with (R/'remediation/findings_log.csv').open(encoding='utf-8-sig',newline='') as f:findings=list(csv.DictReader(f))
updates={
 'F01':('closed','Полный официальный текущий RU-ESC получен человеком после CAPTCHA; 17 страниц, штамп/РУ/форма проверены. Восемь ESC-карт и три зависимости сверены; числовые ветви допускаются лишь по конкретным условиям.','Selectra_current_registry.pdf; sources.json:RU-ESC; primary_expected_checks.json; result_contracts.yaml'),
 'F02':('closed','Текущая ОХЛП §4.2 с.3 задаёт >30 и <30; ровно30 не отнесено ни к одной категории. Сохранено clinician_choice без дозы; это подтверждённый пробел источника, а не выдуманный включительный знак.','Selectra_current_registry.pdf §4.2 с.3; full_scenarios.json:*clcr*; new_negative_checks.json'),
 'F03':('closed','Доступные сроки остальных продуктов повторно проверены по прежним свидетельствам; ESC §4.2 с.3 1–2 недели согласовано с §4.4 с.6 несколько недель/месяцев. Жёсткого верхнего предела и универсальных процентов нет.','parameter_review.csv; primary_expected_checks.json; result_contracts.yaml'),
 'F12':('partial','КР четыре применяются; текущие ESC и SER сопоставлены с официальными файлами. PHEN РУ ородисперсной формы установлен отдельно. Остальные девять активных продуктовых оснований/зависимостей ещё не сопоставлены с последней официальной редакцией.','version_inventory.json; zoloft_comparison.json; catalog_check.json; sources.json:RU-PHEN.registry_observation'),
 'F13':('closed','Из текущего RU-ESC извлечены Child–Pugh A/B/C. A/B источниковый старт; C наблюдение без числовой формулы. Класс не выводится из одного анализа; A/B органы переключения разделены.','Selectra_current_registry.pdf §4.2 с.3; input_necessity.csv; result_contracts.yaml; full_scenarios.json'),
 'N07':('partial','Коллизия SER разрешена по виду результата и ОХЛП. Рассмотрены старт/снижение SER/PREG и будущие поля PAROX. Для остальных карт явно сохраняется консервативная полнота: глобальная минимальность не доказана. Отдельно доказана нижняя граница12 для AGO, требование5–10 не выполнено.','necessity_policy.yaml; input_necessity.csv; actual_question_paths.json; question_limit_conflict.json')}
for f in findings:
    if f['id'] in updates:
        st,txt,ev=updates[f['id']];f.update(status=st,finding=txt,evidence=ev,closure='Документальный блокер закрыт в указанном объёме' if st=='closed' else 'См. limitations.md: конкретные оставшиеся документы/решение по критерию18')
    else:
        f['status']='rechecked_previous_fix';f['evidence']='Предыдущий primary review: ../remediation/'+f['evidence']+'; текущие contract_verification.json/new_negative_checks.json'
        f['closure']='Ранее исправленная часть проверена на регрессию; это не доказательство актуальности редакции и не клиническая валидация.'
findings += [dict(id='R2-01',status='closed',finding='SER: условность наблюдения не безусловный операнд; выбранное действие и выбор действия разделены; keep не требует increase-полей.',evidence='necessity_policy.yaml; primary_expected_checks.json; new_negative_checks.json',closure='Источник/вид результата, не предпочтение одного флага.'),dict(id='R2-02',status='closed',finding='ESC: strictly >65, CLcr exact30 gap, условные ECG/электролиты, противопоказание QT-препаратов и самостоятельные сроки ИМАО.',evidence='Selectra_current_registry.pdf §4.2–4.5; full_scenarios.json; primary_expected_checks.json',closure='Проверены границы, unknown и отсутствие требуемой ЭКГ.'),dict(id='R2-03',status='closed',finding='Текущая маниакальная фаза отдельно от анамнеза: SER/ESC direct stop, в четырёх переходах отдельные A/B действия.',evidence='RU-SER/RU-ESC §4.4 с.4; RU-AGO §4.4 с.5; repair_switch_mania.py; new_negative_checks.json',closure='Не начинать B автоматически; stop принадлежит принимаемому A. Это не повторная диагностика.')]
csvsave(O/'findings_log.csv',findings)
# Every criterion is authored again against current evidence; literal source text preserved.
accept=W/'psychopharm_codex_pack/ACCEPTANCE.md';texts=re.findall(r'^- \[ \] (.+)$',accept.read_text(encoding='utf-8'),re.M)
evidence=[
 'PROJECT_BRIEF.md; input_contracts.yaml:external_context. Врач вводит диагноз/действие; диагностической анкеты нет.',
 'ru_source_policy.yaml; coverage.csv; catalog_check.json. РФ и тревожные/тревожно-депрессивные контексты сохранены.',
 '38 rules/ + result_contracts.yaml: выбранный продукт/форма и веточный дозовый результат либо обоснованный пробел.',
 'card_review.csv; coverage.csv; switch_matrix.yaml. Четыре режима исследованы; неподдержанные ветви явны.',
 '01_scope_and_sources.md; действующие КР457_3/456_3/455_3 и каталожная проверка. До трёх кандидатов по КР, собственного рейтинга нет.',
 'coverage.csv; applicability и полные under18/elderly/pregnancy/lactation expected. Масштабирования взрослой дозы нет.',
 'PROJECT_BRIEF.md; inputs. Нет обязательной генетики/ML/истории пациентов/стоимости/визитов; известный CYP отдельная применимая ветка.',
 'rules/:identity/applicability; RU-ESC текущие форма/деление/классификация подтверждены; RU-PHEN точное РУ ородисперсной формы установлено. Редакционная актуальность отдельно №9.',
 'version_inventory.json; sources.json; parameter_review.csv. Конкретные прочитанные версии/локаторы есть; последние редакции девяти активных оснований ещё не сопоставлены. F12.',
 'parameter_review.csv 210 параметров; input_necessity.csv; текущий ESC §1–4.6. Числа/условия имеют первичные локаторы; наследованный первичный review явно отделён от новых проверок.',
 'result_contracts.yaml: exact/range/choice/selected_source_example; диапазоны не превращены в произвольные числа, PAROX-композиция явный выбранный пример.',
 'structured_form/renal; result_contracts.yaml и prepared expected: суточная/разовая доза, кратность, единицы, release, недостижимые формы.',
 'full_scenarios.json:overlapping-modifiers; RU-source policy. Нет произведения независимых поправок или среднего несовместимых источников.',
 'switch_matrix.yaml 12 направлений; current ESC + A/B source gates/mania; проверенные ограничения перекрытия и интервалы отдельны. Ненайденные российские парные календари/основание MOC явно сохранены; их отсутствие допускается ТЗ.',
 'result_contracts.yaml; parameter_review.csv; текущий ESC §4.2/4.4; симптомы/изменение темпа сохранены, единого процента/верхнего предела нет.',
 'inputs response/clinical_assessment; КР/label branch conditions. Шкала не преобразована в мг без опубликованного основания.',
 'input_necessity.csv и necessity_policy.yaml разрешают SER и неправильные режимные поля. Для остальных карт консервативные источниковые условия раскрыты, но ещё не обоснована неудалимость каждого вопроса по конкретному результату. №17 частично.',
 '96 фактических branch paths; question_limit_conflict.json. Обычный AGO требует не менее12 независимых выборов/фактов даже без всех наблюдательных cautions. Исходный лимит5–10 не выполнен и не изменён.',
 'question_graphs.yaml; actual_question_paths.json: независимые renal, A/B, MAOI-поля и сложные ветки не удалены ради лимита.',
 'contract_verification.json; full_scenarios.json; new_negative_checks.json: known false отдельно от unknown/not_assessed; непройденный мониторинг явно сохранён.',
 'Все applicable missing fields → insufficient_data без дозы. Вложенные органы/формы/ИМАО; изолированные негативные мутации проверяют отказ.',
 'result_contracts.yaml: будущие этапы условны; no automatic_next_stage/hold/stop. Подготовленные ожидания, не исполнение приложения.',
 'Минимальные интервалы источника отдельно от визитов; MOC ESC минимум суток отдельно от календарного дня FLUVOX; мониторинг AGO не придуманные визиты.',
 'Оригиналы доступных оснований прочитаны; current ESC/SER PDF предоставлены человеком и сохранены с SHA/штампами. Ограниченный доступ/архивы помечены; сниппет не первичная дозовая основа.',
 'Политика РФ; exact RU/forms; reference_rules исключены из routing. Зарубежное руководство не доказывает российское показание или регистрацию.',
 'sources.json:source_type/access_status/evidence_status; правила, КР и исследование/модель имеют разные статусы.',
 'coverage.csv; gaps. Эффективность/упоминание препарата не доказательство любой лестницы или переключения.',
 'verification_results.json: prepared expectations, calculator_tests_executed=false, clinical_validation=not_performed. Техническая проверка не клиническая.',
 'summary.md; limitations.md; технический перенос фиксированных копий отделён от актуальности/внедрения; общая клиническая готовность не заявлена.',
 'findings_log.csv; version_inventory.json; limitations.md. Открытые F12/минимальность/лимит раскрыты; отсутствие найденного аналога не доказательство отсутствия.'
]
partial={9,17,18};criteria=[]
for n,(txt,ev) in enumerate(zip(texts,evidence),1):
    criteria.append(dict(number=n,id=('A'+str(n) if n<=7 else 'B'+str(n-7) if n<=16 else 'C'+str(n-16) if n<=23 else 'D'+str(n-23)),original_criterion=txt,status='partial' if n in partial else 'satisfied_for_research_stage',evidence=ev))
assert len(criteria)==30
report=dict(date='2026-10-08',stage='research_only',acceptance_file='psychopharm_codex_pack/ACCEPTANCE.md',acceptance_sha256=hashlib.sha256(accept.read_bytes()).hexdigest(),criteria_count=30,satisfied_count=27,partial_count=3,not_satisfied_count=0,application_implemented=False,clinical_validation='not_performed',evaluation_type='New manual evidence-limited recheck; literal criteria unchanged; independent final review follows',criteria=criteria)
save(O/'acceptance_recheck.json',report);save(R/'acceptance_audit.json',report)
md='# Повторная приёмка второго прохода\n\n27 выполнено, 3 частично: №9,17,18. Приложение и клиническая валидация не входят в исследовательскую приёмку. Исходный ACCEPTANCE сохранён.\n\n| № | Дословный критерий | Статус | Свидетельство / предел |\n|---|---|---|---|\n'
md+='\n'.join('| '+str(c['number'])+' | '+c['original_criterion']+' | '+('частично' if c['status']=='partial' else 'выполнено')+' | '+c['evidence'].replace('|','/')+' |' for c in criteria)+'\n'
(O/'acceptance_recheck.md').write_text(md,encoding='utf-8');(R/'07_acceptance.md').write_text(md.replace('input_contracts.yaml','remediation_round2/input_contracts.yaml')+'\nПодробные новые доказательства: [второй проход](remediation_round2/summary.md).\n',encoding='utf-8')
oldscore=json.loads((R/'remediation/scoring.json').read_text(encoding='utf-8'));newvals=[8.0,9.0,8.0,9.0,9.0]
reasons=['ESC current full original and SER full byte comparison; PHEN exact RU/form. Nine active product edition confirmations remain F12, so not10.','All11 affected ESC/dependency cards source-read, exact30 and >65, hepatic classes, taper semantics and A/B mania repaired; key expected independently checked. Medical review is limited, not exhaustive.','Source/result necessity collision repaired; increase vs keep, start vs cessation separated; actual paths count independent facts. Other card minimum necessity and universal5–10 remain open.','27 of30 literal research criteria met by new evidence; current source/limits/form criteria close. General short path remains incompatible with the enumerated lower bound.','38 contracts/typed inputs and all indices agree; 27 targeted plus5 structural mutations reject defects; primary checks supplement internal anchors. No executed calculator or clinical validation.']
dims=[]
for old,v,why in zip(oldscore['dimensions'],newvals,reasons):dims.append(dict(dimension=old['dimension'],previous_score=old['score'],score=v,weight_percent=old['weight_percent'],contribution=v*old['weight_percent']/100,new_evidence_and_change=why))
raw=round(sum(x['contribution'] for x in dims),3)
score=dict(dimensions=dims,previous_uncapped_score=7.75,weighted_score=raw,original_audit_cap=6.0,original_cap_applies=False,cap_reason='Original audit 04_scoring.md ties cap6 to unavailable key RU-ESC plus unclosed substantial input/output contracts. Current original and explicit branch/typed/unknown contracts are now present; residual F12 is scored in source dimension, and minimum-question requirement remains partial. Removing the cap alone would leave7.75; the weighted changes above explain8.55. Cap4 has no established unresolved critical executable dose/unit/interval; no calculator execution is claimed.',final_score=raw,clinical_validation='not_performed',independent_review_status='pending')
save(O/'scoring.json',score)
(O/'scoring.md').write_text('# Оценка исследования\n\nЭкспертная оценка с ограниченной проверкой источников: **'+str(raw)+'/10**. Не оценка клинической безопасности приложения.\n\n| Измерение | Было без cap | Теперь | Вес | Новое основание |\n|---|---:|---:|---:|---|\n'+'\n'.join('| '+x['dimension']+' | '+str(x['previous_score'])+' | '+str(x['score'])+' | '+str(x['weight_percent'])+'% | '+x['new_evidence_and_change']+' |' for x in dims)+'\n\n'+score['cap_reason']+'\n\nНезависимая проверка финального снимка обязательна; её замечания могут изменить статус и балл.\n',encoding='utf-8')
limits='''# Открытые ограничения и точные действия

F12 частично: подтверждены текущие официальные ESC/SER. Получить последние официальные ОХЛП и необходимый список изменений для точных РУ/форм: Вальдоксан ЛП-№(000528), Рексетин (008861), Дулоксента (000186), Феварин (008757), Лирика (001631), Прегабалин-Рихтер (002412), Велаксин XR (002093), Велаксин IR (002276), Феназепам ородисперсный (005387). Суффиксы РГ-RU и точные формы/силы см. version_inventory.json. Лирика: номер проверять по официальной строке sources.json.registry_observation, не по пустому полю PDF. После получения сравнить штамп/редакцию и все затронутые медицинские разделы; дата имени файла и загрузки недостаточна. CAPTCHA — только обычное действие человека. Текущие документы можно скачать в lk.regmed.ru/Register/EAEU_SmPC и сохранить локально, как ESC/SER. Полный исторический архив не требуется.

Критерий17: у остальных карт ещё нужен результат-специфический разбор обязательности каждого консервативно сохранённого вопроса. Ledger связывает все38 карты; он не доказывает глобальную минимальность. SER selected action/keep/increase, start/cessation SER/PREG и будущие поля PAROX разобраны отдельно по первичным основаниям.

Критерий18: после удаления наблюдательных рисков источниковый нижний предел AGO всё равно12 независимых фактов/выборов (question_limit_conflict.json). Одни подтверждённые факты можно повторно использовать в текущем расчёте, но это не уменьшает необходимое число независимых сведений для нового пациента. Возможное минимальное изменение ТЗ для отдельного решения: 5–10 дозовых вопросов после открыто перечисленной источниковой проверки применимости, учитываемой отдельно. Здесь это изменение не применено; исходный критерий остаётся частичным.

Сохраняются допустимые источниковые пробелы: ESC CLcr ровно30 не определён; совместные модификаторы не опубликованы; нет полной российской лестницы многих отмен/парных календарей. Они не заполняются чужой схемой. Лирика неоднозначная единица формулы, литий ошибочная единица таблицы КР и внутренний конфликт циталопрама заблокированы; Рихтер отдельная формула, не исправление Лирики молча. Недостижимый XR37,5 не заменяется IR.

Перенос: допускаются ограниченные технические контракты явно указанных прочитанных версий, их ограничения/причины отказа и prepared expected. ESC/SER текущая редакция подтверждена; F12 у прочих переносится как явная нерешённая зависимость. Нельзя объявлять всю базу окончательно актуальной для РФ, скрывать unassessed context, автоматически исполнять clinician_choice или общий парный календарь. До клинического применения нужны отдельные технические испытания и клинический/регуляторный процесс; они не входят в этот исследовательский балл.
'''
(O/'limitations.md').write_text(limits,encoding='utf-8')
summary='''# Второй проход исследования — 08.10.2026

Получены текущие официальные ОХЛП/ЛВ Селектры и Золофта после участия человека. Селектра:17 страниц, штамп31.10.2025/0002; Золофт:22 страницы, штамп29.05.2026/0008, полная byte identity с прочитанным оригиналом. См. [реестр версий](version_inventory.json); неизвестные даты пересмотра/публикации не придуманы. КР457_3/456_3/455_3/301_3 в новом каталоге применяются. Феназепам связан с точным РУ ородисперсной формы, но последняя редакция его PDF ещё не подтверждена.

Пересмотрены все8 ESC-карт и3 зависимости: строгий >65; CLcr >30/<30 и пробел=30; классы Чайлд–Пью A/B/C; формы/деление; противопоказания QT-препаратов; ECG при стабильной ИБС и коррекция электролитов; собственные сроки ИМАО. Отмена сохраняет индивидуальный темп без потолка1–2 недели. Источникового общего шага повышения, совместных коэффициентов и полного парного календаря не добавлено. Локаторы в [параметрах](parameter_review.csv) и [полях](input_necessity.csv).

SER: обязательность определяется источником и выбранным результатом. Контекст наблюдения может оставаться неоценённым с явным предупреждением, не превращаясь в false/клинический допуск. Выбор действия отделён от его выполнения; keep не требует интервала повышения. Текущая мания отдельно от анамнеза; A/B действия в затронутых переходах имеют свои источники. Стартовые поля убраны из выбранных отмен SER/PREG; поля будущего повышения PAROX не требуются для первого старта. Общая минимальность остальных карт пока не доказана.

Для38 карт согласованы типы, условия вопросов, ветки и [полные synthetic expected](full_scenarios.json);124 исходных фрагмента сохранены отдельно. Это подготовленные ожидания, не исполненные тесты калькулятора. [Графы](question_graphs.yaml) содержат96 веточных путей с независимыми сведениями и полным примером; счётчики каталога не выдаются за длину индивидуального пути. AGO имеет источниковую нижнюю границу12 даже без наблюдательных cautions: исходный лимит5–10 не выполнен.

Предварительная новая приёмка: **27 выполнено,3 частично (№9,17,18); 8,55/10**. Снятие прежнего ограничения6 само по себе оставляло7,75; изменения каждого измерения объяснены в [оценке](scoring.md). Все30 исходных формулировок сохранены в [повторной приёмке](acceptance_recheck.md). Независимое заключение финального снимка может скорректировать эти выводы.

Открыты F12 по девяти активным основаниям/зависимостям, минимальность оставшихся вопросов и конфликт критерия18. [Точные действия и предел переноса](limitations.md). Новые свидетельства находятся только в remediation_round2; прежние audit/remediation и ACCEPTANCE защищены исходным manifest. Приложение не написано, клиническая валидация не выполнялась.
'''
(O/'summary.md').write_text(summary,encoding='utf-8');(R/'00_summary.md').write_text(summary.replace('](version_',' ](remediation_round2/version_').replace('](parameter_',' ](remediation_round2/parameter_').replace('](input_',' ](remediation_round2/input_').replace('](full_',' ](remediation_round2/full_').replace('](question_',' ](remediation_round2/question_').replace('](scoring.',' ](remediation_round2/scoring.').replace('](acceptance_',' ](remediation_round2/acceptance_').replace('](limitations.',' ](remediation_round2/limitations.'),encoding='utf-8')
# Current document entry points supersede the earlier pass; old reports remain untouched.
(R/'10_source_audit.md').write_text('# Актуальность первичных документов\n\nТекущая проверка: [реестр используемых версий](remediation_round2/version_inventory.json), [сравнение Золофта](remediation_round2/zoloft_comparison.json), [текущий каталог КР](remediation_round2/catalog_check.json), [параметры](remediation_round2/parameter_review.csv), [условия вопросов](remediation_round2/input_necessity.csv). ESC/SER текущие официальные оригиналы получены и сопоставлены; девять остальных продуктовых оснований/зависимостей остаются F12. Оригиналы прежних проходов и их исторические оценки сохранены без изменений. SHA/имя файла не самостоятельное доказательство актуальности. Статические проверки и независимая проверка части expected не клиническая валидация.\n',encoding='utf-8')
brief=R/'06_implementation_brief.md';txt=brief.read_text(encoding='utf-8');txt=txt.replace('remediation/full_scenarios.json','remediation_round2/full_scenarios.json');txt=txt[:txt.index('Общая приёмка 22/8')]+ 'Текущие контракты: remediation_round2/input_contracts.yaml и result_contracts.yaml; графы actual_question_paths.json. ESC/SER текущие оригиналы подтверждены. 27/3 и8,55 — предварительно до независимого финального заключения. Ограничения остальных редакций, минимальность и лимит5–10 остаются открытыми; непройденный контекст наблюдения сохраняется явно и не означает клинический допуск.\n';brief.write_text(txt,encoding='utf-8')
rulemd=R/'02_rules.md';txt=rulemd.read_text(encoding='utf-8').replace('source_unavailable: текущий RU-ESC не подтверждён','источниковая ветка current RU-ESC; конкретные ограничения/пробелы в round2');rulemd.write_text(txt,encoding='utf-8')
(R/'03_question_flows.md').write_text('# Индивидуальные пути и счёт сведений\n\n[Графы всех38 карт](remediation_round2/question_graphs.yaml) и [96 путей с полными данными/expected](remediation_round2/actual_question_paths.json) считают начальные выборы и независимые сведения, включая renal metric/value/method, A/B и каждый ИМАО. Старые пять коротких flows — справочные/узкие исходные примеры, не доказательство обычного индивидуального пути.\n\nSER selected action/keep/increase и режимные поля пересмотрены по источнику. Остальным консервативным полям нужна дальнейшая минимизация с основанием; автоматическое предпочтение короткого/строгого флага исключено. [AGO нижняя граница12](remediation_round2/question_limit_conflict.json) показывает конфликт с исходным лимитом5–10 даже после снятия наблюдательных рисков. Критерии17/18 частичны, требование не изменено. Unknown не нормализуется; подтверждённые факты текущего расчёта можно повторно использовать, происхождение явно.\n',encoding='utf-8')
# Search journal records only actions actually performed in this pass.
with (R/'search_log.csv').open(encoding='utf-8-sig',newline='') as f:log=list(csv.DictReader(f))
for sid in ['RU-ESC','RU-SER']:
    log.append(dict(date='2026-10-08',database_or_site='Official registry + human download',exact_query_or_request='Current SmPC/PIL of '+sid+' after human CAPTCHA',found_source=S[sid].get('registry_observation',{}).get('document_url',S[sid]['url']),read_part='Current original + visible first page stamp; byte comparison recorded in round2',inclusion_status='current_primary',reason='Resolve F01/F12 without bypass; latest edition evidence separate from download date'))
log.append(dict(date='2026-10-08',database_or_site='Minzdrav public catalog',exact_query_or_request='Read-only POST query, exact body recorded in round2/catalog_check.json',found_source=json.loads((O/'catalog_check.json').read_text(encoding='utf-8'))['endpoint'],read_part='CodeVersion/ApplyStatusCalculated for457_3/456_3/455_3/301_3',inclusion_status='current_guideline_status',reason='Fresh KR applicability, separate from product label version'))
csvsave(R/'search_log.csv',log)
for name in ['verification_report.json','verification_negative_checks.json']:shutil.copy2(R/name,O/name)
save(O/'verification_results.json',dict(main_structure='verification_report.json',structural_negative_mutations='verification_negative_checks.json',contracts='contract_verification.json',targeted_negative_mutations='new_negative_checks.json',independent_primary_expectations='primary_expected_checks.json',rule_cards=38,prepared_full_scenarios=len(cases),prepared_isolated_fragments=124,question_paths=len(paths),calculator_tests_executed=False,clinical_validation='not_performed',scope='Counts do not prove medical coverage; key primary checks supplement internal consistency. Independent final reviewer separately required.'))
print('Reports prepared:27/3; expert weighted8.55; active label inventory',len(inventory),'unconfirmed',unconfirmed)
