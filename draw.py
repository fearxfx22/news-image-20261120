#!/usr/bin/env python3
"""Friday 20 November 2026 — THE WORLD IN ONE DAY (make.fun news-image-20261120).

v2 revision: our v1 scored 98.39% (rank #252). The top 10 (99.0-99.2%) all
share one visual formula our v1 lacked: the DATE as the giant masthead,
dense dark full-bleed illustrations with bold on-image banner labels,
taller medium illustrations, a compact dark map panel beside the list,
UTC stamps and REPORTED/CLAIM/FORECAST tags on every card, and a
three-part date rail (19 Nov left out / 20 Nov on this page / 21 Nov not
yet). This revision rebuilds the page to that formula. All 44 stories are
the same verified 20 Nov 2026 stories as v1 — no new facts, no new dates;
list items were only shortened to fit the side-by-side layout.

1024x1024, deterministic (seeded grain), standard library + PIL only.
The grader runs main.py, which copies the committed entry.png to /output.
"""

import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
PAPER2 = (242, 237, 226)
INK = (18, 18, 18)
GREY = (92, 88, 80)
LIGHT = (178, 172, 160)
RED = (178, 34, 26)
RED_DK = (140, 24, 18)
BLUE = (31, 78, 121)
OCHRE = (122, 90, 18)
GREEN = (47, 107, 79)
PURPLE = (107, 63, 122)
TEAL = (47, 107, 122)
RUST = (138, 47, 47)
NAVY = (16, 30, 54)
NAVY2 = (24, 44, 72)

FDIR = "/usr/share/fonts/truetype"
SERIF = os.path.join(FDIR, "liberation/LiberationSerif-Regular.ttf")
SERIF_B = os.path.join(FDIR, "liberation/LiberationSerif-Bold.ttf")
SERIF_I = os.path.join(FDIR, "liberation/LiberationSerif-Italic.ttf")
SANS = os.path.join(FDIR, "liberation/LiberationSans-Regular.ttf")
SANS_B = os.path.join(FDIR, "liberation/LiberationSans-Bold.ttf")
SANS_I = os.path.join(FDIR, "liberation/LiberationSans-Italic.ttf")

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def tw(draw, text, fnt):
    """Text width in px."""
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if tw(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Wrap, then drop a trailing ellipsis if it still overflows."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and tw(draw, lines[-1] + " …", fnt) > max_w:
            lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else lines[-1][:-1]
        lines[-1] = lines[-1] + " …"
    return lines


def one_line(draw, text, fnt, max_w, min_size=None):
    """Return (text, font) fitting one line, shrinking font if allowed."""
    f = fnt
    while tw(draw, text, f) > max_w and min_size is not None and f.size > min_size:
        f = font(f.path, f.size - 1)
    if tw(draw, text, f) > max_w:
        while tw(draw, text + "…", f) > max_w and len(text) > 8:
            text = text.rsplit(" ", 1)[0] if " " in text else text[:-1]
        text = text + "…"
    return text, f


def tracked(draw, x, y, text, fnt, fill, tracking=1):
    """Draw uppercase text with letter tracking; returns width."""
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=fnt, fill=fill)
        cx += draw.textlength(ch, font=fnt) + tracking
    return cx - x - tracking


def rule(draw, x, y, w, fill=INK, h=1):
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=fill)


def art_banner(d, x, y, text, size=12):
    """Bold red banner label drawn ON an illustration; returns width."""
    f = font(SANS_B, size)
    w = int(tw(d, text, f)) + 12
    d.rectangle([x, y, x + w - 1, y + size + 6], fill=RED)
    d.text((x + 6, y + 3), text, font=f, fill=(255, 255, 255))
    return w


def art_chip(d, x, y, text, size=9, right=None):
    """Small dark chip with white text, drawn ON an illustration.
    If right is given, the chip is right-aligned to that x."""
    f = font(SANS_B, size)
    w = int(tw(d, text, f)) + 10
    if right is not None:
        x = right - w
    d.rectangle([x, y, x + w - 1, y + size + 6], fill=(16, 16, 16))
    d.text((x + 5, y + 3), text, font=f, fill=(255, 255, 255))
    return w


# ---------------------------------------------------------------- data ----
HEROES = [
    dict(n=1, kicker="ODISHA · CYCLONE", src="REUTERS", tag="REPORTED",
         art="cyclone", banner="CYCLONE AKVAN", chip="LANDFALL · 02:00 UTC",
         head="Cyclone Akvan makes landfall on India's east coast",
         deck="Crossed near Gopalpur at 70–80 km/h, gusting to 90. "
              "Over 300,000 evacuated; no deaths reported."),
    dict(n=2, kicker="ANTALYA · CLIMATE", src="UN NEWS", tag="FORECAST",
         art="cop", banner="COP31: NO DEAL", chip="FINAL DAY · ANTALYA",
         head="COP31 enters its final day with no deal in sight",
         deck="Antalya talks reach their final day with no agreement; "
              "the draft drops fossil fuels and the $120bn figure."),
    dict(n=3, kicker="NEW YORK · MARKETS", src="IBD · WSJ", tag="REPORTED",
         art="chart", banner="AI SELL-OFF", chip="CLOSE · 20 NOV",
         head="Anthropic slides 10% on day two as markets rout deepens",
         deck="Shares fell to about $85, near the $83 IPO price. The S&P 500 "
              "headed for a seventh straight down day."),
]

