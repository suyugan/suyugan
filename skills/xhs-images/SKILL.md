---
name: xhs-images
description: 小红书信息图系列生成器，支持 10 种视觉风格和 8 种布局。将内容拆解为 1-10 张卡通风格图片，专为小红书优化。当用户提到"小红书图片"、"XHS images"、"RedNote infographics"、"小红书种草"或需要中文社交媒体信息图时使用。
---

# 小红书信息图系列生成器

将复杂内容拆解为适合小红书的吸睛信息图系列，支持多种风格选项。

## 使用方法

```bash
# 根据内容自动选择风格和布局
/xhs-images posts/ai-future/article.md

# 指定风格
/xhs-images posts/ai-future/article.md --style notion

# 指定布局
/xhs-images posts/ai-future/article.md --layout dense

# 同时指定风格和布局
/xhs-images posts/ai-future/article.md --style notion --layout list

# 直接输入内容
/xhs-images
[粘贴内容]

# 带选项的直接输入
/xhs-images --style bold --layout comparison
[粘贴内容]
```

## 选项

| 选项 | 说明 |
|--------|-------------|
| `--style <名称>` | 视觉风格（见风格画廊） |
| `--layout <名称>` | 信息布局（见布局画廊） |

## 两个维度

| 维度 | 控制内容 | 选项 |
|-----------|----------|---------|
| **风格** | 视觉美学：配色、线条、装饰 | cute, fresh, warm, bold, minimal, retro, pop, notion, chalkboard, study-notes |
| **布局** | 信息结构：密度、排列 | sparse, balanced, dense, list, comparison, flow, mindmap, quadrant |

风格 × 布局可自由组合。例如：`--style notion --layout dense` 创建知性风格的高密度知识卡片。

## 风格画廊

| 风格 | 说明 |
|-------|-------------|
| `cute`（默认） | 甜美、可爱、少女感 - 经典小红书风格 |
| `fresh` | 清新、自然、干净 |
| `warm` | 温馨、友好、亲切 |
| `bold` | 高冲击力、吸睛醒目 |
| `minimal` | 极简、高级感 |
| `retro` | 复古、怀旧、潮流 |
| `pop` | 活力四射、充满能量 |
| `notion` | 极简手绘线条、知性风格 |
| `chalkboard` | 黑板彩色粉笔风格、教育感 |
| `study-notes` | 真实手写笔记照片风格，蓝笔 + 红色批注 + 黄色荧光笔 |

详细风格定义：`references/presets/<风格>.md`

## 布局画廊

| 布局 | 说明 |
|--------|-------------|
| `sparse`（默认） | 极简信息、最大冲击力（1-2个要点） |
| `balanced` | 标准内容布局（3-4个要点） |
| `dense` | 高信息密度、知识卡片风格（5-8个要点） |
| `list` | 列举和排名格式（4-7个项目） |
| `comparison` | 左右对比布局 |
| `flow` | 流程和时间线布局（3-6个步骤） |
| `mindmap` | 中心辐射式思维导图布局（4-8个分支） |
| `quadrant` | 四象限 / 圆形分区布局 |

详细布局定义：`references/elements/canvas.md`

## 自动选择

| 内容信号 | 风格 | 布局 |
|-----------------|-------|--------|
| 美妆、时尚、可爱、少女、粉色 | `cute` | sparse/balanced |
| 健康、自然、干净、清新、有机 | `fresh` | balanced/flow |
| 生活、故事、情感、感受、温暖 | `warm` | balanced |
| 警告、重要、必须、关键 | `bold` | list/comparison |
| 专业、商务、优雅、简约 | `minimal` | sparse/balanced |
| 经典、复古、老、传统 | `retro` | balanced |
| 有趣、刺激、哇、惊艳 | `pop` | sparse/list |
| 知识、概念、效率工具、SaaS | `notion` | dense/list |
| 教育、教程、学习、教学、课堂 | `chalkboard` | balanced/dense |
| 笔记、手写、学习指南、知识、真实感、照片 | `study-notes` | dense/list/mindmap |

