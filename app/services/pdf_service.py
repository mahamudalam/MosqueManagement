import os
import calendar
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


class PDFService:


    @staticmethod
    def generate_monthly_report(report, pdf_path):

    

        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        doc = SimpleDocTemplate(
            pdf_path,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        styles = getSampleStyleSheet()

    # -------------------------------------------------------
    # Styles
    # -------------------------------------------------------

        title_style = styles["Heading1"]
        title_style.alignment = TA_CENTER
        title_style.textColor = colors.darkblue
        title_style.fontSize = 22
        title_style.leading = 28

        masjid_style = styles["Heading2"]
        masjid_style.alignment = TA_CENTER
        masjid_style.textColor = colors.darkgreen
        masjid_style.fontSize = 16

        report_style = styles["BodyText"]
        report_style.alignment = TA_CENTER
        report_style.fontSize = 11

        footer_style = styles["Italic"]
        footer_style.alignment = TA_CENTER
        footer_style.fontSize = 9

        month_name = calendar.month_name[report.report_month]

        elements = []

    # -------------------------------------------------------
    # Title
    # -------------------------------------------------------

        elements.append(
            Paragraph(
                "MASJID MONTHLY FINANCIAL REPORT",
                title_style
            )
        )

        elements.append(
            Paragraph(
                "<b>Durga Nagar Masjid</b>",
                masjid_style
            )
        )

        elements.append(Spacer(1, 0.08 * inch))

        elements.append(
            Paragraph(
                f"<b>Report Period:</b> {month_name} {report.report_year}",
                report_style
            )
        )

        elements.append(Spacer(1, 0.10 * inch))

    # -------------------------------------------------------
    # Green separator line
    # -------------------------------------------------------

        line = Table(
          [[""]],
            colWidths=[7 * inch]
        )

        line.setStyle(
            TableStyle([
                ("LINEBELOW", (0, 0), (-1, -1), 2, colors.darkgreen)
            ])
        )

        elements.append(line)

        elements.append(Spacer(1, 0.25 * inch))

    # -------------------------------------------------------
    # Financial Table
    # -------------------------------------------------------

        data = [

            ["Description", "Amount (INR)"],

            ["Opening Balance", f"{report.opening_balance:,.2f}"],

             ["Friday Contribution", ""],
            ["• Cash Collection", f"{report.friday_money_contribution:,.2f}"],
            ["• Jumma Namaz Collection", f"{report.friday_jumma_namaz_contribution:,.2f}"],
            ["• Rice Collection", f"{report.friday_rice_contribution:,.2f}"],

            ["General Contribution", f"{report.general_contribution:,.2f}"],

            ["Imam Contribution", f"{report.imam_contribution:,.2f}"],

            ["Total Income", f"{report.total_income:,.2f}"],

            ["Total Expense", f"{report.total_expense:,.2f}"],

            ["Closing Balance", f"{report.closing_balance:,.2f}"]

        ]

        table = Table(
            data,
            colWidths=[4.7 * inch, 2.0 * inch]
        )

        table.setStyle(
            TableStyle([

                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

                ("GRID", (0, 0), (-1, -1), 1, colors.grey),

                ("BACKGROUND", (0, 1), (-1, -2), colors.beige),
                ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),

                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 8),

                # ===== Bold Rows =====
                ("FONTNAME", (0, 2), (1, 2), "Helvetica-Bold"),   # Friday Contribution
                ("FONTNAME", (0, 8), (1, 8), "Helvetica-Bold"),   # Total Income
                ("FONTNAME", (0,10), (1,10), "Helvetica-Bold"),   # Closing Balance

                # Optional: Gray background for heading rows
                ("BACKGROUND", (0, 2), (-1, 2), colors.whitesmoke),
                ("BACKGROUND", (0, 8), (-1, 8), colors.lightgrey),
                ("BACKGROUND", (0,10), (-1,10), colors.lightgrey),

            ])
        )

        elements.append(table)

        elements.append(Spacer(1, 0.40 * inch))

    # -------------------------------------------------------
    # Footer
    # -------------------------------------------------------

        generated = datetime.now().strftime("%d-%b-%Y %I:%M %p")

        elements.append(

            Paragraph(

                f"Generated on: {generated}<br/><br/>"
                "This report is system generated by "
                "<b>Durga Nagar Masjid Management System</b>.",

                footer_style

            )

        )

        doc.build(elements)

        return pdf_path