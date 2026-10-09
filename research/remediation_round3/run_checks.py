"""Bind preserved checks to round3; scripts write only round3 reports."""
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parent
for name in ['verify_new_negative_checks.py','verify_graphs.py','primary_expected_checks.py']:
    s=(R/'remediation_round2'/name).read_text(encoding='utf-8').replace('remediation_round2','remediation_round3')
    if name=='primary_expected_checks.py':
        s=s.replace("(R/'sources.json')","(O/'sources.json')").replace("page('RU-PAROX',16)","page('RU-PAROX',3)").replace("'RU-PAROX',16,","'RU-PAROX',3,")
    if name=='verify_new_negative_checks.py':
        s=s.replace("d['sources']['RU-AGO']['latest_registration_revision_confirmed']=True","d['sources']['RU-AGO']['latest_registry_document_comparison']=None")
    (O/name).write_text(s,encoding='utf-8')
print('Historical detector and key primary checks adapted without modifying old code/reports.')
