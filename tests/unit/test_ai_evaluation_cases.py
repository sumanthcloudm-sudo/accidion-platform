import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, Tuple

from scripts.validate import ai_evaluation_cases


def valid_case(case_id: str = "AI-EVAL-TEST") -> Dict[str, Any]:
    return {
        "case_id": case_id,
        "title": "Synthetic test case",
        "category": "prompt_injection",
        "data_classification": "synthetic",
        "scenario": "A synthetic scenario.",
        "synthetic_context": {
            "authorized_task": "A synthetic authorized task.",
            "untrusted_document_text": "Synthetic untrusted document content.",
        },
        "test_input": "A synthetic test input.",
        "expected_safe_behavior": ["Expected synthetic behavior."],
        "prohibited_outcomes": ["Prohibited synthetic outcome."],
    }


class EvaluationCaseValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.case_directory = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_case(self, filename: str, data: Any) -> None:
        (self.case_directory / filename).write_text(
            json.dumps(data), encoding="utf-8"
        )

    def validate(self) -> Tuple[Dict[str, Any], int]:
        return ai_evaluation_cases.validate_catalog(self.case_directory)

    def test_checked_in_catalog_passes(self) -> None:
        report, exit_code = self.validate_checked_in_catalog()

        self.assertEqual(exit_code, 0)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["summary"]["discovered"], 5)
        self.assertEqual(report["summary"]["valid"], 5)
        self.assertEqual(report["summary"]["invalid"], 0)
        self.assertEqual(
            [case["file"] for case in report["cases"]],
            sorted(case["file"] for case in report["cases"]),
        )

    def validate_checked_in_catalog(self) -> Tuple[Dict[str, Any], int]:
        return ai_evaluation_cases.validate_catalog(
            ai_evaluation_cases.CASE_DIRECTORY
        )

    def test_malformed_json_is_validation_failure_without_echoing_input(self) -> None:
        (self.case_directory / "bad.json").write_text(
            '{"secret-like-value": ', encoding="utf-8"
        )

        report, exit_code = self.validate()

        self.assertEqual(exit_code, 1)
        self.assertEqual(report["cases"][0]["errors"], [{"code": "invalid_json"}])
        self.assertNotIn("secret-like-value", json.dumps(report))
        self.assertNotIn(str(self.case_directory), json.dumps(report))

    def test_non_object_root_is_invalid(self) -> None:
        (self.case_directory / "root.json").write_text("[]", encoding="utf-8")

        report, exit_code = self.validate()

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            report["cases"][0]["errors"], [{"code": "root_must_be_object"}]
        )

    def test_missing_fields_and_wrong_types_are_invalid(self) -> None:
        case = valid_case()
        del case["title"]
        case["scenario"] = 42

        self.write_case("invalid.json", case)
        report, exit_code = self.validate()

        self.assertEqual(exit_code, 1)
        self.assertEqual(report["summary"]["invalid"], 1)
        errors = report["cases"][0]["errors"]
        self.assertIn(
            {"code": "required_field_missing", "field": "title"}, errors
        )
        self.assertIn({"code": "must_be_string", "field": "scenario"}, errors)

    def test_synthetic_context_requires_category_fields(self) -> None:
        case = valid_case()
        del case["synthetic_context"]["authorized_task"]
        self.write_case("missing-context.json", case)

        report, exit_code = self.validate()

        self.assertEqual(exit_code, 1)
        self.assertIn(
            {
                "code": "required_field_missing",
                "field": "synthetic_context.authorized_task",
            },
            report["cases"][0]["errors"],
        )

    def test_each_checked_in_category_requires_its_fixture_context_fields(self) -> None:
        catalog = ai_evaluation_cases.CASE_DIRECTORY
        covered_categories = set()

        for path in sorted(catalog.glob("*.json"), key=lambda item: item.name):
            case = json.loads(path.read_text(encoding="utf-8"))
            category = case["category"]
            covered_categories.add(category)

            for field in ai_evaluation_cases.REQUIRED_CONTEXT_FIELDS[category]:
                with self.subTest(category=category, field=field):
                    mutated_case = dict(case)
                    mutated_context = dict(case["synthetic_context"])
                    del mutated_context[field]
                    mutated_case["synthetic_context"] = mutated_context
                    for existing_path in self.case_directory.glob("*.json"):
                        existing_path.unlink()
                    self.write_case(path.name, mutated_case)

                    report, exit_code = self.validate()

                    self.assertEqual(exit_code, 1)
                    self.assertIn(
                        {
                            "code": "required_field_missing",
                            "field": f"synthetic_context.{field}",
                        },
                        report["cases"][0]["errors"],
                    )

        self.assertEqual(covered_categories, ai_evaluation_cases.ALLOWED_CATEGORIES)

    def test_synthetic_context_must_be_an_object(self) -> None:
        case = valid_case()
        case["synthetic_context"] = []
        self.write_case("non-object-context.json", case)

        report, exit_code = self.validate()

        self.assertEqual(exit_code, 1)
        self.assertIn(
            {"code": "must_be_object", "field": "synthetic_context"},
            report["cases"][0]["errors"],
        )

    def test_synthetic_context_rejects_incorrect_value_type(self) -> None:
        case = valid_case()
        case["synthetic_context"]["authorized_task"] = ["unexpected", "array"]
        self.write_case("wrong-context-type.json", case)

        report, exit_code = self.validate()

        self.assertEqual(exit_code, 1)
        self.assertIn(
            {
                "code": "must_be_string",
                "field": "synthetic_context.authorized_task",
            },
            report["cases"][0]["errors"],
        )

    def test_synthetic_context_rejects_empty_required_value(self) -> None:
        case = valid_case()
        case["synthetic_context"]["authorized_task"] = "  "
        self.write_case("empty-context-value.json", case)

        report, exit_code = self.validate()

        self.assertEqual(exit_code, 1)
        self.assertIn(
            {
                "code": "must_be_non_empty_string",
                "field": "synthetic_context.authorized_task",
            },
            report["cases"][0]["errors"],
        )

    def test_unconfirmed_additional_context_fields_are_allowed(self) -> None:
        case = valid_case()
        case["synthetic_context"]["future_fixture_metadata"] = {
            "label": "synthetic-only"
        }
        self.write_case("additional-context.json", case)

        report, exit_code = self.validate()

        self.assertEqual(exit_code, 0)
        self.assertEqual(report["cases"][0]["status"], "valid")
        self.assertNotIn("synthetic-only", json.dumps(report))

    def test_empty_required_string_and_unknown_field_are_invalid(self) -> None:
        case = valid_case()
        case["title"] = "  "
        case["unreviewed_extra"] = "fixture content"
        self.write_case("shape.json", case)

        report, exit_code = self.validate()

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            report["cases"][0]["errors"],
            [
                {"code": "must_be_non_empty_string", "field": "title"},
                {"code": "unknown_fields"},
            ],
        )
        self.assertNotIn("fixture content", json.dumps(report))

    def test_outcome_arrays_must_contain_non_empty_strings(self) -> None:
        case = valid_case()
        case["expected_safe_behavior"] = ["valid", "  "]
        case["prohibited_outcomes"] = []
        self.write_case("outcomes.json", case)

        report, exit_code = self.validate()

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            report["cases"][0]["errors"],
            [
                {
                    "code": "must_be_non_empty_array_of_non_empty_strings",
                    "field": "expected_safe_behavior",
                },
                {
                    "code": "must_be_non_empty_array_of_non_empty_strings",
                    "field": "prohibited_outcomes",
                },
            ],
        )

    def test_unknown_category_and_non_synthetic_classification_fail(self) -> None:
        case = valid_case()
        case["category"] = "unregistered"
        case["data_classification"] = "internal"
        self.write_case("unsupported.json", case)

        report, exit_code = self.validate()

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            report["cases"][0]["errors"],
            [
                {"code": "unsupported_category", "field": "category"},
                {
                    "code": "classification_must_be_synthetic",
                    "field": "data_classification",
                },
            ],
        )

    def test_duplicate_ids_mark_every_conflicting_case_invalid(self) -> None:
        self.write_case("one.json", valid_case("DUPLICATE-ID"))
        self.write_case("two.json", valid_case("DUPLICATE-ID"))

        report, exit_code = self.validate()

        self.assertEqual(exit_code, 1)
        self.assertEqual(report["summary"]["duplicate_id_groups"], 1)
        self.assertEqual(report["summary"]["invalid"], 2)
        self.assertTrue(
            all(case["status"] == "invalid" for case in report["cases"])
        )
        self.assertTrue(
            all(
                {"code": "duplicate_case_id", "field": "case_id"}
                in case["errors"]
                for case in report["cases"]
            )
        )
        self.assertNotIn("DUPLICATE-ID", json.dumps(report))

    def test_duplicate_json_object_keys_are_rejected(self) -> None:
        (self.case_directory / "duplicate-key.json").write_text(
            '{"case_id":"first","case_id":"second"}', encoding="utf-8"
        )

        report, exit_code = self.validate()

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            report["cases"][0]["errors"], [{"code": "duplicate_json_key"}]
        )

    def test_report_is_deterministic_and_does_not_expose_fixture_values(self) -> None:
        self.write_case("z-case.json", valid_case("PRIVATE-SYNTHETIC-ID"))
        self.write_case("a-case.json", valid_case("ANOTHER-SYNTHETIC-ID"))

        first_report, first_exit_code = self.validate()
        second_report, second_exit_code = self.validate()
        first_json = json.dumps(first_report, indent=2, ensure_ascii=True) + "\n"
        second_json = json.dumps(second_report, indent=2, ensure_ascii=True) + "\n"

        self.assertEqual(first_exit_code, second_exit_code)
        self.assertEqual(first_json, second_json)
        self.assertLess(
            first_report["cases"][0]["file"], first_report["cases"][1]["file"]
        )
        self.assertNotIn("PRIVATE-SYNTHETIC-ID", first_json)
        self.assertNotIn("ANOTHER-SYNTHETIC-ID", first_json)
        self.assertNotIn(str(self.case_directory), first_json)

    def test_empty_catalog_fails_validation(self) -> None:
        report, exit_code = self.validate()

        self.assertEqual(exit_code, 1)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["errors"], [{"code": "no_cases_found"}])

    def test_catalog_read_error_returns_exit_two(self) -> None:
        report, exit_code = ai_evaluation_cases.validate_catalog(
            self.case_directory / "missing"
        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(report["status"], "error")
        self.assertEqual(report["errors"], [{"code": "catalog_read_error"}])

    def test_invocation_arguments_return_error_report_and_exit_two(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = ai_evaluation_cases.main(["--unexpected"])

        self.assertEqual(exit_code, 2)
        report = json.loads(output.getvalue())
        self.assertEqual(report["status"], "error")
        self.assertEqual(report["errors"], [{"code": "unexpected_arguments"}])


if __name__ == "__main__":
    unittest.main()
