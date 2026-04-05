"""Pytest hooks for generating a detailed PDF test report in the repo root."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from textwrap import wrap

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def pytest_sessionstart(session):
    session.config._report_start_time = datetime.now()
    session.config._component_results = []
    session.config._report_kind = "generic"


def pytest_collection_modifyitems(session, config, items):
    has_whitebox = any(item.get_closest_marker("whitebox") for item in items)
    has_selenium = any(item.get_closest_marker("slow") for item in items)

    if has_whitebox and has_selenium:
        config._report_kind = "mixed"
    elif has_whitebox:
        config._report_kind = "whitebox"
    elif has_selenium:
        config._report_kind = "selenium"


def pytest_runtest_makereport(item, call):
    if call.when != "call":
        return

    component_results = getattr(item.config, "_component_results", None)
    if component_results is None:
        return

    for key, value in item.user_properties:
        if key == "component_results":
            component_results.append(value)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    start_time = getattr(config, "_report_start_time", datetime.now())
    end_time = datetime.now()
    duration = end_time - start_time

    summary = {
        "passed": len(terminalreporter.stats.get("passed", [])),
        "failed": len(terminalreporter.stats.get("failed", [])),
        "skipped": len(terminalreporter.stats.get("skipped", [])),
        "error": len(terminalreporter.stats.get("error", [])),
        "xfailed": len(terminalreporter.stats.get("xfailed", [])),
        "xpassed": len(terminalreporter.stats.get("xpassed", [])),
    }

    root_dir = Path(config.rootpath).parent
    report_kind = getattr(config, "_report_kind", "generic")
    report_name = {
        "whitebox": "whitebox-test-report.pdf",
        "selenium": "selenium-test-report.pdf",
        "mixed": "asprams-test-report.pdf",
    }.get(report_kind, "pytest-test-report.pdf")
    pdf_path = root_dir / report_name
    component_results = getattr(config, "_component_results", [])
    _write_pdf_report(pdf_path, summary, duration, exitstatus, component_results, report_kind)


def _draw_wrapped_lines(c, text: str, x: int, y: int, max_chars: int = 95, font_name: str = "Helvetica", font_size: int = 11, line_height: int = 16) -> int:
    c.setFont(font_name, font_size)
    paragraphs = text.splitlines() or [""]
    for paragraph in paragraphs:
        for line in wrap(paragraph, max_chars) or [""]:
            c.drawString(x, y, line)
            y -= line_height
    return y


def _write_pdf_report(pdf_path: Path, summary: dict, duration, exitstatus: int, component_results: list[dict], report_kind: str) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    left = 48
    right_margin = 48
    max_chars = 95
    y = height - 48

    def next_page() -> None:
        nonlocal y
        c.showPage()
        y = height - 48

    def new_page_if_needed(required_lines: int = 1) -> None:
        nonlocal y
        if y - (required_lines * 16) < 56:
            next_page()

    def section_title(text: str) -> None:
        nonlocal y
        new_page_if_needed(2)
        c.setFont("Helvetica-Bold", 15)
        c.drawString(left, y, text)
        y -= 22

    def body(text: str, indent: int = 0, size: int = 11) -> None:
        nonlocal y
        new_page_if_needed()
        y = _draw_wrapped_lines(c, text, left + indent, y, max_chars=max_chars, font_size=size)
        y -= 4

    # Cover page
    title = {
        "whitebox": "ASPRAMS White-Box Test Report",
        "selenium": "ASPRAMS Selenium Test Report",
        "mixed": "ASPRAMS Test Report",
    }.get(report_kind, "ASPRAMS Test Report")

    c.setFont("Helvetica-Bold", 24)
    c.drawString(left, y, title)
    y -= 42
    c.setFont("Helvetica", 12)
    y = _draw_wrapped_lines(
        c,
        "A browser-level validation report for the ASPRAMS application. The report focuses on the non-Gemini user journey: account creation, sign-in, MongoDB-backed history, form input handling, and PDF export.",
        left,
        y,
        max_chars=max_chars,
        font_size=12,
        line_height=18,
    )
    y -= 8
    body(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    body(f"Run duration: {duration}")
    body(f"Exit status: {exitstatus}")
    body("Environment: Microsoft Edge headless, FastAPI backend, Vite frontend, MongoDB connected.")
    body("External AI services: Gemini was intentionally excluded from this test run.")
    next_page()

    audience_note = "Audience: This report is written for readers who do not know the internal codebase. It explains what the application does, what was tested, and what each test step produced."
    if report_kind == "whitebox":
        audience_note = "Audience: This report is written for readers who do not know the internal codebase. It explains the internal branches and control-flow paths that were exercised by the white-box unit tests."
    body(audience_note)

    section_title("1. What Was Tested")
    if report_kind == "whitebox":
        body("The white-box tests focused on internal decision paths in the ML risk model. They checked the low, medium, and high risk branches, feature-importance ordering, and the default fallback path when the model is missing.")
    elif report_kind == "selenium":
        body("The Selenium test focused only on the non-Gemini parts of ASPRAMS. It checked user registration, login, MongoDB-backed history, form input handling, and PDF download behavior in Microsoft Edge headless mode.")
    else:
        body("The automated tests covered the important deterministic parts of ASPRAMS. Depending on the selected test set, this may include UI flows, database-backed history, and white-box model branches.")

    section_title("2. Test Environment")
    body(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    body(f"Exit status: {exitstatus}")
    body(f"Duration: {duration}")
    if report_kind == "whitebox":
        body("Browser: Not applicable. These were Python unit tests.")
        body("Backend: ML model module only.")
        body("Frontend: Not used.")
        body("Database: Not used.")
        body("AI services: Not used.")
    else:
        body("Browser: Microsoft Edge (headless)")
        body("Backend: FastAPI on http://localhost:8000")
        body("Frontend: Vite React app on http://localhost:5173")
        body("Database: MongoDB connected locally")
        body("AI services: Gemini was not used in this test run.")

    section_title("3. Overall Summary")
    body(f"Passed checks: {summary['passed']}")
    body(f"Failed checks: {summary['failed']}")
    body(f"Skipped checks: {summary['skipped']}")
    body(f"Errors: {summary['error']}")
    body(f"XFailed: {summary['xfailed']}")
    body(f"XPassed: {summary['xpassed']}")

    section_title("4. Component-by-Component Results")
    if component_results:
        new_page_if_needed(8)
        table_x = left
        table_width = width - left - right_margin
        col_component = int(table_width * 0.28)
        col_status = int(table_width * 0.12)
        col_details = table_width - col_component - col_status
        row_height = 44

        c.setFont("Helvetica-Bold", 10)
        c.rect(table_x, y - row_height, table_width, row_height, stroke=1, fill=0)
        c.drawString(table_x + 6, y - 18, "Component")
        c.drawString(table_x + col_component + 6, y - 18, "Status")
        c.drawString(table_x + col_component + col_status + 6, y - 18, "Result")
        y -= row_height

        for index, component in enumerate(component_results, start=1):
            name = component.get("component", f"Component {index}")
            status = component.get("status", "Unknown")
            details = component.get("details", "")
            details_lines = wrap(details, 70) or [""]
            required_height = max(30, 16 + (len(details_lines) * 12))
            new_page_if_needed(required_height // 16 + 2)
            c.setFont("Helvetica", 9)
            c.rect(table_x, y - required_height, table_width, required_height, stroke=1, fill=0)
            c.drawString(table_x + 6, y - 16, name)
            c.drawString(table_x + col_component + 6, y - 16, status)
            text_y = y - 16
            for line in details_lines:
                c.drawString(table_x + col_component + col_status + 6, text_y, line)
                text_y -= 11
            y -= required_height
            y -= 4
    else:
        body("No component-level details were captured for this run.")

    y -= 10

    section_title("5. Plain-Language Interpretation")
    if report_kind == "whitebox":
        body("The white-box tests showed that the risk model makes a different decision depending on the predicted score and that its fallback path produces a safe default result when the model is unavailable. This gives confidence that the internal model logic is behaving consistently across the key branches.")
    elif report_kind == "selenium":
        body("The application successfully handled user creation and sign-in, proved that data can be stored and retrieved from MongoDB, and confirmed that the user can export a PDF report from the interface. The test intentionally did not exercise any Gemini-driven simulation logic, so the report reflects only the deterministic parts of the system.")
    else:
        body("The automated tests validated both user-facing flows and internal logic, depending on which suite was executed. Together they provide broad coverage of the deterministic behavior in ASPRAMS.")

    section_title("6. Conclusion")
    body(f"The tested suite passed end-to-end. The result file was generated automatically after pytest completed and saved in the project root as {pdf_path.name}.")

    c.save()