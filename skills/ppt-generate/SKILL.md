---
name: ppt-generate
description: 从内容生成专业的幻灯片图片。创建带有样式说明的大纲，然后生成单独的幻灯片图片。当用户要求"创建幻灯片"、"制作演示文稿"、"生成演示"、"幻灯片"或"PPT"时使用。
---

# 幻灯片生成器

将内容转换为专业的幻灯片图片。

## 使用方法

```bash
/ppt-generate path/to/content.md
/ppt-generate path/to/content.md --style sketch-notes
/ppt-generate path/to/content.md --audience executives
/ppt-generate path/to/content.md --lang zh
/ppt-generate path/to/content.md --slides 10
/ppt-generate path/to/content.md --outline-only
/ppt-generate  # 然后粘贴内容
```

## 脚本目录

**Agent 执行说明**：
1. 确定此 SKILL.md 文件的目录路径为 `SKILL_DIR`
2. 脚本路径 = `${SKILL_DIR}/scripts/<script-name>.ts`

| 脚本 | 用途 |
|--------|---------|
| `scripts/generate-slide-image.ts` | 使用 Google Gemini 生成幻灯片图片（**必须使用**） |
| `scripts/merge-to-pptx.ts` | 将幻灯片合并为 PowerPoint |
| `scripts/merge-to-pdf.ts` | 将幻灯片合并为 PDF |

## 选项

| 选项 | 描述 |
|--------|-------------|
| `--style <name>` | 视觉样式：预设名称、`custom` 或自定义样式名称 |
| `--audience <type>` | 目标受众：beginners（初学者）、intermediate（中级）、experts（专家）、executives（高管）、general（通用） |
| `--lang <code>` | 输出语言（en、zh、ja 等） |
| `--slides <number>` | 目标幻灯片数量（建议 8-25，最多 30） |
| `--outline-only` | 仅生成大纲，跳过图片生成 |
| `--prompts-only` | 生成大纲 + 提示词，跳过图片 |
| `--images-only` | 从现有提示词目录生成图片 |
| `--regenerate <N>` | 重新生成特定幻灯片：`--regenerate 3` 或 `--regenerate 2,5,8` |

**根据内容长度确定幻灯片数量**：
| 内容 | 幻灯片数 |
|---------|--------|
| < 1000 词 | 5-10 |
| 1000-3000 词 | 10-18 |
| 3000-5000 词 | 15-25 |
| > 5000 词 | 20-30（建议拆分） |

## 样式系统

### 预设

| 预设 | 维度 | 最适用于 |
|--------|------------|----------|
| `blueprint`（默认） | 网格 + 冷色 + 技术 + 均衡 | 架构、系统设计 |
| `chalkboard` | 有机 + 暖色 + 手写 + 均衡 | 教育、教程 |
| `corporate` | 干净 + 专业 + 几何 + 均衡 | 投资者演示、提案 |
| `minimal` | 干净 + 中性 + 几何 + 极简 | 高管简报 |
| `sketch-notes` | 有机 + 暖色 + 手写 + 均衡 | 教育、教程 |
| `watercolor` | 有机 + 暖色 + 人文 + 极简 | 生活方式、健康 |
| `dark-atmospheric` | 干净 + 深色 + 编辑 + 均衡 | 娱乐、游戏 |
| `notion` | 干净 + 中性 + 几何 + 密集 | 产品演示、SaaS |
| `bold-editorial` | 干净 + 鲜艳 + 编辑 + 均衡 | 产品发布、主题演讲 |
| `editorial-infographic` | 干净 + 冷色 + 编辑 + 密集 | 技术讲解、研究 |
| `fantasy-animation` | 有机 + 鲜艳 + 手写 + 极简 | 教育故事 |
| `intuition-machine` | 干净 + 冷色 + 技术 + 密集 | 技术文档、学术 |
| `pixel-art` | 像素 + 鲜艳 + 技术 + 均衡 | 游戏、开发者演讲 |
| `scientific` | 干净 + 冷色 + 技术 + 密集 | 生物、化学、医学 |
| `vector-illustration` | 干净 + 鲜艳 + 人文 + 均衡 | 创意、儿童内容 |
| `vintage` | 纸质 + 暖色 + 编辑 + 均衡 | 历史、传统 |

### 样式维度