## 大纲策略

针对不同内容目标的三种差异化大纲策略：

### 策略 A：故事驱动型

| 方面 | 说明 |
|--------|-------------|
| **理念** | 以个人经历为主线，情感共鸣优先 |
| **特点** | 从痛点出发，展示前后变化，真实感强 |
| **适用** | 测评、个人分享、蜕变故事 |
| **结构** | 钩子 → 问题 → 发现 → 体验 → 总结 |

### 策略 B：信息密集型

| 方面 | 说明 |
|--------|-------------|
| **理念** | 价值优先，高效信息传递 |
| **特点** | 结构清晰、要点明确、专业可信 |
| **适用** | 教程、对比、产品测评、清单 |
| **结构** | 核心结论 → 信息卡片 → 优缺点 → 推荐 |

### 策略 C：视觉优先型

| 方面 | 说明 |
|--------|-------------|
| **理念** | 视觉冲击为核心，文字极简 |
| **特点** | 大图、氛围感、即时吸引力 |
| **适用** | 高颜值产品、生活方式、氛围类内容 |
| **结构** | 主图 → 细节 → 生活场景 → 行动号召 |

## 文件结构

每次会话创建以内容标识命名的独立目录：

```
xhs-images/{topic-slug}/
├── source-{slug}.{ext}             # 源文件（文本、图片等）
├── analysis.md                     # 深度分析 + 提问记录
├── outline-strategy-a.md           # 策略 A：故事驱动型
├── outline-strategy-b.md           # 策略 B：信息密集型
├── outline-strategy-c.md           # 策略 C：视觉优先型
├── outline.md                      # 最终选择/合并的大纲
├── prompts/
│   ├── 01-cover-[slug].md
│   ├── 02-content-[slug].md
│   └── ...
├── 01-cover-[slug].png
├── 02-content-[slug].png
└── NN-ending-[slug].png
```

**标识生成规则**：
1. 从内容中提取主题（2-4个词，kebab-case）
2. 例如："AI工具推荐" → `ai-tools-recommend`

**冲突处理**：
如果 `xhs-images/{topic-slug}/` 已存在：
- 追加时间戳：`{topic-slug}-YYYYMMDD-HHMMSS`
- 例如：`ai-tools` 存在 → `ai-tools-20260118-143052`

**源文件**：
复制所有源文件，命名为 `source-{slug}.{ext}`：
- `source-article.md`、`source-photo.jpg` 等
- 支持多个源文件：文本、图片、对话中的文件

## 工作流程

### 进度清单

复制并追踪进度：

```
小红书信息图进度：
- [ ] 步骤 0：检查偏好设置（EXTEND.md）⚠️ 未找到时必须设置
- [ ] 步骤 1：分析内容 → analysis.md
- [ ] 步骤 2：确认 1 - 内容理解 ⚠️ 必须确认
- [ ] 步骤 3：生成 3 套大纲 + 风格方案
- [ ] 步骤 4：确认 2 - 大纲 & 风格 & 元素选择 ⚠️ 必须确认
- [ ] 步骤 5：生成图片（逐张）
- [ ] 步骤 6：完成报告
```

### 流程

```
输入 → 分析 → [确认 1] → 3套大纲 → [确认 2: 大纲 + 风格 + 元素] → 生成 → 完成
```

### 步骤 0：加载偏好设置（EXTEND.md）⚠️

**目的**：加载用户偏好或运行首次设置。**未找到 EXTEND.md 时不可跳过设置。**

使用 Bash 检查 EXTEND.md 是否存在（优先级顺序）：

```bash
# 先检查项目级
test -f .baoyu-skills/xhs-images/EXTEND.md && echo "project"

# 再检查用户级（跨平台：$HOME 在 macOS/Linux/WSL 通用）
test -f "$HOME/.baoyu-skills/xhs-images/EXTEND.md" && echo "user"
```

