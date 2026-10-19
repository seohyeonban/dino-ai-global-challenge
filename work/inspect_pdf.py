import pymupdf, pdfplumber, sys
p = "11103-Sounding-Tables _sample1.pdf"
d = pymupdf.open(p)
print("pages", len(d), "meta", d.metadata)
for i, pg in enumerate(d):
    t = pg.get_text()
    print(f"--- p{i+1} size={pg.rect} chars={len(t)} images={len(pg.get_images())} words={len(pg.get_text('words'))}")
    if i < 2: print(t[:1500])
with pdfplumber.open(p) as pl:
    pg = pl.pages[0]
    tb = pg.extract_tables()
    print("tables on p1:", len(tb), [ (len(t), len(t[0])) for t in tb][:5])
