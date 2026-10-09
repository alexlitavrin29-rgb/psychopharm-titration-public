# Остатки в неизменной копии 8fe52f…

## RCR-01 — отдельный неизвестный тип ИМАО потребляется бесплатно

В copied `build_graphs.py` active допускает interaction_class `unknown` для `maoi_record`, а `facts(record_map)` перечисляет только class `maoi`. Например `esc-adult-adjust--audit-final-primary-RU-ESC-reversible_MAO_A-unknown`: `ask_maoi_type` посещён, projected given содержит `maoi_type.primary_class=unknown`, но required_independent_facts его не содержит; count=29. Аналогично `switch-ser-esc--audit-final-primary-RU-SER-bleeding-unknown`: count=14. Полный список **79** путей: [count_defects.json](count_defects.json).

Это содержательный дефект честного счёта и причинного порядка, не штраф за длинный путь. Источниковые ИМАО type/clock условия RU-ESC физ.7–8 и RU-SER физ.7–8 применяются к соответствующему подтверждённому типу; неизвестный класс не становится известным ИМАО.

Безопасное закрытие: либо считать каждый действительно запрошенный/потреблённый отдельный тип, либо сначала уточнять классификацию и не активировать speculative type/timestamp при unknown class. Во втором варианте согласовать full missing_fields, проекции и question traces; известные MAOI type/date и их собственные часы сохранить. Новая фактически сообщённая отдельная классификация не должна становиться бесплатным предварительным фактом. Исправление live пока не проверено.

## RCR-02 — три generic unknown смешивают published reference и permission

Случаи `switch-esc-ago--audit-final-primary-RU-AGO-mania-unknown`, `…suicide_risk-unknown`, `…alcohol_use-unknown` сохраняют `overlap_allowed_on_first_day_of_A_reduction=True` и `target_source_start_mg=25`, одновременно `target_source_start_scope` говорит reference-only/no automatic target start/overlap. Unknown generic caution может остаться clinician_choice с not_assessed; обязательное False для исправления не требуется.

RU-AGO SHA `a98d383832688cee9a09588b1a908555d01ed8b659281cdeee2646c1115ce7c1`, физ.1–2 даёт опубликованные 25 мг и возможность начала AGO с первого дня постепенного снижения SSRI/SNRI; это не универсальный проверенный календарь пары и не допуск конкретного пациента при неизвестности. Нормы generic mania/suicide/alcohol — физ.4–6. Число 25 не признано ошибочным.

Закрытие: вынести опубликованные компоненты в явно ограниченный source_reference; top-level individual overlap/start permission должен оставаться null/false. Сохранить unknown, physician choice, отсутствие полного календаря и automatic start. [checks.json](checks.json) содержит три точных нарушения этой границы.

## RCR-03 — PHEN form-локатор остался на старой странице

`rules/phen-taper-limit.yaml inputs[form].source_locator` содержит «§1–3 с.1; §4.2 с.3». RU-PHEN SHA `850486408d225fc603f8f053765491c1e9fd688c5c3d765cdf80a34dd2b3cf1a`: форма физ.1, §4.2/постепенность физ.2; физ.3 относится уже к §4.3/4.4. Это отдельный остаточный локатор, исходные 24 исправления материализованы и проверены.

Закрытие: §1–3 физ.1; если способ применения нужен этому reference-полю — §4.2 физ.2. Не возвращать form always ради исправления страницы и не превращать источник-only справку в индивидуальную схему.

## RCR-04 / NR05 — прежние stop outputs наследуют обычный payload

В [legacy_stop_payloads.json](legacy_stop_payloads.json) самостоятельно перечислены **22 из 121** copied source_stop результатов с лишним обычным payload. Примеры: PAR SS-stop — recommended40/обычный interval/hold; FLUV/XR taper stop — minimum-choice taper; XR panic аллергия — source_initial37.5/initial_days7; ESC/PAR→AGO urgent stop — target25/overlap/предлечебный liver monitoring.

Первичные urgent нормы: RU-PAROX физ.7/9; RU-FLUVOX физ.5/7; RU-VENLA-XR физ.9/13; RU-ESC физ.4/6. Они задают свои прекращение/помощь/ECG, а не разрешение будущего обычного режима или нового B. AGO liver followup до нормализации и иные source-specific действия после прекращения сохраняются отдельно от предлечебного календаря.

Закрытие требует удалить обычный future/dose/taper/overlap payload из конкретного stop-result и оставить опубликованные текущие действия/помощь/наблюдение с нужным владельцем и фазой. Для этой проверки не принят авторский live-count23 вместо собственного перечня. Это отдельный открытый NR05, не опровержение чистых новых urgent witnesses и не полная приёмка живого ядра.

Все четыре finding относятся к состоянию копии. Новые live-исправления и их заявленные PASS не считаются закрытием до отдельного freeze/recheck. Более 15 вопросов по V3 допустимо; отсутствие доказательства всех per-result always по NR08 не скрыто.
