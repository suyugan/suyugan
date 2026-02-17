<!-- 本文件是 douyin-clone 技能的子文件，完整流程见 ../SKILL.md -->
<!-- phase5c: Remotion动画生成（content_type=动画模式时使用） -->

## 5.1c Remotion动画生成（动画模式）

**适用于：火柴人、简笔画、线条动画、MG动画等风格的博主。**

### 适用场景
- 火柴人动画（SVG骨骼+关节角度控制）
- 简笔画逐笔绘制效果
- 线条动画/白板动画
- 数据可视化动效
- 文字逐字/逐行出现动效

### 流程

#### 步骤1：分析对标视频动画风格
从抽帧中提取动画特征（线条粗细、颜色、背景色、人物造型、运动方式、转场方式），写入 `style_template.json`：
```json
{
  "content_type": "动画模式",
  "animation_style": {
    "character_type": "火柴人",
    "line_color": "#FFFFFF",
    "line_width": 3,
    "bg_color": "#1a1a2e",
    "accent_color": "#e94560",
    "motion_style": "简洁流畅",
    "transition": "淡入淡出",
    "text_animation": "逐字出现"
  }
}
```

#### 步骤2：读取段落动画描述
从阶段4B生成的 `prompts.json` 读取 `animation_desc`、`key_actions`、`duration_sec`、`transition_to_next` 等字段。

#### 步骤3：Remotion项目生成
技能文档参考：`skills/remotion-video/SKILL.md`

```
1. 初始化项目：D:\video-analysis\output\{主题}\remotion\
2. 为每个场景创建React组件：src/scenes/Scene01.tsx ~ SceneXX.tsx
   - SVG绘制人物/场景
   - useCurrentFrame() + interpolate() 控制动画
3. 主组件 Composition 按时间线串联
4. 渲染：npx remotion render src/index.ts Main --output video_only.mp4
```

**火柴人SVG模板**：
```tsx
const StickMan = ({ x, y, headTilt, armAngle, legAngle, emotion }) => (
  <g transform={`translate(${x}, ${y})`}>
    <circle cx={0} cy={-60} r={15} fill="none" stroke="white" strokeWidth={3} />
    {emotion === 'sad' && <>
      <line x1={-5} y1={-65} x2={-3} y2={-63} stroke="white" strokeWidth={2} />
      <line x1={5} y1={-65} x2={3} y2={-63} stroke="white" strokeWidth={2} />
      <path d="M -5,-55 Q 0,-58 5,-55" fill="none" stroke="white" strokeWidth={2} />
    </>}
    <line x1={0} y1={-45} x2={0} y2={0} stroke="white" strokeWidth={3} />
    <line x1={0} y1={-35} x2={-25} y2={-35 + armAngle} stroke="white" strokeWidth={3} />
    <line x1={0} y1={-35} x2={25} y2={-35 + armAngle} stroke="white" strokeWidth={3} />
    <line x1={0} y1={0} x2={-20} y2={30 + legAngle} stroke="white" strokeWidth={3} />
    <line x1={0} y1={0} x2={20} y2={30 + legAngle} stroke="white" strokeWidth={3} />
  </g>
);
```

**动画插值**：
```tsx
const frame = useCurrentFrame();
const fps = useVideoConfig().fps;
const y = interpolate(frame, [0, fps * 3], [200, 280], { extrapolateRight: 'clamp' });
const armAngle = interpolate(frame, [0, fps * 2], [0, 20], { extrapolateRight: 'clamp' });
```

#### 步骤4：合成完整视频
```
1. Remotion渲染 → video_only.mp4
2. 混合TTS+BGM → mixed_audio.m4a
3. ffmpeg合并：ffmpeg -y -i video_only.mp4 -i mixed_audio.m4a -c:v copy -c:a aac -movflags +faststart raw_video.mp4
4. FunASR字幕 → subs.srt
5. 烧录字幕 → final.mp4
6. 上传腾讯云 → 交付
```

### 与配图模式的区别
| 环节 | 配图模式 | 动画模式 |
|------|---------|---------|
| 素材生成 | 即梦AI生图 | Remotion代码渲染 |
| 画面切换 | 静态图+Ken Burns | 连续动画自然过渡 |
| 风格控制 | 提示词+style_positive | SVG/CSS代码精确控制 |
| TTS/BGM/字幕 | 相同 | 相同 |
