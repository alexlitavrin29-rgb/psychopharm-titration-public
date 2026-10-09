# Проверенный объём и пределы

Просмотрены38 активных карточек, их clinical_parameters, inputs и branches;211 вхождений параметров свёрнуты в104 разных source/parameter/value/unit сочетания и сопоставлены с реально прочитанными дозовыми разделами. Не заявлена исчерпывающая первичная рецензия каждого клинического условия/взаимодействия всех38 карточек. Обнаруженные медицинские пропуски показывают, почему такую рецензию нельзя заменить внутренними anchors.

Все4953 cases прошли самостоятельно повторённую структурную проверку; конфликтующих целых given/context/expected внутри одного rule не найдено.14 собственных первичных assertions прошли.255 графовых traces пересчитаны самостоятельно;97 проекций имеют неподтверждённые negatives.40 авторских целевых мутаций повторены изолированно;12 собственных проверок мутаций/границ —PASS. Некоторые собственные проверки — технические свойства типов/предикатов, а не медицинский evaluator.

Не завершено: содержательное доказательство неудалимости каждого поля по каждому результату, все уникальные лекарственные взаимодействия/стоп-факты, независимое наблюдение каждой реестровой строки и полное чтение всех PIL. Ни один из этих пробелов не объявлен проверенным; конкретные находки остаются открыты. Клиническая валидация не проводилась и не требовалась для исследовательского балла.

- ago-depression-start: 8 параметров; usual, liver_caution, renal_caution, repeat_tests.
- ago-gad-start: 8 параметров; usual, liver_caution, renal_caution, repeat_tests.
- ago-stop: 0 параметров; chosen_stop.
- dulox-depression-start: 2 параметров; usual.
- dulox-gad-adjust: 3 параметров; at30, at60, other.
- dulox-gad-start: 5 параметров; usual, comorbid, elderly, overlap.
- dulox-taper-limit: 2 параметров; source_limit, withdrawal.
- esc-adult-adjust: 5 параметров; response_decision.
- esc-cyp2c19-start: 7 параметров; special.
- esc-elderly-start: 7 параметров; elderly.
- esc-gad-start: 7 параметров; usual.
- esc-hepatic-start: 7 параметров; special.
- esc-panic-start: 9 параметров; usual.
- esc-social-start: 7 параметров; usual.
- esc-taper-limit: 4 параметров; source_limit.
- fluvox-depression-start: 7 параметров; selected50, selected100, choice.
- fluvox-taper-limit: 1 параметров; source_limit, withdrawal.
- parox-panic-kr: 10 параметров; usual, elderly, organ_caution.
- parox-taper-example: 4 параметров; selected40, other.
- phen-taper-limit: 0 параметров; source_limit, withdrawal.
- preg-gad-adjust: 9 параметров; from150-frequency2, from300-frequency2, from450-frequency2, from150-frequency3, from300-frequency3, from450-frequency3, other.
- preg-gad-start: 9 параметров; frequency2, frequency3.
- preg-renal-start: 14 параметров; ge60, 30_60, 15_30, lt15.
- preg-taper-limit: 3 параметров; source_limit, withdrawal.
- ser-adult-adjust: 7 параметров; increase, keep, increase-from50, increase-from150, keep50, keep150, keep200, initial25, other-source-dose, ceiling, early, decrease, clinical_option.
- ser-panic-start: 7 параметров; usual.
- ser-social-start: 7 параметров; usual.
- ser-taper-limit: 3 параметров; source_limit, withdrawal.
- switch-esc-ago: 7 параметров; class_overlap.
- switch-esc-ser: 1 параметров; pair_gap.
- switch-parox-ago-selected-example: 11 параметров; selected40, withdrawal_hold, not_selected.
- switch-parox-ago: 7 параметров; source_class_overlap.
- switch-ser-ago: 7 параметров; source_class_overlap.
- switch-ser-esc: 1 параметров; pair_gap.
- venla-xr-gad-start: 5 параметров; usual, renal_reduction, hepatic_reduction, joint_modifiers.
- venla-xr-panic-form-limit: 4 параметров; form_limit.
- venla-xr-social-start: 5 параметров; usual, renal_reduction, hepatic_reduction, joint_modifiers.
- venla-xr-taper-limit: 1 параметров; source_limit, withdrawal.
