"""Thoth Ledger — value strategy model workbook (private: contains Bloomberg-derived data, never published)."""
import sys, os, json
sys.path.insert(0, "/home/claude/portfolio-project/strategies/etf")
import pandas as pd, numpy as np, engine as E
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule
from openpyxl.comments import Comment

O = pd.read_pickle(E.D + "/official.pkl"); SS = pd.read_parquet(E.D + "/../screen/sat_scores_monthly.parquet")
J = json.load(open("/home/claude/portfolio-project/site/data/etf_strategies.json"))
core, sat = O["core"], O["sat"]; IDX = O["combo"].index
wv = E.world_value().reindex(IDX); mw = E.BENCH.reindex(IDX); cash = E.CASH.reindex(IDX).fillna(0)
he = pd.Series(J["horus_eur"]["r"], index=pd.to_datetime(J["horus_eur"]["dates"]) + pd.offsets.MonthEnd(0)).reindex(IDX)
expo = O["expo"]; rs = O["rs"].copy(); rs.index = pd.to_datetime(rs.index); rs = rs[~rs.index.duplicated()].sort_index(); expo.index = pd.to_datetime(expo.index); nred = rs[["trend", "credit", "breadth"]].astype(int).sum(axis=1)
W, R, on, zc, zs = E.value_v4c(timing=False)
N = len(IDX); LAST = N + 1; FIRST_H = 2 + list(IDX).index(pd.Timestamp("2007-01-31")); MIDROW = 1 + list(IDX).index(pd.Timestamp("2015-12-31")) + 1
NAMES = {"C_US": "United States", "C_JP": "Japan", "C_GB": "United Kingdom", "C_FR": "France", "C_DE": "Germany", "C_CH": "Switzerland", "C_NL": "Netherlands",
         "C_IT": "Italy", "C_ES": "Spain", "C_SE": "Sweden", "C_DK": "Denmark", "C_CA": "Canada", "C_AU": "Australia", "C_HK": "Hong Kong",
         "S_EN": "Energy", "S_MT": "Materials", "S_IN": "Industrials", "S_CD": "Consumer Discretionary", "S_CS": "Consumer Staples", "S_HC": "Health Care",
         "S_FN": "Financials", "S_IT": "Information Technology", "S_TC": "Communication Services", "S_UT": "Utilities", "S_RE": "Real Estate"}
LINES = list(NAMES)

F_ = "Arial"; base = Font(name=F_, size=10); bold = Font(name=F_, size=10, bold=True); blue = Font(name=F_, size=10, color="0000FF")
green = Font(name=F_, size=10, color="008000"); hdr = Font(name=F_, size=10, bold=True, color="FFFFFF"); title = Font(name=F_, size=14, bold=True, color="0A1A30")
FH = PatternFill("solid", fgColor="0A1A30"); FV = PatternFill("solid", fgColor="EFE7D6"); FY = PatternFill("solid", fgColor="FFFF00"); FS = PatternFill("solid", fgColor="F6F2EA")
thin = Border(bottom=Side(style="thin", color="E5DCCB")); PCT = "0.0%;(0.0%);-"; PCT2 = "0.00%;(0.00%);-"
wb = Workbook()
def name(n, ref): wb.defined_names[n] = DefinedName(n, attr_text=ref)
def head(ws, r, vals, widths=None):
    for i, v in enumerate(vals, 1):
        c = ws.cell(r, i, v); c.font = hdr; c.fill = FH; c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    ws.row_dimensions[r].height = 32
    if widths:
        for i, w in enumerate(widths, 1): ws.column_dimensions[L(i)].width = w
def note(ws, r, text, c=1):
    x = ws.cell(r, c, text); x.font = Font(name=F_, size=9, italic=True, color="616A78"); return x

