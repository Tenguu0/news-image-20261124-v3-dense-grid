#!/usr/bin/env python3
"""Compose the illustrated dense-grid front page (news-image-20261124 v3).

Every illustration is a small pictogram drawn with PIL primitives, so the
render is fully deterministic: same input, same PNG bytes.
"""

import hashlib
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
PANEL = (238, 230, 211)
INK = (25, 25, 25)
RED = (176, 30, 36)
BLUE = (31, 78, 121)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
GREY = (110, 104, 92)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(d, text, path, sizes, width, max_lines):
    """Pick the largest size whose wrap fits in max_lines lines."""
    for size in sizes:
        fnt = font(path, size)
        lines = wrap(d, text, fnt, width)
        if len(lines) <= max_lines:
            return fnt, lines, size
    fnt = font(path, sizes[-1])
    return fnt, wrap(d, text, fnt, width)[:max_lines], sizes[-1]


def star_points(cx, cy, r_out, r_in, n, rot=-90.0):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180.0 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def rot_rect(cx, cy, w, h, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        out.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    return out


# ---------------------------------------------------------------- icons
# Each pictogram is drawn centred on (cx, cy) with half-size s.

def icon_burst(d, cx, cy, s):
    d.polygon(star_points(cx, cy, s, s * 0.45, 8), fill=INK)
    d.polygon(star_points(cx, cy, s * 0.45, s * 0.2, 5), fill=RED)
    for ang in (20, 140, 260):
        a = math.radians(ang)
        d.ellipse([cx + s * 1.05 * math.cos(a) - 2.5, cy + s * 1.05 * math.sin(a) - 2.5,
                   cx + s * 1.05 * math.cos(a) + 2.5, cy + s * 1.05 * math.sin(a) + 2.5],
                  fill=RED)


def icon_globe(d, cx, cy, s):
    d.ellipse([cx - s, cy - s, cx + s, cy + s], outline=INK, width=3)
    d.ellipse([cx - s * 0.45, cy - s, cx + s * 0.45, cy + s], outline=INK, width=2)
    d.line([(cx - s, cy), (cx + s, cy)], fill=INK, width=2)
    d.line([(cx - s * 0.7, cy - s * 0.5), (cx - s * 0.2, cy),
            (cx + s * 0.2, cy - s * 0.3), (cx + s * 0.6, cy + s * 0.4)],
           fill=RED, width=2)


def icon_scales(d, cx, cy, s):
    d.line([(cx, cy - s), (cx, cy + s * 0.8)], fill=INK, width=3)
    d.line([(cx - s * 0.85, cy - s + 6), (cx + s * 0.85, cy - s + 6)], fill=INK, width=3)
    for sx in (cx - s * 0.85, cx + s * 0.85):
        d.line([(sx, cy - s + 6), (sx, cy + 2)], fill=INK, width=2)
        d.arc([sx - 9, cy - 7, sx + 9, cy + 11], 0, 180, fill=INK, width=2)
    d.line([(cx - 12, cy + s * 0.85), (cx + 12, cy + s * 0.85)], fill=INK, width=3)


def icon_flags(d, cx, cy, s):
    cols = [RED, BLUE, INK]
    for i, px in enumerate((cx - s * 0.7, cx, cx + s * 0.7)):
        d.line([(px, cy - s), (px, cy + s * 0.8)], fill=INK, width=2)
        top = cy - s + 2
        d.polygon([(px, top), (px + 16, top), (px + 12, top + 5),
                   (px + 16, top + 10), (px, top + 10)], fill=cols[i])
    d.line([(cx - s, cy + s * 0.85), (cx + s, cy + s * 0.85)], fill=INK, width=2)


def icon_trophy(d, cx, cy, s):
    d.polygon([(cx - s * 0.55, cy - s * 0.8), (cx + s * 0.55, cy - s * 0.8),
               (cx + s * 0.35, cy - s * 0.1), (cx - s * 0.35, cy - s * 0.1)],
              fill=GOLD, outline=INK)
    d.arc([cx - s * 0.95, cy - s * 0.8, cx - s * 0.3, cy - s * 0.05], 90, 270,
          fill=INK, width=3)
    d.arc([cx + s * 0.3, cy - s * 0.8, cx + s * 0.95, cy - s * 0.05], -90, 90,
          fill=INK, width=3)
    d.rectangle([cx - 3, cy - s * 0.1, cx + 3, cy + s * 0.35], fill=INK)
    d.rectangle([cx - s * 0.5, cy + s * 0.35, cx + s * 0.5, cy + s * 0.55], fill=INK)
    bx, by, br = cx + s * 0.78, cy + s * 0.45, s * 0.22
    d.ellipse([bx - br, by - br, bx + br, by + br], outline=INK, width=2)
    d.arc([bx - br, by - br, bx + br, by + br], -60, 60, fill=RED, width=2)


def icon_ship(d, cx, cy, s):
    d.polygon([(cx - s, cy - s * 0.1), (cx + s * 0.85, cy - s * 0.25),
               (cx + s, cy), (cx + s * 0.7, cy + s * 0.35),
               (cx - s * 0.7, cy + s * 0.35)], fill=INK)
    d.line([(cx + s * 0.1, cy - s * 0.2), (cx + s * 0.1, cy - s * 0.85)],
           fill=INK, width=2)
    d.polygon([(cx + s * 0.1, cy - s * 0.85), (cx + s * 0.45, cy - s * 0.7),
               (cx + s * 0.1, cy - s * 0.6)], fill=RED)
    for ox, oy in ((-0.45, -0.55), (-0.15, -0.7), (0.15, -0.55)):
        d.ellipse([cx + ox * s - 4, cy + oy * s - 4, cx + ox * s + 4,
                   cy + oy * s + 4], outline=GREY, width=2)
    d.arc([cx - s, cy + s * 0.4, cx - s * 0.1, cy + s * 0.8], 0, 180,
          fill=BLUE, width=2)
    d.arc([cx + s * 0.05, cy + s * 0.4, cx + s * 0.95, cy + s * 0.8], 0, 180,
          fill=BLUE, width=2)


def icon_jet(d, cx, cy, s):
    # Side-profile fighter jet pointing right, kept inside the icon square.
    d.polygon([(cx + s * 0.9, cy), (cx + s * 0.2, cy - s * 0.18),
               (cx - s * 0.7, cy - s * 0.12), (cx - s * 0.7, cy + s * 0.12),
               (cx + s * 0.2, cy + s * 0.18)], fill=INK)
    d.polygon([(cx + s * 0.1, cy), (cx - s * 0.35, cy + s * 0.75),
               (cx - s * 0.15, cy + s * 0.05)], fill=INK)
    d.polygon([(cx - s * 0.55, cy - s * 0.1), (cx - s * 0.75, cy - s * 0.7),
               (cx - s * 0.35, cy - s * 0.12)], fill=INK)
    d.ellipse([cx + s * 0.45 - 3, cy - s * 0.16 - 2, cx + s * 0.45 + 3,
               cy - s * 0.16 + 2], fill=RED)
    for dy in (-16, 0, 16):
        d.line([(cx - s, cy + dy), (cx - s * 0.78, cy + dy)], fill=RED, width=2)


def icon_chip(d, cx, cy, s):
    d.rectangle([cx - s * 0.7, cy - s * 0.7, cx + s * 0.7, cy + s * 0.7],
                outline=INK, width=3)
    for k in (-0.35, 0, 0.35):
        d.line([(cx + k * s, cy - s * 0.7 - 6), (cx + k * s, cy - s * 0.7)],
               fill=INK, width=2)
        d.line([(cx + k * s, cy + s * 0.7), (cx + k * s, cy + s * 0.7 + 6)],
               fill=INK, width=2)
        d.line([(cx - s * 0.7 - 6, cy + k * s), (cx - s * 0.7, cy + k * s)],
               fill=INK, width=2)
        d.line([(cx + s * 0.7, cy + k * s), (cx + s * 0.7 + 6, cy + k * s)],
               fill=INK, width=2)
    d.rectangle([cx - s * 0.3, cy - s * 0.3, cx + s * 0.3, cy + s * 0.3],
                outline=INK, width=2)
    d.ellipse([cx - s, cy - s, cx + s, cy + s], outline=RED, width=3)
    d.line([(cx - s * 0.7, cy + s * 0.7), (cx + s * 0.7, cy - s * 0.7)],
           fill=RED, width=3)


def icon_gavel(d, cx, cy, s):
    d.polygon(rot_rect(cx - s * 0.2, cy - s * 0.4, s * 0.85, s * 0.4, -35),
              fill=INK)
    d.line([(cx + s * 0.05, cy - s * 0.15), (cx + s * 0.75, cy + s * 0.55)],
           fill=INK, width=4)
    d.rectangle([cx - s * 0.4, cy + s * 0.6, cx + s * 0.6, cy + s * 0.78],
                fill=INK)
    d.arc([cx - s * 0.95, cy - s * 0.95, cx - s * 0.35, cy - s * 0.35],
          200, 340, fill=GREY, width=2)


def icon_pentagon(d, cx, cy, s):
    pts = []
    for i in range(5):
        a = math.radians(-90 + i * 72)
        pts.append((cx + s * math.cos(a), cy + s * math.sin(a)))
    d.polygon(pts, outline=INK, width=3)
    d.polygon(star_points(cx, cy, s * 0.55, s * 0.24, 5), fill=RED)


def icon_talks(d, cx, cy, s):
    d.rounded_rectangle([cx - s * 0.95, cy - s * 0.8, cx + s * 0.95, cy + s * 0.3],
                        radius=8, outline=INK, width=3)
    d.polygon([(cx - s * 0.5, cy + s * 0.28), (cx - s * 0.65, cy + s * 0.7),
               (cx - s * 0.2, cy + s * 0.28)], fill=INK)
    for dx in (-0.45, 0.45):
        for dy in (-0.45, -0.05):
            d.ellipse([cx + dx * s - 3.5, cy + dy * s - 3.5,
                       cx + dx * s + 3.5, cy + dy * s + 3.5], fill=INK)


def icon_missile(d, cx, cy, s):
    # Missile flying up-right (unit u) with an intercept burst at its nose.
    ux, uy = 0.7071, -0.7071
    vx, vy = 0.7071, 0.7071
    bx, by = cx - s * 0.05, cy + s * 0.05
    d.polygon(rot_rect(bx, by, s * 1.1, s * 0.28, -45), fill=INK)
    ex, ey = bx + s * 0.55 * ux, by + s * 0.55 * uy
    tx, ty = ex + s * 0.45 * ux, ey + s * 0.45 * uy
    d.polygon([(tx, ty),
               (ex + s * 0.14 * vx, ey + s * 0.14 * vy),
               (ex - s * 0.14 * vx, ey - s * 0.14 * vy)], fill=INK)
    tailx, taily = bx - s * 0.55 * ux, by - s * 0.55 * uy
    d.line([(tailx - s * 0.25 * vx, taily - s * 0.25 * vy),
            (tailx + s * 0.25 * vx, taily + s * 0.25 * vy)],
           fill=INK, width=3)
    fx, fy = tailx - s * 0.18 * ux, taily - s * 0.18 * uy
    d.polygon([(fx, fy), (fx - s * 0.3 * ux + s * 0.12 * vx,
                          fy - s * 0.3 * uy + s * 0.12 * vy),
               (fx - s * 0.3 * ux - s * 0.12 * vx,
                fy - s * 0.3 * uy - s * 0.12 * vy)], fill=RED)
    d.polygon(star_points(tx, ty, s * 0.3, s * 0.13, 6), fill=RED)


def icon_radar(d, cx, cy, s):
    d.line([(cx, cy + s * 0.9), (cx, cy - s * 0.3)], fill=INK, width=3)
    d.line([(cx - s * 0.55, cy + s * 0.9), (cx + s * 0.55, cy + s * 0.9)],
           fill=INK, width=3)
    d.arc([cx - s, cy - s * 1.1, cx + s, cy + s * 0.5], 180, 360,
          fill=INK, width=3)
    d.line([(cx - s, cy - s * 0.3), (cx + s, cy - s * 0.3)], fill=INK, width=2)
    d.line([(cx, cy - s * 0.3), (cx - s * 0.75, cy - s * 0.85)], fill=INK, width=2)
    d.line([(cx, cy - s * 0.3), (cx + s * 0.75, cy - s * 0.85)], fill=INK, width=2)
    for r, col in ((s * 1.25, INK), (s * 1.5, RED), (s * 1.75, INK)):
        d.arc([cx - r, cy - s * 0.3 - r, cx + r, cy - s * 0.3 + r], -70, 15,
              fill=col, width=3)
    a = math.radians(-28)
    ex, ey = cx + s * 1.5 * math.cos(a), cy - s * 0.3 + s * 1.5 * math.sin(a)
    d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=RED)


