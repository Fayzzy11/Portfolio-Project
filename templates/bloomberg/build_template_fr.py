"""Construit le classeur d'extraction Bloomberg pour le backtest trend following."""
import datetime as dt
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule

OUT = sys.argv[1] if len(sys.argv) > 1 else "Extract_Trend_Following_Bloomberg.xlsx"

FIRST = 4          # première ligne de données dans Prix
LAST = 7503        # dernière ligne réservée (7 500 lignes ≈ 28 ans de séances)

F = "Arial"
f_base = Font(name=F, size=10)
f_bold = Font(name=F, size=10, bold=True)
f_title = Font(name=F, size=14, bold=True)
f_h = Font(name=F, size=10, bold=True, color="FFFFFF")
f_input = Font(name=F, size=10, color="0000FF")
f_link = Font(name=F, size=10, color="008000")
f_link_b = Font(name=F, size=10, color="008000", bold=True)
f_note = Font(name=F, size=9, italic=True, color="595959")
fill_h = PatternFill("solid", fgColor="1F3864")
fill_in = PatternFill("solid", fgColor="FFFF00")
fill_sub = PatternFill("solid", fgColor="D9E1F2")
thin = Side(style="thin", color="BFBFBF")
box = Border(left=thin, right=thin, top=thin, bottom=thin)
wrap = Alignment(wrap_text=True, vertical="top")

TICKERS = [
    # bloc, ticker, description, statut, future ?
    ("Futures actions", "ES1 Index", "S&P 500 E-mini (CME)", "OK", True),
    ("Futures actions", "VG1 Index", "Euro Stoxx 50 (Eurex)", "OK", True),
    ("Futures actions", "NK1 Index", "Nikkei 225 (Osaka)", "OK", True),
    ("Futures actions", "MES1 Index", "MSCI Emerging Markets (ICE)", "OK", True),
    ("Futures taux", "TY1 Comdty", "US Treasury 10 ans (CBOT)", "OK", True),
    ("Futures taux", "US1 Comdty", "US Treasury Bond 30 ans (CBOT)", "OK", True),
    ("Futures taux", "RX1 Comdty", "Euro-Bund 10 ans (Eurex)", "OK", True),
    ("Futures taux", "G 1 Comdty", "Long Gilt (ICE)", "OK", True),
    ("Futures matières premières", "GC1 Comdty", "Or (COMEX)", "OK", True),
    ("Futures matières premières", "SI1 Comdty", "Argent (COMEX)", "OK", True),
    ("Futures matières premières", "CL1 Comdty", "Pétrole WTI (NYMEX)", "OK", True),
    ("Futures matières premières", "HG1 Comdty", "Cuivre (COMEX)", "OK", True),
    ("Futures matières premières", "C 1 Comdty", "Maïs (CBOT)", "OK", True),
    ("Futures devises", "EC1 Curncy", "EUR/USD (CME)", "OK", True),
    ("Futures devises", "JY1 Curncy", "JPY/USD (CME)", "OK", True),
    ("Futures devises", "BP1 Curncy", "GBP/USD (CME)", "OK", True),
    ("Futures devises", "AD1 Curncy", "AUD/USD (CME)", "OK", True),
    ("Change spot", "EURUSD Curncy", "EUR/USD spot", "OK", False),
    ("Change spot", "EURJPY Curncy", "EUR/JPY spot", "OK", False),
    ("Change spot", "EURGBP Curncy", "EUR/GBP spot", "OK", False),
    ("Taux courts", "USGG3M Index", "US Treasury 3 mois (rendement, %)", "OK", False),
    ("Taux courts", "EUR003M Index", "Euribor 3 mois (%)", "OK", False),
    ("Référence actions", "MSDEWIN Index", "MSCI World Net TR EUR", "OK", False),
    ("Référence actions", "M1WO000V Index", "MSCI World Value Net TR (en USD, converti en EUR dans le backtest)", "OK", False),
]
def second(tk):
    root, yk = tk.rsplit(" ", 1)
    return root[:-1] + "2 " + yk
