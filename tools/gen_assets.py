#!/usr/bin/env python3
"""Draws the splash logo (exact geometry from the design SVG) and the app icon."""
import os, json, math
from PIL import Image, ImageDraw

BG = (0x0F, 0x0F, 0x15); TRACK = (0x25, 0x25, 0x40); ACCENT = (0x6C, 0x63, 0xFF); GREEN = (0x34, 0xD3 - 0x00 + 0x00, 0x99)
GREEN = (0x34, 0xD3, 0x99)

def logo(px, bg=None):
    """104x104 design units rendered at px pixels, 8x supersampled."""
    SS = 8; N = px * SS; k = N / 104.0
    im = Image.new('RGBA', (N, N), (0, 0, 0, 0) if bg is None else bg + (255,))
    d = ImageDraw.Draw(im)
    def circ(cx, cy, r, col):
        d.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], fill=col)
    # track ring r=42 stroke 9
    d.ellipse([(52 - 46.5) * k, (52 - 46.5) * k, (52 + 46.5) * k, (52 + 46.5) * k], outline=TRACK, width=int(round(9 * k)))
    # progress arc: dasharray 198/264 => 270deg clockwise from 12 o'clock, round caps
    d.arc([(52 - 46.5) * k, (52 - 46.5) * k, (52 + 46.5) * k, (52 + 46.5) * k], -90, 180, fill=ACCENT, width=int(round(9 * k)))
    circ(52, 52 - 42, 4.5, ACCENT); circ(52 - 42, 52, 4.5, ACCENT)
    # checkmark M36 53 l11 11 21-23, stroke 7 round
    pts = [(36, 53), (47, 64), (68, 41)]
    d.line([(x * k, y * k) for x, y in pts], fill=GREEN, width=int(round(7 * k)), joint='curve')
    for x, y in pts: circ(x, y, 3.5, GREEN)
    return im.resize((px, px), Image.LANCZOS)

root = '../HabitTracker/Assets.xcassets'
os.makedirs(root + '/AppIcon.appiconset', exist_ok=True)
os.makedirs(root + '/Logo.imageset', exist_ok=True)
json.dump({"info": {"author": "xcode", "version": 1}}, open(root + '/Contents.json', 'w'), indent=2)

# Logo @1x/2x/3x (104pt)
imgs = []
for s in (1, 2, 3):
    fn = f'Logo{"" if s == 1 else f"@{s}x"}.png'
    logo(104 * s).save(f'{root}/Logo.imageset/{fn}')
    imgs.append({"filename": fn, "idiom": "universal", "scale": f"{s}x"})
json.dump({"images": imgs, "info": {"author": "xcode", "version": 1}}, open(root + '/Logo.imageset/Contents.json', 'w'), indent=2)

# App icon 1024 (opaque)
icon = Image.new('RGB', (1024, 1024), BG)
lg = logo(620)
icon.paste(lg, ((1024 - 620) // 2, (1024 - 620) // 2), lg)
icon.save(root + '/AppIcon.appiconset/AppIcon.png')
json.dump({"images": [{"filename": "AppIcon.png", "idiom": "universal", "platform": "ios", "size": "1024x1024"}],
           "info": {"author": "xcode", "version": 1}}, open(root + '/AppIcon.appiconset/Contents.json', 'w'), indent=2)
print('assets written')
