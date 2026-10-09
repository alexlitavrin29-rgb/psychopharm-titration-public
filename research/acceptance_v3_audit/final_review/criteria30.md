# Все30 критериев ТЗ V3

Снимок `b13033a0687a28b4da4299c171ac6b88a96667e2d6888ab8aecf5e9c85af0514`. **28 выполнено,2 частично(№17 и№20)**. №18 оценён в редакции V3 без жёсткого предела.

## 1. выполнено

Основной пользователь — психиатр, диагноз вводит врач; нет повторной диагностики и анкеты уверенности в диагнозе.

38 выбранных карточек используют диагноз и действие психиатра; PAR bipolar screen — источниковая узкая оценка, не повторная диагностика.

Свидетельства: [main_alignment_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/main_alignment_checks.json>), [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>).

## 2. выполнено

Фокус остался на тревожных/тревожно-депрессивных состояниях и применимости в РФ.

Российские КР GAD/PANIC/PHOB/DEP и регистрационные источники задают основной профиль; зарубежные сравнения не заполняют российский пробел.

Свидетельства: [main_alignment_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/main_alignment_checks.json>), [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>).

## 3. выполнено

Основной сценарий — выбранный препарат → дозовая схема, не только выбор лекарства или прогноз концентрации.

Карточки дают source-bound дозовые действия выбранного препарата или явно ограниченный gap/choice, а не только рейтинг или прогноз концентрации.

Свидетельства: [main_alignment_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/main_alignment_checks.json>), [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>).

## 4. выполнено

Исследованы старт, титрование/коррекция, отмена и переключение. Непокрытые режимы явно обозначены, не удалены молча.

Старт, коррекция, отмена и направления переключения представлены; отсутствующие российские calendars явно сохранены как gaps.

Свидетельства: [main_alignment_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/main_alignment_checks.json>), [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>).

## 5. выполнено

Дополнительный топ-3 опирается на КР; не создана собственная шкала индивидуального превосходства.

Топ-3 основан на линиях КР; собственной шкалы индивидуального превосходства нет.

Свидетельства: [main_alignment_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/main_alignment_checks.json>), [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>).

## 6. выполнено

Дети, пожилые, беременность и лактация присутствуют в карте покрытия; нет автоматического переноса взрослых доз.

Возрастные/детские, пожилые, pregnancy/lactation области присутствуют. Known child/unknown population не получают взрослую индивидуальную схему.

Свидетельства: [main_alignment_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/main_alignment_checks.json>), [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>).

## 7. выполнено

Нет обязательной генетики, ML, истории пациентов, стоимости, профилей предпочтений и календаря визитов.

Генетика, ML, patient history database, стоимость, preference profiles и календарь визитов не обязательны. Лабораторные source monitoring сроки не выданы за визиты.

Свидетельства: [main_alignment_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/main_alignment_checks.json>), [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>).

## 8. выполнено

Есть точные МНН, показание, код/классификация, форма, популяция и режим.

Main и round3 содержат38 идентичных активных карточек с INN/indication/code/mode/population/own product/form.906 active inputs отделены от26 дополнительных каталоговых зависимостей.

Свидетельства: [main_alignment_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/main_alignment_checks.json>), [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>).

## 9. выполнено

Есть конкретный источник, версия и локатор, а не только ссылка на главную страницу реестра.

13503 nested source bindings соответствуют собственному owner/version/SHA; текущие originals и physical locators сверены. PHEN physical form locator, IR version, SER/ESC provenance исправлены. SHA, регистрация и редакция различаются.

Свидетельства: [main_alignment_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/main_alignment_checks.json>), [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>).

## 10. выполнено

Каждая медицинская доза, граница, поправка, срок и условие имеют источник.

Завершённый USED первичный инвентарь391 norm-key records/6241 old occurrences/906 bindings повторно привязан по той же SHA.211 numeric objects,249 prose groups и все уникальные используемые условия были первично прочитаны; текущие изменённые action/result scopes и1867 used causes/actions проверены. Непереносимые источник-пробелы не заполнены числами.

Свидетельства: [used_expected_condition_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/used_expected_condition_checks.json>), [all_expected_check_results.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/all_expected_check_results.json>), [source_scope_review.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_scope_review.json>).

## 11. выполнено

Опубликованный диапазон не заменён произвольно выбранным числом; пример не превращён в обязательный протокол.

Диапазоны/physician options FLUV50or100, PREG25–50/frequencies и optional selectedPAR40 сохранены; пример не превращён в обязательный ladder.

