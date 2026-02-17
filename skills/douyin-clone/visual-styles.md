# 抖音博主视觉风格分类库

> 用于分析抖音博主时快速匹配风格类型的参考文档。
> 最后更新：2026-02-18

---

## 一、实拍类 (Live Action)

### 1.1 真人出镜口播

- **英文名**: Talking Head
- **视觉特征**: 博主正面对镜头讲话，通常半身或胸部以上构图，背景为室内/纯色/虚化。画面核心是人脸和表情。
- **关键区分点**: 与Vlog的区别——口播是固定机位对着镜头讲，Vlog是移动拍摄记录生活。
- **代表博主**: 张雪峰、董宇辉、刘媛媛
- **生成方式**: 手机/相机拍摄 + 剪映/PR剪辑，加字幕和花字
- **风格关键词**: N/A（实拍，非AI生图）

### 1.2 产品实拍

- **英文名**: Product Showcase
- **视觉特征**: 以产品为主体，特写镜头展示细节、质感、使用过程。常用微距、旋转展示、开箱等手法。背景干净简洁。
- **关键区分点**: 与口播的区别——画面主体是产品而非人；与图文类的区别——是视频拍摄而非静态图片。
- **代表博主**: 老爸评测、何同学（数码部分）
- **生成方式**: 相机+灯光拍摄，PR/达芬奇调色剪辑
- **风格关键词**: N/A

### 1.3 Vlog日常

- **英文名**: Vlog / Daily Life
- **视觉特征**: 移动拍摄，记录日常生活场景，画面多变（室内外切换），有运镜和场景转换。通常配旁白或现场音。
- **关键区分点**: 与口播的区别——不是对着镜头讲，而是记录过程；画面更丰富多场景。
- **代表博主**: 房琪kiki、张踩铃
- **生成方式**: 手机/运动相机拍摄 + 剪映剪辑，配乐+字幕
- **风格关键词**: N/A

### 1.4 街拍采访

- **英文名**: Street Interview
- **视觉特征**: 户外街头场景，博主手持麦克风采访路人，画面有明显的街头环境感。通常双人构图（采访者+被访者）。
- **关键区分点**: 与口播的区别——有互动对象，在户外；与Vlog的区别——有明确的采访互动形式。
- **代表博主**: 大能、街头壹哥
- **生成方式**: 手机/相机拍摄 + 剪辑，加字幕和花字特效
- **风格关键词**: N/A

---

## 二、插画类 (Illustration)

### 2.1 手绘风

- **英文名**: Hand-drawn / Sketch Style
- **视觉特征**: 模拟手绘质感，线条有粗细变化和不规则感，色彩可浓可淡，有纸张纹理或铅笔/马克笔痕迹。
- **关键区分点**: 与扁平插画的区别——手绘风有明显的笔触质感和不规则性；与简笔画的区别——手绘风更精致有细节。
- **代表博主**: 一禅小和尚（早期风格）
- **生成方式**: Midjourney / Stable Diffusion / ComfyUI
- **风格关键词**: `hand-drawn illustration, pencil sketch, marker drawing, textured paper, organic lines, artistic sketch style`

### 2.2 水彩风

- **英文名**: Watercolor Style
- **视觉特征**: 色彩晕染、透明叠加效果，有水渍边缘和颜料扩散感。色调柔和，画面有留白，整体氛围温柔治愈。
- **关键区分点**: 与手绘风的区别——水彩风核心是晕染和透明感，而非线条；颜色边缘模糊而非锐利。
- **代表博主**: 文艺情感类账号常用
- **生成方式**: Midjourney / Stable Diffusion，提示词加水彩风格关键词
- **风格关键词**: `watercolor painting, soft washes, wet-on-wet technique, transparent layers, bleeding edges, delicate watercolor illustration`

### 2.3 扁平矢量插画

- **英文名**: Flat Vector Illustration
- **视觉特征**: 几何化造型，无渐变或仅少量渐变，色块填充，边缘锐利。人物比例夸张（大头小身），配色鲜明统一。
- **关键区分点**: 与手绘风的区别——扁平风无笔触质感，边缘干净利落；与图标类的区别——扁平插画有场景和细节，不只是符号。
- **代表博主**: 科普类、职场类账号常用
- **生成方式**: Midjourney / AI + Illustrator修图；或直接Illustrator/Figma手工制作
- **风格关键词**: `flat vector illustration, geometric shapes, bold colors, minimal shading, clean edges, modern flat design, 2D character`