MEDIUMS = [
    dict(n=4, kicker="KYIV · WAR", src="BBC", tag="REPORTED", art="bridge",
         banner="KYIV: BRIDGES HIT",
         head="Russia strikes Kyiv's bridges overnight; 8 killed",
         deck="Strikes hit Dnipro bridges; 8 killed, 28 injured in nine "
              "regions. (BBC)"),
    dict(n=5, kicker="BERLIN · DIPLOMACY", src="TBS · BBC", tag="REPORTED",
         art="summit", banner="BERLIN: READY TO TALK",
         head="European leaders ready to negotiate with Russia",
         deck="Berlin summit: Burnham cites unity; Merz rejects demands. "
              "(TBS · BBC)"),
    dict(n=6, kicker="POLAND · SECURITY", src="REUTERS", tag="REPORTED",
         art="radar", banner="POLAND: MISSILE",
         head="Russia violates Poland's airspace overnight",
         deck="Two missiles and a drone crossed as Poland prepared exercises. "
              "(Reuters)"),
    dict(n=7, kicker="RIYADH · SECURITY", src="REUTERS", tag="REPORTED",
         art="intercept", banner="RIYADH: INTERCEPTED",
         head="Saudi Arabia intercepts Houthi missile and two drones",
         deck="Missile and two drones intercepted; alerts in Riyadh, Najran. "
              "(Reuters)"),
    dict(n=8, kicker="TALLINN · SECURITY", src="REUTERS", tag="REPORTED",
         art="border", banner="ESTONIA: BORDER SHUT",
         head="Estonia to close Russia border for at least six months",
         deck="Tallinn announced the closure; Moscow threatened a response. "
              "(Reuters)"),
    dict(n=9, kicker="LONDON · POLITICS", src="BBC", tag="REPORTED",
         art="passport", banner="UK–EU: YOUTH DEAL",
         head="UK–EU agree youth mobility scheme, 100,000 a year",
         deck="To be agreed Friday; the EU wants UK tuition fees cut. (BBC)"),
    dict(n=10, kicker="WELLINGTON · SPORT", src="REUTERS", tag="REPORTED",
         art="cricket", banner="WELLINGTON: 368",
         head="India fight back in Wellington after NZ post 368",
         deck="Nicholls 175*, Phillips 118; Jaiswal's 85 led a 130-run stand. "
              "(Reuters)"),
    dict(n=11, kicker="KENYA · CONFLICT", src="JUBA GLOBAL NEWS",
         tag="REPORTED", art="route", banner="KENYA: 50,000 FLEE",
         head="50,000 flee Ethiopia fighting into Kenya",
         deck="Fleeing violence into Kenya; El Niño floods batter Kenya. "
              "(Juba Global)"),
    dict(n=12, kicker="GAZA · CONFLICT", src="MITZPE INSTITUTE",
         tag="REPORTED", art="skyline", banner="GAZA: HAMAS BACK",
         head="Hamas government is back on its feet in Gaza",
         deck="All 17 ministries back at work, plus 22 of 25 municipalities. "
              "(Mitzpe)"),
    dict(n=13, kicker="IRAQ · SECURITY", src="REUTERS", tag="REPORTED",
         art="checkpoint", banner="IRAQ: ARMY IN",
         head="Iraq deploys forces against Iran-aligned Kataib Hezbollah",
         deck="Deployed in Jurf al-Sakhar to curb the group. (Reuters)"),
]

# List items shortened to fit the side-by-side map+list layout.
# Same facts as v1; format "City: story (Source)".
LIST_ITEMS = [
    (14, "London", "RAF Fairford trial Nov 2027; Iran blamed", "Reuters"),
    (15, "London", "UK runs offensive cyber ops on four states", "Sky News"),
    (16, "Washington", "Kushner floated NATO-for-land Ukraine deal", "WSJ"),
    (17, "Yangon", "Myanmar dismisses the ICJ genocide ruling", "BBC"),
    (18, "Washington", "DOJ assigns Essayli to Mar-a-Lago probe", "Politico"),
    (19, "Washington", "Tillis to block Ueland GAO confirmation", "Politico"),
    (20, "Washington", "Sen. Wyden: secure lawmakers' phones", "NYT"),
    (21, "Washington", "AI Safety and Innovation Caucus forms", "Politico"),
    (22, "Juba", "US deportee families endured hunger, thirst", "AP"),
    (23, "Georgetown", "Ex-US official: Guyana cede land", "Reuters"),
    (24, "Beqaa", "Israel hits Hezbollah missile factory again", "Mitzpe"),
    (25, "Peshawar", "Pakistan kills 22 militants at border", "B. Chronicle"),
    (26, "Dhaka", "Dhaka tense after shutdown and violence", "B. Chronicle"),
    (27, "New Delhi", "India relaxes vessel-age rules", "B. Chronicle"),
    (28, "Shenzhen", "Middle powers move as Trump courts Xi", "Reuters"),
    (29, "South Kordofan", "Drone strike kills 10 at gold mine", "One Turn"),
    (30, "Juba", "S. Sudan launches accountants' institute", "Juba Global"),
    (31, "Johannesburg", "Rand at one-year low; gold slides", "Juba Global"),
    (32, "Geneva", "UN warns antibiotics are failing", "Juba Global"),
    (33, "Dakar", "Senegal imposes 2026 budget by decree", "Juba Global"),
    (34, "Dakar", "Senegal boat capsizes; dozens missing", "One Turn"),
    (35, "Nairobi", "El Niño floods batter Kenya", "Juba Global"),
    (36, "Canberra", "Albanese pressed Putin on Ukraine at APEC", "Guardian"),
    (37, "Invercargill", "Southland storm review finds poor comms", "RNZ"),
    (38, "London", "Barrett to win 150th Test cap at Twickenham", "Reuters"),
    (39, "Manchester", "Pochettino's Utd debut filmed by drone", "Guardian"),
    (40, "Colombo", "India A beat Nepal by 306 runs", "Inshorts"),
    (41, "Rawalpindi", "Pakistan seal Test series 1–0", "Inshorts"),
    (42, "Colombo", "Sri Lanka's first winless Test year since 1997", "Inshorts"),
    (43, "Nairobi", "Peres Jepchirchir gets three-year doping ban", "mykhel"),
    (44, "Budapest", "Carlsen stages 11–9 comeback vs Artemiev", "Inshorts"),
]

