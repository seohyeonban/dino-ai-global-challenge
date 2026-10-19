"""Build an OCR benchmark from a digital PDF: page images (clean + degraded) with gold words.

Gold = PDF text layer (word text + bbox), mapped into each image's pixel space (rotation included),
so OCR output can be scored automatically. Writes, per variant:
    <out>/images/<variant>/p<NN>.<png|jpg>
    <out>/labels/<variant>/p<NN>.json   {"image","w","h","dpi","variant","words":[{text,quad,is_number,has_decimal}]}

usage: make_ocr_bench.py <pdf> <out_dir> [first_page last_page] [seed]
Pages are 1-based; default = the data pages only (sounding / centers tables).
"""
import io
import json
import math
import random
import re
import sys
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image, ImageEnhance, ImageFilter

NUM_RE = re.compile(r"^-?\d[\d,]*(?:\.\d+)?$")

# name: dpi, blur sigma (applied at 200 dpi), noise sigma, jpeg quality, max |rotation| deg, contrast
VARIANTS = {
    "clean_200": dict(dpi=200, blur=0.0, noise=0.0, jpeg=None, rot=0.0, contrast=1.0),
    "scan_mild": dict(dpi=150, blur=0.6, noise=6.0, jpeg=60, rot=0.6, contrast=0.95),
    "scan_hard": dict(dpi=100, blur=1.0, noise=12.0, jpeg=35, rot=1.5, contrast=0.75),
    "scan_lowres": dict(dpi=70, blur=0.8, noise=8.0, jpeg=50, rot=1.0, contrast=0.9),
}


def render(page, dpi):
    pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, alpha=False)
    return Image.frombytes("L", (pix.width, pix.height), pix.samples)


def degrade(img200, v, rng):
    """200-dpi grayscale -> degraded image. Returns (image, scale, angle, (w,h) before rotation)."""
    img = img200
    if v["blur"]:
        img = img.filter(ImageFilter.GaussianBlur(v["blur"]))
    scale = v["dpi"] / 200.0
    if scale != 1.0:
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.BILINEAR)
    if v["contrast"] != 1.0:
        img = ImageEnhance.Contrast(img).enhance(v["contrast"])
    if v["noise"]:
        arr = np.asarray(img, dtype=np.float32)
        arr += np.random.default_rng(rng.randrange(1 << 30)).normal(0, v["noise"], arr.shape)
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    angle = rng.uniform(-v["rot"], v["rot"]) if v["rot"] else 0.0
    if angle:
        img = img.rotate(angle, resample=Image.BICUBIC, fillcolor=255)  # counter-clockwise, about centre
    return img, scale, angle


def rotate_pt(x, y, w, h, angle_deg):
    """Same mapping PIL.rotate uses (counter-clockwise visually, y axis down)."""
    t = math.radians(angle_deg)
    cx, cy = w / 2, h / 2
    dx, dy = x - cx, y - cy
    return cx + dx * math.cos(t) + dy * math.sin(t), cy - dx * math.sin(t) + dy * math.cos(t)


def gold_words(page, scale_to_px, angle, size):
    out = []
    w, h = size
    for x0, y0, x1, y1, text, *_ in page.get_text("words"):
        quad = []
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            px, py = x * scale_to_px, y * scale_to_px
            if angle:
                px, py = rotate_pt(px, py, w, h, angle)
            quad.append([round(px, 1), round(py, 1)])
        isnum = bool(NUM_RE.match(text))
        out.append(dict(text=text, quad=quad, is_number=isnum, has_decimal=isnum and "." in text))
    return out


def default_pages(doc):
    pages = []
    for i, p in enumerate(doc):
        head = p.get_text("text", sort=True)[:300]
        if "SOUNDING TABLE for" in head or "Table of Centers for" in head:
            pages.append(i + 1)
    return pages


def main():
    pdf, out = sys.argv[1], Path(sys.argv[2])
    doc = pymupdf.open(pdf)
    if len(sys.argv) >= 5:
        pages = list(range(int(sys.argv[3]), int(sys.argv[4]) + 1))
    else:
        pages = default_pages(doc)
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 7
    rng = random.Random(seed)
    stats = {}
    for pno in pages:
        page = doc[pno - 1]
        img200 = render(page, 200)
        for name, v in VARIANTS.items():
            if name == "clean_200":
                img, scale, angle = img200, 1.0, 0.0
            else:
                img, scale, angle = degrade(img200, v, rng)
            ext = "png" if v["jpeg"] is None else "jpg"
            idir, ldir = out / "images" / name, out / "labels" / name
            idir.mkdir(parents=True, exist_ok=True)
            ldir.mkdir(parents=True, exist_ok=True)
            ipath = idir / f"p{pno:02d}.{ext}"
            if v["jpeg"] is None:
                img.save(ipath)
            else:
                img.save(ipath, quality=v["jpeg"])
            words = gold_words(page, v["dpi"] / 72.0, angle, img.size)
            (ldir / f"p{pno:02d}.json").write_text(json.dumps(dict(
                image=str(ipath.relative_to(out)).replace("\\", "/"), w=img.size[0], h=img.size[1],
                dpi=v["dpi"], variant=name, angle=round(angle, 3), page=pno, words=words),
                ensure_ascii=False), encoding="utf-8")
            s = stats.setdefault(name, dict(pages=0, words=0, numbers=0, decimals=0))
            s["pages"] += 1
            s["words"] += len(words)
            s["numbers"] += sum(w["is_number"] for w in words)
            s["decimals"] += sum(w["has_decimal"] for w in words)
    (out / "manifest.json").write_text(json.dumps(dict(
        source=Path(pdf).name, pages=pages, seed=seed, variants=VARIANTS, stats=stats), indent=2),
        encoding="utf-8")
    for k, s in stats.items():
        print(k, s)


if __name__ == "__main__":
    main()
