"""Thoth Ledger learning notes, version 3 (24 Nov 2026): one study guide per pitch, English and French.

Content: tools/notes_v3/content/<CODE>.py (long-form text, English and French side by side).
Reused: the v3 deck spec of the same pitch (pillars, environment, differences, catalysts, numbers, risks),
site/data/pitches.json (facts, scenarios, sources) and tools/pitch_deck_v3/valmath.py (every valuation number).

    python3 tools/notes_v3/build_notes.py <out_dir> [CODE ...]
"""
import asyncio
import html
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools/pitch_deck_v3"))
sys.path.insert(0, str(ROOT / "tools/pitch_deck_v3/specs"))
import valmath as vm  # noqa: E402
from deck import Ctx, fr_typo  # noqa: E402

PFR = json.loads((ROOT / "site/data/pitches_fr.json").read_text(encoding="utf-8"))
FONTS = ROOT / "site/static/fonts"
LOGO = ROOT / "site/static/brand/mark_256.png"
NB = " "


def load(path, name="X"):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------ formatting
def esc(s):
    return html.escape(str(s), quote=False)


def rich(s):
    """Escape, then **bold**."""
    s = esc(s)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


def num(x, d, lg):
    s = f"{x:,.{d}f}"
    return s.replace(",", NB).replace(".", ",") if lg == "fr" else s


def money(sym, x, lg, d=None):
    if d is None:
        d = 0 if (abs(x) >= 1000 or sym == "¥") else (1 if abs(x) >= 100 else 2)
    n = num(x, d, lg)
    if lg == "fr":
        return f"{n}{NB}{sym.replace('US$', '$' + NB + 'US').replace('HK$', '$HK')}"
    return f"{sym}{n}"


def pct(x, d, lg, sign=False):
    s = num(abs(x) * 100, d, lg) + (NB + "%" if lg == "fr" else "%")
    if sign:
        return ("+" if x >= 0 else "−") + s
    return ("−" + s) if x < 0 else s


SCEN = {"Bear": ("Bear", "Pessimiste"), "Base": ("Base", "Central"), "Bull": ("Bull", "Optimiste")}


# ------------------------------------------------------------------ automatic blocks
def scenarios_table(P, t, lg):
    sym = P["sym"]
    stories = PFR.get(P["code"], {}).get("stories")
    rows = []
    for i, s in enumerate(P["scenarios_out"]):
        story = stories[i] if (lg == "fr" and stories) else s["story"]
        inputs = s["inputs"] if lg == "en" else fr_inputs(s["inputs"])
        cls = "pos" if s["upside"] >= 0 else "neg"
        rows.append(f"<tr{' class=hl' if s['name'] == 'Base' else ''}><td><b>{t(SCEN[s['name']])}</b></td><td>{esc(inputs)}</td>"
                    f"<td class=n><b>{money(sym, s['value'], lg)}</b></td><td class='n {cls}'>{pct(s['upside'], 0, lg, True)}</td><td>{esc(story)}</td></tr>")
    head = t([("Scenario", "Scénario"), ("Inputs", "Hypothèses"), ("Value / share", "Valeur / action"), ("vs price", "vs cours"), ("What has to happen", "Ce qu’il faut voir")])
    return ("<table class=t><thead><tr>" + "".join(f"<th{' class=n' if i in (2, 3) else ''}>{h}</th>" for i, h in enumerate(head)) + "</tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>")


def fr_inputs(x):
    x = re.sub(r"(\d)\.(\d)", r"\1,\2", x)
    x = x.replace("EPS", "BPA").replace("CoE", "CFP").replace("book", "l’actif net").replace("TBV", "ANT").replace(" at ", " à ").replace("yield", "de rendement")
    x = re.sub(r"€(\d[\d,]*)", r"\1" + NB + "€", x)
    x = re.sub(r"US\$(\d[\d,]*)", r"\1" + NB + "$" + NB + "US", x)
    x = re.sub(r"\$(\d[\d,]*)", r"\1" + NB + "$", x)
    x = re.sub(r"¥(\d[\d,]*)", r"\1" + NB + "¥", x)
    x = re.sub(r"(\d) ?%", r"\1" + NB + "%", x)
    x = x.replace("(¥1,221 BVPS)", "(1" + NB + "221" + NB + "¥ par action)").replace("normalised", "normalisé")
    return x


