from pathlib import Path
from decimal import Decimal
import json,collections,hashlib,re
ROOT=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent;P=ROOT/'research/acceptance_v3_audit/final_recheck'
SHA='b66e9e0dadca7234ed1e66bc8c103047ff2f96e963313d07dd0075494695f0a4'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def md(n,t):(D/n).write_text(t.rstrip()+'\n',encoding='utf8')
def link(n,label=None):return f'[{label or n}](<{(D/n).as_posix()}>)'
def prev(n,label=None):return f'[{label or n}](<{(P/n).as_posix()}>)'
result=read(D/'metadata_delta_checks.json');guard=read(D/'guard_mutation_checks.json')
assert not result['errors'] and guard['author13th_mutation_rejected'] and guard['all_rejected'] and not guard['baseline_errors']
manifest=read(D/'initial_manifest.json');assert manifest['snapshot_sha256']==SHA and len(manifest['files'])==228
original=read(P/'initial_manifest.json');prior={r['path']:r['sha256'] for r in original['files']}
same_files=[r for r in manifest['files'] if prior.get(r['path'])==r['sha256']]
assert len(same_files)==222
registry=read(P/'source_read_registry.json')
for row in registry:
 assert hashlib.sha256(Path(row['file']).read_bytes()).hexdigest()==row['sha256']
 row['bytes_same_at_final_metadata_review']=True;row['new_current_read_pages']=[]
 row['reuse_statement']='Actual independent earlier primary USED reading and completed227 review reused after SHA verification; last228 delta is metadata only, no new primary reading claimed.'
write('source_read_registry.json',registry)
closure=read(P/'finding_closure.json')['rows']
for row in closure:
 row['status']='closed_in_228'
 row['remaining']=None
 if row['finding_id']=='V3-03':row['independent_evidence']+=' Final22 sparse population metadata repaired; own4410 assertions and actual13th guard mutation/12 independent controls passed.'
closure.append(dict(finding_id='V3-RC01',status='closed_in_228',independent_evidence='Exact22 raw/projected population labels now not_assessed with age unassessed; raw/projected known18+ guard and13th mutation plus12 controls actually repeated. Counts/actions/numbers/questions unchanged.',remaining=None))
write('finding_closure.json',dict(previous_snapshot=original['snapshot_sha256'],current_snapshot=SHA,rows=closure))
write('findings.json',dict(snapshot=SHA,open_findings=[],new_findings=[],closed_finding_ids=[x['finding_id'] for x in closure],
 scope='Finite final metadata correction plus reused completed full USED research review of38 cards; no claim of exhaustive unused label/PIL text or every patient combination.'))
md('findings.md','# Закрытие независимых замечаний\n\nВсе конечныеV3-01..07 иV3-RC01 закрыты в снимке228. Новых открытых медицинских, источниковых, обязательных входных или метаданных замечаний в проверенном исследовательском объёме не осталось.\n\nПоследние22 отметки взрослой популяции исправлены только в соответствующих полных и спроецированных результатах. Факты пациента, фазы, действия, числа и вопросы не менялись. Общая проверка требует фактически введённый известный возраст18+ для `adult_source_population`; отсутствие, неизвестность и детский возраст это условие не удовлетворяют.\n\nПодробные условия закрытия — '+link('finding_closure.json')+'. Исторические216/227 отчёты сохранены без исправления их прежних выводов.')

