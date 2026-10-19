"""Validation layer (no ground truth needed) + accuracy scoring (when gold exists).

Checks (each failure is an 'issue' with severity):
  E0 INVALID_NUMBER    cell is not a parseable number            (critical)
  E1 PARSE_ERROR       row/cell count mismatch                    (critical)
  E2 NON_MONOTONIC     content must be non-decreasing with sounding (critical)
  E3 DECIMAL_JUMP      step >> neighbours' step (30.77 -> 3077 signature) (critical)
  E4 CROSS_MISMATCH    sounding-table value != table-of-centers volume at same
                       sounding (independent redundancy in the document) (critical)
  E5 MISSING_GRID      sounding grid has gaps                      (critical)
  E6 FORMAT            decimals differ from rest of the column (30.77 -> 3077) (critical)
  E7 SPIKE             value deviates from local trend beyond rounding noise (review: suspicious, needs human look)
  E8 DECREASING        vcg / volume / weight decreases with sounding (critical)
  W1 ORPHAN_LABEL      label without values                        (warning)
"""
import csv
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


def load(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def tkey(t):
    """Loose tank key: drops port/stbd/&/#/() so 'Ballast Tank #1 Port & Stbd' ~ 'Ballast Tank #1'."""
    for ch in "()#&":
        t = t.replace(ch, " ")
    return " ".join(w for w in t.lower().split() if w not in ("port", "stbd"))


def ulp_of(d):
    return Decimal(1).scaleb(d.as_tuple().exponent)


def spikes(pts):
    """pts: [(key, Decimal)] sorted, equally spaced. Return keys whose value deviates from
    the local linear trend by far more than rounding noise (robust, window-median scale)."""
    n = len(pts)
    if n < 5:
        return []
    x = [float(v) for _, v in pts]
    u = float(min(ulp_of(v) for _, v in pts))
    r = [None] + [x[i] - (x[i - 1] + x[i + 1]) / 2 for i in range(1, n - 1)] + [None]
    ar = [abs(v) if v is not None else None for v in r]

    def scale(i):
        w = sorted(a for j, a in enumerate(ar) if a is not None and abs(j - i) >= 2 and abs(j - i) <= 7)
        return w[len(w) // 2] if w else 0.0

    out = []
    # A single wrong cell d shows up as r_i = d and r_{i-1} ~ r_{i+1} ~ -d/2 (opposite sign).
    # A genuine bend in the tank geometry does not have that signature.
    for i in range(1, n - 1):
        thr = max(2.5 * u, 5 * scale(i))
        if ar[i] <= thr:
            continue
        a_, b_ = r[i - 1], r[i + 1]
        both = (a_ is None or a_ * r[i] < 0) and (b_ is None or b_ * r[i] < 0)
        side = min([abs(v) for v in (a_, b_) if v is not None] or [0])
        if both and side >= 0.3 * ar[i]:
            out.append(pts[i][0])
    # edges: one-sided extrapolation, same shape test against the single neighbour residual
    e0 = x[0] - (2 * x[1] - x[2])
    if abs(e0) > max(4 * u, 5 * scale(0)) and r[1] * e0 < 0 and abs(r[1]) >= 0.3 * abs(e0):
        out.append(pts[0][0])
    e1 = x[-1] - (2 * x[-2] - x[-3])
    if abs(e1) > max(4 * u, 5 * scale(n - 1)) and r[-2] * e1 < 0 and abs(r[-2]) >= 0.3 * abs(e1):
        out.append(pts[-1][0])
    return out


def validate(rows):
    issues = []
    snd = defaultdict(dict)    # tank -> sounding_in -> Decimal
    ctr = defaultdict(lambda: defaultdict(dict))  # tank -> field -> sounding_in -> Decimal
    units = {}                 # (tank, table_type, field) -> unit
    fmt = defaultdict(list)    # (tank, table_type, field) -> [(sounding_in, decimals, page)]
    for r in rows:
        if r["field"] == "ORPHAN_LABEL":
            issues.append(("W1", "warning", r["page"], r["tank"], r["sounding_in"], "label without values"))
            continue
        if r["field"].startswith("PARSE_ERROR"):
            issues.append(("E1", "critical", r["page"], r["tank"], r["sounding_in"], r["field"]))
            continue
        try:
            v = Decimal(r["value"])
        except InvalidOperation:
            issues.append(("E0", "critical", r["page"], r["tank"], r["sounding_in"],
                           f"not a number: {r['value']!r}"))
            continue
        si = int(r["sounding_in"])
        units[(r["tank"], r["table_type"], r["field"])] = r["unit"]
        fmt[(r["tank"], r["table_type"], r["field"])].append((si, -v.as_tuple().exponent, r["page"]))
        if r["table_type"] == "sounding":
            snd[(r["tank"], r["unit"])][si] = v
        else:
            ctr[r["tank"]][r["field"]][si] = v

    # E6 format consistency: every cell of a column keeps the same number of decimals
    for (tank, tt, field), cells in fmt.items():
        cnt = defaultdict(int)
        for _, dp, _ in cells:
            cnt[dp] += 1
        mode = max(cnt, key=cnt.get)
        for si, dp, page in cells:
            if dp != mode:
                issues.append(("E6", "critical", page, tank, si, f"{field}: {dp} decimals, column uses {mode}"))

    # sounding tables
    for (tank, _u), d in snd.items():
        keys = sorted(d)
        if keys != list(range(keys[0], keys[-1] + 1)):
            issues.append(("E5", "critical", "", tank, "", "gaps in sounding grid"))
        steps = [(keys[i], d[keys[i + 1]] - d[keys[i]]) for i in range(len(keys) - 1)]
        for k, s in steps:
            if s < 0:
                issues.append(("E2", "critical", "", tank, k, f"step {s}"))
        pos = sorted(s for _, s in steps if s > 0)
        if pos:
            med = pos[len(pos) // 2]
            for k, s in steps:
                if med > 0 and s > 10 * med and s > 0:
                    issues.append(("E3", "critical", "", tank, k, f"step {s} vs median {med}"))
        if keys == list(range(keys[0], keys[-1] + 1)):
            for k in spikes([(k, d[k]) for k in keys]):
                issues.append(("E7", "review", "", tank, k, "deviates from local trend"))

    # centers tables
    for tank, fields in ctr.items():
        for field, d in fields.items():
            keys = sorted(d)
            if len(keys) > 1 and keys != list(range(keys[0], keys[-1] + 1, 6)):
                issues.append(("E5", "critical", "", tank, "", f"gaps in centers grid ({field})"))
            elif len(keys) > 4 and field != "weight" and field != "volume":
                for k in spikes([(k, d[k]) for k in keys]):
                    issues.append(("E7", "review", "", tank, k, f"{field} deviates from local trend"))
            if field in ("vcg", "volume", "weight"):
                for a, b in zip(keys, keys[1:]):
                    if d[b] < d[a] - ulp_of(d[a]):
                        issues.append(("E8", "critical", "", tank, b, f"{field} decreases {d[a]} -> {d[b]}"))
        # cross-check against sounding tables (independent copy of the same numbers)
        for field in ("volume", "weight"):
            if field not in fields:
                continue
            cu = units.get((tank, "centers", field))
            cands = [k for k in snd if k[1] == cu and norm(k[0]) == norm(tank)] or                     [k for k in snd if k[1] == cu and tkey(k[0]) == tkey(tank)]
            if len(cands) != 1:
                continue
            sd = snd[cands[0]]
            for si, b in fields[field].items():
                a = sd.get(si)
                if a is None:
                    continue
                ulp = max(ulp_of(a), ulp_of(b))
                if abs(a - b) > ulp:
                    issues.append(("E4", "critical", "", tank, si, f"sounding={a} centers {field}={b}"))
    return issues, snd, ctr


def norm(t):
    """Exact-ish tank key (keeps Port/Stbd): 'Cargo Tank #1 (Port)' ~ 'Cargo Tank #1 Port'."""
    for ch in "()#&":
        t = t.replace(ch, " ")
    return " ".join(t.lower().split())


def score(pred_csv, gold_csv):
    """Exact-match cell accuracy vs hand-built gold set (string compare, Decimal-normalised)."""
    key = lambda r: (r["tank"], r["table_type"], r["sounding_in"], r["field"])
    pred = {key(r): r["value"] for r in load(pred_csv)}
    gold = {key(r): r["value"] for r in load(gold_csv)}
    ok = sum(1 for k, v in gold.items() if k in pred and Decimal(pred[k]) == Decimal(v))
    miss = [k for k in gold if k not in pred]
    wrong = [(k, pred[k], gold[k]) for k in gold if k in pred and Decimal(pred[k]) != Decimal(gold[k])]
    return dict(gold=len(gold), correct=ok, missing=len(miss), wrong=len(wrong),
                accuracy=ok / len(gold) if gold else None, wrong_examples=wrong[:10])


if __name__ == "__main__":
    csv_path = sys.argv[1]
    rows = load(csv_path)
    issues, snd, ctr = validate(rows)
    n_cells = len(rows)
    print(f"records={n_cells} tanks(sounding)={len(snd)} tanks(centers)={len(ctr)}")
    by = defaultdict(int)
    for i in issues:
        by[i[0]] += 1
    print("issues:", dict(by) or "none")
    for i in issues[:25]:
        print("  ", i)
    if len(sys.argv) > 2:
        print(score(csv_path, sys.argv[2]))