def grid_table(P, spec, t, lg):
    d = spec["valuation"]
    rows, cols, m = vm.grid(P)
    a0, b0 = vm.base_inputs(P)
    px, sym = P["price"], P["sym"]
    rf, cf = d["row_fmt"], d["col_fmt"]
    single = cols == [None]
    head = [t(d["corner"])] + ([t(("Value", "Valeur")), t(("vs price", "vs cours"))] if single else [cf(c, lg) for c in cols])
    out = "<table class='t grid'><thead><tr>" + "".join(f"<th{' class=n' if i else ''}>{esc(h)}</th>" for i, h in enumerate(head)) + "</tr></thead><tbody>"
    for r, vals in zip(rows, m):
        out += f"<tr><td><b>{esc(rf(r, lg))}</b></td>"
        if single:
            v = vals[0]
            cls = "g" if v >= px * 1.15 else ("r" if v <= px * 0.9 else "")
            if abs(r - a0) < 1e-9:
                cls = "b"
            out += f"<td class='n {cls}'>{money(sym, v, lg)}</td><td class='n {cls}'>{pct(v / px - 1, 0, lg, True)}</td>"
        else:
            for c, v in zip(cols, vals):
                cls = "g" if v >= px * 1.15 else ("r" if v <= px * 0.9 else "")
                if abs(r - a0) < 1e-9 and abs(c - b0) < 1e-9:
                    cls = "b"
                out += f"<td class='n {cls}'>{money(sym, v, lg, 0 if (abs(v) >= 1000 or sym == '¥') else 1)}</td>"
        out += "</tr>"
    return out + "</tbody></table>"


def screen_table(P, t, lg):
    f = P["facts"]
    keys = [("e_p", ("Earnings yield (E/P)", "Rendement bénéficiaire (E/P)")), ("b_p", ("Book-to-price (B/P)", "Actif net sur cours (B/P)")),
            ("ebit_ev", ("EBIT / EV", "EBIT / VE")), ("fcf_p", ("Free-cash-flow yield (FCF/P)", "Rendement du free cash flow (FCF/P)")),
            ("s_ev", ("Sales / EV", "CA / VE"))]
    mk = {"e_p": "P/E", "b_p": "P/B", "ebit_ev": "EV/EBIT", "fcf_p": "P/FCF", "s_ev": "EV/Sales"}
    fx = lambda v: t(("n.m.", "n.s.")) if v is None else num(v, 2 if v < 1 else 1, lg) + "x"
    head = t([("Signal", "Signal"), ("z-score in sector", "z-score dans le secteur"), ("Multiple", "Multiple"), (P["name"], P["name"]), ("Peer median", "Médiane des pairs"), ("Sector median", "Médiane du secteur")])
    out = "<table class=t><thead><tr>" + "".join(f"<th{' class=n' if i else ''}>{esc(h)}</th>" for i, h in enumerate(head)) + "</tr></thead><tbody>"
    for k, lab in keys:
        z = f["z"].get(k)
        m = mk[k]
        zs = "—" if z is None else (("+" if z >= 0 else "−") + num(abs(z), 1, lg))
        cls = "" if z is None else ("pos" if z >= 1 else ("neg" if z < 0 else ""))
        out += (f"<tr><td>{t(lab)}</td><td class='n {cls}'><b>{zs}</b></td><td class=n>{t(({'EV/Sales': ('EV/Sales', 'VE/CA'), 'EV/EBIT': ('EV/EBIT', 'VE/EBIT'), 'P/E': ('P/E', 'PER')}.get(m, (m, m))))}</td>"
                f"<td class=n><b>{fx(f['multiples'].get(m))}</b></td><td class=n>{fx(f['peer_median'].get(m))}</td><td class=n>{fx(f['sector_median'].get(m))}</td></tr>")
    out += "</tbody></table>"
    sc = num(f["score"], 2, lg)
    cap = t((f"Composite score {sc} (rank {f['sector_rank']} of {f['sector_n']} in {f['sector']}) at the 31 December 2025 rebalance, on accounts for the fiscal year to {f['fy_used'][:7]} "
             f"(used with a six-month lag). Held at {len(f['dates_held'])} of 10 rebalances since {f['held_since'][:7]}.",
             f"Score composite {sc} (rang {f['sector_rank']} sur {f['sector_n']} dans son secteur) au rebalancement du 31 décembre 2025, sur les comptes de l’exercice clos en {f['fy_used'][:7]} "
             f"(utilisés avec six mois de décalage). Détenu à {len(f['dates_held'])} rebalancements sur 10 depuis {f['held_since'][:7]}."))
    return out + f"<p class=cap>{esc(cap)}</p>"