### 2.4 日系/韩系插画

- **英文名**: Japanese/Korean Anime Style
- **视觉特征**: 大眼睛、精致五官、发丝细腻，色彩柔和偏粉/蓝/紫。日系偏动漫感，韩系偏时尚写实。有光影渐变和细节装饰。
- **关键区分点**: 与扁平插画的区别——日韩风有丰富的光影和细节；与手绘风的区别——日韩风更精致规整，有明确的动漫/时尚美学。
- **代表博主**: 二次元、美妆、穿搭类账号
- **生成方式**: Stable Diffusion (AnimagineXL, NovelAI模型) / Midjourney niji模式
- **风格关键词**: `anime style illustration, soft shading, cel shading, pastel colors, detailed hair, sparkling eyes, Japanese anime art`

### 2.5 国潮插画

- **英文名**: Chinese Traditional / Guochao Style
- **视觉特征**: 融合中国传统元素（祥云、龙凤、古建筑、水墨）与现代设计，色彩以红金黑为主或用传统色谱。有书法字体和传统纹样。
- **关键区分点**: 与水彩风的区别——国潮有明确的中国传统符号；与扁平插画的区别——国潮强调文化元素和东方美学。
- **代表博主**: 国风文化类、非遗类账号
- **生成方式**: Midjourney / Stable Diffusion + 后期合成
- **风格关键词**: `Chinese traditional art, guochao style, ink wash painting, red and gold palette, oriental aesthetic, traditional Chinese patterns, cultural illustration`

---

## 三、图标类 (Icon / Symbol)  ⚠️ 重点分类

> **这是之前踩坑最多的地方！三种图标风格容易混淆，必须严格区分。**

### 3.1 实心剪影图标

- **英文名**: Pictogram / Silhouette Icon
- **视觉特征**: 公共标识风格，人物为实心填充的剪影。圆形头部（实心圆），身体和四肢都是实心色块填充，无描边线条。类似厕所标志、机场指示牌、奥运会运动图标。整体简洁、高辨识度。
- **关键区分点**: **核心区别是fill实心，不是stroke线条！** 与火柴人的区别——剪影是填充色块，火柴人是线条；与简笔画的区别——剪影是规整的几何形，简笔画有手绘感。
- **代表博主**: 心知说
- **生成方式**: SVG代码直接生成 / Figma设计 / Remotion渲染
- **风格关键词**: `pictogram, silhouette icon, public signage style, solid fill figure, ISO 7001 style, universal symbol`
- **SVG模板**:

```svg
<!-- 实心剪影人物 - Pictogram Style -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 400" width="200" height="400">
  <!-- 头部：实心圆 -->
  <circle cx="100" cy="50" r="35" fill="#333333" />
  <!-- 身体：实心矩形/梯形 -->
  <path d="M65 95 L135 95 L125 230 L75 230 Z" fill="#333333" />
  <!-- 左臂：实心色块 -->
  <path d="M65 95 L20 180 L40 190 L75 130 Z" fill="#333333" />
  <!-- 右臂：实心色块 -->
  <path d="M135 95 L180 180 L160 190 L125 130 Z" fill="#333333" />
  <!-- 左腿：实心色块 -->
  <path d="M75 230 L55 380 L80 380 L95 230 Z" fill="#333333" />
  <!-- 右腿：实心色块 -->
  <path d="M125 230 L145 380 L120 380 L105 230 Z" fill="#333333" />
</svg>
```

### 3.2 线条火柴人

- **英文名**: Stick Figure
- **视觉特征**: 极简线条构成，圆形头部（stroke描边，不填充），一条竖线身体，线条四肢。线条粗细均匀（2-4px），整体像小孩画画的火柴人。
- **关键区分点**: **核心区别是stroke线条，不是fill实心！** 与剪影的区别——火柴人是线条，剪影是填充色块；与简笔画的区别——火柴人线条规整均匀，简笔画线条有手绘抖动感。
- **代表博主**: 暂无明确代表
- **生成方式**: SVG代码直接生成 / Remotion程序化渲染
- **风格关键词**: `stick figure, line drawing, minimal character, thin stroke figure`
- **SVG模板**:

