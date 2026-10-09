"""Regression for the A/B phase schema inconsistency found independently."""
from pathlib import Path
from copy import deepcopy
import json,sys

O=Path(__file__).resolve().parent
sys.path.insert(0,str(O))
import verify_contracts

d=verify_contracts.collect();errors=verify_contracts.validate(d);checks=[]
for name in ['unrecognized_A_phase','unknown_A_missing_from_declared_domain']:
 x=deepcopy(d)
 if name=='unrecognized_A_phase':x['cases'][0]['external_context']['treatment_phase']='unrecognized_phase'
 else:x['schema']['external_context']['treatment_phase']['allowed_values'].remove('unknown')
 e=verify_contracts.validate(x);caught=any('phase declaration/value not typed' in s for s in e)
 checks.append(dict(mutation=name,rejected=caught,evidence=[s for s in e if 'phase declaration/value not typed' in s][:2]))
 if not caught:errors.append('Phase typing mutation not rejected: '+name)
r=dict(status='pass' if not errors else 'fail',actual_case_count=len(d['cases']),isolated_mutations=checks,scope='Declared context enum and meaningful phase input consistency; no calculator or clinical validation',errors=errors)
(O/'phase_enum_verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(r,ensure_ascii=False));raise SystemExit(bool(errors))
