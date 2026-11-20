#!/usr/bin/env python3
"""THE WORLD — 20 November 2026. One-image front page, 1024x1024.
Draws the entry with PIL (local build tool). The grader runs main.py,
which copies the committed entry.png to /output/entry.png.
All 44 stories verified 20 Nov 2026; see the design spec for sources.
Palette: off-white paper, near-black ink, one red accent. No raster art:
every illustration is drawn in code with vector-style shapes."""

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


# ---------------------------------------------------------------- data ----
HEROES = [
    dict(n=1, kicker="ASIA · WEATHER", src="REUTERS", tag="REPORTED",
         art="cyclone",
         head="Cyclone Akvan makes landfall on India's east coast",
         deck="Crossed near Gopalpur at 70–80 km/h, gusting to 90. "
              "Over 300,000 evacuated; no deaths reported."),
    dict(n=2, kicker="WORLD · CLIMATE", src="UN NEWS", tag="FORECAST",
         art="cop",
         head="COP31 enters its final day with no deal in sight",
         deck="Antalya talks end with no agreement; the draft drops fossil "
              "fuels and the $120bn figure."),
    dict(n=3, kicker="AMERICAS · MARKETS", src="IBD · WSJ", tag="REPORTED",
         art="chart",
         head="Anthropic slides 10% on day two as markets rout deepens",
         deck="Shares fell to about $85, near the $83 IPO price. The S&P 500 "
              "headed for a seventh straight down day."),
]

MEDIUMS = [
    dict(n=4, kicker="EUROPE · WAR", src="BBC", tag="REPORTED", art="bridge",
         head="Russia strikes Kyiv's bridges overnight; 8 killed",
         deck="Strikes hit Dnipro bridges; 8 killed, 28 injured in nine regions."),
    dict(n=5, kicker="EUROPE · DIPLOMACY", src="TBS · BBC", tag="REPORTED",
         art="summit",
         head="European leaders ready to negotiate with Russia",
         deck="Berlin summit: Burnham cites unity; Merz rejects Moscow's demands."),
    dict(n=6, kicker="EUROPE · SECURITY", src="REUTERS", tag="REPORTED",
         art="radar",
         head="Russia violates Poland's airspace overnight",
         deck="Two missiles and a drone crossed as Poland prepared exercises."),
    dict(n=7, kicker="MIDDLE EAST · SECURITY", src="REUTERS", tag="REPORTED",
         art="intercept",
         head="Saudi Arabia intercepts Houthi missile and two drones",
         deck="Missile and two drones intercepted; alerts in Riyadh, Najran."),
    dict(n=8, kicker="EUROPE · SECURITY", src="REUTERS", tag="REPORTED",
         art="border",
         head="Estonia to close Russia border for at least six months",
         deck="Tallinn announced the closure; Moscow threatened a response."),
    dict(n=9, kicker="EUROPE · POLITICS", src="BBC", tag="REPORTED",
         art="passport",
         head="UK–EU agree youth mobility scheme, 100,000 a year",
         deck="To be agreed Friday; the EU wants UK tuition fees cut."),
    dict(n=10, kicker="OCEANIA · SPORT", src="REUTERS", tag="REPORTED",
         art="cricket",
         head="India fight back in Wellington after NZ post 368",
         deck="Nicholls 175*, Phillips 118; Jaiswal's 85 led a 130-run stand."),
    dict(n=11, kicker="AFRICA · CONFLICT", src="JUBA GLOBAL NEWS",
         tag="REPORTED", art="route",
         head="50,000 flee Ethiopia fighting into Kenya",
         deck="Fleeing violence into Kenya; El Niño floods batter Kenya."),
    dict(n=12, kicker="MIDDLE EAST · CONFLICT", src="MITZPE INSTITUTE",
         tag="REPORTED", art="skyline",
         head="Hamas government is back on its feet in Gaza",
         deck="All 17 ministries back at work, plus 22 of 25 municipalities."),
    dict(n=13, kicker="MIDDLE EAST · SECURITY", src="REUTERS", tag="REPORTED",
         art="checkpoint",
         head="Iraq deploys forces against Iran-aligned Kataib Hezbollah",
         deck="Deployed in Jurf al-Sakhar to limit the group, accused of smuggling."),
]

