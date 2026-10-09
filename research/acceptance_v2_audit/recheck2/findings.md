# Находки recheck2

## R2-01 — substantial integration defect

Файл: `research/remediation_round3/input_contracts.yaml:147`. Карточки: ser-panic-start, ser-social-start, preg-gad-start, preg-renal-start, dulox-depression-start, dulox-gad-start, venla-xr-gad-start, venla-xr-social-start, venla-xr-panic-form-limit, dulox-gad-adjust, dulox-taper-limit, preg-gad-adjust, preg-taper-limit, ser-adult-adjust, ser-taper-limit, switch-ser-ago, switch-ser-esc, venla-xr-taper-limit. Критерии: [14, 17, 21].

Утверждение: Фазы первой дозы, текущей терапии и unknown типизированы и различаются.

Установлено: Домен treatment_phase содержит только ongoing/selected_mode;18cases используют not_started/unknown. Graph отдельно считает unknown, а author validate принимает invalid_phase. Кроме этого schema явно определяет selected_mode только для start=first administration;9 новых positive current-event cases для nonstart A используют selected_mode при условии source_phase=ongoing. Вопросы событий говорят о текущем приёме, но show_when требует отдельно известную фазу A/B: необходимо согласовать происхождение этого факта. Одно желаемое дозовое действие не доказывает факт приёма.

Влияние: Не менять источниковые числа; текущий enum A нельзя перенести как согласованный контракт. Unknown expected правильно запрашивает фазу, но этот input не принадлежит объявленному домену.

Исправление: Согласовать домен и mode-specific origin A, проверить enum A наряду с B. Для current-event action нужна подтверждённая taking phase. Допустимо вывести ongoing у nonstart из активного, реально потреблённого current_dose с документированной семантикой фактически принимаемой сейчас дозы данного A/product, известным положительным значением и происхождением. Report-only/inactive/proposed/unknown/zero этого не подтверждают; явные unknown/not_started нельзя перекрывать таким выводом. При отсутствии подтверждённого current-treatment факта нужна явная A phase с отдельным count. Повторно не спрашивать уже подтверждённую фазу. Добавить unknown/not_started nonstart A fixtures и отрицательные мутации.

Условие закрытия: Новый SHA; все cases имеют объявленную фазу, invalid phase отвергнута, known/not_started/unknown actors/actions/count сохранены. Это допустимое условие закрытия ещё не применённого патча, не утверждение о проверке будущей версии.

Первоисточники/версии/SHA/локаторы полностью в findings.json; source_verification фиксирует фактическое чтение.

## R2-02 — substantial necessity gap

Файл: `research/remediation_round3/rules/parox-taper-example.yaml:107`. Карточки: parox-taper-example, preg-taper-limit, phen-taper-limit. Критерии: [17].

Утверждение: Каждое always поле необходимо именно выбранному результату.

Установлено: Существующий branch other/current10 не вычисляет календарь, но duration/past_withdrawal всегда обязательны. Собственный допустимый example_selected=false также не использует current_dose; это логический witness, не существующий frozen fixture. Age в качественных PREG/PHEN ограничениях нуждается в отдельном доказательстве: запрет применения/взрослая область не равны запрету показать условное взрослое источниковое правило прекращения.

Влияние: 22 демоции полезны, но не доказывают неудалимость остальных 511 always входов по каждому исходу. Ни эти сведения, ни возраст нельзя незаметно считать нормальными.

Исправление: Разделить необходимость numerical selected40 и qualitative other; зависимые вопросы после контролирующего выбора. Для population-unknown допускается только явно условная взрослая справка, без individual_duration/schedule/clinical clearance; child не получает взрослую схему.

Условие закрытия: Новый result-specific predicate/ledger/expected с missing/unknown/false выбора и current10, взрослым/неизвестным/детским возрастом; срочные source actions сохраняются. Все оставшиеся необходимости отдельно доказаны либо отмечены открытыми.

Первоисточники/версии/SHA/локаторы полностью в findings.json; source_verification фиксирует фактическое чтение.

## R2-03 — substantial source-scope residual

Файл: `research/remediation_round3/rules/phen-taper-limit.yaml:212`. Карточки: phen-taper-limit, preg-taper-limit. Критерии: [9, 10, 15, 30].

Утверждение: Неподтверждённое возобновление PREG/PHEN заменено null+gap и опубликованная постепенность сохранена.

Установлено: Expected resumption действительно null+gap. Однако PHEN why_needed/necessity_reason приписывают источнику удержание/возврат/замедление; logic.actions ссылается на постепенность физ.3 вместо2. PREG logic.actions[1] приписывает КР более медленную индивидуальную отмену при длительном приёме/высоком риске: применимое найденное приложение RU-GAD Б2 физ.77–78 относится к АНТИДЕПРЕССАНТАМ, не PREG.

Влияние: Новой ошибочной числовой ступени/возобновляемой дозы нет. Но опубликованное основание PREG/PHEN действия и necessity цепочки всё ещё неверно расширено.

Исправление: Убрать неподтверждённую атрибуцию hold/restore/slower, указать индивидуальное решение врача и конкретный source gap. PHEN постепенность физ.2; AD алгоритм оставить в его области. Обновить card/ledger/reasons/projections/indices согласованно.

Условие закрытия: Новый SHA; первичный PHEN/PREG scope совпадает с narrative/why/necessity/expected; поиск остаточных generic restore/slow атрибуций и изолированная scope mutation проходят.

Первоисточники/версии/SHA/локаторы полностью в findings.json; source_verification фиксирует фактическое чтение.

## R2-04 — substantial dialogue-order gap