| 维度 | 选项 | 描述 |
|-----------|---------|-------------|
| **Texture（纹理）** | clean、grid、organic、pixel、paper | 视觉纹理和背景处理 |
| **Mood（色调）** | professional、warm、cool、vibrant、dark、neutral | 色温和调色板风格 |
| **Typography（排版）** | geometric、humanist、handwritten、editorial、technical | 标题和正文样式 |
| **Density（密度）** | minimal、balanced、dense | 每张幻灯片的信息密度 |

完整规格：`references/dimensions/*.md`

### 自动样式选择

| 内容信号 | 预设 |
|-----------------|--------|
| tutorial、learn、education、guide、beginner | `sketch-notes` |
| classroom、teaching、school、chalkboard | `chalkboard` |
| architecture、system、data、analysis、technical | `blueprint` |
| creative、children、kids、cute | `vector-illustration` |
| briefing、academic、research、bilingual | `intuition-machine` |
| executive、minimal、clean、simple | `minimal` |
| saas、product、dashboard、metrics | `notion` |
| investor、quarterly、business、corporate | `corporate` |
| launch、marketing、keynote、magazine | `bold-editorial` |
| entertainment、music、gaming、atmospheric | `dark-atmospheric` |
| explainer、journalism、science communication | `editorial-infographic` |
| story、fantasy、animation、magical | `fantasy-animation` |
| gaming、retro、pixel、developer | `pixel-art` |
| biology、chemistry、medical、scientific | `scientific` |
| history、heritage、vintage、expedition | `vintage` |
| lifestyle、wellness、travel、artistic | `watercolor` |
| 默认 | `blueprint` |

## 设计理念

幻灯片设计用于**阅读和分享**，而非现场演示：
- 每张幻灯片无需口头解释即可自成一体
- 滚动时逻辑流畅
- 每张幻灯片内包含所有必要上下文
- 针对社交媒体分享进行优化

参见 `references/design-guidelines.md` 了解：
- 受众特定原则
- 视觉层次
- 内容密度指南
- 颜色和排版选择
- 字体推荐

参见 `references/layouts.md` 了解布局选项。

## 文件管理

### 输出目录

```
slide-deck/{topic-slug}/
├── source-{slug}.{ext}
├── outline.md
├── prompts/
│   └── 01-slide-cover.md, 02-slide-{slug}.md, ...
├── 01-slide-cover.png, 02-slide-{slug}.png, ...
├── {topic-slug}.pptx
└── {topic-slug}.pdf
```

**Slug**：提取主题（2-4 个词，kebab-case）。示例："Introduction to Machine Learning" → `intro-machine-learning`

**冲突处理**：参见步骤 1.3 了解现有内容检测和用户选项。

## 语言处理

**检测优先级**：
1. `--lang` 标志（显式）
2. EXTEND.md `language` 设置
3. 用户对话语言（输入语言）
4. 源内容语言

**规则**：所有响应使用用户首选语言：
- 问题和确认
- 进度报告
- 错误消息
- 完成摘要

技术术语（样式名称、文件路径、代码）保持英文。

## 工作流程

复制此检查清单并在完成时勾选：

```
幻灯片进度：
- [ ] 步骤 1：设置和分析
  - [ ] 1.1 加载偏好设置
  - [ ] 1.2 分析内容
  - [ ] 1.3 检查现有内容 ⚠️ 必需
- [ ] 步骤 2：确认 ⚠️ 必需（第 1 轮，可选第 2 轮）
- [ ] 步骤 3：生成大纲
- [ ] 步骤 4：审查大纲（有条件）
- [ ] 步骤 5：生成提示词
- [ ] 步骤 6：审查提示词（有条件）
- [ ] 步骤 7：生成图片
- [ ] 步骤 8：合并为 PPTX/PDF
- [ ] 步骤 9：输出摘要
```

### 流程

```
输入 → 偏好设置 → 分析 → [检查现有？] → 确认（1-2 轮） → 大纲 → [审查大纲？] → 提示词 → [审查提示词？] → 图片 → 合并 → 完成
```

### 步骤 1：设置和分析

**1.1 加载偏好设置（EXTEND.md）**

使用 Bash 检查 EXTEND.md 是否存在（优先顺序）：

```bash
# 首先检查项目级别
test -f .baoyu-skills/ppt-generate/EXTEND.md && echo "project"

# 然后检查用户级别（跨平台：$HOME 在 macOS/Linux/WSL 上都有效）
test -f "$HOME/.baoyu-skills/ppt-generate/EXTEND.md" && echo "user"
```

