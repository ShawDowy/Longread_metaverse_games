# -*- coding: utf-8 -*-
"""Сборка короткого анимационного ролика для лонгрида (WebM VP9)."""

import os
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
FPS = 24
DUR = 14.0
N = int(FPS * DUR)
BASE = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(BASE, "video_frames")
OUT = os.path.join(BASE, "assets", "video", "web3-game.webm")
os.makedirs(FRAMES, exist_ok=True)
os.makedirs(os.path.dirname(OUT), exist_ok=True)

FONT_D = os.path.join(BASE, "assets", "fonts", "unbounded-700.ttf")
FONT_M = os.path.join(BASE, "assets", "fonts", "manrope-500.ttf")
FONT_B = os.path.join(BASE, "assets", "fonts", "manrope-700.ttf")

def font(path, size):
    return ImageFont.truetype(path, size)

f_kicker = font(FONT_M, 15)
f_title = font(FONT_D, 30)
f_sub = font(FONT_M, 15)
f_node = font(FONT_B, 17)
f_node_s = font(FONT_M, 13)
f_caption = font(FONT_B, 21)
f_foot = font(FONT_M, 13)

BG = (7, 11, 20)
PANEL = (13, 20, 36)
CYAN = (99, 230, 255)
VIOLET = (167, 139, 250)
PINK = (255, 122, 200)
LIME = (163, 230, 53)
MUTED = (142, 158, 186)
TEXT = (232, 238, 249)

NX = {
    "P": (130, 360, 220, 130),
    "S": (500, 210, 270, 130),
    "B": (500, 440, 270, 130),
    "M": (930, 360, 250, 130),
}

def center(n):
    x, y, w, h = NX[n]
    return (x + w / 2, y + h / 2)

def edge_point(n, target):
    x, y, w, h = NX[n]
    cx, cy = x + w / 2, y + h / 2
    tx, ty = target
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    # пересечение луча с прямоугольником
    sx = (w / 2) / abs(dx) if dx else 1e9
    sy = (h / 2) / abs(dy) if dy else 1e9
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s

def make_bg():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # сетка
    for x in range(0, W, 40):
        d.line((x, 0, x, H), fill=(13, 21, 36), width=1)
    for y in range(0, H, 40):
        d.line((0, y, W, y), fill=(13, 21, 36), width=1)
    # цветные пятна
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-160, -220, 520, 340), fill=(36, 160, 210, 34))
    gd.ellipse((880, 360, 1480, 920), fill=(140, 90, 240, 34))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    im = Image.alpha_composite(im.convert("RGBA"), glow).convert("RGB")
    # виньетка
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse((-250, -200, W + 250, H + 200), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(140))
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    im = Image.composite(im, dark, vig)
    return im

BASE_IMG = make_bg()

def rounded(draw, box, r, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def draw_glow_box(base, box, color, radius=18, blur=17, alpha=105):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius, fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base.convert("RGBA"), layer)

def draw_arrow(d, a, b, color=(70, 90, 120), width=2):
    d.line((a[0], a[1], b[0], b[1]), fill=color, width=width)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    L = 12
    for s in (-0.5, 0.5):
        x = b[0] - L * math.cos(ang + s)
        y = b[1] - L * math.sin(ang + s)
        d.line((b[0], b[1], x, y), fill=color, width=width)

def packet(base, a, b, t, color):
    x = a[0] + (b[0] - a[0]) * t
    y = a[1] + (b[1] - a[1]) * t
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i, k in enumerate((0.0, 0.06, 0.13, 0.21)):
        tt = max(0.0, t - k)
        xx = a[0] + (b[0] - a[0]) * tt
        yy = a[1] + (b[1] - a[1]) * tt
        alpha = int(150 * (1 - i / 4))
        rr = max(2, 7 - i * 1.5)
        d.ellipse((xx - rr, yy - rr, xx + rr, yy + rr),
                  fill=color + (alpha,))
    d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=color + (255,))
    layer = layer.filter(ImageFilter.GaussianBlur(4))
    base = Image.alpha_composite(base.convert("RGBA"), layer)
    d2 = ImageDraw.Draw(base)
    d2.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 255, 255, 255))
    return base

def caption_for(tt):
    if tt < 2.6:
        return "Игрок входит в мир"
    if tt < 5.2:
        return "Сервер считает состояние мира"
    if tt < 8.0:
        return "В блокчейн — только значимые операции"
    if tt < 10.6:
        return "Актив можно проверить и передать"
    return "Но переносимость не гарантирована"