# ---------------- Read me
ws = wb.active; ws.title = "Read me"; ws.sheet_view.showGridLines = False
txt = [("Thoth Ledger — Global Value Rotation: strategy model", title), ("", None),
 ("Noah Doose · monthly backtest February 2006 – June 2026 (245 months) · EUR · net of costs · private file (Bloomberg-derived data, do not publish)", bold), ("", None),
 ("The strategy", bold),
 ("70% ETF core + 30% stock satellite. Core (V7): each month, the 4 cheapest developed countries (of 14) and the 4 cheapest MSCI World sectors (of 11), cheapness = mean z-score of E/P, B/P and dividend yield versus each line's own 10-year history; a held line stays while among the 6 cheapest; equal weight. Risk rule: when at least 2 of 3 indicators are red (MSCI World below its 10-month average; euro high yield lagging short euro government bonds over 3 months; fewer than half of the 25 lines above their 10-month average), the portfolio is cut to 50% equities, 50% euro money market; back to 100% when fewer than 2 are red.", None),
 ("Satellite: each month, 8 stocks from the 300 largest developed-market companies (point-in-time Bloomberg WORLD Index), in a country OR sector held by the core, ranked on the stock screen's sector-relative value score (EV/EBIT, B/P, FCF/P, Sales/EV; B/P and E/P for financials; fundamentals usable from fiscal-year end + 6 months and never before publication); a held stock stays while in the cheapest 40% of its sector; max 2 per sector, 3 per country; equal weight; same 50% risk rule.", None),
 ("Costs: core 0.10% per unit of turnover + 0.25%/yr ETF fees; satellite 0.15% per unit of turnover + 0.40%/yr withholding-tax haircut. Benchmark: MSCI World Value Net EUR; MSCI World Net EUR shown as the investor's alternative.", None), ("", None),
 ("Sheets", bold),
 ("Inputs — the levers (blue/yellow cells): core weight in the strategy, value weight when combined with Horus Smart Beta.", None),
 ("Monthly — one row per month: returns (inputs in blue), strategy return, NAVs and drawdowns (formulas).", None),
 ("Summary — CAGR, volatility, Sharpe, max drawdown, t-statistic for the full period, design half (2006-2015) and validation half (2016-2026), and the correlation matrix.", None),
 ("Yearly — calendar-year returns.  Horus_Mix — value strategy combined with Horus Smart Beta (in EUR) at 0-100%.  Optimiser — set up for Excel Solver.", None),
 ("Explorer — choose a month: core scores, ranks, holdings, risk indicators and the 8 satellite stocks of that month.", None),
 ("Core_Scores, Core_Holdings, Risk, Sat_Holdings, Sat_Scores (73,757 rows: every stock, every month) — the underlying data.", None), ("", None),
 ("Colour code: blue = input from the backtest engine (Python, strategies/etf/); black = formula; green = link to another sheet; yellow = cell you may change. Each monthly return is earned over that month by the portfolio decided at the end of the previous month.", None),
 ("Honesty notes: the versions were chosen after seeing the full period, so 2016-2026 is not a clean out-of-sample test of the choices; the clean test is the live record from November 2026. 162 delisted companies had no Bloomberg GICS and were classified by hand. No result is statistically significant at 5% against MSCI World Value (see Summary).", None),
 ("Sources: Bloomberg (MSCI country and sector indices, valuation ratios, WORLD Index compositions, total returns, market caps, original fundamentals, euro money-market rates); Horus Smart Beta 60/40 from Horus AM (USD, converted at month-end EUR/USD). Hypothetical backtest, not investment advice.", None)]
for i, (t, f) in enumerate(txt, 1):
    c = ws.cell(i, 1, t); c.font = f or base; c.alignment = Alignment(wrap_text=True, vertical="top")
ws.column_dimensions["A"].width = 125

# ---------------- Inputs
wi = wb.create_sheet("Inputs"); wi.sheet_view.showGridLines = False
wi.cell(1, 1, "Inputs — change the yellow cells; everything else recalculates").font = title
head(wi, 3, ["Lever", "Value", "Note"], [40, 12, 80])
inp = [("CORE_W", "Core weight in the strategy", 0.70, "Official 70% core / 30% satellite (decided 4 Nov 2026)"),
       ("PORT_W", "Value strategy weight when combined with Horus", 0.50, "Used in Monthly!U (value + Horus portfolio); 1 = value only, 0 = Horus only")]
for i, (n, lab, val, nt) in enumerate(inp, 4):
    wi.cell(i, 1, lab).font = base; c = wi.cell(i, 2, val); c.font = blue; c.fill = FY; c.number_format = "0%"; wi.cell(i, 3, nt).font = base
    name(n, f"Inputs!$B${i}")
wi.cell(7, 1, "Fixed in the backtest (shown for reference)").font = bold
for i, (a, b) in enumerate([("Core trading cost", "0.10% per unit of turnover"), ("Core ETF fees", "0.25% a year"), ("Satellite trading cost", "0.15% per unit of turnover"),
                            ("Satellite withholding-tax haircut", "0.40% a year"), ("Risk rule cut", "50% of equities to cash"), ("Rebalancing", "Monthly, month-end signal, trades next day")], 8):
    wi.cell(i, 1, a).font = base; wi.cell(i, 2, b).font = base