┌──────────────────────────────────────────────────┬───────────────────┐
│                       路径                       │     位置          │
├──────────────────────────────────────────────────┼───────────────────┤
│ .baoyu-skills/ppt-generate/EXTEND.md         │ 项目目录          │
├──────────────────────────────────────────────────┼───────────────────┤
│ $HOME/.baoyu-skills/ppt-generate/EXTEND.md   │ 用户主目录        │
└──────────────────────────────────────────────────┴───────────────────┘

**找到 EXTEND.md 时** → 读取、解析，**向用户输出摘要**：

```
📋 已从 [完整路径] 加载偏好设置
├─ 样式：[预设/自定义名称]
├─ 受众：[受众或"自动检测"]
├─ 语言：[语言或"自动检测"]
└─ 审查：[启用/禁用]
```

**未找到 EXTEND.md 时** → 使用 AskUserQuestion 进行首次设置或使用默认值继续。

**EXTEND.md 支持**：首选样式 | 自定义维度 | 默认受众 | 语言偏好 | 审查偏好

Schema：`references/config/preferences-schema.md`

**1.2 分析内容**

1. 保存源内容（如果是粘贴的，保存为 `source.md`）
   - **备份规则**：如果 `source.md` 存在，重命名为 `source-backup-YYYYMMDD-HHMMSS.md`
2. 按照 `references/analysis-framework.md` 进行内容分析
3. 分析内容信号以获取样式推荐
4. 检测源语言
5. 确定推荐的幻灯片数量
6. 从内容生成主题 slug

**1.3 检查现有内容** ⚠️ 必需

**必须在进入步骤 2 之前执行。**

使用 Bash 检查输出目录是否存在：

```bash
test -d "slide-deck/{topic-slug}" && echo "exists"
```

**如果目录存在**，使用 AskUserQuestion：

```
header: "现有内容"
question: "发现现有内容。如何处理？"
options:
  - label: "重新生成大纲"
    description: "保留图片，仅重新生成大纲"
  - label: "重新生成图片"
    description: "保留大纲，仅重新生成图片"
  - label: "备份并重新生成"
    description: "备份到 {slug}-backup-{timestamp}，然后全部重新生成"
  - label: "退出"
    description: "取消，保持现有内容不变"
```

**保存到 `analysis.md`** 包含：
- 主题、受众、内容信号
- 推荐样式（基于自动样式选择）
- 推荐幻灯片数量
- 语言检测

### 步骤 2：确认 ⚠️ 必需

**两轮确认**：第 1 轮始终进行，第 2 轮仅在选择"自定义维度"时进行。

**语言**：使用用户的输入语言或保存的语言偏好。

**显示摘要**：
- 识别的内容类型 + 主题
- 语言：[来自 EXTEND.md 或检测]
- **推荐样式**：[预设]（基于内容信号）
- **推荐幻灯片数**：[N]（基于内容长度）

#### 第 1 轮（始终）

**使用 AskUserQuestion** 询问所有 5 个问题：

**问题 1：样式**
```
header: "样式"
question: "此幻灯片使用哪种视觉样式？"
options:
  - label: "{recommended_preset}（推荐）"
    description: "基于内容分析的最佳匹配"
  - label: "{alternative_preset}"
    description: "[备选样式描述]"
  - label: "自定义维度"
    description: "分别选择纹理、色调、排版、密度"
```

**问题 2：受众**
```
header: "受众"
question: "主要读者是谁？"
options:
  - label: "普通读者（推荐）"
    description: "广泛吸引力，易于理解的内容"
  - label: "初学者/学习者"
    description: "教育为主，清晰解释"
  - label: "专家/专业人士"
    description: "技术深度，领域知识"
  - label: "高管"
    description: "高层洞察，最少细节"
```

**问题 3：幻灯片数量**
```
header: "幻灯片"
question: "需要多少张幻灯片？"
options:
  - label: "{N} 张幻灯片（推荐）"
    description: "基于内容长度"
  - label: "更少（{N-3} 张幻灯片）"
    description: "更精简，更少细节"
  - label: "更多（{N+3} 张幻灯片）"
    description: "更详细的分解"
```

**问题 4：审查大纲**
```
header: "大纲"
question: "在生成提示词之前审查大纲吗？"
options:
  - label: "是的，审查大纲（推荐）"
    description: "审查幻灯片标题和结构"
  - label: "不，跳过大纲审查"
    description: "直接进入提示词生成"
```

