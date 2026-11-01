"""检查留白和字号：哪些屏几乎是空的，字号用了多少种、小字有多少。

用法：
    python layout_check.py index.html
    python layout_check.py http://localhost:5173 --width 390 --height 844

输出供人判断，不代替判断：
1. 空屏：逐屏截图，统计最大一种颜色的占比。占比很高说明这一屏几乎只有背景，
   要确认这片留白是在引导视线、衬托主体，还是只是内容不够。
2. 字号：按实际渲染的可见文字统计字号种类和字数。种类太多说明层级没有体系；
   小于 12px 的文字太多，多半是可以删的辅助小字，或者可读性有问题。
3. 小字清单：列出小于 13px 的文字块，配合 SKILL.md 技巧 8 的小字审计逐条判断。

依赖：pip install playwright pillow && python -m playwright install chromium
"""

import argparse
import io

from PIL import Image
from playwright.sync_api import sync_playwright

from shoot import scroll_through, settle, to_url

EMPTY_SHARE = 0.85
MAX_SIZES = 8
SMALL = 12
LIST_BELOW = 13

TEXT_STATS = """
() => {
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const sizes = {};
  const small = [];
  let node;
  while ((node = walker.nextNode())) {
    const text = node.textContent.replace(/\\s+/g, ' ').trim();
    if (!text) continue;
    const el = node.parentElement;
    const style = getComputedStyle(el);
    if (style.visibility === 'hidden' || parseFloat(style.opacity) === 0) continue;
    const rect = el.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) continue;
    const size = Math.round(parseFloat(style.fontSize));
    sizes[size] = sizes[size] || { chars: 0, blocks: 0 };
    sizes[size].chars += text.length;
    sizes[size].blocks += 1;
    if (size < %d) small.push([size, text.slice(0, 40)]);
  }
  return { sizes, small };
}
""" % LIST_BELOW


def empty_share(png):
    img = Image.open(io.BytesIO(png)).convert("RGB").resize((160, 100))
    quant = img.quantize(colors=6, method=Image.Quantize.MEDIANCUT)
    counts = sorted(quant.getcolors(), reverse=True)
    return counts[0][0] / (img.width * img.height)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="本地 HTML 路径或 URL")
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=900)
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": args.width, "height": args.height})
        page.goto(to_url(args.target))
        settle(page)
        height = scroll_through(page, args.height)

        print(f"## 空屏（{args.width}×{args.height}，最大一种颜色占比 ≥ {EMPTY_SHARE:.0%} 的屏）")
        flagged = 0
        screens = -(-height // args.height)
        for i in range(screens):
            top = i * args.height
            clip = {"x": 0, "y": top, "width": args.width, "height": min(args.height, height - top)}
            share = empty_share(page.screenshot(full_page=True, clip=clip))
            mark = "  ← 几乎只有背景" if share >= EMPTY_SHARE else ""
            flagged += bool(mark)
            print(f"- 第 {i + 1} 屏（y={top}）：{share:.0%}{mark}")
        if flagged:
            print("- 逐屏判断：留白在引导视线或衬托主体就保留；只是内容不够、间距过大，就收紧或重新经营这一屏。")

        stats = page.evaluate(TEXT_STATS)
        browser.close()

    sizes = {int(k): v for k, v in stats["sizes"].items()}
    total = sum(v["chars"] for v in sizes.values()) or 1
    print(f"\n## 字号（共 {len(sizes)} 种）")
    for size in sorted(sizes, reverse=True):
        v = sizes[size]
        print(f"- {size}px：{v['blocks']} 块，{v['chars']} 字（{v['chars'] / total:.0%}）")
    small_chars = sum(v["chars"] for s, v in sizes.items() if s < SMALL)
    small_blocks = sum(v["blocks"] for s, v in sizes.items() if s < SMALL)
    if len(sizes) > MAX_SIZES:
        print(f"- 提示：字号超过 {MAX_SIZES} 种，层级没有成体系。合并相近的字号，建一个有明显跳跃的字号阶梯。")
    if small_blocks > 5 or small_chars / total > 0.05:
        print(f"- 提示：小于 {SMALL}px 的文字有 {small_blocks} 块、{small_chars} 字。多半是可删的辅助小字，留下的要放大到可读。")
    sizes_sorted = sorted(sizes)
    if len(sizes_sorted) >= 2:
        gaps = [(b / a, a, b) for a, b in zip(sizes_sorted, sizes_sorted[1:])]
        ratio, a, b = max(gaps)
        if ratio >= 3:
            print(f"- 提示：字号从 {a}px 直接跳到 {b}px，中间没有过渡层级，画面会只剩巨字和碎字。")

    print(f"\n## 小于 {LIST_BELOW}px 的文字块（配合小字审计逐条判断）")
    for size, text in stats["small"][:40]:
        print(f"- {size}px  {text}")
    if len(stats["small"]) > 40:
        print(f"- ……另有 {len(stats['small']) - 40} 块")
    if not stats["small"]:
        print("- 无")


if __name__ == "__main__":
    main()
