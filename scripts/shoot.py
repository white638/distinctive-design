"""给设计评审截图：首屏 + 分段长图，桌面与移动端各一套。

用法：
    python shoot.py index.html --round 1
    python shoot.py http://localhost:5173 --round 2 --out .design/shots --frames 4

为什么不直接 full_page 一张：
- 滚动触发的入场动画（IntersectionObserver）和懒加载图片在不滚动时不会出现，
  整页截图里会是一片空白，评审会据此误判。所以先逐屏滚到底再截。
- 很长的整页图会被看图工具压缩到看不清细节，所以按视口高度切成若干段。
- 首屏最影响第一印象，单独截一张。

依赖：pip install playwright && python -m playwright install chromium
"""

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

VIEWPORTS = {
    "desktop": ({"width": 1440, "height": 900}, 1),
    "mobile": ({"width": 390, "height": 844}, 2),
}
MAX_TILES = 8


def to_url(target: str) -> str:
    if target.startswith(("http://", "https://", "file://")):
        return target
    return Path(target).resolve().as_uri()


def settle(page) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass
    page.evaluate("document.fonts && document.fonts.ready")
    page.wait_for_timeout(600)


def scroll_through(page, step: int) -> int:
    height = page.evaluate("document.documentElement.scrollHeight")
    y = 0
    while y < height:
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(250)
        y += step
        height = page.evaluate("document.documentElement.scrollHeight")
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(800)
    return height


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="本地 HTML 路径或 URL")
    parser.add_argument("--round", type=int, required=True)
    parser.add_argument("--out", default=".design/shots")
    parser.add_argument("--frames", type=int, default=0, help="首屏动效抽帧数")
    parser.add_argument("--interval", type=int, default=400, help="抽帧间隔 ms")
    parser.add_argument("--reduced-motion", action="store_true")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    url = to_url(args.target)
    written = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, (vp, scale) in VIEWPORTS.items():
            page = browser.new_page(viewport=vp, device_scale_factor=scale)
            if args.reduced_motion:
                page.emulate_media(reduced_motion="reduce")
            page.goto(url)
            settle(page)

            prefix = out / f"round{args.round}_{name}"
            if args.frames:
                for i in range(args.frames):
                    path = f"{prefix}_frame{i}.png"
                    page.screenshot(path=path)
                    written.append(path)
                    page.wait_for_timeout(args.interval)
                page.reload()
                settle(page)

            height = scroll_through(page, vp["height"])
            tiles = min(MAX_TILES, -(-height // vp["height"]))
            for i in range(tiles):
                top = i * vp["height"]
                clip = {"x": 0, "y": top, "width": vp["width"],
                        "height": min(vp["height"], height - top)}
                path = f"{prefix}_fold.png" if i == 0 else f"{prefix}_part{i + 1}.png"
                page.screenshot(path=path, full_page=True, clip=clip)
                written.append(path)
            if -(-height // vp["height"]) > MAX_TILES:
                print(f"注意：{name} 页面超过 {MAX_TILES} 屏，后半部分未截，必要时手动补截。")
            page.close()
        browser.close()

    for path in written:
        print(Path(path).resolve())


if __name__ == "__main__":
    main()