# ------------------------------------------------- meanwhile mini icons
def icon_chart_w(d, cx, cy, s):
    d.line([(cx - s, cy + s), (cx - s, cy - s), (cx + s, cy - s)], fill=WHITE,
           width=2)
    d.line([(cx - s * 0.8, cy + s * 0.5), (cx - s * 0.2, cy),
            (cx + s * 0.3, cy + s * 0.2), (cx + s * 0.8, cy - s * 0.6)],
           fill=WHITE, width=2)
    d.polygon([(cx + s * 0.8, cy - s * 0.6), (cx + s * 0.45, cy - s * 0.6),
               (cx + s * 0.8, cy - s * 0.25)], fill=RED)


def icon_syringe_w(d, cx, cy, s):
    d.line([(cx - s * 0.55, cy + s * 0.55), (cx + s * 0.25, cy - s * 0.25)],
           fill=WHITE, width=6)
    d.line([(cx + s * 0.25, cy - s * 0.25), (cx + s * 0.95, cy - s * 0.95)],
           fill=WHITE, width=2)
    d.line([(cx - s * 0.55, cy + s * 0.55), (cx - s * 0.85, cy + s * 0.85)],
           fill=WHITE, width=3)
    d.line([(cx - s * 0.85, cy + s * 0.55), (cx - s * 0.55, cy + s * 0.85)],
           fill=RED, width=2)


