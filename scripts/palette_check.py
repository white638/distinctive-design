"""检查截图的配色层次，以及界面色块是否融入环境。

用法：
    python palette_check.py shot.png
    python palette_check.py shot.png --source assets/hero.jpg   # 主视觉图作为色彩来源

输出三项，供人判断，不代替判断：
1. 主色板：截图量化后的主要颜色、面积占比、明度（L*）。
2. 单调度：大面积颜色之间的明度跨度和色差。几乎只有一种明度、一种色相的背景会显得平。
3. 外来色块：面积不小、却离页面边缘背景色很远的颜色；给了 --source 时，另报页面与主视觉图的色彩关系。
   典型例子是深色照片背景上一块纯白卡片。强调色本来就该跳出来，列出来后自己判断是不是有意的。

依赖：Pillow（pip install pillow）。
"""

import argparse
import colorsys

from PIL import Image

SAMPLE_WIDTH = 240


def srgb_to_lab(rgb):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(float(c)) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a, b):
    return sum((p - q) ** 2 for p, q in zip(a, b)) ** 0.5


def edge_strip(path, ratio=0.06):
    """把截图四周的边缘拼成一张图：页面边缘通常就是背景。"""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    bw, bh = max(1, int(w * ratio)), max(1, int(h * ratio))
    parts = [img.crop((0, 0, w, bh)), img.crop((0, h - bh, w, h)),
             img.crop((0, 0, bw, h)).rotate(90, expand=True),
             img.crop((w - bw, 0, w, h)).rotate(90, expand=True)]
    strip = Image.new("RGB", (max(p.width for p in parts), sum(p.height for p in parts)))
    y = 0
    for p in parts:
        strip.paste(p, (0, y))
        y += p.height
    return strip


def palette(path, colors):
    img = path if isinstance(path, Image.Image) else Image.open(path).convert("RGB")
    scale = SAMPLE_WIDTH / img.width
    if scale < 1:
        img = img.resize((SAMPLE_WIDTH, max(1, round(img.height * scale))))
    quant = img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    raw = quant.getpalette()[: colors * 3]
    total = img.width * img.height
    result = []
    for count, idx in sorted(quant.getcolors(), reverse=True):
        rgb = tuple(raw[idx * 3: idx * 3 + 3])
        result.append({"rgb": rgb, "share": count / total, "lab": srgb_to_lab(rgb)})
    return result


def hex_of(rgb):
    return "#%02x%02x%02x" % rgb


def describe(entry):
    r, g, b = (c / 255 for c in entry["rgb"])
    h, _, s = colorsys.rgb_to_hls(r, g, b)
    return f"{hex_of(entry['rgb'])}  {entry['share']:5.1%}  L*={entry['lab'][0]:5.1f}  色相={h * 360:5.0f}°  饱和={s:.2f}"


def chroma(entry):
    _, a, b = entry["lab"]
    return (a * a + b * b) ** 0.5


def hue_deg(entry):
    r, g, b = (c / 255 for c in entry["rgb"])
    return colorsys.rgb_to_hls(r, g, b)[0] * 360


def nearest(entry, pool):
    return min(delta_e(entry["lab"], e["lab"]) for e in pool)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("shot", help="页面截图")
    parser.add_argument("--source", help="主视觉图或品牌图，作为环境色来源")
    parser.add_argument("--colors", type=int, default=16)
    parser.add_argument("--outlier", type=float, default=30.0, help="外来色块的色差阈值（ΔE）")
    args = parser.parse_args()

    page = palette(args.shot, args.colors)
    print("## 主色板")
    for entry in page:
        if entry["share"] >= 0.005:
            print("- " + describe(entry))

    big = [e for e in page if e["share"] >= 0.03]
    lightness = [e["lab"][0] for e in big]
    spread = max(lightness) - min(lightness) if lightness else 0
    bins = {}
    chromatic = 0.0
    for e in page:
        if chroma(e) >= 8:
            chromatic += e["share"]
            key = int(hue_deg(e) // 30)
            bins[key] = bins.get(key, 0) + e["share"]
    hue_families = [k for k, v in bins.items() if v >= 0.05]
    print("\n## 单调度")
    print(f"- 明度跨度（面积 ≥3% 的颜色）：{spread:.1f}")
    print(f"- 有彩色占画面 {chromatic:.0%}，其中面积 ≥5% 的色相族（每 30° 一族）{len(hue_families)} 个")
    if len(hue_families) <= 1 and chromatic >= 0.3:
        print("- 提示：画面几乎只有一个色相，即使明暗有变化也容易显得单调。考虑从主视觉图或灵感物件里取第二个色相，"
              "做冷暖对比或局部光源，而不是只调同一色相的深浅。")
    if spread < 20:
        print("- 提示：大面积颜色明度接近，画面缺少明暗层次。考虑加入远近、光源、阴影。")

    bg = palette(edge_strip(args.shot), 8)
    flat = bg[0]["share"] if bg else 0
    print(f"- 页面边缘（通常是背景）最大的一种颜色占 {flat:.0%}")
    if flat >= 0.8:
        print("- 提示：背景接近平涂。从主视觉吸一个颜色铺满全页，不等于和主视觉属于同一个环境。"
              "把主视觉的世界延伸出来：它的天色渐变、纸张或胶片的颗粒、画里的光，以及第二个色相。")

    if args.source:
        env = palette(args.source, 8)
        related = sum(e["share"] for e in page if nearest(e, env) <= args.outlier)
        print("\n## 与主视觉的色彩关系")
        print(f"- 页面中 {related:.0%} 的面积落在主视觉图色板附近（ΔE ≤ {args.outlier:.0f}）")
        if related < 0.3:
            print("- 提示：页面的色彩世界和主视觉图基本无关，主视觉像是贴上去的。考虑从主视觉图取底色、"
                  "光色或强调色，让背景和它属于同一个环境。")

    print(f"\n## 外来色块（面积 0.5%–15%，离页面边缘的背景色 ΔE > {args.outlier:.0f}）")
    found = False
    for entry in page:
        if not 0.005 <= entry["share"] <= 0.15:
            continue
        gap = nearest(entry, bg)
        if gap > args.outlier:
            found = True
            print(f"- {describe(entry)}  离背景最近色差 {gap:.1f}")
    if not found:
        print("- 无")
    else:
        print("- 逐个判断：大片文字和图片也会出现在这里，跳过它们。是有意的强调色，就让它只出现在一处；"
              "是卡片、按钮底色等表面，就改为从环境色里取色、降低与背景的明度差，或干脆去掉这个表面。")


if __name__ == "__main__":
    main()
