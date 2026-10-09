"""Update active pointers; retain the previous main documents separately."""
from pathlib import Path
import csv, json, shutil

O = Path(__file__).resolve().parent
R = O.parent
old = O / 'previous_main_documents'
old.mkdir(exist_ok=True)
names = ['00_summary.md', '01_scope_and_sources.md', '02_rules.md',
         '03_question_flows.md', '05_gaps_and_conflicts.md',
         '06_implementation_brief.md', '07_acceptance.md',
         '08_russian_priority_update.md', '09_download_links.md', '10_source_audit.md']
for name in names:
    if not (old / name).exists():
        shutil.copyfile(R / name, old / name)

(R / '00_summary.md').write_text('''# Третий проход исследования — 08.10.2026

Активные источники и 38 карточек основного пакета согласованы с remediation_round3/. Получены все девять ранее недоступных текущих официальных ОХЛП и девять ЛВ; Селектра и Золофт остаются подтверждёнными основаниями второго прохода. Точные РУ, формы, штампы и SHA перечислены в [реестре документов](remediation_round3/current_registry_documents.json). Получение документа и полнота медицинского переноса проверяются отдельно; ЛВ не объявлены полностью прочитанными.

Действует [ACCEPTANCE_V2](../psychopharm_codex_pack/ACCEPTANCE_V2.md): 5–10 вопросов — цель, до 15 включительно допустимо для обычного пути. Изменён только №18. Предыдущие оценки и исходные критерии сохранены.

[Контракты](remediation_round3/result_contracts.yaml), [полные подготовленные ожидания](remediation_round3/full_scenarios.json), [графы](remediation_round3/question_graphs.yaml) и [фактические пути](remediation_round3/actual_question_paths.json) относятся к третьему проходу. Начальные выборы, каждый независимый факт, лекарство/статус и этап плана считаются явно. Наблюдение без влияния на выбранный результат отделено от обязательных исходных условий; неизвестность не заменена нормой.

Источник за источником пересмотрены формы, почечные метрики, условия прекращения и обязательные предлечебные сведения. Дулоксента: §4.4 требует снижения не менее 2 недель; отдельное «1–2 недели» §4.2 не становится верхним пределом. ОХЛП ородисперсного Феназепама запрещает деление таблетки. Для Лирики сохранены ошибочная единица её формулы и отдельный корректный оценщик Рихтера; автоматическая подмена не разрешена.

Независимая приёмка проверяет [зафиксированный снимок](remediation_round3/final_manifest.json), все 30 критериев и первоисточники; результаты сохраняются в acceptance_v2_audit/. Исполнительская оценка остаётся предварительной: №17 и №18 не закрыты. Обычные AGO, DULOX при ГТР и PREG пока превышают 15. Уже выявленные независимым проверяющим пропуски исправляются с повторной проверкой нового снимка.

Прежние 124 ожидания сохранены как фрагменты. Полные synthetic expected и обходы графа — исследовательские проверки, медицинский калькулятор ими не исполняется. Приложение и клиническая валидация не выполнялись. Точный текущий объём проверки и ограничения: [README](remediation_round3/README.md), [limitations](remediation_round3/limitations.md). Исторический итог второго прохода — [сохранённая копия](remediation_round3/previous_main_documents/00_summary.md).
''', encoding='utf-8')

(R / '03_question_flows.md').write_text('''# Индивидуальные пути по ТЗ версии 2

Активные [графы 38 карточек](remediation_round3/question_graphs.yaml), [полные пути](remediation_round3/actual_question_paths.json) и [обоснования входов по результатам](remediation_round3/input_necessity.csv) относятся к третьему проходу. Цель 5–10 вопросов; обычный путь может содержать до 15 включительно. Считаются независимые сведения и начальные выборы, а не экраны.

Источник фиксирует название почечной метрики и единицу прямо в вопросе; вводится подтверждённое врачом числовое значение. Метод расчёта может храниться как происхождение, если не нужен самому табличному результату. Ошибочная единица или индексированная eGFR вместо требуемой абсолютной метрики блокирует число. Для каждого препарата в списке раздельно считаются МНН и статус; для ИМАО — необходимые тип и дата отмены; для фактического плана — сведения каждого этапа.

Фаза уже начатого лечения и условия второго препарата имеют отдельный счёт. Сложность определяется реальным условием источника/сценария. Длинный обычный путь не переименован в сложный из-за числа вопросов. Текущие обычные AGO, DULOX при ГТР и PREG превышают 15; №18 частичен, пока доказательного исправления нет. Нижняя граница AGO не выдаётся за полный путь или доказательство глобального оптимума.

Привязка поля к ветке сама по себе не доказывает минимальность всех вопросов. Необходимость неизменённых полей и раннего прекращения ещё проверяется независимо. Пропуск наблюдательного контекста означает not_assessed с предупреждением; выдача выбранного дозового действия не является полным клиническим допуском. Граф использует подготовленный expected и не исполняет медицинский калькулятор.
''', encoding='utf-8')