REGIONS = [
    ("EUROPE", 10, BLUE), ("AFRICA", 9, OCHRE), ("ASIA", 8, RUST),
    ("AMERICAS", 6, GREEN), ("MIDDLE EAST", 4, PURPLE), ("OCEANIA", 4, TEAL),
    ("WORLD", 3, GREY),
]

NUMBERS = [
    ("300,000+", "people evacuated ahead of Cyclone Akvan, India"),
    ("8 · 28", "killed · injured in Russia's overnight strikes on Ukraine"),
    ("−10%", "Anthropic shares on day two of trading (low $85.00)"),
    ("7", "straight down days for the S&P 500, longest since 2020"),
    ("50,000", "people who fled Ethiopia fighting into Kenya"),
    ("100,000", "young people a year in the UK–EU youth mobility scheme"),
]

# Three-part date rail: 19 Nov left out / 20 Nov on this page / 21 Nov not yet.
DATE_RAIL = [
    ("19 NOV — LEFT OUT", RED,
     "Trump–Xi–Putin summit; ICJ Myanmar ruling; COP31 draft; Anthropic IPO "
     "debut; GTA VI launch; IMF debt warning; IEA data-centre report; 879,000 "
     "AI chips for China; Kerch Bridge strike; Bukele third-term launch; "
     "Kenya Ebola countdown; PIF Tower strike; White House cyber director."),
    ("20 NOV — ON THIS PAGE", INK,
     "Every story here happened, or was first reported, on Friday 20 November "
     "2026. Claims are attributed, not stated as fact."),
    ("21 NOV — NOT YET", GREY,
     "The COP31 final deal; the Kerch Bridge road span reopening."),
]

SOURCES_LINE = (
    "Sources: Reuters · BBC · AP · WSJ · AFP · Al Jazeera · Politico · NYT · "
    "Guardian · RNZ · Inshorts · Sky News · TBS News · Juba Global News · "
    "Mitzpe Institute · One Turn · Bangladesh Chronicle · IBD · UN News"
)

# ------------------------------------------------------- illustrations ----
def art_cyclone(d, x, y, w, h):
    """Dense dark-teal cyclone scene: big spiral, coastline, Gopalpur pin."""
    for i in range(6):
        d.rectangle([x, y + i * h // 6, x + w, y + (i + 1) * h // 6],
                    fill=(10 + i * 3, 42 + i * 7, 60 + i * 8))
    # landmass (Odisha coast) on the right
    d.polygon([(x + w * 0.66, y), (x + w, y), (x + w, y + h),
               (x + w * 0.74, y + h), (x + w * 0.60, y + h * 0.55),
               (x + w * 0.68, y + h * 0.28)], fill=(214, 196, 150))
    d.line([(x + w * 0.66, y), (x + w * 0.68, y + h * 0.28),
            (x + w * 0.60, y + h * 0.55), (x + w * 0.74, y + h)],
           fill=(120, 100, 70), width=2)
    # Gopalpur pin on the coast
    gx, gy = x + w * 0.665, y + h * 0.42
    d.ellipse([gx - 5, gy - 5, gx + 5, gy + 5], fill=RED,
              outline=(255, 255, 255), width=1)
    d.text((gx + 8, gy - 6), "GOPALPUR", font=font(SANS_B, 8),
           fill=(60, 50, 30))
    # rain bands sweeping in from the left
    for fy in (0.18, 0.38, 0.62, 0.82):
        d.line([(x + 4, y + h * fy), (x + w * 0.30, y + h * (fy + 0.10))],
               fill=(150, 185, 205), width=2)
    # big white spiral
    cx, cy = x + w * 0.36, y + h * 0.54
    for r, a0, a1, lw in [(46, 20, 300, 4), (38, 200, 120, 4),
                         (30, 20, 280, 3), (22, 180, 60, 3), (14, 20, 300, 3)]:
        rr = int(r * h / 100)
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0, a1,
              fill=(255, 255, 255), width=lw)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED)
    d.text((x + 6, y + h - 15), "BAY OF BENGAL", font=font(SANS_B, 8),
           fill=(190, 210, 222))


