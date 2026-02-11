# 布局库

可选的单张幻灯片布局提示。在大纲的 `// LAYOUT` 部分指定。

## 幻灯片专用布局

| 布局 | 描述 | 最适用于 |
|--------|-------------|----------|
| `title-hero` | 大号居中标题 + 副标题 | 封面幻灯片、章节分隔 |
| `quote-callout` | 突出引言带署名 | 推荐语、关键洞察 |
| `key-stat` | 单个大数字作为焦点 | 冲击力统计、指标 |
| `split-screen` | 一半图像、一半文本 | 功能亮点、对比 |
| `icon-grid` | 图标网格带标签 | 功能、能力、好处 |
| `two-columns` | 平衡的两栏内容 | 配对信息、双要点 |
| `three-columns` | 三栏内容 | 三项比较、分类 |
| `image-caption` | 满版图像 + 文本叠加 | 视觉叙事、情感化 |
| `agenda` | 编号列表带高亮 | 会议概览、路线图 |
| `bullet-list` | 结构化要点 | 简单内容、列表 |

## 信息图衍生布局

| 布局 | 描述 | 最适用于 |
|--------|-------------|----------|
| `linear-progression` | 从左到右的顺序流程 | 时间线、分步骤 |
| `binary-comparison` | 并排 A vs B | 前后对比、优缺点 |
| `comparison-matrix` | 多因素网格 | 功能比较 |
| `hierarchical-layers` | 金字塔或堆叠层级 | 优先级、重要性 |
| `hub-spoke` | 中心节点带辐射项目 | 概念图、生态系统 |
| `bento-grid` | 不同大小的瓷砖 | 概览、摘要 |
| `funnel` | 逐渐收窄的阶段 | 转化、筛选 |
| `dashboard` | 带图表/数字的指标 | KPI、数据展示 |
| `venn-diagram` | 重叠圆圈 | 关系、交集 |
| `circular-flow` | 连续循环 | 循环流程 |
| `winding-roadmap` | 带里程碑的曲线路径 | 旅程、时间线 |
| `tree-branching` | 父子层级 | 组织图、分类 |
| `iceberg` | 可见 vs 隐藏层 | 表面 vs 深层 |
| `bridge` | 带连接的缺口 | 问题-解决方案 |

**用法**：在幻灯片的 `// LAYOUT` 部分添加 `Layout: <name>`。

## 布局选择技巧

**匹配布局与内容**：
| 内容类型 | 推荐布局 |
|--------------|-------------------|
| 单一叙事 | `bullet-list`、`image-caption` |
| 两个概念 | `split-screen`、`binary-comparison` |
| 三个项目 | `three-columns`、`icon-grid` |
| 流程/步骤 | `linear-progression`、`winding-roadmap` |
| 数据/指标 | `dashboard`、`key-stat` |
| 关系 | `hub-spoke`、`venn-diagram` |
| 层级 | `hierarchical-layers`、`tree-branching` |

**布局流程模式**：
| 位置 | 推荐布局 |
|----------|-------------------|
| 开场 | `title-hero`、`agenda` |
| 中间 | 内容特定布局 |
| 结尾 | `quote-callout`、`key-stat` |

**常见错误避免**：
- 对 2 个项目使用 3 栏布局（留下空栏）
- 将图表/表格堆叠在文本下方（改用并排）
- 没有实际图像的图像布局
- 引言布局用于强调（仅用于带署名的真实引言）