**问题 5：审查提示词**
```
header: "提示词"
question: "在生成图片之前审查提示词吗？"
options:
  - label: "是的，审查提示词（推荐）"
    description: "审查图片生成提示词"
  - label: "不，跳过提示词审查"
    description: "直接进入图片生成"
```

#### 第 2 轮（仅在选择"自定义维度"时）

**使用 AskUserQuestion** 询问所有 4 个维度：

**问题 1：纹理**
```
header: "纹理"
question: "使用哪种视觉纹理？"
options:
  - label: "clean"
    description: "纯色实心，无纹理"
  - label: "grid"
    description: "细微网格叠加，技术感"
  - label: "organic"
    description: "柔和纹理，手绘感"
  - label: "pixel"
    description: "粗块像素，8位风格"
```
（注意："paper"可通过其他选项获得）

**问题 2：色调**
```
header: "色调"
question: "使用哪种颜色色调？"
options:
  - label: "professional"
    description: "冷中性，海军蓝/金色"
  - label: "warm"
    description: "大地色系，友好"
  - label: "cool"
    description: "蓝色、灰色，分析感"
  - label: "vibrant"
    description: "高饱和度，大胆"
```
（注意："dark"、"neutral"可通过其他选项获得）

**问题 3：排版**
```
header: "排版"
question: "使用哪种排版风格？"
options:
  - label: "geometric"
    description: "现代无衬线，干净"
  - label: "humanist"
    description: "友好，易读"
  - label: "handwritten"
    description: "马克笔/画笔，有机"
  - label: "editorial"
    description: "杂志风格，戏剧性"
```
（注意："technical"可通过其他选项获得）

**问题 4：密度**
```
header: "密度"
question: "信息密度？"
options:
  - label: "balanced（推荐）"
    description: "每张幻灯片 2-3 个要点"
  - label: "minimal"
    description: "一个焦点，最大留白"
  - label: "dense"
    description: "多个数据点，紧凑"
```

**第 2 轮之后**：将自定义维度存储为样式配置。

**确认之后**：
1. 使用确认的偏好更新 `analysis.md`
2. 从问题 4 存储 `skip_outline_review` 标志
3. 从问题 5 存储 `skip_prompt_review` 标志
4. → 步骤 3

### 步骤 3：生成大纲

使用步骤 2 确认的样式创建大纲。

**样式解析**：
- 如果选择预设 → 读取 `references/styles/{preset}.md`
- 如果自定义维度 → 读取 `references/dimensions/` 中的维度文件并组合

**生成**：
1. 按照 `references/outline-template.md` 的结构
2. 从样式或维度构建 STYLE_INSTRUCTIONS
3. 应用确认的受众、语言、幻灯片数量
4. 保存为 `outline.md`

**生成后**：
- 如果 `--outline-only`，在此停止
- 如果 `skip_outline_review` 为 true → 跳过步骤 4，进入步骤 5
- 如果 `skip_outline_review` 为 false → 继续步骤 4

### 步骤 4：审查大纲（有条件）

**如果用户在步骤 2 选择"不，跳过大纲审查"，则跳过此步骤。**

**目的**：在提示词生成之前审查大纲结构。

**语言**：使用用户的输入语言或保存的语言偏好。

**显示**：
- 总幻灯片数：N
- 样式：[预设名称或"custom: 纹理+色调+排版+密度"]
- 逐张幻灯片摘要表：

```
| # | 标题 | 类型 | 布局 |
|---|-------|------|--------|
| 1 | [标题] | Cover | title-hero |
| 2 | [标题] | Content | [布局] |
| 3 | [标题] | Content | [布局] |
| ... | ... | ... | ... |
```

**使用 AskUserQuestion**：
```
header: "确认"
question: "准备好生成提示词了吗？"
options:
  - label: "是的，继续（推荐）"
    description: "生成图片提示词"
  - label: "先编辑大纲"
    description: "我会在继续之前修改 outline.md"
  - label: "重新生成大纲"
    description: "使用不同方法创建新大纲"
```

**响应后**：
1. 如果"先编辑大纲" → 通知用户编辑 `outline.md`，准备好后再次询问
2. 如果"重新生成大纲" → 返回步骤 3
3. 如果"是的，继续" → 继续步骤 5

### 步骤 5：生成提示词

