"""Freeze content with exact SHA, separate from historical and later audit reports."""
from pathlib import Path
import hashlib,json
O=Path(__file__).resolve().parent;R=O.parent
names=['sources.json','input_contracts.yaml','result_contracts.yaml','full_scenarios.json','necessity_decisions.json','necessity_policy.yaml','question_graphs.yaml','actual_question_paths.json','input_necessity.csv','renal_estimator.yaml','current_registry_documents.json','requirements_diff.json','version_inventory.json','coverage_map.json','verify_contracts.py','verify_v2_negatives.py','verify_graphs.py','verify_new_negative_checks.py','verify_audit_repairs.py','primary_expected_checks.py','primary_current_expected_checks.py','build_graphs.py','ordinary_path_report.json','source_binding_repairs.json','medical_condition_repairs.json','qualitative_necessity_repairs.json','findings_response.json','primary_review_notes.md','README.md','limitations.md']
paths=[O/n for n in names]+sorted((O/'rules').glob('*.yaml'))+sorted((O/'originals').glob('*.pdf'))+[R.parent/'psychopharm_codex_pack/ACCEPTANCE_V2.md',R.parent/'REQUIREMENTS_UPDATE_2026-10-08.md']+[R/n for n in ['sources.json','input_catalog.csv','question_counts.json','question_flows.yaml','switch_matrix.yaml','test_cases.yaml','renal_estimator.yaml','source_transfer_audit.yaml','verify_research.py']]+sorted((R/'rules').glob('*.yaml'))
paths+=[O/n for n in ['verify_recheck_repairs.py','repair_recheck_findings.py','align_current_input_locators.py','recheck_repairs.json','current_input_locator_repairs.json','recheck_primary_read_notes.md']]
paths+=[O/n for n in ['phase_provenance.py','verify_phase_types.py','verify_final_repairs.py','phase_enum_repair.json','phase_semantics_repairs.json','final_necessity_repairs.json','final_source_scope_repairs.json']]
paths+=[R.parent/'psychopharm_codex_pack/ACCEPTANCE_V3.md',R.parent/'REQUIREMENTS_UPDATE_2026-10-09.md']
paths+=[O/n for n in ['requirements_v3_diff.json','bounded_source_actions.py','verify_reported_context.py','verify_condition_repairs.py','verify_scope_repairs.py','necessity_evidence.json','necessity_result_policy.md','current_candidate_metrics.json','caution_necessity_repairs.json','condition_locator_repairs.json','result_scope_repairs.json','reported_context_repairs.json','condition_case_repairs.json','condition_payload_alignment.json','stop_result_payload_repairs.json','maoi_unknown_class_repairs.json','switch_reference_payload_repairs.json','qualitative_result_scope_repairs.json','qualitative_unassessed_structure_repairs.json','bounded_source_action_repairs.json','selected_pair_necessity_repairs.json','reference_guard_repairs.json','legacy_action_cause_repairs.json','form_limit_scope_repairs.json','scope_metadata_repairs.json']]
paths+=[R/'acceptance_v2_audit/condition_completion'/n for n in ['primary_norms.json','scoped_input_conditions.json','positive_expected_gaps_exact.json','early_terminal_candidates.json','necessity_remaining.json','summary.md','coverage.md','findings.md']]
paths+=[O/n for n in ['bounded_source_exclusions.py','bounded_unselected_example.py','verify_result_scopes.py','source_exclusion_scope_repairs.json','taper_reference_scope_repairs.json','unselected_example_scope_repairs.json','source_choice_scope_repairs.json','remaining_terminal_scope_repairs.json','terminal_certificate_alignment.json']]
paths+=[O/'v3_completion_response.md',R/'verify_negative_checks.py']
paths+=[O/'sparse_population_metadata_repairs.json']
paths+=[R/'acceptance_v3_audit/condition_repair_review'/n for n in ['summary.md','findings.md','closure.json','final_verification.json']]
paths+=sorted(R.glob('[0-1][0-9]_*.md'))+[R/'search_log.csv']
for source in json.loads((O/'sources.json').read_text(encoding='utf-8')).values():
    local=source.get('local_file')
    if local and (R/local).is_file():
        paths.append(R/local)
paths=list(dict.fromkeys(paths))
rows=[dict(path=p.relative_to(R.parent).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]
aggregate=hashlib.sha256(json.dumps(rows,sort_keys=True,ensure_ascii=False).encode('utf-8')).hexdigest()
(O/'final_manifest.json').write_text(json.dumps(dict(snapshot_sha256=aggregate,files=rows,main_package_state='round3 promoted; independent acceptance pending',nature='Research data freeze, not git commit or clinical validation'),ensure_ascii=False,indent=2),encoding='utf-8')
print(aggregate,len(rows),'frozen files')