LIST_ITEMS = [
    (14, "London", "RAF Fairford defendants to stand trial in Nov 2027; Iran alleged behind it", "Reuters"),
    (15, "London", "UK running offensive cyber operations on Russia, China, Iran, N. Korea, top general says", "Sky News"),
    (16, "Washington", "Kushner floated NATO membership for Ukraine in exchange for ceding land, WSJ reports", "WSJ"),
    (17, "Yangon", "Myanmar dismisses the ICJ genocide ruling", "BBC"),
    (18, "Washington", "DOJ assigns Bill Essayli to the Mar-a-Lago \u201cgrand conspiracy\u201d probe", "Politico"),
    (19, "Washington", "Sen. Tillis plans to block the Ueland GAO confirmation", "Politico"),
    (20, "Washington", "Sen. Wyden urges Congress to secure lawmakers' phones", "NYT"),
    (21, "Washington", "AI Safety and Innovation Caucus forms in Congress", "Politico"),
    (22, "Juba", "US deportee families endured hunger and thirst, AP reports", "AP"),
    (23, "Georgetown", "Ex-US official suggested Guyana cede land to Venezuela, Reuters reports", "Reuters"),
    (24, "Beqaa", "Israel hits a Hezbollah missile factory again — second strike near Janta in four days", "Mitzpe"),
    (25, "Peshawar", "Pakistan forces kill 22 militants near the Afghan frontier", "Bangladesh Chronicle"),
    (26, "Dhaka", "Bangladesh tense after opposition shutdown and political violence", "Bangladesh Chronicle"),
    (27, "New Delhi", "India relaxes vessel-age restrictions", "Bangladesh Chronicle"),
    (28, "Shenzhen", "Middle powers make their own moves as Trump courts Xi and Putin", "Reuters"),
    (29, "South Kordofan", "Drone strike kills 10 at a gold mine", "One Turn"),
    (30, "Juba", "South Sudan launches its first Institute of Certified Public Accountants", "Juba Global News"),
    (31, "Johannesburg", "Rand nears a one-year low; gold heads for worst week in 8 months", "Juba Global News"),
    (32, "Geneva", "UN warns antibiotics are failing against common infections", "Juba Global News"),
    (33, "Dakar", "Senegal president implements 2026 budget changes by decree", "Juba Global News"),
    (34, "Dakar", "Migrant boat capsizes off Senegal; dozens missing", "One Turn"),
    (35, "Nairobi", "El Niño floods batter Kenya", "Juba Global News"),
    (36, "Canberra", "Albanese challenged Putin over Ukraine at APEC, Guardian reports", "Guardian"),
    (37, "Invercargill", "Southland storm review finds poor communication, stretched staffing", "RNZ"),
    (38, "London", "Beauden Barrett to win his 150th Test cap against England at Twickenham", "Reuters"),
    (39, "Manchester", "Pochettino's first Man Utd session filmed by a drone; operator apologises", "Guardian"),
    (40, "Colombo", "India A beat Nepal by 306 runs — Nepal 26 all out in Rising Stars Asia Cup", "Inshorts"),
    (41, "Rawalpindi", "Pakistan beat Sri Lanka by 8 wickets to seal the Test series 1–0", "Inshorts"),
    (42, "Colombo", "Sri Lanka close 2026 without a single Test win — first time since 1997", "Inshorts"),
    (43, "Nairobi", "Peres Jepchirchir receives a three-year doping ban", "mykhel"),
    (44, "Budapest", "Carlsen stages an 11–9 comeback against Artemiev", "Inshorts"),
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

DATE_CHECK = (
    "DATE CHECK — left out on purpose. These happened on 19 November, not 20 November: "
    "Trump–Xi–Putin summit; ICJ Myanmar ruling; COP31 draft; Anthropic IPO debut; GTA VI launch; "
    "Denmark Arctic pact; IMF debt warning; IEA data-centre report; 879,000 AI chips for China; "
    "Kerch Bridge strike; Bukele third-term launch; Kenya Ebola countdown; PIF Tower strike; "
    "White House cyber director. Not yet news on 20 Nov: the COP31 final deal; "
    "the Kerch Bridge road span reopening."
)

SOURCES_LINE = (
    "Sources: Reuters · BBC · AP · WSJ · AFP · Al Jazeera · Politico · NYT · Guardian · "
    "RNZ · Inshorts · Sky News · TBS News · Juba Global News · Mitzpe Institute · One Turn · "
    "Bangladesh Chronicle · IBD · UN News · BNN Bloomberg"
)

# ------------------------------------------------------- illustrations ----
def art_cyclone(d, x, y, w, h):
    """Cyclone spiral over the Bay of Bengal coastline."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 226, 232))
    d.polygon([(x + w * 0.62, y), (x + w, y), (x + w, y + h),
               (x + w * 0.55, y + h), (x + w * 0.48, y + h * 0.62),
               (x + w * 0.55, y + h * 0.35)], fill=(226, 211, 170))
    d.line([(x + w * 0.62, y), (x + w * 0.55, y + h * 0.35),
            (x + w * 0.48, y + h * 0.62), (x + w * 0.55, y + h)],
           fill=(120, 100, 70), width=2)
    cx, cy = x + w * 0.34, y + h * 0.52
    lw = max(2, int(h / 16))
    for r, a0, a1 in [(0.45, 20, 300), (0.35, 200, 120), (0.25, 20, 280),
                      (0.15, 180, 60)]:
        rr = int(h * r)
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0, a1,
              fill=(255, 255, 255), width=lw)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED)
    for i, ay in enumerate((0.30, 0.48, 0.66)):
        ax = x + w * (0.60 + i * 0.06)
        ay = y + h * ay
        d.line([(ax, ay), (ax + 14, ay)], fill=RED_DK, width=2)
        d.polygon([(ax + 14, ay), (ax + 9, ay - 3), (ax + 9, ay + 3)],
                  fill=RED_DK)
    d.text((x + 6, y + 4), "BAY OF BENGAL", font=font(SANS_B, 9),
           fill=(31, 78, 121))


def art_cop(d, x, y, w, h):
    """Antalya conference hall: rows of seats, flags, an empty deal table."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    d.rectangle([x, y, x + w, y + int(h * 0.16)], fill=(196, 178, 150))
    d.text((x + 8, y + 3), "ANTALYA · NO DEAL", font=font(SANS_B, 9),
           fill=(90, 70, 40))
    for i in range(9):
        fx = x + 14 + i * 32
        d.line([(fx, y + h * 0.24), (fx, y + h * 0.44)], fill=(90, 80, 60),
               width=2)
        d.rectangle([fx, y + h * 0.24, fx + 20, y + h * 0.34],
                    fill=[RED, BLUE, GREEN, OCHRE, PURPLE, TEAL, RUST,
                          (31, 78, 121), (60, 60, 60)][i])
    for r in range(2):
        for c in range(9):
            sx = x + 16 + c * 32
            sy = y + h * (0.50 + r * 0.14)
            d.ellipse([sx, sy, sx + 10, sy + 10], fill=(60, 60, 66))
            d.rectangle([sx - 2, sy + 11, sx + 12, sy + 19], fill=(90, 80, 70))
    d.rectangle([x + 10, y + h * 0.86, x + w - 10, y + h * 0.97],
                fill=(120, 90, 60))
    ccx, ccy, cr = x + w - 32, y + h * 0.90, 12
    d.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=PAPER,
              outline=INK, width=2)
    d.line([(ccx, ccy), (ccx, ccy - 8)], fill=INK, width=2)
    d.line([(ccx, ccy), (ccx + 7, ccy - 3)], fill=INK, width=2)


