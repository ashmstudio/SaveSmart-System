from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request

try:
    from .oop_system import SavingsAssessmentSystem
except ImportError:
    from oop_system import SavingsAssessmentSystem


PROJECT_DIR = Path(__file__).resolve().parent.parent
ASSESSMENTS_PATH = PROJECT_DIR / "data" / "assessments.json"

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/assessment", methods=["POST"])
def process_assessment():
    assessment_input = request.get_json(silent=True)
    if not isinstance(assessment_input, dict):
        return jsonify({"error": "Please provide assessment information."}), 400

    try:
        result = SavingsAssessmentSystem(assessment_input).process()
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    ASSESSMENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if ASSESSMENTS_PATH.exists():
        with ASSESSMENTS_PATH.open("r", encoding="utf-8") as file:
            assessments = json.load(file)
        if not isinstance(assessments, list):
            raise ValueError("Assessment data must contain a JSON list.")
    else:
        assessments = []

    record = {"date": datetime.now().strftime("%B %d, %Y"), **result}
    assessments.append(record)
    with ASSESSMENTS_PATH.open("w", encoding="utf-8") as file:
        json.dump(assessments, file, indent=2)

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
