#!/usr/bin/env python3
"""Generate Perimeter social share (OG) image — 1200×630."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, os

W, H = 1200, 630
ICON_PATH = "perimeter/img/icon.png"
OUT_PATH  = "perimeter/img/og-image.png"

# ── Colours ──────────────────────────────────────────────────────────
BG   = (11, 11, 16)
GREEN  = (0,   220, 110)   # 30-min glow
YELLOW = (255, 200,  30)   # 10-min
ORANGE = (255, 120,  20)   # 5-min
RED    = (255,  45,  55)   # NOW

# ── Canvas ────────────────────────────────────────────────────────────
img  = Image.new("RGBA", (W, H), BG + (255,))
draw = ImageDraw.Draw(img)

def add_glow_strip(img, edge, color, strip_w=38, blur=28, intensity=0.85):
    """Paint a glowing gradient strip on one edge."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    r, g, b = color
    steps = strip_w * 3
    for i in range(steps):
        t = i / steps              # 0 = edge, 1 = inner fade
        alpha = int(255 * intensity * (1 - t) ** 1.6)
        c = (r, g, b, alpha)
        if edge == "top":
            ld.line([(0, i), (W, i)], fill=c)
        elif edge == "bottom":
            ld.line([(0, H - 1 - i), (W, H - 1 - i)], fill=c)
        elif edge == "left":
            ld.line([(i, 0), (i, H)], fill=c)
        elif edge == "right":
            ld.line([(W - 1 - i, 0), (W - 1 - i, H)], fill=c)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(layer)

# Top = green (calm, early)
add_glow_strip(img, "top",    GREEN,  strip_w=40, blur=30, intensity=0.9)
# Bottom = red (NOW)
add_glow_strip(img, "bottom", RED,    strip_w=40, blur=30, intensity=0.9)
# Left = yellow
add_glow_strip(img, "left",   YELLOW, strip_w=34, blur=26, intensity=0.75)
# Right = orange
add_glow_strip(img, "right",  ORANGE, strip_w=34, blur=26, intensity=0.75)

# ── App icon ─────────────────────────────────────────────────────────
ICON_SIZE = 148
icon = Image.open(ICON_PATH).convert("RGBA").resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
# Subtle drop shadow under icon
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
ix = (W - ICON_SIZE) // 2
iy = int(H * 0.30)
sd.ellipse([ix + 10, iy + ICON_SIZE - 8, ix + ICON_SIZE - 10, iy + ICON_SIZE + 18],
           fill=(0, 0, 0, 120))
shadow = shadow.filter(ImageFilter.GaussianBlur(14))
img.alpha_composite(shadow)
img.paste(icon, (ix, iy), icon)

# ── Text ──────────────────────────────────────────────────────────────
draw = ImageDraw.Draw(img)

def load_font(size, bold=False):
    attempts = [
        f"/System/Library/Fonts/{'SFNS' if bold else 'SFNS'}.ttf",
        f"/System/Library/Fonts/Helvetica{'Neue' if not bold else 'Neue Bold'}.ttf",
        f"/System/Library/Fonts/{'SF-Pro-Display-Bold' if bold else 'SF-Pro-Display-Regular'}.otf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in attempts:
        if os.path.exists(path):
            try: return ImageFont.truetype(path, size)
            except: pass
    # Try system font dirs
    for root in ["/System/Library/Fonts", "/Library/Fonts"]:
        for fn in os.listdir(root) if os.path.isdir(root) else []:
            if bold and "Bold" in fn and fn.endswith((".ttf", ".otf")):
                try: return ImageFont.truetype(os.path.join(root, fn), size)
                except: pass
            elif not bold and "Regular" in fn and fn.endswith((".ttf", ".otf")):
                try: return ImageFont.truetype(os.path.join(root, fn), size)
                except: pass
    return ImageFont.load_default()

font_title = load_font(58, bold=True)
font_sub   = load_font(26, bold=False)

title    = "Perimeter"
subtitle = "Never be late to a meeting again."

tx = W // 2
ty = iy + ICON_SIZE + 28

# Title
bbox = draw.textbbox((0, 0), title, font=font_title)
tw = bbox[2] - bbox[0]
draw.text((tx - tw // 2, ty), title, font=font_title, fill=(255, 255, 255, 255))

# Subtitle
ty2 = ty + (bbox[3] - bbox[1]) + 16
bbox2 = draw.textbbox((0, 0), subtitle, font=font_sub)
sw = bbox2[2] - bbox2[0]
draw.text((tx - sw // 2, ty2), subtitle, font=font_sub, fill=(180, 180, 195, 230))

# ── Save ──────────────────────────────────────────────────────────────
final = img.convert("RGB")
final.save(OUT_PATH, "PNG", optimize=True)
print(f"Saved {OUT_PATH}  ({W}×{H})")
