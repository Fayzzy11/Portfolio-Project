"""Bloomberg workbook #2 (3 Nov 2026): index market caps (cap-weighted value tilt), sector net TR, wider trend universe."""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import get_column_letter as L
from openpyxl.formatting.rule import CellIsRule

NAVY = "0B1F3A"; GOLD = "B08D57"; CREAM = "F7F2E7"; GREY = "F1EFEA"; OKF = "DDEBDD"; KOF = "F6E3E0"; AMB = "F6EDD9"
H = Font(bold=True, color="FFFFFF"); B = Font(bold=True)
FH = PatternFill("solid", fgColor=NAVY); FG = PatternFill("solid", fgColor=GREY); FA = PatternFill("solid", fgColor=AMB)

COUNTRIES = [("US", "MXUS Index"), ("JP", "MXJP Index"), ("GB", "MXGB Index"), ("FR", "MXFR Index"), ("DE", "MXDE Index"),
             ("CH", "MXCH Index"), ("NL", "MXNL Index"), ("IT", "MXIT Index"), ("ES", "MXES Index"), ("SE", "MXSE Index"),
             ("DK", "MXDK Index"), ("CA", "MXCA Index"), ("AU", "MXAU Index"), ("HK", "MXHK Index")]
SECTORS = [("EN", "Energy"), ("MT", "Materials"), ("IN", "Industrials"), ("CD", "Consumer Discretionary"), ("CS", "Consumer Staples"),
           ("HC", "Health Care"), ("FN", "Financials"), ("IT", "Information Technology"), ("TC", "Communication Services"),
           ("UT", "Utilities"), ("RE", "Real Estate")]
# Wider trend universe: candidates, the Tests tab tells which ones the room's licence returns
TREND_NEW = [
    ("BD_EGB13", "Euro govt 1-3y", "Bonds", "LET1TREU Index"),
    ("BD_EGB10", "Euro govt 10y+", "Bonds", "LET5TREU Index"),
    ("BD_UST13", "US Treasury 1-3y", "Bonds", "LT01TRUU Index"),
    ("BD_UST20", "US Treasury 20y+", "Bonds", "LUTLTRUU Index"),
    ("BD_EILB", "Euro inflation-linked govt", "Bonds", "BEIG1T Index"),
    ("BD_TIPS", "US TIPS", "Bonds", "LBUTTRUU Index"),
    ("BD_EHY", "Euro high yield", "Bonds", "LP01TREU Index"),
    ("EQ_EUR", "MSCI Europe net (EUR)", "Equities", "MSDEE15N Index"),
    ("EQ_UK", "MSCI UK net", "Equities", "NDDUUK Index"),
    ("EQ_PXJ", "MSCI Pacific ex Japan net", "Equities", "NDDUPXJ Index"),
    ("EQ_WSC", "MSCI World Small Cap net", "Equities", "NCUDWI Index"),
    ("CM_BRENT", "Brent (BCOM TR)", "Commodities", "BCOMCOTR Index"),
    ("CM_NG", "Natural gas (BCOM TR)", "Commodities", "BCOMNGTR Index"),
    ("CM_IND", "Industrial metals (BCOM TR)", "Commodities", "BCOMINTR Index"),
    ("CM_PREC", "Precious metals (BCOM TR)", "Commodities", "BCOMPRTR Index"),
    ("CM_LIVE", "Livestock (BCOM TR)", "Commodities", "BCOMLITR Index"),
]

wb = openpyxl.Workbook(); wb.calculation.fullCalcOnLoad = True
def name(n, ref): wb.defined_names[n] = DefinedName(n, attr_text=ref)
def head(ws, r, vals):
    for i, v in enumerate(vals, 1):
        c = ws.cell(r, i, v); c.fill = FH; c.font = H; c.alignment = Alignment(wrap_text=True, vertical="center")