def icon_peace_w(d, cx, cy, s):
    d.ellipse([cx - s, cy - s, cx + s, cy + s], outline=WHITE, width=2)
    d.line([(cx, cy - s), (cx, cy + s)], fill=WHITE, width=2)
    d.line([(cx, cy), (cx - s * 0.7, cy + s * 0.7)], fill=WHITE, width=2)
    d.line([(cx, cy), (cx + s * 0.7, cy + s * 0.7)], fill=WHITE, width=2)


def icon_school_w(d, cx, cy, s):
    d.polygon([(cx - s * 0.7, cy - s * 0.1), (cx, cy - s * 0.7),
               (cx + s * 0.7, cy - s * 0.1)], fill=WHITE)
    d.rectangle([cx - s * 0.55, cy - s * 0.1, cx + s * 0.55, cy + s * 0.6],
                outline=WHITE, width=2)
    d.line([(cx + s * 0.3, cy - s * 0.7), (cx + s * 0.3, cy - s * 1.05)],
           fill=WHITE, width=2)
    d.polygon([(cx + s * 0.3, cy - s * 1.05), (cx + s * 0.65, cy - s * 0.95),
               (cx + s * 0.3, cy - s * 0.85)], fill=RED)
    d.ellipse([cx - s * 0.95, cy - s * 1.05, cx - s * 0.6, cy - s * 0.7],
              outline=RED, width=2)


