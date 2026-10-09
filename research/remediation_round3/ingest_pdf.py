"""Archive a human-provided registry PDF; text equality is not clinical review."""
from pathlib import Path
import argparse, difflib, hashlib, json, re, shutil
import fitz

O = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('sid'); p.add_argument('file'); p.add_argument('--old')
p.add_argument('--role', default='SmPC'); p.add_argument('--render', default='1')
a = p.parse_args()
stem = a.sid + '_current' + ('' if a.role == 'SmPC' else '_' + a.role)
dst = O / 'originals' / (stem + '.pdf')
src = Path(a.file)
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
if dst.exists() and sha(dst) != sha(src):
    raise SystemExit('Refusing to replace a different archived original')
if not dst.exists(): shutil.copy2(src, dst)
d = fitz.open(dst)
pages = [page.get_text() for page in d]
(O / 'source_texts' / (stem + '.txt')).write_text(''.join(f'\n=== PHYSICAL PAGE {i+1} ===\n{t}' for i,t in enumerate(pages)), encoding='utf-8')
record = dict(source_id=a.sid, role=a.role, human_file=str(src), archived_file=str(dst), sha256=sha(dst), physical_pages=len(d), access='human download after registry CAPTCHA', clinical_review='pending', first_page_text=pages[0])
if a.old:
    old = Path(a.old); od = fitz.open(old)
    # Normalizing pagination/line wrapping aids review; no medical differences are discarded.
    def tokens(doc): return re.findall(r'\S+', '\n'.join(x.get_text() for x in doc))
    x,y = tokens(od),tokens(d)
    sm = difflib.SequenceMatcher(None,x,y,autojunk=False)
    changes=[]
    for kind,i,j,k,l in sm.get_opcodes():
        if kind != 'equal': changes.append(dict(kind=kind, old=' '.join(x[max(0,i-18):min(len(x),j+18)]), new=' '.join(y[max(0,k-18):min(len(y),l+18)])))
    record.update(previous_file=str(old), previous_sha256=sha(old), byte_identical=sha(old)==sha(dst), previous_pages=len(od), normalized_token_changes=len(changes))
    (O / (stem + '_text_changes.json')).write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
for n in map(int,a.render.split(',')):
    d[n-1].get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(O / f'{stem}_page{n}.png')
(O / (stem + '_provenance.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k!='first_page_text'},ensure_ascii=False))
