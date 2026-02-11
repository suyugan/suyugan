# EXTEND.md Schema

`.baoyu-skills/ppt-generate/EXTEND.md` 中用户偏好设置的结构。

## 完整 Schema

```yaml
# 幻灯片偏好设置

## 默认值
style: blueprint              # 预设名称或 "custom"
audience: general             # beginners | intermediate | experts | executives | general
language: auto                # auto | en | zh | ja 等
review: true                  # true = 生成前审查大纲

## 自定义维度（仅当 style: custom 时）
dimensions:
  texture: clean              # clean | grid | organic | pixel | paper
  mood: professional          # professional | warm | cool | vibrant | dark | neutral
  typography: geometric       # geometric | humanist | handwritten | editorial | technical
  density: balanced           # minimal | balanced | dense

## 自定义样式（可选）
custom_styles:
  my-style:
    texture: organic
    mood: warm
    typography: humanist
    density: minimal
    description: "我的自定义暖色友好样式"
```

## 字段描述

### 默认值

| 字段 | 类型 | 默认值 | 描述 |
|-------|------|---------|-------------|
| `style` | string | `blueprint` | 预设名称、`custom` 或自定义样式名称 |
| `audience` | string | `general` | 默认目标受众 |
| `language` | string | `auto` | 输出语言（auto = 从输入检测） |
| `review` | boolean | `true` | 生成前显示大纲审查 |

### 自定义维度

仅在 `style: custom` 时使用。直接定义维度值。

| 字段 | 选项 | 默认值 |
|-------|---------|---------|
| `texture` | clean、grid、organic、pixel、paper | clean |
| `mood` | professional、warm、cool、vibrant、dark、neutral | professional |
| `typography` | geometric、humanist、handwritten、editorial、technical | geometric |
| `density` | minimal、balanced、dense | balanced |

### 自定义样式

定义可重用的自定义维度组合。

```yaml
custom_styles:
  style-name:
    texture: <texture>
    mood: <mood>
    typography: <typography>
    density: <density>
    description: "可选描述"
```

然后使用：`/ppt-generate content.md --style style-name`

## 最小示例

### 仅更改默认样式

```yaml
style: sketch-notes
```

### 偏好不审查

```yaml
review: false
```

### 自定义默认维度

```yaml
style: custom
dimensions:
  texture: organic
  mood: professional
  typography: humanist
  density: minimal
```

### 定义可重用的自定义样式

```yaml
custom_styles:
  brand-style:
    texture: clean
    mood: vibrant
    typography: editorial
    density: balanced
    description: "公司品牌样式"
```

## 文件位置

优先顺序（找到第一个即生效）：

1. `.baoyu-skills/ppt-generate/EXTEND.md`（项目）
2. `$HOME/.baoyu-skills/ppt-generate/EXTEND.md`（用户）

## 首次设置

当不存在 EXTEND.md 时，技能会提示初始偏好设置：

1. 首选样式（预设或自定义）
2. 默认受众
3. 语言偏好
4. 审查偏好
5. 保存位置（项目或用户）

在选定位置创建 EXTEND.md。
