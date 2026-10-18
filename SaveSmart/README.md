# SaveSmart

SaveSmart contains two independent versions of the same savings assessment:

- **JavaScript Procedural:** `procedural-js/` — open `index.html` in a browser.
- **Python OOP:** `oop-python/` — a Flask site using `SavingsAssessmentSystem`.

## Run

Double-click `start_savesmart.bat` and choose JavaScript, Python Flask, or comparison tests.

To start Python from PowerShell at the project root:

```powershell
& ..\.venv\Scripts\python.exe oop-python\app.py
```

Then open http://127.0.0.1:5000. To run the shared comparisons:

```powershell
& ..\.venv\Scripts\python.exe tests\verify_systems.py
```

The Python-only requirements are in `oop-python/requirements.txt`. Install them into the workspace virtual environment if needed:

```powershell
& ..\.venv\Scripts\python.exe -m pip install -r oop-python\requirements.txt
```

The shared `tests/` folder stays at the project root because its tests exercise and compare both implementation folders. The Python app stores its records in `oop-python/data/assessments.json`; the procedural browser page does not save assessment history.

For the complete folder guide, formulas, examples, code walkthrough, test coverage, common mistakes, and defense practice, see [oop-python/DEFENSE_GUIDE.md](oop-python/DEFENSE_GUIDE.md).
