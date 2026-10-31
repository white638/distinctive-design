# distinctive-design

一个让 AI 代理做出"不像 AI 做的"视觉设计的 Agent Skill，适用于落地页、官网、App 界面、海报等。Claude Code 和 Codex 通用。

流程分三段：
- **Discover**：用外部随机种子在八条设计轴上抽签，避免落回平均值。
- **Define**：独立评审子代理只看截图，循环打分；用生成图像和视频丰富视觉。
- **Deliver**：大胆删减，按三层 AI 痕迹清单数命中，并手工重写文案。

附带中文字体与中文排版的检查清单。

## 文件

| 路径 | 作用 |
|---|---|
| `SKILL.md` | 主流程 |
| `scripts/seed_axes.py` | 生成种子并在八条设计轴上抽签 |
| `scripts/shoot.py` | 给评审截图：先滚动触发懒加载与入场动画，再截首屏与分段长图（桌面 + 移动） |
| `references/critic-prompt.md` | 评审 prompt 原文（打分式 / 排名式）、两个宿主的调用方式、评审记录格式 |
| `references/ai-tells.md` | 三层 AI 痕迹清单（老套路 / 新套路 / 组合套路）与计数规则，注明日期 |
| `references/media-generation.md` | 图像与视频生成的预检、命令和备选 |
| `references/cjk-typography.md` | 中文字体授权与子集化、排版细节、浏览器支持、中文 AI 腔 |
| `assets/critic-schema.json` | Codex 备选评审（`codex exec --output-schema`）的输出格式 |
| `codex/design_critic.toml` | Codex 的评审子代理定义 |
| `agents/openai.yaml` | Codex 界面元数据，Claude Code 会忽略它 |

## 安装

Claude Code：

```bash
git clone https://github.com/white638/distinctive-design ~/.claude/skills/distinctive-design
```

Codex（官方文档的用户级技能目录是 `~/.agents/skills`）：

```bash
git clone https://github.com/white638/distinctive-design ~/.agents/skills/distinctive-design
```

再把评审子代理装进 Codex。这个文件只是一层约束外壳，评审内容来自 skill 里的 prompt，skill 更新时一般不用重装：

```bash
cp ~/.agents/skills/distinctive-design/codex/design_critic.toml ~/.codex/agents/
```

两边都用时只 clone 一份，另一边建目录链接指过去，例如 Windows PowerShell：

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.agents\skills\distinctive-design" -Target "$env:USERPROFILE\.claude\skills\distinctive-design"
```

同一个 skill 不要同时放在 Codex 的多个技能目录里，Codex 不会合并同名 skill，会出现两份。

截图脚本依赖 Playwright：

```bash
pip install playwright && python -m playwright install chromium
```

运行时会在项目根目录生成 `.design/`（方向说明、评审 prompt、评审记录、截图、快照），不想提交可加进 `.gitignore`。