(R / '07_acceptance.md').write_text('''# Приёмка по версии 2

Канонические 30 критериев — [ACCEPTANCE_V2](../psychopharm_codex_pack/ACCEPTANCE_V2.md). Изменён только №18: цель 5–10 содержательных вопросов, допустимый обычный путь до 15 включительно. Исходный ACCEPTANCE и предыдущие заключения сохранены; путь 11–15 не штрафуется за прежний предел.

[Исполнительская таблица всех 30 критериев](remediation_round3/acceptance_recheck.json) и [расчёт предварительного балла](remediation_round3/scoring.json) не заменяют независимую приёмку. Проверяющий изучает первоисточники и зафиксированный снимок в acceptance_v2_audit/. Его находки могут изменить статусы и ограничение балла; найденные исправления требуют повторной проверки.

№17 и №18 остаются материальными открытыми требованиями: неудалимость каждого входа не доказана, несколько обычных путей превышают 15. Получение девяти ОХЛП закрывает приобретение источников, но не автоматически полноту медицинского переноса. PASS, число файлов и synthetic expected не являются основанием для 10/10. Приложение и клиническая валидация не выполнялись.

Прежняя таблица 27/3 с исходным лимитом сохранена [отдельно](remediation_round3/previous_main_documents/07_acceptance.md).
''', encoding='utf-8')

(R / '10_source_audit.md').write_text('''# Актуальность и проверка первоисточников

Для девяти прежних открытых оснований получены текущие официальные ОХЛП и ЛВ точных записей РФ. [Реестр](remediation_round3/current_registry_documents.json) фиксирует РУ/форму, отдельные регистрационный и экспертный штампы, оригинал, SHA, фактически прочитанные и визуально проверенные страницы. Неизвестные даты пересмотра/публикации сохранены. Номер редакции в имени файла не подменяет номер штампа.

Селектра и Золофт: официальные оригиналы из remediation_round2/. Девять новых пар: remediation_round3/originals/. [Индекс версий](remediation_round3/version_inventory.json) отделяет активные российские основания от исключённых зарубежных и архивных материалов. Номер Лирики ЛП-№(004450)-(РГ-RU) согласован с реестром.

Официальный статус, содержательная идентичность и побайтовое совпадение — разные утверждения. Текстовые diff не считаются полной клинической классификацией всех изменений. ЛВ не объявлены полностью медицински сверенными. Медицинский перенос и все 38 карточек независимо проверяются в acceptance_v2_audit/. Получение PDF не заменяет эту проверку.

Исторические источники/снимки/аудиты сохранены; новая запись поискового журнала указывает точную запись и фактический объём чтения. Клиническая валидация не заявляется.
''', encoding='utf-8')