# ------------------------------------------------------------------ page
STORIES = [
    ("UKRAINE", "KYIV REGION: 15 KILLED IN RUSSIAN STRIKES",
     "Power grid may need four months to repair.", icon_burst),
    ("CLIMATE", "COP31 COLLAPSES WITHOUT A DEAL",
     "Pacific nations call it the \u201cworst COP ever\u201d.", icon_globe),
    ("JUSTICE", "WORLD COURT: MYANMAR GUILTY OF GENOCIDE",
     "ICJ rules 9\u20136 against Myanmar over the Rohingya.", icon_scales),
    ("DIPLOMACY", "XI\u2013TRUMP\u2013PUTIN SUMMIT ENDS IN DEADLOCK",
     "First trilateral in Shenzhen ends with no deal.", icon_flags),
    ("SPORT", "ALCARAZ WINS FIRST ATP FINALS TITLE",
     "Beats Zverev 6\u20132, 7\u20136 in Turin; $5.17m prize.", icon_trophy),
    ("WAR AT SEA", "KYIV SAYS IT SANK A RUSSIAN WARSHIP OFF LIBYA",
     "Zelensky confirms the strike; Moscow stays silent.", icon_ship),
    ("ASIA", "SEOUL SCRAMBLES JETS AS RUSSIAN PLANES ENTER ZONE",
     "Russian jets enter Korea\u2019s air-defence zone.", icon_jet),
    ("TECH", "U.S. BLACKLISTS MEGASPEED IN NVIDIA SPY CASE",
     "Singapore firm at the centre of the chip scandal.", icon_chip),
    ("CHINA", "CHINA SENTENCES OFFICIAL TO DEATH FOR SPYING",
     "Official Ma condemned for spying for a foreign state.", icon_gavel),
    ("ALLIES", "PENTAGON REBUKES CANADA OVER DEFENCE",
     "Washington cites shortfalls and the F-35 review.", icon_pentagon),
    ("PEACE TALKS", "ZELENSKY URGES FOUR-WAY TALKS \u201cAS SOON AS POSSIBLE\u201d",
     "Kyiv ready to meet Russia, the US and Europe.", icon_talks),
    ("GULF", "HOUTHI MISSILE INTERCEPTED NEAR MECCA",
     "Saudi coalition downs a missile aimed at the west.", icon_missile),
]