```svg
<!-- 线条火柴人 - Stick Figure Style -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 400" width="200" height="400">
  <!-- 头部：空心圆（stroke描边） -->
  <circle cx="100" cy="50" r="30" fill="none" stroke="#333333" stroke-width="4" />
  <!-- 身体：竖线 -->
  <line x1="100" y1="80" x2="100" y2="230" stroke="#333333" stroke-width="4" stroke-linecap="round" />
  <!-- 左臂 -->
  <line x1="100" y1="120" x2="40" y2="180" stroke="#333333" stroke-width="4" stroke-linecap="round" />
  <!-- 右臂 -->
  <line x1="100" y1="120" x2="160" y2="180" stroke="#333333" stroke-width="4" stroke-linecap="round" />
  <!-- 左腿 -->
  <line x1="100" y1="230" x2="50" y2="370" stroke="#333333" stroke-width="4" stroke-linecap="round" />
  <!-- 右腿 -->
  <line x1="100" y1="230" x2="150" y2="370" stroke="#333333" stroke-width="4" stroke-linecap="round" />
</svg>
```

### 3.3 简笔画

- **英文名**: Sketch / Doodle
- **视觉特征**: 手绘感线条，粗细不均匀，有抖动和不规则感。可能有简单的颜色填充。比火柴人有更多细节（衣服轮廓、头发等），但比插画简单很多。整体感觉像在白纸上随手画的。
- **关键区分点**: 与火柴人的区别——简笔画有更多细节和手绘不规则感；与手绘插画的区别——简笔画更简单粗糙，没有精致的光影和细节。
- **代表博主**: 手账类、教育类部分账号
- **生成方式**: Stable Diffusion (线稿模型) / 手绘板绘制 / SVG + 手绘滤镜
- **风格关键词**: `doodle, sketch drawing, hand-drawn style, rough lines, casual illustration, notebook doodle`
- **SVG模板**:

```svg
<!-- 简笔画人物 - Doodle Style（用曲线模拟手绘感） -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 400" width="200" height="400">
  <!-- 头部：略不规则的圆 -->
  <ellipse cx="100" cy="55" rx="32" ry="35" fill="none" stroke="#333333" stroke-width="3" />
  <!-- 眼睛 -->
  <circle cx="88" cy="50" r="3" fill="#333333" />
  <circle cx="112" cy="50" r="3" fill="#333333" />
  <!-- 嘴巴 -->
  <path d="M90 65 Q100 75 110 65" fill="none" stroke="#333333" stroke-width="2" />
  <!-- 身体轮廓 -->
  <path d="M80 90 Q78 160 75 230 L125 230 Q122 160 120 90 Z" fill="none" stroke="#333333" stroke-width="3" />
  <!-- 左臂 -->
  <path d="M80 100 Q50 140 35 180" fill="none" stroke="#333333" stroke-width="3" stroke-linecap="round" />
  <!-- 右臂 -->
  <path d="M120 100 Q150 140 165 180" fill="none" stroke="#333333" stroke-width="3" stroke-linecap="round" />
  <!-- 左腿 -->
  <path d="M85 230 Q75 300 60 370" fill="none" stroke="#333333" stroke-width="3" stroke-linecap="round" />
  <!-- 右腿 -->
  <path d="M115 230 Q125 300 140 370" fill="none" stroke="#333333" stroke-width="3" stroke-linecap="round" />
</svg>
```

### ⚠️ 三种图标风格对比表

| 特征 | 实心剪影 (Pictogram) | 线条火柴人 (Stick Figure) | 简笔画 (Doodle) |
|------|---------------------|-------------------------|-----------------|
| **头部** | 实心圆 `fill` | 空心圆 `stroke` | 略不规则椭圆 `stroke` |
| **身体** | 实心色块/梯形 | 单根竖线 | 轮廓线条（有形状） |
| **四肢** | 实心色块 | 单根线条 | 曲线（有粗细变化） |
| **填充方式** | `fill` 实心填充 | `stroke` 仅描边 | `stroke` 描边 + 可选填充 |
| **线条粗细** | 无线条（色块边缘） | 均匀（2-4px） | 不均匀（有手绘感） |
| **细节程度** | 无（纯轮廓） | 极少 | 有（五官、衣服轮廓） |
| **整体感觉** | 厕所标志/机场指示牌 | 小孩画的火柴人 | 随手涂鸦/手账画 |
| **CSS关键属性** | `fill: #333` | `stroke: #333; fill: none` | `stroke: #333; fill: none/可选色` |

---

## 四、动画类 (Animation)

