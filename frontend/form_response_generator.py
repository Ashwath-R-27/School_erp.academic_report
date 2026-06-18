"""
PDF Generation module.

Builds the HSC student-details PDF report. Kept separate from the main
Flask app (app.py) so the report-building logic can be developed, tested,
and reused independently of the web routes.
"""

import io
import os
from collections import defaultdict

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak
)

SCHOOL_NAME = "SVGV Matriculation Higher Secondary School, Karamadai"
LOGO_PATH = os.path.join(os.path.dirname(__file__), "static", "logo.avif")

HEADER_BG = colors.HexColor("#1a3c6e")
GROUP_BG = colors.HexColor("#dce6f5")
TABLE_HEAD = colors.HexColor("#1a3c6e")
ALT_ROW = colors.HexColor("#f2f6fc")

# Group display names (covers all groups used in hscgroups())
GROUP_DISPLAY = {
    "csc": "CSC + MATHS",
    "biomat": "BIO + MATHS",
    "biocs": "BIO + CS",
    "artsca": "ARTS (CA)",
    "artsbm": "ARTS (BM)",
    "bme": "BME + MATHS",
}

# Preferred group order inside each class table
GROUP_ORDER = ["csc", "biomat", "biocs", "artsca", "artsbm", "bme"]

PAGE_W, PAGE_H = A4
MARGIN = 10 * mm


def _make_pdf_header(subtitle):
    """
    Returns a page-decoration callback (for SimpleDocTemplate's
    onFirstPage/onLaterPages) that draws the school header with the
    given exam subtitle (e.g. "HSE (+2) Examination", "SSLC Examination").
    """
    def _header(canvas, doc):
        canvas.saveState()

        top = PAGE_H - MARGIN

        # Logo
        logo_w = logo_h = 18 * mm
        if os.path.exists(LOGO_PATH):
            try:
                canvas.drawImage(
                    LOGO_PATH, MARGIN, top - logo_h,
                    width=logo_w, height=logo_h,
                    preserveAspectRatio=True, mask="auto"
                )
            except Exception:
                pass

        # School name
        text_x = MARGIN + logo_w + 4 * mm
        canvas.setFont("Helvetica-Bold", 13)
        canvas.setFillColor(HEADER_BG)
        canvas.drawString(text_x, top - 8 * mm, SCHOOL_NAME)

        # Sub-headings
        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColor(colors.HexColor("#333333"))
        canvas.drawString(text_x, top - 14 * mm, subtitle)
        canvas.drawString(text_x, top - 19 * mm, "Student Details")

        # Horizontal rule
        canvas.setStrokeColor(HEADER_BG)
        canvas.setLineWidth(1.2)
        canvas.line(MARGIN, top - 23 * mm, PAGE_W - MARGIN, top - 23 * mm)

        # Page number
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(PAGE_W - MARGIN, MARGIN - 4 * mm, f"Page {doc.page}")

        canvas.restoreState()

    return _header


_pdf_header = _make_pdf_header("HSE (+2) Examination")
_sslc_pdf_header = _make_pdf_header("SSLC Examination")


def _cell_para(text, alignment=TA_LEFT, bold=False, text_color="black"):
    return Paragraph(
        f"<b>{text}</b>" if bold else text,
        ParagraphStyle(
            "cell",
            fontName="Helvetica-Bold" if bold else "Helvetica",
            fontSize=10,
            alignment=alignment,
            textColor=colors.white if text_color == "white" else (colors.black if text_color == "black" else colors.HexColor(text_color)),
            leading=11,
        )
    )