┌────────────────────────────────────────────────────┬───────────────────┐
│                        路径                         │     位置          │
├────────────────────────────────────────────────────┼───────────────────┤
│ .baoyu-skills/xhs-images/EXTEND.md           │ 项目目录          │
├────────────────────────────────────────────────────┼───────────────────┤
│ $HOME/.baoyu-skills/xhs-images/EXTEND.md     │ 用户主目录        │
└────────────────────────────────────────────────────┴───────────────────┘

┌───────────┬───────────────────────────────────────────────────────────────────────────┐
│  结果     │                                  操作                                      │
├───────────┼───────────────────────────────────────────────────────────────────────────┤
│ 找到      │ 读取、解析、显示摘要 → 继续步骤 1                                          │
├───────────┼───────────────────────────────────────────────────────────────────────────┤
│ 未找到    │ ⚠️ 必须运行首次设置（见下方）→ 然后继续步骤 1                              │
└───────────┴───────────────────────────────────────────────────────────────────────────┘

**首次设置**（当未找到 EXTEND.md 时）：

**语言**：使用用户的输入语言或已保存的语言偏好。

使用 AskUserQuestion 在一次调用中询问所有问题。详见 `references/config/first-time-setup.md`。

**EXTEND.md 支持**：水印 | 偏好风格/布局 | 自定义风格定义 | 语言偏好

架构：`references/config/preferences-schema.md`

### 步骤 1：分析内容 → `analysis.md`

读取源内容，必要时保存，并进行深度分析。

**操作**：
1. **保存源内容**（如果还不是文件）：
   - 如果用户提供文件路径：直接使用
   - 如果用户粘贴内容：保存到目标目录的 `source.md`
   - **备份规则**：如果 `source.md` 存在，重命名为 `source-backup-YYYYMMDD-HHMMSS.md`
2. 读取源内容
3. **深度分析** 遵循 `references/workflows/analysis-framework.md`：
   - 内容类型分类（种草/干货/测评/教程/避坑...）
   - 钩子分析（爆款标题潜力）
   - 目标用户识别
   - 互动潜力（收藏/分享/评论）
   - 视觉机会规划
   - 滑动流设计
4. 检测源语言
5. 确定建议图片数量（2-10）
6. **生成澄清问题**（见步骤 2）
7. **保存到 `analysis.md`**

### 步骤 2：确认 1 - 内容理解 ⚠️

**目的**：验证理解 + 收集缺失信息。**不可跳过。**

**显示摘要**：
- 识别的内容类型 + 主题
- 提取的要点
- 检测的语气
- 源图片数量

**使用 AskUserQuestion** 询问：
1. 核心卖点（multiSelect: true）
2. 目标受众
3. 风格偏好：真实分享 / 专业测评 / 氛围感 / 自动
4. 补充信息（可选）

**回复后**：更新 `analysis.md` → 步骤 3

### 步骤 3：生成 3 套大纲 + 风格方案

基于分析 + 用户上下文，创建三种差异化策略方案。每种方案包含**大纲结构**和**推荐视觉风格**。

**每个策略**：

| 策略 | 文件名 | 大纲 | 推荐风格 |
|----------|----------|---------|-------------------|
| A | `outline-strategy-a.md` | 故事驱动：情感化、前后对比 | warm, cute, fresh |
| B | `outline-strategy-b.md` | 信息密集：结构化、事实型 | notion, minimal, chalkboard |
| C | `outline-strategy-c.md` | 视觉优先：氛围感、极简文字 | bold, pop, retro |

**大纲格式**（YAML frontmatter + 内容）：
```yaml
---
strategy: a  # a, b, 或 c
name: 故事驱动型
style: warm  # 此策略的推荐风格
style_reason: "暖色调增强情感叙事和个人连接"
elements:  # 来自风格预设，可在步骤 4 自定义
  background: solid-pastel
  decorations: [clouds, stars-sparkles]
  emphasis: star-burst
  typography: highlight
layout: balanced  # 主布局
image_count: 5
---

## P1 封面
**类型**: cover
**钩子**: "入冬后脸不干了🥹终于找到对的面霜"
**视觉**: 产品主图配温馨冬日氛围
**布局**: sparse

## P2 痛点
**类型**: pain-point
**信息**: 之前干燥肌肤的困扰
**视觉**: 之前状态，共鸣场景
**布局**: balanced

...
```