### 4.1 MG动画

- **英文名**: Motion Graphics
- **视觉特征**: 图形元素（文字、形状、图标）有动态运动效果——缩放、旋转、弹跳、路径动画。色彩鲜明，节奏感强，常配合BGM节奏做动效。
- **关键区分点**: 与图文类的区别——MG动画有明确的运动效果和转场；与3D的区别——MG通常是2D平面元素。
- **代表博主**: 科普类、商业宣传类账号
- **生成方式**: After Effects / Remotion（程序化） / Lottie动画
- **风格关键词**: `motion graphics, animated infographic, kinetic typography, dynamic shapes`

### 4.2 3D渲染

- **英文名**: 3D Rendering
- **视觉特征**: 立体建模场景/角色，有光影、材质、透视效果。画面有明显的三维深度感。可以是写实风也可以是卡通风3D。
- **关键区分点**: 与MG动画的区别——3D有立体感和光影；与实拍的区别——3D是建模渲染，非真实拍摄。
- **代表博主**: 科技类、游戏类账号
- **生成方式**: Blender / C4D / Unreal Engine / 3D AI生成工具
- **风格关键词**: `3D render, CGI, three-dimensional, realistic lighting, 3D character, isometric 3D`

### 4.3 像素风

- **英文名**: Pixel Art
- **视觉特征**: 方格像素构成画面，复古游戏机风格（8-bit/16-bit），色彩有限但鲜明，有明显的锯齿边缘。
- **关键区分点**: 与扁平插画的区别——像素风有明显的方格感和复古游戏美学；与MG动画的区别——像素风是特定的视觉风格。
- **代表博主**: 游戏怀旧类、创意类账号
- **生成方式**: Aseprite / Piskel / Stable Diffusion (pixel art模型) / Remotion渲染
- **风格关键词**: `pixel art, 8-bit style, retro game, pixelated, 16-bit graphics`

### 4.4 白板动画

- **英文名**: Whiteboard Animation
- **视觉特征**: 白色背景上手绘线条逐渐出现的动画效果，模拟在白板上画画的过程。通常配合讲解，有"手"在画面中绘画的效果。
- **关键区分点**: 与简笔画的区别——白板动画强调"绘画过程"的动态呈现；与MG动画的区别——白板动画风格更素，以黑白线条为主。
- **代表博主**: 教育类、知识讲解类账号
- **生成方式**: VideoScribe / Doodly / After Effects手绘效果 / FFmpeg逐帧合成
- **风格关键词**: `whiteboard animation, hand-drawn process, sketch reveal, educational drawing`

### 4.5 定格动画

- **英文名**: Stop Motion
- **视觉特征**: 逐帧拍摄实物（黏土、纸片、积木等），有略微跳帧的运动感。材质有实物质感，光影真实。帧率较低（12-15fps），动作有独特的"一顿一顿"感。
- **关键区分点**: 与实拍的区别——定格是逐帧拍摄非连续录制；与3D渲染的区别——定格用真实材料，不是电脑建模。
- **代表博主**: 手工类、创意类账号
- **生成方式**: 相机逐帧拍摄 + Dragonframe / PR合成
- **风格关键词**: `stop motion, claymation, frame-by-frame, handmade animation`

---

## 五、图文类 (Text & Image)

### 5.1 纯文字卡片

- **英文名**: Text Card
- **视觉特征**: 以文字为绝对主体，大字号标题+正文排列，背景纯色或简单渐变。可能有emoji装饰。翻页形式呈现多张文字卡。
- **关键区分点**: 与PPT风格的区别——文字卡片更简洁，没有复杂排版和图表；与口播的区别——完全没有人物。
- **代表博主**: 情感语录类、知识点总结类账号
- **生成方式**: Canva / HTML+截图 / Remotion生成 / FFmpeg图片序列
- **风格关键词**: `text card, typography design, minimal text layout, quote card`

### 5.2 信息图

- **英文名**: Infographic
- **视觉特征**: 数据可视化+图文排版，有图表（柱状图、饼图、流程图）、图标、数字标注。信息密度高，排版结构化，配色统一。
- **关键区分点**: 与PPT风格的区别——信息图更注重数据可视化和视觉设计；与MG动画的区别——信息图是静态的。
- **代表博主**: 财经数据类、行业分析类账号
- **生成方式**: Figma / Canva / HTML+CSS渲染截图 / D3.js生成
- **风格关键词**: `infographic, data visualization, chart design, statistical graphics`