def packet_for(tt):
    # (from, to, local_t, color)
    if tt < 2.6:
        return ("P", "S", (tt / 2.6) % 1.0, CYAN)
    if tt < 5.2:
        return ("S", "M", ((tt - 2.6) / 2.6) % 1.0, LIME)
    if tt < 8.0:
        return ("P", "B", ((tt - 5.2) / 2.8) % 1.0, VIOLET)
    if tt < 10.6:
        return ("B", "M", ((tt - 8.0) / 2.6) % 1.0, PINK)
    return None

NODE_TEXT = {
    "P": ("Игрок", "кошелёк / аккаунт"),
    "S": ("Игровой сервер", "правила и состояние"),
    "B": ("Блокчейн", "только значимые операции"),
    "M": ("Маркетплейс", "активы и обмен"),
}
NODE_COLOR = {"P": CYAN, "S": LIME, "B": VIOLET, "M": PINK}

for idx in range(N):
    tt = idx / FPS
    im = BASE_IMG.copy().convert("RGBA")
    d = ImageDraw.Draw(im)

    # заголовок
    d.text((56, 42), "WEB3 / АРХИТЕКТУРА ИГРЫ", font=f_kicker, fill=MUTED)
    d.text((56, 66), "Как устроена Web3-игра", font=f_title, fill=TEXT)
    d.text((58, 110), "Упрощённая схема: сервер, блокчейн и рынок активов",
           font=f_sub, fill=MUTED)

    # стрелки
    arrows = {
        ("P", "S"): (edge_point("P", center("S")), edge_point("S", center("P"))),
        ("S", "M"): (edge_point("S", center("M")), edge_point("M", center("S"))),
        ("P", "B"): (edge_point("P", center("B")), edge_point("B", center("P"))),
        ("B", "M"): (edge_point("B", center("M")), edge_point("M", center("B"))),
    }
    for a, b in arrows.values():
        draw_arrow(d, a, b)

    # пакет
    pk = packet_for(tt)
    if pk:
        a, b, lt, col = pk
        im = packet(im, arrows[(a, b)][0], arrows[(a, b)][1], lt, col)
        d = ImageDraw.Draw(im)

    # узлы
    active = set()
    if pk:
        active.add(pk[0]); active.add(pk[1])
    for n, (x, y, w, h) in NX.items():
        col = NODE_COLOR[n]
        pulse = 0.5 + 0.5 * math.sin(tt * 2.4 + list(NX).index(n))
        glow_alpha = 90 if n in active else int(35 + 25 * pulse)
        im = draw_glow_box(im, (x, y, x + w, y + h), col,
                           radius=18, blur=18, alpha=glow_alpha)
        d = ImageDraw.Draw(im)
        fill = PANEL if n not in active else (18, 28, 50)
        rounded(d, (x, y, x + w, y + h), 18, fill,
                outline=col + (200,) if n in active else (48, 62, 90, 255),
                width=2 if n in active else 1)
        title, sub = NODE_TEXT[n]
        tw = d.textlength(title, font=f_node)
        d.text((x + w / 2 - tw / 2, y + 28), title, font=f_node, fill=TEXT)
        sw = d.textlength(sub, font=f_node_s)
        d.text((x + w / 2 - sw / 2, y + 58), sub, font=f_node_s, fill=MUTED)
        # маленький индикатор
        d.ellipse((x + 18, y + 17, x + 26, y + 25), fill=col + (230,))

    # нижняя подпись
    cap = caption_for(tt)
    d.rectangle((56, 600, 1224, 662), fill=(9, 15, 28, 220))
    d.rectangle((56, 600, 62, 662), fill=CYAN + (255,))
    d.text((84, 616), cap, font=f_caption, fill=TEXT)

    # нижняя сноска
    d.text((58, 682),
           "Блокчейн не заменяет игровой сервер и не делает все предметы переносимыми.",
           font=f_foot, fill=MUTED)

    # прогресс
    d.line((56, 675, 1224, 675), fill=(30, 43, 66), width=2)
    d.line((56, 675, 56 + int(1168 * tt / DUR), 675), fill=CYAN, width=2)

    im.convert("RGB").save(os.path.join(FRAMES, f"f_{idx:04d}.png"))

print("frames", N)

cmd = (
    f'gst-launch-1.0 -e multifilesrc location="{FRAMES}/f_%04d.png" '
    f'start-index=0 stop-index={N-1} caps="image/png,framerate=24/1" '
    f'! pngdec ! videoconvert ! vp9enc deadline=1 cpu-used=4 '
    f'target-bitrate=2200000 ! webmmux ! filesink location="{OUT}"'
)
print("encoding...")
subprocess.run(cmd, shell=True, check=True)
print("saved", OUT, os.path.getsize(OUT) // 1024, "KB")

# постер
poster = Image.open(os.path.join(FRAMES, f"f_{int(7.5*FPS):04d}.png"))
poster.save(os.path.join(BASE, "assets", "img", "video-poster.webp"),
            "WEBP", quality=88, method=6)
print("poster saved")
