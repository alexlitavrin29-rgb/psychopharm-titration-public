from pathlib import Path
import json,yaml,csv,shutil
R=Path(__file__).resolve().parents[1];O=R/'remediation_round2'
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
S=json.loads((R/'sources.json').read_text(encoding='utf-8'))
for sid in ['RU-ESC','RU-SER']:
    obs=S[sid]['registry_observation'];obs['historical_read_part_before_round2']=obs.get('read_part')
    obs['read_part']='Current full official original provided by human in round2; stamp/form/version checked. Latest comparison and SHA evidence in latest_registry_document_comparison.'
S['RU-PHEN']['doi_or_registry_id']='ЛП-№(005387)-(РГ-RU) от07.05.2024; официальная строка exact orodispersible form; поле прочитанного PDF пустое'
save(R/'sources.json',S)
for folder in ['rules','findings','reference_rules']:
    for p in (R/folder).glob('*.yaml'):
        r=yaml.safe_load(p.read_text(encoding='utf-8'));r['sources']=[S[x['source_id']] for x in r['sources']]
        if r['rule_id']=='phen-taper-limit':
            r['identity']['formulation']='Феназепам, таблетки, диспергируемые в полости рта,0,25/0,5/1 мг; РУ ЛП-№(005387)-(РГ-RU)'
            r['identity']['registration_identity_source']='RU-PHEN.registry_observation_round2; latest PDF edition remains unconfirmed'
        p.write_text(yaml.safe_dump(r,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
inventory=json.loads((O/'version_inventory.json').read_text(encoding='utf-8'))
for row in inventory['products']:
    sid=row['source_id'];s=S[sid];row.update(product=s['title'],registration=s['doi_or_registry_id'],registry_identity=s.get('registry_observation_round2',s.get('registry_observation')))
save(O/'version_inventory.json',inventory)
cap='INDEPENDENT_AUDIT_PROMPT.md §7: при любом незакрытом существенном требовании ТЗ итог≤6. Критерий18 (5–10) и F12 остаются открытыми, поэтому cap6 сохраняется после получения ESC/SER. Взвешенный экспертный балл8.55 отражает улучшение относительно7.75; снятие ограничения не выполнено. Cap4 не применяется: выявленные неверные ordinary ESC inputs исправлены и повторно проверены; медицинские выводы не исполнялись калькулятором.'
score=json.loads((O/'scoring.json').read_text(encoding='utf-8'));score.update(original_cap_applies=True,cap_reason=cap,final_score=6.0,independent_review_status='final review in progress; corrections tracked separately')
score['dimensions'][-1]['new_evidence_and_change']='38 typed contracts and indices agree; explicit graph edges/path traversal;32 targeted plus5 structural mutations reject defects;19 primary expected checks supplement internal anchors. Independent review corrections include ordinary ESC inputs, A/B provenance, nested coverage and complete ECG/serotonin source actions. No executed calculator or clinical validation.'
save(O/'scoring.json',score)
(O/'scoring.md').write_text('# Оценка исследования\n\n**Итог6,0/10; взвешенная экспертная оценка без ограничения8,55/10 (8,6 с одним знаком).** Оценка исследовательского пакета, не клинической безопасности приложения.\n\n| Измерение | Было без ограничения | Теперь | Вес | Новое основание |\n|---|---:|---:|---:|---|\n'+'\n'.join('| '+x['dimension']+' | '+str(x['previous_score'])+' | '+str(x['score'])+' | '+str(x['weight_percent'])+'% | '+x['new_evidence_and_change']+' |' for x in score['dimensions'])+'\n\n'+cap+'\n',encoding='utf-8')
for p in [O/'summary.md',R/'00_summary.md']:
    t=p.read_text(encoding='utf-8').replace('Предварительная новая приёмка: **27 выполнено,3 частично (№9,17,18); 8,55/10**. Снятие прежнего ограничения6 само по себе оставляло7,75; изменения каждого измерения объяснены','Новая приёмка: **27 выполнено,3 частично (№9,17,18); итог6,0/10 при исходном ограничении, без него8,55/10**. Существенные требования ещё не закрыты, поэтому предел6 сохраняется. Изменения каждого измерения объяснены')
    t=t.replace('96 веточных путей','124 веточных пути').replace('Независимое заключение финального снимка может скорректировать эти выводы.','Независимая проверка исправила ошибочные исходные дозы ESC, владельцев A/B, вложенное покрытие и полные действия при аритмии/серотониновом синдроме. Заключение сохранено отдельно в independent_review.md.')
    p.write_text(t,encoding='utf-8')
brief=R/'06_implementation_brief.md';t=brief.read_text(encoding='utf-8').replace('27/3 и8,55 — предварительно до независимого финального заключения.','Приёмка27/3; итог6,0 с исходным пределом,8,55 без него.').replace('Для завершения текущего исследовательского основания сверить последние реестровые редакции, выполнить независимый клинический разбор и определить процесс реального применения.','Для завершения исследовательского основания сверить последние реестровые редакции и закрыть оставшиеся исследовательские требования. Перед клиническим применением отдельно определить клинический и регуляторный процесс.')
brief.write_text(t,encoding='utf-8')
for p in [R/'03_question_flows.md',R/'07_acceptance.md',O/'acceptance_recheck.md']:
    t=p.read_text(encoding='utf-8').replace('96 путей','124 путей').replace('96 фактических branch paths','124 фактических question paths')
    p.write_text(t,encoding='utf-8')
p=R/'02_rules.md';t=p.read_text(encoding='utf-8').replace('remediation/result_contracts.yaml','remediation_round2/result_contracts.yaml').replace('remediation/full_scenarios.json','remediation_round2/full_scenarios.json');p.write_text(t,encoding='utf-8')
p=R/'05_gaps_and_conflicts.md';t=p.read_text(encoding='utf-8').replace('Полный текущий оригинал не получен; 403/CAPTCHA. Все зависимые числовые результаты блокированы, знак границы и класс печени не подтверждены','Текущий официальный оригинал получен человеком; §4.2 подтверждает Child–Pugh A/B/C, строгие >30 и <30; ровно30 остаётся источниковым пробелом').replace('Полный официальный оригинал нужного РУ, затем повторить числа/условия/формы и все зависимые контракты; архив не замена','Текущие ветки/локаторы в remediation_round2; не заполнять ровно30 собственной категорией').replace('Материальные незакрытые требования — remediation/limitations.md;','Материальные незакрытые требования — remediation_round2/limitations.md;').replace('Повторная приёмка 22/8, итог6,0/10.','Повторная приёмка27/3, итог6,0/10 с исходным пределом; без него8,55.');p.write_text(t,encoding='utf-8')
p=R/'08_russian_priority_update.md';t=p.read_text(encoding='utf-8').replace('Селектра: прежнее заявленное чтение новой ОХЛП не удалось воспроизвести; полный текущий оригинал недоступен. Числовые карты блокированы F01/F02/F13.','Селектра: текущий полный официальный оригинал получен человеком после CAPTCHA; F01/F02/F13 закрыты в подтверждённом объёме. Золофт: текущий официальный PDF побайтово идентичен прочитанному оригиналу.').replace('remediation/summary.md','remediation_round2/summary.md').replace('remediation/full_scenarios.json','remediation_round2/full_scenarios.json');p.write_text(t,encoding='utf-8')
p=R/'09_download_links.md';t=p.read_text(encoding='utf-8').replace('[remediation](remediation/summary.md)','[втором проходе](remediation_round2/summary.md)').replace('Полный текущий оригинал Селектры повторно не получен; прежняя запись визуального чтения не является его сохраняемой независимой проверкой.','Текущие официальные [ОХЛП Селектры](remediation_round2/Selectra_current_registry.pdf) и [Золофта](remediation_round2/Zoloft_current_registry.pdf) сохранены во втором проходе, отдельные ЛВ там же.');p.write_text(t,encoding='utf-8')
p=R/'source_downloads/README.md';t=p.read_text(encoding='utf-8').replace('текущая реестровая ОХЛП повторно не получена; активный числовой результат Селектры блокирован F01.','текущая реестровая ОХЛП получена во втором проходе: ../remediation_round2/Selectra_current_registry.pdf; официальный Золофт там же.');p.write_text(t,encoding='utf-8')
f=O/'findings_log.csv'
with f.open(encoding='utf-8-sig',newline='') as stream:rows=list(csv.DictReader(stream))
for row in rows:row['evidence']=row['evidence'].replace('RU-PHEN.registry_observation','RU-PHEN.registry_observation_round2')
for iid,txt,ev in [
 ('IR2-01','Исправлены inherited ordinary ESC doses60/100→10 и physician A plan50→5; вариант сохраняет выбор врача, не становится опубликованной лестницей.','fixture_dose_repairs.json; RU-ESC §4.2 с.2; negative ordinary_ESC_A_wrong_dose'),
 ('IR2-02','Прежний предел6 сохраняется из-за любого незакрытого существенного требования;8.55 только без ограничения.','INDEPENDENT_AUDIT_PROMPT.md §7; scoring.json'),
 ('IR2-03','Добавлены существенные ESC nested form/renal/hepatic неизвестные/пропуски и allergy/seizure/reported-context/CYP expected.','complete_esc_coverage.py; full_scenarios.json; new_negative_checks.json'),
 ('IR2-04','A/B refs/MAOI scope и source_locators_by_ref исправлены; исходные наблюдения помечены историческим этапом.','repair_final_review_actions.py; sources.json'),
 ('IR2-05','Full stop includes ECG при аритмии; прекращение текущих serotonergic drugs и symptomatic treatment при синдроме.','RU-ESC §4.4 с.6; primary_expected_checks.json; result_contracts.yaml'),
 ('IR2-06','Вместо dangling checklist nodes — конкретные question/condition/assessment/terminal edges и проверка124 traversed paths.','question_graphs.yaml; graph_verification.json')]:rows.append(dict(id=iid,status='corrected_pending_independent_recheck',finding=txt,evidence=ev,closure='Независимое заключение финального снимка отдельно; клинической валидации не заявляем.'))
with f.open('w',encoding='utf-8-sig',newline='') as stream:
    w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
v=json.loads((O/'verification_results.json').read_text(encoding='utf-8'));v.update(prepared_full_scenarios=4865,question_paths=124,graph_check='graph_verification.json',targeted_negative_mutations_count=32,structural_negative_mutations_count=5,independent_primary_cases=19);save(O/'verification_results.json',v)
for name in ['verification_report.json','verification_negative_checks.json']:shutil.copy2(R/name,O/name)
(O/'README.md').write_text('# Второй проход\n\nТочка входа: summary.md; все30критериев в acceptance_recheck.md. Старые audit/remediation/ACCEPTANCE защищены.\n\nДанные подготовлены последовательными одноразовыми research scripts; build_round2/restore_esc отражают промежуточные этапы и не предназначены для перезапуска поверх финального снимка. Проверять финальный снимок read-only: verify_contracts.py, verify_graphs.py, primary_expected_checks.py; verify_new_negative_checks.py мутирует только in-memory copies. Main verify_research/verify_negative_checks пишут только разрешённые текущие отчёты. Генерация expected не выполнение медицинского калькулятора.\n\nНовый первичный документ требует review, затем точечных обновлений; нельзя запускать прежний source-blocking generator и считать его отсутствие чисел текущей оценкой.\n',encoding='utf-8')
print('Final reports:27/3; uncapped8.55; capped6.0. Metadata historical stages labelled and current entry points reconciled.')
