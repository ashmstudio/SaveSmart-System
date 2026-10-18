const expenseFields = [
  "food",
  "transportation",
  "school",
  "internet",
  "personal",
  "other",
];

const fieldLabels = {
  monthlyAllowance: "monthly allowance",
  currentSavings: "current savings",
  savingsGoal: "savings goal",
  savingPeriod: "saving period",
  plannedMonthlySavings: "planned monthly savings",
  food: "food expenses",
  transportation: "transportation expenses",
  school: "school expenses",
  internet: "internet expenses",
  personal: "personal expenses",
  other: "other expenses",
};

const statusLabels = {
  GREEN: "GOAL ACHIEVABLE",
  YELLOW: "NEEDS ADJUSTMENT",
  RED: "GOAL NEEDS REVISION",
};

const numberPattern = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/;

function readNumber(input, field, allowEmpty = false) {
  let value = input[field];
  const errorMessage =
    field === "savingPeriod"
      ? "Please enter a whole number of months greater than 0."
      : `Please enter a valid amount for ${fieldLabels[field]}.`;

  if (allowEmpty && (value === undefined || value === null || value === "")) {
    return 0;
  }

  if (
    typeof value === "boolean" ||
    value === undefined ||
    value === null ||
    value === "" ||
    (typeof value === "string" && value.trim() === "") ||
    (typeof value !== "number" && typeof value !== "string")
  ) {
    throw new Error(errorMessage);
  }

  if (typeof value === "string") {
    value = value.trim();
    if (!numberPattern.test(value)) {
      throw new Error(errorMessage);
    }
  }

  value = Number(value);
  if (field === "savingPeriod") {
    if (!Number.isFinite(value) || value <= 0 || !Number.isInteger(value)) {
      throw new Error(errorMessage);
    }
  } else if (!Number.isFinite(value) || value < 0) {
    throw new Error(errorMessage);
  } else {
    const centsValue = value * 100;
    if (
      !Number.isFinite(centsValue) ||
      Math.abs(centsValue - Math.round(centsValue)) > 1e-8
    ) {
      throw new Error(errorMessage);
    }
  }
  return value;
}

function processAssessment(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) {
    throw new Error("Please provide assessment information.");
  }

  const studentName =
    typeof input.studentName === "string" && input.studentName.trim()
      ? input.studentName.trim()
      : "Student";
  const goalPurpose =
    typeof input.goalPurpose === "string" && input.goalPurpose.trim()
      ? input.goalPurpose.trim()
      : "Personal Goal";
  const monthlyAllowance = readNumber(input, "monthlyAllowance");
  const currentSavings = readNumber(input, "currentSavings");
  const savingsGoal = readNumber(input, "savingsGoal");
  const savingPeriod = readNumber(input, "savingPeriod");
  const plannedMonthlySavings = readNumber(input, "plannedMonthlySavings");
  const expenses = {};

  for (const field of expenseFields) {
    expenses[field] = readNumber(input, field, true);
  }

  let estimatedMonthlyIncome = monthlyAllowance;
  const allowanceFrequency = input.allowanceFrequency || "monthly";
  if (allowanceFrequency === "weekly") {
    estimatedMonthlyIncome = monthlyAllowance * 4;
  } else if (allowanceFrequency === "every_2_weeks") {
    estimatedMonthlyIncome = monthlyAllowance * 2;
  }

  let totalMonthlyExpenses = 0;
  for (const field of expenseFields) {
    totalMonthlyExpenses += expenses[field];
  }

  const availableMoney = estimatedMonthlyIncome - totalMonthlyExpenses;
  const remainingGoal = savingsGoal - currentSavings;
  let requiredMonthlySavings = 0;
  if (remainingGoal > 0) {
    requiredMonthlySavings = remainingGoal / savingPeriod;
  }

  const expectedSavings =
    currentSavings + plannedMonthlySavings * savingPeriod;
  let status = "RED";

  if (savingsGoal <= 0) {
    status = "GREEN";
  } else if (
    availableMoney >= requiredMonthlySavings &&
    expectedSavings >= savingsGoal
  ) {
    status = "GREEN";
  } else if (
    availableMoney > 0 &&
    (expectedSavings >= savingsGoal * 0.8 ||
      availableMoney >= requiredMonthlySavings * 0.8)
  ) {
    status = "YELLOW";
  }

  let recommendation =
    "Your current available money may not support this goal within the selected period. Consider a smaller goal or a longer saving period.";
  if (status === "GREEN") {
    recommendation =
      "Your current plan can support your savings goal. Try to save your planned amount consistently each month.";
  } else if (status === "YELLOW") {
    recommendation =
      "Your goal may be difficult to reach within your selected period. Consider reducing some non-essential expenses or extending the saving period.";
  }

  return {
    studentName,
    estimatedMonthlyIncome,
    totalMonthlyExpenses,
    availableMoney,
    currentSavings,
    savingsGoal,
    requiredMonthlySavings,
    plannedMonthlySavings,
    savingPeriod,
    expectedSavings,
    goalPurpose,
    status,
    statusLabel: statusLabels[status],
    recommendation,
  };
}