TICKERS += [("Plan B — 2e génériques", second(tk), "2e contrat : " + desc, "Plan B", True)
            for bloc, tk, desc, stat, fut in list(TICKERS) if fut]
N = len(TICKERS)

wb = Workbook()

# ---------------------------------------------------------------- Parametres
p = wb.active
p.title = "Parametres"
p.sheet_view.showGridLines = False
p.column_dimensions["A"].width = 34
p.column_dimensions["B"].width = 22
p.column_dimensions["C"].width = 70

p["A1"] = "Extraction Bloomberg — backtest trend following multi-actifs"
p["A1"].font = f_title
p["A2"] = "Les cellules jaunes à texte bleu sont les seules à remplir. Tout le reste est calculé."
p["A2"].font = f_note

rows = [
    (4, "Date de début", dt.date(2000, 1, 3), "dd/mm/yyyy", "Premier jour ouvré de 2000."),
    (5, "Date de fin", dt.date(2026, 9, 30), "dd/mm/yyyy", "Fin de période convenue pour le backtest."),
    (6, "Champ extrait", "PX_LAST", "@", "Cours de clôture (settlement pour les futures)."),
]
p["A3"] = "Paramètres d'extraction"
p["A3"].font = f_bold
for r, lab, val, fmt, note in rows:
    p.cell(r, 1, lab).font = f_base
    c = p.cell(r, 2, val)
    c.font, c.fill, c.number_format, c.border = f_input, fill_in, fmt, box
    p.cell(r, 3, note).font = f_note

p["A8"] = "À noter au terminal (obligatoire)"
p["A8"].font = f_bold
notes = [
    (9, "Méthode de roll des génériques", "Ex. : roll à l'expiration, ou sur open interest"),
    (10, "Type d'ajustement des prix", "Ex. : Ratio (attendu), Différence, ou Aucun"),
    (11, "Date de l'extraction", "Ex. : 13/10/2026"),
    (12, "Poste / login utilisé", "Ex. : salle SKEMA, poste 4"),
]
for r, lab, ex in notes:
    p.cell(r, 1, lab).font = f_base
    c = p.cell(r, 2)
    c.font, c.fill, c.border = f_input, fill_in, box
    p.cell(r, 3, ex).font = f_note
p["B11"].number_format = "dd/mm/yyyy"
p["B10"].comment = Comment(
    "Un générique non ajusté contient un saut artificiel à chaque roll de contrat. "
    "Il faut un rétro-ajustement par ratio. Réglage dans les préférences de roll "
    "des futures génériques (GFUT <GO>, nom à confirmer à l'écran) ; BDH reprend ce réglage.",
    "Claude")

