"""Re-skin the stock-pitch decks in the Thoth Ledger charter (navy / gold / cream, serif titles) and add the logo on the cover.
Colour-for-colour mapping on every XML part (slides, layouts, master, theme, charts), so layouts and content are untouched.

    python3 tools/decks_style/restyle_thoth.py docs/assets/pitches/*.pptx
"""
import re, sys, zipfile, shutil, tempfile
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches

ROOT = Path(__file__).resolve().parents[2]
LOGO = ROOT / "site/static/brand/mark_256_light.png"
MAP = {  # old green palette -> Thoth Ledger
    "141A17": "0A1A30",  # ink / cover background -> navy
    "0E6B4F": "1B3358",  # accent green (table headers, dots, big numbers) -> navy blue
    "F2F4F1": "F7F3EC",  # light row -> cream
    "2A322E": "142846",  # cover card
    "3A4540": "2A4066",  # cover card border
    "5B6660": "616A78",  # slate text
    "DCE2DD": "E5DCCB",  # hairlines
    "D5DBD6": "DDD3C2",
    "D7EBE2": "EFE3CC",  # mint -> light gold (cover kicker, highlighted rows)
    "EAF4EF": "F6F2EA",  # mint panels -> cream
    "C9DED3": "E5DCCB",
    "EEF2EF": "F8F5EF",
    "E3E8E4": "ECE6DA",
    "B9C4BE": "B8C0CC",  # muted on dark
    "8E9A94": "8C97A8",
    "9AAAA2": "9AA1AB",  # benchmark grey
    "9DB8AC": "A9B4C4",
    "B07A12": "B58F55",  # amber -> gold
    "B23A2E": "A33A2B",  # red (sell / downside)
}
THEME_ACCENT1 = "9A7440"   # kickers ("01  EXECUTIVE SUMMARY") in gold ink
PAT = re.compile(r'(srgbClr val=")([0-9A-Fa-f]{6})(")')


def recolor(xml):
    return PAT.sub(lambda m: m.group(1) + MAP.get(m.group(2).upper(), m.group(2)) + m.group(3), xml)


def restyle(path):
    path = Path(path)
    tmp = Path(tempfile.mkdtemp()) / path.name
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            data = zin.read(it.filename)
            if it.filename.endswith(".xml"):
                x = recolor(data.decode("utf-8"))
                if it.filename.startswith("ppt/theme/"):
                    x = re.sub(r'(<a:accent1>\s*<a:srgbClr val=")[0-9A-Fa-f]{6}', r'\g<1>' + THEME_ACCENT1, x)
                    x = re.sub(r'(<a:majorFont>\s*<a:latin typeface=")[^"]*', r"\g<1>Georgia", x)
                data = x.encode("utf-8")
            zout.writestr(it, data)
    prs = Presentation(str(tmp))
    cover = prs.slides[0]
    if not any(getattr(sh, "name", "") == "thoth logo" for sh in cover.shapes):
        pic = cover.shapes.add_picture(str(LOGO), Inches(12.08), Inches(0.32), Inches(0.62), Inches(0.62)); pic.name = "thoth logo"
    # serif for the cover company name (largest text on slide 1)
    big = max((sh for sh in cover.shapes if sh.has_text_frame and sh.text_frame.text.strip()),
              key=lambda sh: max((r.font.size or 0) for p in sh.text_frame.paragraphs for r in p.runs) if sh.text_frame.paragraphs[0].runs else 0)
    for p in big.text_frame.paragraphs:
        for r in p.runs: r.font.name = "Georgia"
    prs.save(str(path)); shutil.rmtree(tmp.parent)
    print("restyled", path.name)


if __name__ == "__main__":
    for f in sys.argv[1:]:
        restyle(f)