criteria=read(P/'criteria30.json')['rows']
for row in criteria:
 row['status']='выполнено';row['finding_ids']=[]
 row['evidence_provenance']='Completed independent227 review reused;228 changes verified by exact delta. Original USED sources unchanged SHA, not newly reread.'
 if row['number']==20:
  row['independent_evidence']='Прежние24 ложные confirmed_negatives и последние22 population metadata исправлены. Собственная проверка всех текущих raw/projected source-only reference population states проходит. Отметкаadult_source_population допускается только при фактически supplied known age18+;13-я мутация и12 дополнительных raw/projected unknown/nonadult controls отвергнуты. Typed unknown/units/classification и own A/B phase logic прежнего227 набора неизменны и их завершённые проверки переиспользованы.'
  row['evidence_files']=['metadata_delta_checks.json','population_registry.json','guard_mutation_checks.json','finding_closure.json']
 if row['number']==29:
  row['independent_evidence']='Исследовательская готовность конкретных38карточек и их ограниченных контрактов подтверждена в согласованном текущем снимке.Полный подготовленный oracle теперь принят в заявленном объёме. Готовность к реализации отделена от допуска к медицинскому применению; приложения или клинической валидации не было.'
 if row['number']==30:
  row['independent_evidence']='Все источниковые пробелы/конфликты и границы исследования перечислены; конечные медицинские/necessity/unknown/metadata замечания закрыты собственными свидетельствами. Отсутствие найденного полного российского протокола не названо доказанным отсутствием. Не предъявляется бесконечный неперечисленный хвост минимальности.'
 row['evidence_files']=[p if (D/p).is_file() else (P/p).as_posix() for p in row['evidence_files']]
 row['limit']='Полная приёмка исследовательского ТЗ V3 в_USED38 области, включая только используемые нормы/условия/числа/подготовленные результаты. Не clinical clearance/validation, не исполнение приложения или медицинского selector; эти этапы не требовались для текущей приёмки.'
assert len(criteria)==30 and [r['number'] for r in criteria]==list(range(1,31))
statuses=dict(collections.Counter(r['status'] for r in criteria))
literal=re.findall(r'^- \[ \] (.+)$',(ROOT/'psychopharm_codex_pack/ACCEPTANCE_V3.md').read_text(encoding='utf-8-sig'),re.M)
assert [r['literal_criterion'] for r in criteria]==literal
write('criteria30.json',dict(snapshot=SHA,canonical='psychopharm_codex_pack/ACCEPTANCE_V3.md',rows=criteria,statuses=statuses,
 full_research_acceptance=True,changed_from_v2_only=[18],hard_question_limit=False,global_mathematical_minimum_required=False))
md('criteria30.md','# Все30 критериев ТЗ V3\n\n**30 выполнено,0 частично,0 не выполнено,0 не удалось проверить.** Статусы относятся к исследовательскому набору38 карточек; источниковые пробелы сохраняют ограниченный результат.\n\n'+
 '\n\n'.join(f"## {r['number']}. {r['status']}\n\n{r['literal_criterion']}\n\n{r['independent_evidence']}" for r in criteria)+
 '\n\nОснование переиспользования: '+prev('criteria30.json')+' и'+link('metadata_delta_checks.json')+'. Никакое неизменённое первичное чтение не объявлено новым.')

dimensions=[
 ('Источники, версии и применимость РФ',Decimal('9.5'),25,'Полный применяемый первичный объём и точные версии/байты подтверждены. Оценка качества оформления provenance учитывает распределение сведений между реестром, карточкой и нормами; неподтверждённого ключевого источника нет.'),
 ('Правила, ограничения и воспроизводимость',Decimal('9.6'),30,'Числа/условия/границы/владельцы/фазы сверены независимо.Источник-пробелы ограничены явно, диапазоны и решения врача сохранены.Подготовленные сложные контракты требуют внимательного чтения нескольких связанных полей, но медицинского открытого дефекта не осталось.'),
 ('Входы, unknown и пути',Decimal('9.6'),20,'Все906 входов и необходимые result scopes рассмотрены предметно; finite причинные сертификаты/условная справка/source actions сохраняют честный unknown и count. Последние22 population tags и общий guard исправлены.'),
 ('Покрытие ТЗ и честность приёмки',Decimal('9.5'),15,'Все30 literalcriteria выполнены в_USED38 области.Точное покрытие и различие own primary reuse/static/graph/clinical execution раскрыты.Объём evidence велик и повторяет ряд норм, что влияет на удобство независимого воспроизведения, а не на охват ТЗ.'),
 ('Техническая согласованность и перенос',Decimal('9.6'),10,'Current contracts/graphs/counts согласованы; прошлые35+5 отрицательных и4591 finite causal controls зачитываются только при unchanged code/data.Собственные4410 metadata assertions, новый guard и13-я mutation повторены. Машинные свидетельства корректны; множество взаимосвязанных артефактов повышает стоимость сопровождения.')]