p["A14"] = "Mode d'emploi"
p["A14"].font = f_bold
steps = [
    "1. Avant d'ouvrir le fichier : GFUT <GO> → ajustement RATIO et roll AVANT l'expiration (jamais « à l'expiration »). Remplir B9 et B10. Si le réglage est verrouillé sur le poste, extraire quand même : le bloc Plan B (2e génériques) permet de reconstruire les rendements.",
    "2. Onglet Tickers : vérifier les lignes jaunes au terminal (SECF). Compléter le ticker MSCI World Value Net TR EUR et corriger MES1 Index s'il ne répond pas. Tout l'onglet Prix suit automatiquement.",
    "3. Ouvrir le fichier sur le poste Bloomberg, puis ruban Bloomberg > Refresh Workbook. Si des #NAME? apparaissent : Ctrl+Alt+F9 ; s'ils persistent, sélectionner la cellule de formule, F2 puis Entrée.",
    "4. Attendre la fin des « #N/A Requesting Data… ». L'onglet Controles doit afficher « Oui » en B3 (aucune erreur). Lire la colonne Statut ligne par ligne.",
    "5. Contrôle manuel : comparer la dernière valeur de ES1 Index et de CL1 Comdty avec l'écran GP. Un écart = mauvais réglage de roll ou de champ.",
    "6. Figer : Fichier > Enregistrer sous « Extract_Trend_AAAAMMJJ_valeurs.xlsx ». Dans CETTE copie, onglets Tickers puis Prix : Ctrl+A, Ctrl+C, Ctrl+Alt+V > Valeurs. Les formats sont déjà en place, ils restent. Laisser Controles en formules : ils fonctionnent aussi sur des valeurs.",
    "7. Vérifier le figeage : Ctrl+F, chercher « BDH » puis « BDP » dans les formules (Options > Rechercher dans : Formules). Zéro résultat attendu.",
    "8. Envoyer le fichier « _valeurs » à Claude. Garder le fichier avec formules comme modèle réutilisable.",
]
for i, s in enumerate(steps):
    c = p.cell(15 + i, 1, s)
    c.font, c.alignment = f_base, wrap
    p.merge_cells(start_row=15 + i, start_column=1, end_row=15 + i, end_column=3)
    p.row_dimensions[15 + i].height = 30

p["A24"] = f"Quota : {N} tickers × 1 champ en BDH ≈ {N} hits, très en dessous de la limite quotidienne (500 000). Chaque recalcul reconsomme : figer dès que les contrôles sont verts."
p["A24"].font = f_note
p.merge_cells("A24:C24")
p["A24"].alignment = wrap
p.row_dimensions[24].height = 26

# ---------------------------------------------------------------- Tickers
t = wb.create_sheet("Tickers")
t.sheet_view.showGridLines = False
t.freeze_panes = "A5"
widths = [5, 26, 18, 52, 13, 34, 10, 14, 14]
for i, w in enumerate(widths, 1):
    t.column_dimensions[get_column_letter(i)].width = w
t["A1"] = "Univers du backtest"
t["A1"].font = f_title
t["A2"] = "Colonne C (bleu) : ticker modifiable. Colonnes F à H : vérification au terminal via BDP (nom, devise, taille de contrat)."
t["A2"].font = f_note
hdr = ["#", "Bloc", "Ticker", "Description", "Statut", "NAME (BDP)", "CRNCY (BDP)", "FUT_CONT_SIZE (BDP)", "Colonnes dans Prix"]
for j, h in enumerate(hdr, 1):
    c = t.cell(4, j, h)
    c.font, c.fill, c.border = f_h, fill_h, box
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
t.row_dimensions[4].height = 28

for i, (bloc, tick, desc, stat, fut) in enumerate(TICKERS):
    r = 5 + i
    dcol = get_column_letter(1 + 3 * i)
    vcol = get_column_letter(2 + 3 * i)
    vals = [i + 1, bloc, tick, desc, stat,
            f"=BDP(C{r},\"NAME\")",
            f"=BDP(C{r},\"CRNCY\")",
            f"=BDP(C{r},\"FUT_CONT_SIZE\")" if fut else "n/a",
            f"{dcol}:{vcol}"]
    for j, v in enumerate(vals, 1):
        c = t.cell(r, j, v)
        c.font, c.border = f_base, box
    t.cell(r, 3).font = f_input
    if stat in ("À vérifier", "À compléter"):
        for j in (3, 5):
            t.cell(r, j).fill = fill_in
t.cell(5 + N + 1, 2, "Ajustement par ratio requis pour toutes les lignes « Futures » — voir Parametres!B10.").font = f_note

