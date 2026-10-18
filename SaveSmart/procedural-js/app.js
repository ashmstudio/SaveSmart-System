const expenseFields = [
  "food",
  "transportation",
  "school",
  "internet",
  "personal",
  "other",
];

const fieldLabels = {
  monthlyAllowance: "allowance received each time",
  currentSavings: "current savings",
  savingsGoal: "target savings amount",
  savingPeriod: "months remaining to reach your goal",
  plannedMonthlySavings: "money you can set aside each month",
  food: "food and meals expenses",
  transportation: "transportation expenses",
  school: "school expenses",
  internet: "internet and data expenses",
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
      : `Please enter a whole-peso amount for ${fieldLabels[field]}.`;

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
  } else {
    if (!Number.isFinite(value) || value < 0 || !Number.isInteger(value)) {
      throw new Error(errorMessage);
    }
    if (field === "savingsGoal" && value <= 0) {
      throw new Error("Target savings amount must be greater than 0.");
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
  const monthlySavingsCapacity = Math.max(
    0,
    Math.min(plannedMonthlySavings, availableMoney),
  );
  const remainingGoal = savingsGoal - currentSavings;
  let requiredMonthlySavings = 0;
  if (remainingGoal > 0) {
    requiredMonthlySavings = remainingGoal / savingPeriod;
  }

  const expectedSavings = currentSavings + monthlySavingsCapacity * savingPeriod;
  let status = "RED";

  if (currentSavings >= savingsGoal) {
    status = "GREEN";
  } else if (
    monthlySavingsCapacity >= requiredMonthlySavings &&
    expectedSavings >= savingsGoal
  ) {
    status = "GREEN";
  } else if (
    monthlySavingsCapacity > 0 &&
    (expectedSavings >= savingsGoal * 0.8 ||
      monthlySavingsCapacity >= requiredMonthlySavings * 0.8)
  ) {
    status = "YELLOW";
  }

  let recommendation;
  if (currentSavings >= savingsGoal) {
    recommendation = "You have already saved enough to reach your target.";
  } else if (availableMoney <= 0) {
    recommendation =
      "Your allowance does not cover the monthly expenses entered, so there is no money left to save. Check your amounts.";
  } else if (plannedMonthlySavings > availableMoney) {
    recommendation =
      "Your planned monthly savings are higher than the money left after expenses. The assessment uses only the available amount as your monthly savings capacity. Review your plan or expenses.";
  } else if (status === "GREEN") {
    recommendation =
      "Your monthly savings amount is enough to reach your target within the months remaining.";
  } else if (status === "YELLOW") {
    recommendation =
      "Your savings may get close to the target but may not reach it in time. Try saving more each month or allow more months.";
  } else {
    recommendation =
      "Your monthly savings amount is not enough to reach the target in time. Try saving more each month or allow more months.";
  }

  return {
    studentName,
    monthlyAllowance,
    estimatedMonthlyIncome,
    totalMonthlyExpenses,
    availableMoney,
    currentSavings,
    savingsGoal,
    requiredMonthlySavings,
    plannedMonthlySavings,
    monthlySavingsCapacity,
    savingPeriod,
    expectedSavings,
    goalPurpose,
    status,
    statusLabel: statusLabels[status],
    recommendation,
    allowanceFrequency,
  };
}

function showResult(result) {
  const details = [
    ["Your name", result.studentName],
    ["What are you saving for?", result.goalPurpose],
    ["Current savings so far", formatMoney(result.currentSavings)],
    ["Target savings amount", formatMoney(result.savingsGoal)],
    ["Months remaining to reach your goal", `${result.savingPeriod} months`],
    ["Allowance received each time", formatMoney(result.monthlyAllowance)],
    ["Allowance frequency", result.allowanceFrequency],
    ["Amount you can set aside each month", formatMoney(result.plannedMonthlySavings)],
    ["Available to save after expenses", formatMoney(result.monthlySavingsCapacity)],
    ["Estimated monthly allowance", formatMoney(result.estimatedMonthlyIncome)],
    ["Estimated monthly expenses", formatMoney(result.totalMonthlyExpenses)],
    ["Required savings each month", formatMoney(result.requiredMonthlySavings)],
    ["Estimated savings by your target date", formatMoney(result.expectedSavings)],
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
  return `₱${Number(amount).toLocaleString("en-PH", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
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
