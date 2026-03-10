import io
import pandas as pd
from flask import Flask, request, jsonify, send_file
from workday_ics import get_events, get_ics

app = Flask(__name__)


def parse_enrolled_classes(df):
    """Return a list of enrolled class names from the schedule DataFrame."""
    classes = []
    for _, row in df.iterrows():
        course = row.get("Course Listing")
        if pd.isna(course) or course == "":
            continue
        classes.append(str(course).strip())
    return classes


@app.route("/")
def index():
    return jsonify({
        "service": "UBC Workday ICS Server",
        "endpoints": {
            "POST /classes": "Upload an Excel schedule file to list enrolled classes",
            "POST /calendar": "Upload an Excel schedule file to get an ICS calendar file",
        }
    })


@app.route("/classes", methods=["POST"])
def classes():
    """Accept a Workday Excel file and return the list of enrolled classes."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Send the Excel file as 'file' in form-data."}), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    try:
        df = pd.read_excel(f, dtype=str)
    except Exception as e:
        return jsonify({"error": f"Could not parse Excel file: {e}"}), 422

    enrolled = parse_enrolled_classes(df)
    return jsonify({"enrolled_classes": enrolled, "count": len(enrolled)})


@app.route("/calendar", methods=["POST"])
def calendar():
    """Accept a Workday Excel file and return an ICS calendar file."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Send the Excel file as 'file' in form-data."}), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    try:
        df = pd.read_excel(f, dtype=str)
    except Exception as e:
        return jsonify({"error": f"Could not parse Excel file: {e}"}), 422

    events = get_events(df)
    ics_string = get_ics(events, author="UBC Workday ICS Server")
    return send_file(
        io.BytesIO(ics_string.encode("utf-8")),
        mimetype="text/calendar",
        as_attachment=True,
        download_name="schedule.ics",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