# ---------------- Monthly
wm = wb.create_sheet("Monthly")
cols = ["Month", "Period", "Core return", "Satellite return", "Strategy return", "MSCI World Value", "MSCI World", "Horus Smart Beta (EUR)", "Cash rate (month)",
        "Equity exposure", "Red indicators (prior month end)", "Strategy NAV", "MSCI World Value NAV", "MSCI World NAV", "Strategy drawdown", "MSCI World Value drawdown",
        "MSCI World drawdown", "Core NAV", "Satellite NAV", "Excess vs MSCI World Value", "Value + Horus portfolio"]
head(wm, 1, cols, [9, 10, 10, 10, 10, 11, 10, 11, 9, 9, 10, 10, 11, 10, 10, 11, 10, 10, 10, 11, 11])
for k, t in enumerate(IDX):
    r = k + 2; prev = expo.shift(1).reindex([t]).iloc[0]; nr_prev = nred.shift(1).reindex([t]).iloc[0]
    vals = [t.strftime("%Y-%m"), "Design" if t.year <= 2015 else "Validation", float(core[t]), float(sat[t]), f"=CORE_W*C{r}+(1-CORE_W)*D{r}",
            float(wv[t]), float(mw[t]), (float(he[t]) if pd.notna(he[t]) else None), float(cash[t]), float(prev if pd.notna(prev) else 1.0),
            int(nr_prev) if pd.notna(nr_prev) else None,
            f"=1+E{r}" if k == 0 else f"=L{r-1}*(1+E{r})", f"=1+F{r}" if k == 0 else f"=M{r-1}*(1+F{r})", f"=1+G{r}" if k == 0 else f"=N{r-1}*(1+G{r})",
            f"=L{r}/MAX(L$2:L{r})-1", f"=M{r}/MAX(M$2:M{r})-1", f"=N{r}/MAX(N$2:N{r})-1",
            f"=1+C{r}" if k == 0 else f"=R{r-1}*(1+C{r})", f"=1+D{r}" if k == 0 else f"=S{r-1}*(1+D{r})", f"=E{r}-F{r}",
            f'=IF(H{r}="","",PORT_W*E{r}+(1-PORT_W)*H{r})']
    for j, x in enumerate(vals, 1):
        c = wm.cell(r, j, x); c.font = blue if j in (3, 4, 6, 7, 8, 9, 10, 11) else base; c.border = thin
        if j in (3, 4, 5, 6, 7, 8, 15, 16, 17, 20, 21): c.number_format = PCT2
        elif j == 9: c.number_format = "0.000%"
        elif j == 10: c.number_format = "0%"
        elif j in (12, 13, 14, 18, 19): c.number_format = "0.000"
        if t.year > 2015: c.fill = FV
wm.freeze_panes = "C2"; wm.auto_filter.ref = f"A1:U{LAST}"
wm.conditional_formatting.add(f"J2:J{LAST}", CellIsRule(operator="lessThan", formula=["1"], font=Font(name=F_, size=10, bold=True, color="A33A2B")))

# ---------------- Summary
su = wb.create_sheet("Summary", 2); su.sheet_view.showGridLines = False
su.cell(1, 1, "Summary statistics, net of costs — February 2006 to June 2026").font = title
note(su, 2, "Design = Feb 2006 – Dec 2015 · Validation = Jan 2016 – Jun 2026 (shaded). Sharpe = (CAGR − average cash rate) / volatility. t-statistic = mean monthly excess return / its standard deviation × √months.")
series = [("Strategy 70/30", "E"), ("Core V7", "C"), ("Satellite", "D"), ("MSCI World Value", "F"), ("MSCI World", "G")]
periods = [("Full", 2, LAST), ("Design", 2, MIDROW), ("Validation", MIDROW + 1, LAST)]
hdrs = ["Statistic"] + [f"{s} · {p}" for s, _ in series for p, _, _ in periods]
head(su, 4, hdrs, [30] + [11] * (len(hdrs) - 1))
stats = [("CAGR", lambda c, a, b: f"=EXP(SUMPRODUCT(LN(1+Monthly!{c}{a}:{c}{b})))^(12/COUNT(Monthly!{c}{a}:{c}{b}))-1", PCT),
         ("Volatility", lambda c, a, b: f"=STDEV(Monthly!{c}{a}:{c}{b})*SQRT(12)", PCT),
         ("Average cash rate", lambda c, a, b: f"=(1+AVERAGE(Monthly!I{a}:I{b}))^12-1", PCT),
         ("Sharpe ratio", None, "0.00"),
         ("Positive months", lambda c, a, b: f'=COUNTIF(Monthly!{c}{a}:{c}{b},">0")/COUNT(Monthly!{c}{a}:{c}{b})', "0%"),
         ("Worst month", lambda c, a, b: f"=MIN(Monthly!{c}{a}:{c}{b})", PCT),
         ("Excess return vs MSCI World Value (a year)", lambda c, a, b: f"=SUMPRODUCT(Monthly!{c}{a}:{c}{b}-Monthly!F{a}:F{b})/COUNT(Monthly!{c}{a}:{c}{b})*12", PCT2),
         ("t-statistic of the excess return", lambda c, a, b: f"=(SUMPRODUCT(Monthly!{c}{a}:{c}{b}-Monthly!F{a}:F{b})/COUNT(Monthly!{c}{a}:{c}{b}))/SQRT(SUMPRODUCT((Monthly!{c}{a}:{c}{b}-Monthly!F{a}:F{b}-SUMPRODUCT(Monthly!{c}{a}:{c}{b}-Monthly!F{a}:F{b})/COUNT(Monthly!{c}{a}:{c}{b}))^2)/(COUNT(Monthly!{c}{a}:{c}{b})-1))*SQRT(COUNT(Monthly!{c}{a}:{c}{b}))", "0.00"),
         ("Maximum drawdown", None, PCT)]
