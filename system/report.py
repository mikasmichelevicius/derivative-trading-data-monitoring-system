from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .models import DerivativeTrades

def renderReport(buffer, reportName, date):
    styleNormal = getSampleStyleSheet()["Normal"]
    styleHeading1 = getSampleStyleSheet()["Heading1"]
    styleHeading2 = getSampleStyleSheet()["Heading2"]
    doc = SimpleDocTemplate(buffer)
    S = [].append
    S(Paragraph(reportName[:-4], style = styleHeading1))

    # Insertions
    S(Paragraph("Inserted Trades", style = styleHeading2))
    for trade in DerivativeTrades.objects.order_by("-date"):
        S(Paragraph(trade.trade_id, style = styleNormal))

    # Expirations
    S(Paragraph("Expired Trades", style = styleHeading2))

    # Edits
    S(Paragraph("Edited Trades", style = styleHeading2))

    # Deletions
    S(Paragraph("Deleted Trades", style = styleHeading2))

    doc.build(S.__self__)