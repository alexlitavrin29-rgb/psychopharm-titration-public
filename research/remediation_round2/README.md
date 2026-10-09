# Второй проход

Точка входа: summary.md; все30критериев в acceptance_recheck.md. Старые audit/remediation/ACCEPTANCE защищены.

Данные подготовлены последовательными одноразовыми research scripts; build_round2/restore_esc отражают промежуточные этапы и не предназначены для перезапуска поверх финального снимка. Проверять финальный снимок read-only: verify_contracts.py, verify_graphs.py, primary_expected_checks.py; verify_new_negative_checks.py мутирует только in-memory copies. Main verify_research/verify_negative_checks пишут только разрешённые текущие отчёты. Генерация expected не выполнение медицинского калькулятора.

Новый первичный документ требует review, затем точечных обновлений; нельзя запускать прежний source-blocking generator и считать его отсутствие чисел текущей оценкой.