def mdd(x): n = (1 + x).cumprod(); return float((n / n.cummax() - 1).min())
ser_py = {"E": O["combo"], "C": core.reindex(IDX), "D": sat.reindex(IDX), "F": wv, "G": mw}
for i, (lab, fn, fmt) in enumerate(stats, 5):
    su.cell(i, 1, lab).font = bold
    col = 2
    for s, c in series:
        for p, a, b in periods:
            cell = su.cell(i, col)
            if lab == "Sharpe ratio": cell.value = f"=({L(col)}5-{L(col)}7)/{L(col)}6"
            elif lab == "Maximum drawdown":
                if p == "Full" and c in "EFG": cell.value = f"=MIN(Monthly!{ {'E':'O','F':'P','G':'Q'}[c] }{a}:{ {'E':'O','F':'P','G':'Q'}[c] }{b})".replace(" ", "")
                else:
                    x = ser_py[c]; x = x.loc[:"2015-12-31"] if p == "Design" else x.loc["2016-01-31":] if p == "Validation" else x
                    cell.value = mdd(x); cell.font = blue; cell.comment = Comment("Computed in Python from this period's monthly returns (peak reset at the start of the period).", "Thoth Ledger")
            elif lab.startswith(("Excess", "t-stat")) and c == "F": cell.value = "—"
            else: cell.value = fn(c, a, b)
            if cell.font != blue: cell.font = base
            cell.number_format = fmt; cell.border = thin
            if p == "Validation": cell.fill = FV
            col += 1
r0 = 16
su.cell(r0, 1, "Correlation of monthly returns (Jan 2007 – Jun 2026, common period with Horus)").font = bold
cn = [("Strategy 70/30", "E"), ("Core V7", "C"), ("Satellite", "D"), ("MSCI World Value", "F"), ("MSCI World", "G"), ("Horus Smart Beta (EUR)", "H")]
head(su, r0 + 1, [""] + [n for n, _ in cn])
for i, (n1, c1) in enumerate(cn):
    su.cell(r0 + 2 + i, 1, n1).font = bold
    for j, (n2, c2) in enumerate(cn):
        x = su.cell(r0 + 2 + i, 2 + j, f"=CORREL(Monthly!{c1}{FIRST_H}:{c1}{LAST},Monthly!{c2}{FIRST_H}:{c2}{LAST})"); x.number_format = "0.00"; x.font = base
su.conditional_formatting.add(f"B{r0+2}:G{r0+7}", ColorScaleRule(start_type="num", start_value=0, start_color="FFFFFF", end_type="num", end_value=1, end_color="C9A46B"))
su.freeze_panes = "B5"

# ---------------- Yearly
wy = wb.create_sheet("Yearly", 3)
head(wy, 1, ["Year", "Period", "Strategy 70/30", "Core V7", "Satellite", "MSCI World Value", "MSCI World", "Horus (EUR)", "Strategy − MSCI World Value", "Months at 50%"], [14, 11, 12, 11, 11, 13, 11, 11, 14, 11])
years = sorted(set(IDX.year))
for i, y in enumerate(years):
    rows = [k + 2 for k, t in enumerate(IDX) if t.year == y]; a, b = rows[0], rows[-1]; r = i + 2
    wy.cell(r, 1, str(y) + (" (Feb-Dec)" if y == 2006 else " (Jan-Jun)" if y == 2026 else "")).font = base
    wy.cell(r, 2, "Design" if y <= 2015 else "Validation").font = base
    for j, c in enumerate("ECDFGH", 3):
        x = wy.cell(r, j, f"=EXP(SUMPRODUCT(LN(1+Monthly!{c}{a}:{c}{b})))-1" if c != "H" else (f"=EXP(SUMPRODUCT(LN(1+Monthly!H{a}:H{b})))-1" if y >= 2007 else "")); x.number_format = PCT; x.font = base
    x = wy.cell(r, 9, f"=C{r}-F{r}"); x.number_format = PCT; x.font = base
    x = wy.cell(r, 10, f'=COUNTIF(Monthly!J{a}:J{b},"<1")'); x.font = base
    if y > 2015:
        for j in range(1, 11): wy.cell(r, j).fill = FV