total=sum(v*Decimal(w)/100 for _,v,w,_ in dimensions);assert total==Decimal('9.560')
score=dict(snapshot=SHA,method='Five independent expert dimensions, not30/30 percentage and not executor score',
 dimensions=[dict(dimension=n,score=float(v),weight_percent=w,contribution=str(v*Decimal(w)/100),reason=r) for n,v,w,r in dimensions],
 raw_unrounded=str(total),raw_one_decimal=float(total.quantize(Decimal('0.1'))),cap=None,final_score=9.6,
 cap4_not_applied='No established critical transferable medical dose/unit/interval/contraindication permission defect.',
 cap6_not_applied='No material required research criterion, hidden mandatory fact or key unsupported source remains open in the checked_USED scope.',
 not_penalized=['More than15 ordinary questions','No global mathematical minimum','Honest source gaps','No application implementation','No clinical validation','Unused_PIL content outside research_USED'],
 full_research_acceptance=True,clinical_validation=False)
write('scoring.json',score)
md('scoring.md','# Итоговая независимая оценка\n\n| Измерение | Балл | Вес | Вклад |\n|---|---:|---:|---:|\n'+'\n'.join(f'| {n} | {v} | {w}% | {v*Decimal(w)/100} |' for n,v,w,r in dimensions)+
 '\n\nСумма без округления **9,560**, итог **9,6/10**.Пределы4/6 не применяются: открытого критического медицинского дефекта, существенного невыполненного исследовательского требования или неподтверждённого ключевого основания нет.\n\n30/30 не переводится автоматически в10/10.Экспертные баллы также учитывают читаемость, распределение provenance и сопровождение большого набора связанных свидетельств.Источник-пробелы,>15вопросов, отсутствие приложения/клинической валидации и неприменяемый текстЛВ не штрафуются.\n\n'+'\n\n'.join(f'**{n}:** {r}' for n,v,w,r in dimensions))

transfer=read(P/'transfer_decision.json')
transfer.update(snapshot=SHA,full_research_ready=True,decision='Accepted full research specification of38 active cards within explicitly source-bound limited results; sufficient basis for subsequent implementation of this concrete scope.',
 excluded=['Automatic universal Russian pair/taper protocol where source supports only individual components/reference/gap.',
 'Clinical deployment or patient-specific clinical clearance from this research acceptance.',
 'Unsupported combination coefficient, arbitrary range choice, rounding or IR/XR/form substitution.',
 'Automatic inference of negative facts, drug current-use phase, organ classification or interaction class from absent/unknown input.'])
write('transfer_decision.json',transfer)
md('transfer_decision.md','# Решение о конкретном переносе\n\n**Исследовательская спецификация38 активных карточек принята для последующей реализации в установленной области результата.** Числовые параметры/границы/единицы/формы, типизированные входы/unknown, own source actions, фазовые и временные условия, bounded refusal/choice/reference и обоснованные вопросы допускают перенос. Подготовленные полные expected приняты как эталоны исследования.\n\nУсловия источникового пробела и `clinician_choice` остаются такими результатами. Они не требуют выдумывать календарь. Published AGO25/overlap и selectedPAR40 пример не становятся универсальной индивидуальной схемой; последующие этапы сохраняют свои условия.\n\nПосле написания приложения необходимо реально выполнить проверки реализации по нормальным, граничным, unknown, единицам, формам, направлениямA/B, source clocks и условным этапам. Это будущий этап, не блокер данного исследования. Клиническая/регуляторная готовность и индивидуальный допуск не следуют из исследовательской приёмки. Точная область — '+link('transfer_decision.json')+'.')

