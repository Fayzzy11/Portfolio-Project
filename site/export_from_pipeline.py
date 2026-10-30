"""Copy the aggregated results of the value pipeline into site/data/ (JSON snapshots the site is built from).

Usage (from the repository root):
    python site/export_from_pipeline.py PATH/TO/value-pipeline [PATH/TO/pitch_content.json]

Only aggregated outputs are exported (portfolio NAVs, statistics, attribution, signal diagnostics).
No security-level Bloomberg series is written: per-stock price histories and peer tables are dropped.
"""
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"


def read_csv(p):
    with open(p, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def table(p):
    head, rows = read_csv(p)
    return {"columns": head[1:], "index": [r[0] for r in rows], "values": [[num(v) for v in r[1:]] for r in rows]}


def md_table(text, heading):
    """First markdown table after a heading, as list of rows."""
    part = text.split(heading, 1)[1]
    out, started = [], False
    for l in part.splitlines():
        if not l.strip().startswith("|"):
            if started:
                break
            continue
        started = True
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if set("".join(cells)) <= set(":- "):
            continue
        out.append(cells)
    return out


def main(pipe, pitch_json=None):
    pipe = Path(pipe)
    o = pipe / "outputs"
    head, rows = read_csv(o / "backtest/nav_weekly.csv")
    nav = {"dates": [r[0] for r in rows], "series": {h: [round(float(v), 5) for v in col]
                                                      for h, col in zip(head[1:], zip(*[r[1:] for r in rows]))}}
    ic_h, ic_r = read_csv(o / "scores/information_coefficient.csv")
    value = {
        "headline": json.loads((o / "backtest/headline.json").read_text()),
        "performance": table(o / "backtest/performance_summary.csv"),
        "calendar": table(o / "backtest/calendar_returns.csv"),
        "nav": nav,
        "ic": [{"date": r[0], "ic": float(r[1]), "n": int(float(r[2]))} for r in ic_r],
        "quintiles": table(o / "scores/quintile_returns.csv"),
        "attribution": [dict(zip(["method", "dimension", "allocation", "selection"], [r[0], r[1], num(r[2]), num(r[3])]))
                        for r in read_csv(o / "risk/attribution_summary.csv")[1]],
        "factors": table(o / "risk/factor_regressions.csv"),
    }
    rh, rr = read_csv(o / "backtest/robustness.csv")
    value["robustness"] = [dict(zip(rh, [r[0], r[1]] + [num(v) for v in r[2:]])) for r in rr]
    dq = (pipe / "docs/data_quality.md").read_text(encoding="utf-8")
    value["coverage"] = md_table(dq, "## 1. Coverage")
    value["replica"] = md_table(dq, "### Benchmark consistency")
    (DATA / "value_developed.json").write_text(json.dumps(value, indent=1))
    print("written", DATA / "value_developed.json")

    if pitch_json:
        pitches = json.loads(Path(pitch_json).read_text(encoding="utf-8"))
        for s in pitches:
            s.pop("prices", None)                     # per-stock price history: licensed, not published
            if s.get("facts"):
                s["facts"].pop("peers", None)         # security-level peer multiples: not published
        (DATA / "pitches.json").write_text(json.dumps(pitches, ensure_ascii=False, indent=1))
        print("written", DATA / "pitches.json")


if __name__ == "__main__":
    main(*sys.argv[1:])
