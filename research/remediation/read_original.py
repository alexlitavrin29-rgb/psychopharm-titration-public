from pathlib import Path
import sys, fitz
R=Path(__file__).resolve().parents[1]
sid=sys.argv[1]
p=R/'audit/retrieved'/f'{sid}.pdf'
if not p.exists(): raise SystemExit(p)
d=fitz.open(p)
for item in sys.argv[2:]:
    for n in range(int(item.split('-')[0]),int(item.split('-')[-1])+1):
        print(f'PAGE {n}:\n{d[n-1].get_text()}')