# ---------------- Mode d'emploi
ws = wb.active; ws.title = "Mode d'emploi"
lines = [
    ("Extraction n°2 — capitalisations des indices, secteurs en net TR, univers trend élargi (mensuel)", "t"),
    ("", None),
    ("À quoi ça sert :", "b"),
    ("• Capi : poids de chaque pays et secteur dans le MSCI World, mois par mois. Sert à la version « inclinée » de la stratégie value "
     "(on part des poids de l'indice et on surpondère les marchés bon marché, au lieu de tout équipondérer).", None),
    ("• Secteurs_TR : rendements net TR des secteurs MSCI World (aujourd'hui on les reconstruit avec prix + dividendes estimés).", None),
    ("• Trend_Plus : marchés supplémentaires pour diversifier le trend following (obligations courtes/longues, indexées, high yield, "
     "autres actions, autres matières premières).", None),
    ("", None),
    ("Étapes (environ 15 minutes) :", "b"),
    ("1. Ouvre le fichier sur le terminal, ENREGISTRE SOUS dans ton dossier, attends 1 à 2 minutes.", None),
    ("2. Onglet Tests : colonne Statut. Les « KO » sont normaux pour certains tickers (licence de la salle). Ne corrige rien, SAUF ceci :", None),
    ("   si TOUTE la colonne CAP est KO, le champ de capitalisation n'est pas le bon pour les indices. Leçon Bloomberg : tape "
     "MXUS Index FLDS <GO>, cherche « market cap », repère le mnémonique (ex. CUR_MKT_CAP, INDX_MARKET_CAP…), "
     "écris-le dans Config!C2 (CAP_FIELD). Tout le classeur se met à jour.", None),
    ("3. Onglet Config : passe RUN_Capi à OUI, attends que l'onglet soit rempli (plus de « #N/A Requesting »), puis Ctrl+A, Ctrl+C, "
     "Ctrl+Alt+V, V, Entrée (collage en valeurs).", None),
    ("4. Même chose, dans l'ordre, pour RUN_Secteurs_TR puis RUN_Trend_Plus. Colle aussi l'onglet Tests en valeurs à la fin.", None),
    ("5. Enregistre sous ETF_EXTRACT_2_AAAAMMJJ.xlsx et envoie-le à Claude.", None),
    ("", None),
    ("Si une cellule affiche #N/A Review : plafond Bloomberg. Arrête-toi, enregistre, envoie le fichier tel quel.", None),
    ("Rappel : ce fichier contient des données Bloomberg brutes. Il ne va ni sur le site ni sur GitHub.", None),
]
for i, (t, f) in enumerate(lines, 1):
    c = ws.cell(i, 1, t); c.alignment = Alignment(wrap_text=True, vertical="top")
    if f == "t": c.font = Font(bold=True, size=14, color=NAVY)
    if f == "b": c.font = Font(bold=True, color=GOLD)
ws.column_dimensions["A"].width = 130

# ---------------- Config
ws = wb.create_sheet("Config"); head(ws, 1, ["Nom", "Rôle", "Valeur", "Note"])
cfg = [("CAP_FIELD", "Champ capitalisation", "CUR_MKT_CAP", "À changer ici seulement si la colonne CAP des Tests est KO (voir FLDS)"),
       ("CCY", "Devise des rendements", "EUR", "Conversion par Bloomberg"),
       ("CAP_CCY", "Devise des capitalisations", "USD", "Même devise pour tous : seuls les poids relatifs comptent"),
       ("S_START", "Début", "19991231", "Même historique que l'extraction n°1"),
       ("S_END", "Fin", "20260930", "Même fin que l'extraction n°1"),
       ("T_DATE", "Date des tests", "20250930", ""),
       ("RUN_Capi", "Interrupteur Capi", "NON", "Passe à OUI, attends, colle en valeurs, puis le suivant"),
       ("RUN_Secteurs_TR", "Interrupteur Secteurs_TR", "NON", ""),
       ("RUN_Trend_Plus", "Interrupteur Trend_Plus", "NON", "")]
for i, row in enumerate(cfg, 2):
    for j, v in enumerate(row, 1): ws.cell(i, j, v)
    name(row[0], f"Config!$C${i}")
    if row[0] == "CAP_FIELD": ws.cell(i, 3).fill = FA
for c, w in zip("ABCD", [16, 28, 16, 70]): ws.column_dimensions[c].width = w

def bdh(t, f, ccy, run):
    fld = "CAP_FIELD" if f == "CAP" else f'"{f}"'
    extra = f',"Currency",{ccy}' if ccy else ""
    return f'=IF({run}="OUI",BDH("{t}",{fld},S_START,S_END,"Per","M","Days","A","Fill","P"{extra}),"")'

