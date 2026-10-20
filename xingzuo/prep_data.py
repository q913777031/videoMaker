"""一次性数据预处理：从 d3-celestial 星表生成 xingzuo/data/zodiac.json（构建时只读这个 JSON）。

数据来源：d3-celestial（Olaf Frohn，BSD-3-Clause，https://github.com/ofrohn/d3-celestial）的
constellations.lines.json / stars.6.json / starnames.json；太阳所在星座用 skyfield 自带的 IAU 星座边界（Roman 1987）
加 Meeus 低精度太阳位置公式（精度约 0.01°）逐日计算，取 2026 年北京时间正午。

用法：python3 -m xingzuo.prep_data <d3-celestial data 目录>
"""

import datetime
import json
import math
import sys
from pathlib import Path

from skyfield.api import load, load_constellation_map, position_of_radec

OUT = Path(__file__).resolve().parent / "data" / "zodiac.json"
ZODIAC = ["Ari", "Tau", "Gem", "Cnc", "Leo", "Vir", "Lib", "Sco", "Sgr", "Cap", "Aqr", "Psc"]
ECLIPTIC = ZODIAC[:8] + ["Oph"] + ZODIAC[8:]
# 占星“太阳星座”的常见日期（不同来源前后差 1 天）
ASTRO = {"Ari": ((3, 21), (4, 19)), "Tau": ((4, 20), (5, 20)), "Gem": ((5, 21), (6, 21)), "Cnc": ((6, 22), (7, 22)),
         "Leo": ((7, 23), (8, 22)), "Vir": ((8, 23), (9, 22)), "Lib": ((9, 23), (10, 23)), "Sco": ((10, 24), (11, 22)),
         "Sgr": ((11, 23), (12, 21)), "Cap": ((12, 22), (1, 19)), "Aqr": ((1, 20), (2, 18)), "Psc": ((2, 19), (3, 20))}
YEAR = 2026
LON, LAT = 116.4, 40.0          # 北京


def sun_radec(jd: float) -> tuple[float, float]:
    """Meeus 低精度视太阳位置（当日春分点）：返回 (赤经小时, 赤纬度)。"""
    T = (jd - 2451545.0) / 36525
    L0 = (280.46646 + 36000.76983 * T + 0.0003032 * T * T) % 360
    M = math.radians(357.52911 + 35999.05029 * T - 0.0001537 * T * T)
    C = ((1.914602 - 0.004817 * T) * math.sin(M) + (0.019993 - 0.000101 * T) * math.sin(2 * M)
         + 0.000289 * math.sin(3 * M))
    om = math.radians(125.04 - 1934.136 * T)
    lam = math.radians(L0 + C - 0.00569 - 0.00478 * math.sin(om))
    eps = math.radians(23.439291 - 0.0130042 * T + 0.00256 * math.cos(om))
    ra = math.degrees(math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))) % 360
    return ra / 15, math.degrees(math.asin(math.sin(eps) * math.sin(lam)))


def sun_constellations():
    """2026 年每天北京时间正午太阳所在的 IAU 星座。"""
    ts = load.timescale()
    cmap = load_constellation_map()
    out = {}
    d = datetime.date(YEAR, 1, 1)
    while d.year == YEAR:
        t = ts.utc(d.year, d.month, d.day, 4)
        ra, dec = sun_radec(t.tt)
        out[d] = cmap(position_of_radec(ra, dec, epoch=t))
        d += datetime.timedelta(days=1)
    return out


def best_evening(ra_deg: float) -> str:
    """北京晚上 9 点该赤经上中天（位于正南、最高）的日期。"""
    ts = load.timescale()
    best, err = None, 1e9
    d = datetime.date(YEAR, 1, 1)
    while d.year == YEAR:
        t = ts.utc(d.year, d.month, d.day, 13)
        lst = (t.gmst * 15 + LON) % 360
        e = abs((lst - ra_deg + 180) % 360 - 180)
        if e < err:
            best, err = d, e
        d += datetime.timedelta(days=1)
    return f"{best.month:02d}-{best.day:02d}"


