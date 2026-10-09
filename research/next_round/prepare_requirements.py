import hashlib
import json
import re
from collections import Counter
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
PACK=ROOT/'psychopharm_codex_pack'
ROUND=ROOT/'research/remediation_round2'
original=(PACK/'ACCEPTANCE.md').read_text(encoding='utf-8')
old='Обычный путь действительно укладывается в 5–10 содержательных вопросов; нагрузка не спрятана в подпунктах.'
new=('Для обычного индивидуального дозового расчёта 5–10 содержательных вопросов — целевой диапазон; '
     'допустимо до 15 включительно при обоснованной необходимости каждого вопроса. '
     'Начальные выборы и независимые сведения считаются отдельно; нагрузка не скрыта в подпунктах '
     'или предварительной анкете, необходимые ограничения не удалены ради лимита.')
assert original.count(old)==1
body=original.replace(old,new)
body=body.replace('# Проверка результата поиска и подготовки правил',
                  '# Проверка результата поиска и подготовки правил — версия 2',1)
notice=('\nВерсия 2 от 08.10.2026 основана на прямом уточнении пользователя. Изменён только критерий №18: '
        '5–10 — цель, до 15 включительно допустимо для обычного расчёта. Подробности — '
        '`../REQUIREMENTS_UPDATE_2026-10-08.md`. Остальные 29 критериев и граница исследовательского этапа сохранены. '
        'Исходный ACCEPTANCE.md и старые аудиты остаются историческими; новая приёмка не исправляет их задним числом.\n')
first,rest=body.split('\n',1)
body=first+'\n'+notice+'\n'+rest
(PACK/'ACCEPTANCE_V2.md').write_text(body,encoding='utf-8')
criteria_old=re.findall(r'^- \[ \] (.+)$',original,re.M)[:30]
criteria_new=re.findall(r'^- \[ \] (.+)$',body,re.M)[:30]
differences=[i+1 for i,(a,b) in enumerate(zip(criteria_old,criteria_new)) if a!=b]
assert len(criteria_old)==len(criteria_new)==30 and differences==[18]

acceptance=json.loads((ROUND/'acceptance_recheck.json').read_text(encoding='utf-8'))
status=Counter(c['status'] for c in acceptance['criteria'])
paths=json.loads((ROUND/'actual_question_paths.json').read_text(encoding='utf-8'))
usual=[x for x in paths if x['path_label']=='usual']
protected=json.loads((ROUND/'preservation_check.json').read_text(encoding='utf-8'))
changes=[]
for entry in protected['protected']:
    p=ROOT/entry['path']
    actual=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
    if actual!=entry['sha256_before']: changes.append(entry['path'])
assert not changes,changes

expected_hashes={
 'result_contracts.yaml':'38e4ee5e528f3908ccd4b7ca8852966712f95f63d1b1766577c8ce24217b1b63',
 'input_contracts.yaml':'0979f7ca0346a4990039772532511cc22825520c5da8f50db20524cd3dba859d',
 'full_scenarios.json':'e1e47edde753edbd5544af9570847ec439b47792073e3f7abbef2adcced8e33b',
 'question_graphs.yaml':'0f69a142f67ffe5810ae85fa642bc5dc3d0c4d0f37b2a7641d46539d947e5a3e',
 'actual_question_paths.json':'43c0d18268d6c1bddfa76804a368bcab1bd283ad500de7d8b846f059ba98b2c0'}
hash_checks={name:hashlib.sha256((ROUND/name).read_bytes()).hexdigest()==value for name,value in expected_hashes.items()}
assert all(hash_checks.values())
raw_score=8*.25+9*.30+8*.20+9*.15+9*.10
assert abs(raw_score-8.55)<1e-9
proof=dict(date='2026-10-08',review_scope='Targeted read-only review; no repeated complete medical audit or script execution',
           previous_acceptance_counts=dict(status),original_criteria_count=30,v2_criteria_count=30,changed_criteria= differences,
           protected_files_rechecked=len(protected['protected']),protected_files_changed=changes,
           snapshot_hashes_match_review=hash_checks,reported_weighted_score_arithmetic=raw_score,
           full_expected_count=len(json.loads((ROUND/'full_scenarios.json').read_text(encoding='utf-8'))['cases']),
           path_count=len(paths),all_path_buckets=dict(Counter('<=10' if p['count']<=10 else '11-15' if p['count']<=15 else '>15' for p in paths)),
           usual_paths=[dict(rule_id=p['rule_id'],count=p['count'],result_type=p['result_type']) for p in usual],
           original_acceptance_sha256=hashlib.sha256((PACK/'ACCEPTANCE.md').read_bytes()).hexdigest(),
           v2_acceptance_sha256=hashlib.sha256((PACK/'ACCEPTANCE_V2.md').read_bytes()).hexdigest())
