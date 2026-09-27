"""Generate the profile banner and numbers card (light + dark SVGs) for github.com/adityagis.

    pip install pillow numpy scipy
    python scripts/generate.py

Edit INFO / NUMBERS below, run again, commit assets/.
"""
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
PHOTO = ROOT / "scripts" / "portrait.webp"
ASSETS = ROOT / "assets"

INFO = [
    ("Subject", "Aditya Kumar Jha"),
    ("Role", "GIS Engineer · Survey of India"),
    ("Branch", "Geodetic & Research Branch"),
    ("Location", "Dehradun · India"),
    ("Education", "B.Tech GeoInformatics · NSUT"),
    ("Status", "Processing GNSS + Building GeoAI"),
    ("Core.GNSS", "GAMIT/GLOBK · PRIDE PPP-AR · RINEX"),
    ("Core.GIS", "QGIS · ArcGIS Pro · Earth Engine"),
    ("Core.Python", "GDAL · GeoPandas · Rasterio · PyTorch"),
    ("Core.RS", "LiDAR · Hyperspectral · UAV"),
    ("Core.Data", "PostgreSQL · PostGIS · GeoServer"),
    ("Consulting", "Uday GeoAnalytics"),
    ("Grid.Web", "adityagis.github.io/Portfolio"),
    ("Grid.Mail", "adityajha976@gmail.com"),
    ("Grid.LinkedIn", "/in/adityaashujha"),
    ("Grid.GitHub", "adityagis"),
]

NUMBERS = [
    ("1023+", "GNSS CORS stations processed"),
    ("7 → 3", "days per station, after automation"),
    ("30 → 1", "days of levelling analysis"),
    ("3M+", "LiDAR points analysed at DRDO"),
    ("98.1%", "LULC model validation accuracy"),
    ("200+", "members, NSUT Geospatial Club"),
]

THEMES = {
    "light": dict(bg="#ffffff", frame="#e6e9ef", panel="#f3f6fa", border="#d5dce6", text="#0f1b3d", dim="#64708a",
                  accent="#1f7a8c", dot="#23347a", live="#e5484d", pill="#d7eef2", rule="#c9d2de"),
    "dark": dict(bg="#0d1117", frame="#30363d", panel="#111822", border="#243044", text="#dbe4f3", dim="#7d8aa3",
                 accent="#4fd1c5", dot="#9fb4ff", live="#ff6b6b", pill="#11303a", rule="#2a3547"),
}
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# Hand-traced silhouette around head and shoulders; keeps the busy background out of the portrait.
SIL = [(70, 70), (95, 22), (140, 12), (180, 30), (195, 80), (192, 150), (185, 200), (215, 212), (262, 228),
       (300, 250), (322, 290), (338, 370), (360, 420), (385, 500), (0, 500), (0, 290), (12, 250), (60, 222),
       (88, 205), (80, 160), (72, 120)]


def halftone(step=4, invert=False):
    """Return (cols, rows, [(i, j, tone)]) for a 1-bit style halftone of the portrait.

    Light theme draws dark dots for shadows; dark theme (invert=True) draws light dots for highlights,
    so the portrait reads as a positive on both backgrounds."""
    im = Image.open(PHOTO).convert("RGB")
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon(SIL, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(3))
    gw, gh = w // step, h // step
    g = np.asarray(im.convert("L").resize((gw, gh), Image.LANCZOS), dtype=float) / 255
    m = np.asarray(mask.resize((gw, gh), Image.LANCZOS), dtype=float) / 255
    lo, hi = np.percentile(g[m > 0.5], [3, 97])
    g = np.clip((g - lo) / (hi - lo), 0, 1)
    ed = np.hypot(ndimage.sobel(g, 0), ndimage.sobel(g, 1))
    ed = np.clip(ed / np.percentile(ed, 98), 0, 1)
    base = 0.8 * g ** 1.7 if invert else (1 - g) ** 1.25
    tone = np.clip(base + 0.3 * ed, 0, 1) * m
    tone = np.maximum(tone, 0.45 * np.clip(np.hypot(*np.gradient(m)) * 3, 0, 1))
    pts = [(i, j, float(tone[j, i])) for j in range(gh) for i in range(gw) if tone[j, i] >= 0.1]
    return gw, gh, pts