Файл: `research/remediation_round3/rules/ser-adult-adjust.yaml:396`. Карточки: ser-adult-adjust. Критерии: [17].

Утверждение: Граф даёт адаптивный полный путь нового расчёта, без скрытого предварительного ввода.

Установлено: 21 selected traces проверяют условные time_at_dose/response/tolerability/adherence/akathisia до ask_clinician_action; этот контроллер отсутствует в initial_selections. branch-increase: checks27/30/31/32/37, ask controller41. branch-keep: ask37. Builder определяет active по уже полному future given.

Влияние: Конечный факт-набор и count правильны, но это не доказывает причинный порядок нового короткого диалога. Дозовой калькулятор не запускался.

Исправление: Контроллер спрашивается/явно поступает раньше зависимого check; топологический порядок по объявленным dependencies. Повторное использование реально известных текущих фактов отдельно от полного нового набора.

Условие закрытия: Новый граф/SHA; causal dependency check без обратных зависимостей, complete path counts/unknown/keep/increase клинические expected неизменны.

Первоисточники/версии/SHA/локаторы полностью в findings.json; source_verification фиксирует фактическое чтение.

## R2-05 — substantial unmet requirement

Файл: `research/remediation_round3/actual_question_paths.json:1`. Карточки: ago-depression-start, ago-gad-start, dulox-gad-start, preg-gad-start, ser-adult-adjust. Критерии: [18].

Утверждение: Обычные длинные пути честно оставлены открытыми; глобальный минимум не объявлен.

Установлено: Независимый пересчёт подтверждает ordinary AGO20, DULOX-GAD17, PREG17/18 и SER increase+explicit reported negative event16. Они не переименованы в сложные. Обоснованный общий вариант ordinary≤15 пока не доказан.

Влияние: Материально незакрытый №18; cap≤6. Короткий пример или справочная альтернатива не закрывает индивидуальный числовой путь.

Исправление: Доказать result-specific необходимость и весь реальный допустимый путь ≤15 либо честно сохранить предел/непокрытую обычную ветку. Не удалять срочные действия или склеивать независимые сведения.

Условие закрытия: Источник + полный given/expected + causal graph/count + unknown/conditional alternatives. Narrow hepatic AGO assessment даёт арифметически17; потенциальная дополнительная renal demotion16 ещё не закрывает≤15. PREG frequency options без выбора не точный индивидуальный результат.

Первоисточники/версии/SHA/локаторы полностью в findings.json; source_verification фиксирует фактическое чтение.

## Точное закрытие прошлых находок

- V2-01: closed in original scope. Ранее проверенная правка сохранена; medical parameters unchanged and source SHA equality confirmed.
- V2-02: closed in original scope. Ранее проверенная правка сохранена; medical parameters unchanged and source SHA equality confirmed.
- V2-03: closed in original scope. Ранее проверенная правка сохранена; medical parameters unchanged and source SHA equality confirmed.
- V2-04: closed in original scope. Ранее проверенная правка сохранена; medical parameters unchanged and source SHA equality confirmed.
- V2-05: closed in original scope. Ранее проверенная правка сохранена; medical parameters unchanged and source SHA equality confirmed.
- V2-06: closed in original scope. Ранее проверенная правка сохранена; medical parameters unchanged and source SHA equality confirmed.
- V2-07: closed in original scope. Ранее проверенная правка сохранена; medical parameters unchanged and source SHA equality confirmed.
- V2-08: closed in original scope. 68 ранее зафиксированных locator records изменены; текущие PAR физ.страницы, DULOX §4.8 physical11/14 и AGO/PREG типовые locators сверены. Новая PHEN scope/locator ошибка отдельно R2-03.
- V2-09: closed in original scope. Ранее проверенная правка сохранена; medical parameters unchanged and source SHA equality confirmed.
- V2-10: closed in original scope. Все531 projected paths: zero absent negatives/negative-unassessed overlap/hidden positive input; SER strong_CYP3A4 qualitative path count9 includes INN/status.
- V2-11: closed in original scope. Current main01/09 не объявляют ESC unavailable; README/main pointers и historical copies различаются.
- V2-12: partial/open. 22 qualitative operands demoted; PREG3 закрыты. Полная necessity остаётся открытой; R2-02/04.
- V2-13: partial/open. Long ordinary20/17/17–18/16 сохраняются; R2-05.
- V2-14: closed in original scope. Ранее проверенная правка сохранена; medical parameters unchanged and source SHA equality confirmed.
- R1-01: partial: source actions checked, nonstart A phase mapping unresolved (R2-01). Four known events preserve exact consider/help actions, actor and ongoing phase; unknown/omitted explicit unassessed; missing phase requests a named field. Domain mismatch separately R2-01.
- R1-02: closed in reviewed source/expected scope. Seven XR classes: caution / avoid QT / not recommended precursor and weightloss, no invented factor; all4 cards fixtures independently checked.
- R1-03: closed in reviewed source/expected scope. Own SER gate both SSRI directions, source role A/B and strong_CYP3A4 avoidance retained; no pair calendar invented.
- R1-04: closed in reviewed source/expected scope. Additional concurrent duloxetine product counted as a separate fact; selected product alone not duplicate; unknown additional identity blocked.
- R1-05: closed in reviewed source/expected scope. All4 PREG SCAR known-stop results: immediate stop plus conditional consider alternative; no named/dosed alternative.
- R1-06: partial: expected fixed, narrative/necessity residual open. Expected prior_dose_resumption null+gap correct for PREG/PHEN; residual source-attribution metadata remains R2-03.
- R1-07: closed in reviewed source/expected scope. XR confirmed pregnancy question differs from suspected pregnancy; both facts still counted.
