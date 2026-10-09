"""Inventory of the exact registry records and human-downloaded current originals."""
from pathlib import Path
import hashlib, json
import fitz

O = Path(__file__).resolve().parent
R = O.parent
REGISTRY = 'https://lk.regmed.ru/Register/EAEU_SmPC'
rows = [
    ('RU-AGO', 'Вальдоксан', '000528', '2022-01-25', '2024-12-28', '2024-12-23', '28427', '0018', 'таблетки25мг', '§4.1–4.6 с.1–6; §8–10 с.16', [1,2,3,4,5,6], [1,2,3,4,5,6]),
    ('RU-DULOX', 'Дулоксента', '000186', '2021-04-02', '2026-03-24', '2026-03-20', '5759', '0015', 'капсулы кишечнорастворимые30/60мг', '§4.1–4.3 с.1–4; §4.4 с.4–7; §4.5 с.7–9; §4.6 с.9–10', list(range(1,11))+[22], [1,2,3,4]),
    ('RU-FLUVOX', 'Феварин', '008757', '2025-02-07', '2026-08-19', '2026-08-14', '16133', '0004', 'таблетки50/100мг', '§3 с.1; §4.1–4.3 с.1–3; §4.4–4.6 с.4–10', list(range(1,11)), [1]),
    ('RU-PAROX', 'Рексетин', '008861', '2025-02-14', '2025-02-14', '2025-02-12', '3370', '0003', 'текущая ОХЛП только таблетки20мг; строка реестра20/30мг', '§4.1–4.3 с.1–5; §4.4 с.5–11; §4.5 с.11–14; §4.6 с.14–15', list(range(1,16)), [1,3,4]),
    ('RU-PREG', 'Лирика', '004450', '2024-01-30', '2025-08-13', '2024-01-26', '1319', '0011', 'капсулы25/50/75/100/150/200/300мг', '§4.1–4.2 с.2–5; §4.3–4.4 с.6–11; §4.5–4.6 с.11–13; формула с.4, таблица со сносками с.5', list(range(3,14)), [1,3,4,5]),
    ('RU-PREG-RICHTER', 'Прегабалин-Рихтер', '002412', '2023-05-25', '2026-02-06', '2026-02-02', '1678', '0014', 'капсулы75/150/300мг', '§4.1–4.3 с.1–3; формула/таблица1/сноска с.3; §4.4–4.6 с.3–8', list(range(1,9)), [1,3]),
    ('RU-VENLA-IR', 'Велаксин', '002276', '2023-05-02', '2023-11-21', '2025-12-26', '32413', '0009', 'таблетки37,5/75мг', '§1–4.3 с.1–3; §4.4 с.3–7; §4.5 с.7–11', list(range(1,11)), [1]),
    ('RU-VENLA-XR', 'Велаксин', '002093', '2023-04-03', '2026-06-25', '2026-06-11', '11677', '0019', 'капсулы с пролонгированным высвобождением75/150мг', '§1–3 с.1; §4.1–4.3 с.2–5; §4.4 с.5–13; §4.5 с.13–17; §4.6 с.17–18', list(range(1,18)), [1,4]),
    ('RU-PHEN', 'Феназепам', '005387', '2024-05-07', '2026-05-07', '2026-05-05', '9041', '0004', 'таблетки, диспергируемые в полости рта,0,25/0,5/1мг', '§1–3 с.1; §4.1–4.2 с.1–3; §4.3–4.4 с.3–4; §4.5–4.6 с.4–5', list(range(1,7)), [1,2]),
]
records = []
for sid, product, number, first, registered, expert, report, sequence, form, locator, read, visual in rows:
    original = O / 'originals' / (sid+'_current.pdf')
    leaflet = O / 'originals' / (sid+'_current_PIL.pdf')
    doc = fitz.open(original)
    records.append(dict(source_id=sid, product=product, registration_number=f'ЛП-№({number})-(РГ-RU)',
        registry_url=REGISTRY, query=product, registry_first_registration=first,
        document_registration_stamp=registered, expert_stamp=dict(date=expert, report_number=report, sequence=sequence),
        revision_field_date=None, revision_date_state='No separately stated revision date established; expert/registration stamps recorded separately', publication_date=None, accessed_on='2026-10-08', exact_form=form,
        original_file=original.relative_to(R).as_posix(), original_sha256=hashlib.sha256(original.read_bytes()).hexdigest(), physical_pages=len(doc),
        PIL_file=leaflet.relative_to(R).as_posix(), PIL_sha256=hashlib.sha256(leaflet.read_bytes()).hexdigest(),
        authority_evidence='Exact RU/form row observed in official registry; user downloaded after CAPTCHA request; matching title/form and stamps visually checked',
        captcha_completion_observed_by_agent=False, filename_sequence_not_used_as_stamp=True,
        latest_record_document_obtained=True, current_source_locator=locator,
        actually_read_text_physical_pages=sorted(set(read+[len(doc)]+([2] if sid=='RU-PREG' else [])+([11,12] if sid=='RU-VENLA-IR' else [])+([18,29] if sid=='RU-VENLA-XR' else []))), actually_reviewed_visual_physical_pages=visual,
        visual_stamp_crops=['RU-FLUVOX_current_stamp_page2.png'] if sid=='RU-FLUVOX' else [],
        dependent_contract_recheck_complete=False,
        review_limit='Identity/currency and listed sections only; transfer of every dependent condition and full independent audit still pending'))
out=dict(date='2026-10-08', requested_current_bases=9, obtained=9, acquisition_open=[],
    official_status_not_byte_identity=True, medical_transfer_not_inferred_from_download=True, documents=records)
(O/'current_registry_documents.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('Nine exact registry originals and nine leaflets inventoried; dependent medical transfer remains in review.')