def art_chart(d, x, y, w, h):
    """Plunging market line chart, red arrow, $85 marker."""
    d.rectangle([x, y, x + w, y + h], fill=(250, 244, 238))
    for gy in range(5):
        yy = y + 10 + gy * (h - 20) // 4
        d.line([(x + 8, yy), (x + w - 8, yy)], fill=(222, 214, 200), width=1)
    pts = [(x + 12 + i * (w - 24) / 9,
            y + 14 + (h - 30) * v) for i, v in
           enumerate([0.05, 0.12, 0.10, 0.28, 0.34, 0.30, 0.55, 0.62, 0.78, 0.92])]
    d.line(pts, fill=RED, width=4, joint="curve")
    d.ellipse([pts[0][0] - 4, pts[0][1] - 4, pts[0][0] + 4, pts[0][1] + 4],
              fill=INK)
    d.text((pts[0][0] + 8, pts[0][1] - 13), "$97.17", font=font(SANS_B, 10),
           fill=INK)
    d.line([(x + 8, pts[-1][1]), (x + w - 8, pts[-1][1])],
           fill=RED_DK, width=1)
    d.text((x + w - 52, pts[-1][1] - 16), "$85.00", font=font(SANS_B, 11),
           fill=RED_DK)
    d.polygon([(pts[-1][0] - 2, pts[-1][1] - 16), (pts[-1][0] + 12, pts[-1][1] - 16),
               (pts[-1][0] + 5, pts[-1][1] - 2)], fill=RED)
    d.text((x + 8, y + h - 16), "NASDAQ −2.3% · S&P 7TH DOWN DAY",
           font=font(SANS_B, 9), fill=(90, 80, 70))


