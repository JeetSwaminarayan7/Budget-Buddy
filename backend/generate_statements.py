"""
Generates two realistic UK bank statement PDFs for demo/testing.
Run: python generate_statements.py
Outputs: statement_jan2025.pdf, statement_feb2025.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

W, H = A4

# ── Colour palette ──────────────────────────────────────────────────────────
NAVY   = colors.HexColor("#0f2044")
BLUE   = colors.HexColor("#1a56db")
LGRAY  = colors.HexColor("#f3f4f6")
MGRAY  = colors.HexColor("#d1d5db")
DGRAY  = colors.HexColor("#6b7280")
BLACK  = colors.HexColor("#111827")
RED    = colors.HexColor("#dc2626")
GREEN  = colors.HexColor("#16a34a")
WHITE  = colors.white


def build_pdf(filename, account_name, account_number, sort_code,
              period_label, opening_balance, transactions):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=18*mm,  bottomMargin=18*mm,
    )

    styles = getSampleStyleSheet()

    def style(name, **kw):
        s = ParagraphStyle(name, parent=styles["Normal"], **kw)
        return s

    title_s   = style("title",   fontSize=20, textColor=WHITE,   fontName="Helvetica-Bold", leading=24)
    sub_s     = style("sub",     fontSize=9,  textColor=colors.HexColor("#bfdbfe"), fontName="Helvetica")
    label_s   = style("label",   fontSize=7,  textColor=DGRAY,   fontName="Helvetica",      spaceAfter=1)
    value_s   = style("value",   fontSize=9,  textColor=BLACK,   fontName="Helvetica-Bold")
    head_s    = style("head",    fontSize=7,  textColor=DGRAY,   fontName="Helvetica",      alignment=TA_CENTER)
    cell_s    = style("cell",    fontSize=8,  textColor=BLACK,   fontName="Helvetica")
    cell_r_s  = style("cell_r",  fontSize=8,  textColor=BLACK,   fontName="Helvetica",      alignment=TA_RIGHT)
    debit_s   = style("debit",   fontSize=8,  textColor=RED,     fontName="Helvetica-Bold", alignment=TA_RIGHT)
    credit_s  = style("credit",  fontSize=8,  textColor=GREEN,   fontName="Helvetica-Bold", alignment=TA_RIGHT)
    bal_s     = style("bal",     fontSize=8,  textColor=BLACK,   fontName="Helvetica-Bold", alignment=TA_RIGHT)
    footer_s  = style("footer",  fontSize=7,  textColor=DGRAY,   fontName="Helvetica",      alignment=TA_CENTER)

    story = []

    # ── Header banner ──────────────────────────────────────────────────────
    header_data = [[
        Paragraph("NatWest", title_s),
        Paragraph(f"<b>Bank Statement</b><br/>{period_label}", sub_s),
    ]]
    header_table = Table(header_data, colWidths=[80*mm, None])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",  (0,0), (0,0), 6*mm),
        ("RIGHTPADDING", (1,0), (1,0), 6*mm),
        ("TOPPADDING",   (0,0), (-1,-1), 5*mm),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5*mm),
        ("ALIGN",      (1,0), (1,0), "RIGHT"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6*mm))

    # ── Account info ───────────────────────────────────────────────────────
    info_data = [
        [
            Paragraph("Account Name",   label_s),
            Paragraph("Account Number", label_s),
            Paragraph("Sort Code",      label_s),
            Paragraph("Statement Period", label_s),
        ],
        [
            Paragraph(account_name,   value_s),
            Paragraph(account_number, value_s),
            Paragraph(sort_code,      value_s),
            Paragraph(period_label,   value_s),
        ],
    ]
    info_table = Table(info_data, colWidths=[55*mm, 45*mm, 35*mm, None])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LGRAY),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [LGRAY, WHITE]),
        ("BOX",        (0,0), (-1,-1), 0.5, MGRAY),
        ("GRID",       (0,0), (-1,-1), 0.3, MGRAY),
        ("LEFTPADDING",  (0,0), (-1,-1), 4*mm),
        ("RIGHTPADDING", (0,0), (-1,-1), 4*mm),
        ("TOPPADDING",   (0,0), (-1,-1), 2*mm),
        ("BOTTOMPADDING",(0,0), (-1,-1), 2*mm),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 6*mm))

    # ── Opening balance ────────────────────────────────────────────────────
    ob_data = [[
        Paragraph("Opening Balance", style("ob_l", fontSize=8, textColor=DGRAY, fontName="Helvetica")),
        Paragraph(f"£{opening_balance:,.2f}", style("ob_r", fontSize=9, textColor=BLACK, fontName="Helvetica-Bold", alignment=TA_RIGHT)),
    ]]
    ob_table = Table(ob_data, colWidths=[None, 40*mm])
    ob_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), colors.HexColor("#eff6ff")),
        ("BOX",          (0,0), (-1,-1), 0.5, BLUE),
        ("LEFTPADDING",  (0,0), (-1,-1), 4*mm),
        ("RIGHTPADDING", (0,0), (-1,-1), 4*mm),
        ("TOPPADDING",   (0,0), (-1,-1), 2*mm),
        ("BOTTOMPADDING",(0,0), (-1,-1), 2*mm),
    ]))
    story.append(ob_table)
    story.append(Spacer(1, 4*mm))

    # ── Transaction table ──────────────────────────────────────────────────
    col_heads = [
        Paragraph("DATE",        head_s),
        Paragraph("DESCRIPTION", head_s),
        Paragraph("TYPE",        head_s),
        Paragraph("DEBIT (£)",   head_s),
        Paragraph("CREDIT (£)",  head_s),
        Paragraph("BALANCE (£)", head_s),
    ]

    balance = opening_balance
    rows = [col_heads]
    for tx in transactions:
        date, desc, amount, tx_type = tx
        if tx_type == "debit":
            balance -= amount
            debit_str  = Paragraph(f"{amount:,.2f}", debit_s)
            credit_str = Paragraph("—", cell_r_s)
        else:
            balance += amount
            debit_str  = Paragraph("—", cell_r_s)
            credit_str = Paragraph(f"{amount:,.2f}", credit_s)

        rows.append([
            Paragraph(date,    cell_s),
            Paragraph(desc,    cell_s),
            Paragraph(tx_type.capitalize(), cell_s),
            debit_str,
            credit_str,
            Paragraph(f"{balance:,.2f}", bal_s),
        ])

    col_widths = [22*mm, 72*mm, 18*mm, 23*mm, 23*mm, 25*mm]
    tx_table = Table(rows, colWidths=col_widths, repeatRows=1)
    tx_table.setStyle(TableStyle([
        # Header row
        ("BACKGROUND",   (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",    (0,0), (-1,0), WHITE),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,0), 7),
        ("ALIGN",        (0,0), (-1,0), "CENTER"),
        # Data rows alternating
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, LGRAY]),
        ("GRID",          (0,0),(-1,-1), 0.3, MGRAY),
        ("BOX",           (0,0),(-1,-1), 0.5, MGRAY),
        ("LEFTPADDING",  (0,0), (-1,-1), 3*mm),
        ("RIGHTPADDING", (0,0), (-1,-1), 3*mm),
        ("TOPPADDING",   (0,0), (-1,-1), 2*mm),
        ("BOTTOMPADDING",(0,0), (-1,-1), 2*mm),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(tx_table)
    story.append(Spacer(1, 6*mm))

    # ── Closing balance ────────────────────────────────────────────────────
    cb_data = [[
        Paragraph("Closing Balance", style("cb_l", fontSize=8, textColor=DGRAY, fontName="Helvetica-Bold")),
        Paragraph(f"£{balance:,.2f}", style("cb_r", fontSize=10, textColor=NAVY, fontName="Helvetica-Bold", alignment=TA_RIGHT)),
    ]]
    cb_table = Table(cb_data, colWidths=[None, 40*mm])
    cb_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), colors.HexColor("#e0e7ff")),
        ("BOX",          (0,0), (-1,-1), 0.8, NAVY),
        ("LEFTPADDING",  (0,0), (-1,-1), 4*mm),
        ("RIGHTPADDING", (0,0), (-1,-1), 4*mm),
        ("TOPPADDING",   (0,0), (-1,-1), 2.5*mm),
        ("BOTTOMPADDING",(0,0), (-1,-1), 2.5*mm),
    ]))
    story.append(cb_table)
    story.append(Spacer(1, 8*mm))

    # ── Footer ────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=MGRAY))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "NatWest Bank plc. Registered in England &amp; Wales (No. 929027). "
        "Registered Office: 250 Bishopsgate, London EC2M 4AA. "
        "Authorised by the Prudential Regulation Authority and regulated by the "
        "Financial Conduct Authority and the Prudential Regulation Authority.",
        footer_s
    ))

    doc.build(story)
    print(f"Generated: {filename}")


# ── Statement 1: January 2025 ───────────────────────────────────────────────
jan_transactions = [
    ("2025-01-02", "OPENING SALARY — EMPLOYER LTD",       3850.00, "credit"),
    ("2025-01-03", "RENT — FOLIO PROPERTIES",              850.00, "debit"),
    ("2025-01-04", "TESCO SUPERSTORE WATFORD",              87.43, "debit"),
    ("2025-01-05", "EE MOBILE BILL",                        35.00, "debit"),
    ("2025-01-06", "LIDL GB HEMEL",                         43.20, "debit"),
    ("2025-01-07", "VUE CINEMA WATFORD",                    24.00, "debit"),
    ("2025-01-08", "GP PRESCRIPTION NHS",                    9.90, "debit"),
    ("2025-01-09", "AMAZON.CO.UK",                          35.76, "debit"),
    ("2025-01-10", "MCDONALDS 1234",                        12.30, "debit"),
    ("2025-01-11", "TFL TRAVEL CHARGE",                     40.00, "debit"),
    ("2025-01-12", "THAMES WATER UTILITIES",                45.00, "debit"),
    ("2025-01-13", "COSTA COFFEE WATFORD",                   8.40, "debit"),
    ("2025-01-14", "SPOTIFY UK",                            11.99, "debit"),
    ("2025-01-15", "SAINSBURYS SUPERMARKETS",               56.30, "debit"),
    ("2025-01-16", "UBER UK",                               14.80, "debit"),
    ("2025-01-17", "NEW YEAR BONUS — EMPLOYER LTD",        500.00, "credit"),
    ("2025-01-19", "ASOS.COM",                              45.99, "debit"),
    ("2025-01-20", "BRITISH GAS ENERGY",                    89.00, "debit"),
    ("2025-01-21", "NANDOS WATFORD",                        32.50, "debit"),
    ("2025-01-22", "SHELL PETROL STATION",                  64.20, "debit"),
    ("2025-01-23", "NETFLIX SERVICES UK",                   17.99, "debit"),
    ("2025-01-24", "BOOTS PHARMACY",                        12.75, "debit"),
    ("2025-01-27", "ZARA UK LTD",                           89.99, "debit"),
    ("2025-01-28", "NATIONAL RAIL ENQUIRIES",               52.40, "debit"),
    ("2025-01-29", "PRET A MANGER",                          7.85, "debit"),
    ("2025-01-30", "MARKS AND SPENCER FOOD",                34.60, "debit"),
    ("2025-01-31", "PAYPAL — EBAY PURCHASE",                28.00, "debit"),
]

build_pdf(
    "statement_jan2025.pdf",
    account_name    = "Alex Smith",
    account_number  = "****4721",
    sort_code       = "60-14-32",
    period_label    = "1 January 2025 – 31 January 2025",
    opening_balance = 1240.50,
    transactions    = jan_transactions,
)


# ── Statement 2: February 2025 ──────────────────────────────────────────────
feb_transactions = [
    ("2025-02-01", "SALARY — EMPLOYER LTD",               3850.00, "credit"),
    ("2025-02-02", "RENT — FOLIO PROPERTIES",              850.00, "debit"),
    ("2025-02-03", "WAITROSE WATFORD",                      72.15, "debit"),
    ("2025-02-04", "DELIVEROO ORDER",                       26.50, "debit"),
    ("2025-02-05", "ODEON CINEMA HATFIELD",                 21.00, "debit"),
    ("2025-02-06", "BOOTS PHARMACY",                        15.40, "debit"),
    ("2025-02-07", "EE MOBILE BILL",                        35.00, "debit"),
    ("2025-02-08", "TFL TRAVEL CHARGE",                     40.00, "debit"),
    ("2025-02-10", "JOHN LEWIS PARTNERSHIP",                64.00, "debit"),
    ("2025-02-11", "THAMES WATER UTILITIES",                45.00, "debit"),
    ("2025-02-12", "STARBUCKS COFFEE",                       6.90, "debit"),
    ("2025-02-13", "SPOTIFY UK",                            11.99, "debit"),
    ("2025-02-14", "VALENTINES DINNER — HAWKSMOOR",        115.00, "debit"),
    ("2025-02-15", "ALDI STORES",                           51.20, "debit"),
    ("2025-02-16", "UBER UK",                               18.30, "debit"),
    ("2025-02-17", "NETFLIX SERVICES UK",                   17.99, "debit"),
    ("2025-02-18", "BRITISH GAS ENERGY",                    95.00, "debit"),
    ("2025-02-19", "H AND M UK",                            57.00, "debit"),
    ("2025-02-20", "SHELL PETROL STATION",                  71.40, "debit"),
    ("2025-02-21", "MCDONALDS 5678",                        10.80, "debit"),
    ("2025-02-22", "AMAZON.CO.UK",                          42.99, "debit"),
    ("2025-02-24", "TESCO EXPRESS WATFORD",                 29.75, "debit"),
    ("2025-02-25", "NATIONAL RAIL ENQUIRIES",               38.60, "debit"),
    ("2025-02-26", "PRET A MANGER",                          6.50, "debit"),
    ("2025-02-27", "NIKE UK ONLINE",                        89.95, "debit"),
    ("2025-02-28", "FREELANCE PAYMENT — CLIENT A",         350.00, "credit"),
]

build_pdf(
    "statement_feb2025.pdf",
    account_name    = "Alex Smith",
    account_number  = "****4721",
    sort_code       = "60-14-32",
    period_label    = "1 February 2025 – 28 February 2025",
    opening_balance = 850.00,
    transactions    = feb_transactions,
)