1. 读取 `references/base-prompt.md`
2. 对于大纲中的每张幻灯片：
   - 从大纲中提取 STYLE_INSTRUCTIONS（不要再次读取样式文件）
   - 添加幻灯片特定内容
   - 如果指定了 `Layout:`，包含来自 `references/layouts.md` 的布局指导
3. 保存到 `prompts/` 目录
   - **备份规则**：如果提示词文件存在，重命名为 `prompts/NN-slide-{slug}-backup-YYYYMMDD-HHMMSS.md`

**生成后**：
- 如果 `--prompts-only`，在此停止并输出提示词摘要
- 如果 `skip_prompt_review` 为 true → 跳过步骤 6，进入步骤 7
- 如果 `skip_prompt_review` 为 false → 继续步骤 6

### 步骤 6：审查提示词（有条件）

**如果用户在步骤 2 选择"不，跳过提示词审查"，则跳过此步骤。**

**目的**：在图片生成之前审查提示词。

**语言**：使用用户的输入语言或保存的语言偏好。

**显示**：
- 总提示词数：N
- 样式：[预设名称或自定义维度]
- 提示词列表：

```
| # | 文件名 | 幻灯片标题 |
|---|----------|-------------|
| 1 | 01-slide-cover.md | [标题] |
| 2 | 02-slide-xxx.md | [标题] |
| ... | ... | ... |
```

- 提示词目录路径：`prompts/`

**使用 AskUserQuestion**：
```
header: "确认"
question: "准备好生成幻灯片图片了吗？"
options:
  - label: "是的，继续（推荐）"
    description: "生成所有幻灯片图片"
  - label: "先编辑提示词"
    description: "我会在继续之前修改提示词"
  - label: "重新生成提示词"
    description: "使用不同方法创建新提示词"
```

**响应后**：
1. 如果"先编辑提示词" → 通知用户编辑提示词，准备好后再次询问
2. 如果"重新生成提示词" → 返回步骤 5
3. 如果"是的，继续" → 继续步骤 7

### 步骤 7：生成图片

**对于 `--images-only`**：从此处开始使用现有提示词。

**对于 `--regenerate N`**：仅重新生成指定的幻灯片。

**⚠️ 必须使用 Google Gemini 生成图片**：所有 PPT 幻灯片图片必须通过 `generate-slide-image.ts` 脚本生成，这是强制要求。

**标准流程**：
1. 对于每张幻灯片，使用以下命令生成图片：

```bash
npx -y bun ${SKILL_DIR}/scripts/generate-slide-image.ts \
  --promptfile <prompts/NN-slide-{slug}.md> \
  --image <NN-slide-{slug}.png> \
  --ar 16:9 \
  --quality 2k
```

2. **备份规则**：如果图片文件存在，在生成前重命名为 `NN-slide-{slug}-backup-YYYYMMDD-HHMMSS.png`
3. 报告进度："已生成 X/N"（使用用户语言）
4. 脚本内置自动重试机制（失败时重试一次）

**环境变量要求**：
- 需要设置 `GOOGLE_API_KEY` 或 `GEMINI_API_KEY`
- 可选：`GOOGLE_IMAGE_MODEL`（默认：gemini-3-pro-image-preview）

**选项说明**：
| 选项 | 描述 |
|------|------|
| `--promptfile <file>` | 从 markdown 文件读取提示词 |
| `--image <path>` | 输出图片路径 |
| `--ar <ratio>` | 宽高比（推荐 `16:9`） |
| `--quality 2k` | 高质量输出（2K 分辨率） |
| `--ref <files...>` | 参考图片（可选，用于风格参考） |

### 步骤 8：合并为 PPTX 和 PDF

```bash
npx -y bun ${SKILL_DIR}/scripts/merge-to-pptx.ts <slide-deck-dir>
npx -y bun ${SKILL_DIR}/scripts/merge-to-pdf.ts <slide-deck-dir>
```

### 步骤 9：输出摘要

**语言**：使用用户的输入语言或保存的语言偏好。

```
幻灯片完成！

主题：[主题]
样式：[预设名称或自定义维度]
位置：[目录路径]
幻灯片：共 N 张

- 01-slide-cover.png - 封面
- 02-slide-intro.png - 内容
- ...
- {NN}-slide-back-cover.png - 封底

大纲：outline.md
PPTX：{topic-slug}.pptx
PDF：{topic-slug}.pdf
```

## 部分工作流程

