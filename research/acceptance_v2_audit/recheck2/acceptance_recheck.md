# Все30 критериев ТЗ V2

23 выполнено/7частично. Изменён только№18; исходный ACCEPTANCE неизменен.

1. **выполнено** — Основной пользователь — психиатр, диагноз вводит врач; нет повторной диагностики и анкеты уверенности в диагнозе.

Диагноз/режим выбирает психиатр; PAR bipolar screen — узкая источниковая оценка, без повторной диагностики. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

2. **выполнено** — Фокус остался на тревожных/тревожно-депрессивных состояниях и применимости в РФ.

RF/EAEU labels и RU-GAD/PANIC/PHOB/DEP определяют область; иностранное сравнение не закрывает РФ пробел. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

3. **выполнено** — Основной сценарий — выбранный препарат → дозовая схема, не только выбор лекарства или прогноз концентрации.

38 cards содержат выбранный препарат/форму и дозовые либо ограниченные qualitative результаты, а не только рейтинг лекарств. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

4. **выполнено** — Исследованы старт, титрование/коррекция, отмена и переключение. Непокрытые режимы явно обозначены, не удалены молча.

Старт/коррекция/отмена/6направлений switch представлены; отсутствующие точные pair calendars явно clinician_choice/gap. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

5. **выполнено** — Дополнительный топ-3 опирается на КР; не создана собственная шкала индивидуального превосходства.

Топ-3 как варианты линий RU КР; индивидуальная шкала превосходства не придумана. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

6. **выполнено** — Дети, пожилые, беременность и лактация присутствуют в карте покрытия; нет автоматического переноса взрослых доз.

Карта детей/пожилых/беременности/лактации есть; известные детские и формовые ограничения не дают взрослую числовую схему. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

7. **выполнено** — Нет обязательной генетики, ML, истории пациентов, стоимости, профилей предпочтений и календаря визитов.

Обязательных генетики/ML/истории/стоимости/профилей/визитов нет; laboratory monitoring не является календарём посещений. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

8. **выполнено** — Есть точные МНН, показание, код/классификация, форма, популяция и режим.

INN/diagnosis/mode/population/identified product form present; current registration/form provenance reviewed. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

9. **частично** — Есть конкретный источник, версия и локатор, а не только ссылка на главную страницу реестра.

Current 11 primary product files/SHA/versions available; nested11377bases consistent. PHEN locator/attribution residual R2-03. Findings: R2-03. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

10. **частично** — Каждая медицинская доза, граница, поправка, срок и условие имеют источник.

211parameter rows/104distinct groups inspected; no numeric changes vs recheck1. Source-owned known actions corrected, but PREG/PHEN scope residual R2-03 and explicitly unverified completeness remain. Findings: R2-03. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

11. **выполнено** — Опубликованный диапазон не заменён произвольно выбранным числом; пример не превращён в обязательный протокол.

Source alternatives/ranges preserved: FLUV50or100, PREG25–50 and frequency alternatives; PAR taper an optional selected example. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

12. **выполнено** — Различаются разовая/суточная доза, единицы, кратность и лекарственные формы.

Daily/per-administration/frequency arithmetic consistent; CLcr/absoluteGFR/indexed units distinguished; form split/release bound to identified label. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

13. **выполнено** — Не перемножены самостоятельные поправки и не усреднены несовместимые источники.

Independent renal/hepatic/CYP changes not multiplied; DULOX overlap and XR combination stay clinician_choice. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

14. **частично** — Для переключения проверено направление, оба препарата, допустимость перекрытия и необходимый интервал.

Sources/roles and existing urgent A/B fixtures reviewed; new current-event nonstart A selected_mode→ongoing relation is not declared (R2-01). Full Russian pair calendar absent explicitly, not invented. Findings: R2-01. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

15. **частично** — Для отмены сохранены условия изменения темпа; нет единого придуманного процента/срока для всех.

Published minima/conditional symptoms retained; PREG/PHEN null resumption gaps fixed but narrative source-scope residual R2-03 remains. Findings: R2-03. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

