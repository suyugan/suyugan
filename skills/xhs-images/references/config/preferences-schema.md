---
name: preferences-schema
description: xhs-images 用户偏好 EXTEND.md YAML 架构
---

# 偏好设置架构

## 完整架构

```yaml
---
version: 1

watermark:
  enabled: false
  content: ""
  position: bottom-right  # bottom-right|bottom-left|bottom-center|top-right

preferred_style:
  name: null              # 内置或自定义风格名称
  description: ""         # 覆盖/备注

preferred_layout: null    # sparse|balanced|dense|list|comparison|flow

language: null            # zh|en|ja|ko|auto

custom_styles:
  - name: my-style
    description: "风格描述"
    color_palette:
      primary: ["#FED7E2", "#FEEBC8"]
      background: "#FFFAF0"
      accents: ["#FF69B4", "#FF6B6B"]
    visual_elements: "爱心、星星、闪光"
    typography: "圆润、可爱的手写字体"
    best_for: "生活方式、美妆"
---
```

## 字段说明

| 字段 | 类型 | 默认值 | 说明 |
|-------|------|---------|-------------|
| `version` | int | 1 | 架构版本 |
| `watermark.enabled` | bool | false | 启用水印 |
| `watermark.content` | string | "" | 水印文字（@用户名或自定义） |
| `watermark.position` | enum | bottom-right | 图片上的位置 |
| `preferred_style.name` | string | null | 风格名称或 null |
| `preferred_style.description` | string | "" | 自定义备注/覆盖 |
| `preferred_layout` | string | null | 布局偏好或 null |
| `language` | string | null | 输出语言（null = 自动检测） |
| `custom_styles` | array | [] | 用户自定义风格 |

## 位置选项

| 值 | 说明 |
|-------|-------------|
| `bottom-right` | 右下角（默认，最常见） |
| `bottom-left` | 左下角 |
| `bottom-center` | 底部居中 |
| `top-right` | 右上角 |

## 自定义风格字段

| 字段 | 必需 | 说明 |
|-------|----------|-------------|
| `name` | 是 | 唯一风格标识（kebab-case） |
| `description` | 是 | 风格传达的感觉 |
| `color_palette.primary` | 否 | 主色（数组） |
| `color_palette.background` | 否 | 背景色 |
| `color_palette.accents` | 否 | 强调色（数组） |
| `visual_elements` | 否 | 装饰元素 |
| `typography` | 否 | 字体/手写风格 |
| `best_for` | 否 | 推荐的内容类型 |

## 示例：简洁偏好

```yaml
---
version: 1
watermark:
  enabled: true
  content: "@myusername"
preferred_style:
  name: notion
---
```

## 示例：完整偏好

```yaml
---
version: 1
watermark:
  enabled: true
  content: "@myxhsaccount"
  position: bottom-right

preferred_style:
  name: notion
  description: "技术内容的简洁知识卡片"

preferred_layout: dense

language: zh

custom_styles:
  - name: corporate
    description: "专业 B2B 风格"
    color_palette:
      primary: ["#1E3A5F", "#4A90D9"]
      background: "#F5F7FA"
      accents: ["#00B4D8", "#48CAE4"]
    visual_elements: "简洁线条、微妙渐变、几何形状"
    typography: "现代无衬线、专业感"
    best_for: "商务、SaaS、企业"
---
```