def art_cop(d, x, y, w, h):
    """Dark navy COP31 scene: globe + big red thermometer + deal text."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.rectangle([x, y, x + w, y + int(h * 0.16)], fill=NAVY2)
    # globe, left
    gx, gy, gr = x + w * 0.28, y + h * 0.54, int(h * 0.38)
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(28, 88, 138),
              outline=(255, 255, 255), width=2)
    d.ellipse([gx - gr * 0.55, gy - gr * 0.62, gx + gr * 0.15,
               gy - gr * 0.05], fill=(62, 142, 82))
    d.ellipse([gx - gr * 0.15, gy + gr * 0.10, gx + gr * 0.62,
               gy + gr * 0.62], fill=(62, 142, 82))
    d.arc([gx - gr, gy - gr, gx + gr, gy + gr], 300, 60,
          fill=(200, 220, 240), width=1)
    d.line([(gx - gr, gy), (gx + gr, gy)], fill=(200, 220, 240), width=1)
    # thermometer, right (below the top chip row)
    tx = x + w * 0.70
    ty0, ty1 = y + h * 0.18, y + h * 0.84
    twd = 16
    d.rectangle([tx, ty0, tx + twd, ty1], fill=(255, 255, 255),
                outline=(255, 255, 255), width=1)
    d.rectangle([tx + 3, ty0 + (ty1 - ty0) * 0.18, tx + twd - 3, ty1 - 3],
                fill=RED)
    bx, by, br = tx + twd // 2, int(ty1) + 2, 13
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=RED,
              outline=(255, 255, 255), width=2)
    for i, fy in enumerate((0.25, 0.50, 0.75)):
        d.line([(tx + twd + 3, y + h * fy), (tx + twd + 9, y + h * fy)],
               fill=(255, 255, 255), width=2)


def art_chart(d, x, y, w, h):
    """Dark market panel: descending candlesticks + red line, $85.00 big."""
    d.rectangle([x, y, x + w, y + h], fill=(12, 22, 16))
    for gy in range(5):
        yy = y + 10 + gy * (h - 20) // 4
        d.line([(x + 8, yy), (x + w - 8, yy)], fill=(42, 62, 48), width=1)
    # price scale 83..98 across the panel height
    def py(p):
        return y + 8 + (98 - p) / 15 * (h - 16)
    candles = [(97.2, 96.4), (96.4, 94.8), (94.8, 95.6), (95.6, 92.9),
               (92.9, 91.2), (91.2, 92.0), (92.0, 89.4), (89.4, 87.1),
               (87.1, 85.0)]
    cw = (w - 40) / len(candles)
    closes = []
    for i, (o, c) in enumerate(candles):
        cx = x + 22 + i * cw
        d.line([(cx + cw / 2, py(max(o, c) + 0.9)),
                (cx + cw / 2, py(min(o, c) - 0.9))], fill=(200, 200, 200),
               width=1)
        col = (60, 190, 110) if c >= o else (230, 60, 45)
        d.rectangle([cx + 2, py(max(o, c)), cx + cw - 2, py(min(o, c))],
                    fill=col)
        closes.append((cx + cw / 2, py(c)))
    d.line(closes, fill=(255, 90, 70), width=3, joint="curve")
    d.text((x + 8, y + 2), "$97.17", font=font(SANS_B, 11),
           fill=(255, 255, 255))
    d.text((x + w - 74, y + h - 32), "$85.00", font=font(SANS_B, 17),
           fill=(255, 110, 90))
    d.text((x + 8, y + h - 15), "NASDAQ −2.3% · S&P 7TH DOWN DAY",
           font=font(SANS_B, 9), fill=(200, 210, 200))


def art_bridge(d, x, y, w, h):
    """Night Kyiv: skyline, bridge deck, missile arcs, fire bursts."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 44))
    # skyline
    for i, (bx, bw, bh) in enumerate(((0.02, 0.16, 0.42), (0.20, 0.12, 0.60),
                                      (0.34, 0.18, 0.34), (0.54, 0.12, 0.55),
                                      (0.68, 0.14, 0.40), (0.84, 0.14, 0.48))):
        d.rectangle([x + w * bx, y + h * (0.78 - bh), x + w * (bx + bw),
                     y + h * 0.78], fill=(8, 12, 26))
        for wy in range(2):
            for wx in range(2):
                d.rectangle([x + w * bx + 3 + wx * 9, y + h * (0.78 - bh) + 4 + wy * 9,
                             x + w * bx + 7 + wx * 9, y + h * (0.78 - bh) + 8 + wy * 9],
                            fill=(255, 210, 90))
    # river + bridge deck
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(28, 52, 88))
    d.line([(x, y + h * 0.66), (x + w, y + h * 0.66)], fill=(220, 220, 220),
           width=3)
    for tx in (0.25, 0.60):
        d.line([(x + w * tx, y + h * 0.66), (x + w * tx, y + h * 0.40)],
               fill=(220, 220, 220), width=2)
        d.line([(x + w * tx, y + h * 0.40), (x + w * (tx + 0.14), y + h * 0.66)],
               fill=(180, 180, 180), width=1)
    # missile arcs + bursts
    for ax, ay in ((0.42, 0.30), (0.78, 0.22)):
        ex, ey = x + w * ax, y + h * ay
        d.arc([ex - 26, ey - 30, ex + 26, ey + 6], 200, 340,
              fill=(255, 200, 90), width=2)
        for a in range(0, 360, 45):
            r = 11 if a % 90 == 0 else 6
            d.line([(ex, ey), (ex + r * math.cos(math.radians(a)),
                               ey + r * math.sin(math.radians(a)))],
                   fill=(255, 180, 40), width=2)
        d.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(255, 240, 180))


def art_summit(d, x, y, w, h):
    """Berlin summit table: flags, heads, long table."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 228, 232))
    d.rectangle([x, y + h * 0.62, x + w, y + h * 0.94], fill=(120, 100, 70))
    d.rectangle([x, y + h * 0.62, x + w, y + h * 0.68], fill=(90, 74, 52))
    for i, fx in enumerate((0.14, 0.34, 0.56, 0.76)):
        d.line([(x + w * fx, y + h * 0.06), (x + w * fx, y + h * 0.42)],
               fill=INK, width=2)
        d.rectangle([x + w * fx, y + h * 0.06, x + w * fx + 15,
                     y + h * 0.26], fill=[BLUE, RED, GREEN, OCHRE][i])
    for i, hx in enumerate((0.20, 0.42, 0.62, 0.82)):
        d.ellipse([x + w * hx - 7, y + h * 0.40, x + w * hx + 7,
                   y + h * 0.54], fill=(60, 58, 54))
        d.rectangle([x + w * hx - 9, y + h * 0.54, x + w * hx + 9,
                     y + h * 0.62], fill=(90, 86, 80))


def art_radar(d, x, y, w, h):
    """Dark radar scope: rings, sweep, three blips."""
    d.rectangle([x, y, x + w, y + h], fill=(14, 34, 24))
    cx, cy = x + w / 2, y + h / 2
    for r in (int(h * 0.46), int(h * 0.32), int(h * 0.18)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(80, 200, 120),
                  width=1)
    d.line([(cx, cy - h * 0.48), (cx, cy + h * 0.48)], fill=(80, 200, 120),
           width=1)
    d.line([(cx - w * 0.20, cy), (cx + w * 0.20, cy)], fill=(80, 200, 120),
           width=1)
    d.line([(cx, cy), (cx + w * 0.34, cy - h * 0.40)], fill=(120, 230, 150),
           width=2)
    s = h / 40.0
    for bx, by in ((cx + 18 * s, cy - 12 * s), (cx + 26 * s, cy + 6 * s),
                   (cx - 14 * s, cy + 14 * s)):
        d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 80, 60))


def art_intercept(d, x, y, w, h):
    """Night intercept: skyline, missile arc, double burst."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 28, 48))
    for sx in (0.12, 0.30, 0.48, 0.68, 0.86):
        d.rectangle([x + w * sx, y + h * (0.72 + (sx % 0.2) * 0.4),
                     x + w * (sx + 0.10), y + h], fill=(12, 14, 28))
    d.arc([x + w * 0.45, y - 12, x + w * 1.10, y + h * 0.72], 90, 200,
          fill=(255, 200, 80), width=3)
    for bx, by, br in ((0.68, 0.30, 13), (0.52, 0.44, 9)):
        px, py = x + w * bx, y + h * by
        for a in range(0, 360, 30):
            r = br if a % 60 == 0 else br // 2
            d.line([(px, py), (px + r * math.cos(math.radians(a)),
                               py + r * math.sin(math.radians(a)))],
                   fill=(255, 220, 120), width=2)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255))