(OUT/'review_checks.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')

report='''# Оценка второго прохода и новое ТЗ

Проверка от 08.10.2026: прочитаны итог, ограничения, приёмка, оценка, независимое заключение, инвентарь версий и фактические пути. Это целевой разбор результата, не новый полный медицинский аудит.

Подтверждены арифметика заявленной оценки 8,55, счёт 27 выполнено / 3 частично, 4897 подготовленных полных ожиданий и 124 пути. SHA пяти основных артефактов совпадают со снимком независимого заключения. Собственная повторная проверка 342 защищённых файлов не обнаружила изменений. Авторские проверяющие скрипты в этом проходе не запускались; прежние PASS прочитаны, а не объявлены собственными повторными запусками.

Исправления существенно продвинули исследование. Получение официальных ESC/SER сняло прежний ключевой документальный блокер. Но оставшиеся девять редакций активных оснований и неполная доказанная минимальность входов сохраняют существенные ограничения. Значения пяти оценок являются экспертной оценкой автора второго прохода; арифметическая проверка не является независимым подтверждением всего медицинского содержания. Пока нет основания автоматически снимать предел 6 или объявлять 10/10.

Пользователь теперь изменил ТЗ: 5–10 вопросов — цель, до 15 включительно допустимо. Созданы отдельное уточнение и ACCEPTANCE_V2; первоначальный документ и предыдущие оценки сохранены. Изменён ровно №18, остальные 29 текстов критериев совпадают. Это новое требование, не завышение прежней приёмки.

Однако AGO=12 в question_limit_conflict — нижняя граница, не законченная длина обычного пути. В actual_question_paths обычный AGO сейчас содержит 28 сведений. Новый предел не превращает №18 автоматически в выполненный. Нужно завершить №17 и пересобрать обычные пути по источникам.

| Обычная ветка | Текущий счёт независимых сведений/выборов |
|---|---:|
'''
for p in usual: report+=f"| {p['rule_id']} | {p['count']} |\n"
report+='''
Из всех 124 путей 15 укладываются в 10, ещё 19 — в 11–15, 90 превышают 15. Это совокупность обычных и специальных путей; 90 не объявлены автоматически нарушениями обычного лимита. Обычная классификация и реальные условные триггеры должны проверяться отдельно.

Дополнительное замечание синхронизации: в limitations приведён номер Лирики (004450), но registration у RU-PREG в version_inventory.json равен null. Это не доказательство отсутствия регистрации; точный номер и источник его подтверждения нужно согласовать между индексами.

Следующий проход должен закрыть №9, закончить результат-специфическую необходимость каждого вопроса для №17 и доказать обычные пути по новому №18. Медицинские условия нельзя удалять ради счётчика; наблюдение и данные другого режима нельзя делать обязательными без основания. Снятие ограничения с прежних 8,55 даст 8,6, а не автоматически 10: итог требует отдельной независимой оценки всех пяти измерений.

Промпты подготовлены отдельно: PROMPT_IMPROVEMENT.md — исполнитель, PROMPT_INDEPENDENT_ACCEPTANCE.md — независимая приёмка. Сначала выполнить первый, затем передать зафиксированный итоговый снимок проверяющему. Источниковые ограничения, отсутствие реализации и клинической валидации сохраняются честно.
'''
(OUT/'assessment.md').write_text(report,encoding='utf-8')
print(json.dumps({k:proof[k] for k in ['changed_criteria','protected_files_rechecked','protected_files_changed','previous_acceptance_counts','all_path_buckets']},ensure_ascii=False,indent=2))
