"""Score OCR output against the benchmark gold, with the numeric failure modes broken out.

OCR output format (one JSON per page, same name as the label file):
    [{"text": "30.77", "box": [x0, y0, x1, y1]}, ...]     # pixel coords of the benchmark image
(`quad` = 4 points is also accepted.)

Each gold NUMBER token is matched to the OCR token whose centre lies inside the gold box (largest
overlap wins). Outcomes per gold number:
    exact          text identical
    decimal_lost   OCR text == gold with '.' removed          (30.77 -> 3077)
    merged         OCR token covers >= 2 gold numbers          (cells glued together)
    digit_error    same length of digits, other digits differ
    other_wrong    anything else
    missing        no OCR token found

usage: bench_score.py <bench_dir> <variant> <ocr_dir>
"""
import json
import sys
from collections import Counter
from pathlib import Path


def bbox(q):
    xs = [p[0] for p in q]
    ys = [p[1] for p in q]
    return min(xs), min(ys), max(xs), max(ys)


def overlap(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return max(w, 0) * max(h, 0)


def ocr_box(t):
    return tuple(t["box"]) if "box" in t else bbox(t["quad"])


def norm(s):
    return s.replace(",", "")


CELL = 40


def build_index(preds):
    """Grid hash of OCR boxes so each gold box only meets nearby candidates."""
    idx = {}
    for p in preds:
        b = ocr_box(p)
        for gx in range(int(b[0] // CELL), int(b[2] // CELL) + 1):
            for gy in range(int(b[1] // CELL), int(b[3] // CELL) + 1):
                idx.setdefault((gx, gy), []).append(p)
    return idx


def candidates(idx, gb):
    seen, out = set(), []
    for gx in range(int(gb[0] // CELL), int(gb[2] // CELL) + 1):
        for gy in range(int(gb[1] // CELL), int(gb[3] // CELL) + 1):
            for p in idx.get((gx, gy), ()):
                if id(p) not in seen:
                    seen.add(id(p))
                    out.append(p)
    return out


def classify(gold, idx):
    gb = bbox(gold["quad"])
    garea = max((gb[2] - gb[0]) * (gb[3] - gb[1]), 1e-6)
    best, best_ov = None, 0.0
    for p in candidates(idx, gb):
        pb = ocr_box(p)
        ov = overlap(gb, pb)
        if ov > best_ov:
            best, best_ov = p, ov
    if best is None or best_ov / garea < 0.3:
        return "missing", None
    g, t = norm(gold["text"]), norm(best["text"].strip())
    if t == g:
        return "exact", best
    if t == g.replace(".", ""):
        return "decimal_lost", best
    pb = ocr_box(best)
    pa = max((pb[2] - pb[0]) * (pb[3] - pb[1]), 1e-6)
    if pa > 1.7 * garea and g in t:
        return "merged", best
    gd, td = [c for c in g if c.isdigit()], [c for c in t if c.isdigit()]
    if len(gd) == len(td):
        return "digit_error", best
    return "other_wrong", best


def score_variant(bench, variant, ocr_dir):
    res = Counter()
    per_page = {}
    for lf in sorted((Path(bench) / "labels" / variant).glob("p*.json")):
        label = json.loads(lf.read_text(encoding="utf-8"))
        of = Path(ocr_dir) / lf.name
        preds = json.loads(of.read_text(encoding="utf-8")) if of.exists() else []
        c = Counter()
        idx = build_index(preds)
        for w in label["words"]:
            if not w["is_number"]:
                continue
            kind, _ = classify(w, idx)
            c[kind] += 1
            if w["has_decimal"]:
                c["dec_total"] += 1
                if kind == "exact":
                    c["dec_exact"] += 1
        per_page[lf.stem] = c
        res.update(c)
    return res, per_page


def summarize(res):
    n = sum(res[k] for k in ("exact", "decimal_lost", "merged", "digit_error", "other_wrong", "missing"))
    lines = [f"numbers: {n}"]
    for k in ("exact", "decimal_lost", "merged", "digit_error", "other_wrong", "missing"):
        lines.append(f"  {k:13s} {res[k]:6d}  {res[k] / n:7.2%}" if n else f"  {k}: 0")
    if res["dec_total"]:
        lines.append(f"  decimal-number exact: {res['dec_exact']}/{res['dec_total']} = "
                     f"{res['dec_exact'] / res['dec_total']:.2%}")
    return "\n".join(lines)


if __name__ == "__main__":
    res, _ = score_variant(sys.argv[1], sys.argv[2], sys.argv[3])
    print(summarize(res))