MEANWHILE = [
    ("SK hynix +20% as Huang returns as Nvidia CEO", icon_chart_w),
    ("Bangladesh typhoid jabs for 50m children", icon_syringe_w),
    ("Thai\u2013Cambodia border truce holds", icon_peace_w),
    ("Fiji closes schools 5 days in El Ni\u00f1o drought", icon_school_w),
]

LEAD_HEAD = "IRAN SAYS IT HIT TWO U.S. PATRIOT RADARS IN BAHRAIN"
LEAD_SUM = ("The IRGC claims missile and drone strikes on US bases at Al-Riffa "
            "and Awali; Bahrain says a civilian plant burned and two people "
            "were hurt. CENTCOM stays silent as the Gulf war enters its "
            "second week.")


def draw_box(d, bx, by, bw, bh, tag, head, summ, icon_fn):
    d.rectangle([bx, by, bx + bw, by + bh], outline=INK, width=1)
    f_tag = font(SANS_B, 15)
    d.text((bx + 10, by + 9), tag, font=f_tag, fill=RED)
    icon_side = 62
    ix, iy = bx + 10, by + 32
    d.rounded_rectangle([ix, iy, ix + icon_side, iy + icon_side], radius=4,
                        fill=PANEL, outline=INK, width=1)
    icon_fn(d, ix + icon_side // 2, iy + icon_side // 2, 24)
    tx = ix + icon_side + 8
    tw = bx + bw - 10 - tx
    f_head, hlines, hsize = fit_lines(d, head, SERIF_B, [20, 18, 17], tw, 3)
    hy = iy + 2
    for ln in hlines:
        d.text((tx, hy), ln, font=f_head, fill=INK)
        hy += hsize + 3
    f_sum, slines, ssize = fit_lines(d, summ, SANS, [14, 13, 12], tw, 2)
    sy = hy + 4
    for ln in slines:
        d.text((tx, sy), ln, font=f_sum, fill=INK)
        sy += ssize + 3


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([7, 7, W - 8, H - 8], outline=INK, width=2)
    d.rectangle([12, 12, W - 13, H - 13], outline=INK, width=1)
    x0, x1 = 20, W - 20
    y = 20

    f_mast = font(SERIF_B, 54)
    d.text((W / 2, y + 30), "THE WORLD IN ONE PAGE", font=f_mast, fill=INK,
           anchor="mm")
    y += 62
    d.line([(x0, y), (x1, y)], fill=INK, width=1)
    f_date = font(SANS_B, 15)
    d.text((W / 2, y + 11),
           "TUESDAY, 24 NOVEMBER 2026  \u2022  13 STORIES FROM AROUND THE GLOBE"
           "  \u2022  ONE IMAGE, THE WHOLE DAY",
           font=f_date, fill=RED, anchor="mm")
    y += 22
    d.line([(x0, y), (x1, y)], fill=INK, width=1)
    y += 6

    d.rectangle([x0, y, x1, y + 22], fill=RED)
    f_bar = font(SANS_B, 14)
    d.text((x0 + 10, y + 11), "LEAD  \u2014  THE GULF WAR WIDENS", font=f_bar,
           fill=WHITE, anchor="lm")
    y += 22

    lead_h = 158
    panel_w = 210
    panel_x = x1 - panel_w
    d.rectangle([panel_x + 1, y + 1, x1 - 1, y + lead_h - 1], fill=PANEL)
    d.rectangle([x0, y, x1, y + lead_h], outline=INK, width=2)
    d.line([(panel_x, y), (panel_x, y + lead_h)], fill=INK, width=1)
    icon_radar(d, panel_x + panel_w // 2, y + lead_h // 2 + 10, 38)
    f_lead = font(SERIF_B, 31)
    text_w = panel_x - 14 - (x0 + 12)
    hlines = wrap(d, LEAD_HEAD, f_lead, text_w)[:2]
    hy = y + 14
    for ln in hlines:
        d.text((x0 + 12, hy), ln, font=f_lead, fill=INK)
        hy += 38
    f_lsum = font(SANS, 15)
    slines = wrap(d, LEAD_SUM, f_lsum, text_w)[:3]
    sy = hy + 6
    for ln in slines:
        d.text((x0 + 12, sy), ln, font=f_lsum, fill=INK)
        sy += 19
    y += lead_h + 8

    gap = 8
    col_w = (x1 - x0 - gap * 2) // 3
    row_h = 158
    for r in range(4):
        for c in range(3):
            bx = x0 + c * (col_w + gap)
            by = y + r * (row_h + gap)
            tag, head, summ, fn = STORIES[r * 3 + c]
            draw_box(d, bx, by, col_w, row_h, tag, head, summ, fn)
    y += 4 * row_h + gap * 3 + 8

    strip_h = 48
    d.rectangle([x0, y, x1, y + strip_h], fill=INK)
    label_w = 96
    f_lab = font(SANS_B, 13)
    d.multiline_text((x0 + label_w // 2, y + strip_h // 2), "MEAN-\nWHILE",
                     font=f_lab, fill=WHITE, anchor="mm", align="center")
    d.line([(x0 + label_w, y), (x0 + label_w, y + strip_h)], fill=RED, width=2)
    rest_w = x1 - (x0 + label_w)
    col_w2 = (rest_w - gap * 3) // 4
    f_mw = font(SANS, 12)
    for i, (txt, fn) in enumerate(MEANWHILE):
        cx0 = x0 + label_w + i * (col_w2 + gap)
        fn(d, cx0 + 16, y + strip_h // 2, 11)
        tx = cx0 + 34
        tw = col_w2 - 34 - 6
        mlines = wrap(d, txt, f_mw, tw)[:2]
        my = y + strip_h // 2 - (len(mlines) * 15) // 2 + 2
        for ln in mlines:
            d.text((tx, my), ln, font=f_mw, fill=WHITE)
            my += 15

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG")
    digest = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print("wrote", out)
    print("sha256", digest)


if __name__ == "__main__":
    build()