def art_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 210, 224))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(120, 150, 190))
    d.line([(x, y + h * 0.45), (x + w, y + h * 0.45)], fill=INK, width=3)
    for cx in range(4):
        bx = x + 12 + cx * (w - 24) // 3
        d.line([(bx, y + h * 0.45), (bx, y + h * 0.20)], fill=INK, width=2)
        d.line([(bx, y + h * 0.20), (bx + (w - 24) // 6, y + h * 0.45)],
               fill=INK, width=1)
    ex, ey = x + w * 0.72, y + h * 0.28
    for a in range(0, 360, 45):
        r = 12 if a % 90 == 0 else 6
        d.line([(ex, ey), (ex + r * math.cos(math.radians(a)),
                           ey + r * math.sin(math.radians(a)))],
               fill=(255, 180, 40), width=3)
    d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=RED)


def art_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 228, 232))
    d.arc([x + w * 0.5 - 52, y + h * 0.05, x + w * 0.5 + 52,
           y + h * 0.95], 180, 360, fill=INK, width=2)
    d.rectangle([x + w * 0.5 - 62, y + h * 0.62, x + w * 0.5 + 62,
                 y + h * 0.92], fill=(120, 100, 70))
    for i, fx in enumerate((0.18, 0.36, 0.64, 0.82)):
        d.line([(x + w * fx, y + h * 0.08), (x + w * fx, y + h * 0.45)],
               fill=INK, width=2)
        d.rectangle([x + w * fx, y + h * 0.08, x + w * fx + 14,
                     y + h * 0.28], fill=[BLUE, RED, GREEN, OCHRE][i])


def art_radar(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 40, 30))
    cx, cy = x + w / 2, y + h / 2
    for r in (int(h * 0.46), int(h * 0.32), int(h * 0.18)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(80, 200, 120),
                  width=1)
    d.line([(cx, cy - h * 0.48), (cx, cy + h * 0.48)], fill=(80, 200, 120),
           width=1)
    d.line([(cx - w * 0.20, cy), (cx + w * 0.20, cy)], fill=(80, 200, 120),
           width=1)
    s = h / 40.0
    for bx, by in ((cx + 18 * s, cy - 12 * s), (cx + 26 * s, cy + 6 * s),
                   (cx - 14 * s, cy + 14 * s)):
        d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 80, 60))


def art_intercept(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 34, 52))
    for sx, sy in ((0.25, 0.75), (0.55, 0.85), (0.80, 0.70)):
        d.line([(x + w * sx, y + h), (x + w * sx, y + h * 0.55)],
               fill=(200, 200, 210), width=2)
    d.arc([x + w * 0.55, y - 10, x + w * 1.15, y + h * 0.75], 90, 200,
          fill=(255, 200, 80), width=3)
    bx, by = x + w * 0.70, y + h * 0.32
    for a in range(0, 360, 30):
        r = 14 if a % 60 == 0 else 7
        d.line([(bx, by), (bx + r * math.cos(math.radians(a)),
                           by + r * math.sin(math.radians(a)))],
               fill=(255, 220, 120), width=2)
    d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(255, 255, 255))


def art_border(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 222, 200))
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(150, 170, 120))
    for px in range(0, int(w), 14):
        d.line([(x + px, y + 6), (x + px, y + h * 0.62)], fill=INK, width=2)
    d.line([(x, y + 14), (x + w, y + 14)], fill=INK, width=2)
    d.line([(x, y + 30), (x + w, y + 30)], fill=INK, width=1)
    d.rectangle([x + w * 0.42, y + 6, x + w * 0.58, y + h * 0.62],
                fill=RED, outline=INK, width=1)
    d.text((x + w * 0.42 + 3, y + 12), "✕", font=font(SANS_B, 10), fill=(255, 255, 255))


