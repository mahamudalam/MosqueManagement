from io import BytesIO
from datetime import datetime

from flask import send_file
from zoneinfo import ZoneInfo
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def generate_imam_contri_due_pdf(year, report_data, summary):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=f"Imam Due Report - {year}",
        author="Jama Masjid Durga Nagar"
    )

    styles = getSampleStyleSheet()

    # --------------------------------------------------
    # Styles
    # --------------------------------------------------

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=17,
        leading=20,
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=12,
        leading=15,
        spaceAfter=3
    )

    year_style = ParagraphStyle(
        "YearStyle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        leading=13,
        spaceAfter=10
    )

    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=10,
        alignment=TA_CENTER
    )

    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontSize=8,
        leading=10
    )

    member_style = ParagraphStyle(
        "MemberStyle",
        parent=cell_style,
        fontName="Helvetica-Bold"
    )

    count_style = ParagraphStyle(
        "CountStyle",
        parent=cell_style,
        alignment=TA_CENTER
    )

    month_style = ParagraphStyle(
        "MonthStyle",
        parent=styles["Normal"],
        fontSize=7.5,
        leading=9,
        alignment=TA_LEFT
    )

    summary_header_style = ParagraphStyle(
        "SummaryHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        alignment=TA_CENTER
    )

    summary_value_style = ParagraphStyle(
        "SummaryValue",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        alignment=TA_CENTER
    )

    footer_style = ParagraphStyle(
        "FooterStyle",
        parent=styles["Normal"],
        fontSize=7,
        textColor=colors.grey
    )

    story = []

    # ==================================================
    # REPORT HEADER
    # ==================================================

    story.append(
        Paragraph(
            "JAMA MASJID DURGA NAGAR",
            title_style
        )
    )

    story.append(
        Paragraph(
            "IMAM COLLECTION DUE REPORT",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Year:</b> {year}",
            year_style
        )
    )

    # ==================================================
    # SUMMARY
    # ==================================================

    summary_data = [
        [
            Paragraph(
                "Total Members",
                summary_header_style
            ),
            Paragraph(
                "Members With Due",
                summary_header_style
            ),
            Paragraph(
                "Total Due Months",
                summary_header_style
            )
        ],
        [
            Paragraph(
                str(summary["total_members"]),
                summary_value_style
            ),
            Paragraph(
                str(summary["members_with_due"]),
                summary_value_style
            ),
            Paragraph(
                str(summary["total_due_months"]),
                summary_value_style
            )
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            58 * mm,
            58 * mm,
            58 * mm
        ]
    )

    summary_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    story.append(summary_table)

    story.append(Spacer(1, 10))

    # ==================================================
    # MAIN REPORT TABLE
    # ==================================================

    table_data = []

    # Header
    table_data.append([
        Paragraph("#", header_style),
        Paragraph("Member", header_style),
        Paragraph("Due Months", header_style),
        Paragraph("Due Month List", header_style)
    ])

    # --------------------------------------------------
    # Member rows
    # --------------------------------------------------

    for index, member in enumerate(report_data, start=1):

        due_months = member.get("due_months", [])

        # --------------------------------------------------
        # Convert months into inline text.
        #
        # Using Paragraph allows ReportLab to automatically
        # wrap the months if the member has many dues.
        # --------------------------------------------------

        month_text = ""

        for month in due_months:

            if month_text:
                month_text += "&nbsp;&nbsp;&nbsp;"

            month_text += month

        # If there are no months
        if not month_text:
            month_text = "-"

        table_data.append([
            Paragraph(
                str(index),
                cell_style
            ),

            Paragraph(
                member["member_name"],
                member_style
            ),

            Paragraph(
                str(member["due_count"]),
                count_style
            ),

            Paragraph(
                month_text,
                month_style
            )
        ])

    # ==================================================
    # CREATE TABLE
    # ==================================================

    report_table = Table(
        table_data,
        colWidths=[
            10 * mm,     # #
            63 * mm,     # Member
            25 * mm,     # Due Months
            83 * mm      # Due Month List
        ],
        repeatRows=1
    )

    # ==================================================
    # TABLE STYLE
    # ==================================================

    report_table.setStyle(
        TableStyle([

            # Header
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#f2f2f2")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.black
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            # Borders
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#b8b8b8")
            ),

            # Alignment
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "ALIGN",
                (0, 0),
                (0, -1),
                "CENTER"
            ),

            (
                "ALIGN",
                (2, 1),
                (2, -1),
                "CENTER"
            ),

            (
                "ALIGN",
                (1, 1),
                (1, -1),
                "LEFT"
            ),

            (
                "ALIGN",
                (3, 1),
                (3, -1),
                "LEFT"
            ),

            # Padding
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    story.append(report_table)

    # ==================================================
    # NO DATA
    # ==================================================

    if not report_data:

        story.append(
            Spacer(1, 10)
        )

        story.append(
            Paragraph(
                "No Imam contribution dues found.",
                cell_style
            )
        )

    # ==================================================
    # GENERATED TIME
    # ==================================================

    story.append(
        Spacer(1, 10)
    )

    generated_on = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%d-%b-%Y %I:%M %p")

    story.append(
        Paragraph(
            f"Generated On: {generated_on}",
            footer_style
        )
    )
    #generated_on_file = generated_on.strftime("%d-%b-%Y")
    # ==================================================
    # FOOTER / PAGE NUMBER
    # ==================================================

    def add_page_number(canvas, doc):

        canvas.saveState()

        width, height = A4

        canvas.setFont(
            "Helvetica",
            7
        )

        canvas.setFillColor(
            colors.grey
        )

        # Left footer
        canvas.drawString(
            12 * mm,
            7 * mm,
            "Jama Masjid Durga Nagar | Imam Due Report"
        )

        # Right footer
        canvas.drawRightString(
            width - 12 * mm,
            7 * mm,
            f"Page {doc.page}"
        )

        canvas.restoreState()

    # ==================================================
    # BUILD PDF
    # ==================================================

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Imam_Due_Report_{generated_on}.pdf",
        mimetype="application/pdf"
    )