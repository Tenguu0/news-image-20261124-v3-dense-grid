#!/usr/bin/env python3
"""Compose the dense-grid front page for 24 November 2026.

One 1024x1024 newsprint page: masthead, one lead story, a uniform
3x4 grid of twelve more stories, and a MEANWHILE footer strip.
Everything is drawn with PIL + DejaVu fonts; the output is fully
deterministic (no clock, no randomness, no network).
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 232)
INK = (17, 17, 17)
RED = (164, 30, 34)
GREY = (110, 105, 95)
RULE = (60, 58, 52)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, lines, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Outer frame
    d.rectangle([8, 8, W - 9, H - 9], outline=INK, width=3)
    d.rectangle([14, 14, W - 15, H - 15], outline=RULE, width=1)

    # ---- Masthead ----
    mast = font(SERIF_B, 54)
    title = "THE WORLD IN ONE PAGE"
    tw = d.textlength(title, font=mast)
    d.text(((W - tw) / 2, 26), title, font=mast, fill=INK)
    d.line([40, 96, W - 40, 96], fill=INK, width=2)
    dateline = font(SANS_B, 15)
    sub = "TUESDAY, 24 NOVEMBER 2026  •  13 STORIES FROM AROUND THE GLOBE  •  ONE IMAGE, THE WHOLE DAY"
    sw = d.textlength(sub, font=dateline)
    d.text(((W - sw) / 2, 104), sub, font=dateline, fill=RED)

    # ---- Lead story ----
    lx0, ly0, lx1, ly1 = 28, 132, W - 28, 296
    d.rectangle([lx0, ly0, lx1, ly1], outline=INK, width=2)
    d.rectangle([lx0, ly0, lx1, ly0 + 26], fill=RED)
    kick = font(SANS_B, 14)
    d.text((lx0 + 12, ly0 + 5), "LEAD  —  THE GULF WAR WIDENS", font=kick, fill=(255, 255, 255))
    head = font(SERIF_B, 33)
    lead_lines = wrap(d, "IRAN SAYS IT HIT TWO U.S. PATRIOT RADARS IN BAHRAIN", head, lx1 - lx0 - 32)
    y = ly0 + 34
    y = draw_wrapped(d, lx0 + 16, y, lead_lines, head, INK, 40)
    body = font(SANS, 17)
    lead_body = wrap(
        d,
        "The IRGC claims missile and drone strikes on US bases at Al-Riffa and Awali; Bahrain says a "
        "civilian plant burned and two people were hurt. CENTCOM stays silent as the Gulf war enters its second week.",
        body, lx1 - lx0 - 32)
    draw_wrapped(d, lx0 + 16, y + 4, lead_body, body, (40, 38, 34), 22)

    # ---- Dense grid: 3 columns x 4 rows, 12 stories ----
    stories = [
        ("UKRAINE", "KYIV REGION: 15 KILLED IN RUSSIAN STRIKES",
         "Power grid may need four months to repair as drone debris sets Kyiv ablaze."),
        ("CLIMATE", "COP31 COLLAPSES WITHOUT A DEAL",
         "Pacific nations call it the \u201cworst COP ever\u201d as talks in T\u00fcrkiye fail."),
        ("JUSTICE", "WORLD COURT: MYANMAR GUILTY OF GENOCIDE",
         "ICJ rules 9\u20136 against Myanmar over the Rohingya in a historic verdict."),
        ("DIPLOMACY", "XI\u2013TRUMP\u2013PUTIN SUMMIT ENDS IN DEADLOCK",
         "First trilateral in Shenzhen closes with no deal on trade or Ukraine."),
        ("SPORT", "ALCARAZ WINS FIRST ATP FINALS TITLE",
         "Beats Zverev 6\u20132, 7\u20136 in Turin and takes home $5.17 million."),
        ("WAR AT SEA", "KYIV SAYS IT SANK A RUSSIAN WARSHIP OFF LIBYA",
         "Zelensky confirms the strike; Moscow silent as the war reaches the Med."),
        ("ASIA", "SEOUL SCRAMBLES JETS AS RUSSIAN PLANES ENTER ZONE",
         "Several Russian aircraft flew into Korea\u2019s air-defence zone, the military says."),
        ("TECH", "U.S. BLACKLISTS MEGASPEED IN NVIDIA SPY CASE",
         "Singapore firm at the centre of the chip scandal hits the export list."),
        ("CHINA", "CHINA SENTENCES OFFICIAL TO DEATH FOR SPYING",
         "Official surnamed Ma condemned for spying for an unnamed foreign state."),
        ("ALLIES", "PENTAGON REBUKES CANADA OVER DEFENCE",
         "Washington cites shortfalls and Ottawa\u2019s F-35 review as the partnership strains."),
        ("PEACE TALKS", "ZELENSKY URGES FOUR-WAY TALKS \u201cAS SOON AS POSSIBLE\u201d",
         "Kyiv ready to meet Russia, the US and Europe as early as Tuesday."),
        ("GULF", "HOUTHI MISSILE INTERCEPTED NEAR MECCA",
         "Saudi coalition downs a ballistic missile aimed at western Saudi Arabia."),
    ]

    gx0, gy0 = 28, 310
    gap = 10
    cell_w = (W - 2 * gx0 - 2 * gap) // 3
    cell_h = 156
    tag_f = font(SANS_B, 12)
    h_f = font(SERIF_B, 18)
    s_f = font(SANS, 13)
    for i, (tag, headline, summary) in enumerate(stories):
        col, row = i % 3, i // 3
        x0 = gx0 + col * (cell_w + gap)
        y0 = gy0 + row * (cell_h + gap)
        x1, y1 = x0 + cell_w, y0 + cell_h
        d.rectangle([x0, y0, x1, y1], outline=RULE, width=1)
        d.text((x0 + 10, y0 + 7), tag, font=tag_f, fill=RED)
        d.line([x0 + 10, y0 + 26, x1 - 10, y0 + 26], fill=(200, 192, 175), width=1)
        lines = wrap(d, headline, h_f, cell_w - 20)
        y = draw_wrapped(d, x0 + 10, y0 + 33, lines[:3], h_f, INK, 22)
        slines = wrap(d, summary, s_f, cell_w - 20)
        draw_wrapped(d, x0 + 10, y + 3, slines[:2], s_f, (55, 52, 48), 17)

    # ---- MEANWHILE footer strip ----
    fy0, fy1 = 972, 1006
    d.rectangle([28, fy0, W - 28, fy1], fill=INK)
    foot = font(SANS_B, 14)
    meanwhile = ("MEANWHILE:  SK hynix jumps 20% as Huang returns as Nvidia CEO  •  "
                 "Bangladesh starts typhoid jabs for 50m children  •  Thai\u2013Cambodia truce holds  •  "
                 "Fiji closes schools for five days in the El Ni\u00f1o drought")
    flines = wrap(d, meanwhile, foot, W - 28 - 2 * 28 - 20)
    draw_wrapped(d, 44, fy0 + 3, flines[:2], foot, (255, 255, 255), 16)

    img.save("entry.png")
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