wy.conditional_formatting.add(f"I2:I{len(years)+1}", CellIsRule(operator="lessThan", formula=["0"], font=Font(name=F_, size=10, color="A33A2B")))
wy.conditional_formatting.add(f"I2:I{len(years)+1}", CellIsRule(operator="greaterThan", formula=["0"], font=Font(name=F_, size=10, color="2E6B4E")))
wy.freeze_panes = "A2"

# ---------------- Horus_Mix (helper columns + table)
hm = wb.create_sheet("Horus_Mix")
hm.cell(1, 1, "Value strategy combined with Horus Smart Beta 60/40 (in EUR), rebalanced monthly — January 2007 to June 2026").font = title
note(hm, 2, "Horus converted from USD at month-end EUR/USD. Weights = share of the value strategy; the rest is Horus. Helper columns from column M.")
head(hm, 4, ["Value weight", "CAGR", "Volatility", "Sharpe", "Max drawdown", "Correlation value/Horus"], [13, 10, 10, 10, 12, 14])
WS = [round(x / 10, 1) for x in range(11)]
start_col = 13; nrows = LAST - FIRST_H + 1
hm.cell(3, start_col, "Month").font = bold
for k in range(nrows): hm.cell(5 + k, start_col, f"=Monthly!A{FIRST_H + k}").font = green
for i, w in enumerate(WS):
    cr, cn_, cd = start_col + 1 + 3 * i, start_col + 2 + 3 * i, start_col + 3 + 3 * i
    hm.cell(3, cr, w).number_format = "0%"; hm.cell(4, cr, "Return"); hm.cell(4, cn_, "NAV"); hm.cell(4, cd, "Drawdown")
    for k in range(nrows):
        r = 5 + k; src = FIRST_H + k
        hm.cell(r, cr, f"={L(cr)}$3*Monthly!E{src}+(1-{L(cr)}$3)*Monthly!H{src}").number_format = PCT2
        hm.cell(r, cn_, f"=1+{L(cr)}{r}" if k == 0 else f"={L(cn_)}{r-1}*(1+{L(cr)}{r})").number_format = "0.000"
        hm.cell(r, cd, f"={L(cn_)}{r}/MAX({L(cn_)}$5:{L(cn_)}{r})-1").number_format = PCT
    R0 = 5 + i; rng = f"{L(cr)}5:{L(cr)}{4 + nrows}"
    hm.cell(R0, 1, f"={L(cr)}3").number_format = "0%"
    hm.cell(R0, 2, f"=EXP(SUMPRODUCT(LN(1+{rng})))^(12/COUNT({rng}))-1").number_format = PCT
    hm.cell(R0, 3, f"=STDEV({rng})*SQRT(12)").number_format = PCT
    hm.cell(R0, 4, f"=(B{R0}-((1+AVERAGE(Monthly!I{FIRST_H}:I{LAST}))^12-1))/C{R0}").number_format = "0.00"
    hm.cell(R0, 5, f"=MIN({L(cd)}5:{L(cd)}{4 + nrows})").number_format = PCT
hm.cell(5, 6, f"=CORREL(Monthly!E{FIRST_H}:E{LAST},Monthly!H{FIRST_H}:H{LAST})").number_format = "0.00"
hm.cell(17, 1, "Best Sharpe in the grid").font = bold
hm.cell(17, 2, "=INDEX(A5:A15,MATCH(MAX(D5:D15),D5:D15,0))").number_format = "0%"
hm.cell(17, 4, "=MAX(D5:D15)").number_format = "0.00"
for r in range(5, 16):
    for c in range(1, 6): hm.cell(r, c).font = base; hm.cell(r, c).border = thin
hm.freeze_panes = "A5"

# ---------------- Optimiser (Excel Solver)
op = wb.create_sheet("Optimiser"); op.sheet_view.showGridLines = False
op.cell(1, 1, "Optimiser — find the value/Horus weight with the best Sharpe ratio (Excel Solver)").font = title
steps = ["1. Enable Solver once: File › Options › Add-ins › Manage Excel Add-ins › Go › tick Solver Add-in.",
         "2. Data › Solver. Set Objective: $B$8 (Sharpe ratio), To: Max.",
         "3. By Changing Variable Cells: $B$5 (value weight).",
         "4. Subject to the Constraints: $B$5 >= 0 and $B$5 <= 1. Solving method: GRG Nonlinear. Solve.",
         "5. Compare with the grid in Horus_Mix. Caution: an optimum fitted on the past is itself a backtest choice — it is information, not a rule."]
