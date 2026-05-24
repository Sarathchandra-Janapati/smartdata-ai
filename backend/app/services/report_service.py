import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from app.services.analytics_service import get_summary, get_kpis, _load_latest_cleaned
from app.core.config import settings

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


def generate_pdf_report(file_path: Optional[str] = None) -> str:
    summary = get_summary(file_path)
    kpis = get_kpis(file_path)

    output_path = str(REPORTS_DIR / f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf")
    doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle("title", parent=styles["Heading1"], fontSize=22, textColor=colors.HexColor("#1a1a2e"), spaceAfter=6)
    story.append(Paragraph("SmartData AI Platform — Analytics Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#4ade80")))
    story.append(Spacer(1, 0.2 * inch))

    # Dataset Summary
    story.append(Paragraph("Dataset Summary", styles["Heading2"]))
    summary_data = [
        ["Metric", "Value"],
        ["Total Records", f"{summary['total_rows']:,}"],
        ["Total Columns", str(summary["total_columns"])],
        ["Numeric Columns", str(summary["numeric_columns"])],
        ["Categorical Columns", str(summary["categorical_columns"])],
        ["Missing Values", str(summary["missing_values"])],
        ["Duplicate Rows", str(summary["duplicate_rows"])],
    ]
    t = Table(summary_data, colWidths=[3 * inch, 3 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2 * inch))

    # KPIs
    story.append(Paragraph("Key Performance Indicators", styles["Heading2"]))
    kpi_data = [["KPI", "Value"]] + [[k.replace("_", " ").title(), str(v)] for k, v in kpis.items()]
    kt = Table(kpi_data, colWidths=[3 * inch, 3 * inch])
    kt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16213e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.lightyellow, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(kt)
    story.append(Spacer(1, 0.2 * inch))

    # Columns list
    story.append(Paragraph("Dataset Columns", styles["Heading2"]))
    cols_text = ", ".join(summary["columns"])
    story.append(Paragraph(cols_text, styles["Normal"]))

    doc.build(story)
    return output_path


def generate_csv_report(file_path: Optional[str] = None) -> str:
    df = _load_latest_cleaned(file_path)
    return df.to_csv(index=False)