def table_from_rows(rows, t, hl=(), first_bold=True):
    rows = t(rows)
    short = [all(len(str(r[j])) <= 22 for r in rows[1:]) for j in range(len(rows[0]))]   # numeric-looking column: right-aligned
    out = "<table class=t><thead><tr>" + "".join(f"<th{' class=n' if (i and short[i]) else ''}>{esc(h)}</th>" for i, h in enumerate(rows[0])) + "</tr></thead><tbody>"
    for i, r in enumerate(rows[1:], 1):
        out += f"<tr{' class=hl' if i in hl else ''}>" + "".join(f"<td{' class=n' if (j and short[j]) else ''}>{'<b>' if (j == 0 and first_bold) else ''}{esc(c)}{'</b>' if (j == 0 and first_bold) else ''}</td>" for j, c in enumerate(r)) + "</tr>"
    return out + "</tbody></table>"


# ------------------------------------------------------------------ page
CSS = """
@font-face{font-family:Corm;src:url(FONTS/cormorant-garamond-latin-500-normal.woff2)}
@font-face{font-family:Corm;font-weight:600;src:url(FONTS/cormorant-garamond-latin-600-normal.woff2)}
@font-face{font-family:Corm;font-style:italic;src:url(FONTS/cormorant-garamond-latin-500-italic.woff2)}
@font-face{font-family:SS;src:url(FONTS/source-sans-3-latin-400-normal.woff2)}
@font-face{font-family:SS;font-weight:600;src:url(FONTS/source-sans-3-latin-600-normal.woff2)}
@font-face{font-family:SS;font-weight:700;src:url(FONTS/source-sans-3-latin-700-normal.woff2)}
:root{--navy:#0A1A30;--navy2:#1B3358;--gold:#B58F55;--goldd:#7B5A2A;--cream:#F6F2EA;--line:#E5DCCB;--slate:#4A5363;--pos:#2E6B4E;--neg:#A33A2B}
*{box-sizing:border-box}
html,body{width:210mm}body{margin:0;font:400 10.4pt/1.5 SS,Arial,sans-serif;color:#1d2533}
h1,h2,h3{font-family:Corm,Georgia,serif;color:var(--navy);font-weight:600;margin:0}
.cover{background:var(--navy);color:#C9D0DB;padding:16mm 16mm 12mm;margin:-1px}
.cover .kick{font:600 8.5pt SS;letter-spacing:.14em;text-transform:uppercase;color:var(--gold)}
.cover h1{color:#F6F2EA;font-size:34pt;line-height:1;margin:6mm 0 2mm}
.cover .claim{font:500 21pt/1.15 Corm,Georgia,serif;color:#F6F2EA;margin:4mm 0 1.5mm}
.cover .sub{font:italic 500 13pt/1.3 Corm,Georgia,serif;color:#AEB8C7}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm;margin-top:7mm}
.tile{border:1px solid #2A4066;background:#13294A;padding:3mm 4mm;border-radius:2mm}
.tile b{display:block;font:600 17pt SS;color:#fff}.tile span{font-size:8.5pt;color:#9FAABB}
.tile.r{background:var(--rc);border-color:var(--rc)}.tile.r span{color:#fff}
.cover .by{margin-top:6mm;font-size:8.5pt;color:#8C97A8}
.wrap{padding:0 16mm}
h2{font-size:19pt;margin:9mm 0 3mm;padding-top:3mm;border-top:1.5px solid var(--gold);display:flex;gap:4mm;align-items:baseline;break-after:avoid}
h2 .no{font:600 11pt SS;color:var(--gold)}
h3{font-size:13.5pt;margin:5mm 0 1.5mm;break-after:avoid}
p{margin:0 0 2.6mm}
.lead{font-size:11pt}
.box{background:var(--cream);border-left:3px solid var(--gold);padding:3mm 4.5mm;margin:3mm 0 4mm;break-inside:avoid}
.box.navy{background:var(--navy);color:#DCE2EA;border-left-color:var(--gold)}.box.navy b{color:#fff}
.box .lab{font:700 7.8pt SS;letter-spacing:.12em;text-transform:uppercase;color:var(--goldd);margin-bottom:1mm}
.box.navy .lab{color:var(--gold)}
.formula{font:600 12pt SS;color:var(--navy);text-align:center;padding:3mm;border:1px solid var(--line);background:#fff;margin:2mm 0 3mm}
table.t{width:100%;border-collapse:collapse;margin:2mm 0 3mm;font-size:9.2pt;break-inside:avoid}
table.t th{background:var(--navy);color:#fff;font-weight:600;text-align:left;padding:1.6mm 2mm;font-size:8.6pt}
table.t td{padding:1.5mm 2mm;border-bottom:1px solid var(--line);vertical-align:top}
table.t td:first-child{background:#FBF8F2}
table.t .n{text-align:right;white-space:nowrap}table.t{table-layout:auto}table.t td{overflow-wrap:anywhere}
table.t tr.hl td{background:#EFE3CC}
table.grid td.n{text-align:center}table.grid th.n{text-align:center}
td.g{background:#E3EEE7!important}td.r{background:#F7E6E1!important}td.b{background:#EFE3CC!important;font-weight:700}
.pos{color:var(--pos)}.neg{color:var(--neg)}
.cap{font-size:8.4pt;color:var(--slate);font-style:italic;margin-top:-1mm}
.two{display:grid;grid-template-columns:1fr 1fr;gap:5mm}
.pill{display:grid;grid-template-columns:8mm 1fr;gap:1mm 3mm;margin:2.5mm 0;break-inside:avoid}
.pill .d{width:7mm;height:7mm;border-radius:50%;background:var(--navy2);color:#fff;font:700 9pt/7mm SS;text-align:center}
.pill h4{margin:0;font:700 10.6pt SS;color:var(--navy)}
.pill .ch{font-size:9pt;color:var(--slate);margin:.5mm 0 1mm}
.qa{margin:0 0 3mm;break-inside:avoid}.qa .q{font-weight:700;color:var(--navy)}.qa .q:before{content:"Q  ";color:var(--gold)}
.qa .a{padding-left:5mm;border-left:2px solid var(--line);margin-top:.8mm}
.mem{display:grid;grid-template-columns:1fr 1fr;gap:0 6mm}
.mem div{display:flex;justify-content:space-between;gap:3mm;border-bottom:1px solid var(--line);padding:1.4mm 0;font-size:9.4pt;break-inside:avoid}
.mem b{color:var(--navy);white-space:nowrap}
ol.src{font-size:8.4pt;color:var(--slate);padding-left:5mm}ol.src li{margin-bottom:1mm}
.tag{display:inline-block;font:700 7.5pt SS;letter-spacing:.1em;text-transform:uppercase;padding:.6mm 2mm;border-radius:1mm;background:#EFE3CC;color:var(--goldd)}
.tag.k{background:#F7E6E1;color:var(--neg)}
"""

