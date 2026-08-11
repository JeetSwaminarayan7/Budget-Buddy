"""Generate dummy UK student bank statements as PDFs using reportlab."""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "bank_statements")
os.makedirs(OUT_DIR, exist_ok=True)

STATEMENTS = [
    {
        "filename": "statement_mar2025.pdf",
        "period":   "01 March 2025 – 31 March 2025",
        "opening":  1243.80,
        "transactions": [
            ("2025-03-01", "Student Loan Company",          "credit", 1200.00),
            ("2025-03-02", "Tesco Superstore",              "debit",    54.30),
            ("2025-03-03", "TfL Contactless",               "debit",    12.50),
            ("2025-03-05", "Deliveroo",                     "debit",    17.99),
            ("2025-03-06", "Spotify Premium",               "debit",     6.99),
            ("2025-03-07", "Amazon Books",                  "debit",    31.49),
            ("2025-03-08", "ALDI",                          "debit",    22.10),
            ("2025-03-09", "Costa Coffee",                  "debit",     5.40),
            ("2025-03-10", "National Rail",                 "debit",    28.50),
            ("2025-03-12", "Part-time Job – Cafe Nero",     "credit",  380.00),
            ("2025-03-13", "Netflix",                       "debit",     4.99),
            ("2025-03-14", "Sainsbury's",                   "debit",    46.85),
            ("2025-03-15", "Uber",                          "debit",     9.20),
            ("2025-03-17", "ASOS",                          "debit",    55.00),
            ("2025-03-18", "McDonald's",                    "debit",     8.45),
            ("2025-03-19", "EE Phone Bill",                 "debit",    20.00),
            ("2025-03-20", "Waterstones",                   "debit",    14.99),
            ("2025-03-21", "Lidl",                          "debit",    19.60),
            ("2025-03-22", "Cineworld",                     "debit",    13.50),
            ("2025-03-24", "Amazon",                        "debit",    24.99),
            ("2025-03-25", "Pret A Manger",                 "debit",     6.80),
            ("2025-03-26", "TfL Contactless",               "debit",    15.00),
            ("2025-03-28", "Greggs",                        "debit",     4.20),
            ("2025-03-29", "Gym Membership – PureGym",      "debit",    25.99),
            ("2025-03-31", "M&S Simply Food",               "debit",    18.70),
        ],
    },
    {
        "filename": "statement_apr2025.pdf",
        "period":   "01 April 2025 – 30 April 2025",
        "opening":  2356.10,
        "transactions": [
            ("2025-04-01", "Student Loan Company",          "credit", 1200.00),
            ("2025-04-01", "University Library Fine",       "debit",     5.00),
            ("2025-04-02", "Tesco",                         "debit",    62.40),
            ("2025-04-03", "TfL Contactless",               "debit",    14.20),
            ("2025-04-04", "Nando's",                       "debit",    22.50),
            ("2025-04-05", "Amazon Prime",                  "debit",     8.99),
            ("2025-04-07", "Spotify Premium",               "debit",     6.99),
            ("2025-04-08", "Boots",                         "debit",    12.30),
            ("2025-04-09", "Uber Eats",                     "debit",    19.80),
            ("2025-04-10", "Part-time Job – Cafe Nero",     "credit",  380.00),
            ("2025-04-11", "IKEA",                          "debit",    78.50),
            ("2025-04-12", "Sainsbury's",                   "debit",    38.70),
            ("2025-04-14", "National Rail",                 "debit",    42.00),
            ("2025-04-15", "Costa Coffee",                  "debit",     4.80),
            ("2025-04-16", "Netflix",                       "debit",     4.99),
            ("2025-04-17", "ALDI",                          "debit",    27.35),
            ("2025-04-18", "Vue Cinema",                    "debit",    11.99),
            ("2025-04-20", "H&M",                           "debit",    45.00),
            ("2025-04-21", "EE Phone Bill",                 "debit",    20.00),
            ("2025-04-22", "Deliveroo",                     "debit",    21.50),
            ("2025-04-24", "Waterstones",                   "debit",    18.99),
            ("2025-04-25", "TfL Contactless",               "debit",    10.80),
            ("2025-04-26", "Greggs",                        "debit",     3.90),
            ("2025-04-28", "Gym Membership – PureGym",      "debit",    25.99),
            ("2025-04-29", "Pizza Hut",                     "debit",    16.40),
            ("2025-04-30", "Tesco",                         "debit",    29.90),
        ],
    },
    {
        "filename": "statement_may2025.pdf",
        "period":   "01 May 2025 – 31 May 2025",
        "opening":  1890.55,
        "transactions": [
            ("2025-05-01", "Part-time Job – Cafe Nero",     "credit",  420.00),
            ("2025-05-02", "Sainsbury's",                   "debit",    55.10),
            ("2025-05-03", "TfL Contactless",               "debit",    16.40),
            ("2025-05-04", "Spotify Premium",               "debit",     6.99),
            ("2025-05-05", "Deliveroo",                     "debit",    14.20),
            ("2025-05-06", "Amazon Books",                  "debit",    22.99),
            ("2025-05-07", "Costa Coffee",                  "debit",     5.10),
            ("2025-05-08", "EE Phone Bill",                 "debit",    20.00),
            ("2025-05-09", "ALDI",                          "debit",    31.50),
            ("2025-05-10", "Netflix",                       "debit",     4.99),
            ("2025-05-12", "National Rail",                 "debit",    56.00),
            ("2025-05-13", "Uber",                          "debit",    11.30),
            ("2025-05-14", "McDonald's",                    "debit",     7.60),
            ("2025-05-15", "ASOS",                          "debit",    72.00),
            ("2025-05-16", "Pret A Manger",                 "debit",     8.40),
            ("2025-05-17", "Tesco",                         "debit",    44.20),
            ("2025-05-19", "Part-time Job – Cafe Nero",     "credit",  420.00),
            ("2025-05-20", "Vue Cinema",                    "debit",    13.50),
            ("2025-05-21", "Gym Membership – PureGym",      "debit",    25.99),
            ("2025-05-22", "Boots",                         "debit",     9.80),
            ("2025-05-23", "Lidl",                          "debit",    23.45),
            ("2025-05-24", "Uber Eats",                     "debit",    18.60),
            ("2025-05-25", "Waterstones",                   "debit",    11.99),
            ("2025-05-27", "TfL Contactless",               "debit",    13.20),
            ("2025-05-28", "Greggs",                        "debit",     4.50),
            ("2025-05-30", "Amazon",                        "debit",    34.99),
            ("2025-05-31", "Nando's",                       "debit",    20.10),
        ],
    },
    {
        "filename": "statement_jun2025.pdf",
        "period":   "01 June 2025 – 30 June 2025",
        "opening":  2104.30,
        "transactions": [
            ("2025-06-01", "Student Loan Company",          "credit", 1200.00),
            ("2025-06-02", "Tesco",                         "debit",    67.80),
            ("2025-06-03", "TfL Contactless",               "debit",    18.60),
            ("2025-06-04", "Spotify Premium",               "debit",     6.99),
            ("2025-06-05", "EE Phone Bill",                 "debit",    20.00),
            ("2025-06-06", "Deliveroo",                     "debit",    23.40),
            ("2025-06-07", "Netflix",                       "debit",     4.99),
            ("2025-06-08", "Costa Coffee",                  "debit",     5.60),
            ("2025-06-09", "Amazon",                        "debit",    44.99),
            ("2025-06-10", "Part-time Job – Cafe Nero",     "credit",  450.00),
            ("2025-06-11", "ALDI",                          "debit",    29.70),
            ("2025-06-12", "Uber",                          "debit",    13.50),
            ("2025-06-13", "McDonald's",                    "debit",     9.10),
            ("2025-06-14", "National Rail",                 "debit",    38.00),
            ("2025-06-15", "Zara",                          "debit",    89.50),
            ("2025-06-16", "Sainsbury's",                   "debit",    51.30),
            ("2025-06-18", "Pret A Manger",                 "debit",     7.20),
            ("2025-06-19", "Gym Membership – PureGym",      "debit",    25.99),
            ("2025-06-20", "Vue Cinema",                    "debit",    12.50),
            ("2025-06-21", "Uber Eats",                     "debit",    16.80),
            ("2025-06-22", "Boots",                         "debit",    14.60),
            ("2025-06-23", "Greggs",                        "debit",     3.70),
            ("2025-06-24", "Part-time Job – Cafe Nero",     "credit",  450.00),
            ("2025-06-25", "TfL Contactless",               "debit",    16.00),
            ("2025-06-26", "Waterstones",                   "debit",    13.49),
            ("2025-06-27", "Nando's",                       "debit",    24.80),
            ("2025-06-28", "IKEA",                          "debit",    35.00),
            ("2025-06-29", "Lidl",                          "debit",    21.90),
            ("2025-06-30", "Amazon Books",                  "debit",    19.99),
        ],
    },
]


styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "BankTitle",
    parent=styles["Normal"],
    fontSize=18,
    fontName="Helvetica-Bold",
    textColor=colors.HexColor("#1a3a6b"),
    spaceAfter=4,
)
SUBTITLE_STYLE = ParagraphStyle(
    "BankSubtitle",
    parent=styles["Normal"],
    fontSize=10,
    fontName="Helvetica",
    textColor=colors.HexColor("#555555"),
    spaceAfter=2,
)
LABEL_STYLE = ParagraphStyle(
    "Label",
    parent=styles["Normal"],
    fontSize=9,
    fontName="Helvetica-Bold",
    textColor=colors.HexColor("#333333"),
)
NORMAL_STYLE = ParagraphStyle(
    "Normal2",
    parent=styles["Normal"],
    fontSize=9,
    fontName="Helvetica",
    textColor=colors.HexColor("#333333"),
)


def build_pdf(stmt):
    path = os.path.join(OUT_DIR, stmt["filename"])
    doc  = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    story = []

    # ── Bank header ──────────────────────────────────────────────────────────
    story.append(Paragraph("NatWest Student Account", TITLE_STYLE))
    story.append(Paragraph("NatWest Bank plc  |  250 Bishopsgate, London, EC2M 4AA", SUBTITLE_STYLE))
    story.append(Spacer(1, 0.4*cm))

    # ── Account / period info table ──────────────────────────────────────────
    info_data = [
        [Paragraph("Account Holder:", LABEL_STYLE),  Paragraph("Alex Smith", NORMAL_STYLE),
         Paragraph("Statement Period:", LABEL_STYLE), Paragraph(stmt["period"], NORMAL_STYLE)],
        [Paragraph("Account Number:", LABEL_STYLE),  Paragraph("47291836", NORMAL_STYLE),
         Paragraph("Sort Code:", LABEL_STYLE),        Paragraph("60-10-45", NORMAL_STYLE)],
        [Paragraph("Account Type:", LABEL_STYLE),    Paragraph("Student Current Account", NORMAL_STYLE),
         Paragraph("Currency:", LABEL_STYLE),         Paragraph("GBP (£)", NORMAL_STYLE)],
    ]
    info_tbl = Table(info_data, colWidths=[3.5*cm, 5.5*cm, 3.5*cm, 5.5*cm])
    info_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#f0f4ff")),
        ("BOX",        (0,0), (-1,-1), 0.5, colors.HexColor("#c0cce8")),
        ("INNERGRID",  (0,0), (-1,-1), 0.3, colors.HexColor("#c0cce8")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 0.5*cm))

    # ── Opening balance ───────────────────────────────────────────────────────
    story.append(Paragraph(f"Opening Balance:  £{stmt['opening']:.2f}", LABEL_STYLE))
    story.append(Spacer(1, 0.3*cm))

    # ── Transaction table ─────────────────────────────────────────────────────
    header = [
        Paragraph("Date",        LABEL_STYLE),
        Paragraph("Description", LABEL_STYLE),
        Paragraph("Debit (£)",   LABEL_STYLE),
        Paragraph("Credit (£)",  LABEL_STYLE),
        Paragraph("Balance (£)", LABEL_STYLE),
    ]
    rows = [header]
    balance = stmt["opening"]
    for date, desc, ttype, amount in stmt["transactions"]:
        if ttype == "debit":
            balance -= amount
            rows.append([
                Paragraph(date, NORMAL_STYLE),
                Paragraph(desc, NORMAL_STYLE),
                Paragraph(f"{amount:.2f}", NORMAL_STYLE),
                Paragraph("",  NORMAL_STYLE),
                Paragraph(f"{balance:.2f}", NORMAL_STYLE),
            ])
        else:
            balance += amount
            rows.append([
                Paragraph(date, NORMAL_STYLE),
                Paragraph(desc, NORMAL_STYLE),
                Paragraph("",  NORMAL_STYLE),
                Paragraph(f"{amount:.2f}", NORMAL_STYLE),
                Paragraph(f"{balance:.2f}", NORMAL_STYLE),
            ])

    tbl = Table(rows, colWidths=[2.5*cm, 7.5*cm, 2.5*cm, 2.5*cm, 3*cm])
    tbl.setStyle(TableStyle([
        # header row
        ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#1a3a6b")),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0), 9),
        # data rows alternate shading
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f7f9ff")]),
        ("FONTSIZE",      (0,1), (-1,-1), 8),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, colors.HexColor("#d0d8ec")),
        ("BOX",           (0,0), (-1,-1), 0.5, colors.HexColor("#a0aece")),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
        ("ALIGN",         (2,0), (-1,-1), "RIGHT"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.4*cm))

    # ── Closing balance ───────────────────────────────────────────────────────
    story.append(Paragraph(f"Closing Balance:  £{balance:.2f}", LABEL_STYLE))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "This statement is for informational purposes only. "
        "NatWest Bank plc. Registered in England & Wales (No. 929027).",
        SUBTITLE_STYLE,
    ))

    doc.build(story)
    print(f"  Created: {stmt['filename']}  (closing balance £{balance:.2f})")


if __name__ == "__main__":
    print("Generating dummy bank statements…")
    for s in STATEMENTS:
        build_pdf(s)
    print("Done — files saved to backend/bank_statements/")
