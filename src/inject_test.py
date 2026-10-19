"""Error-injection test: how many single-cell OCR-style errors does validate.py miss?

For each error type, mutate ONE random cell of the clean baseline, run the
validator, and count the trial as detected if it yields any critical issue
that the clean data does not already have. Reports detection rate per error
type and per cell class, plus examples of misses.

usage: inject_test.py out/baseline.csv [N_per_type] [seed]
"""
import copy
import random
import sys
from collections import defaultdict

import validate as V

CONFUSE = {"1": "7", "7": "1", "0": "8", "8": "0", "5": "6", "6": "5",
           "3": "8", "9": "4", "2": "7", "4": "9"}


def digits_idx(s):
    return [i for i, c in enumerate(s) if c.isdigit()]


# Each injector returns (new_value | None=skip, delete_next: bool)
def decimal_drop(v, rng):
    return (v.replace(".", ""), False) if "." in v else (None, False)


def decimal_shift(v, rng):
    if "." not in v:
        return None, False
    i = v.index(".")
    d = v.replace(".", "")
    j = max(1, min(len(d) - 1, i + rng.choice([-1, 1])))
    out = d[:j] + "." + d[j:]
    return (out if out != v else None), False


def digit_drop(v, rng):
    idx = digits_idx(v)
    if len(idx) < 2:
        return None, False
    i = rng.choice(idx)
    out = v[:i] + v[i + 1:]
    return (out if out.strip(".") else None), False


def digit_insert(v, rng):
    i = rng.choice(digits_idx(v))
    return v[:i] + rng.choice(v[i]) + v[i:], False  # duplicate a digit (stutter)


def digit_swap(v, rng):
    idx = [i for i in range(len(v) - 1) if v[i].isdigit() and v[i + 1].isdigit() and v[i] != v[i + 1]]
    if not idx:
        return None, False
    i = rng.choice(idx)
    return v[:i] + v[i + 1] + v[i] + v[i + 2:], False


def digit_confuse(v, rng):
    idx = [i for i in digits_idx(v) if v[i] in CONFUSE]
    if not idx:
        return None, False
    i = rng.choice(idx)
    return v[:i] + CONFUSE[v[i]] + v[i + 1:], False


def cell_merge(v, rng):
    return "MERGE", True  # handled specially: concat with next cell, delete next


def cell_delete(v, rng):
    return "DELETE", False


INJECTORS = dict(decimal_drop=decimal_drop, decimal_shift=decimal_shift, digit_drop=digit_drop,
                 digit_insert=digit_insert, digit_swap=digit_swap, digit_confuse=digit_confuse,
                 cell_merge=cell_merge, cell_delete=cell_delete)


def cell_class(r):
    return "sounding" if r["table_type"] == "sounding" else f"centers:{r['field']}"


def issue_keys(issues):
    return {(i[0], i[2], i[3], str(i[4])) for i in issues if i[1] in ("critical", "review")}


def located(found, r):
    """Strict credit: an issue counts only if it points at the mutated tank and (when it
    carries a sounding height) within 12 inches of the mutated cell."""
    tk = V.tkey(r["tank"])
    si = int(r["sounding_in"])
    for code, page, tank, h in found:
        if V.tkey(tank) != tk:
            continue
        if h in ("", "None") or abs(int(h) - si) <= 12:
            return True
    return False


CLEAN_REVIEW = CLEAN_CELLS = 0


def run(rows, n, seed):
    """Light version: validation rules are independent across tank groups (same V.tkey), so each
    trial re-validates only the mutated tank's group instead of the whole document."""
    global CLEAN_REVIEW, CLEAN_CELLS
    groups = defaultdict(list)                   # tkey -> rows (document order kept)
    for r in rows:
        groups[V.tkey(r["tank"])].append(r)
    clean = {g: issue_keys(V.validate(rs)[0]) for g, rs in groups.items()}
    CLEAN_REVIEW = sum(len(v) for v in clean.values())
    CLEAN_CELLS = len(rows)
    rng = random.Random(seed)
    cand = [(g, p) for g, rs in groups.items() for p, r in enumerate(rs)
            if r["field"] != "ORPHAN_LABEL" and not r["field"].startswith("PARSE_ERROR") and r["value"]]
    stats = defaultdict(lambda: [0, 0])          # (err, class) -> [detected, total]
    misses = defaultdict(list)
    for err, fn in INJECTORS.items():
        done = 0
        while done < n:
            g, p = rng.choice(cand)
            grp = groups[g]
            r = grp[p]
            new, _ = fn(r["value"], rng)
            if new is None:
                continue
            mut = list(grp)
            if new == "DELETE":
                del mut[p]
            elif new == "MERGE":
                q = p + 1
                if q >= len(grp) or grp[q]["page"] != r["page"] or grp[q]["tank"] != r["tank"]                         or not grp[q]["value"] or grp[q]["table_type"] != r["table_type"]                         or (r["table_type"] == "centers" and grp[q]["sounding_in"] != r["sounding_in"]):
                    continue
                mut[p] = dict(r, value=r["value"] + grp[q]["value"])
                del mut[q]
            else:
                mut[p] = dict(r, value=new)
            found = issue_keys(V.validate(mut)[0]) - clean[g]
            k = (err, cell_class(r))
            stats[k][1] += 1
            if located(found, r):
                stats[k][0] += 1
            elif len(misses[err]) < 6:
                misses[err].append((r["tank"], r["page"], r["sounding_in"], r["field"], r["value"], new))
            done += 1
    return stats, misses


def report(stats, misses, n):
    by_err = defaultdict(lambda: [0, 0])
    by_cls = defaultdict(lambda: [0, 0])
    for (e, c), (d, t) in stats.items():
        by_err[e][0] += d; by_err[e][1] += t
        by_cls[c][0] += d; by_cls[c][1] += t
    tot_d = sum(v[0] for v in by_err.values()); tot_t = sum(v[1] for v in by_err.values())
    L = [f"# 오류 주입 테스트 결과 (오류유형당 {n}건, 1셀씩 주입)", "",
         f"정상 데이터에서 검수 후보로 뜨는 셀(오탐): {CLEAN_REVIEW}/{CLEAN_CELLS} = {CLEAN_REVIEW / CLEAN_CELLS:.2%}", "",
         f"**전체 검출률 {tot_d}/{tot_t} = {tot_d / tot_t:.1%}  |  미검출 {tot_t - tot_d}건**", "",
         "## 오류 유형별", "| 유형 | 검출 | 전체 | 검출률 |", "|---|---|---|---|"]
    for e, (d, t) in by_err.items():
        L.append(f"| {e} | {d} | {t} | {d / t:.1%} |")
    L += ["", "## 셀 종류별", "| 셀 | 검출 | 전체 | 검출률 |", "|---|---|---|---|"]
    for c, (d, t) in sorted(by_cls.items()):
        L.append(f"| {c} | {d} | {t} | {d / t:.1%} |")
    L += ["", "## 미검출 예시 (tank, page, sounding_in, field, 원본 → 변조)"]
    for e, ms in misses.items():
        for m in ms:
            L.append(f"- {e}: {m[0]} p{m[1]} s={m[2]} {m[3]}: `{m[4]}` → `{m[5]}`")
    return "\n".join(L)


if __name__ == "__main__":
    rows = V.load(sys.argv[1])
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    stats, misses = run(rows, n, seed)
    txt = report(stats, misses, n)
    out = sys.argv[4] if len(sys.argv) > 4 else "out/inject_report.md"
    open(out, "w", encoding="utf-8").write(txt)
    print(txt)