for i, s in enumerate(steps, 12): op.cell(i, 1, s).font = base
op.cell(4, 1, "Lever").font = bold; op.cell(4, 2, "Value").font = bold
op.cell(5, 1, "Value weight (changing cell)").font = base; c = op.cell(5, 2, 0.5); c.font = blue; c.fill = FY; c.number_format = "0%"; name("OPT_W", "Optimiser!$B$5")
op.cell(6, 1, "CAGR").font = base; op.cell(7, 1, "Volatility").font = base; op.cell(8, 1, "Sharpe ratio (objective)").font = bold; op.cell(9, 1, "Max drawdown").font = base
op.column_dimensions["A"].width = 34; op.column_dimensions["B"].width = 12
oc = 5
op.cell(3, oc, "Month").font = bold; op.cell(3, oc + 1, "Return").font = bold; op.cell(3, oc + 2, "NAV").font = bold; op.cell(3, oc + 3, "Drawdown").font = bold
for k in range(nrows):
    r = 4 + k; src = FIRST_H + k
    op.cell(r, oc, f"=Monthly!A{src}").font = green
    op.cell(r, oc + 1, f"=OPT_W*Monthly!E{src}+(1-OPT_W)*Monthly!H{src}").number_format = PCT2
    op.cell(r, oc + 2, f"=1+F{r}" if k == 0 else f"=G{r-1}*(1+F{r})").number_format = "0.000"
    op.cell(r, oc + 3, f"=G{r}/MAX(G$4:G{r})-1").number_format = PCT
rng = f"F4:F{3 + nrows}"
op.cell(6, 2, f"=EXP(SUMPRODUCT(LN(1+{rng})))^(12/COUNT({rng}))-1").number_format = PCT
op.cell(7, 2, f"=STDEV({rng})*SQRT(12)").number_format = PCT
c = op.cell(8, 2, f"=(B6-((1+AVERAGE(Monthly!I{FIRST_H}:I{LAST}))^12-1))/B7"); c.number_format = "0.00"; c.font = bold
op.cell(9, 2, f"=MIN(H4:H{3 + nrows})").number_format = PCT

# ---------------- Core_Scores / Core_Holdings / Risk
def matrix_sheet(title_, df, fmt, note_txt, idx_sel=None):
    ws = wb.create_sheet(title_)
    head(ws, 1, ["Month"] + [NAMES[c] for c in LINES], [9] + [11] * len(LINES))
    df = df.reindex(columns=LINES)
    for k, (t, row) in enumerate(df.iterrows()):
        ws.cell(k + 2, 1, t.strftime("%Y-%m")).font = base
        for j, c in enumerate(LINES, 2):
            v = row[c]; cell = ws.cell(k + 2, j, None if pd.isna(v) else float(v)); cell.font = blue; cell.number_format = fmt
    ws.freeze_panes = "B2"; note(ws, len(df) + 3, note_txt); return ws
zz = pd.concat([zc.add_prefix("C_"), zs.add_prefix("S_")], axis=1).loc["2006-01-31":"2026-06-30"]
cs = matrix_sheet("Core_Scores", zz, "0.00", "Value score at each month end: mean z-score of E/P, B/P, dividend yield versus the line's own 10-year history. Higher = cheaper. Decision at the month end, held the following month.")
cs.conditional_formatting.add(f"B2:Z{len(zz)+1}", ColorScaleRule(start_type="num", start_value=-2, start_color="F7E6E1", mid_type="num", mid_value=0, mid_color="FFFFFF", end_type="num", end_value=2, end_color="DDEBDD"))
ch = matrix_sheet("Core_Holdings", W.loc["2006-01-31":"2026-06-30"], "0.0%;;-", "Value selection decided at each month end (12.5% per line before the risk rule). Multiply by the equity exposure (sheet Risk) for the actual weight.")
ch.conditional_formatting.add(f"B2:Z{len(zz)+1}", CellIsRule(operator="greaterThan", formula=["0"], fill=PatternFill("solid", fgColor="DDE4EE")))
wr = wb.create_sheet("Risk")
head(wr, 1, ["Month", "Trend red", "Credit red", "Breadth red", "Red indicators", "Share of lines above 10m average", "Equity exposure decided"], [9, 9, 9, 9, 10, 14, 12])
rr = rs.loc["2006-01-31":"2026-06-30"]
for k, (t, row) in enumerate(rr.iterrows()):
    r = k + 2; wr.cell(r, 1, t.strftime("%Y-%m")).font = base
    for j, c in enumerate(["trend", "credit", "breadth"], 2): x = wr.cell(r, j, int(bool(row[c]))); x.font = blue
    wr.cell(r, 5, f"=SUM(B{r}:D{r})").font = base
    x = wr.cell(r, 6, float(row["breadth_share"])); x.font = blue; x.number_format = "0%"
    x = wr.cell(r, 7, f"=IF(E{r}>=2,0.5,1)"); x.number_format = "0%"; x.font = base
