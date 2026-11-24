"""Valuation arithmetic shared by the v3 decks and the learning notes.

Every number shown on a valuation slide or in a note is computed here from site/data/pitches.json,
so the deck, the note and the site cannot disagree.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PITCHES = {p["code"]: p for p in json.loads((ROOT / "site/data/pitches.json").read_text(encoding="utf-8"))}


def book_per_share(p):
    """Book (or tangible book) per share used by the valuation."""
    v = p["valuation"]
    if v["kind"] == "ptbv":
        return v["tbvps"]
    if v["kind"] in ("pb", "pb_just"):
        return p["price"] / v["pb_now"]
    return None


def value(p, a, b=None):
    """Value per share for one set of inputs (a, b) in the pitch's own method."""
    v = p["valuation"]; k = v["kind"]
    if k == "pe":                      # a = EPS, b = P/E
        return a * b
    if k == "ptbv":                    # a = RoTE, b = cost of equity
        return (a - v["g"]) / (b - v["g"]) * v["tbvps"]
    if k == "pb_just":                 # a = ROE, b = cost of equity
        return (a - v["g"]) / (b - v["g"]) * book_per_share(p)
    if k == "fcf":                     # a = FCF (bn), b = required yield
        return a / b * 1000 / v["shares_m"]
    if k == "pb":                      # a = P/B multiple
        return a * book_per_share(p)
    if k == "norm_pe":                 # a = factor on normalised EPS, b = P/E
        return a * v["normal_eps_usd"] * b * v["fx"]
    raise ValueError(k)


def grid(p):
    """Sensitivity grid: (row label kind, column label kind, rows, cols, matrix)."""
    k = p["valuation"]["kind"]
    if k == "pe" and p["code"] == "RNO_FP":
        rows, cols = [4.0, 5.0, 6.0, 7.0, 8.0], [4.0, 5.0, 6.0, 7.0, 8.0]
    elif k == "pe":
        rows, cols = [3.5, 4.25, 5.0, 5.75, 6.5], [10.0, 11.0, 12.0, 13.0, 14.0]
    elif k == "ptbv":
        rows, cols = [0.10, 0.11, 0.12, 0.13, 0.135], [0.105, 0.11, 0.115, 0.12, 0.125]
    elif k == "pb_just":
        rows, cols = [0.055, 0.06, 0.065, 0.075, 0.085], [0.065, 0.07, 0.075]
    elif k == "fcf" and p["code"] == "CA_FP":
        rows, cols = [1.0, 1.2, 1.4, 1.6, 1.7], [0.10, 0.11, 0.12, 0.13]
    elif k == "fcf":
        rows, cols = [2.3, 2.6, 3.0, 3.3], [0.075, 0.085, 0.10, 0.11]
    elif k == "pb":
        rows, cols = [0.45, 0.55, 0.65, 0.75, 0.85, 0.95], [None]
    elif k == "norm_pe":
        rows, cols = [0.7, 1.0, 1.5], [6.0, 7.0, 8.0, 9.0, 10.0]
    m = [[value(p, r, c) for c in cols] for r in rows]
    return rows, cols, m


def base_inputs(p):
    sc = {s[0]: s for s in p["valuation"]["scenarios"]}
    return sc["Base"][1], sc["Base"][2]


def implied(p):
    """What today's price implies in the pitch's own method (one input solved, the other at the base case)."""
    v = p["valuation"]; k = v["kind"]; a, b = base_inputs(p); px = p["price"]
    out = {}
    if k == "pe":
        out["pe_on_our_eps"] = px / a                      # multiple paid on our EPS
        out["eps_at_our_pe"] = px / b                      # EPS the price implies at our multiple
    elif k == "ptbv":
        pb = px / v["tbvps"]; g = v["g"]
        out["p_tbv"] = pb
        out["rote_at_our_coe"] = g + pb * (b - g)
        out["coe_at_our_rote"] = g + (a - g) / pb
    elif k == "pb_just":
        pb = v["pb_now"]; g = v["g"]
        out["p_b"] = pb
        out["roe_at_our_coe"] = g + pb * (b - g)
    elif k == "fcf":
        mcap = px * v["shares_m"] / 1000
        out["fcf_at_our_yield"] = b * mcap                 # FCF the price implies at our yield
        out["yield_on_our_fcf"] = a / mcap
    elif k == "pb":
        out["p_b"] = v["pb_now"]
    elif k == "norm_pe":
        out["pe_on_normal_eps"] = px / v["fx"] / v["normal_eps_usd"]
    return out


def sensitivities(p):
    """Value change per share for one simple move in each input (at the base case)."""
    v = p["valuation"]; k = v["kind"]; a, b = base_inputs(p); base = value(p, a, b)
    s = {}
    if k == "pe":
        s["eps_step"] = (0.5, value(p, a + 0.5, b) - base)
        s["pe_step"] = (1.0, value(p, a, b + 1) - base)
    elif k in ("ptbv", "pb_just"):
        s["roe_step"] = (0.01, value(p, a + 0.01, b) - base)
        s["coe_step"] = (-0.005, value(p, a, b - 0.005) - base)
    elif k == "fcf":
        s["fcf_step"] = (0.1, value(p, a + 0.1, b) - base)
        s["yield_step"] = (-0.01, value(p, a, b - 0.01) - base)
    elif k == "pb":
        s["pb_step"] = (0.1, value(p, a + 0.1) - base)
    elif k == "norm_pe":
        s["pe_step"] = (1.0, value(p, a, b + 1) - base)
        s["eps_step"] = (0.5, 0.5 * b * v["fx"])          # +US$0.50 of normalised EPS
    return s


if __name__ == "__main__":
    for c, p in PITCHES.items():
        if c == "INTC_US":
            continue
        a, b = base_inputs(p)
        print(c, round(value(p, a, b), 2), "site", p["target"], implied(p), {k: (x, round(y, 2)) for k, (x, y) in sensitivities(p).items()})