def build_student_pdf(students, class_counts):
    """
    Build a PDF from a list of student dicts and a class-count dict.
    Returns a BytesIO buffer ready to send.

    students    – list of dicts with keys: reg_no, name, class, dob, group_code
    class_counts – dict like {'A': 6, 'B': 8, ...}
    """
    buffer = io.BytesIO()
    top_padding = 30 * mm

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN + top_padding,
        bottomMargin=MARGIN + 6 * mm,
    )

    class_style = ParagraphStyle(
        "ClassHeader",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=HEADER_BG,
        spaceAfter=2 * mm,
    )
    count_style = ParagraphStyle(
        "CountLine",
        fontName="Helvetica",
        fontSize=12,
        textColor=colors.HexColor("#555555"),
        spaceAfter=3 * mm,
    )

    # Group students by class → group
    by_class = defaultdict(lambda: defaultdict(list))
    for s in students:
        by_class[s["class"]][s["group_code"]].append(s)

    story = []
    col_widths = [15*mm, 65*mm, 45*mm, 29*mm, 29*mm]

    for idx, cls in enumerate(sorted(by_class.keys())):
        if idx > 0:
            story.append(PageBreak())

        story.append(Paragraph(f"XII - {cls}", class_style))

        total = class_counts.get(cls, sum(len(v) for v in by_class[cls].values()))
        story.append(Paragraph(f"No. of Students: {total}", count_style))

        # Table header row
        header_row = [
            _cell_para("S.NO",   TA_CENTER, bold=True, text_color="white"),
            _cell_para("Name",   TA_LEFT,   bold=True, text_color="white"),
            _cell_para("Group",  TA_LEFT,   bold=True, text_color="white"),
            _cell_para("Reg No", TA_CENTER, bold=True, text_color="white"),
            _cell_para("DOB",    TA_CENTER, bold=True, text_color="white"),
        ]
        rows = [header_row]
        span_rows = []   # row indices that should span all columns (group separators)
        row_bgs = {0: TABLE_HEAD}

        sno = 0
        groups_in_class = [g for g in GROUP_ORDER if g in by_class[cls]]
        for g in by_class[cls]:
            if g not in groups_in_class:
                groups_in_class.append(g)

        for grp in groups_in_class:
            grp_students = sorted(by_class[cls][grp], key=lambda s: s["name"])

            # Group separator
            sep_idx = len(rows)
            rows.append([
                _cell_para(GROUP_DISPLAY.get(grp, grp.upper()), TA_LEFT, bold=True, text_color="#1a3c6e"),
                "", "", "", ""
            ])
            span_rows.append(sep_idx)
            row_bgs[sep_idx] = GROUP_BG

            for student in grp_students:
                sno += 1
                row_idx = len(rows)
                row_bgs[row_idx] = ALT_ROW if sno % 2 == 0 else colors.white
                rows.append([
                    _cell_para(str(sno),                                         TA_CENTER),
                    _cell_para(student["name"],                                  TA_LEFT),
                    _cell_para(GROUP_DISPLAY.get(student["group_code"],
                                                 student["group_code"].upper()), TA_LEFT),
                    _cell_para(str(student["reg_no"]),                           TA_CENTER),
                    _cell_para(student["dob"],                                   TA_CENTER),
                ])

        table = Table(rows, colWidths=col_widths, repeatRows=1)

        ts = TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), TABLE_HEAD),
            ("FONTSIZE",     (0, 0), (-1, -1), 9),
            ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#aaaaaa")),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
            ("TOPPADDING",   (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING",(0, 0), (-1, 0), 8),
        ])

        # Apply per-row backgrounds
        for row_idx, bg in row_bgs.items():
            ts.add("BACKGROUND", (0, row_idx), (-1, row_idx), bg)

        # Span group separator rows
        for row_idx in span_rows:
            ts.add("SPAN",     (0, row_idx), (-1, row_idx))
            ts.add("FONTNAME", (0, row_idx), (-1, row_idx), "Helvetica-Bold")

        table.setStyle(ts)
        story.append(table)

    doc.build(story, onFirstPage=_pdf_header, onLaterPages=_pdf_header)
    buffer.seek(0)
    return buffer


def build_sslc_student_pdf(students, class_counts):
    """
    Build the SSLC student-details PDF. Same look and page layout as the
    HSC report, but with no group column/separators since SSLC classes
    have no subject groups. Each class still starts on a fresh page.

    students     – list of dicts with keys: reg_no, name, class, dob
    class_counts – dict like {'A': 40, 'B': 38, ...}
    """
    buffer = io.BytesIO()
    top_padding = 30 * mm

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN + top_padding,
        bottomMargin=MARGIN + 6 * mm,
    )

    class_style = ParagraphStyle(
        "ClassHeader",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=HEADER_BG,
        spaceAfter=2 * mm,
    )
    count_style = ParagraphStyle(
        "CountLine",
        fontName="Helvetica",
        fontSize=12,
        textColor=colors.HexColor("#555555"),
        spaceAfter=3 * mm,
    )

    # Group students by class only (no sub-groups for SSLC)
    by_class = defaultdict(list)
    for s in students:
        by_class[s["class"]].append(s)

    story = []
    # Wider columns than HSC since there's no Group column to fit.
    col_widths = [17*mm, 87*mm, 40*mm, 34*mm]

    for idx, cls in enumerate(sorted(by_class.keys())):
        if idx > 0:
            story.append(PageBreak())

        story.append(Paragraph(f"X - {cls}", class_style))

        total = class_counts.get(cls, len(by_class[cls]))
        story.append(Paragraph(f"No. of Students: {total}", count_style))

        # Table header row
        header_row = [
            _cell_para("S.NO",   TA_CENTER, bold=True, text_color="white"),
            _cell_para("Name",   TA_LEFT,   bold=True, text_color="white"),
            _cell_para("Reg No", TA_CENTER, bold=True, text_color="white"),
            _cell_para("DOB",    TA_CENTER, bold=True, text_color="white"),
        ]
        rows = [header_row]
        row_bgs = {0: TABLE_HEAD}

        cls_students = sorted(by_class[cls], key=lambda s: s["name"])
        for sno, student in enumerate(cls_students, start=1):
            row_idx = len(rows)
            row_bgs[row_idx] = ALT_ROW if sno % 2 == 0 else colors.white
            rows.append([
                _cell_para(str(sno),               TA_CENTER),
                _cell_para(student["name"],         TA_LEFT),
                _cell_para(str(student["reg_no"]),  TA_CENTER),
                _cell_para(student["dob"],          TA_CENTER),
            ])

        table = Table(rows, colWidths=col_widths, repeatRows=1)

        ts = TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), TABLE_HEAD),
            ("FONTSIZE",     (0, 0), (-1, -1), 9),
            ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#aaaaaa")),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
            ("TOPPADDING",   (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING",(0, 0), (-1, 0), 8),
        ])

        for row_idx, bg in row_bgs.items():
            ts.add("BACKGROUND", (0, row_idx), (-1, row_idx), bg)

        table.setStyle(ts)
        story.append(table)

    doc.build(story, onFirstPage=_sslc_pdf_header, onLaterPages=_sslc_pdf_header)
    buffer.seek(0)
    return buffer