| 选项 | 工作流程 |
|--------|----------|
| `--outline-only` | 仅步骤 1-3（在大纲后停止） |
| `--prompts-only` | 步骤 1-5（生成提示词，跳过图片） |
| `--images-only` | 跳到步骤 7（需要现有的 prompts/） |
| `--regenerate N` | 仅重新生成特定幻灯片 |

### 使用 `--prompts-only`

生成大纲和提示词，不生成图片：

```bash
/ppt-generate content.md --prompts-only
```

输出：`outline.md` + `prompts/*.md` 准备好供审查/编辑。

### 使用 `--images-only`

从现有提示词生成图片（从步骤 7 开始）：

```bash
/ppt-generate slide-deck/topic-slug/ --images-only
```

前提条件：
- `prompts/` 目录包含幻灯片提示词文件
- `outline.md` 包含样式信息

### 使用 `--regenerate`

重新生成特定幻灯片：

```bash
# 单张幻灯片
/ppt-generate slide-deck/topic-slug/ --regenerate 3

# 多张幻灯片
/ppt-generate slide-deck/topic-slug/ --regenerate 2,5,8
```

流程：
1. 读取指定幻灯片的现有提示词
2. 仅为这些幻灯片重新生成图片
3. 重新生成 PPTX/PDF

## 幻灯片修改

### 快速参考

| 操作 | 命令 | 手动步骤 |
|--------|---------|--------------|
| **编辑** | `--regenerate N` | **先更新提示词文件** → 重新生成图片 → 重新生成 PDF |
| **添加** | 手动 | 创建提示词 → 生成图片 → 重新编号后续文件 → 更新大纲 → 重新生成 PDF |
| **删除** | 手动 | 删除文件 → 重新编号后续文件 → 更新大纲 → 重新生成 PDF |

### 编辑单张幻灯片

1. **先更新** `prompts/NN-slide-{slug}.md` 中的提示词文件
2. 运行：`/ppt-generate <dir> --regenerate N`
3. 或手动重新生成图片 + PDF

**重要**：更新幻灯片时，始终**先**更新提示词文件（`prompts/NN-slide-{slug}.md`），然后再重新生成。这确保更改被记录且可重现。

### 添加新幻灯片

1. 在位置创建提示词：`prompts/NN-slide-{new-slug}.md`
2. 使用相同的会话 ID 生成图片
3. **重新编号**：后续文件 NN+1（slug 不变）
4. 更新 `outline.md`
5. 重新生成 PPTX/PDF

### 删除幻灯片

1. 删除 `NN-slide-{slug}.png` 和 `prompts/NN-slide-{slug}.md`
2. **重新编号**：后续文件 NN-1（slug 不变）
3. 更新 `outline.md`
4. 重新生成 PPTX/PDF

### 文件命名

格式：`NN-slide-[slug].png`
- `NN`：两位数序号（01、02、...）
- `slug`：从内容派生的 kebab-case（2-5 个词，唯一）

**重新编号规则**：只有 NN 改变，slug 保持不变。

参见 `references/modification-guide.md` 了解完整详情。

## 参考文档

| 文件 | 内容 |
|------|---------|
| `references/analysis-framework.md` | 演示文稿内容分析 |
| `references/outline-template.md` | 大纲结构和格式 |
| `references/modification-guide.md` | 编辑、添加、删除幻灯片工作流程 |
| `references/content-rules.md` | 内容和样式指南 |
| `references/design-guidelines.md` | 受众、排版、颜色、视觉元素 |
| `references/layouts.md` | 布局选项和选择技巧 |
| `references/base-prompt.md` | 图片生成基础提示词 |
| `references/dimensions/*.md` | 维度规格（纹理、色调、排版、密度） |
| `references/dimensions/presets.md` | 预设 → 维度映射 |
| `references/styles/<style>.md` | 完整样式规格（旧版） |
| `references/config/preferences-schema.md` | EXTEND.md 结构 |

## 注意事项

- 图片生成：每张幻灯片 10-30 秒
- 生成失败时自动重试一次
- 对敏感公众人物使用风格化替代形象
- 通过会话 ID 保持样式一致性
- **步骤 2 确认必需** - 不要跳过（样式、受众、幻灯片数、大纲审查、提示词审查）
- **步骤 4 有条件** - 仅在用户在步骤 2 请求大纲审查时
- **步骤 6 有条件** - 仅在用户在步骤 2 请求提示词审查时

## 扩展支持

通过 EXTEND.md 自定义配置。参见**步骤 1.1** 了解路径和支持的选项。