**差异化要求**：
- 每个策略必须有不同的大纲结构和不同的推荐风格
- 调整页数：A 通常 4-6 页，B 通常 3-5 页，C 通常 3-4 页
- 包含 `style_reason` 解释为什么这个风格适合该策略
- 考虑用户在步骤 2 的风格偏好

参考：`references/workflows/outline-template.md`

### 步骤 4：确认 2 - 大纲 & 风格 & 元素选择 ⚠️

**目的**：用户选择大纲策略，确认视觉风格，自定义元素。**不可跳过。**

**展示每个策略**：
- 策略名称 + 页数 + 推荐风格
- 逐页摘要（P1 → P2 → P3...）

**使用 AskUserQuestion** 包含三个问题：

**问题 1：大纲策略**
- 策略 A（如果"真实分享"则推荐）
- 策略 B（如果"专业测评"则推荐）
- 策略 C（如果"氛围感"则推荐）
- 组合：指定各策略的页面

**问题 2：视觉风格**
- 使用策略推荐的风格（显示是哪个风格）
- 或从以下选择：cute / fresh / warm / bold / minimal / retro / pop / notion / chalkboard
- 或输入自定义风格描述

**问题 3：视觉元素**（风格选择后显示）
显示所选风格的预设默认元素，然后询问：
- 使用风格默认值（推荐）- 显示预览：背景、装饰、强调
- 调整背景 - 选项：solid-pastel / solid-saturated / gradient-linear / gradient-radial / paper-texture / grid
- 调整装饰 - 选项：hearts / stars-sparkles / flowers / clouds / leaves / confetti
- 输入自定义元素偏好

**回复后**：
- 单一策略 → 复制到 `outline.md` 并应用确认的风格
- 组合 → 合并指定页面并应用确认的风格
- 自定义请求 → 根据反馈重新生成
- 风格默认值 → 直接使用预设的元素组合
- 背景调整 → 用用户选择更新 elements.background
- 装饰调整 → 用用户选择更新 elements.decorations
- 自定义元素 → 将用户偏好解析到 elements 字段
- 用最终风格和元素更新 `outline.md` frontmatter

### 步骤 5：生成图片

确认大纲 + 风格 + 布局后，使用内置图片生成脚本：

**图片生成命令**：
```bash
# 基本用法（从提示词文件生成）
npx -y bun ~/.agents/skills/xhs-images/scripts/generate-image.ts \
  --promptfile prompts/01-cover-slug.md \
  --image 01-cover-slug.png

# 指定宽高比（默认 3:4）
npx -y bun ~/.agents/skills/xhs-images/scripts/generate-image.ts \
  --promptfile prompts/01-cover-slug.md \
  --image 01-cover-slug.png \
  --ar 1:1

# 使用参考图片保持风格一致
npx -y bun ~/.agents/skills/xhs-images/scripts/generate-image.ts \
  --promptfile prompts/02-content-slug.md \
  --image 02-content-slug.png \
  --ref 01-cover-slug.png
```

**对每张图片（封面 + 内容 + 结尾）**：
1. 保存提示词到 `prompts/NN-{type}-[slug].md`（使用用户偏好的语言）
   - **备份规则**：如果提示词文件存在，重命名为 `prompts/NN-{type}-[slug]-backup-YYYYMMDD-HHMMSS.md`
2. 调用内置脚本生成图片
   - **备份规则**：如果图片文件存在，重命名为 `NN-{type}-[slug]-backup-YYYYMMDD-HHMMSS.png`
3. 每张生成后报告进度