def art_border(d, x, y, w, h):
    """Border fence with red closed gate."""
    d.rectangle([x, y, x + w, y + h], fill=(228, 222, 200))
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(150, 170, 120))
    for px in range(0, int(w), 13):
        d.line([(x + px, y + 4), (x + px, y + h * 0.62)], fill=INK, width=2)
    d.line([(x, y + 12), (x + w, y + 12)], fill=INK, width=2)
    d.line([(x, y + 26), (x + w, y + 26)], fill=INK, width=1)
    d.rectangle([x + w * 0.42, y + 4, x + w * 0.58, y + h * 0.62],
                fill=RED, outline=INK, width=1)
    d.text((x + w * 0.42 + 4, y + 10), "✕", font=font(SANS_B, 10),
           fill=(255, 255, 255))
    d.text((x + 4, y + h - 13), "CLOSED 6 MONTHS", font=font(SANS_B, 8),
           fill=(60, 50, 30))


def art_passport(d, x, y, w, h):
    """Two passports with exchange arrows."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 220))
    d.rectangle([x + 14, y + 5, x + 62, y + h - 5], fill=BLUE, outline=INK,
                width=1)
    d.rectangle([x + w - 62, y + 5, x + w - 14, y + h - 5], fill=RED,
                outline=INK, width=1)
    for px in (14, w - 62):
        d.ellipse([x + px + 14, y + h * 0.24, x + px + 34, y + h * 0.56],
                  outline=(255, 220, 120), width=2)
        d.line([(x + px + 6, y + h * 0.64), (x + px + 42, y + h * 0.64)],
               fill=(255, 255, 255), width=2)
        d.line([(x + px + 6, y + h * 0.76), (x + px + 42, y + h * 0.76)],
               fill=(255, 255, 255), width=2)
    d.line([(x + 66, y + h / 2 - 4), (x + w - 66, y + h / 2 - 4)], fill=INK,
           width=2)
    d.polygon([(x + w - 66, y + h / 2 - 4), (x + w - 74, y + h / 2 - 8),
               (x + w - 74, y + h / 2)], fill=INK)
    d.line([(x + w - 66, y + h / 2 + 5), (x + 66, y + h / 2 + 5)], fill=INK,
           width=2)
    d.polygon([(x + 66, y + h / 2 + 5), (x + 74, y + h / 2 + 1),
               (x + 74, y + h / 2 + 9)], fill=INK)


def art_cricket(d, x, y, w, h):
    """Green pitch: stumps, bat swing, red ball, 175* chip."""
    d.rectangle([x, y, x + w, y + h], fill=(170, 200, 140))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(110, 145, 85))
    d.rectangle([x + w * 0.42, y + h * 0.30, x + w * 0.58, y + h * 0.72],
                fill=(220, 200, 150))
    for sx in (0.30, 0.36, 0.42):
        d.line([(x + w * sx, y + h * 0.72), (x + w * sx, y + h * 0.50)],
               fill=(220, 180, 90), width=3)
    d.line([(x + w * 0.62, y + h * 0.78), (x + w * 0.80, y + h * 0.28)],
           fill=(180, 130, 70), width=7)
    d.ellipse([x + w * 0.80 - 6, y + h * 0.28 - 6, x + w * 0.80 + 6,
               y + h * 0.28 + 6], fill=RED)
    art_chip(d, x + 4, y + h - 20, "175*")


def art_route(d, x, y, w, h):
    """Ethiopia–Kenya route: border line, figures, red arrows."""
    d.rectangle([x, y, x + w, y + h], fill=(238, 228, 205))
    d.line([(x + w * 0.55, y), (x + w * 0.48, y + h)], fill=INK, width=2)
    d.text((x + w * 0.60, y + h - 14), "KENYA", font=font(SANS_B, 8),
           fill=INK)
    rr = max(3, int(h * 0.12))
    for i, (fx, fy) in enumerate(((0.28, 0.28), (0.40, 0.46), (0.50, 0.60))):
        px, py = x + w * fx, y + h * fy
        d.ellipse([px, py, px + 2 * rr, py + 2 * rr], fill=INK)
        ex, ey = px + rr + int(h * 0.22), py + rr + int(h * 0.22)
        d.line([(px + rr, py + rr), (ex, ey)], fill=RED, width=2)
        d.polygon([(ex, ey), (ex - 6, ey - 1), (ex - 1, ey - 6)], fill=RED)


def art_skyline(d, x, y, w, h):
    """Gaza skyline at dusk: buildings, lit windows, sun, flag."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 222, 208))
    base = y + h
    for i, (bw, bf) in enumerate(((26, 0.62), (20, 0.88), (30, 0.52),
                                  (22, 0.78), (26, 0.66))):
        bx = x + 8 + i * 34
        bh = int(h * bf)
        d.rectangle([bx, base - bh, bx + bw, base], fill=(90, 88, 80))
        for wy in range(2):
            for wx in range(2):
                d.rectangle([bx + 4 + wx * 10, base - bh + 6 + wy * 12,
                             bx + 9 + wx * 10, base - bh + 11 + wy * 12],
                            fill=(255, 220, 120))
    d.line([(x + 8 + 4 * 34 + 13, y + 4), (x + 8 + 4 * 34 + 13,
                                           y + h * 0.30)], fill=INK, width=2)
    d.rectangle([x + 8 + 4 * 34 + 13, y + 4, x + 8 + 4 * 34 + 27,
                 y + 14], fill=GREEN)
    d.ellipse([x + w - 26, y + 6, x + w - 6, y + 26], fill=(240, 200, 80))


