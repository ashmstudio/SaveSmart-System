from __future__ import annotations

import math
import re


EXPENSE_FIELDS = (
    "food",
    "transportation",
    "school",
    "internet",
    "personal",
    "other",
)

FIELD_LABELS = {
    "monthlyAllowance": "monthly allowance",
    "currentSavings": "current savings",
    "savingsGoal": "savings goal",
    "savingPeriod": "saving period",
    "plannedMonthlySavings": "planned monthly savings",
    "food": "food expenses",
    "transportation": "transportation expenses",
    "school": "school expenses",
    "internet": "internet expenses",
    "personal": "personal expenses",
    "other": "other expenses",
}

STATUS_LABELS = {
    "GREEN": "GOAL ACHIEVABLE",
    "YELLOW": "NEEDS ADJUSTMENT",
    "RED": "GOAL NEEDS REVISION",
}

NUMBER_PATTERN = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")


class SavingsAssessmentSystem:
    def __init__(self, assessment_input: dict):
        if not isinstance(assessment_input, dict):
            raise ValueError("Please provide assessment information.")

        self.student_name = self._read_text(assessment_input.get("studentName"), "Student")
        self.goal_purpose = self._read_text(assessment_input.get("goalPurpose"), "Personal Goal")
        self.monthly_allowance = self._read_number(assessment_input, "monthlyAllowance")
        self.allowance_frequency = assessment_input.get("allowanceFrequency") or "monthly"
        self.current_savings = self._read_number(assessment_input, "currentSavings")
        self.savings_goal = self._read_number(assessment_input, "savingsGoal")
        self.saving_period = self._read_number(assessment_input, "savingPeriod")
        self.planned_monthly_savings = self._read_number(
            assessment_input, "plannedMonthlySavings"
        )
        self.expenses = {}

        for field in EXPENSE_FIELDS:
            self.expenses[field] = self._read_number(
                assessment_input, field, allow_empty=True
            )

    @staticmethod
    def _read_text(value, default):
        if not isinstance(value, str) or not value.strip():
            return default
        return value.strip()

    @staticmethod
    def _read_number(assessment_input, field, allow_empty=False):
        value = assessment_input.get(field)
        error_message = (
            "Please enter a whole number of months greater than 0."
            if field == "savingPeriod"
            else f"Please enter a valid amount for {FIELD_LABELS[field]}."
        )
        if allow_empty and (value is None or value == ""):
            return 0.0

        if isinstance(value, bool) or value is None or value == "":
            raise ValueError(error_message)

        if isinstance(value, str):
            value = value.strip()
            if not NUMBER_PATTERN.fullmatch(value):
                raise ValueError(error_message)
        elif not isinstance(value, (int, float)):
            raise ValueError(error_message)

        try:
            number = float(value)
        except (OverflowError, TypeError, ValueError):
            raise ValueError(error_message) from None

        if field == "savingPeriod":
            if not math.isfinite(number) or number <= 0 or not number.is_integer():
                raise ValueError(error_message)
        elif not math.isfinite(number) or number < 0:
            raise ValueError(error_message)
        else:
            cents_value = number * 100
            if not math.isfinite(cents_value) or abs(cents_value - round(cents_value)) > 1e-8:
                raise ValueError(error_message)
        return number

    def calculate_monthly_income(self):
        if self.allowance_frequency == "weekly":
            return self.monthly_allowance * 4
        if self.allowance_frequency == "every_2_weeks":
            return self.monthly_allowance * 2
        return self.monthly_allowance

    def calculate_total_expenses(self):
        total = 0
        for amount in self.expenses.values():
            total += amount
        return total

    def calculate_required_monthly_savings(self):
        remaining = self.savings_goal - self.current_savings
        if remaining <= 0:
            return 0
        return remaining / self.saving_period

    def calculate_expected_savings(self):
        return self.current_savings + (
            self.planned_monthly_savings * self.saving_period
        )

    def assess_goal(self, available_money, required_savings, expected_savings):
        if self.savings_goal <= 0:
            return "GREEN"
        if available_money >= required_savings and expected_savings >= self.savings_goal:
            return "GREEN"
        if available_money > 0 and (
            expected_savings >= self.savings_goal * 0.8
            or available_money >= required_savings * 0.8
        ):
            return "YELLOW"
        return "RED"

    @staticmethod
    def recommendation_for(status):
        if status == "GREEN":
            return (
                "Your current plan can support your savings goal. Try to save your "
                "planned amount consistently each month."
            )
        if status == "YELLOW":
            return (
                "Your goal may be difficult to reach within your selected period. "
                "Consider reducing some non-essential expenses or extending the "
                "saving period."
            )
        return (
            "Your current available money may not support this goal within the "
            "selected period. Consider a smaller goal or a longer saving period."
        )

    def process(self):
        monthly_income = self.calculate_monthly_income()
        total_expenses = self.calculate_total_expenses()
        available_money = monthly_income - total_expenses
        required_savings = self.calculate_required_monthly_savings()
        expected_savings = self.calculate_expected_savings()
        status = self.assess_goal(
            available_money, required_savings, expected_savings
        )

        return {
            "studentName": self.student_name,
            "estimatedMonthlyIncome": monthly_income,
            "totalMonthlyExpenses": total_expenses,
            "availableMoney": available_money,
            "currentSavings": self.current_savings,
            "savingsGoal": self.savings_goal,
            "requiredMonthlySavings": required_savings,
            "plannedMonthlySavings": self.planned_monthly_savings,
            "savingPeriod": self.saving_period,
            "expectedSavings": expected_savings,
            "goalPurpose": self.goal_purpose,
            "status": status,
            "statusLabel": STATUS_LABELS[status],
            "recommendation": self.recommendation_for(status),
        }


SAMPLE_INPUT = {
    "studentName": "Sample Student",
    "monthlyAllowance": 1500,
    "allowanceFrequency": "weekly",
    "food": 600,
    "transportation": 200,
    "school": 300,
    "internet": 150,
    "personal": 250,
    "other": 100,
    "currentSavings": 500,
    "goalPurpose": "Gadget / Laptop",
    "savingsGoal": 12000,
    "savingPeriod": 6,
    "plannedMonthlySavings": 1800,
}


if __name__ == "__main__":
    import json

    result = SavingsAssessmentSystem(SAMPLE_INPUT).process()
    print(json.dumps(result, indent=2))