**水印应用**（如果在偏好中启用）：
添加到每个图片生成提示词：
```
在 [位置] 添加微妙的水印 "[内容]"。
水印应清晰可辨但不干扰主要内容。
```
参考：`references/config/watermark-guide.md`

**小红书宽高比**：
| 宽高比 | 说明 | 适用场景 |
|--------|------|----------|
| `3:4` | 标准小红书（默认） | 大多数信息图、种草笔记 |
| `1:1` | 方形 | 头图、对比图 |
| `4:3` | 横向 | 宽幅内容、时间线 |
| `9:16` | 全屏故事 | 竖屏长图 |

**风格一致性**：
使用 `--ref` 参数传入已生成的图片作为参考，确保系列图片视觉风格统一：
```bash
# 第一张图片（封面）
npx -y bun ~/.agents/skills/xhs-images/scripts/generate-image.ts \
  --promptfile prompts/01-cover-slug.md --image 01-cover-slug.png

# 后续图片使用封面作为参考
npx -y bun ~/.agents/skills/xhs-images/scripts/generate-image.ts \
  --promptfile prompts/02-content-slug.md --image 02-content-slug.png \
  --ref 01-cover-slug.png
```

### 步骤 6：完成报告

```
小红书信息图系列完成！

主题：[主题]
策略：[A/B/C/组合]
风格：[风格名称]
布局：[布局名称或"多样"]
位置：[目录路径]
图片：共 N 张

✓ analysis.md
✓ outline-strategy-a.md
✓ outline-strategy-b.md
✓ outline-strategy-c.md
✓ outline.md（选择：[策略]）

文件：
- 01-cover-[slug].png ✓ 封面（sparse）
- 02-content-[slug].png ✓ 内容（balanced）
- 03-content-[slug].png ✓ 内容（dense）
- 04-ending-[slug].png ✓ 结尾（sparse）
```

## 图片修改

| 操作 | 步骤 |
|--------|-------|
| **编辑** | **先更新提示词文件** → 使用相同会话 ID 重新生成 |
| **添加** | 指定位置 → 创建提示词 → 生成 → 后续文件重新编号（NN+1）→ 更新大纲 |
| **删除** | 删除文件 → 后续重新编号（NN-1）→ 更新大纲 |

**重要**：更新图片时，务必**先更新提示词文件**（`prompts/NN-{type}-[slug].md`）再重新生成。这确保更改有记录且可复现。

## 内容拆分原则

1. **封面（图 1）**：钩子 + 视觉冲击 → `sparse` 布局
2. **内容（中间）**：每张一个核心价值点 → `balanced`/`dense`/`list`/`comparison`/`flow`
3. **结尾（最后一张）**：行动号召 / 总结 → `sparse` 或 `balanced`

**风格 × 布局矩阵**（✓✓ = 强烈推荐，✓ = 适用）：

| | sparse | balanced | dense | list | comparison | flow | mindmap | quadrant |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| cute | ✓✓ | ✓✓ | ✓ | ✓✓ | ✓ | ✓ | ✓ | ✓ |
| fresh | ✓✓ | ✓✓ | ✓ | ✓ | ✓ | ✓✓ | ✓ | ✓ |
| warm | ✓✓ | ✓✓ | ✓ | ✓ | ✓✓ | ✓ | ✓ | ✓ |
| bold | ✓✓ | ✓ | ✓ | ✓✓ | ✓✓ | ✓ | ✓ | ✓✓ |
| minimal | ✓✓ | ✓✓ | ✓✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| retro | ✓✓ | ✓✓ | ✓ | ✓✓ | ✓ | ✓ | ✓ | ✓ |
| pop | ✓✓ | ✓✓ | ✓ | ✓✓ | ✓✓ | ✓ | ✓ | ✓ |
| notion | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ |
| chalkboard | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓ | ✓✓ | ✓✓ | ✓ |
| study-notes | ✗ | ✓ | ✓✓ | ✓✓ | ✓ | ✓ | ✓✓ | ✓ |

