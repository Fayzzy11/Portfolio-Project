# Research Ledger — site source

The website in `docs/` (GitHub Pages) is generated from this folder, in English (`docs/`) and French (`docs/fr/`).
One command rebuilds every page in both languages:

```bash
pip install markdown          # once
python site/build_site.py     # writes docs/, leaves docs/trend-following/ and docs/downloads/ untouched
```

Then commit `site/` and `docs/` and push: GitHub Pages republishes within a minute.

## What lives where

| Path | Content | Edit by hand? |
|---|---|---|
| `site/content/en/` and `site/content/fr/` | About, journal, methodology, anti-bias checklist and research notes, one folder per language | Yes |
| `site/data/pitches_fr.json` | French text of each pitch (headline, thesis, valuation, catalysts, triggers) | Yes |
| `site/data/horus_smart_beta.json` | Monthly returns of Horus Smart Beta 60/40 (copy of `assets/data/backtest.json` in the HORUS_AM repo) | Copy each month |
| `site/lib.py` | Shared helpers: page shell, navigation, UI strings in both languages, tables, SVG charts | Rarely |
| `site/data/value_developed.json` | Aggregated backtest results (NAV, statistics, IC, attribution, robustness) | No: exported from the pipeline |
| `site/data/pitches.json` | The eight pitches (thesis, macro, financials, valuation, learning note) | No: exported from the pitch content |
| `site/static/site.css`, `site.js` | Design system and behaviour (filters, chart, theme) | Rarely |
| `site/build_site.py` | Page templates, charts (SVG), dataset and field catalogue (`DATASETS`, `FIELDS`) | For structure changes |
| `docs/assets/pitches/` | Decks (.pptx and .pdf), the only downloadable files of the pitches | Replace files, keep the names |

## Everyday edits

**Add a journal entry.** Add a row to the table in `site/content/en/journal.md` and `site/content/fr/journal.md`, rebuild.

**Publish a research note.** Copy an existing file in `site/content/en/research/` (and its French twin in `site/content/fr/research/`), rename it `YYYY-MM-DD-short-title.md`,
fill the front matter (`title`, `date`, `summary`) and write the body in Markdown. Rebuild: the note appears on the
Research page and the home page.

```markdown
---
title: What the note is about, in one line
date: 12 Nov 2026
summary: One or two sentences shown in the list.
---
## The question
...
```

**Refresh the strategy results after a new backtest.** From the repository root:

```bash
python site/export_from_pipeline.py PATH/TO/value-pipeline PATH/TO/pitch_content.json
python site/build_site.py
```

The export keeps aggregated series only. It drops per-stock price histories and peer tables (Bloomberg licence).

**Add a pitch (for example Intel, Sell).** Add an entry to `site/data/pitches.json` with the same fields as the others (rating
`"Sell"` is supported), its French text to `site/data/pitches_fr.json`, and the deck as
`docs/assets/pitches/<CODE>_<Name>_pitch.pptx` (+ `.pdf`). Rebuild: the card, the page and the strategy links appear.

**Update Horus Smart Beta.** Copy `assets/data/backtest.json` from the HORUS_AM repository to `site/data/horus_smart_beta.json`, rebuild.

**Update a pitch.** Edit the pitch content file in the pitch workspace (`content/<CODE>.py`), rebuild `content.json`,
re-export, rebuild the site. Replace the deck and note files in `docs/assets/pitches/` with the same names.

**Add a field to the data dictionary.** Append a tuple to `FIELDS` in `build_site.py`:
`(mnemonic, meaning, dataset, function, pitfall)`.

## Adding a strategy page

1. Put the aggregated results in `site/data/<strategy>.json`.
2. Write a `build_<strategy>()` function modelled on `build_value()` (sections built with `section()`, tables with `tbl()`,
   charts with the `svg_*` helpers).
3. Add a card to `build_strategies()` and call the function in `main()`.

## Design rules

- Palette and fonts are tokens in `site.css` (`--green`, `--ink`, `--paper`…); dark mode redefines the same tokens.
- Numbers are always set in IBM Plex Mono; reading text in Source Serif 4; structure in Archivo.
- Every chart is inline SVG generated at build time, except the interactive performance chart (`site.js`).
- Pages print cleanly: the learning-note PDFs are the pitch pages printed with the print stylesheet.