wr.freeze_panes = "B2"; note(wr, len(rr) + 3, "1 = red. Exposure 50% when at least 2 indicators are red (formula), applied over the following month.")

# ---------------- Sat_Holdings / Sat_Scores
sh = wb.create_sheet("Sat_Holdings")
head(sh, 1, ["Key", "Month", "Slot", "Ticker", "Company", "GICS sector", "Country", "Score percentile in sector", "Weight in satellite"], [16, 9, 6, 18, 34, 22, 8, 12, 12])
r = 2
for t in sorted(O["logs"]):
    lg = O["logs"][t]
    for s_, (tk, row) in enumerate(lg.iterrows(), 1):
        vals = [f"{t.strftime('%Y-%m')}|{s_}", t.strftime("%Y-%m"), s_, tk, row["name"], row["sector"], row["cty"], float(row["score_pct"]), float(row["expo"]) / len(lg)]
        for j, x in enumerate(vals, 1):
            c = sh.cell(r, j, x); c.font = blue if j >= 8 else base
            if j == 8: c.number_format = "0%"
            if j == 9: c.number_format = "0.0%"
        r += 1
sh.freeze_panes = "B2"; sh.auto_filter.ref = f"A1:I{r-1}"
sc = wb.create_sheet("Sat_Scores")
head(sc, 1, ["Month", "Ticker", "Company", "GICS sector", "Country", "Market cap (M EUR)", "EBIT/EV", "Book/Price", "FCF/Price", "Sales/EV", "Earnings/Price", "Score (z)", "Score percentile in sector"],
     [9, 18, 34, 22, 8, 12, 9, 9, 9, 9, 9, 9, 11])
SS2 = SS.sort_values(["date", "sector", "score_pct"], ascending=[True, True, False])
for k, row in enumerate(SS2.itertuples(index=False), 2):
    vals = [row.date.strftime("%Y-%m"), row.ticker, row.name, row.sector, row.cty, row.mcap, row.ebit_ev, row.b_p, row.fcf_p, row.s_ev, row.e_p, row.score, row.score_pct]
    for j, x in enumerate(vals, 1):
        if isinstance(x, float) and np.isnan(x): x = None
        c = sc.cell(k, j, x)
        if j == 6: c.number_format = "#,##0"
        elif 7 <= j <= 11: c.number_format = "0.0%"
        elif j == 12: c.number_format = "0.00"
        elif j == 13: c.number_format = "0%"
sc.freeze_panes = "C2"; sc.auto_filter.ref = f"A1:M{len(SS2)+1}"

# ---------------- Explorer
ex = wb.create_sheet("Explorer", 4); ex.sheet_view.showGridLines = False
ex.cell(1, 1, "Explorer — what the strategy did in a given month").font = title
ex.cell(3, 1, "Decision month (month end)").font = bold
c = ex.cell(3, 2, IDX[-1].strftime("%Y-%m")); c.fill = FY; c.font = blue
dv = DataValidation(type="list", formula1=f"=Monthly!$A$2:$A${LAST}", allow_blank=False); ex.add_data_validation(dv); dv.add("B3")
note(ex, 4, "Choose a month: the portfolio decided at that month end is held over the following month. Returns shown are those of the chosen month (earned by the previous decision).")
ex.cell(6, 1, "Returns of the chosen month").font = bold
for i, (lab, col) in enumerate([("Strategy 70/30", "E"), ("Core", "C"), ("Satellite", "D"), ("MSCI World Value", "F"), ("MSCI World", "G")], 7):
    ex.cell(i, 1, lab).font = base; x = ex.cell(i, 2, f'=IFERROR(INDEX(Monthly!{col}$2:{col}${LAST},MATCH($B$3,Monthly!$A$2:$A${LAST},0)),"")'); x.number_format = PCT2; x.font = green
