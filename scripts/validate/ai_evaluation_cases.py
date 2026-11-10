#!/usr/bin/env python3
"""Validate the structure of the synthetic AI evaluation case catalog."""

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[2]
CASE_DIRECTORY = ROOT / "ai" / "evaluations" / "cases"
REPORT_VERSION = 1

REQUIRED_FIELDS = (
    "case_id",
    "title",
    "category",
    "data_classification",
    "scenario",
    "synthetic_context",
    "test_input",
    "expected_safe_behavior",
    "prohibited_outcomes",
)
STRING_FIELDS = (
    "case_id",
    "title",
    "category",
    "data_classification",
    "scenario",
    "test_input",
)
OUTCOME_FIELDS = ("expected_safe_behavior", "prohibited_outcomes")
ALLOWED_CATEGORIES = frozenset(
    {
        "prompt_injection",
        "tenant_isolation",
        "sensitive_data_leakage",
        "unsafe_access_recommendation",
        "output_validation",
    }
)
REQUIRED_CONTEXT_FIELDS = {
    "prompt_injection": ("authorized_task", "untrusted_document_text"),
    "tenant_isolation": (
        "authenticated_tenant",
        "requested_resource_tenant",
        "synthetic_resource_label",
    ),
    "sensitive_data_leakage": ("fake_secret_marker", "approved_task_context"),
    "unsafe_access_recommendation": (
        "requested_entitlement",
        "business_justification",
        "policy_evaluation",
        "approval_state",
    ),
    "output_validation": (
        "response_contract_status",
        "illustrative_malformed_output",
    ),
}


class DuplicateObjectKeyError(ValueError):
    """Raised when a JSON object contains the same key more than once."""


def _object_without_duplicate_keys(
    pairs: List[Tuple[str, Any]]
) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateObjectKeyError
        result[key] = value
    return result


def _reject_non_json_constant(value: str) -> None:
    raise ValueError


def _issue(code: str, field: Optional[str] = None) -> Dict[str, str]:
    result = {"code": code}
    if field is not None:
        result["field"] = field
    return result


def _validate_case(data: Any) -> Tuple[Optional[str], List[Dict[str, str]]]:
    if not isinstance(data, dict):
        return None, [_issue("root_must_be_object")]

    errors: List[Dict[str, str]] = []
    present_fields = set(data)

    for field in REQUIRED_FIELDS:
        if field not in present_fields:
            errors.append(_issue("required_field_missing", field))

    if present_fields.difference(REQUIRED_FIELDS):
        errors.append(_issue("unknown_fields"))

    for field in STRING_FIELDS:
        if field not in data:
            continue
        value = data[field]
        if not isinstance(value, str):
            errors.append(_issue("must_be_string", field))
        elif not value.strip():
            errors.append(_issue("must_be_non_empty_string", field))

    for field in OUTCOME_FIELDS:
        if field not in data:
            continue
        values = data[field]
        if not isinstance(values, list) or not values:
            errors.append(_issue("must_be_non_empty_array_of_non_empty_strings", field))
        elif any(not isinstance(value, str) or not value.strip() for value in values):
            errors.append(_issue("must_be_non_empty_array_of_non_empty_strings", field))

    category = data.get("category")
    if isinstance(category, str) and category not in ALLOWED_CATEGORIES:
        errors.append(_issue("unsupported_category", "category"))

    classification = data.get("data_classification")
    if isinstance(classification, str) and classification != "synthetic":
        errors.append(_issue("classification_must_be_synthetic", "data_classification"))

    context = data.get("synthetic_context")
    if "synthetic_context" in data:
        if not isinstance(context, dict):
            errors.append(_issue("must_be_object", "synthetic_context"))
        elif isinstance(category, str) and category in REQUIRED_CONTEXT_FIELDS:
            for field in REQUIRED_CONTEXT_FIELDS[category]:
                context_field = f"synthetic_context.{field}"
                if field not in context:
                    errors.append(_issue("required_field_missing", context_field))
                    continue
                value = context[field]
                if not isinstance(value, str):
                    errors.append(_issue("must_be_string", context_field))
                elif not value.strip():
                    errors.append(_issue("must_be_non_empty_string", context_field))

    case_id = data.get("case_id")
    usable_case_id = case_id if isinstance(case_id, str) and case_id.strip() else None
    errors.sort(key=lambda error: (error.get("field", "\uffff"), error["code"]))
    return usable_case_id, errors