coverage=dict(current_snapshot=SHA,previous_completed_snapshot=original['snapshot_sha256'],
 final_delta='Six files; exact22 raw and22 projected population/unassessed-age metadata + guarded detector/document journal. No numbers/actions/questions/given/phases altered.',
 own_current_assertions=4410,own_current_errors=0,actual_mutation13_rejected=True,own_raw_projected_controls=12,
 prior_results_reused={'primary_USED':{'old_occurrences':6241,'own_norm_key_records':391,'active_input_bindings':906,'numeric_objects':211,'medical_prose_groups':249,'literal_condition_groups':900},
 'full227':{'cards':38,'full_prepared_cases':6646,'numeric_assertions':22869,'data_source_phase_count_assertions':81616,'used_cause_action_occurrences':2731,
 'terminal_certificate_cases':1386,'terminal_assertions':19126,'terminal_causal_controls':4591,'selected_paths':2652,'ordinary_numeric_paths':96,'ordinary_count_min':10,'ordinary_count_max':34,'lower_bounds':0,'current_targeted_negatives':35,'current_main_negatives':5}},
 reuse_basis='All222 unchanged core files have exact old227 SHA; remaining full/graph/path changes were semantically compared field-by-field. Sixteen original source SHA reconfirmed. Previous population22 errors superseded only by actual current check.',
 outside_scope=['All unconsumed source/PIL sentences and all nonactive drugs','Arbitrary exhaustive patient combinations','Application/medical selector execution','Clinical validation/regulatory process'],
 coverage_not_automatic_from_count=True,full_research_acceptance=True)
write('coverage.json',coverage)
md('coverage.md','# Фактический проверенный объём\n\nПоследний проход —метадельта228:4410 собственных утверждений без ошибки; ровно22 raw и22 projected результата изменены только по population/unassessed-age.13-я мутация фактически выполнена read-only,12 дополнительных raw/projected unknown/nonadult контролей отвергнуты. Числа, действия, patient given, own phases, вопросы/count и graph nodes/edges неизменны.\n\nПолная предметная приёмка227 зачитывается по сохранённым SHA и точной семантической дельте:38карточек,906входов,211числовых параметров,6646полных expected,2731используемая причина/действие,1386источниковых сертификатов,2652выбранных полных пути.Собственное завершённое USED первичное чтение6241occurrences/391norm-key records и прежняя numerical/conditional проверка переиспользованы, а не названы новым чтением.391 включает aliases и не означает391 независимое клиническое исследование.\n\nЧисло файлов/сценариев/PASS не было доказательством нормы или необходимости. Финальные bounded scopes проверены по каждому именованному первичному условию, actor/phase/source/form/compound/interval; источник-пустоты сохранены.Реальные ordinary96numeric paths10–34 открыто считаются; более15 допустимо.\n\nНе сертифицировались неприменяемые фразы всехЛВ/неактивные препараты и все произвольные пациентские сочетания.Это не скрытый непроверенный хвост_USED38 и не дополнительные условия текущего ТЗ.Не исполнялся медицинский калькулятор; клиническая валидация не проведена. Реестр реального чтения и reused evidence — '+link('source_read_registry.json')+'; сводная машинная карта — '+link('coverage.json')+'.')
write('checks.json',dict(snapshot=SHA,current_metadata_assertions=result['assertions'],current_metadata_errors=0,current_exact_raw_changes=22,current_exact_projected_changes=22,
 numeric_actions_questions_phase_given_changed=False,new_result_guard_baseline_errors=guard['baseline_errors'],actual_thirteenth_mutation=guard['author13th_mutation_rejected'],
 independent_raw_projected_controls=len(guard['own_twelve_controls']),all_12_rejected=guard['all_rejected'],
 reused_checks=coverage['prior_results_reused'],scope='Current metadata tests actually repeated; unchanged full227/source results reused by exact identity. No app/clinical engine executed.'))
md('required_fixes.md','# Обязательные исправления исследования\n\nОткрытых обязательных исправлений исследовательского ТЗ V3 в проверенном снимке228 нет.Источник-пробелы и ограниченные результаты остаются опубликованными ограничениями, а не задолженностью выдумать схему.\n\nПосле будущей реализации — фактическая проверка исполнения source-derived expected, типов/границ/форм/unknown/actors/времени и conditional stages. Клиническая и регуляторная приёмка относятся к отдельному этапу. При смене исходного документа/медицинского условия нужна новая источниковая проверка затронутого основания, а не механический перенос нынешнегоPASS.')