ex.cell(13, 1, "Risk rule at the month end").font = bold
for i, (lab, col, fmt) in enumerate([("Red indicators (of 3)", "E", "0"), ("Equity exposure decided", "G", "0%"), ("Share of lines in uptrend", "F", "0%")], 14):
    ex.cell(i, 1, lab).font = base; x = ex.cell(i, 2, f'=IFERROR(INDEX(Risk!{col}$2:{col}$1000,MATCH($B$3,Risk!$A$2:$A$1000,0)),"")'); x.number_format = fmt; x.font = green
head(ex, 18, ["Core line", "Sleeve", "Value score", "Rank in sleeve", "Weight decided (before risk rule)"], [30, 10, 12, 12, 16])
for i, c_ in enumerate(LINES):
    r = 19 + i; colL = L(2 + i)
    ex.cell(r, 1, NAMES[c_]).font = base; ex.cell(r, 2, "Country" if c_.startswith("C_") else "Sector").font = base
    x = ex.cell(r, 3, f'=IFERROR(INDEX(Core_Scores!{colL}$2:{colL}$1000,MATCH($B$3,Core_Scores!$A$2:$A$1000,0)),"")'); x.number_format = "0.00"; x.font = green
    rng = "$C$19:$C$32" if c_.startswith("C_") else "$C$33:$C$43"
    ex.cell(r, 4, f'=IF(ISNUMBER(C{r}),RANK(C{r},{rng},0),"")').font = base
    x = ex.cell(r, 5, f'=IFERROR(INDEX(Core_Holdings!{colL}$2:{colL}$1000,MATCH($B$3,Core_Holdings!$A$2:$A$1000,0)),"")'); x.number_format = "0.0%;;-"; x.font = green
ex.conditional_formatting.add("E19:E43", CellIsRule(operator="greaterThan", formula=["0"], fill=PatternFill("solid", fgColor="DDE4EE")))
head(ex, 46, ["Satellite slot", "Company", "GICS sector", "Country", "Score percentile in sector"])
for s_ in range(1, 9):
    r = 46 + s_; ex.cell(r, 1, s_).font = base
    for j, col in enumerate("EFGH", 2):
        x = ex.cell(r, j, f'=IFERROR(INDEX(Sat_Holdings!{col}$2:{col}$5000,MATCH($B$3&"|"&$A{r},Sat_Holdings!$A$2:$A$5000,0)),"")'); x.font = green
        if col == "H": x.number_format = "0%"
note(ex, 56, "Ranks: 1 = cheapest in its sleeve. A held line can rank 5th or 6th because of the holding buffer.")

# ---------------- Sources
so = wb.create_sheet("Sources"); so.sheet_view.showGridLines = False
src = [("Item", "Source", "Detail"),
       ("Country indices", "Bloomberg", "MSCI country price (valuation ratios) and net total-return indices, EUR"), ("Sector indices", "Bloomberg", "MSCI World sector price and net total-return indices (M1WO0xx), EUR"),
       ("Valuation ratios", "Bloomberg", "PE_RATIO, PX_TO_BOOK_RATIO, EQY_DVD_YLD_12M, monthly"), ("Risk indicators", "Bloomberg", "MSCI World Net EUR (MSDEWIN), Bloomberg Euro High Yield TR (LP01TREU), Euro Treasury 1-3y TR (LET1TREU)"),
       ("Stock universe", "Bloomberg", "WORLD Index compositions, BDS INDX_MWEIGHT_HIST with END_DATE_OVERRIDE, semi-annual 2005-2025"),
       ("Stock data", "Bloomberg", "TOT_RETURN_INDEX_GROSS_DVDS and CUR_MKT_CAP monthly EUR; fundamentals FILING_STATUS = OR, EQY_FUND_CRNCY EUR"),
       ("GICS of delisted names", "Manual", "162 companies, current GICS definitions (strategies/etf/satellite_lists/manual_gics.csv)"),
       ("Benchmarks", "Bloomberg", "MSCI World Value Net EUR (M1WO000V), MSCI World Net EUR (MSDEWIN)"), ("Cash", "Bloomberg", "3-month Euribor before Oct 2019, €STR after"),
       ("Horus Smart Beta 60/40", "Horus AM", "Monthly USD returns, converted at month-end EUR/USD (Bloomberg)"),
       ("Code", "GitHub", "Fayzzy11/Portfolio-Project, strategies/etf/ (engine.py, satellite_v2.py, export.py) and pre-registrations PREREG_*.md")]
for i, row in enumerate(src, 1):
    for j, x in enumerate(row, 1):
        c = so.cell(i, j, x); c.font = bold if i == 1 else base
so.column_dimensions["A"].width = 24; so.column_dimensions["B"].width = 12; so.column_dimensions["C"].width = 110
out = "/home/claude/work/deliv/Thoth_Value_Strategy_Model.xlsx"; wb.save(out); print(out)
