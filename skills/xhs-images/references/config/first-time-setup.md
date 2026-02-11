---
name: first-time-setup
description: xhs-images 偏好设置首次设置流程
---

# 首次设置

## 概述

当未找到 EXTEND.md 时，引导用户完成偏好设置。

## 设置流程

```
未找到 EXTEND.md
        │
        ▼
┌─────────────────────┐
│ AskUserQuestion     │
│ （所有问题）        │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ 创建 EXTEND.md      │
└─────────────────────┘
        │
        ▼
    继续步骤 1
```

## 问题

**语言**：使用用户的输入语言或已保存的语言偏好。

使用单个 AskUserQuestion 包含多个问题（AskUserQuestion 自动添加"其他"选项）：

### 问题 1：水印

```
header: "水印"
question: "生成图片的水印文字？输入您的水印内容（如姓名、@账号）"
options:
  - label: "无水印（推荐）"
    description: "不添加水印，之后可在 EXTEND.md 中启用"
```

位置默认为右下角。

### 问题 2：偏好风格

```
header: "风格"
question: "默认视觉风格偏好？或输入其他风格名称或自定义风格"
options:
  - label: "无（推荐）"
    description: "根据内容分析自动选择"
  - label: "cute"
    description: "甜美可爱 - 经典小红书风格"
  - label: "notion"
    description: "极简手绘、知性风格"
```

### 问题 3：保存位置

```
header: "保存"
question: "偏好设置保存到哪里？"
options:
  - label: "项目"
    description: ".baoyu-skills/（仅当前项目）"
  - label: "用户"
    description: "~/.baoyu-skills/（所有项目通用）"
```

## 保存位置

| 选择 | 路径 | 范围 |
|--------|------|-------|
| 项目 | `.baoyu-skills/xhs-images/EXTEND.md` | 当前项目 |
| 用户 | `~/.baoyu-skills/xhs-images/EXTEND.md` | 所有项目 |

## 设置后

1. 如需创建目录
2. 写入带 frontmatter 的 EXTEND.md
3. 确认："偏好设置已保存到 [路径]"
4. 继续步骤 1

## EXTEND.md 模板

```yaml
---
version: 1
watermark:
  enabled: [true/false]
  content: "[用户输入或留空]"
  position: bottom-right
  opacity: 0.7
preferred_style:
  name: [选择的风格或 null]
  description: ""
preferred_layout: null
language: null
custom_styles: []
---
```

## 之后修改偏好

用户可直接编辑 EXTEND.md 或重新运行设置：
- 删除 EXTEND.md 可触发重新设置
- 编辑 YAML frontmatter 进行快速更改
- 完整架构：`config/preferences-schema.md`
