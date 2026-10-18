const assessmentForm = document.getElementById("assessmentForm");

assessmentForm.addEventListener("input", () => {
  document.getElementById("formMessage").textContent = "";
  document.getElementById("resultCard").hidden = true;
});

assessmentForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formMessage = document.getElementById("formMessage");
  const resultCard = document.getElementById("resultCard");
  formMessage.textContent = "";

  const formData = new FormData(assessmentForm);
  const assessmentInput = Object.fromEntries(formData.entries());

  try {
    const response = await fetch("/api/assessment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(assessmentInput),
    });
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "The assessment could not be completed.");
    }

    showResult(result);
    resultCard.hidden = false;
  } catch (error) {
    formMessage.textContent =
      error instanceof TypeError
        ? "Could not connect to the assessment app. Check that the Flask server is running."
        : error.message;
    resultCard.hidden = true;
  }
});

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

  for (const [label, amount] of details) {
    const row = document.createElement("p");
    const name = document.createElement("span");
    const value = document.createElement("strong");
    name.textContent = label;
    value.textContent = amount;
    row.append(name, value);
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
