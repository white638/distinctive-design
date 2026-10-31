# distinctive-design

一个让 AI 代理做出"不像 AI 做的"视觉设计的 Agent Skill，适用于落地页、官网、App 界面、海报等。

流程分三段：
- **Discover**：用外部随机种子在设计轴上抽签，避免落回平均值。
- **Define**：独立评审子代理只看截图，循环打分；用生成图像和视频丰富视觉。
- **Deliver**：大胆删减，对照两层 AI 痕迹清单检查，并手工重写文案。

附带中文字体与中文排版的检查清单。

## 文件

| 路径 | 作用 |
|---|---|
| `SKILL.md` | 主流程 |
| `scripts/seed_axes.py` | 生成种子并在七条设计轴上抽签 |
| `scripts/shoot.py` | 给评审截图：先滚动触发懒加载与入场动画，再截首屏与分段长图（桌面 + 移动） |
| `references/critic-prompt.md` | 评审 prompt 原文（打分式 / 排名式）与评审记录格式 |
| `references/cjk-typography.md` | 中文字体授权与子集化、排版细节、中文 AI 腔 |

## 安装

Claude Code：

```bash
git clone https://github.com/white638/distinctive-design ~/.claude/skills/distinctive-design
```

截图脚本依赖 Playwright：

```bash
pip install playwright && python -m playwright install chromium
```