# ---------------------------------------------------------------- Prix
x = wb.create_sheet("Prix")
x.freeze_panes = "A4"
date_fmt = "dd/mm/yyyy"
num_fmt = "#,##0.0000"
for i in range(N):
    dcol_i, vcol_i, scol_i = 1 + 3 * i, 2 + 3 * i, 3 + 3 * i
    dcol, vcol = get_column_letter(dcol_i), get_column_letter(vcol_i)
    r_t = 5 + i
    c = x.cell(1, dcol_i, f"=Tickers!$C${r_t}")
    c.font, c.fill = f_link_b, fill_sub
    x.cell(1, vcol_i).fill = fill_sub
    c = x.cell(2, dcol_i, f"=Tickers!$D${r_t}")
    c.font = Font(name=F, size=8, color="008000")
    for col, lab in ((dcol_i, "Date"), (vcol_i, "PX_LAST")):
        c = x.cell(3, col, lab)
        c.font, c.fill, c.border = f_h, fill_h, box
    x.cell(FIRST, dcol_i,
           f"=BDH({dcol}$1,Parametres!$B$6,Parametres!$B$4,Parametres!$B$5,"
           f"\"Dir=V\",\"Dts=S\",\"Sort=A\",\"Days=T\",\"Per=D\")").font = f_base
    for r in range(FIRST, LAST + 1):
        a = x.cell(r, dcol_i)
        a.number_format = date_fmt
        a.font = f_base
        b = x.cell(r, vcol_i)
        b.number_format = num_fmt
        b.font = f_base
    x.column_dimensions[dcol].width = 11
    x.column_dimensions[vcol].width = 13
    x.column_dimensions[get_column_letter(scol_i)].width = 2

# ---------------------------------------------------------------- Controles
k = wb.create_sheet("Controles")
k.sheet_view.showGridLines = False
k.freeze_panes = "A8"
kw = [5, 16, 26, 11, 13, 13, 10, 13, 34]
for i, w in enumerate(kw, 1):
    k.column_dimensions[get_column_letter(i)].width = w
k["A1"] = "Contrôles avant figeage"
k["A1"].font = f_title
k["A3"] = "Prêt à figer ?"
k["A3"].font = f_bold
k.merge_cells("A3:B3")
first_r, last_r = 8, 8 + N - 1
k["C3"] = f'=IF(AND(SUM(G{first_r}:G{last_r})=0,LEFT(C6,3)<>"NON"),"Oui","Non — voir Statut et test d\'ajustement")'
k["C3"].font = f_bold
k["A4"] = "Seuil saut journalier suspect"
k["A4"].font = f_base
k.merge_cells("A4:B4")
k["C4"] = 0.25
k["C4"].font, k["C4"].fill, k["C4"].number_format = f_input, fill_in, "0%"
k["D4"] = ("Hypothèse : une variation journalière > 25 % sur un future ajusté signale probablement un roll non ajusté "
           "(exception connue : CL1 en avril 2020, prix négatif). Non appliqué aux taux courts.")
k["D4"].font = f_note
k["A5"] = "Nb minimal de points attendu"
k["A5"].font = f_base
k.merge_cells("A5:B5")
k["C5"] = 5000
k["C5"].font, k["C5"].fill, k["C5"].number_format = f_input, fill_in, "#,##0"
k["D5"] = "Hypothèse : ≈ 250 séances × 20 ans. En dessous, l'historique est court (information, pas forcément une erreur)."
k["D5"].font = f_note
k["A6"] = "Test d'ajustement des futures"
k["A6"].font = f_bold
k.merge_cells("A6:B6")
k["C6"] = '=IF(Prix!A4<>DATE(2000,1,3),"Date de début différente — test non applicable",IF(ABS(Prix!B4/1466.75-1)<0.005,"NON AJUSTÉ — refaire avec GFUT en Ratio","Ajusté"))'
k["C6"].font = f_bold
k["D6"] = ("ES1 brut valait 1 466,75 le 03/01/2000 (source : extraction non ajustée du 13/10/2026). "
           "Une série rétro-ajustée par ratio affiche un niveau différent.")
