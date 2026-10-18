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
    "monthlyAllowance": "allowance received each time",
    "currentSavings": "current savings",
    "savingsGoal": "target savings amount",
    "savingPeriod": "months remaining to reach your goal",
    "plannedMonthlySavings": "money you can set aside each month",
    "food": "food and meals expenses",
    "transportation": "transportation expenses",
    "school": "school expenses",
    "internet": "internet and data expenses",
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
            else f"Please enter a whole-peso amount for {FIELD_LABELS[field]}."
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
        else:
            if not math.isfinite(number) or number < 0 or not number.is_integer():
                raise ValueError(error_message)
            if field == "savingsGoal" and number <= 0:
                raise ValueError("Target savings amount must be greater than 0.")
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
            self.calculate_monthly_savings_capacity() * self.saving_period
        )

    def calculate_monthly_savings_capacity(self):
        monthly_income = self.calculate_monthly_income()
        total_expenses = self.calculate_total_expenses()
        available_money = monthly_income - total_expenses
        return max(0, min(self.planned_monthly_savings, available_money))

    def assess_goal(self, required_savings, expected_savings):
        if self.current_savings >= self.savings_goal:
            return "GREEN"
        monthly_savings_capacity = self.calculate_monthly_savings_capacity()
        if (
            monthly_savings_capacity >= required_savings
            and expected_savings >= self.savings_goal
        ):
            return "GREEN"
        if monthly_savings_capacity > 0 and (
            expected_savings >= self.savings_goal * 0.8
            or monthly_savings_capacity >= required_savings * 0.8
        ):
            return "YELLOW"
        return "RED"

    def recommendation_for(self, status, available_money):
        if self.current_savings >= self.savings_goal:
            return "You have already saved enough to reach your target."
        if available_money <= 0:
            return (
                "Your allowance does not cover the monthly expenses entered, so "
                "there is no money left to save. Check your amounts."
            )
        if self.planned_monthly_savings > available_money:
            return (
                "Your planned monthly savings are higher than the money left after "
                "expenses. The assessment uses only the available amount as your "
                "monthly savings capacity. Review your plan or expenses."
            )
        if status == "GREEN":
            return (
                "Your monthly savings amount is enough to reach your target within "
                "the months remaining."
            )
        if status == "YELLOW":
            return (
                "Your savings may get close to the target but may not reach it in "
                "time. Try saving more each month or allow more months."
            )
        return (
            "Your monthly savings amount is not enough to reach the target in "
            "time. Try saving more each month or allow more months."
        )

    def process(self):
        monthly_income = self.calculate_monthly_income()
        total_expenses = self.calculate_total_expenses()
        available_money = monthly_income - total_expenses
        monthly_savings_capacity = self.calculate_monthly_savings_capacity()
        required_savings = self.calculate_required_monthly_savings()
        expected_savings = self.calculate_expected_savings()
        status = self.assess_goal(required_savings, expected_savings)

        return {
            "studentName": self.student_name,
            "monthlyAllowance": self.monthly_allowance,
            "allowanceFrequency": self.allowance_frequency,
            "estimatedMonthlyIncome": monthly_income,
            "totalMonthlyExpenses": total_expenses,
            "availableMoney": available_money,
            "currentSavings": self.current_savings,
            "savingsGoal": self.savings_goal,
            "requiredMonthlySavings": required_savings,
            "plannedMonthlySavings": self.planned_monthly_savings,
            "monthlySavingsCapacity": monthly_savings_capacity,
            "savingPeriod": self.saving_period,
            "expectedSavings": expected_savings,
            "goalPurpose": self.goal_purpose,
            "status": status,
            "statusLabel": STATUS_LABELS[status],
            "recommendation": self.recommendation_for(status, available_money),
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
