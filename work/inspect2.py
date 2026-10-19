import pymupdf
d = pymupdf.open("11103-Sounding-Tables _sample1.pdf")
for n in (3, 6, 16, 22, 37):
    pg = d[n-1]
    print(f"===== PAGE {n} (layout text) =====")
    print(pg.get_text("text", sort=True)[:1800])