k["D6"].font = f_note
k.conditional_formatting.add("C6", FormulaRule(formula=['$C$6="Ajusté"'], fill=PatternFill("solid", fgColor="C6EFCE")))
k.conditional_formatting.add("C6", FormulaRule(formula=['LEFT($C$6,3)="NON"'], fill=PatternFill("solid", fgColor="F8CBAD")))

khdr = ["#", "Ticker", "Bloc", "Nb points", "Première date", "Dernière date", "Nb erreurs", "Plus forte var. jour.", "Statut"]
for j, h in enumerate(khdr, 1):
    c = k.cell(7, j, h)
    c.font, c.fill, c.border = f_h, fill_h, box
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
k.row_dimensions[7].height = 28

for i in range(N):
    r = first_r + i
    dcol = get_column_letter(1 + 3 * i)
    vcol = get_column_letter(2 + 3 * i)
    rng_v = f"Prix!{vcol}{FIRST}:{vcol}{LAST}"
    rng_v_prev = f"Prix!{vcol}{FIRST - 1}:{vcol}{LAST - 1}"
    rng_d = f"Prix!{dcol}{FIRST}:{dcol}{LAST}"
    rng_all = f"Prix!{dcol}{FIRST}:{vcol}{LAST}"
    cells = [
        i + 1,
        f"=Tickers!C{5 + i}",
        f"=Tickers!B{5 + i}",
        f"=COUNT({rng_v})",
        f"=IF(D{r}=0,\"\",MIN({rng_d}))",
        f"=IF(D{r}=0,\"\",MAX({rng_d}))",
        f"=SUMPRODUCT(ISERROR({rng_all})+ISTEXT({rng_all}))",
        f"=IF(D{r}<2,\"\",_xlfn.AGGREGATE(14,6,ABS({rng_v}/{rng_v_prev}-1)/(ISNUMBER({rng_v})*ISNUMBER({rng_v_prev})),1))",
        (f"=IF(B{r}=\"\",\"Ticker manquant\",IF(G{r}>0,\"Erreurs ou données en attente\","
         f"IF(D{r}=0,\"Aucune donnée\","
         f"IF(F{r}<Parametres!$B$5-7,\"Série arrêtée avant la date de fin\","
         f"IF(AND(C{r}<>\"Taux courts\",LEFT(C{r},6)<>\"Plan B\",H{r}>$C$4),\"Saut suspect : roll non ajusté ?\","
         f"IF(D{r}<$C$5,\"OK — historique court\",\"OK\"))))))"),
    ]
    fmts = ["0", "@", "@", "#,##0", "dd/mm/yyyy", "dd/mm/yyyy", "0", "0.0%", "@"]
    for j, (v, fm) in enumerate(zip(cells, fmts), 1):
        c = k.cell(r, j, v)
        c.font, c.border, c.number_format = f_base, box, fm
    k.cell(r, 2).font = f_link
    k.cell(r, 3).font = f_link

red = PatternFill("solid", fgColor="F8CBAD")
green = PatternFill("solid", fgColor="C6EFCE")
k.conditional_formatting.add(f"I{first_r}:I{last_r}",
                             FormulaRule(formula=[f'LEFT($I{first_r},2)="OK"'], fill=green))
k.conditional_formatting.add(f"I{first_r}:I{last_r}",
                             FormulaRule(formula=[f'LEFT($I{first_r},2)<>"OK"'], fill=red))
k.conditional_formatting.add("C3", FormulaRule(formula=['$C$3="Oui"'], fill=green))
k.conditional_formatting.add("C3", FormulaRule(formula=['$C$3<>"Oui"'], fill=red))
k.cell(last_r + 2, 1, "Nb erreurs compte aussi les textes du type « #N/A Requesting Data… » ou « #N/A N/A » renvoyés par Bloomberg.").font = f_note
k.cell(last_r + 3, 1, "Plus forte var. jour. = plus grande variation absolue d'une séance à la suivante sur la série.").font = f_note

wb.active = 0
wb.save(OUT)
print("saved", OUT)
