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
| `agents/openai.yaml` | Codex 界面元数据 |

## 安装

同一份文件同时支持 Claude Code 和 Codex，宿主差异写在 `SKILL.md` 的"宿主适配"一节；`agents/openai.yaml` 是 Codex 的界面元数据，Claude Code 会忽略它。

Claude Code：

```bash
git clone https://github.com/white638/distinctive-design ~/.claude/skills/distinctive-design
```

Codex：

```bash
git clone https://github.com/white638/distinctive-design ~/.codex/skills/distinctive-design
```

两边都用时只 clone 一份，另一边建目录链接指过去，例如 Windows PowerShell：

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.codex\skills\distinctive-design" -Target "$env:USERPROFILE\.claude\skills\distinctive-design"
```

运行时会在项目根目录生成 `.design/`（方向说明、评审记录、截图、快照），不想提交可加进 `.gitignore`。

截图脚本依赖 Playwright：

```bash
pip install playwright && python -m playwright install chromium
```
