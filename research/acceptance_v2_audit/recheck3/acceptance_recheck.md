# Все 30 критериев ТЗ V2

**27 выполнено / 3 частично**. Изменён только №18. Это частичная исследовательская приёмка.

1. **выполнено** — Основной пользователь — психиатр, диагноз вводит врач; нет повторной диагностики и анкеты уверенности в диагнозе.

Диагноз/режим выбирает психиатр; PAR bipolar screen — узкая источниковая оценка, без повторной диагностики.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

2. **выполнено** — Фокус остался на тревожных/тревожно-депрессивных состояниях и применимости в РФ.

RF/EAEU labels и RU-GAD/PANIC/PHOB/DEP определяют область; иностранное сравнение не закрывает РФ пробел.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

3. **выполнено** — Основной сценарий — выбранный препарат → дозовая схема, не только выбор лекарства или прогноз концентрации.

38 cards содержат выбранный препарат/форму и дозовые либо ограниченные qualitative результаты, а не только рейтинг лекарств.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

4. **выполнено** — Исследованы старт, титрование/коррекция, отмена и переключение. Непокрытые режимы явно обозначены, не удалены молча.

Старт/коррекция/отмена/6направлений switch представлены; отсутствующие точные pair calendars явно clinician_choice/gap.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

5. **выполнено** — Дополнительный топ-3 опирается на КР; не создана собственная шкала индивидуального превосходства.

Топ-3 как варианты линий RU КР; индивидуальная шкала превосходства не придумана.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

6. **выполнено** — Дети, пожилые, беременность и лактация присутствуют в карте покрытия; нет автоматического переноса взрослых доз.

Карта детей/пожилых/беременности/лактации есть; известные детские и формовые ограничения не дают взрослую числовую схему.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

7. **выполнено** — Нет обязательной генетики, ML, истории пациентов, стоимости, профилей предпочтений и календаря визитов.

Обязательных генетики/ML/истории/стоимости/профилей/визитов нет; laboratory monitoring не является календарём посещений.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

8. **выполнено** — Есть точные МНН, показание, код/классификация, форма, популяция и режим.

INN/diagnosis/mode/population/identified product form present; current registration/form provenance reviewed.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

9. **выполнено** — Есть конкретный источник, версия и локатор, а не только ссылка на главную страницу реестра.

Current source owners/versions/SHA remain bound. PHEN physical2/4 locator and source-attribution residual corrected;11801 nested source bases match owner/version/SHA. Source provenance and current registry copy identity remain separately described.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

10. **частично** — Каждая медицинская доза, граница, поправка, срок и условие имеют источник.

All211 parameter objects unchanged from recheck2 and104distinct groups covered by actual primary reading. New population/source-scope results checked independently; exhaustive every-condition→expected medical verification not completed (R3-LIMIT-01).

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

11. **выполнено** — Опубликованный диапазон не заменён произвольно выбранным числом; пример не превращён в обязательный протокол.

Source alternatives/ranges preserved: FLUV50or100, PREG25–50 and frequency alternatives; PAR taper an optional selected example.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

12. **выполнено** — Различаются разовая/суточная доза, единицы, кратность и лекарственные формы.

Daily/per-administration/frequency arithmetic consistent; CLcr/absoluteGFR/indexed units distinguished; form split/release bound to identified label.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

13. **выполнено** — Не перемножены самостоятельные поправки и не усреднены несовместимые источники.

Independent renal/hepatic/CYP changes not multiplied; DULOX overlap and XR combination stay clinician_choice.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

14. **выполнено** — Для переключения проверено направление, оба препарата, допустимость перекрытия и необходимый интервал.

Explicit A/B source roles and phase gates reviewed: current A may derive ongoing only from consumed active actual positive dose; unknown/not_started overrides, B separate. Russian pair calendar gaps remain explicit; no silent overlap or wait invented.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

15. **выполнено** — Для отмены сохранены условия изменения темпа; нет единого придуманного процента/срока для всех.

PREG/PHEN resumption/hold/slower permission no longer borrowed; published gradual restriction/source gaps and urgent conditions retained. Conditional adult reference does not assign pediatric/unknown individual duration. Other source taper families remain as previously independently reviewed on identical originals.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

