"""Přehledový list fotek: python skripty/kontakt.py <složka> <výstup.jpg>"""
import glob, os, sys
from PIL import Image, ImageDraw
fs = sorted(f for f in glob.glob(os.path.join(sys.argv[1], '*.jpg')))
C, S = 4, 360
rows = (len(fs) + C - 1) // C
out = Image.new('RGB', (C * S, rows * S), (30, 30, 30)); d = ImageDraw.Draw(out)
for k, f in enumerate(fs):
    im = Image.open(f).convert('RGB'); im.thumbnail((S - 6, S - 22))
    x, y = (k % C) * S, (k // C) * S
    out.paste(im, (x + 3, y + 3)); d.text((x + 4, y + S - 17), f'{k}: {os.path.basename(f)[:46]}', fill=(255, 255, 0))
out.save(sys.argv[2], quality=85)