Свидетельства: [used_expected_condition_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/used_expected_condition_checks.json>), [all_expected_check_results.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/all_expected_check_results.json>), [source_scope_review.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_scope_review.json>).

## 12. выполнено

Различаются разовая/суточная доза, единицы, кратность и лекарственные формы.

20647 own prepared assertions проверяют total/per-administration/frequency, units/renal metric и формы. Нет автоматического IR/XR переноса, деления запрещённой формы или исполнения ошибочной printed renal unit.

Свидетельства: [used_expected_condition_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/used_expected_condition_checks.json>), [all_expected_check_results.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/all_expected_check_results.json>), [source_scope_review.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_scope_review.json>).

## 13. выполнено

Не перемножены самостоятельные поправки и не усреднены несовместимые источники.

Independent hepatic/renal/CYP adjustments не перемножены; DULOX combined modifiers и XR overlap остаются physician_choice/gap.

Свидетельства: [used_expected_condition_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/used_expected_condition_checks.json>), [all_expected_check_results.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/all_expected_check_results.json>), [source_scope_review.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_scope_review.json>).

## 14. выполнено

Для переключения проверено направление, оба препарата, допустимость перекрытия и необходимый интервал.

Own A/B forms, source clocks, direction и phase проверены.87 no-auto/source-reference guards сохраняют опубликованный AGO25/overlap как справку, не patient-specific permission. Selected PAR40 composition ограничена явно выбранным примером; полный generic calendar не заявлен.

Свидетельства: [used_expected_condition_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/used_expected_condition_checks.json>), [all_expected_check_results.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/all_expected_check_results.json>), [source_scope_review.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_scope_review.json>).

## 15. выполнено

Для отмены сохранены условия изменения темпа; нет единого придуманного процента/срока для всех.

Дозовой общий процент отмены не придуман. DULOX обычный минимум2weeks без потолка учитывает обе нормы; SSRI/XR variation и symptoms source actions сохранены, PREG/PHEN не заимствуют AD hold/restore/slower.

Свидетельства: [used_expected_condition_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/used_expected_condition_checks.json>), [all_expected_check_results.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/all_expected_check_results.json>), [source_scope_review.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_scope_review.json>).

## 16. выполнено

Баллы шкалы влияют на дозовое действие только там, где это действительно задано найденным правилом.

Ни monitoring scale, ни efficacy/PK data не создают coefficient без source rule.

Свидетельства: [used_expected_condition_checks.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/used_expected_condition_checks.json>), [all_expected_check_results.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/all_expected_check_results.json>), [source_scope_review.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_scope_review.json>).

## 17. частично

Для каждого вопроса показано, какое правило использует ответ и почему его нельзя убрать.

906 полей и сохраняемые mandatory/result scopes рассмотрены по собственным первичным нормам. Для numeric outputs прямые source gates/operands сохранены. Но finite V3-01/02/03/04/07 показывают unrelated always после достаточного bounded cause/reference/refusal; таблица906 и witnesses не доказывают эти crossproducts.

Свидетельства: [necessity_906_review.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/necessity_906_review.json>), [counts_independent.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/counts_independent.json>), [independent_data_results.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/independent_data_results.json>), [findings.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/findings.json>).

## 18. выполнено

Для обычного индивидуального дозового расчёта 5–10 содержательных вопросов — цель удобства, до 15 — желательный ориентир; более 15 допустимо при обоснованной необходимости обязательных вопросов для конкретного результата. Само превышение числа вопросов не является нарушением или основанием снижения оценки. Начальные выборы и независимые сведения считаются открыто; нагрузка не скрыта в подпунктах или предварительной анкете, необходимые ограничения не удалены ради краткости, длинная обычная ветка не переименована в сложную.

Самостоятельно восстановлены1907 selected paths, в том числе96 обычных числовых10–34. Начальные выборы и supplied independent optional positive/negative/unknown считаются. Ни одного lower_bound; длинный обычный путь не переименован в сложный. V3 снимает upper limit; необходимость отдельный№17, длина сама не штрафуется.

Свидетельства: [necessity_906_review.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/necessity_906_review.json>), [counts_independent.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/counts_independent.json>), [independent_data_results.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/independent_data_results.json>), [findings.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/findings.json>).

## 19. выполнено

Для сложных веток зафиксирован предел короткого расчёта, а не удалены обязательные сведения.

Source-triggered CAD/electrolyte/MAOI/organ/switch complexity явна. Own actor, stages/day/dose/frequency и independent clocks считаются отдельно; счёт сложного пути не скрыт.

Свидетельства: [necessity_906_review.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/necessity_906_review.json>), [counts_independent.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/counts_independent.json>), [independent_data_results.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/independent_data_results.json>), [findings.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/findings.json>).