summary=f'''# Окончательная независимая приёмка ТЗ V3

**Исследовательский набор принят:30 из30 критериев выполнены. Итоговая независимая оценка9,6/10; взвешенная сумма9,560, ограничения4/6 не применяются.**

Снимок `{SHA}`,228файлов. Это конкретный новый набор; старые216/227 заключения сохраняются. Все22 последние отметки взрослой популяции исправлены. Собственные4410 утверждений дали0ошибок; общийraw/projectedguard и13-я мутация с12 дополнительными unknown/nonadult контролями проверены фактически. Числа, действия, ввод пациента, фазы, вопросы и счёт2652путей не менялись.

Завершённая предметная приёмка38карточек и906входов переиспользована по неизменному источниковомуSHA и точной дельте. Она включает211числовых параметров,6646полных expected, необходимый_USED medical scope и конечное обоснование mandatory/result prerequisites. Это не новое повторное чтение всех источников. Обычные96числовых путей содержат10–34независимых сведений;0lowerbounds, никакого штрафа за>15или требования globalminimum.

Перенос в последующую реализацию подтверждён для исследованных source-bound values/форм/входов/unknown/ownactions/фаз/clocks и bounded choice/refusal/reference contracts. Честные российские источник-пробелы остаются ограниченными результатами, без иностранной подстановки или выдуманного полного календаря. Приложение, индивидуальный клинический допуск и клиническая валидация не выполнены и не объявлены выполненными; они не требовались для этой исследовательской приёмки.

Открытых обязательных исправлений в принятом объёме нет. После написания приложения требуется фактически проверить его исполнение по подготовленным source-derived expected.Экспертный балл9,6 отражает также удобство чтения/сопровождения большого набора свидетельств;30/30 не было автоматически переведено в10/10.
'''
# Editorial readability; identifiers and SHA untouched.
for a,b in [('30 из30','30 из 30'),('сумма9','сумма 9'),('оценка9','оценка 9'),('ограничения4/6','ограничения 4/6'),('`,228','`, 228'),('Все22','Все 22'),('Собственные4410','Собственные 4410'),('дали0','дали 0'),('и13-я','и 13-я'),('с12','с 12'),('счёт2652путей','счёт 2652 путей'),('приёмка38карточек','приёмка 38 карточек'),('и906входов','и 906 входов'),('включает211числовых','включает 211 числовых'),(',6646полных',', 6646 полных'),('Обычные96числовых','Обычные 96 числовых'),('содержат10–34независимых','содержат 10–34 независимых'),(';0lowerbounds','; 0 нижних границ'),('за>15или','за >15 или'),('балл9,6','балл 9,6')]:summary=summary.replace(a,b)
summary+='\nАртефакты: '+', '.join(link(n) for n in ['criteria30.md','scoring.md','findings.md','coverage.md','transfer_decision.md','final_verification.json'])+'.\n'
md('summary.md',summary);md('acceptance_final.md',summary)

agg=hashlib.sha256(json.dumps(manifest['files'],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
bad=[x['path'] for x in manifest['files'] if hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()!=x['sha256']]
assert agg==SHA and not bad
links=[]
for p in D.glob('*.md'):
 for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf8')):
  if not Path(target).is_file() and Path(target)!=D/'final_verification.json':links.append(dict(file=p.name,target=target))
assert not links
write('final_verification.json',dict(snapshot=SHA,aggregate=agg,files=228,core_changes=bad,source_originals_sha_rechecked=16,
 previous_research_content_unchanged_files=222,raw_cases_changed_metadata_only=22,projected_paths_changed_metadata_only=22,missing_report_links=links,
 old_reports_edited_by_reviewer=False,core_edited_by_reviewer=False,output_directory='research/acceptance_v3_audit/final_metadata_review',
 criteria=statuses,raw_score=str(total),final_score=9.6,cap=None,full_research_acceptance=True,application_executed=False,clinical_validation=False))
print(json.dumps(dict(snapshot=SHA,criteria=statuses,raw_score=str(total),final_score=9.6,files228_unchanged=True,report_links_ok=True),ensure_ascii=False))
