"""Compare the SmPC portion of combined historical files; retain every text delta."""
from pathlib import Path
import difflib, hashlib, json, re
import fitz

O = Path(__file__).resolve().parent
R = O.parents[1]
old_files = {
    'RU-DULOX': 'Дулоксента — дулоксетин.pdf',
    'RU-FLUVOX': 'Феварин — флувоксамин.pdf',
    'RU-PAROX': 'Рексетин — пароксетин.pdf',
    'RU-PREG-RICHTER': 'Прегабалин-Рихтер — прегабалин.pdf',
}

def smpc_tokens(path):
    doc = fitz.open(path)
    texts = [p.get_text() for p in doc]
    starts = [i for i, t in enumerate(texts) if 'ОБЩАЯ ХАРАКТЕРИСТИКА ЛЕКАРСТВЕННОГО ПРЕПАРАТА' in t]
    assert len(starts) == 1, (path, starts)
    text = '\n'.join(texts[starts[0]:])
    # Bare numeric lines can be clinical values. Remove only explicit pagination labels.
    text = re.sub(r'(?m)^\s*(?:Стр\.?\s*\d+(?:\s*из\s*\d+)?|\d+\s*из\s*\d+)\s*$', '', text)
    return re.findall(r'\S+', text), starts[0] + 1

records = []
for sid, name in old_files.items():
    old = R / 'research' / 'source_downloads' / name
    new = O / 'originals' / (sid + '_current.pdf')
    x, start = smpc_tokens(old)
    y, new_start = smpc_tokens(new)
    deltas = []
    for kind, i, j, k, l in difflib.SequenceMatcher(None, x, y, autojunk=False).get_opcodes():
        if kind != 'equal':
            deltas.append(dict(kind=kind, old=' '.join(x[i:j]), new=' '.join(y[k:l]),
                before=' '.join(y[max(0, k-12):k]), after=' '.join(y[l:l+12]), clinical_review='pending'))
    record = dict(source_id=sid, old_smPC_physical_start=start, new_smPC_physical_start=new_start,
        normalization='Whitespace and explicit Стр/из pagination labels only; bare numbers and hyphenation preserved',
        byte_identical=hashlib.sha256(old.read_bytes()).digest()==hashlib.sha256(new.read_bytes()).digest(),
        deltas=deltas, all_deltas_clinically_reviewed=False)
    (O / (sid + '_smpc_comparison.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    records.append(dict(source_id=sid, deltas=len(deltas), old_start=start))
print(json.dumps(records, ensure_ascii=False))
