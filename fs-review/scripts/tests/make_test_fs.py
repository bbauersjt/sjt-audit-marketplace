"""Synthetic construction-contractor FS PDF with PLANTED errors, to prove the pipeline.

Planted errors (what the pipeline MUST catch):
  E1  Balance sheet: Total current assets printed $1 high (rounding slip): 4,857,224
      vs true sum 4,857,223.
  E2  Income statement: two-column comparative; PY "Total operating expenses" printed
      1,412,338 vs true 1,412,238 ($100 fat-finger).
  E3  Note 4 debt total 2,455,000 vs balance sheet total debt 2,456,000 (broken tie).
  E4  WIP schedule: Job 103 over/(under)billings printed (61,000) but billings -
      revenues earned = 405,000 - 1,193,876 = (788,876): the printed cell is wrong.
  E5  WIP schedule: total contract price column printed 100 low.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

W, H = letter
LEFT = 0.9 * inch


def money(v, paren_zero_dash=True):
    if v is None:
        return ""
    if v == 0 and paren_zero_dash:
        return "-"
    s = f"{abs(v):,.0f}"
    return f"({s})" if v < 0 else s


def draw_rows(c, y, rows, cols_x, title=None, size=8.5):
    c.setFont("Helvetica", size)
    for label, vals, bold in rows:
        if bold:
            c.setFont("Helvetica-Bold", size)
        c.drawString(LEFT, y, label)
        for x, v in zip(cols_x, vals):
            if v is not None:
                c.drawRightString(x, y, v if isinstance(v, str) else money(v))
        if bold:
            c.setFont("Helvetica", size)
        y -= 13
    return y


c = canvas.Canvas(str(__file__).replace("make_test_fs.py", "test_fs.pdf"),
                  pagesize=letter)

# ---- Page 1: Balance Sheet ----
c.setFont("Helvetica-Bold", 11)
c.drawCentredString(W / 2, H - 60, "APEX BUILDERS, INC.")
c.setFont("Helvetica-Bold", 10)
c.drawCentredString(W / 2, H - 75, "Balance Sheet")
c.drawCentredString(W / 2, H - 90, "December 31, 2025")
x1 = 5.4 * inch
y = H - 130
rows = [
    ("ASSETS", [None], True),
    ("Cash and cash equivalents", [812_455], False),
    ("Contract receivables, net", [2_314_887], False),
    ("Costs and estimated earnings in excess of billings", [187_654], False),
    ("Prepaid expenses", [98_341], False),
    ("Other current assets", [1_443_886], False),
    # true sum = 4,857,223 ; printed $1 high  (E1)
    ("Total current assets", [4_857_224], True),
    ("Property and equipment, net", [1_982_400], False),
    ("Total assets", [6_839_624], True),   # foots to the (wrong) subtotal
    ("", [None], False),
    ("LIABILITIES AND STOCKHOLDERS' EQUITY", [None], True),
    ("Accounts payable", [1_204_112], False),
    ("Billings in excess of costs and estimated earnings", [278_450], False),
    ("Accrued expenses", [391_062], False),
    ("Current portion of long-term debt", [312_000], False),
    ("Total current liabilities", [2_185_624], True),
    ("Long-term debt, net of current portion", [2_144_000], False),
    ("Total liabilities", [4_329_624], True),
    ("Common stock", [100_000], False),
    ("Retained earnings", [2_410_000], False),
    ("Total stockholders' equity", [2_510_000], True),
    ("Total liabilities and stockholders' equity", [6_839_624], True),
]
draw_rows(c, y, rows, [x1])
c.showPage()

# ---- Page 2: Income Statement (comparative, 2 cols) ----
c.setFont("Helvetica-Bold", 11)
c.drawCentredString(W / 2, H - 60, "APEX BUILDERS, INC.")
c.setFont("Helvetica-Bold", 10)
c.drawCentredString(W / 2, H - 75, "Statements of Operations")
c.drawCentredString(W / 2, H - 90, "Years Ended December 31, 2025 and 2024")
c.setFont("Helvetica-Bold", 9)
xA, xB = 4.9 * inch, 6.4 * inch
c.drawRightString(xA, H - 112, "2025")
c.drawRightString(xB, H - 112, "2024")
y = H - 130
rows = [
    ("Contract revenues earned", [14_882_450, 12_640_310], False),
    ("Cost of revenues earned", [-12_913_207, -11_002_881], False),
    ("Gross profit", [1_969_243, 1_637_429], True),
    ("Salaries and administrative", [802_114, 748_220], False),
    ("Insurance", [214_007, 198_444], False),
    ("Depreciation", [287_300, 265_100], False),
    ("Office and other", [211_512, 200_474], False),
    # PY true total = 1,412,238; printed 1,412,338 (E2)
    ("Total operating expenses", [1_514_933, 1_412_338], True),
    ("Income from operations", [454_310, 225_091], True),
    ("Interest expense", [-112_480, -98_240], False),
    ("Net income", [341_830, 126_851], True),
]
draw_rows(c, y, rows, [xA, xB])
c.showPage()

# ---- Page 3: Note 4 Long-Term Debt ----
c.setFont("Helvetica-Bold", 10)
c.drawString(LEFT, H - 60, "NOTE 4 — LONG-TERM DEBT")
c.setFont("Helvetica", 9)
c.drawString(LEFT, H - 80, "Long-term debt consists of the following at December 31, 2025:")
x1 = 5.4 * inch
y = H - 105
rows = [
    ("Equipment note payable, 6.75%, due 2029", [1_455_000], False),
    ("Term loan, 7.25%, due 2031", [1_000_000], False),
    # note total 2,455,000 vs BS 312,000 + 2,144,000 = 2,456,000 (E3)
    ("Total long-term debt", [2_455_000], True),
    ("Less current portion", [-312_000], False),
    ("Long-term debt, net of current portion", [2_143_000], True),
]
draw_rows(c, y, rows, [x1])
c.showPage()

# ---- Page 4: WIP schedule (landscape, like a real job schedule) ----
from reportlab.lib.pagesizes import landscape
c.setPageSize(landscape(letter))
LW, LH = landscape(letter)
c.setFont("Helvetica-Bold", 10)
c.drawCentredString(LW / 2, LH - 55, "APEX BUILDERS, INC.")
c.drawCentredString(LW / 2, LH - 70, "Schedule of Contracts in Progress")
c.drawCentredString(LW / 2, LH - 85, "December 31, 2025")
c.setFont("Helvetica-Bold", 7.5)
hdrs = ["Contract Price", "Costs Incurred to Date", "Estimated Cost to Complete",
        "Estimated Gross Profit", "Revenues Earned", "Billings to Date",
        "Over (Under) Billings"]
xs = [3.4 * inch, 4.5 * inch, 5.6 * inch, 6.7 * inch, 7.8 * inch, 8.9 * inch,
      10.0 * inch]
ytop = LH - 110
for x, htxt in zip(xs, hdrs):
    for i, wln in enumerate(htxt.split(" ")):
        c.drawRightString(x, ytop + 8 - i * 8, wln)
y = ytop - 30

jobs = [
    # label, price, ctd, ctc, rev_earned, billings, printed_ou
    ("Job 101 - Riverside Plaza", 3_200_000, 1_845_000, 655_000, 2_361_600, 2_402_000, 40_400),
    ("Job 102 - Hangar 7", 1_850_000, 402_500, 1_207_500, 462_500, 380_000, -82_500),
    # E4: printed OU (61,000); true billings-earned = 405,000-464,876 = (59,876)
    ("Job 103 - Mill Creek WWTP", 2_760_000, 1_104_000, 1_449_000, 1_193_876+0, 405_000, -61_000),
]
# recompute consistent columns
rows = []
tot = [0] * 7
for label, price, ctd, ctc, rev, bil, ou in jobs:
    tec = ctd + ctc
    egp = price - tec
    vals = [price, ctd, ctc, egp, rev, bil, ou]
    for i, v in enumerate(vals):
        tot[i] += v
    rows.append((label, vals, False))
tot[0] -= 100  # E5: total contract price printed 100 low
rows.append(("Total", tot, True))
draw_rows(c, y, rows, xs, size=7.5)
c.showPage()

# ---- Page 5: Notes text page with PLANTED PROOF ERRORS ----
# P1 dangling "Note 9" reference; P2 note sequence gap (Notes 1,2 here + Note 4 on p3,
# no Note 3) and out-of-order (4 appears before 1); P3 stale year 2023; P4 mixed
# Auditor's / Auditors'; P5 DRAFT marker; P6 casing drift on a repeated heading;
# P7 mixed serial comma; P8 mixed date formats (Dec. 31, 2025 vs December 31, 2025).
c.setPageSize(letter)
c.setFont("Helvetica", 9)
y = H - 60
for line, bold in [
    ("NOTES TO FINANCIAL STATEMENTS", True),
    ("December 31, 2025", False),
    ("", False),
    ("NOTE 1 - NATURE OF OPERATIONS", True),
    ("The Company is a general contractor performing commercial and municipal", False),
    ("construction throughout the region. Contract costs include materials, labor, and", False),
    ("overhead, as well as equipment, fuel, and repairs.", False),
    ("The Company expects to complete the Riverside Plaza project during 2023.", False),
    ("", False),
    ("NOTE 2 - SUMMARY OF SIGNIFICANT ACCOUNTING POLICIES", True),
    ("Summary of Significant Accounting Policies", False),
    ("Summary of significant accounting policies", False),
    ("Summary of Significant Accounting Policies", False),
    ("Revenue is recognized over time using the cost-to-cost method as described", False),
    ("in Note 9, based on costs incurred relative to total estimated costs.", False),
    # P9 misspelling; P10 rare-font run (Times-Roman line in a Helvetica document)
    ("Contract recievables are stated net of an allowance for expected credit losses.", False),
    ("Financial instruments consist of cash, receivables and payables.", False),
    ("Job costs consist of materials, subcontracts and equipment. DRAFT", False),
    ("As reported in the Independent Auditor's Report dated Dec. 31, 2025, and", False),
    ("consistent with the Auditors' opinion thereon, the statements are presented", False),
    ("in accordance with accounting principles generally accepted in the United States.", False),
] :
    c.setFont("Helvetica-Bold" if bold else "Helvetica", 9)
    c.drawString(LEFT, y, line)
    y -= 14
c.setFont("Times-Roman", 11)
c.drawString(LEFT, y, "Management believes these estimates are reasonable.")
c.save()
print("wrote test_fs.pdf")

# ---- PY package: the issued 2024 statements (true figures) ----
py = canvas.Canvas(str(__file__).replace("make_test_fs.py", "test_fs_py.pdf"),
                   pagesize=letter)
py.setFont("Helvetica-Bold", 11)
py.drawCentredString(W / 2, H - 60, "APEX BUILDERS, INC.")
py.setFont("Helvetica-Bold", 10)
py.drawCentredString(W / 2, H - 75, "Statement of Operations")
py.drawCentredString(W / 2, H - 90, "Year Ended December 31, 2024")
py.setFont("Helvetica-Bold", 9)
py.drawRightString(4.9 * inch, H - 112, "2024")
y = H - 130
py_rows = [
    ("Contract revenues earned", [12_640_310], False),
    ("Cost of revenues earned", [-11_002_881], False),
    ("Gross profit", [1_637_429], True),
    ("Salaries and administrative", [748_220], False),
    ("Insurance", [198_444], False),
    ("Depreciation", [265_100], False),
    ("Office and other", [200_474], False),
    ("Total operating expenses", [1_412_238], True),   # TRUE figure (CY package shows 1,412,338)
    ("Income from operations", [225_191], True),        # consistent with true total
    ("Interest expense", [-98_240], False),
    ("Net income", [126_951], True),                    # CY comparative shows 126,851
]
py.setFont("Helvetica", 8.5)
for label, vals, bold in py_rows:
    if bold:
        py.setFont("Helvetica-Bold", 8.5)
    py.drawString(LEFT, y, label)
    py.drawRightString(4.9 * inch, y, money(vals[0]))
    if bold:
        py.setFont("Helvetica", 8.5)
    y -= 13
py.save()
print("wrote test_fs_py.pdf")