## 20. частично

«Неизвестно/не исследовано/не помню» не интерпретируются как норма/нет.

Typed unknown/units/phase/medicine classification в projected paths корректны. Однако24 raw expected в PAR→AGO сохраняют неизвестные optional поля в confirmed_negatives. Это конкретное несоответствие полных эталонов; нет нового подтверждённого критического numeric допуска.

Свидетельства: [necessity_906_review.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/necessity_906_review.json>), [counts_independent.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/counts_independent.json>), [independent_data_results.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/independent_data_results.json>), [findings.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/findings.json>).

## 21. выполнено

Недостаток обязательного значения даёт конкретный запрос данных без безусловной дозы.

Missing mandatory operands дают named request без unconditional dose. Unknown class запрашивает classification передMAOItype/time, own actor unknown/not_started не создаёт automatic stop/start.

Свидетельства: [necessity_906_review.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/necessity_906_review.json>), [counts_independent.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/counts_independent.json>), [independent_data_results.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/independent_data_results.json>), [findings.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/findings.json>).

## 22. выполнено

Схема может быть выдана заранее, но последующие условные шаги не показаны как обязательные.

Future stages имеют условия повторного выбора/оценки; stop/choice/gap не наследуют executable future dose/overlap/calendar. Печатный source reference отдельно от индивидуального действия.

Свидетельства: [necessity_906_review.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/necessity_906_review.json>), [counts_independent.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/counts_independent.json>), [independent_data_results.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/independent_data_results.json>), [findings.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/findings.json>).

## 23. выполнено

Минимальные интервалы изменения дозы не перепутаны с датами назначаемых врачом визитов.

Minimum interval, approximate laboratory monitoring и physician visit timing не смешаны.

Свидетельства: [necessity_906_review.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/necessity_906_review.json>), [counts_independent.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/counts_independent.json>), [independent_data_results.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/independent_data_results.json>), [findings.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/findings.json>).

## 24. выполнено

Доступность первоисточника проверена; сниппет/абстракт/перепечатка не названы прочитанным оригиналом.

Own actual primary reading receipts доступны.16 source registry records повторно SHA-checked; старое чтение same bytes зачтено как reuse, не заявлено новым чтением. Human registry originals/CAPTCHA evidence не приписаны самостоятельному сетевому скачиванию.

Свидетельства: [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>), [transfer_decision.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/transfer_decision.json>), [findings.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/findings.json>).

## 25. выполнено

Российская регистрационная применимость не выведена из иностранного руководства.

Российская применимость определена own current registered product/form и КР; иностранные руководства не заменяют её.

Свидетельства: [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>), [transfer_decision.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/transfer_decision.json>), [findings.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/findings.json>).

## 26. выполнено

Источник/КР/экспертный протокол/исследованная модель имеют разные, точно описанные статусы.

КР/label/expert composition/form policy/source reference/model/effectiveness study имеют разные статусы. PREG source table и model whole-form policy явно различены.

Свидетельства: [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>), [transfer_decision.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/transfer_decision.json>), [findings.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/findings.json>).

## 27. выполнено

Эффективность препарата не объявлена доказательством любой алгоритмической дозировки.

Efficacy не доказательство algorithmic dosage. DULOX diabetes adverse-reaction context не коэффициент; medication class fixtures не объявлены исполненным INN classifier.

Свидетельства: [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>), [transfer_decision.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/transfer_decision.json>), [findings.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/findings.json>).

## 28. выполнено

Технический перенос не объявлен клинической валидацией нового продукта.

Static checks, prepared expectations и graph traces не названы запуском приложения или клинической валидацией.

Свидетельства: [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>), [transfer_decision.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/transfer_decision.json>), [findings.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/findings.json>).

## 29. выполнено

Готовность к реализации не перепутана с готовностью к клиническому применению.

Допустимый технический перенос конкретно ограничен проверенными values/forms/conditions/contracts; patient deployment clearance и весь current mandatory dialogue не приняты.

Свидетельства: [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>), [transfer_decision.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/transfer_decision.json>), [findings.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/findings.json>).

## 30. выполнено

Все пробелы и конфликты перечислены; отсутствие найденного аналога не названо доказательством его отсутствия.

Известные source conflicts/gaps и finite current necessity/metadata/technical остатки перечислены. Отсутствие найденного российского полного pair/taper protocol не объявлено его доказанным отсутствием.

Свидетельства: [source_read_registry.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/source_read_registry.json>), [transfer_decision.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/transfer_decision.json>), [findings.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/findings.json>).
