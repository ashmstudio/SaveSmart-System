from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
OOP_DIR = PROJECT_DIR / "oop-python"
JS_FILE = PROJECT_DIR / "procedural-js" / "app.js"


def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {file_path}.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


oop_system = load_module("oop_system", OOP_DIR / "oop_system.py")
python_app = load_module("savesmart_app", OOP_DIR / "app.py")
SAMPLE_INPUT = oop_system.SAMPLE_INPUT
SavingsAssessmentSystem = oop_system.SavingsAssessmentSystem


def run_javascript(assessment_input):
    input_text = json.dumps(assessment_input, separators=(",", ":"))
    return subprocess.run(
        ["node", str(JS_FILE), input_text],
        check=False,
        capture_output=True,
        text=True,
    )


class FormInputParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = {}

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            attributes = dict(attrs)
            if "name" in attributes:
                self.inputs[attributes["name"]] = attributes


class AssessmentSystemTests(unittest.TestCase):
    def test_sample_results_match(self):
        python_result = SavingsAssessmentSystem(SAMPLE_INPUT).process()
        javascript_run = run_javascript(SAMPLE_INPUT)
        javascript_result = json.loads(javascript_run.stdout)

        self.assertEqual(javascript_run.returncode, 0, javascript_run.stderr)
        self.assertEqual(python_result, javascript_result)
        self.assertEqual(python_result["status"], "YELLOW")
        self.assertEqual(python_result["estimatedMonthlyIncome"], 6000)
        self.assertEqual(python_result["totalMonthlyExpenses"], 1600)

    def test_income_frequency_and_default_match(self):
        for frequency, expected_income in (
            ("weekly", 6000),
            ("every_2_weeks", 3000),
            ("monthly", 1500),
            ("not-a-frequency", 1500),
        ):
            assessment_input = dict(SAMPLE_INPUT, allowanceFrequency=frequency)
            python_result = SavingsAssessmentSystem(assessment_input).process()
            javascript_run = run_javascript(assessment_input)
            javascript_result = json.loads(javascript_run.stdout)

            self.assertEqual(javascript_run.returncode, 0, javascript_run.stderr)
            self.assertEqual(python_result, javascript_result)
            self.assertEqual(python_result["estimatedMonthlyIncome"], expected_income)

    def test_second_valid_input_matches(self):
        assessment_input = dict(
            SAMPLE_INPUT,
            studentName="Alex",
            monthlyAllowance="850.25",
            allowanceFrequency="every_2_weeks",
            food="100.50",
            transportation="40",
            school="75.25",
            internet="15",
            personal="30",
            other="0",
            currentSavings="200.75",
            goalPurpose="Emergency Fund",
            savingsGoal="2500",
            savingPeriod="5",
            plannedMonthlySavings="450.25",
        )
        python_result = SavingsAssessmentSystem(assessment_input).process()
        javascript_run = run_javascript(assessment_input)

        self.assertEqual(javascript_run.returncode, 0, javascript_run.stderr)
        self.assertEqual(python_result, json.loads(javascript_run.stdout))

    def test_missing_expenses_are_zero_in_both_systems(self):
        assessment_input = dict(SAMPLE_INPUT)
        for field in ("food", "transportation", "school", "internet", "personal", "other"):
            assessment_input.pop(field)

        python_result = SavingsAssessmentSystem(assessment_input).process()
        javascript_run = run_javascript(assessment_input)

        self.assertEqual(javascript_run.returncode, 0, javascript_run.stderr)
        self.assertEqual(python_result, json.loads(javascript_run.stdout))
        self.assertEqual(python_result["totalMonthlyExpenses"], 0)

    def test_zero_amounts_and_already_reached_goal(self):
        zero_input = dict(
            SAMPLE_INPUT,
            monthlyAllowance=0,
            currentSavings=0,
            savingsGoal=0,
            plannedMonthlySavings=0,
            savingPeriod=1,
            food=0,
            transportation=0,
            school=0,
            internet=0,
            personal=0,
            other=0,
        )
        reached_goal_input = dict(
            SAMPLE_INPUT,
            monthlyAllowance=100,
            allowanceFrequency="monthly",
            currentSavings=12000,
            savingsGoal=12000,
            plannedMonthlySavings=0,
            savingPeriod=6,
            food=0,
            transportation=0,
            school=0,
            internet=0,
            personal=0,
            other=0,
        )

        for assessment_input, expected_status in (
            (zero_input, "GREEN"),
            (reached_goal_input, "GREEN"),
        ):
            with self.subTest(status=expected_status, goal=assessment_input["savingsGoal"]):
                python_result = SavingsAssessmentSystem(assessment_input).process()
                javascript_run = run_javascript(assessment_input)

                self.assertEqual(javascript_run.returncode, 0, javascript_run.stderr)
                self.assertEqual(python_result, json.loads(javascript_run.stdout))
                self.assertEqual(python_result["status"], expected_status)
                self.assertEqual(python_result["requiredMonthlySavings"], 0)

    def test_each_status_matches(self):
        green_input = dict(
            SAMPLE_INPUT,
            monthlyAllowance=1000,
            allowanceFrequency="monthly",
            food=0,
            transportation=0,
            school=0,
            internet=0,
            personal=0,
            other=0,
            currentSavings=500,
            savingsGoal=1000,
            savingPeriod=1,
            plannedMonthlySavings=500,
        )
        red_input = dict(
            SAMPLE_INPUT,
            monthlyAllowance=0,
            allowanceFrequency="monthly",
            food=0,
            transportation=0,
            school=0,
            internet=0,
            personal=0,
            other=0,
            currentSavings=0,
            savingsGoal=10000,
            savingPeriod=6,
            plannedMonthlySavings=0,
        )

        for assessment_input, expected_status in (
            (green_input, "GREEN"),
            (SAMPLE_INPUT, "YELLOW"),
            (red_input, "RED"),
        ):
            with self.subTest(status=expected_status):
                python_result = SavingsAssessmentSystem(assessment_input).process()
                javascript_run = run_javascript(assessment_input)
                javascript_result = json.loads(javascript_run.stdout)

                self.assertEqual(javascript_run.returncode, 0, javascript_run.stderr)
                self.assertEqual(python_result, javascript_result)
                self.assertEqual(python_result["status"], expected_status)

    def test_decimal_calculations_match(self):
        assessment_input = dict(
            SAMPLE_INPUT,
            monthlyAllowance="0.1",
            allowanceFrequency="monthly",
            food="0.1",
            transportation="0.2",
            school="0.3",
            internet="0.4",
            personal="0.5",
            other="0.6",
            currentSavings="0.2",
            savingsGoal="1.1",
            savingPeriod="3",
            plannedMonthlySavings="0.3",
        )
        python_result = SavingsAssessmentSystem(assessment_input).process()
        javascript_run = run_javascript(assessment_input)

        self.assertEqual(javascript_run.returncode, 0, javascript_run.stderr)
        self.assertEqual(python_result, json.loads(javascript_run.stdout))

    def test_invalid_inputs_are_rejected_with_the_same_message(self):
        invalid_cases = (
            ("monthlyAllowance", "-1", "Please enter a valid amount for monthly allowance."),
            ("monthlyAllowance", "NaN", "Please enter a valid amount for monthly allowance."),
            ("monthlyAllowance", "0x10", "Please enter a valid amount for monthly allowance."),
            ("monthlyAllowance", "   ", "Please enter a valid amount for monthly allowance."),
            ("food", "-0.01", "Please enter a valid amount for food expenses."),
            ("food", "0.001", "Please enter a valid amount for food expenses."),
            ("savingPeriod", "0", "Please enter a whole number of months greater than 0."),
            ("savingPeriod", "-1", "Please enter a whole number of months greater than 0."),
            ("savingPeriod", "2.5", "Please enter a whole number of months greater than 0."),
            ("food", "not a number", "Please enter a valid amount for food expenses."),
        )

        for field, invalid_value, expected_message in invalid_cases:
            with self.subTest(field=field, value=invalid_value):
                assessment_input = dict(SAMPLE_INPUT, **{field: invalid_value})
                with self.assertRaisesRegex(ValueError, expected_message):
                    SavingsAssessmentSystem(assessment_input)

                javascript_run = run_javascript(assessment_input)
                javascript_error = json.loads(javascript_run.stdout)["error"]
                self.assertNotEqual(javascript_run.returncode, 0)
                self.assertEqual(javascript_error, expected_message)

    def test_missing_and_blank_required_inputs_are_rejected(self):
        required_fields = (
            "monthlyAllowance",
            "currentSavings",
            "savingsGoal",
            "savingPeriod",
            "plannedMonthlySavings",
        )
        for field in required_fields:
            for value in (None, ""):
                with self.subTest(field=field, value=value):
                    assessment_input = dict(SAMPLE_INPUT)
                    if value is None:
                        assessment_input.pop(field)
                    else:
                        assessment_input[field] = value

                    with self.assertRaises(ValueError) as python_error:
                        SavingsAssessmentSystem(assessment_input)

                    javascript_run = run_javascript(assessment_input)
                    javascript_error = json.loads(javascript_run.stdout)["error"]
                    self.assertNotEqual(javascript_run.returncode, 0)
                    self.assertEqual(str(python_error.exception), javascript_error)

    def test_zero_and_negative_values_are_consistent(self):
        zero_input = dict(
            SAMPLE_INPUT,
            monthlyAllowance="0",
            currentSavings="0",
            savingsGoal="0",
            plannedMonthlySavings="0",
            food="0",
            transportation="0",
            school="0",
            internet="0",
            personal="0",
            other="0",
        )
        python_result = SavingsAssessmentSystem(zero_input).process()
        javascript_run = run_javascript(zero_input)

        self.assertEqual(javascript_run.returncode, 0, javascript_run.stderr)
        self.assertEqual(python_result, json.loads(javascript_run.stdout))

        for field in (
            "monthlyAllowance",
            "currentSavings",
            "savingsGoal",
            "plannedMonthlySavings",
            "food",
            "transportation",
            "school",
            "internet",
            "personal",
            "other",
        ):
            with self.subTest(field=field):
                assessment_input = dict(SAMPLE_INPUT, **{field: "-0.01"})
                with self.assertRaises(ValueError) as python_error:
                    SavingsAssessmentSystem(assessment_input)

                javascript_run = run_javascript(assessment_input)
                javascript_error = json.loads(javascript_run.stdout)["error"]
                self.assertNotEqual(javascript_run.returncode, 0)
                self.assertEqual(str(python_error.exception), javascript_error)

    def test_both_forms_have_matching_input_steps_and_required_fields(self):
        form_files = (
            OOP_DIR / "templates" / "index.html",
            PROJECT_DIR / "procedural-js" / "index.html",
        )
        parsed_forms = []
        for file_path in form_files:
            parser = FormInputParser()
            parser.feed(file_path.read_text(encoding="utf-8"))
            parsed_forms.append(parser.inputs)

        self.assertEqual(parsed_forms[0], parsed_forms[1])
        for field in (
            "savingsGoal",
            "currentSavings",
            "monthlyAllowance",
            "plannedMonthlySavings",
            "food",
            "transportation",
            "school",
            "internet",
            "personal",
            "other",
        ):
            self.assertEqual(parsed_forms[0][field]["type"], "number")
            self.assertEqual(parsed_forms[0][field]["min"], "0")
            self.assertEqual(parsed_forms[0][field]["step"], "0.01")

        period = parsed_forms[0]["savingPeriod"]
        self.assertEqual(period["type"], "number")
        self.assertEqual(period["min"], "1")
        self.assertEqual(period["step"], "1")

        for field in (
            "savingsGoal",
            "currentSavings",
            "monthlyAllowance",
            "plannedMonthlySavings",
            "savingPeriod",
        ):
            self.assertIn("required", parsed_forms[0][field])
        for field in ("food", "transportation", "school", "internet", "personal", "other"):
            self.assertNotIn("required", parsed_forms[0][field])

        for file_path in form_files:
            html = file_path.read_text(encoding="utf-8")
            self.assertIn("<title>SaveSmart</title>", html)
            self.assertIn("<h1>SaveSmart</h1>", html)
            self.assertNotIn("PROCEDURAL VERSION</p>", html)
            self.assertNotIn("OBJECT-ORIENTED VERSION</p>", html)
            self.assertNotIn("Make a simple plan for reaching your savings goal.", html)
            self.assertIn("* Required", html)
            for phrase in (
                "Your name",
                "How much do you want to save?",
                "How much have you saved?",
                "How often do you receive your allowance?",
                "What are you saving for?",
                "How many months do you have?",
                "How much allowance do you receive?",
                "How much can you save each month?",
                "Your monthly expenses",
                "Food and meals",
                "Transportation",
                "School expenses",
                "Internet and data",
                "Personal expenses",
                "Other expenses",
                "Calculate my savings plan",
            ):
                self.assertIn(phrase, html)

    def test_flask_page_and_assessment_api(self):
        client = python_app.app.test_client()
        with tempfile.TemporaryDirectory() as temporary_directory:
            original_path = python_app.ASSESSMENTS_PATH
            python_app.ASSESSMENTS_PATH = Path(temporary_directory) / "assessments.json"
            try:
                page = client.get("/")
                self.assertEqual(page.status_code, 200)
                self.assertIn(b"<title>SaveSmart</title>", page.data)
                self.assertIn(b"<h1>SaveSmart</h1>", page.data)
                self.assertNotIn(b"PYTHON OBJECT-ORIENTED VERSION", page.data)
                self.assertNotIn(
                    b"Make a simple plan for reaching your savings goal.", page.data
                )
                self.assertNotIn(b"Register", page.data)
                css_response = client.get("/static/style.css")
                self.assertEqual(css_response.status_code, 200)
                css_response.close()
                script_response = client.get("/static/app.js")
                self.assertEqual(script_response.status_code, 200)
                script_response.close()

                response = client.post("/api/assessment", json=SAMPLE_INPUT)
                self.assertEqual(response.status_code, 200)
                python_result = response.get_json()
                javascript_result = json.loads(run_javascript(SAMPLE_INPUT).stdout)
                self.assertEqual(python_result, javascript_result)

                with python_app.ASSESSMENTS_PATH.open("r", encoding="utf-8") as file:
                    saved_records = json.load(file)
                self.assertEqual(len(saved_records), 1)
                self.assertEqual(saved_records[0]["status"], python_result["status"])

                invalid_response = client.post(
                    "/api/assessment",
                    json=dict(SAMPLE_INPUT, savingsGoal="-10"),
                )
                self.assertEqual(invalid_response.status_code, 400)
                self.assertEqual(
                    client.post("/api/assessment", json={}).status_code,
                    400,
                )
            finally:
                python_app.ASSESSMENTS_PATH = original_path


if __name__ == "__main__":
    unittest.main(verbosity=2)