16. **выполнено** — Баллы шкалы влияют на дозовое действие только там, где это действительно задано найденным правилом.

Scales provide monitoring where KR says so; no source-free dose coefficient or proprietary scoring.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

17. **частично** — Для каждого вопроса показано, какое правило использует ответ и почему его нельзя убрать.

Causal order and concrete qualitative counterexamples fixed; all737 fact sets/counts independently agree. Full necessity of the remaining mandatory fields across271 decisions is not proved (R3-LIMIT-02).

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

18. **частично** — Для обычного индивидуального дозового расчёта 5–10 содержательных вопросов — целевой диапазон; допустимо до 15 включительно при обоснованной необходимости каждого вопроса. Начальные выборы и независимые сведения считаются отдельно; нагрузка не скрыта в подпунктах или предварительной анкете, необходимые ограничения не удалены ради лимита.

Ordinary AGO20,DULOX-GAD17,PREG17/18,SER increase15 plus separately reported negative event16 independently confirmed; no complete≤15 alternative/global minimum proved.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

19. **выполнено** — Для сложных веток зафиксирован предел короткого расчёта, а не удалены обязательные сведения.

Actual ESC CAD/electrolyte, organ/MAOI/switch source triggers explicit; complexity not assigned just from count. Aplan stages/day/dose/frequency and A/B facts separate.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

20. **выполнено** — «Неизвестно/не исследовано/не помню» не интерпретируются как норма/нет.

All531projections zero fabricated absent negatives / overlap; reported unknown/omitted no clinical clearance. A phase enum integration mismatch R2-01 does not turn unknown into normal.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

21. **выполнено** — Недостаток обязательного значения даёт конкретный запрос данных без безусловной дозы.

Missing/unknown required operands request concrete fields without unconditional dose; A phase enum now includes actual fixture states and invalid enum/domain mutations reject. Explicit unknown/not_started source action variants do not automatically stop or start a medication.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

22. **выполнено** — Схема может быть выдана заранее, но последующие условные шаги не показаны как обязательные.

Future stages are conditional; no guaranteed calendar or source-free taper percentages.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

23. **выполнено** — Минимальные интервалы изменения дозы не перепутаны с датами назначаемых врачом визитов.

Dose minima/monitoring intervals separate from clinician visit timing; AGO approximate laboratory weeks remain approximate.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

24. **выполнено** — Доступность первоисточника проверена; сниппет/абстракт/перепечатка не названы прочитанным оригиналом.

Actually accessible local official originals read; provided human registry download/stamp evidence distinct from own online click/download. Same prior PDF bytes verified before reuse; full PIL reading not claimed.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

25. **выполнено** — Российская регистрационная применимость не выведена из иностранного руководства.

Russian registered forms/labels bind rules; foreign examples not registration evidence.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

26. **выполнено** — Источник/КР/экспертный протокол/исследованная модель имеют разные, точно описанные статусы.

KR/label/expert interpretation/protocol/effectiveness study have different declared statuses.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

27. **выполнено** — Эффективность препарата не объявлена доказательством любой алгоритмической дозировки.

Drug efficacy/PK percentage not proof of any algorithmic dose; current DULOX glycemia evidence not dose factor.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

28. **выполнено** — Технический перенос не объявлен клинической валидацией нового продукта.

Static/graphs/prepared expected not executed app or clinical trial; clinical validation not performed.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

29. **выполнено** — Готовность к реализации не перепутана с готовностью к клиническому применению.

Allowed technical transfer restricted to checked contracts/facts/gaps; no claim of clinical deployment readiness.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.

30. **выполнено** — Все пробелы и конфликты перечислены; отсутствие найденного аналога не названо доказательством его отсутствия.

Known conflicts, long ordinary paths, unproved necessity and independent coverage limits are explicit; indices distinguish pending snapshot review from current completed audit. No assertion that an unfound analogue cannot exist.

Файлы/проверки: текущие cards/contracts/full_scenarios, independent_paths/recheck3_checks; первичные локаторы и фактическая глубина — source_verification/coverage. Ограничение: Status is the stated research-contract scope, not clinical clearance. Actual primary reading/reuse and unverified source conditions/necessity are listed in coverage/source_verification; no exhaustive medical or app execution claim.