def main(src: Path):
    feats = json.load(open(src / "constellations.lines.json"))["features"]
    lines = {f["id"]: f["geometry"]["coordinates"] for f in feats}
    # 巨蛇座被蛇夫座隔成蛇头、蛇尾两块，星表里是两个同名要素（蛇夫座番外用）
    serpens = [f["geometry"]["coordinates"] for f in feats if f["id"] == "Ser"]
    stars = json.load(open(src / "stars.6.json"))["features"]
    names = json.load(open(src / "starnames.json"))
    mag = {f["id"]: f["properties"]["mag"] for f in stars}
    days = sun_constellations()

    # 太阳在各星座的连续区间
    spans, prev, start = [], None, None
    for d in sorted(days):
        if days[d] != prev:
            if prev:
                spans.append((prev, start, d - datetime.timedelta(days=1)))
            prev, start = days[d], d
    spans.append((prev, start, max(days)))
    # 跨年的人马座合并成一段
    if spans[0][0] == spans[-1][0]:
        spans = spans[1:-1] + [(spans[-1][0], spans[-1][1], spans[0][2])]
    sun = {c: (f"{a.month:02d}-{a.day:02d}", f"{b.month:02d}-{b.day:02d}", (b - a).days + 1 if b >= a
               else (b - a).days + 1 + 365) for c, a, b in spans}

    out = {"source": "d3-celestial (BSD-3-Clause); IAU boundaries via skyfield; Sun: Meeus low-precision, "
                     f"{YEAR} Beijing noon", "sun": sun, "order": ECLIPTIC, "signs": {},
           "serpens": serpens}
    for ab in ECLIPTIC:
        segs = lines[ab]
        pts = [p for s in segs for p in s]
        # 赤经可能跨 ±180°：以第一点为参照展开
        ra0 = pts[0][0]

        def unwrap(r):
            return ra0 + (r - ra0 + 180) % 360 - 180

        segs = [[[unwrap(r), d] for r, d in s] for s in segs]
        ras = [p[0] for s in segs for p in s]
        decs = [p[1] for s in segs for p in s]
        cra, cdec = (min(ras) + max(ras)) / 2, (min(decs) + max(decs)) / 2
        span_ra, span_dec = (max(ras) - min(ras)), (max(decs) - min(decs))
        bg = []
        for f in stars:
            m = f["properties"]["mag"]
            if m > 6.0:
                continue
            r, d = f["geometry"]["coordinates"]
            r = cra + (r - cra + 180) % 360 - 180
            if abs(d - cdec) <= span_dec / 2 + 12 and abs(r - cra) * math.cos(math.radians(cdec)) <= span_ra / 2 * \
                    math.cos(math.radians(cdec)) + 14:
                bg.append([round(r, 3), round(d, 3), m])
        vert = []
        for s in segs:
            for r, d in s:
                near = min(bg, key=lambda q: (q[0] - r) ** 2 + (q[1] - d) ** 2)
                vert.append(near[2] if abs(near[0] - r) + abs(near[1] - d) < 0.2 else 4.5)
        named = []
        for k, v in names.items():
            if v.get("c") == ab and k.isdigit() and int(k) in mag:
                f = next(x for x in stars if x["id"] == int(k))
                r, d = f["geometry"]["coordinates"]
                named.append(dict(hip=int(k), en=v["name"], zh=v.get("zh", ""), desig=v["desig"], mag=mag[int(k)],
                                  ra=round(cra + (r - cra + 180) % 360 - 180, 3), dec=round(d, 3)))
        named.sort(key=lambda q: q["mag"])
        sign = dict(lines=segs, center=[round(cra, 3), round(cdec, 3)], stars=bg, named=named[:10],
                    best_evening=best_evening(cra % 360), culmination_alt=round(90 - LAT + cdec, 1))
        if ab in ASTRO:
            (m0, d0), (m1, d1) = ASTRO[ab]
            a, b = datetime.date(YEAR, m0, d0), datetime.date(YEAR, m1, d1)
            rng = []
            d = a
            while d != b + datetime.timedelta(days=1):
                rng.append(days[d])
                d += datetime.timedelta(days=1)
                if d.year > YEAR:
                    d = datetime.date(YEAR, 1, 1)
            count = {}
            for c in rng:
                count[c] = count.get(c, 0) + 1
            sign["astro"] = [f"{m0:02d}-{d0:02d}", f"{m1:02d}-{d1:02d}"]
            sign["astro_actual"] = sorted(count.items(), key=lambda kv: -kv[1])
        out["signs"][ab] = sign
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(OUT, OUT.stat().st_size)
    for ab in ZODIAC:
        s = out["signs"][ab]
        print(ab, s["astro"], s["astro_actual"], sun[ab], s["best_evening"], s["culmination_alt"],
              [(n["zh"], n["en"], n["mag"]) for n in s["named"][:2]], len(s["stars"]))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
