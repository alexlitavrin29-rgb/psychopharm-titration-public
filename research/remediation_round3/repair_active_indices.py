"""Correct current Markdown medical pointers; retain their previous versions."""
from pathlib import Path
import shutil

O = Path(__file__).resolve().parent
R = O.parent
back = O / 'previous_main_documents'
for name in ['02_rules.md', '04_switch_matrix.md', '08_russian_priority_update.md']:
    if not (back / name).exists():
        shutil.copyfile(R / name, back / name)
    text = (R / name).read_text(encoding='utf-8-sig')
    text = text.replace('§ 4.2 с. 16–17', '§ 4.2 с. 3–4')
    text = text.replace('конкретные ограничения/пробелы в round2', 'текущие контракты и ограничения в remediation_round3')
    text = text.replace('новая RU-PREG-RICHTER с.16', 'текущая RU-PREG-RICHTER §4.2 с.3')
    if name == '02_rules.md':
        text = text.replace('Эсциталопрам: текущий полный официальный оригинал RU-ESC недоступен. Все восемь карточек и зависимые переходы source_unavailable; почечный знак и печёночная классификация не выбраны по архиву. Числа прежнего извлечения не разрешены к индивидуальному переносу. F01/F02/F13 открыты.',
            'Эсциталопрам: текущий официальный оригинал Селектры получен. Восемь карточек и зависимые переходы связаны с ним: строгий возраст >65, почечные >30/<30 с отдельным пробелом ровно30, печёночные классы A/B/C, формы и условия прекращения. Текущие контракты — remediation_round3; наличие источника не заменяет независимую проверку каждого конечного действия.')
    if name == '08_russian_priority_update.md':
        text = text.replace('Рихтер: текущая ссылка производителя содержит формулу мкмоль/л с 1,23, визуально сверена с. 16; старая мг/дл сохранена в отдельном источнике/формуле.',
            'Рихтер: полученная текущая официальная ОХЛП содержит формулу мкмоль/л с 1,23, таблицу и сноски на физической с.3. Предыдущая копия производителя имела их на с.16; старая мг/дл сохранена в отдельном источнике/формуле.')
        text = text.replace('Изменений критериев ACCEPTANCE.md, новых клинических коэффициентов и разработки приложения не было.',
            'Исходный ACCEPTANCE.md сохранён. Пользователь уточнил только №18 отдельной версией ACCEPTANCE_V2: цель5–10, обычный путь до15 включительно. Новых клинических коэффициентов и разработки приложения не было.')
        text = text.replace('общая база — 38 карточек, 124 ожиданий.', 'общая база — 38 карточек; 124 прежних ожидания сохранены как фрагменты, полные synthetic expected находятся отдельно в третьем проходе.')
    (R / name).write_text(text, encoding='utf-8')
print('Active source indices corrected; historical copies retained.')
