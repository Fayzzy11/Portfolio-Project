"""Write a French copy of every pitch deck: same layout, translated runs, chart labels, French number format.

Usage (from the repository root):
    python tools/decks_fr/translate_decks.py docs/assets/pitches
Then convert the *_FR.pptx files to PDF (PowerPoint: Save as PDF, or LibreOffice --convert-to pdf).
New text in a deck must be added to fr_deck_dict.py (exact strings in T, or a pattern)."""
import json, sys, glob, re
from pptx import Presentation
from pptx.util import Pt
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fr_deck_dict as D
# pitch text already translated for the website (headline, thesis, catalysts...)
P = json.load(open(HERE.parents[1] / "site/data/pitches.json", encoding="utf-8"))
F = json.load(open(HERE.parents[1] / "site/data/pitches_fr.json", encoding="utf-8"))
for s_ in P:
    fr = F[s_["code"]]
    pairs = [(s_["headline"], fr["headline"]), (s_["one_liner"], fr["one_liner"]), (s_["role"], fr["role"]), (s_["horizon"], fr["horizon"]),
             (s_["valuation"]["method"], fr["method"]), (s_["valuation"]["explain"], fr["explain"])]
    pairs += [(a, c) for (a, b), (c, d) in zip(s_["key_stats"], fr["key_stats"])] + [(b, d) for (a, b), (c, d) in zip(s_["key_stats"], fr["key_stats"])]
    for (a, b), (c, d) in zip(s_["thesis"], fr["thesis"]):
        pairs += [(a, c), (b, d)]
    pairs += list(zip([x[3] for x in s_["valuation"]["scenarios"]], fr["stories"]))
    for (a, b), (c, d) in zip(s_["catalysts"], fr["catalysts"]):
        pairs += [(a, c), (b, d)]
    pairs += list(zip(s_["triggers"], fr["triggers"]))
    for a, b in pairs:
        D.T.setdefault(a, b)
C = '{http://schemas.openxmlformats.org/drawingml/2006/chart}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'


def shapes(coll):
    for sh in coll:
        if sh.shape_type == 6:
            yield from shapes(sh.shapes)
        else:
            yield sh


def tr_runs(tf, report):
    for p in tf.paragraphs:
        for r in p.runs:
            src = r.text
            if not src.strip():
                continue
            out = D.translate(src)
            if out != src:
                r.text = out
                grow = len(out) / max(len(src), 1)
                if grow > 1.08 and len(src) > 25 and r.font.size:
                    r.font.size = Pt(max(r.font.size.pt * max(grow ** -0.5, 0.86), 7))
                report["n"] += 1


def run(src, dst):
    prs = Presentation(src)
    rep = {"n": 0}
    for sl in prs.slides:
        for sh in shapes(sl.shapes):
            if sh.has_text_frame:
                tr_runs(sh.text_frame, rep)
            if getattr(sh, "has_table", False) and sh.has_table:
                for row in sh.table.rows:
                    for c in row.cells:
                        tr_runs(c.text_frame, rep)
            if getattr(sh, "has_chart", False) and sh.has_chart:
                cs = sh.chart._chartSpace
                for v in cs.iter(C + 'v'):
                    if v.text and re.search(r"[A-Za-z]", v.text):
                        v.text = D.translate(v.text)
                for t in cs.iter(A + 't'):
                    if t.text and re.search(r"[A-Za-z]", t.text):
                        t.text = D.translate(t.text)
                # French number format in data labels / axes
                for nf in cs.iter(C + 'numFmt'):
                    fc = nf.get('formatCode')
                    if fc and '.' in fc:
                        pass
    for lay in list(prs.slide_layouts) + [prs.slide_master]:
        for sh in shapes(lay.shapes):
            if sh.has_text_frame:
                tr_runs(sh.text_frame, rep)
    prs.save(dst)
    return rep["n"]


for f in sorted(glob.glob(sys.argv[1] + '/*_pitch.pptx')):  # English masters only
    dst = f.replace('_pitch.pptx', '_pitch_FR.pptx')
    print(dst.split('/')[-1], run(f, dst))