## 参考文档

详细模板在 `references/` 目录：

**元素**（视觉构建块）：
- `elements/canvas.md` - 宽高比、安全区、网格布局
- `elements/image-effects.md` - 抠图、描边、滤镜
- `elements/typography.md` - 花字、标签、文字方向
- `elements/decorations.md` - 强调标记、背景、涂鸦、边框

**预设**（风格预设）：
- `presets/<名称>.md` - 元素组合定义（cute、notion、warm...）

**工作流**（流程指南）：
- `workflows/analysis-framework.md` - 内容分析框架
- `workflows/outline-template.md` - 带布局指南的大纲模板
- `workflows/prompt-assembly.md` - 提示词组装指南

**配置**（设置）：
- `config/preferences-schema.md` - EXTEND.md 架构
- `config/first-time-setup.md` - 首次设置流程
- `config/watermark-guide.md` - 水印配置

## 注意事项

- 失败时自动重试一次 | 敏感人物使用卡通替代
- 使用确认的语言偏好 | 保持风格一致性
- **必须完成两个确认点**（步骤 2 和 4）- 不可跳过

## 扩展支持

通过 EXTEND.md 自定义配置。见**步骤 0**了解路径和支持的选项。

## 内置图片生成脚本

本技能包含独立的图片生成脚本，无需依赖其他技能。

### 脚本位置

```
~/.agents/skills/xhs-images/scripts/generate-image.ts
```

### 环境配置

**必需**：设置 Google API 密钥（任选其一）：
```bash
export GOOGLE_API_KEY="your-api-key"
# 或
export GEMINI_API_KEY="your-api-key"
```

**推荐**：创建 `.env` 文件（自动加载）：
```bash
# ~/.baoyu-skills/.env（全局）
# 或 .baoyu-skills/.env（项目级）

GOOGLE_API_KEY=your-api-key
GOOGLE_IMAGE_MODEL=gemini-3-pro-image-preview
```

### 命令参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--prompt`, `-p` | 提示词文本 | - |
| `--promptfile` | 从文件读取提示词 | - |
| `--image` | 输出图片路径（必需） | - |
| `--model`, `-m` | 模型 ID | gemini-3-pro-image-preview |
| `--ar` | 宽高比 | 3:4 |
| `--quality` | 质量：normal / 2k | 2k |
| `--imageSize` | 图片尺寸：1K / 2K / 4K | 由 quality 决定 |
| `--ref` | 参考图片（支持多个） | - |

### 支持的模型

| 模型 | 说明 | 参考图支持 |
|------|------|------------|
| `gemini-3-pro-image-preview` | Gemini 多模态（默认） | ✓ |
| `gemini-3-flash-preview` | Gemini 快速版 | ✓ |
| `imagen-3.0-generate-002` | Imagen 3 | ✗ |
| `imagen-3.0-generate-001` | Imagen 3 旧版 | ✗ |

### 使用示例

```bash
# 直接提示词
npx -y bun ~/.agents/skills/xhs-images/scripts/generate-image.ts \
  -p "可爱的小红书风格信息图，主题：早起的5个好处" \
  --image morning-routine.png

# 从文件读取提示词
npx -y bun ~/.agents/skills/xhs-images/scripts/generate-image.ts \
  --promptfile prompts/01-cover.md \
  --image 01-cover.png

# 方形图片 + 参考图
npx -y bun ~/.agents/skills/xhs-images/scripts/generate-image.ts \
  --promptfile prompts/02-content.md \
  --image 02-content.png \
  --ar 1:1 \
  --ref 01-cover.png

# 使用 Imagen 模型
npx -y bun ~/.agents/skills/xhs-images/scripts/generate-image.ts \
  --promptfile prompts/01-cover.md \
  --image 01-cover.png \
  --model imagen-3.0-generate-002
```

### 错误处理

- 生成失败自动重试一次
- 敏感内容会返回错误，建议使用卡通风格替代真人
- API 限流时等待后重试