def art_passport(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 220))
    d.rectangle([x + 14, y + 6, x + 62, y + h - 6], fill=BLUE, outline=INK,
                width=1)
    d.rectangle([x + w - 62, y + 6, x + w - 14, y + h - 6], fill=RED,
                outline=INK, width=1)
    d.ellipse([x + 28, y + h * 0.28, x + 48, y + h * 0.60],
              outline=(255, 220, 120), width=2)
    d.line([(x + 20, y + h * 0.66), (x + 56, y + h * 0.66)],
           fill=(255, 255, 255), width=2)
    d.line([(x + 20, y + h * 0.78), (x + 56, y + h * 0.78)],
           fill=(255, 255, 255), width=2)
    d.ellipse([x + w - 48, y + h * 0.28, x + w - 28, y + h * 0.60],
              outline=(255, 220, 120), width=2)
    d.line([(x + w - 56, y + h * 0.66), (x + w - 20, y + h * 0.66)],
           fill=(255, 255, 255), width=2)
    d.line([(x + w - 56, y + h * 0.78), (x + w - 20, y + h * 0.78)],
           fill=(255, 255, 255), width=2)
    d.line([(x + 66, y + h / 2), (x + w - 66, y + h / 2)], fill=INK, width=2)
    d.polygon([(x + w - 66, y + h / 2), (x + w - 74, y + h / 2 - 4),
               (x + w - 74, y + h / 2 + 4)], fill=INK)
    d.polygon([(x + 66, y + h / 2), (x + 74, y + h / 2 - 4),
               (x + 74, y + h / 2 + 4)], fill=INK)


def art_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 228, 190))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(120, 150, 90))
    for sx in (0.30, 0.36, 0.42):
        d.line([(x + w * sx, y + h * 0.72), (x + w * sx, y + h * 0.50)],
               fill=(220, 180, 90), width=3)
    d.line([(x + w * 0.62, y + h * 0.78), (x + w * 0.78, y + h * 0.30)],
           fill=(180, 130, 70), width=7)
    d.ellipse([x + w * 0.78 - 6, y + h * 0.30 - 6, x + w * 0.78 + 6,
               y + h * 0.30 + 6], fill=RED)
    d.text((x + 24, y + 4), "368 · 175*", font=font(SANS_B, 10), fill=INK)


def art_route(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 228, 205))
    d.line([(x + w * 0.55, y), (x + w * 0.48, y + h)], fill=INK, width=2)
    d.text((x + 24, y + 4), "ETHIOPIA", font=font(SANS_B, 8), fill=INK)
    d.text((x + w * 0.60, y + h - 14), "KENYA", font=font(SANS_B, 8),
           fill=INK)
    rr = max(3, int(h * 0.12))
    for i, (fx, fy) in enumerate(((0.30, 0.30), (0.42, 0.48), (0.52, 0.62))):
        px, py = x + w * fx, y + h * fy
        d.ellipse([px, py, px + 2 * rr, py + 2 * rr], fill=INK)
        ex, ey = px + rr + int(h * 0.22), py + rr + int(h * 0.22)
        d.line([(px + rr, py + rr), (ex, ey)], fill=RED, width=2)
        d.polygon([(ex, ey), (ex - 6, ey - 1), (ex - 1, ey - 6)], fill=RED)


def art_skyline(d, x, y, w, h):
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
    d.ellipse([x + w - 26, y + 6, x + w - 6, y + 26], fill=(240, 200, 80))


def art_checkpoint(d, x, y, w, h):
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


