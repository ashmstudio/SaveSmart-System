const sampleInput = {
  studentName: 'Sample Student',
  monthlyAllowance: 1500,
  allowanceFrequency: 'weekly',
  expenses: {
    food: 600,
    transportation: 200,
    school: 300,
    internet: 150,
    personal: 250,
    other: 100,
  },
  currentSavings: 500,
  goalPurpose: 'Gadget / Laptop',
  savingsGoal: 12000,
  savingPeriod: 6,
  plannedMonthlySavings: 1800,
};

function calculateMonthlyIncome(allowance, frequency) {
  if (frequency === 'weekly') return allowance * 4;
  if (frequency === 'every_2_weeks') return allowance * 2;
  return allowance;
}

function calculateTotalExpenses(expenses) {
  let total = 0;
  for (const amount of Object.values(expenses)) total += amount;
  return total;
}

function calculateRequiredMonthlySavings(goal, currentSavings, period) {
  const remaining = goal - currentSavings;
  if (period <= 0 || remaining <= 0) return 0;
  return remaining / period;
}

function calculateExpectedSavings(currentSavings, plannedSavings, period) {
  return currentSavings + plannedSavings * period;
}

function assessGoal(availableMoney, requiredSavings, expectedSavings, goal) {
  if (goal <= 0) return 'GREEN';
  if (availableMoney >= requiredSavings && expectedSavings >= goal) return 'GREEN';
  if (availableMoney > 0 && (expectedSavings >= goal * 0.8 || availableMoney >= requiredSavings * 0.8)) return 'YELLOW';
  return 'RED';
}

function getRecommendation(status) {
  if (status === 'GREEN') return 'Your current plan can support your savings goal. Try to save your planned amount consistently each month.';
  if (status === 'YELLOW') return 'Your goal may be difficult to reach within your selected period. Consider reducing some non-essential expenses or extending the saving period.';
  return 'Your current available money may not support this goal within the selected period. Consider a smaller goal or a longer saving period.';
}

function processAssessment(input) {
  const monthlyIncome = calculateMonthlyIncome(input.monthlyAllowance, input.allowanceFrequency);
  const totalExpenses = calculateTotalExpenses(input.expenses);
  const availableMoney = monthlyIncome - totalExpenses;
  const requiredMonthlySavings = calculateRequiredMonthlySavings(input.savingsGoal, input.currentSavings, input.savingPeriod);
  const expectedSavings = calculateExpectedSavings(input.currentSavings, input.plannedMonthlySavings, input.savingPeriod);
  const status = assessGoal(availableMoney, requiredMonthlySavings, expectedSavings, input.savingsGoal);
  const statusLabels = { GREEN: 'GOAL ACHIEVABLE', YELLOW: 'NEEDS ADJUSTMENT', RED: 'GOAL NEEDS REVISION' };

  return {
    studentName: input.studentName,
    estimatedMonthlyIncome: monthlyIncome,
    totalMonthlyExpenses: totalExpenses,
    availableMoney,
    currentSavings: input.currentSavings,
    savingsGoal: input.savingsGoal,
    requiredMonthlySavings,
    plannedMonthlySavings: input.plannedMonthlySavings,
    savingPeriod: input.savingPeriod,
    expectedSavings,
    goalPurpose: input.goalPurpose,
    status,
    statusLabel: statusLabels[status],
    recommendation: getRecommendation(status),
  };
}

if (require.main === module) {
  console.log(JSON.stringify(processAssessment(sampleInput), null, 2));
}

module.exports = { processAssessment };