replacements = {
    '01_scope_and_sources.md': [('Селектра остаётся кандидатом стратегии КР, однако её текущие числовые/органные/формовые извлечения не подтверждены: F01/F02/F13. Строки особых популяций описывают исследовательскую карту, а не разрешённые дозы недоступной новой инструкции. Последние лекарственные реестровые редакции отдельно не подтверждены (F12).', 'Селектра: официальный текущий оригинал подтверждён во втором проходе. Девять остальных текущих продуктовых оснований получены в третьем; актуальные версии — remediation_round3/version_inventory.json. Полнота переноса условий и специальных популяций проверяется отдельно от получения PDF; независимая приёмка выполняется по ACCEPTANCE_V2.')],
    '02_rules.md': [('remediation_round2/result_contracts.yaml и remediation_round2/full_scenarios.json. Последняя регистрационная редакция копий не доказана (F12); ready означает только ограниченный контракт фиксированного источника. Общая приёмка не достигнута.', 'remediation_round3/result_contracts.yaml и remediation_round3/full_scenarios.json. Текущие официальные оригиналы получены; полнота переноса проверяется отдельно. ready означает ограниченный контракт фиксированного источника. Независимая приёмка V2 и закрытие всех обычных путей до 15 пока не завершены.')],
    '05_gaps_and_conflicts.md': [('Материальные незакрытые требования — remediation_round2/limitations.md; они не считаются закрытыми предупреждениями или снятием ready. Повторная приёмка27/3, итог6,0/10 с исходным пределом; без него8,55.', 'Текущие материальные ограничения — remediation_round3/limitations.md. Девять официальных ОХЛП получены; полнота медицинского переноса и независимая приёмка V2 проверяются отдельно. Не доказана неудалимость всех вопросов; обычные пути AGO/DULOX ГТР/PREG превышают допустимые 15. Прежние оценки сохранены в исторических каталогах.')],
    '08_russian_priority_update.md': [('Для остальных опубликованные копии/штампы и наблюдения строк реестра разделены от независимой проверки последней редакции (F12).', 'Девять остальных текущих официальных ОХЛП получены в третьем проходе; статус реестра, содержательное сравнение и SHA разделены. Полнота медицинского переноса проверяется независимо.'), ('Результат исправления — remediation_round2/summary.md. 124 исходных ожидания сохранены как фрагменты; полные синтетические сценарии отдельно в remediation_round2/full_scenarios.json.', 'Текущий результат исправления — remediation_round3/README.md. 124 исходных ожидания сохранены как фрагменты; активные полные synthetic expected — remediation_round3/full_scenarios.json. Независимая приёмка — acceptance_v2_audit/.')],
    '09_download_links.md': [('актуальные выводы исправления — в [втором проходе](remediation_round2/summary.md)', 'исторический результат второго прохода — в [его итоге](remediation_round2/summary.md); текущие оригиналы девяти дополнительных ОХЛП/ЛВ перечислены в [реестре третьего прохода](remediation_round3/current_registry_documents.json)')],
    '06_implementation_brief.md': [('remediation_round2/full_scenarios.json', 'remediation_round3/full_scenarios.json'), ('[пять коротких путей]', '[адаптивные пути]')]
}
for name, pairs in replacements.items():
    text = (R / name).read_text(encoding='utf-8-sig')
    for before, after in pairs:
        assert before in text, (name, before)
        text = text.replace(before, after)
    if name == '06_implementation_brief.md':
        text = text[:text.index('Текущие контракты:')] + '''Текущие контракты: remediation_round3/input_contracts.yaml и result_contracts.yaml; графы question_graphs.yaml и полные actual_question_paths.json. Текущие официальные ОХЛП получены для всех девяти прежних открытых оснований. Действует ACCEPTANCE_V2: цель 5–10, обычный путь до 15 включительно. Минимальность и длинные обычные пути остаются ограничениями; независимая приёмка выполняется в acceptance_v2_audit/. Непройденный контекст наблюдения сохраняется явно и не означает клинический допуск. Любое выявленное при приёмке медицинское исправление требует повторной проверки перед переносом.
'''
    (R / name).write_text(text, encoding='utf-8')

log = R / 'search_log.csv'
with log.open(encoding='utf-8-sig', newline='') as f:
    reader = csv.DictReader(f)
    fields, rows = reader.fieldnames, list(reader)
docs = json.loads((O / 'current_registry_documents.json').read_text(encoding='utf-8'))['documents']
for d in docs:
    query = f"{d['query']}; {d['registration_number']}; {d['exact_form']}"
    if any(x['exact_query_or_request'] == query and x['database_or_site'] == 'official EAEU SmPC registry; human PDF download' for x in rows):
        continue
    rows.append(dict(date=d['accessed_on'], database_or_site='official EAEU SmPC registry; human PDF download', exact_query_or_request=query,
        found_source=d['registry_url'] + ' | ' + d['original_file'] + ' | SHA256=' + d['original_sha256'],
        read_part=d['current_source_locator'] + '; text pages=' + str(d['actually_read_text_physical_pages']) + '; visual pages=' + str(d['actually_reviewed_visual_physical_pages']),
        inclusion_status='current_official_original_obtained; listed sections read; independent transfer audit pending',
        reason='Exact RU/form record observed; user supplied PDFs after CAPTCHA request. Download is not complete medical transfer; PIL archived and not declared fully read.'))
with log.open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
print('Active documents updated; previous copies retained; search-log rows:', len(rows))