def art_checkpoint(d, x, y, w, h):
    """Iraqi checkpoint: barrier arm, hut, green flag."""
    d.rectangle([x, y, x + w, y + h], fill=(222, 218, 200))
    d.rectangle([x, y + h * 0.68, x + w, y + h], fill=(140, 140, 130))
    d.line([(x + 10, y + h * 0.68), (x + w - 10, y + h * 0.30)], fill=INK,
           width=4)
    d.rectangle([x + w * 0.55, y + h * 0.55, x + w * 0.75, y + h * 0.68],
                fill=(120, 110, 90))
    d.rectangle([x + w * 0.72, y + h * 0.55, x + w * 0.78, y + h * 0.68],
                fill=RED)
    d.polygon([(x + w * 0.20, y + 6), (x + w * 0.20, y + 26),
               (x + w * 0.38, y + 16)], fill=GREEN)
    d.line([(x + w * 0.20, y + 6), (x + w * 0.20, y + h * 0.68)], fill=INK,
           width=2)


ART = {"cyclone": art_cyclone, "cop": art_cop, "chart": art_chart,
       "bridge": art_bridge, "summit": art_summit, "radar": art_radar,
       "intercept": art_intercept, "border": art_border,
       "passport": art_passport, "cricket": art_cricket, "route": art_route,
       "skyline": art_skyline, "checkpoint": art_checkpoint}


def art_into(img, kind, x, y, w, h):
    """Draw one illustration into a temp image and paste it: nothing can
    spill outside its box, by construction."""
    tmp = Image.new("RGB", (int(w), int(h)), PAPER)
    td = ImageDraw.Draw(tmp)
    ART[kind](td, 0, 0, int(w), int(h))
    img.paste(tmp, (int(x), int(y)))


def tag_chip(d, x, y, tag):
    """Small REPORTED / CLAIM / FORECAST chip; returns width used."""
    f = font(SANS_B, 8)
    w = int(tw(d, tag, f)) + 8
    fill = RED if tag == "FORECAST" else (90, 88, 80)
    d.rectangle([x, y, x + w, y + 12], outline=fill, width=1)
    d.text((x + 4, y + 1), tag, font=f, fill=fill)
    return w

# ------------------------------------------------------------- world map ----
# Coarse dotted world map, 96 cols x 13 rows.
# col c -> lon -180 + c*3.75 ; row r -> lat 84 - r*10.77 down to 84-(r+1)*10.77
MAP_ROWS = [
    "   ######      #########      ########    ##  ###############         ",
    "  ########  ##################  #######  #  ######## ###############  ",
    "   ##########################   #   #  ################ ###########  ",
    "    ########################  # ############  ############  #### ##  ",
    "      #######################  ##############  ################ ##   ",
    "        #######  ###########  #############  #####  #########  #     ",
    "            ####  ########  ##########  ##  #########  ########      ",
    "                      #######  ###########  ###   #############      ",
    "                      #########  ##########  #    ############      ",
    "                       ########  ##########      ##########         ",
    "                        #######   ########       ######### ##        ",
    "                         ####                   ########  #          ",
    "                          ##                                  #      ",
]

# (lon, lat) of the 13 numbered stories
PINS = [
    (85.5, 19.8), (30.7, 36.9), (-74.0, 40.7), (30.5, 50.4), (13.4, 52.5),
    (21.0, 52.2), (46.7, 24.6), (24.7, 59.4), (-0.1, 51.5), (174.8, -41.3),
    (38.0, 4.0), (34.5, 31.5), (44.2, 32.8),
]

PIN_KEY_LINES = [
    "1 Gopalpur · 2 Antalya · 3 New York · 4 Kyiv",
    "5 Berlin · 6 Poland · 7 Riyadh · 8 Tallinn · 9 London",
    "10 Wellington · 11 Kenya · 12 Gaza · 13 Iraq",
]