def draw_map(d, x, y, w, h):
    """Dotted world map with 13 numbered pins (collision-nudged)."""
    cols, rows = 96, 13
    px, py = w / cols, h / rows
    for r, row in enumerate(MAP_ROWS):
        for c, ch in enumerate(row):
            if ch == "#":
                cx = x + (c + 0.5) * px
                cy = y + (r + 0.5) * py
                d.ellipse([cx - 2.4, cy - 2.4, cx + 2.4, cy + 2.4],
                          fill=(120, 116, 108))
    offsets = [(0, 0), (0, -17), (17, 0), (0, 17), (-17, 0), (17, -17),
               (-17, -17), (17, 17), (-17, 17), (0, -34), (34, 0), (0, 34),
               (-34, 0), (17, -34), (-17, -34), (34, -17), (-34, -17),
               (34, 17), (-34, 17), (17, 34), (-17, 34), (0, -51), (51, 0),
               (0, 51), (-51, 0), (34, -34), (-34, -34), (34, 34), (-34, 34)]
    placed = []
    for i, (lon, lat) in enumerate(PINS, start=1):
        tx = x + (lon + 180) / 360 * w
        ty = y + (84 - lat) / 140 * h
        nx, ny = tx, ty
        for ox, oy in offsets:
            px, py = tx + ox, ty + oy
            if not (x + 9 <= px <= x + w - 9 and y + 9 <= py <= y + h - 9):
                continue
            if all((px - qx) ** 2 + (py - qy) ** 2 >= 17 ** 2
                   for qx, qy in placed):
                nx, ny = px, py
                break
        placed.append((nx, ny))
        if (nx, ny) != (tx, ty):
            d.line([(tx, ty), (nx, ny)], fill=RED, width=1)
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=RED)
        d.ellipse([nx - 7.5, ny - 7.5, nx + 7.5, ny + 7.5], fill=RED,
                  outline=(255, 255, 255), width=1)
        f = font(SANS_B, 9)
        t = str(i)
        d.text((nx - tw(d, t, f) / 2, ny - 5), t, font=f,
               fill=(255, 255, 255))
    # labels on paper chips so they stay legible over the dots
    d.rectangle([x, y, x + 168, y + 15], fill=PAPER)
    d.text((x + 2, y + 2), "WHERE IT HAPPENED", font=font(SANS_B, 11),
           fill=RED)
    note = "Pins 1–13 match the numbered stories above"
    d.rectangle([x + w - 262, y, x + w, y + 15], fill=PAPER)
    d.text((x + w - 260, y + 2), note, font=font(SANS_I, 10), fill=GREY)


