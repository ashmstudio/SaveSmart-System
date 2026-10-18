# SaveSmart: Project and Defense Guide

SaveSmart estimates whether a student can reach a savings goal using their income, expenses, current savings, and plan. It contains two separate versions of the same assessment: a browser-based JavaScript procedural version and a Python OOP version served by Flask.

## 1. Project layout

```text
SaveSmart/
|-- data/
|   `-- assessments.json
|-- oop-python/
|   |-- app.py
|   |-- oop_system.py
|   |-- static/
|   |   |-- app.js
|   |   `-- style.css
|   `-- templates/
|       `-- index.html
|-- procedural-js/
|   |-- app.js
|   |-- index.html
|   `-- style.css
|-- tests/
|   `-- verify_systems.py
|-- README.md
|-- requirements.txt
`-- start_savesmart.bat
```

| File | Purpose |
|---|---|
| `procedural-js/index.html` | JavaScript version's assessment form and result area. Loads its local stylesheet and script. |
| `procedural-js/app.js` | JavaScript procedural calculation, validation, event handling, and result display. Also accepts sample or JSON input from Node.js for tests. |
| `procedural-js/style.css` | Purple styling for the JavaScript page. |
| `oop-python/app.py` | Python app entry point; Flask serves the page and accepts assessment requests at `/api/assessment`. |
| `oop-python/oop_system.py` | `SavingsAssessmentSystem` class: input validation, instance attributes, calculation methods, and result creation. |
| `oop-python/templates/index.html` | Python version's assessment form. Jinja and Flask connect its template to static files. |
| `oop-python/static/app.js` | Sends form input to Flask and displays the returned Python result; it does not calculate the assessment. |
| `oop-python/static/style.css` | Purple styling for the Python page. |
| `data/assessments.json` | Assessment records saved by the Python app. The browser-only JavaScript version does not save records. |
| `tests/verify_systems.py` | Runs the real Python class and JavaScript program with equivalent inputs and tests their output, validation, forms, and Flask route. |
| `requirements.txt` | Lists Flask, the Python web framework used by the OOP app. |
| `start_savesmart.bat` | Windows shortcut that starts Flask with the workspace `.venv` Python executable. |

## 2. Run the two systems

The workspace already has a virtual environment at `C:\mycodex\MCO_CS301\.venv`. From PowerShell:

```powershell
Set-Location C:\mycodex\MCO_CS301\SaveSmart
& ..\.venv\Scripts\python.exe -m pip install -r requirements.txt
& ..\.venv\Scripts\python.exe oop-python\app.py
```

Open http://127.0.0.1:5000. Stop Flask with **Ctrl+C** in that terminal. The install step is needed only if Flask is not already installed in that environment.

To run the procedural page, open `procedural-js/index.html` in a browser. One PowerShell option is:

```powershell
Start-Process .\procedural-js\index.html
```

It runs its assessment in the browser and does not need the Python server. To run the same JavaScript calculation in Node.js instead:

```powershell
node procedural-js\app.js
```

Run the full comparison tests from the SaveSmart folder:

```powershell
& ..\.venv\Scripts\python.exe tests\verify_systems.py
```

## 3. Inputs, validation, and outputs

The two forms use the same field names and meanings:

| Input | Rule |
|---|---|
| `studentName` | Optional text; blank becomes `Student`. |
| `goalPurpose` | A choice from the form; blank becomes `Personal Goal`. |
| `allowanceFrequency` | `weekly`, `every_2_weeks`, or `monthly`. An unknown or blank value follows the existing monthly default. |
| `monthlyAllowance`, `currentSavings`, `savingsGoal`, `plannedMonthlySavings` | Required, finite, non-negative money amounts. Zero and amounts with up to two decimal places are accepted. |
| `savingPeriod` | Required whole number of months greater than zero. |
| `food`, `transportation`, `school`, `internet`, `personal`, `other` | Optional, finite, non-negative money amounts. Blank means zero; cents are accepted. |

Currency controls use `min="0"` and `step="0.01"` because the system accepts cents. Their spinner arrows therefore change by one cent, not one whole peso. The timeframe uses `min="1"` and `step="1"`; the Python and JavaScript validators also reject fractional months, so its spinner changes by one month. The assessment calculations do not round intermediate values; the result pages display money to two decimal places.

The result objects from both calculators have these corresponding fields: `studentName`, `estimatedMonthlyIncome`, `totalMonthlyExpenses`, `availableMoney`, `currentSavings`, `savingsGoal`, `requiredMonthlySavings`, `plannedMonthlySavings`, `savingPeriod`, `expectedSavings`, `goalPurpose`, `status`, `statusLabel`, and `recommendation`.

Invalid information is not calculated or presented as a result. JavaScript `processAssessment` throws a readable error that the form handler displays. Python `_read_number` raises `ValueError`, which the Flask route returns as a `400` response for the form script to display.

## 4. Exact system flows

### JavaScript Procedural

1. The browser opens `procedural-js/index.html`, which loads `style.css` and `app.js`.
2. The user fills the form and chooses **Calculate my savings plan**.
3. The submit event handler in `app.js` prevents a page reload and reads fields into a plain JavaScript object with `FormData`.
4. `processAssessment(input)` validates the fields, calls the calculation steps, and returns a result object.
5. The event handler passes that result to `showResult(result)`, which adds result rows to the page.
6. `formatMoney(amount)` formats displayed monetary amounts; the original result values are not rounded by this display step.

The same `app.js` can be run from Node.js. Its `require.main === module` block uses the sample input (or JSON passed on the command line), prints the actual calculation result, and sets a failing exit code for invalid input. The browser guard prevents Node.js from trying to access page elements.

### Python OOP

1. `oop-python/app.py` starts Flask on `127.0.0.1:5000`.
2. A browser request to `/` calls `index()`. Flask renders `templates/index.html` and serves files from `static/`.
3. The Python page's `static/app.js` reads the form and sends JSON to `/api/assessment` with `fetch`.
4. The Flask `process_assessment()` route creates `SavingsAssessmentSystem(assessment_input)`.
5. The class constructor validates and stores values in instance attributes. `process()` calls the calculation methods and returns a result dictionary.
6. The route sends that dictionary back as JSON and saves a dated copy in `data/assessments.json`.
7. The page script displays the response using the Python page's result area.

The Python UI script handles the browser form and display; the assessment formulas are in Python `oop_system.py`. The JavaScript calculator in `procedural-js/app.js` never calls Python.

## 5. Formula reviewer and worked example

Both calculation implementations use the same steps:

1. **Estimated monthly income:** weekly allowance × 4; every-two-weeks allowance × 2; monthly allowance × 1.
2. **Total monthly expenses:** add food, transportation, school, internet, personal, and other expenses. A blank expense is zero.
3. **Available money:** estimated monthly income − total monthly expenses.
4. **Required monthly savings:** if the goal minus current savings is positive, divide that remainder by the saving period; otherwise use zero.
5. **Expected savings:** current savings + planned monthly savings × saving period.
6. **Status:**
   - `GREEN` if the goal is zero, or if available money covers required monthly savings **and** expected savings reaches the goal.
   - Otherwise, `YELLOW` if available money is positive and either expected savings reaches 80% of the goal **or** available money covers 80% of required monthly savings.
   - Otherwise, `RED`.

The 80% comparison is the existing assessment rule. The implementation does not round required monthly savings before these comparisons.

### Worked sample (same inputs in both systems)

- Allowance: 1,500 per week; expenses: 600 + 200 + 300 + 150 + 250 + 100.
- Current savings: 500; goal: 12,000; period: 6 months; planned monthly savings: 1,800.
- Monthly income: 1,500 × 4 = **6,000**.
- Total expenses: **1,600**.
- Available money: 6,000 − 1,600 = **4,400**.
- Required monthly savings: (12,000 − 500) ÷ 6 = **1,916.6666666666667** before display formatting.
- Expected savings: 500 + (1,800 × 6) = **11,300**.
- Status: **YELLOW / NEEDS ADJUSTMENT**. The expected savings is 11,300, which is at least 80% of the 12,000 goal (9,600), but it does not reach the full goal.
- Displayed required monthly savings: **1,916.67**. This is formatted for display; it is not used as the rounded calculation value.

## 6. Function and method reviewer

### JavaScript: `procedural-js/app.js`

| Function or section | Parameters | Returns / effect | How it is used |
|---|---|---|---|
| `readNumber(input, field, allowEmpty)` | Input object, field name, optional expense flag | A validated JavaScript number; throws an error for invalid input | Called by `processAssessment` for every numeric input. |
| `processAssessment(input)` | Plain object containing the form values | The complete assessment result object | Called by the browser submit handler and by the Node.js command-line block. |
| `showResult(result)` | Assessment result object | Adds result rows and status text to the page | Called after the browser version calculates successfully. |
| `formatMoney(amount)` | A calculated or entered money value | A localized string with two decimal places | Called by `showResult`; this formats display only. |
| Browser submit handler | Browser submit event | Calculates, displays an error, or shows the result | Reads `FormData`, calls `processAssessment`, and then calls `showResult`. |
| Node.js entry block | Optional JSON command-line argument | Prints JSON; invalid input sets a non-zero exit code | Runs only when `app.js` is the Node.js entry point. |

### Python: `oop-python/oop_system.py` and `oop-python/app.py`

| Class method or route | Parameters | Returns / effect | How it is used |
|---|---|---|---|
| `SavingsAssessmentSystem.__init__(assessment_input)` | Assessment dictionary | Creates an object with validated instance attributes; raises `ValueError` if invalid | Created by the Flask route, tests, or sample block. |
| `_read_text(value, default)` | A value and fallback text | Trimmed text or the fallback | Called by the constructor for the name and goal purpose. |
| `_read_number(assessment_input, field, allow_empty)` | Input dictionary, field name, optional-expense flag | Validated `float`; raises `ValueError` on invalid values | Called by the constructor for all amount and month fields. |
| `calculate_monthly_income()` | `self` | Estimated monthly income | Called by `process()`. |
| `calculate_total_expenses()` | `self` | Sum of the six expenses | Called by `process()`. |
| `calculate_required_monthly_savings()` | `self` | Required monthly saving amount, or zero when no remainder is due | Called by `process()`. |
| `calculate_expected_savings()` | `self` | Current savings plus the planned saving over the period | Called by `process()`. |
| `assess_goal(available_money, required_savings, expected_savings)` | `self` and the calculated amounts | `GREEN`, `YELLOW`, or `RED` | Called by `process()`. |
| `recommendation_for(status)` | A status string | Matching recommendation text | Called by `process()`. It is a static method, so it does not need `self`. |
| `process()` | `self` | Dictionary with all assessment output fields | Calls the calculation methods in order and creates the result. |
| Flask `index()` route | Flask request | Rendered HTML page | Called for `GET /`. |
| Flask `process_assessment()` route | Flask request and its JSON body | JSON result, or a readable `400` validation error | Called for `POST /api/assessment`; it uses the class and stores the dated result. |

`self` means the current `SavingsAssessmentSystem` object. The constructor's `self.monthly_allowance`, `self.expenses`, and other `self.*` values are instance attributes: each object keeps its own validated inputs. A standalone function is called by its function name; a method is called through an object and can read that object's attributes.

## 7. Similarities and differences

| Topic | JavaScript Procedural | Python OOP | Same | Different |
|---|---|---|---|---|
| Language | JavaScript | Python | Both are general-purpose programming languages. | Syntax, runtime, and browser/server roles differ. |
| Approach | Standalone functions and a calculation sequence in `app.js` | `SavingsAssessmentSystem` organizes input and behavior | Both execute the same assessment rules. | One groups calculations as functions; the other groups them as class methods. |
| Entry point | Browser loads `procedural-js/index.html`; Node can run `procedural-js/app.js` | `oop-python/app.py` starts Flask | Both can calculate independently. | JS can run directly in a browser; Python's web UI needs Flask. |
| Processing | Form handler → `processAssessment` → result display | Flask route → object constructor → `process()` → JSON response → display | Values are validated before the result is shown. | Python passes through an HTTP route and object; JS calls a function in the page. |
| Functions and methods | `readNumber`, `processAssessment`, `showResult`, `formatMoney` | Constructor and methods on `SavingsAssessmentSystem` | Both use named units of work. | Python calculation methods belong to a class; JS functions are standalone. |
| Data storage | Ordinary variables and a plain input/result object | Local variables plus instance attributes | Each stores numbers, strings, and the result fields. | JS does not store assessment history; Python saves dated results to JSON. |
| Validation | `readNumber` in `app.js` | `_read_number` in `oop_system.py` | Both allow cents, reject invalid/negative amounts, and require whole positive months. | Each language has its own implementation; tests compare their behavior. |
| Formulas | In `processAssessment` | In `calculate_*` and `assess_goal` methods | Same formulas and status thresholds. | Code organization differs. |
| Error handling | Throws `Error`; form handler displays its message | Raises `ValueError`; Flask returns HTTP 400 JSON | Invalid input does not create a normal result. | Browser event and HTTP response mechanisms differ. |
| Result | JavaScript object displayed on the page | Python dictionary returned as JSON and displayed | Same calculation fields and meanings. | Python also stores a dated record. |
| Interface | Local HTML, CSS, and browser JavaScript | Flask template, CSS, and a form script | Purple theme and field labels are shared. | Python template uses Flask static-file URLs. |
| Execution | Open HTML locally or run JS with Node | Start Flask, then open localhost | Both have explicit run/test commands. | Flask uses port 5000; local JS does not need that server. |
| Testing | `verify_systems.py` runs actual Node calculator | Same test file runs actual Python class and Flask test client | Tests compare corresponding outputs and invalid messages. | Tests use a Node subprocess for JS and Python imports/client for Python. |
| Maintenance | Calculation sequence is easy to follow in one function | Related data and methods are grouped in a class | Both avoid advanced frameworks for calculations. | Changes are made in separate language files, then verified for parity. |

The implementations do not share calculation code. Their internal structures can differ while their validated inputs, calculation values, statuses, and result fields remain equivalent.

## 8. Tests and verification

Run `tests/verify_systems.py` from the SaveSmart folder. Its tests exercise the actual `SavingsAssessmentSystem` class and the actual Node.js `processAssessment` entry point with equivalent JSON inputs. The Flask test client checks the Python page, static files, API result, validation response, and saved record using a temporary file rather than changing the project's real records.

The current test set covers:

- The shared sample and a second valid assessment with different decimal amounts.
- Weekly, every-two-weeks, monthly, and the existing unknown-frequency monthly fallback.
- Matching `GREEN`, `YELLOW`, and `RED` results.
- All-zero allowed amounts, a goal already reached, and blank/missing optional expenses.
- Blank or missing required values, negative amounts, zero/fractional months, invalid numeric text, and money with more than two decimal places.
- Matching form field names, required fields, non-negative minimums, currency spinner steps of `0.01`, and whole-month steps of `1`.
- Flask page and static-file loading, successful and invalid API requests, and assessment-file writing.

No test can prove all possible user behavior. These tests specifically verify equivalent results and validation for the cases above.

## 9. Defense questions and short answers

1. **What is SaveSmart?** A small assessment program that compares a student's income, expenses, savings goal, and plan to produce a savings status.
2. **What problem does it address?** It helps a student estimate whether their planned saving could reach a target in a chosen number of months.
3. **Why use two languages?** The project demonstrates two implementations of the same rules: JavaScript Procedural and Python OOP.
4. **What is procedural programming?** Organizing a program as steps and functions that operate on input values. `procedural-js/app.js` follows this style.
5. **What is OOP?** Organizing related data and behavior into classes and objects. `SavingsAssessmentSystem` in `oop-python/oop_system.py` demonstrates this.
6. **Why is the JavaScript version procedural?** Its standalone `processAssessment` function coordinates calculation steps; it does not put them in a class.
7. **Why is the Python version OOP?** The class stores validated input in instance attributes and uses methods such as `calculate_monthly_income` and `process`.
8. **What is the difference between a function and a method?** A function stands on its own; a method belongs to a class and is usually called through an object.
9. **What is a class?** A definition for the related attributes and methods used by `SavingsAssessmentSystem`.
10. **What is an object?** A particular instance created by calling `SavingsAssessmentSystem(assessment_input)`.
11. **What is an attribute?** A value stored on an object, such as `self.savings_goal`.
12. **What does `self` mean?** It refers to the current Python object, allowing its methods to access that object's attributes.
13. **What does `__init__` do?** It runs when the object is created; here it validates the input and sets attributes.
14. **Where does each program start?** The browser opens `procedural-js/index.html` (or Node runs `procedural-js/app.js`); Python runs `oop-python/app.py`.
15. **Where is input validation?** JavaScript uses `readNumber` and `processAssessment` in `procedural-js/app.js`; Python uses `_read_number` in `oop-python/oop_system.py`.
16. **Where is the savings requirement calculated?** JavaScript calculates it in `processAssessment`; Python uses `calculate_required_monthly_savings`.
17. **How is weekly allowance converted?** Multiply it by four in JavaScript `processAssessment` or Python `calculate_monthly_income`.
18. **How are expenses handled?** The six expenses are added; an omitted or blank expense becomes zero.
19. **How are planned savings used?** Expected savings equals current savings plus planned monthly savings times months.
20. **What happens to a negative money amount?** Both validators reject it and return a field-specific message.
21. **What happens if a required amount is blank?** The calculator rejects it; the JS page shows its validation message and Flask returns a 400 validation response.
22. **Why should results match?** The tests send the same input to both real calculators and compare the complete result dictionaries/objects.
23. **Why does the code look different?** It demonstrates standalone procedural functions versus Python methods and object attributes.
24. **What if a calculation method is removed?** Python `process()` can no longer call it and will fail; removing the corresponding JS logic changes or breaks its result.
25. **How do you know both implementations work?** The current automated tests compare valid results, status boundaries, and validation failures; tests reduce risk but cannot prove every case.
26. **How were they tested?** `tests/verify_systems.py` runs Node, calls the Python class, exercises Flask with a test client, and compares results.
27. **What is Flask for?** It serves the Python template and handles the `/api/assessment` HTTP request.
28. **What do HTML and CSS do?** HTML describes the form and result area; CSS controls their appearance.
29. **How does execution differ?** JavaScript can calculate directly in the browser; Python uses Flask for its web page and API.
30. **What would you improve later?** I would first confirm new requirements, add matching tests for them, and then implement them separately in both calculators.
31. **What does `readNumber` return?** A finite, non-negative number with at most two decimal places, or zero for an optional blank expense; otherwise it throws an error.
32. **Why is `savingPeriod` different from money?** It counts months, so both validators require an integer greater than zero and both HTML controls use `step="1"`.
33. **Why are currency spinner steps `0.01`?** Money inputs allow cents; one spinner click changes the amount by one cent.
34. **What does `availableMoney` mean?** Estimated monthly income minus the sum of the monthly expense fields.
35. **When is a result YELLOW?** Only after GREEN fails: available money must be positive and at least one of the two 80% checks must pass.
36. **Does the assessment round before choosing status?** No. Calculations and comparisons use the unrounded values; `formatMoney` only formats what the user sees.
37. **What is the role of the Python page's `static/app.js`?** It sends form values to Flask and displays the returned result; Python performs the calculations.
38. **Does the JavaScript system need Flask?** No. Its form and calculations run in the browser; Node is optional for command-line running and tests.
39. **Where are Python results saved?** The Flask route appends a dated record to `data/assessments.json`.
40. **What happens with a blank optional expense?** `readNumber` or `_read_number` returns zero, so it does not increase total expenses.

## 10. Live coding practice

Practice on a copy or make one small edit at a time. Before a removal exercise, save the original text or rely on VS Code **Undo** immediately; run the test command only after restoring the code.

| Exercise | File and section | What to explain | If temporarily removed | Safe restore and test |
|---|---|---|---|---|
| Find JavaScript validation | `procedural-js/app.js`, `readNumber` | Required numeric values, zero, cents, negatives, and the month rule | `processAssessment` cannot get validated numbers | Undo, then run `node procedural-js\app.js` and the test suite. |
| Find the JS input sequence | `procedural-js/app.js`, `processAssessment` | How inputs become calculations and result fields | The form and Node entry point cannot create the result | Undo and run `tests\verify_systems.py`. |
| Find the Python constructor | `oop-python/oop_system.py`, `SavingsAssessmentSystem.__init__` | How input gets checked and stored in `self.*` | Object creation fails or has missing attributes | Undo and run the tests. |
| Find one Python formula | `oop-python/oop_system.py`, `calculate_required_monthly_savings` | Remaining goal divided by months; zero if already reached | `process()` fails when it calls the method | Undo and run the tests. |
| Find the status condition | `procedural-js/app.js`, `processAssessment`; Python `assess_goal` | GREEN checks, then YELLOW 80% checks, otherwise RED | Status can be missing or incorrect | Undo and run the GREEN/YELLOW/RED test. |
| Find the Flask route | `oop-python/app.py`, `process_assessment` | JSON in, class object, result JSON and saved record out | The Python form receives no assessment response | Undo and run the Flask API test. |
| Find the form connection | Both `index.html` files and their page scripts | Input `name` values match calculator keys | Missing or renamed fields fail validation | Undo, compare input names with the form-parity test, then run the suite. |
| Find result formatting | `procedural-js/app.js`, `showResult` and `formatMoney`; Python `static/app.js`, `showResult` | Result values become visible labels and two-decimal strings | The calculation may run but no complete result is displayed | Undo and submit the sample through each interface. |

## 11. Short oral defense script

> SaveSmart estimates whether a student could reach a savings goal based on their allowance, expenses, current savings, saving period, and planned monthly savings. I made two independent versions using the same assessment rules.
>
> The JavaScript Procedural version is in `procedural-js`. Its form handler reads the values, `processAssessment` validates and calculates them, and `showResult` displays the output.
>
> The Python OOP version is in `oop-python`. Flask serves the page and receives its form request. The route creates a `SavingsAssessmentSystem` object. The class stores the validated values in instance attributes, and its methods calculate income, expenses, savings, and status.
>
> The calculations use the same formulas in both languages. The tests run the actual JavaScript and Python calculation code on equivalent inputs and compare their output fields and validation behavior. Money accepts cents; calculations keep their full numeric values, and the page formats displayed money to two decimal places.

## 12. Known limits to explain honestly

- Weekly income is estimated as four allowance payments per month; every-two-weeks income is estimated as two. These are the project's existing rules, not a calendar-day average.
- An unrecognized allowance-frequency value follows the monthly default. The forms themselves offer only the three supported choices.
- The Python app appends assessment results to a local JSON file; the JavaScript page does not persist them.
- Flask is run as a local development app on port 5000, not as a production-hosted service.
- The result is an estimate based on user-entered values, not financial advice.