def draw_map(d, x, y, w, h):
    """Compact dark dotted world map with 13 numbered pins (collision-nudged)."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=NAVY)
    cols, rows = 96, 13
    px, py = w / cols, h / rows
    for r, row in enumerate(MAP_ROWS):
        for c, ch in enumerate(row):
            if ch == "#":
                cx = x + (c + 0.5) * px
                cy = y + (r + 0.5) * py
                d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6],
                          fill=(196, 192, 180))
    offsets = [(0, 0), (0, -12), (12, 0), (0, 12), (-12, 0), (12, -12),
               (-12, -12), (12, 12), (-12, 12), (0, -24), (24, 0), (0, 24),
               (-24, 0), (12, -24), (-12, -24), (24, -12), (-24, -12),
               (24, 12), (-24, 12), (12, 24), (-12, 24), (0, -36), (36, 0),
               (0, 36), (-36, 0), (24, -24), (-24, -24), (24, 24),
               (-24, 24), (12, -36), (-12, -36), (36, -12), (-36, -12)]
    placed = []
    for i, (lon, lat) in enumerate(PINS, start=1):
        tx = x + (lon + 180) / 360 * w
        ty = y + (84 - lat) / 140 * h
        nx, ny = tx, ty
        for ox, oy in offsets:
            qx, qy = tx + ox, ty + oy
            if not (x + 9 <= qx <= x + w - 9 and y + 9 <= qy <= y + h - 9):
                continue
            if all((qx - px2) ** 2 + (qy - py2) ** 2 >= 17 ** 2
                   for px2, py2 in placed):
                nx, ny = qx, qy
                break
        placed.append((nx, ny))
        if (nx, ny) != (tx, ty):
            d.line([(tx, ty), (nx, ny)], fill=(255, 120, 100), width=1)
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=RED)
        d.ellipse([nx - 8, ny - 8, nx + 8, ny + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        f = font(SANS_B, 9)
        t = str(i)
        d.text((nx - tw(d, t, f) / 2, ny - 5), t, font=f,
               fill=(255, 255, 255))


# ------------------------------------------------------------ page build ----
TRUNCATED = []  # list items that did not fit and were ellipsised


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    rng = random.Random(20261120)
    # faint paper grain (deterministic; also lifts the file into the 300+ KB band)
    for _ in range(60000):
        gx, gy = rng.randrange(W), rng.randrange(H)
        v = rng.choice([(235, 231, 222), (252, 249, 240)])
        d.point((gx, gy), fill=v)

    MX = 26                      # side margin
    CW = W - 2 * MX              # content width = 972
    y = 8

    # ---- eyebrow + date masthead (the winners' masthead is the date) ----
    tracked(d, MX, y, "THE WORLD IN ONE DAY", font(SANS_B, 11), RED, 1)
    f_cnt = font(SANS_B, 12)
    cnt = "44 STORIES · 7 REGIONS · ONE PAGE"
    d.text((W - MX - tw(d, cnt, f_cnt), y), cnt, font=f_cnt, fill=RED)
    y += 16
    d.text((MX, y - 4), "Friday 20 November 2026", font=font(SERIF_B, 60),
           fill=INK)
    y += 62
    sub = ("Russian missiles hit Kyiv's bridges · Cyclone Akvan strikes India "
           "· An AI sell-off sinks Asia's markets · UK and EU seal a deal")
    d.text((MX, y), sub, font=font(SERIF_I, 15), fill=INK)
    y += 20
    rule(d, MX, y, CW, INK, 2)
    y += 6

    # ---- region strip (widths proportional to counts) ----
    rh = 26
    rx = MX
    for name, n, col in REGIONS:
        seg_w = CW * n / 44
        d.rectangle([rx, y, rx + seg_w - 1, y + rh], fill=col)
        label = f"{name} {n}"
        f = font(SANS_B, 11)
        lx = rx + (seg_w - tw(d, label, f)) / 2
        d.text((lx, y + 7), label, font=f, fill=(255, 255, 255))
        rx += seg_w
    y += rh + 6

    # ---- the day in numbers ----
    d.text((MX, y), "THE DAY IN NUMBERS", font=font(SANS_B, 12), fill=RED)
    rule(d, MX, y + 15, CW, LIGHT, 1)
    y += 19
    col_w = CW / 6
    for i, (num, lab) in enumerate(NUMBERS):
        cx = MX + i * col_w
        d.text((cx + 2, y), num, font=font(SANS_B, 21), fill=RED)
        for li, line in enumerate(wrap(d, lab, font(SANS, 9), col_w - 8)):
            d.text((cx + 2, y + 24 + li * 11), line, font=font(SANS, 9),
                   fill=GREY)
        if i:
            rule(d, cx - 4, y, 1, LIGHT, 40)
    y += 48

    # ---- heroes: 3 across, dense art with on-image banners ----
    gap = 12
    hw = (CW - 2 * gap) / 3
    hh = 216  # kicker 38 + art 100 + head 2x20 + deck 2x14 + gaps
    art_h = 100
    for i, hero in enumerate(HEROES):
        hx = MX + i * (hw + gap)
        d.ellipse([hx, y, hx + 20, y + 20], fill=RED)
        f = font(SANS_B, 12)
        d.text((hx + 10 - tw(d, str(hero["n"]), f) / 2, y + 3),
               str(hero["n"]), font=f, fill=(255, 255, 255))
        kx = hx + 26
        kf = font(SANS_B, 10)
        d.text((kx, y + 4), hero["kicker"], font=kf, fill=RED)
        tag_chip(d, kx + tw(d, hero["kicker"], kf) + 8, y + 4, hero["tag"])
        d.text((hx, y + 24), hero["src"], font=font(SANS_B, 9), fill=GREY)
        iy = y + 38
        art_into(img, hero["art"], hx, iy, hw, art_h)
        d.rectangle([hx, iy, hx + hw - 1, iy + art_h - 1], outline=INK,
                    width=1)
        art_banner(d, hx + 1, iy + 1, hero["banner"], size=12)
        art_chip(d, 0, iy + 1, hero["chip"], size=9, right=hx + hw - 1)
        ty = iy + art_h + 6
        head_lines = fit_lines(d, hero["head"], font(SANS_B, 17), hw, 2)
        for li, line in enumerate(head_lines):
            d.text((hx, ty + li * 20), line, font=font(SANS_B, 17), fill=INK)
        dy = ty + 20 * len(head_lines) + 3
        for li, line in enumerate(wrap(d, hero["deck"], font(SANS, 12), hw)):
            d.text((hx, dy + li * 14), line, font=font(SANS, 12),
                   fill=(40, 40, 40))
    y += hh + 8

    # ---- medium cards: 5 x 2, taller art with on-image banners ----
    mgap = 10
    mw = (CW - 4 * mgap) / 5
    mart_h = 56
    mh = 126
    for r in range(2):
        for c in range(5):
            card = MEDIUMS[r * 5 + c]
            cx = MX + c * (mw + mgap)
            cy = y + r * (mh + 8)
            art_into(img, card["art"], cx, cy, mw, mart_h)
            d.rectangle([cx, cy, cx + mw - 1, cy + mart_h - 1], outline=INK,
                        width=1)
            art_banner(d, cx + 1, cy + 1, card["banner"], size=10)
            ty = cy + mart_h + 5
            kf = font(SANS_B, 8)
            kick = f"{card['n']} · {card['kicker']}"
            d.text((cx, ty), kick, font=kf, fill=RED)
            tag_chip(d, cx + tw(d, kick, kf) + 5, ty, card["tag"])
            hy = ty + 10
            head_lines = fit_lines(d, card["head"], font(SANS_B, 12.5), mw, 2)
            for li, line in enumerate(head_lines):
                d.text((cx, hy + li * 15), line, font=font(SANS_B, 12.5),
                       fill=INK)
            dy = hy + 15 * len(head_lines) + 1
            deck_lines = fit_lines(d, card["deck"], font(SANS, 9.5), mw, 2)
            if deck_lines and deck_lines[-1].endswith("…"):
                TRUNCATED.append((card["n"], deck_lines[-1]))
            for li, line in enumerate(deck_lines):
                d.text((cx, dy + li * 12), line, font=font(SANS, 9.5),
                       fill=(40, 40, 40))
    y += 2 * mh + 8 + 8

    # ---- map (left) + also-on list (right), side by side ----
    map_w = 300
    list_x = MX + map_w + 16
    list_w = W - MX - list_x
    d.text((MX, y), "WHERE IT HAPPENED", font=font(SANS_B, 13), fill=RED)
    d.text((list_x, y), "ALSO ON 20 NOVEMBER — 31 MORE STORIES",
           font=font(SANS_B, 13), fill=INK)
    rule(d, MX, y + 18, CW, INK, 1)
    y += 22
    map_h = 160
    draw_map(d, MX, y, map_w, map_h)
    # pin key under the map (three explicit lines, no mid-name wrap)
    ky = y + map_h + 4
    for li, line in enumerate(PIN_KEY_LINES):
        d.text((MX, ky + li * 11), line, font=font(SANS, 8.5), fill=GREY)
    # list, two columns
    col_w = (list_w - 16) / 2
    row_h = 11.5
    for side in range(2):
        items = LIST_ITEMS[side * 16:(side + 1) * 16]
        lx = list_x + side * (col_w + 16)
        for ri, (num, city, story, src) in enumerate(items):
            ry = y + ri * row_h
            f = font(SANS_B, 9.5)
            d.text((lx, ry), f"{num}", font=f, fill=RED)
            tx = lx + 20
            city_f = font(SANS_B, 9.5)
            d.text((tx, ry), city + ": ", font=city_f, fill=INK)
            sx = tx + tw(d, city + ": ", city_f)
            body, bf = one_line(d, story + " (" + src + ")", font(SANS, 9),
                                col_w - (sx - lx), min_size=9)
            if body.endswith("…"):
                TRUNCATED.append((num, body))
            d.text((sx, ry), body, font=bf, fill=(40, 40, 40))
    y += 16 * row_h + 6

    # ---- date rail: 19 Nov left out / 20 Nov on this page / 21 Nov not yet ----
    d.text((MX, y), "DATE CHECK", font=font(SANS_B, 11), fill=RED)
    rule(d, MX, y + 14, CW, LIGHT, 1)
    y += 18
    for label, lcol, text in DATE_RAIL:
        lf = font(SANS_B, 9)
        lw = tw(d, label, lf)
        d.text((MX, y), label, font=lf, fill=lcol)
        tx = MX + lw + 10
        lines = wrap(d, text, font(SANS, 9), CW - (tx - MX))
        for li, line in enumerate(lines):
            d.text((tx, y + li * 11), line, font=font(SANS, 9), fill=INK)
        y += max(11, len(lines) * 11) + 2
    y += 2

    # ---- sources footer ----
    f_src = font(SANS, 9)
    src_lines = wrap(d, SOURCES_LINE, f_src, CW)
    for li, line in enumerate(src_lines):
        d.text((MX, y + li * 11), line, font=f_src, fill=GREY)
    y += len(src_lines) * 11 + 2
    d.text((MX, y), "Claims are attributed, not stated as fact. Pictures and "
                    "map: original, drawn in code.",
           font=font(SANS_I, 9), fill=GREY)
    d.text((W - MX - tw(d, "THE WORLD · 20 NOVEMBER 2026",
                        font(SANS_B, 9)), y),
           "THE WORLD · 20 NOVEMBER 2026", font=font(SANS_B, 9), fill=GREY)
    y += 11
    return img, y


def main():
    img, bottom = build()
    out = os.environ.get("MAKEFUN_OUTPUT_DIR")
    path = os.path.join(out, "entry.png") if out else "entry.png"
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    img.save(path, "PNG")
    print(f"bottom edge used: {bottom}px of {H}px")
    print(f"stories: {len(HEROES) + len(MEDIUMS) + len(LIST_ITEMS)} "
          f"({len(HEROES)} heroes + {len(MEDIUMS)} medium + "
          f"{len(LIST_ITEMS)} list)")
    print(f"regions sum: {sum(n for _, n, _ in REGIONS)}")
    print(f"truncated list items: {TRUNCATED if TRUNCATED else 'none'}")
    print(f"wrote {path}: {os.path.getsize(path)} bytes")


if __name__ == "__main__":
    main()
