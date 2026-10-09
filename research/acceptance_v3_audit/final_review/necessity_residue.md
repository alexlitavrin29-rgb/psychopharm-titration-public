# Конечный предметный остаток№17

Рассмотрены все906 inputs,355always и их текущие result scopes. Источниковая норма, обязательность full numeric result и достаточность bounded refusal/action/reference различались. Полный mathematical minimum не заявлен и не требуется.

- 305 known not_applicable: [exclusion_scope_independent.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/exclusion_scope_independent.json>).
- 135 explicit known source_condition clinician_choice: [choice_scope_candidates.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/choice_scope_candidates.json>).
- 218 known reason-only clinician_choice (173Boolean+45medicines): [choice_reason_scope_residue.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/choice_reason_scope_residue.json>).
- 35 form refusals (29wrongform/release+6XR source arithmetic): [form_scope_residue.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/form_scope_residue.json>).
- Пять source_limit branches качественной AD отмены:17 current-event operands и5 population scopes; точные поля вV3-03.
- selectedPAR→AGO branch-not_selected: no-calendar вывод при известном выборе/дозе; точные prerequisites вV3-04.

693 списочных case exemplars не пересекаются, но это не693 различных медицинских дефекта. Нельзя закрыть остаток количеством source certificates или совпадением готовых expected: нужно проверить собственные cause/actor/phase/source facts, их unknown controls, отсутствие индивидуального дозового payload и реальное потребление/счёт supplied context.

Для305 exclusions сохраняются source-specific compound facts: ALT/AST>3 и phase first-start/ownBnot_started (12 таких случаев); elderly+dementia; age+indication; renal metric/unit/category/value; hepatic category; current medicine INN/status/class; stoppedMAOItype/time/systemclock; own A/B allergy. Для current choice own ongoing либо consumed actual currentdose; contraceptionFalse нуждается в reproductive_populationTrue. Эти сведения нельзя удалить ради короткого пути.

Для всех остальных current numeric/source conditions источниковое обоснование и applicable predicates рассмотрены по906 строкам в [necessity_906_review.json](<C:/Users/Alex/Documents/ChatGPT/титрование/research/acceptance_v3_audit/final_review/necessity_906_review.json>). Дополнительный неперечисленный бесконечный хвост минимальности не предъявляется.