def banner(t, cols, rows, pts):
    W, H = 1200, 600
    L = dict(x=40, y=84, w=420, h=476)          # left panel
    R = dict(x=484, y=84, w=676, h=476)         # right panel
    o = []
    add = o.append
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-labelledby="t d">')
    add('<title id="t">Aditya Kumar Jha: GIS Engineer at Survey of India</title>')
    add('<desc id="d">Terminal-style profile card. Halftone portrait of Aditya Kumar Jha beside a list: GIS engineer, '
        'Survey of India Geodetic and Research Branch, Dehradun; GNSS processing with GAMIT/GLOBK and PRIDE PPP-AR; '
        'Python, QGIS, ArcGIS Pro, LiDAR, PostGIS.</desc>')
    add(f"""<style>
text{{font-family:{MONO};}}
.k{{fill:{t['dim']};font-size:12.5px}} .v{{fill:{t['text']};font-size:12.5px;font-weight:600}}
.h{{fill:{t['accent']};font-size:12px;font-weight:700;letter-spacing:.12em}}
.s{{fill:{t['dim']};font-size:10px;letter-spacing:.08em}}
.row{{opacity:0;animation:in .35s ease-out forwards}}
.pix{{animation:pulse 5s ease-in-out infinite}}
.live{{animation:blink 1.2s steps(2,start) infinite}}
.scan{{animation:scan 4.5s linear infinite}}
.cur{{animation:blink 1s steps(2,start) infinite}}
@keyframes in{{from{{opacity:0;transform:translateX(-6px)}}to{{opacity:1;transform:none}}}}
@keyframes blink{{to{{visibility:hidden}}}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.78}}}}
@keyframes scan{{from{{transform:translateY(0)}}to{{transform:translateY({L['h'] - 60}px)}}}}
@media (prefers-reduced-motion:reduce){{.row,.pix,.live,.scan,.cur{{animation:none;opacity:1}}}}
</style>""")
    # window
    add(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="{t["bg"]}" stroke="{t["frame"]}" stroke-width="2"/>')
    add(f'<line x1="1" y1="52" x2="{W-1}" y2="52" stroke="{t["frame"]}" stroke-width="1.5"/>')
    for k, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        add(f'<circle cx="{30 + k*22}" cy="27" r="6.5" fill="{c}"/>')
    add(f'<text x="{W/2}" y="31" text-anchor="middle" class="k">profile.sh --live</text>')

    # left panel: halftone portrait
    add(f'<rect x="{L["x"]}" y="{L["y"]}" width="{L["w"]}" height="{L["h"]}" rx="8" fill="{t["panel"]}" stroke="{t["border"]}"/>')
    add(f'<line x1="{L["x"]}" y1="{L["y"]+36}" x2="{L["x"]+L["w"]}" y2="{L["y"]+36}" stroke="{t["border"]}"/>')
    add(f'<text x="{L["x"]+16}" y="{L["y"]+23}" class="h">VISUAL.MAP</text>')
    add(f'<text x="{L["x"]+L["w"]-16}" y="{L["y"]+23}" text-anchor="end" class="s">{cols*4}×{rows*4} / 1-BIT</text>')
    area = dict(x=L["x"] + 30, y=L["y"] + 52, w=L["w"] - 60, h=L["h"] - 84)
    cell = min(area["w"] / (cols + 0.5), area["h"] / rows)
    ox = area["x"] + (area["w"] - cell * (cols + 0.5)) / 2
    oy = area["y"] + (area["h"] - cell * rows) / 2
    add(f'<g class="pix" fill="{t["dot"]}">')
    for i, j, v in pts:
        cx = ox + (i + 0.5 + (0.5 if j % 2 else 0)) * cell
        cy = oy + (j + 0.5) * cell
        add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{cell*0.56*v**0.5:.2f}"/>')
    add('</g>')
    add(f'<rect class="scan" x="{L["x"]+2}" y="{L["y"]+40}" width="{L["w"]-4}" height="18" fill="{t["accent"]}" opacity=".12"/>')
    for (cx, cy, dx, dy) in ((L["x"]+14, L["y"]+50, 1, 1), (L["x"]+L["w"]-14, L["y"]+50, -1, 1),
                             (L["x"]+14, L["y"]+L["h"]-30, 1, -1), (L["x"]+L["w"]-14, L["y"]+L["h"]-30, -1, -1)):
        add(f'<path d="M{cx} {cy+10*dy}V{cy}H{cx+10*dx}" fill="none" stroke="{t["dim"]}" stroke-width="1.2"/>')
    add(f'<text x="{L["x"]+16}" y="{L["y"]+L["h"]-12}" class="s">PTS {len(pts)} · FS/HALFTONE</text>')
    add(f'<text x="{L["x"]+L["w"]-16}" y="{L["y"]+L["h"]-12}" text-anchor="end" class="s">30.32°N 78.03°E</text>')

    # right panel: system info
    add(f'<rect x="{R["x"]}" y="{R["y"]}" width="{R["w"]}" height="{R["h"]}" rx="8" fill="{t["panel"]}" stroke="{t["border"]}"/>')
    add(f'<line x1="{R["x"]}" y1="{R["y"]+36}" x2="{R["x"]+R["w"]}" y2="{R["y"]+36}" stroke="{t["border"]}"/>')
    add(f'<text x="{R["x"]+16}" y="{R["y"]+23}" class="h">SYSTEM.INFO</text>')
    px = R["x"] + R["w"] - 16
    add(f'<rect x="{px-112}" y="{R["y"]+8}" width="112" height="21" rx="10.5" fill="{t["pill"]}"/>')
    add(f'<text x="{px-56}" y="{R["y"]+22.5}" text-anchor="middle" class="v" style="font-size:12px;fill:{t["accent"]}">@adityagis</text>')
    add(f'<circle class="live" cx="{px-160}" cy="{R["y"]+18.5}" r="4" fill="{t["live"]}"/>')
    add(f'<text x="{px-150}" y="{R["y"]+22.5}" class="s" style="fill:{t["live"]};font-weight:700">LIVE</text>')
    y0, lh = R["y"] + 64, 23
    kx, vx = R["x"] + 18, R["x"] + R["w"] - 18
    for n, (k, v) in enumerate(INFO):
        y = y0 + n * lh
        add(f'<g class="row" style="animation-delay:{0.15 + n*0.07:.2f}s">')
        add(f'<text x="{kx}" y="{y}" class="k">{escape(k)}</text>')
        add(f'<line x1="{kx + 8 + len(k)*7.6:.0f}" y1="{y-4}" x2="{vx - 8 - len(v)*7.6:.0f}" y2="{y-4}" '
            f'stroke="{t["rule"]}" stroke-dasharray="1 4"/>')
        add(f'<text x="{vx}" y="{y}" text-anchor="end" class="v">{escape(v)}</text>')
        add('</g>')
    fy = R["y"] + R["h"] - 14
    add(f'<line x1="{R["x"]+16}" y1="{fy-18}" x2="{R["x"]+R["w"]-16}" y2="{fy-18}" stroke="{t["border"]}"/>')
    add(f'<circle cx="{R["x"]+20}" cy="{fy-3.5}" r="3" fill="{t["accent"]}"/>')
    add(f'<text x="{R["x"]+30}" y="{fy}" class="s" style="fill:{t["accent"]}">ALL STATIONS NOMINAL · 1023 CORS ONLINE'
        f'<tspan class="cur">_</tspan></text>')
    add(f'<text x="{R["x"]+R["w"]-16}" y="{fy}" text-anchor="end" class="s">UTC+5:30 · SURVEY OF INDIA NODE</text>')
    add('</svg>')
    return "\n".join(o)


def numbers(t):
    W, cw, ch, gap = 880, 276, 96, 26
    H = 2 * ch + gap + 90
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-labelledby="t"><title id="t">Aditya Kumar Jha in numbers: '
         + escape("; ".join(f"{a} {b}" for a, b in NUMBERS)) + '</title>',
         f'<style>text{{font-family:{MONO}}} .c{{opacity:0;animation:in .4s ease-out forwards}}'
         '@keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}'
         '@media (prefers-reduced-motion:reduce){.c{animation:none;opacity:1}}</style>',
         f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="{t["bg"]}" stroke="{t["frame"]}" stroke-width="2"/>',
         f'<text x="28" y="40" fill="{t["accent"]}" font-size="12" font-weight="700" letter-spacing=".12em">IMPACT.LOG</text>',
         f'<text x="{W-28}" y="40" text-anchor="end" fill="{t["dim"]}" font-size="10" letter-spacing=".08em">SURVEY OF INDIA · DRDO · NSUT</text>']
    for n, (big, small) in enumerate(NUMBERS):
        cx = 28 + (n % 3) * (cw + 0)
        cy = 62 + (n // 3) * (ch + gap)
        o.append(f'<g class="c" style="animation-delay:{0.1 + n*0.1:.1f}s">'
                 f'<rect x="{cx}" y="{cy}" width="{cw-12}" height="{ch}" rx="8" fill="{t["panel"]}" stroke="{t["border"]}"/>'
                 f'<text x="{cx+18}" y="{cy+48}" fill="{t["text"]}" font-size="30" font-weight="700">{escape(big)}</text>'
                 f'<text x="{cx+18}" y="{cy+74}" fill="{t["dim"]}" font-size="12">{escape(small)}</text></g>')
    o.append('</svg>')
    return "\n".join(o)


def main():
    ASSETS.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        cols, rows, pts = halftone(invert=name == "dark")
        (ASSETS / f"banner-{name}.svg").write_text(banner(t, cols, rows, pts), encoding="utf-8")
        (ASSETS / f"numbers-{name}.svg").write_text(numbers(t), encoding="utf-8")
    print(f"banners + number cards -> {ASSETS}")


if __name__ == "__main__":
    main()
