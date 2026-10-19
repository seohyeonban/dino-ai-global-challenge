"""Baseline extractor: text-layer PDF -> standard long-format records.

Schema (one row per measurement):
    source, page, tank, table_type, sounding_in, value, unit, field

Only handles digital PDFs with a text layer (the sample). Scanned/image
tables need the OCR path (see PLAN.md), which must output the same schema.
All numbers are kept as strings until validation so '30.77' can never
silently become 3077 through float/int coercion.
"""
import csv
import re
import sqlite3
import sys
from decimal import Decimal
from pathlib import Path

import pymupdf

NUM = r"-?\d[\d,]*(?:\.\d+)?"
SOUND_RE = re.compile(r"(\d+)'\s*-\s*(\d+)\"")


def lines_of(page, y_tol=2.5):
    """Group words into visual lines (top->bottom), words sorted left->right."""
    words = page.get_text("words")  # x0,y0,x1,y1,text,...
    words.sort(key=lambda w: ((w[1] + w[3]) / 2, w[0]))
    out, cur, cy = [], [], None
    for w in words:
        yc = (w[1] + w[3]) / 2
        if cy is None or abs(yc - cy) <= y_tol:
            cur.append(w)
            cy = yc if cy is None else (cy + yc) / 2
        else:
            out.append(sorted(cur, key=lambda a: a[0]))
            cur, cy = [w], yc
    if cur:
        out.append(sorted(cur, key=lambda a: a[0]))
    return [[w[4] for w in ln] for ln in out]


def detect_unit(text):
    t = text.lower()
    if "barrels" in t:
        return "BBL"
    if "l. tons" in t or "long ton" in t:
        return "LT"
    if "gallons" in t:
        return "GAL"
    return ""


def parse_sounding_page(page, src, pno):
    lines = lines_of(page)
    head = " ".join(" ".join(l) for l in lines[:6])
    m = re.search(r"SOUNDING TABLE for\s+(.*?)\s+(Volume|Weight)", head)
    tank = m.group(1).strip() if m else ""
    unit = detect_unit(head)
    rows = []
    for ln in lines:
        low = " ".join(ln).lower()
        if ("volume in" in low or "weight in" in low) and detect_unit(low):
            unit = detect_unit(low)  # a page may hold several tables (e.g. gallons + L.tons)
            continue
        while ln and ln[0].isalpha():  # margin labels such as 'Feet'
            ln = ln[1:]
        if len(ln) >= 12 and ln == [str(i) for i in range(len(ln))]:  # inch-column header 0..11
            continue
        if 2 <= len(ln) <= 13 and ln[0].isdigit() and all(re.fullmatch(NUM, t) for t in ln[1:]):
            ft = int(ln[0])
            for inch, v in enumerate(ln[1:]):
                rows.append(dict(source=src, page=pno, tank=tank, table_type="sounding",
                                 sounding_in=ft * 12 + inch, value=v.replace(",", ""),
                                 unit=unit, field=f"content_{unit}"))
    return rows


def parse_centers_page(page, src, pno):
    lines = lines_of(page)
    head = " ".join(" ".join(l) for l in lines[:4])
    m = re.search(r"Table of Centers for\s+(.*?)\s+Center of Gravity", head)
    tank = m.group(1).strip() if m else ""
    full = " ".join(" ".join(l) for l in lines[:10]).lower()
    fields = ((["volume"] if "volume" in full else [])
              + (["weight"] if "weight" in full else []) + ["vcg", "lcg", "tcg"])
    vol_unit = "GAL" if "gallons" in full else "BBL"
    units = {"volume": vol_unit, "weight": "LT", "vcg": "ft", "lcg": "ft", "tcg": "ft"}
    rows = []
    for ln in lines:
        joined = " ".join(ln)
        ms = list(SOUND_RE.finditer(joined))
        if not ms:
            continue
        for i, mm in enumerate(ms):
            end = ms[i + 1].start() if i + 1 < len(ms) else len(joined)
            nums = re.findall(NUM, joined[mm.end():end])
            if len(nums) == 0:
                rows.append(dict(source=src, page=pno, tank=tank, table_type="centers",
                                 sounding_in=int(mm.group(1)) * 12 + int(mm.group(2)),
                                 value="", unit="", field="ORPHAN_LABEL"))
                continue
            if len(nums) != len(fields):
                rows.append(dict(source=src, page=pno, tank=tank, table_type="centers",
                                 sounding_in=int(mm.group(1)) * 12 + int(mm.group(2)),
                                 value="", unit="", field=f"PARSE_ERROR({len(nums)} nums)"))
                continue
            si = int(mm.group(1)) * 12 + int(mm.group(2))
            for f, v in zip(fields, nums):
                rows.append(dict(source=src, page=pno, tank=tank, table_type="centers",
                                 sounding_in=si, value=v.replace(",", ""),
                                 unit=units[f], field=f))
    return rows


def extract(pdf_path):
    doc = pymupdf.open(pdf_path)
    src = Path(pdf_path).name
    rows = []
    for i, page in enumerate(doc):
        head = page.get_text("text", sort=True)[:300]
        if "SOUNDING TABLE for" in head:
            rows += parse_sounding_page(page, src, i + 1)
        elif "Table of Centers for" in head:
            rows += parse_centers_page(page, src, i + 1)
    return rows


def write_outputs(rows, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    cols = ["source", "page", "tank", "table_type", "sounding_in", "value", "unit", "field"]
    with open(outdir / "baseline.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    db = outdir / "baseline.sqlite"
    if db.exists():
        db.unlink()
    con = sqlite3.connect(db)
    con.execute("""CREATE TABLE measurement(source TEXT, page INT, tank TEXT, table_type TEXT,
                   sounding_in INT, value TEXT, unit TEXT, field TEXT)""")
    con.executemany("INSERT INTO measurement VALUES(:source,:page,:tank,:table_type,"
                    ":sounding_in,:value,:unit,:field)", rows)
    con.commit()
    con.close()


if __name__ == "__main__":
    pdf = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "out"
    r = extract(pdf)
    write_outputs(r, out)
    print(f"{len(r)} records -> {out}/baseline.csv, baseline.sqlite")