function showResult(result) {
  const details = [
    ["Your name", result.studentName],
    ["What are you saving for?", result.goalPurpose],
    ["How much have you saved?", formatMoney(result.currentSavings)],
    ["How much do you want to save?", formatMoney(result.savingsGoal)],
    ["How many months do you have?", `${result.savingPeriod} months`],
    ["How much can you save each month?", formatMoney(result.plannedMonthlySavings)],
    ["Estimated monthly income", formatMoney(result.estimatedMonthlyIncome)],
    ["Total monthly expenses", formatMoney(result.totalMonthlyExpenses)],
    ["Available money", formatMoney(result.availableMoney)],
    ["Required monthly savings", formatMoney(result.requiredMonthlySavings)],
    ["Expected savings", formatMoney(result.expectedSavings)],
  ];
  const resultDetails = document.getElementById("resultDetails");
  resultDetails.replaceChildren();

  for (const [label, value] of details) {
    const row = document.createElement("p");
    const name = document.createElement("span");
    const amount = document.createElement("strong");
    name.textContent = label;
    amount.textContent = value;
    row.append(name, amount);
    resultDetails.append(row);
  }

  const statusLabel = document.getElementById("statusLabel");
  statusLabel.textContent = result.statusLabel;
  statusLabel.className = `status-label ${result.status.toLowerCase()}`;
  document.getElementById("recommendation").textContent = result.recommendation;
}

function formatMoney(amount) {
  return Number(amount).toLocaleString("en-PH", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

if (typeof document !== "undefined") {
  const assessmentForm = document.getElementById("assessmentForm");

  assessmentForm.addEventListener("input", () => {
    document.getElementById("formMessage").textContent = "";
    document.getElementById("resultCard").hidden = true;
  });

  assessmentForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formMessage = document.getElementById("formMessage");
    const resultCard = document.getElementById("resultCard");
    formMessage.textContent = "";

    const formData = new FormData(assessmentForm);
    const assessmentInput = Object.fromEntries(formData.entries());

    try {
      const result = processAssessment(assessmentInput);
      showResult(result);
      resultCard.hidden = false;
    } catch (error) {
      formMessage.textContent = error.message;
      resultCard.hidden = true;
    }
  });
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { processAssessment };

  if (require.main === module) {
    const sampleInput = {
      studentName: "Sample Student",
      monthlyAllowance: 1500,
      allowanceFrequency: "weekly",
      food: 600,
      transportation: 200,
      school: 300,
      internet: 150,
      personal: 250,
      other: 100,
      currentSavings: 500,
      goalPurpose: "Gadget / Laptop",
      savingsGoal: 12000,
      savingPeriod: 6,
      plannedMonthlySavings: 1800,
    };

    try {
      const input = process.argv[2]
        ? JSON.parse(process.argv[2])
        : sampleInput;
      console.log(JSON.stringify(processAssessment(input)));
    } catch (error) {
      console.log(JSON.stringify({ error: error.message }));
      process.exitCode = 1;
    }
  }
}
