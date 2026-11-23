"""Digitize Fig. 2 of Sanchez 2023 (ACI 15(1) 2780, page 5): the black data points and the QCD-multijet
fill (bottom of the stack, light gray). Page rendered at 600 dpi with:
    pdftoppm -f 5 -l 5 -r 600 -png docs/Sanchez2023_ACI2780.pdf <out>/hi
Usage: python digitalizar_fig2.py <hi-5.png> [check.png]
Writes docs/figuras_p1/paper_fig2_datos_qcd.json (counts per 10 mm*GeV bin, -150..150).
Calibration (600 dpi, measured on the frame and on the right-axis major ticks):
    x: kappa=-150 at px 1069, +150 at px 3416.5 ; y: log10(v) = (2797.5 - y)/446.0
"""
import sys, os, json
import numpy as np
from PIL import Image

X0, X1 = 1069.0, 3416.5
W = (X1 - X0) / 30
Y1, DEC = 2797.5, 446.0          # y pixel of 1, pixels per decade
YTOP, YBOT = 1308, 2974          # inside the frame
QCD = np.array([222, 221, 222])
val = lambda y: 10 ** ((Y1 - y) / DEC)

im = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
isq = (np.abs(im - QCD).max(2) <= 6)
dark = (im.sum(2) < 200)

bins = list(range(-150, 151, 10))
data, qcd, qcd_ok = [], [], []
dots = []
for k in range(30):
    xc = X0 + (k + 0.5) * W
    # --- QCD: per column, climb from the bottom through light-gray, allowing short gaps (hatch, dashed line)
    tops = []
    for x in range(int(xc - 0.3 * W), int(xc + 0.3 * W)):
        last, gap = None, 0
        for y in range(YBOT, YTOP, -1):
            if isq[y, x]:
                last, gap = y, 0
            else:
                gap += 1
                if gap > 14 and last is not None: break
                if gap > 40 and last is None: break
        tops.append(last)
    t = [v for v in tops if v is not None]
    if len(t) < 0.5 * len(tops):
        qcd.append(0.0); qcd_ok.append(False)
    else:
        qcd.append(round(val(np.median(t)), 3)); qcd_ok.append(True)
    # --- data point: rows where the dark run around xc is wider than an error bar (circle body)
    win = dark[YTOP:YBOT, int(xc - 30):int(xc + 30)]
    wid = win.sum(1)
    rows = np.where(wid >= 22)[0]
    if len(rows) == 0:
        data.append(0.0); dots.append(None); continue
    # biggest contiguous group
    g, cur = [], [rows[0]]
    for r in rows[1:]:
        if r - cur[-1] <= 2: cur.append(r)
        else: g.append(cur); cur = [r]
    g.append(cur)
    g = max(g, key=len)
    if len(g) < 15:
        data.append(0.0); dots.append(None); continue
    yc = YTOP + 0.5 * (g[0] + g[-1])
    dots.append((xc, yc))
    data.append(round(val(yc), 3))

out = dict(source='Sanchez 2023, ACI 15(1) 2780, Fig. 2 (page 5), digitized at 600 dpi',
           bins=bins, paper_data=data, paper_qcd=qcd,
           note='paper_data: black points (0 = no point drawn); paper_qcd: QCD multijet fill top '
                '(0 = below the axis minimum ~0.39). Values read on a log axis: ~2-3 % precision.')
dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'paper_fig2_datos_qcd.json')
json.dump(out, open(dst, 'w'), indent=1)
for k in range(30):
    print(f'{bins[k]:5d}..{bins[k+1]:4d}  datos {data[k]:8.2f}   qcd {qcd[k]:8.2f}')
print('suma datos', round(sum(data), 1), ' suma qcd', round(sum(qcd), 1), '->', dst)

if len(sys.argv) > 2:   # check image: marks over the original
    from PIL import ImageDraw
    img = Image.open(sys.argv[1]).convert('RGB'); d = ImageDraw.Draw(img)
    for k in range(30):
        xa, xb = X0 + k * W, X0 + (k + 1) * W
        if qcd[k] > 0:
            y = Y1 - DEC * np.log10(qcd[k]); d.line([(xa, y), (xb, y)], fill=(0, 160, 255), width=6)
        if dots[k]:
            x, y = dots[k]; d.ellipse([x - 26, y - 26, x + 26, y + 26], outline=(0, 200, 0), width=6)
    img.crop((950, 1250, 3500, 3050)).resize((1275, 900)).save(sys.argv[2])