def block(title, series, note):
    ws = wb.create_sheet(title); ws.cell(1, 1, note).font = Font(bold=True, color=NAVY)
    for k, (lab, t, f, ccy) in enumerate(series):
        c = 1 + 3 * k
        ws.cell(2, c, lab).font = B; ws.cell(3, c, t); ws.cell(3, c + 1, f if f != "CAP" else "=CAP_FIELD")
        ws.cell(4, c, "Date").fill = FG; ws.cell(4, c + 1, "Valeur").fill = FG
        ws.cell(5, c, bdh(t, f, ccy, "RUN_" + title))
        for x, w in ((c, 11), (c + 1, 13), (c + 2, 2)): ws.column_dimensions[L(x)].width = w
    ws.freeze_panes = "A5"

SEC_PX = [(f"MXWO0{c} Index", nm) for c, nm in SECTORS]
SEC_NET = [(f"M1WO0{c} Index", nm) for c, nm in SECTORS]  # MSCI World sector net TR (USD); Tests confirms licence
cap = [(f"{c} · capi", t, "CAP", "CAP_CCY") for c, t in COUNTRIES] + \
      [(f"{nm} · capi", t, "CAP", "CAP_CCY") for t, nm in SEC_PX] + [("MSCI World · capi", "MXWO Index", "CAP", "CAP_CCY")]
block("Capi", cap, "Capitalisation mensuelle des indices pays et secteurs MSCI (champ = Config!CAP_FIELD), même devise pour tous.")
block("Secteurs_TR", [(f"{nm} · net TR", t, "PX_LAST", "CCY") for t, nm in SEC_NET],
      "Secteurs MSCI World en net total return, convertis en EUR.")
block("Trend_Plus", [(f"{code} {nm}", t, "PX_LAST", "CCY") for code, nm, ac, t in TREND_NEW],
      "Marchés supplémentaires pour le trend following, indices de rendement total, en EUR.")

# ---------------- Tests
ws = wb.create_sheet("Tests", 1)
ws.cell(1, 1, "Tests : chaque ticker à la date T_DATE. OK = la donnée existe.").font = Font(bold=True, color=NAVY)
head(ws, 3, ["Ticker", "Rôle", "NAME", "PX_LAST", "CAP", "Statut"])
tick = [(t, f"Capi pays {c}", True) for c, t in COUNTRIES] + [(t, f"Capi secteur {nm}", True) for t, nm in SEC_PX] + \
       [("MXWO Index", "Capi MSCI World", True)] + [(t, f"Secteur net TR {nm}", False) for t, nm in SEC_NET] + \
       [(t, f"Trend {code} ({ac})", False) for code, nm, ac, t in TREND_NEW]
for i, (t, role, is_cap) in enumerate(tick, 4):
    ws.cell(i, 1, t); ws.cell(i, 2, role); ws.cell(i, 3, f'=BDP("{t}","NAME")')
    ws.cell(i, 4, f'=BDH("{t}","PX_LAST",T_DATE,T_DATE,"Dts","H")')
    if is_cap:
        ws.cell(i, 5, f'=BDH("{t}",CAP_FIELD,T_DATE,T_DATE,"Dts","H")')
        ws.cell(i, 6, f'=IF(COUNT(D{i}:E{i})=2,"OK",IF(COUNT(D{i}:E{i})=0,"KO","PARTIEL"))')
    else:
        ws.cell(i, 6, f'=IF(COUNT(D{i})=1,"OK","KO")')
n = 3 + len(tick)
ws.cell(2, 1, "Résumé :").font = B
ws.cell(2, 2, f'=COUNTIF(F4:F{n},"OK")&" OK / "&COUNTIF(F4:F{n},"KO")&" KO / "&COUNTIF(F4:F{n},"PARTIEL")&" partiel"')
for c, w in zip("ABCDEF", [18, 32, 36, 12, 16, 10]): ws.column_dimensions[c].width = w
ws.freeze_panes = "A4"
for v, f in (("OK", OKF), ("KO", KOF), ("PARTIEL", AMB)):
    ws.conditional_formatting.add(f"F4:F{n}", CellIsRule(operator="equal", formula=[f'"{v}"'], fill=PatternFill("solid", fgColor=f)))
ws.sheet_view.showGridLines = True
wb["Mode d'emploi"].sheet_view.showGridLines = False
wb.save("/home/claude/work/ETF_Extraction_2.xlsx")
print("tests", len(tick), "| capi", len(cap), "| sect TR", len(SEC_NET), "| trend+", len(TREND_NEW))