# ------------------------------------------------------------ page build ----
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

    # ---- masthead ----
    f_mast = font(SERIF_B, 58)
    d.text((MX, y - 4), "THE WORLD", font=f_mast, fill=INK)
    bx, by, bw, bh = W - MX - 208, y + 2, 208, 52
    d.rectangle([bx, by, bx + bw, by + bh], fill=RED)
    d.text((bx + 12, by + 4), "FRIDAY", font=font(SANS_B, 13),
           fill=(255, 255, 255))
    d.text((bx + 12, by + 22), "20 NOVEMBER 2026", font=font(SANS_B, 18),
           fill=(255, 255, 255))
    y += 60
    rule(d, MX, y, CW, INK, 2)
    y += 6
    sub = ("Everything on this page happened, or was first reported, on "
           "Friday 20 November 2026.")
    d.text((MX, y), sub, font=font(SERIF_I, 15), fill=INK)
    f_cnt = font(SANS_B, 13)
    cnt = "44 STORIES · 7 REGIONS · ONE PAGE"
    d.text((W - MX - tw(d, cnt, f_cnt), y + 1), cnt, font=f_cnt, fill=RED)
    y += 22
    rule(d, MX, y, CW, INK, 1)
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
        d.text((cx + 2, y), num, font=font(SANS_B, 21), fill=INK)
        for li, line in enumerate(wrap(d, lab, font(SANS, 9), col_w - 8)):
            d.text((cx + 2, y + 24 + li * 11), line, font=font(SANS, 9),
                   fill=GREY)
        if i:
            rule(d, cx - 4, y, 1, LIGHT, 40)
    y += 48

    # ---- heroes: 3 across ----
    gap = 12
    hw = (CW - 2 * gap) / 3
    hh = 208
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
        art_into(img, hero["art"], hx, iy, hw, 92)
        d.rectangle([hx, iy, hx + hw - 1, iy + 91], outline=INK, width=1)
        ty = iy + 100
        head_lines = fit_lines(d, hero["head"], font(SANS_B, 18), hw, 2)
        for li, line in enumerate(head_lines):
            d.text((hx, ty + li * 21), line, font=font(SANS_B, 18), fill=INK)
        dy = ty + 21 * len(head_lines) + 3
        for li, line in enumerate(wrap(d, hero["deck"], font(SANS, 12),
                                       hw)):
            d.text((hx, dy + li * 14), line, font=font(SANS, 12),
                   fill=(40, 40, 40))
    y += hh + 8

    # ---- medium cards: 5 x 2 ----
    mgap = 10
    mw = (CW - 4 * mgap) / 5
    mh = 101
    for r in range(2):
        for c in range(5):
            card = MEDIUMS[r * 5 + c]
            cx = MX + c * (mw + mgap)
            cy = y + r * (mh + 6)
            art_into(img, card["art"], cx, cy, mw, 32)
            d.rectangle([cx, cy, cx + mw - 1, cy + 31], outline=INK, width=1)
            d.ellipse([cx + 3, cy + 3, cx + 19, cy + 19], fill=RED)
            f = font(SANS_B, 10)
            d.text((cx + 11 - tw(d, str(card["n"]), f) / 2, cy + 5),
                   str(card["n"]), font=f, fill=(255, 255, 255))
            ty = cy + 36
            kf = font(SANS_B, 8)
            d.text((cx, ty), card["kicker"], font=kf, fill=RED)
            d.text((cx + tw(d, card["kicker"], kf) + 5, ty),
                   "· " + card["src"], font=kf, fill=GREY)
            hy = ty + 9
            head_lines = fit_lines(d, card["head"], font(SANS_B, 12.5), mw, 2)
            for li, line in enumerate(head_lines):
                d.text((cx, hy + li * 15), line, font=font(SANS_B, 12.5),
                       fill=INK)
            dy = hy + 15 * len(head_lines) + 1
            for li, line in enumerate(fit_lines(d, card["deck"],
                                                font(SANS, 9.5), mw, 2)):
                d.text((cx, dy + li * 12), line, font=font(SANS, 9.5),
                       fill=(40, 40, 40))
    y += 2 * mh + 6 + 8

    # ---- map (label chips drawn inside draw_map) ----
    map_h = 100
    draw_map(d, MX, y, CW, map_h)
    y += map_h + 4

    # ---- also on 20 november: 31 more stories ----
    d.text((MX, y), "ALSO ON 20 NOVEMBER — 31 MORE STORIES",
           font=font(SANS_B, 13), fill=INK)
    rule(d, MX, y + 18, CW, INK, 1)
    y += 22
    col_w = (CW - 24) / 2
    for side in range(2):
        items = LIST_ITEMS[side * 16:(side + 1) * 16]
        lx = MX + side * (col_w + 24)
        for ri, (num, city, story, src) in enumerate(items):
            ry = y + ri * 10
            f = font(SANS_B, 9.5)
            d.text((lx, ry), f"{num}", font=f, fill=RED)
            tx = lx + 20
            city_f = font(SANS_B, 9.5)
            d.text((tx, ry), city + ": ", font=city_f, fill=INK)
            sx = tx + tw(d, city + ": ", city_f)
            body, bf = one_line(d, story + " — " + src, font(SANS, 9.5),
                                col_w - (sx - lx), min_size=9)
            d.text((sx, ry), body, font=bf, fill=(40, 40, 40))
    y += 16 * 10 + 6

    # ---- date check box ----
    box_lines = wrap(d, DATE_CHECK, font(SANS, 9), CW - 24)
    bh = 22 + len(box_lines) * 11 + 6
    d.rectangle([MX, y, MX + CW - 1, y + bh - 1], outline=RED, width=2)
    d.rectangle([MX, y, MX + CW - 1, y + 17], fill=RED)
    d.text((MX + 8, y + 3), "DATE CHECK — LEFT OUT ON PURPOSE",
           font=font(SANS_B, 10), fill=(255, 255, 255))
    for li, line in enumerate(box_lines):
        d.text((MX + 12, y + 22 + li * 11), line, font=font(SANS, 9),
               fill=INK)
    y += bh + 4

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
    return img, y


def main():
    img, bottom = build()
    out = os.environ.get("MAKEFUN_OUTPUT_DIR")
    path = os.path.join(out, "entry.png") if out else "entry.png"
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    img.save(path, "PNG")
    print(f"bottom edge used: {bottom}px of {H}px")
    print(f"wrote {path}: {os.path.getsize(path)} bytes")


if __name__ == "__main__":
    main()
