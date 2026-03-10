"""Tests for the UBC Workday ICS Flask server."""
import io
import pytest
import openpyxl
from server import app, parse_enrolled_classes
import pandas as pd


# ---------------------------------------------------------------------------
# Sample schedule data matching the Workday Excel export format
# ---------------------------------------------------------------------------
SAMPLE_CLASSES = [
    {
        "Course Listing": "CPSC 110 - Computation, Programs and Programming",
        "Meeting Patterns": "2024-01-08 - 2024-04-15 | Mon Wed Fri | 9:00 AM - 10:00 AM\n",
    },
    {
        "Course Listing": "MATH 200 - Calculus III",
        "Meeting Patterns": "2024-01-08 - 2024-04-15 | Tue Thu | 11:00 AM - 12:30 PM\n",
    },
    {
        "Course Listing": "ENGL 110 - Approaches to Literature and Language",
        "Meeting Patterns": "2024-01-08 - 2024-04-15 | Mon Wed | 2:00 PM - 3:30 PM\n",
    },
    {
        # Row with no meeting pattern (e.g. an online async course) should still appear in /classes
        "Course Listing": "BIOL 111 - Introduction to Modern Biology",
        "Meeting Patterns": float("nan"),
    },
]


def _make_excel_bytes(rows: list[dict]) -> bytes:
    """Build an in-memory Excel file from a list of row dicts."""
    wb = openpyxl.Workbook()
    ws = wb.active
    headers = list(rows[0].keys())
    ws.append(headers)
    for row in rows:
        ws.append([row.get(h) for h in headers])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def excel_bytes():
    return _make_excel_bytes(SAMPLE_CLASSES)


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

class TestParseEnrolledClasses:
    def test_returns_all_courses(self):
        df = pd.DataFrame(SAMPLE_CLASSES, dtype=str)
        result = parse_enrolled_classes(df)
        assert len(result) == 4

    def test_course_names_correct(self):
        df = pd.DataFrame(SAMPLE_CLASSES, dtype=str)
        result = parse_enrolled_classes(df)
        assert "CPSC 110 - Computation, Programs and Programming" in result
        assert "MATH 200 - Calculus III" in result

    def test_empty_dataframe(self):
        df = pd.DataFrame(columns=["Course Listing", "Meeting Patterns"])
        assert parse_enrolled_classes(df) == []


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

class TestIndexEndpoint:
    def test_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_lists_endpoints(self, client):
        data = resp = client.get("/").get_json()
        assert "endpoints" in data
        assert "POST /classes" in data["endpoints"]
        assert "POST /calendar" in data["endpoints"]


class TestClassesEndpoint:
    def test_no_file_returns_400(self, client):
        resp = client.post("/classes")
        assert resp.status_code == 400

    def test_returns_enrolled_classes(self, client, excel_bytes):
        resp = client.post(
            "/classes",
            data={"file": (io.BytesIO(excel_bytes), "schedule.xlsx")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert "enrolled_classes" in body
        assert body["count"] == 4

    def test_enrolled_class_names(self, client, excel_bytes):
        resp = client.post(
            "/classes",
            data={"file": (io.BytesIO(excel_bytes), "schedule.xlsx")},
            content_type="multipart/form-data",
        )
        classes = resp.get_json()["enrolled_classes"]
        assert "CPSC 110 - Computation, Programs and Programming" in classes
        assert "MATH 200 - Calculus III" in classes
        assert "ENGL 110 - Approaches to Literature and Language" in classes
        assert "BIOL 111 - Introduction to Modern Biology" in classes

    def test_invalid_file_returns_422(self, client):
        resp = client.post(
            "/classes",
            data={"file": (io.BytesIO(b"not an excel file"), "bad.xlsx")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 422


class TestCalendarEndpoint:
    def test_no_file_returns_400(self, client):
        resp = client.post("/calendar")
        assert resp.status_code == 400

    def test_returns_ics_content_type(self, client, excel_bytes):
        resp = client.post(
            "/calendar",
            data={"file": (io.BytesIO(excel_bytes), "schedule.xlsx")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 200
        assert "text/calendar" in resp.content_type

    def test_ics_contains_vcalendar(self, client, excel_bytes):
        resp = client.post(
            "/calendar",
            data={"file": (io.BytesIO(excel_bytes), "schedule.xlsx")},
            content_type="multipart/form-data",
        )
        body = resp.data.decode("utf-8")
        assert "BEGIN:VCALENDAR" in body
        assert "END:VCALENDAR" in body
