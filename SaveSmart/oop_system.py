from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class SavingsAssessmentInput:
    student_name: str
    monthly_allowance: float
    allowance_frequency: str
    expenses: dict[str, float]
    current_savings: float
    goal_purpose: str
    savings_goal: float
    saving_period: float
    planned_monthly_savings: float


@dataclass
class SavingsAssessmentResult:
    student_name: str
    estimated_monthly_income: float
    total_monthly_expenses: float
    available_money: float
    current_savings: float
    savings_goal: float
    required_monthly_savings: float
    planned_monthly_savings: float
    saving_period: float
    expected_savings: float
    goal_purpose: str
    status: str
    status_label: str
    recommendation: str

    def to_dict(self) -> dict:
        return asdict(self)


class SavingsAssessmentSystem:
    def __init__(self, assessment_input: SavingsAssessmentInput):
        self.assessment_input = assessment_input

    def calculate_monthly_income(self) -> float:
        frequency = self.assessment_input.allowance_frequency
        allowance = self.assessment_input.monthly_allowance
        if frequency == "weekly":
            return allowance * 4
        if frequency == "every_2_weeks":
            return allowance * 2
        return allowance

    def calculate_total_expenses(self) -> float:
        return sum(self.assessment_input.expenses.values())

    def calculate_required_monthly_savings(self) -> float:
        remaining = self.assessment_input.savings_goal - self.assessment_input.current_savings
        if self.assessment_input.saving_period <= 0 or remaining <= 0:
            return 0
        return remaining / self.assessment_input.saving_period

    def calculate_expected_savings(self) -> float:
        return self.assessment_input.current_savings + (
            self.assessment_input.planned_monthly_savings * self.assessment_input.saving_period
        )

    def assess_goal(self, available_money: float, required_savings: float, expected_savings: float) -> str:
        goal = self.assessment_input.savings_goal
        if goal <= 0:
            return "GREEN"
        if available_money >= required_savings and expected_savings >= goal:
            return "GREEN"
        if available_money > 0 and (
            expected_savings >= goal * 0.8 or available_money >= required_savings * 0.8
        ):
            return "YELLOW"
        return "RED"

    @staticmethod
    def recommendation_for(status: str) -> str:
        if status == "GREEN":
            return "Your current plan can support your savings goal. Try to save your planned amount consistently each month."
        if status == "YELLOW":
            return "Your goal may be difficult to reach within your selected period. Consider reducing some non-essential expenses or extending the saving period."
        return "Your current available money may not support this goal within the selected period. Consider a smaller goal or a longer saving period."

    def process(self) -> SavingsAssessmentResult:
        monthly_income = self.calculate_monthly_income()
        total_expenses = self.calculate_total_expenses()
        available_money = monthly_income - total_expenses
        required_savings = self.calculate_required_monthly_savings()
        expected_savings = self.calculate_expected_savings()
        status = self.assess_goal(available_money, required_savings, expected_savings)
        labels = {"GREEN": "GOAL ACHIEVABLE", "YELLOW": "NEEDS ADJUSTMENT", "RED": "GOAL NEEDS REVISION"}

        return SavingsAssessmentResult(
            student_name=self.assessment_input.student_name,
            estimated_monthly_income=monthly_income,
            total_monthly_expenses=total_expenses,
            available_money=available_money,
            current_savings=self.assessment_input.current_savings,
            savings_goal=self.assessment_input.savings_goal,
            required_monthly_savings=required_savings,
            planned_monthly_savings=self.assessment_input.planned_monthly_savings,
            saving_period=self.assessment_input.saving_period,
            expected_savings=expected_savings,
            goal_purpose=self.assessment_input.goal_purpose,
            status=status,
            status_label=labels[status],
            recommendation=self.recommendation_for(status),
        )


SAMPLE_INPUT = SavingsAssessmentInput(
    student_name="Sample Student",
    monthly_allowance=1500,
    allowance_frequency="weekly",
    expenses={"food": 600, "transportation": 200, "school": 300, "internet": 150, "personal": 250, "other": 100},
    current_savings=500,
    goal_purpose="Gadget / Laptop",
    savings_goal=12000,
    saving_period=6,
    planned_monthly_savings=1800,
)


if __name__ == "__main__":
    import json

    print(json.dumps(SavingsAssessmentSystem(SAMPLE_INPUT).process().to_dict(), indent=2))