### 5.3 PPT风格

- **英文名**: Slide / Presentation Style
- **视觉特征**: 类似演示文稿的排版，有标题+要点+配图的固定版式，每页一个知识点。有统一的模板和配色方案。
- **关键区分点**: 与文字卡片的区别——PPT有更复杂的排版（分栏、配图、列表）；与信息图的区别——PPT更偏文字讲解，数据图表少。
- **代表博主**: 职场技能类、教育课程类账号
- **生成方式**: PowerPoint / Keynote / Canva / HTML模板渲染
- **风格关键词**: `presentation slide, keynote style, lecture format, educational slide`

### 5.4 截图/对话截图

- **英文名**: Screenshot / Chat Screenshot
- **视觉特征**: 手机/电脑截图风格，有系统UI元素（状态栏、对话气泡、输入框）。对话截图有明显的聊天界面特征（微信/iMessage风格气泡）。
- **关键区分点**: 与文字卡片的区别——截图有明确的系统UI框架；真实性感更强，像"随手截的"。
- **代表博主**: 搞笑聊天类、社交话题类账号
- **生成方式**: 手机截图 / 对话生成器网站 / HTML模拟聊天UI + 截图
- **风格关键词**: `chat screenshot, message bubble, phone UI mockup, conversation screenshot`

---

## 快速匹配决策树

分析一个抖音视频/博主的视觉风格时，按以下顺序判断：

```
开始分析
│
├─ Q1: 画面中有真人出镜吗？
│  ├─ YES → 【实拍类】
│  │  ├─ 固定机位对镜头讲话？→ 真人出镜口播
│  │  ├─ 主体是产品特写？→ 产品实拍
│  │  ├─ 多场景移动拍摄记录生活？→ Vlog日常
│  │  └─ 街头采访路人？→ 街拍采访
│  │
│  └─ NO → 继续 Q2
│
├─ Q2: 画面有手绘/艺术/插画质感吗？
│  ├─ YES → 【插画类】
│  │  ├─ 有铅笔/马克笔笔触？→ 手绘风
│  │  ├─ 有水彩晕染效果？→ 水彩风
│  │  ├─ 干净的色块，无渐变，几何化？→ 扁平矢量插画
│  │  ├─ 大眼动漫风？→ 日系/韩系插画
│  │  └─ 中国传统元素（祥云/龙/水墨）？→ 国潮插画
│  │
│  └─ NO → 继续 Q3
│
├─ Q3: 画面是简约图形/符号/人物图标吗？
│  ├─ YES → 【图标类】⚠️ 仔细区分！
│  │  ├─ 人物是实心色块填充（像厕所标志）？→ 实心剪影图标 (Pictogram)
│  │  ├─ 人物是细线条+空心圆头？→ 线条火柴人 (Stick Figure)
│  │  └─ 人物线条不规则有手绘感？→ 简笔画 (Doodle)
│  │
│  └─ NO → 继续 Q4
│
├─ Q4: 画面元素有运动/动效/转场吗？
│  ├─ YES → 【动画类】
│  │  ├─ 2D图形运动（缩放旋转弹跳）？→ MG动画
│  │  ├─ 3D立体场景/角色？→ 3D渲染
│  │  ├─ 方格像素复古游戏感？→ 像素风
│  │  ├─ 白色背景上线条逐渐出现？→ 白板动画
│  │  └─ 实物逐帧拍摄（有顿帧感）？→ 定格动画
│  │
│  └─ NO → 继续 Q5
│
└─ Q5: 画面以文字为主吗？
   ├─ YES → 【图文类】
   │  ├─ 纯文字大字报？→ 纯文字卡片
   │  ├─ 有图表/数据可视化？→ 信息图
   │  ├─ 像PPT演示文稿？→ PPT风格
   │  └─ 有手机UI/聊天气泡？→ 截图/对话截图
   │
   └─ NO → 可能是混合风格，取主要特征归类
```

### 特殊情况处理

- **混合风格**：如「口播+PPT」→ 以画面占比大的为主类，备注副类型
- **AI生成的"伪实拍"**：用数字人/AI换脸的 → 归入实拍类，备注"AI生成"
- **带动效的图文**：轻微动效（文字淡入）→ 图文类；大量动效 → 动画类

---

*本文档持续更新。分析新博主时如发现新的风格子类，请补充。*
