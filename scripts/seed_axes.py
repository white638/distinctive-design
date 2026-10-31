"""生成外部随机种子，并按种子确定性地在几条设计轴上抽签。

用法：
    python seed_axes.py            # 一个方向
    python seed_axes.py -n 3       # 三个备选方向，各用一个新种子
    python seed_axes.py --seed XYZ # 复现某个种子的抽签结果

抽签结果是提示而不是命令：它负责把你推离"最可能"的选项，
最后怎么组合、怎么做好看仍由你判断。若某一签明显伤害产品，
可以重抽这一轴，但要在创意方向说明里写明原因。
"""

import argparse
import hashlib
import secrets
import string

AXES = {
    "灵感来源": [
        "1970 年代瑞士铁路时刻表", "昭和时期家电说明书", "博物馆标本标签", "航海图与等深线",
        "赛车计时屏", "老式计算器的 LCD 段码", "中药铺百子柜的抽屉标签", "地铁线路图",
        "气象雷达回波图", "植物图鉴铜版画", "爵士唱片封套", "建筑施工蓝图",
        "外科器械目录", "邮票与邮戳", "电影片尾字幕", "报纸号外",
        "地质剖面图", "示波器屏幕", "纺织品色卡", "CRT 游戏机菜单",
        "机场翻牌航显", "药品说明书折页", "影印拼贴 zine", "野兽派混凝土建筑",
        "包豪斯基础课作业", "宋刻本古籍版式", "碑帖拓片", "粮票与旧票证",
        "搪瓷杯与搪瓷招牌", "霓虹灯招牌手稿", "天文星图", "乐高说明书",
        "手术室监护仪", "老式图书馆借书卡", "实验室玻璃器皿刻度", "工地安全标识",
        "电路板丝印", "日式便当盒分格", "游园会地图", "黑胶唱机的旋钮面板",
    ],
    "版式原型": [
        "单列长卷，像一篇杂志特稿", "非对称编辑式网格", "全屏单图逐屏推进", "目录 / 索引式",
        "表格与数据即界面", "海报式单页巨字", "横向滚动长廊", "物件散落在桌面上",
        "分屏对照", "时间轴", "地图坐标定位", "终端 / 控制台窗口",
        "书页对开", "仪表盘面板", "层叠纸片", "竖排直书",
    ],
    "配色策略": [
        "单色 + 一处强调色", "双色专色印刷感", "高饱和撞色", "近黑近白、几乎无色",
        "从灵感来源里的实物取色", "低饱和泥土色", "荧光色 + 中性灰", "夜间琥珀色调",
        "褪色的老照片色", "工业警示色（黄黑 / 橙灰）",
    ],
    "明暗": ["亮底", "暗底", "中间调（灰、土、雾色作底）", "亮暗分区交替"],
    "字体气质": [
        "古典衬线 / 宋体", "怪诞无衬线（grotesk）", "几何无衬线", "等宽字体",
        "手写 / 楷体", "超宽展示字体", "极窄长体", "黑体与宋体的强对比",
        "刻本 / 仿宋的书卷气", "像素 / 点阵字体",
    ],
    "形状语言": [
        "直角硬边", "大圆角软胶", "有机曲线", "切角",
        "刻度、虚线与标注线", "打孔、撕边与装订线", "圆点网格", "粗描边贴纸",
    ],
    "动效性格": [
        "机械般精确", "弹性回弹", "几乎静止", "逐帧跳跃（steps）",
        "墨水扩散", "打字机逐字", "翻牌 / 卷帘", "物理惯性与拖拽",
    ],
    "信息密度": ["稀疏，留白主导", "中等", "高密度，信息即装饰"],
}


def new_seed(length: int = 64) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def draw(seed: str) -> dict:
    picks = {}
    for axis, options in AXES.items():
        digest = hashlib.sha256(f"{seed}:{axis}".encode()).digest()
        picks[axis] = options[int.from_bytes(digest[:8], "big") % len(options)]
    return picks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=1, help="备选方向数")
    parser.add_argument("--seed", help="复现指定种子")
    args = parser.parse_args()

    seeds = [args.seed] if args.seed else [new_seed() for _ in range(args.n)]
    for i, seed in enumerate(seeds, 1):
        print(f"## 方向 {i}")
        print(f"种子：{seed}")
        for axis, pick in draw(seed).items():
            print(f"- {axis}：{pick}")
        print()


if __name__ == "__main__":
    main()
