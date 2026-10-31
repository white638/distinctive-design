# 图像与视频生成

技巧 4、5 的操作细节。画面描述一律从 `.design/direction.md` 推导，保证生成的素材和整体设计语言一致。

## 图像：首选 Codex 内置图像生成（走 ChatGPT 订阅，不需要 API key）

Codex 自带 `$imagegen` skill 和内置 `image_gen` 工具，用用户的 ChatGPT 登录（Plus / Pro / Business / Edu / Enterprise），额度计入 ChatGPT 套餐，不产生 API 费用。

### 宿主是 Codex

直接调用内置图像生成，跳过下面的预检和命令行调用；"共同要求"一节照样适用。生成的图保存到项目的 `assets/` 里。

### 宿主是 Claude Code：通过命令行调用 Codex

**预检**

```bash
codex --version || npm i -g @openai/codex   # 未安装则安装（安装前告知用户）
codex login status                          # 应显示以 ChatGPT 登录
```

- 装了 Codex 桌面版不等于命令行里有 `codex`，以 `codex --version` 的结果为准。
- 未登录：请用户运行 `codex login`；无浏览器的环境用 `codex login --device-auth`，把设备码交给用户在浏览器里完成授权。
- **确保走订阅而不是 API key**：登录方式必须是 ChatGPT；调用时清掉 `OPENAI_API_KEY` 环境变量（见下方）。

**调用**

```bash
mkdir -p assets
env -u OPENAI_API_KEY codex exec --ephemeral -s workspace-write --skip-git-repo-check -C "$PWD" \
  '$imagegen 生成一张图：{主体}，{构图与视角}，{光线}，{材质/质感}，配色 {色值，来自创意方向说明}，风格 {…}，宽高比 16:9，画面中不要任何文字。完成后保存为 ./assets/hero.png'
```

PowerShell 里没有 `env -u`，改为先执行 `Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue`，再调用 `codex exec`；`$imagegen` 要放在单引号里，否则会被当成变量展开。

- prompt 里**不要**写"用 OpenAI API / curl / python 脚本生成"——那会让 Codex 绕开内置工具改走 API 计费。直接用 `$imagegen` + 画面描述即可。
- 默认输出目录是 `~/.codex/generated_images/`（Windows 为 `%USERPROFILE%\.codex\generated_images\`）；如果 Codex 没按要求存到项目里，就从那里取最新文件复制过来。
- 以参考图为基础生成或编辑：`codex exec --image ref.png '$imagegen 基于这张图……'`。

**运行位置**：当前环境装不上 Codex 或连不上 OpenAI（云端容器的网络可能有白名单限制）时，如果会话已关联用户的电脑且那里装了 Codex，就在用户电脑上运行，再把生成的图片传回工作区；否则如实告诉用户，并走下面的备选方案。

### 共同要求

- 同一页面的多张图一次批量生成，并写明统一的风格约束。
- 画面里要出现文字（招牌、包装）时，生成"无文字"版本，文字用真实 HTML 叠上去。生成图里的中文字形几乎总是错的。
- 需要透明背景：先在纯色背景上生成，再抠图（如 `pip install rembg`）；只有用户同意时才改用需要 API key 的方式。
- 每张图生成后都亲自打开查看（Claude Code 用 Read，Codex 用图片查看工具）；不满意就改 prompt 重生成，不要将就。
- 结合着色器（WebGL/GLSL）、3D、视差、遮罩使用这些图像，做出更有意思的视觉；完成后逐帧在浏览器里核对效果。

### 备选

- 当前代理本身有其他内置图像生成（如在 Antigravity、Grok Build 里运行）→ 直接用，并明确指示它去用。
- 用户提供 OpenAI / Gemini API key → 只在本地开发时使用，**绝不写进代码、产品或提交的文件**。建议用户为代理单独创建一个限额很低、可随时吊销的 key；经常需要时存进被 gitignore 的 `.env.agents`，并在 CLAUDE.md / AGENTS.md 里注明"仅供开发期使用，不得随产品发布"。
- 都不可用 → 精心手绘的 SVG 插画、由种子驱动的 canvas / 着色器生成艺术、真实感纹理（噪点、纸张、颗粒）；但不要退回到偷懒的渐变光斑。

## 视频：高级动效

用一个聚合平台（如 fal.ai）的 key，让代理自己挑选当前最合适的视频 / 抠像模型。key 的处理规则同图像的"备选"。起始帧和各状态的关键帧用上面的图像生成来做。

**A. 可叠加的动画图形**

- 生成纯色背景（绿幕）上的循环片段，再用色键去背；复杂情况（玻璃、烟雾、毛发）用视频抠像（matting）模型。
- 玻璃 / 折射类效果：先把物体渲染在**页面的真实背景色**上（把折射烘焙进去），再抠掉背景。
- 色键示例：
  ```bash
  ffmpeg -i in.mp4 -vf "chromakey=0x00FF00:0.12:0.06" -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 out.webm
  ```
- Safari 对 VP9 透明 WebM 的支持不可靠，要给 Safari 准备退路：带 alpha 的 HEVC 版本、canvas 图像序列，或一张静态图。在 Safari（或 WebKit）里实际看一遍。

**B. 状态之间的流畅过渡**

- 很多视频模型支持在两张关键帧之间插值：生成各个状态的静帧，再生成从一帧到下一帧的过渡片段；用上一段的最后一帧作为下一段的起始帧，保证无缝衔接。
- 用户操作时播放，或随滚动 / 手势逐帧拖动（scrub）。逐帧拖动要流畅，可导出为图像序列画到 canvas 上，或用全关键帧编码（`-g 1`）。
- 选物理效果和一致性强的模型。

**C. 嵌入**

- 自动播放的视频必须 `muted playsinline`，否则移动端不会播。
- 设 `poster` 首帧，视频加载前不留空洞。
- `prefers-reduced-motion: reduce` 时停在 poster 或改为静态图。