16. **выполнено** — Баллы шкалы влияют на дозовое действие только там, где это действительно задано найденным правилом.

Scales provide monitoring where KR says so; no source-free dose coefficient or proprietary scoring. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

17. **частично** — Для каждого вопроса показано, какое правило использует ответ и почему его нельзя убрать.

906input rows,2230ledger rows,265decisions structurally connected;511always values not all proved individually necessary. PAR qualitative witness and21SER backward dialogue dependencies remain. Findings: R2-01, R2-02, R2-04. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

18. **частично** — Для обычного индивидуального дозового расчёта 5–10 содержательных вопросов — целевой диапазон; допустимо до 15 включительно при обоснованной необходимости каждого вопроса. Начальные выборы и независимые сведения считаются отдельно; нагрузка не скрыта в подпунктах или предварительной анкете, необходимые ограничения не удалены ради лимита.

Own531count checks confirm ordinary20/17/17–18/16; no full individual ordinary≤15 proof.11–15 not penalized for old limit. Findings: R2-05. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

19. **выполнено** — Для сложных веток зафиксирован предел короткого расчёта, а не удалены обязательные сведения.

Actual ESC CAD/electrolyte, organ/MAOI/switch source triggers explicit; complexity not assigned just from count. Aplan stages/day/dose/frequency and A/B facts separate. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

20. **выполнено** — «Неизвестно/не исследовано/не помню» не интерпретируются как норма/нет.

All531projections zero fabricated absent negatives / overlap; reported unknown/omitted no clinical clearance. A phase enum integration mismatch R2-01 does not turn unknown into normal. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

21. **выполнено** — Недостаток обязательного значения даёт конкретный запрос данных без безусловной дозы.

Full typed missing/unknown scenarios request named necessary fields with no executable dose; A/B unknown event phases request phase explicitly. Domain A repair remains required before schema implementation. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

22. **выполнено** — Схема может быть выдана заранее, но последующие условные шаги не показаны как обязательные.

Future stages are conditional; no guaranteed calendar or source-free taper percentages. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

23. **выполнено** — Минимальные интервалы изменения дозы не перепутаны с датами назначаемых врачом визитов.

Dose minima/monitoring intervals separate from clinician visit timing; AGO approximate laboratory weeks remain approximate. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

24. **выполнено** — Доступность первоисточника проверена; сниппет/абстракт/перепечатка не названы прочитанным оригиналом.

Actually accessible local official originals read; provided human registry download/stamp evidence distinct from own online click/download. Same prior PDF bytes verified before reuse; full PIL reading not claimed. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

25. **выполнено** — Российская регистрационная применимость не выведена из иностранного руководства.

Russian registered forms/labels bind rules; foreign examples not registration evidence. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

26. **выполнено** — Источник/КР/экспертный протокол/исследованная модель имеют разные, точно описанные статусы.

KR/label/expert interpretation/protocol/effectiveness study have different declared statuses. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

27. **выполнено** — Эффективность препарата не объявлена доказательством любой алгоритмической дозировки.

Drug efficacy/PK percentage not proof of any algorithmic dose; current DULOX glycemia evidence not dose factor. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

28. **выполнено** — Технический перенос не объявлен клинической валидацией нового продукта.

Static/graphs/prepared expected not executed app or clinical trial; clinical validation not performed. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

29. **выполнено** — Готовность к реализации не перепутана с готовностью к клиническому применению.

Allowed technical transfer restricted to checked contracts/facts/gaps; no claim of clinical deployment readiness. Findings: нет новых по этому пункту. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.

30. **частично** — Все пробелы и конфликты перечислены; отсутствие найденного аналога не названо доказательством его отсутствия.

Main indices reflect current ESC and protected history; new R2 enum/necessity/scope/order findings not yet repaired in frozen package; no absence-of-analogue proof. Findings: R2-01, R2-02, R2-03, R2-04, R2-05. Проверенные файлы: cards/contracts/expected, own source_verification и paths. Ограничение: primary/necessity охват подробно в coverage; это исследовательская оценка.
