from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, inch
from reportlab.lib import colors

from .models import DerivativeTrades, Insertions, Removals, Edits

def renderReport(buffer, reportName, date):
    width, height = A4

    # Styles
    styleHeading1 = getSampleStyleSheet()["Heading1"]
    styleHeading2 = getSampleStyleSheet()["Heading2"]
    styleSmall = ParagraphStyle(
        "Small",
        parent = getSampleStyleSheet()["Normal"],
        fontSize = 8,
        leading = 8,
    )
    doc = SimpleDocTemplate(buffer)

    S = [].append

    #Title
    S(Paragraph(reportName[:-4], style = styleHeading1))

    # Insertions
    S(Paragraph("Inserted Trades", style = styleHeading2))
    
    # Add headers to the data
    data = []
    data.append((Paragraph("ID", style = styleSmall),
                    Paragraph("Date", style = styleSmall),
                    Paragraph("Prod", style = styleSmall),
                    Paragraph("Buyer", style = styleSmall),
                    Paragraph("Seller", style = styleSmall),
                    Paragraph("NAmnt", style = styleSmall),
                    Paragraph("NCur", style = styleSmall),
                    Paragraph("Qty", style = styleSmall),
                    Paragraph("MDate", style = styleSmall),
                    Paragraph("UPr", style = styleSmall),
                    Paragraph("UCur", style = styleSmall),
                    Paragraph("SPr", style = styleSmall)))

    # Populate the data array with the trades
    for trade in DerivativeTrades.objects.filter(date__date = date).order_by("date"):
        data.append((Paragraph(trade.trade_id, style = styleSmall), 
                        Paragraph(str(trade.date), style = styleSmall), 
                        Paragraph(trade.product, style = styleSmall), 
                        Paragraph(str(trade.buying_party), style = styleSmall), 
                        Paragraph(str(trade.selling_party), style = styleSmall), 
                        Paragraph(str(trade.notional_amount), style = styleSmall), 
                        Paragraph(trade.notional_currency, style = styleSmall), 
                        Paragraph(str(trade.quantity), style = styleSmall), 
                        Paragraph(str(trade.maturity_date), style = styleSmall), 
                        Paragraph(str(trade.underlying_price), style = styleSmall), 
                        Paragraph(trade.underlying_currency, style = styleSmall), 
                        Paragraph(str(trade.strike_price), style = styleSmall)))
    
    # Specify a table filled with the data.
    cw = (width - (2 * inch)) / 12
    table = Table(data, colWidths=[cw, cw*1.07, cw*1.07, cw*1.07, cw*1.07, cw*1.07, cw*0.85, cw*0.95, cw, cw, cw*0.85, cw])
    table.setStyle(TableStyle([
                       ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                       ]))
    S(table)

    # Expirations
    S(Paragraph("Expired Trades", style = styleHeading2))

    # Add headers to the data
    data = []
    data.append((Paragraph("ID", style = styleSmall),
                    Paragraph("Date", style = styleSmall),
                    Paragraph("Prod", style = styleSmall),
                    Paragraph("Buyer", style = styleSmall),
                    Paragraph("Seller", style = styleSmall),
                    Paragraph("NAmnt", style = styleSmall),
                    Paragraph("NCur", style = styleSmall),
                    Paragraph("Qty", style = styleSmall),
                    Paragraph("MDate", style = styleSmall),
                    Paragraph("UPr", style = styleSmall),
                    Paragraph("UCur", style = styleSmall),
                    Paragraph("SPr", style = styleSmall)))

    # Populate the data array with the trades
    for trade in DerivativeTrades.objects.filter(maturity_date__date = date).order_by("date"):
        data.append((Paragraph(trade.trade_id, style = styleSmall), 
                        Paragraph(str(trade.date), style = styleSmall), 
                        Paragraph(trade.product, style = styleSmall), 
                        Paragraph(str(trade.buying_party), style = styleSmall), 
                        Paragraph(str(trade.selling_party), style = styleSmall), 
                        Paragraph(str(trade.notional_amount), style = styleSmall), 
                        Paragraph(trade.notional_currency, style = styleSmall), 
                        Paragraph(str(trade.quantity), style = styleSmall), 
                        Paragraph(str(trade.maturity_date), style = styleSmall), 
                        Paragraph(str(trade.underlying_price), style = styleSmall), 
                        Paragraph(trade.underlying_currency, style = styleSmall), 
                        Paragraph(str(trade.strike_price), style = styleSmall)))
    
    # Specify a table filled with the data.
    cw = (width - (2 * inch)) / 12
    table = Table(data, colWidths=[cw, cw*1.07, cw*1.07, cw*1.07, cw*1.07, cw*1.07, cw*0.85, cw*0.95, cw, cw, cw*0.85, cw])
    table.setStyle(TableStyle([
                       ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                       ]))
    S(table)

    # Edits
    S(Paragraph("Edited Trades", style = styleHeading2))

    # Add headers to the data
    data = []
    data.append((Paragraph("User", style = styleSmall),
                    Paragraph("Trade", style = styleSmall),
                    Paragraph("Date", style = styleSmall),
                    Paragraph("Field", style = styleSmall),
                    Paragraph("Old Value", style = styleSmall),
                    Paragraph("New Value", style = styleSmall)))

    # Populate the data array with the trades
    for edit in Edits.objects.filter(date__date = date).order_by("date"):
        data.append((Paragraph(edit.user, style = styleSmall), 
                        Paragraph(edit.trade, style = styleSmall), 
                        Paragraph(str(edit.date), style = styleSmall), 
                        Paragraph(str(edit.field), style = styleSmall), 
                        Paragraph(str(edit.old_value), style = styleSmall), 
                        Paragraph(str(edit.new_value), style = styleSmall)))
    
    # Specify a table filled with the data.
    cw = (width - (2 * inch)) / 6
    table = Table(data, colWidths=[cw, cw, cw, cw, cw, cw])
    table.setStyle(TableStyle([
                       ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                       ]))
    S(table)

    # Deletions
    S(Paragraph("Deleted Trades", style = styleHeading2))

    # Add headers to the data
    data = []
    data.append((Paragraph("User", style = styleSmall),
                    Paragraph("Trade", style = styleSmall),
                    Paragraph("Date", style = styleSmall)))

    # Populate the data array with the trades
    for removal in Removals.objects.filter(date__date = date).order_by("date"):
        data.append((Paragraph(edit.user, style = styleSmall), 
                        Paragraph(edit.trade, style = styleSmall), 
                        Paragraph(str(edit.date), style = styleSmall)))
    
    # Specify a table filled with the data.
    cw = (width - (2 * inch)) / 3
    table = Table(data, colWidths=[cw, cw, cw])
    table.setStyle(TableStyle([
                       ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                       ]))
    S(table)

    doc.build(S.__self__)