RCOL = {"Overweight": "#2E6B4E", "Neutral": "#7B5A2A", "Underweight": "#A33A2B", "Sell": "#A33A2B"}


def section(no, title, body):
    return f"<h2><span class=no>{no:02d}</span>{esc(title)}</h2>{body}"


def paras(lst, t, cls=""):
    return "".join(f"<p{' class=' + cls if cls else ''}>{rich(t(p))}</p>" for p in lst)


def build(code, lg, out_dir):
    t = Ctx(lg)
    P = vm.PITCHES[code]
    C = t(load(HERE / "content" / f"{code}.py", "C_" + code).NOTE)
    spec_path = ROOT / "tools/pitch_deck_v3/specs" / f"{code}.py"
    S = t(load(spec_path, "S_" + code).SPEC) if spec_path.exists() else None
    T = lambda en, fr: t((en, fr))
    secs = []
    n = 0

    # cover
    S0 = S or C["cover"]
    rl = S0["rating_label"]
    cover = (f"<div class=cover><div class=kick>{esc(S0['kicker'])}</div><h1>{esc(S0['company'])}</h1>"
             f"<div class=claim>{esc(S0['claim'])}</div><div class=sub>{esc(S0['sub'])}</div><div class=tiles style='--rc:{RCOL[S0['rating']]}'>"
             f"<div class='tile r'><b>{esc(rl)}</b><span>{T('Rating', 'Recommandation')}</span></div>"
             f"<div class=tile><b>{esc(S0['target_s'])}</b><span>{esc(S0['target_cap'])}</span></div>"
             f"<div class=tile><b>{esc(S0['price_s'])}</b><span>{esc(S0['price_cap'])}</span></div>"
             f"<div class=tile><b>{esc(S0['upside_s'])}</b><span>{esc(S0['upside_cap'])}</span></div></div>"
             f"<div class=by>{T('Learning note', 'Note d’apprentissage')} · {esc(C['authors'])} · {T('Student research, not investment advice', 'Travail étudiant, pas un conseil en investissement')}</div></div>")

    # 1 pitch in 60 seconds
    n += 1
    body = (f"<div class='box navy'><div class=lab>{T('Say it like this (about 60 seconds)', 'À dire comme ça (environ 60 secondes)')}</div>{paras(C['pitch60'], t)}</div>"
            f"<div class=box><div class=lab>{T('If you remember one line', 'Si tu ne retiens qu’une phrase')}</div><p><b>{rich(C['killer'])}</b></p></div>")
    secs.append(section(n, T("The pitch in 60 seconds", "Le pitch en 60 secondes"), body))

    # 2 numbers by heart
    n += 1
    mem = "".join(f"<div><span>{esc(a)}</span><b>{esc(b)}</b></div>" for a, b in C["memorise"])
    secs.append(section(n, T("Numbers to know by heart", "Les chiffres à connaître par cœur"), f"<div class=mem>{mem}</div>"))

    # 3 company
    n += 1
    body = paras(C["company"], t)
    if C.get("money"):
        body += f"<div class=box><div class=lab>{T('How it makes money, in one paragraph', 'Comment elle gagne de l’argent, en un paragraphe')}</div><p>{rich(C['money'])}</p></div>"
    if C.get("segments"):
        body += table_from_rows(C["segments"], t)
    secs.append(section(n, T("The company", "La société"), body))

    # 4 environment
    n += 1
    body = paras(C["industry"], t)
    drivers = S["env"]["drivers"] if S else C["drivers"]
    body += f"<h3>{T('The drivers to follow, and how they reach the accounts', 'Les moteurs à suivre, et comment ils arrivent dans les comptes')}</h3>"
    body += "".join(f"<div class=pill><div class=d>{i + 1}</div><div><h4>{esc(h)}</h4><p>{rich(b)}</p></div></div>" for i, (h, b) in enumerate(drivers))
    if C.get("drivers_extra"):
        body += paras(C["drivers_extra"], t)
    secs.append(section(n, T("Industry and environment", "Le secteur et l’environnement"), body))

    # 5 history
    n += 1
    hist = "".join(f"<tr><td class=n style='text-align:left'><b>{esc(d)}</b></td><td>{rich(e)}</td></tr>" for d, e in C["history"])
    body = (f"<table class=t><thead><tr><th>{T('Date', 'Date')}</th><th>{T('What happened', 'Ce qui s’est passé')}</th></tr></thead><tbody>{hist}</tbody></table>")
    if C.get("history_read"):
        body += f"<p>{rich(C['history_read'])}</p>"
    secs.append(section(n, T("What happened: the story of the stock", "Ce qui s’est passé : l’histoire du titre"), body))

    # 6 screen
    n += 1
    body = paras(C["screen"], t)
    if P.get("facts"):
        body += screen_table(P, t, lg)
    secs.append(section(n, T("Why the screen picked it" if P.get("facts") else "Why this stock", "Pourquoi le screen l’a choisi" if P.get("facts") else "Pourquoi ce titre"), body))

    # 7 thesis
    n += 1
    pillars = S["call"]["pillars"] if S else C["pillars"]
    body = ""
    for i, (pl, long_) in enumerate(zip(pillars, C["thesis"])):
        h, chain = pl[0], pl[1]
        body += f"<div class=pill><div class=d>{i + 1}</div><div><h4>{esc(h)}</h4><div class=ch>{esc(chain)}</div>{paras(long_, t)}</div></div>"
    secs.append(section(n, T("The thesis, pillar by pillar", "La thèse, pilier par pilier"), body))

    # 8 where we differ
    n += 1
    body = paras(C["differ_intro"], t)
    cols = S["differ"]["cols"] if S else C["differ_cols"]
    rows = [[T("Topic", "Sujet"), T("The market / the price", "Le marché / le cours"), T("Our view", "Notre vue"), T("Why", "Pourquoi")]]
    for c in cols:
        rows.append([c[0].split("·")[-1].strip(), f"{c[1]}: {c[2]}" if lg == "en" else f"{c[1]}{NB}: {c[2]}", f"{c[4]}", c[5]])
    body += table_from_rows(rows, lambda x: x)
    body += f"<h3>{T('What the bears say, and our answer', 'Ce que disent les sceptiques, et notre réponse')}</h3>"
    body += "".join(f"<div class=qa><div class=q>{esc(a)}</div><div class=a>{rich(b)}</div></div>" for a, b in C["variant"])
    secs.append(section(n, T("Where we differ from the market", "Où nous différons du marché"), body))

    # 9 numbers
    n += 1
    if S:
        body = table_from_rows(S["numbers"]["rows"], lambda x: x, hl=S["numbers"].get("hl", ()))
        body += f"<p class=cap>{esc(S['numbers']['note'])}</p>"
        body += "".join(f"<div class=pill><div class=d>{i + 1}</div><div><h4>{esc(h)}</h4><p>{rich(b)}</p></div></div>" for i, (h, b) in enumerate(S["numbers"]["read"]))
    else:
        body = C["numbers_html"]
    body += paras(C.get("numbers_extra", []), t)
    secs.append(section(n, T("The numbers and how to read them", "Les chiffres et comment les lire"), body))

    # 10 valuation
    n += 1
    V = C["valuation"]
    body = f"<h3>{T('Why this method', 'Pourquoi cette méthode')}</h3>" + paras(V["why"], t)
    body += f"<div class=formula>{esc(V['formula'])}</div>"
    body += f"<h3>{T('The inputs, where they come from, how to defend them', 'Les hypothèses, d’où elles viennent, comment les défendre')}</h3>"
    body += table_from_rows([[T("Input", "Hypothèse"), T("Value", "Valeur"), T("Where it comes from", "D’où elle vient"), T("How to defend it", "Comment la défendre")]] + V["inputs"], lambda x: x)
    body += f"<h3>{T('The calculation, step by step', 'Le calcul, étape par étape')}</h3>" + paras(V["walk"], t)
    body += f"<h3>{T('Three scenarios', 'Trois scénarios')}</h3>" + scenarios_table(P, t, lg)
    if S:
        body += f"<h3>{esc(S['valuation']['grid_title'])}</h3>" + grid_table(P, S, t, lg) + f"<p class=cap>{esc(S['valuation']['grid_note'])}</p>"
    body += f"<h3>{T('What the price implies (reverse the formula)', 'Ce que suppose le cours (inverser la formule)')}</h3>" + paras(V["implied"], t)
    body += f"<h3>{T('Cross-checks', 'Contrôles croisés')}</h3>" + paras(V["cross"], t)
    body += f"<div class=box><div class=lab>{T('Limits of the method: say them before you are asked', 'Limites de la méthode : les dire avant qu’on te les demande')}</div>{paras(V['limits'], t)}</div>"
    secs.append(section(n, T("Valuation, explained", "La valorisation, expliquée"), body))

    # 11 catalysts
    n += 1
    ev = S["timeline"]["events"] if S else C["events"]
    key = S["timeline"]["key"] if S else C["key"]
    rows = "".join(f"<tr><td><b>{esc(d)}</b><br><span class='tag{' k' if i == key else ''}'>{esc(k)}</span></td><td><b>{esc(h)}</b><br>{esc(m)}</td><td>{esc(u)}</td></tr>"
                   for i, (d, k, h, m, u) in enumerate(ev))
    body = (f"<table class=t><thead><tr><th>{T('When', 'Quand')}</th><th>{T('Event and what the market thinks', 'Événement et ce que pense le marché')}</th>"
            f"<th>{T('What we expect, and the impact', 'Ce que nous attendons, et l’impact')}</th></tr></thead><tbody>{rows}</tbody></table>")
    body += f"<p class=cap>{T('Hard: dated and certain to happen. Soft: may slip or not happen. In red: the key catalyst.', 'Ferme : daté et certain. Incertain : peut glisser ou ne pas arriver. En rouge : le catalyseur clé.')}</p>"
    body += f"<div class=box><div class=lab>{T('The key catalyst', 'Le catalyseur clé')}</div>{paras(C['key_catalyst'], t)}</div>"
    secs.append(section(n, T("Catalysts: what moves the stock, and when", "Les catalyseurs : ce qui fait bouger le titre, et quand"), body))

    # 12 risks
    n += 1
    rk = S["risks"]["risks"] if S else C["risks"]
    body = "".join(f"<div class=pill><div class=d style='background:#7B5A2A'>!</div><div><h4>{esc(h)}</h4><p>{rich(b)}</p></div></div>" for h, b in rk)
    body += paras(C.get("risks_extra", []), t)
    trig = S["risks"]["triggers"] if S else C["triggers"]
    body += f"<div class=box><div class=lab>{T('We change the call if', 'Nous changeons d’avis si')}</div><p>{rich(trig)}</p></div>"
    secs.append(section(n, T("Risks, and what would make us change our mind", "Les risques, et ce qui nous ferait changer d’avis"), body))

    # 13 Q&A
    n += 1
    body = "".join(f"<div class=qa><div class=q>{esc(q)}</div><div class=a>{rich(a)}</div></div>" for q, a in C["qa"])
    secs.append(section(n, T("Interview questions, with answers", "Questions d’entretien, avec les réponses"), body))

    # 14 glossary
    n += 1
    body = "<table class=t><tbody>" + "".join(f"<tr><td style='width:32%'><b>{esc(a)}</b></td><td>{rich(b)}</td></tr>" for a, b in C["glossary"]) + "</tbody></table>"
    secs.append(section(n, T("Glossary", "Glossaire"), body))

    # 15 sources
    n += 1
    src = "".join(f"<li>{esc(s['label'])}{(' — ' + esc(s['url'])) if s.get('url') else ''}</li>" for s in P["sources"])
    note = C.get("data_note") or ("Company figures come from the filings above. Prices, consensus and 52-week ranges are third-party (as of the pitch date) and will be replaced by Bloomberg in December 2026. "
                                  "Screen data come from the Thoth Ledger Bloomberg extract (31 Dec 2025 rebalance). Every valuation number in this note is computed from site/data/pitches.json.",
                                  "Les chiffres de la société viennent des publications ci-dessus. Cours, consensus et plus haut/plus bas 52 semaines sont de source tierce (à la date du pitch) et seront remplacés par Bloomberg en décembre 2026. "
                                  "Les données du screen viennent de l’extraction Bloomberg de Thoth Ledger (rebalancement du 31 déc. 2025). Chaque chiffre de valorisation de cette note est calculé à partir de site/data/pitches.json.")
    body = f"<ol class=src>{src}</ol><p class=cap>{esc(t(note))}</p>"
    secs.append(section(n, T("Sources", "Sources"), body))

    css = CSS.replace("FONTS", FONTS.as_uri())
    doc = (f"<!doctype html><html lang={lg}><head><meta charset=utf-8><style>{css}</style></head><body>{cover}<div class=wrap>{''.join(secs)}</div></body></html>")
    if lg == "fr":
        doc = re.sub(r"(\d) (%|€|Md€|M€|Md\$|M\$|\$|¥|Md¥|pb|x\b)", "\\1" + NB + "\\2", doc)
    stem = (S or C["cover"])["stem"]
    name = f"{stem}_learning_note{'' if lg == 'en' else '_FR'}"
    hp = Path(out_dir) / f"{name}.html"
    hp.write_text(doc, encoding="utf-8")
    return hp, name, t(("Learning note", "Note d’apprentissage")), (S or C["cover"])["company"]


async def to_pdf(items, out_dir):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for hp, name, lab, comp in items:
            pg = await b.new_page()
            await pg.goto(hp.as_uri())
            await pg.wait_for_timeout(300)
            foot = (f"<div style='width:100%;font:7.5pt Arial;color:#7B8494;padding:0 16mm;display:flex;justify-content:space-between'>"
                    f"<span>Thoth Ledger · {esc(comp)} · {esc(lab)}</span><span><span class=pageNumber></span> / <span class=totalPages></span></span></div>")
            await pg.pdf(path=str(Path(out_dir) / f"{name}.pdf"), format="A4", print_background=True, display_header_footer=True,
                         header_template="<div></div>", footer_template=foot, margin={"top": "12mm", "bottom": "14mm", "left": "0", "right": "0"})
            await pg.close()
            print(name)
        await b.close()


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    codes = sys.argv[2:] or sorted(p.stem for p in (HERE / "content").glob("*.py") if not p.stem.startswith("_"))
    items = [build(c, lg, out) for c in codes for lg in ("en", "fr")]
    asyncio.run(to_pdf(items, out))