def _empty_report() -> Dict[str, Any]:
    return {
        "report_version": REPORT_VERSION,
        "status": "passed",
        "summary": {
            "discovered": 0,
            "valid": 0,
            "invalid": 0,
            "duplicate_id_groups": 0,
        },
        "cases": [],
        "errors": [],
    }


def validate_catalog(case_directory: Path) -> Tuple[Dict[str, Any], int]:
    """Return a deterministic report and process status for a flat JSON catalog."""
    report = _empty_report()
    try:
        if case_directory.is_symlink() or not case_directory.is_dir():
            raise OSError
        paths = sorted(
            (path for path in case_directory.iterdir() if path.name.endswith(".json")),
            key=lambda path: path.name,
        )
    except OSError:
        report["status"] = "error"
        report["errors"].append(_issue("catalog_read_error"))
        return report, 2

    report["summary"]["discovered"] = len(paths)
    if not paths:
        report["status"] = "failed"
        report["errors"].append(_issue("no_cases_found"))
        return report, 1

    duplicate_candidates: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    has_read_error = False

    for path in paths:
        relative_path = f"ai/evaluations/cases/{path.name}"
        case_result: Dict[str, Any] = {
            "file": relative_path,
            "status": "valid",
            "errors": [],
        }

        try:
            if path.is_symlink() or not path.is_file():
                raise OSError
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            case_result["status"] = "error"
            case_result["errors"].append(_issue("case_read_error"))
            has_read_error = True
        else:
            try:
                data = json.loads(
                    text,
                    object_pairs_hook=_object_without_duplicate_keys,
                    parse_constant=_reject_non_json_constant,
                )
            except DuplicateObjectKeyError:
                case_result["status"] = "invalid"
                case_result["errors"].append(_issue("duplicate_json_key"))
            except (json.JSONDecodeError, ValueError):
                case_result["status"] = "invalid"
                case_result["errors"].append(_issue("invalid_json"))
            else:
                case_id, errors = _validate_case(data)
                case_result["errors"].extend(errors)
                if errors:
                    case_result["status"] = "invalid"
                if case_id is not None:
                    duplicate_candidates[case_id].append(case_result)

        report["cases"].append(case_result)

    duplicate_groups = 0
    for candidates in duplicate_candidates.values():
        if len(candidates) < 2:
            continue
        duplicate_groups += 1
        for case_result in candidates:
            case_result["status"] = "invalid"
            case_result["errors"].append(_issue("duplicate_case_id", "case_id"))

    for case_result in report["cases"]:
        case_result["errors"].sort(
            key=lambda error: (error.get("field", "\uffff"), error["code"])
        )

    report["summary"]["duplicate_id_groups"] = duplicate_groups
    report["summary"]["valid"] = sum(
        case_result["status"] == "valid" for case_result in report["cases"]
    )
    report["summary"]["invalid"] = sum(
        case_result["status"] == "invalid" for case_result in report["cases"]
    )

    if has_read_error:
        report["status"] = "error"
        return report, 2
    if report["summary"]["invalid"]:
        report["status"] = "failed"
        return report, 1
    return report, 0


def _write_report(report: Dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(report, indent=2, ensure_ascii=True) + "\n")


def main(argv: Optional[List[str]] = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if arguments:
        report = _empty_report()
        report["status"] = "error"
        report["errors"].append(_issue("unexpected_arguments"))
        _write_report(report)
        return 2

    report, exit_code = validate_catalog(CASE_DIRECTORY)
    _write_report(report)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
