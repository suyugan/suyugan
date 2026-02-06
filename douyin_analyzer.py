#!/usr/bin/env python3
"""
抖音/TikTok 视频分析工具
- 解析视频元数据
- 下载视频
- 提取关键帧
- 音频转录 (Whisper)
- 生成分析报告
"""

import os
import sys
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path

# 配置
API_BASE = "http://localhost:18810"
OUTPUT_DIR = Path("./video_analysis")
WHISPER_MODEL = "base"  # tiny, base, small, medium, large

def get_video_data(url: str) -> dict:
    """通过 API 获取视频元数据"""
    print(f"📥 正在解析视频: {url}")
    resp = requests.get(f"{API_BASE}/api/hybrid/video_data", params={"url": url}, timeout=30)
    data = resp.json()
    if data.get("code") != 200:
        raise Exception(f"API 错误: {data}")
    return data["data"]

def download_video(video_data: dict, output_dir: Path) -> Path:
    """下载视频"""
    # 获取下载地址 (540p 平衡质量和速度)
    download_url = None
    for br in video_data.get("video", {}).get("bit_rate", []):
        if br.get("gear_name") == "normal_540_0":
            download_url = br["play_addr"]["url_list"][0]
            break
    
    if not download_url:
        # fallback to first available
        download_url = video_data["video"]["play_addr"]["url_list"][0]
    
    video_id = video_data["aweme_id"]
    video_path = output_dir / f"{video_id}.mp4"
    
    print(f"⬇️ 正在下载视频...")
    resp = requests.get(download_url, stream=True, timeout=60)
    with open(video_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"✅ 视频已保存: {video_path}")
    return video_path

def extract_keyframes(video_path: Path, output_dir: Path, interval: float = 2.0) -> list:
    """使用 ffmpeg 提取关键帧"""
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(exist_ok=True)
    
    print(f"🎞️ 正在提取关键帧 (每 {interval}s 一帧)...")
    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-vf", f"fps=1/{interval}",  # 每 interval 秒一帧
        "-q:v", "2",  # 高质量 JPEG
        str(frames_dir / "frame_%04d.jpg"),
        "-y"  # 覆盖已有文件
    ]
    subprocess.run(cmd, capture_output=True)
    
    frames = sorted(frames_dir.glob("frame_*.jpg"))
    print(f"✅ 提取了 {len(frames)} 个关键帧")
    return frames

def extract_audio(video_path: Path, output_dir: Path) -> Path:
    """提取音频"""
    audio_path = output_dir / "audio.wav"
    print("🔊 正在提取音频...")
    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        str(audio_path), "-y"
    ]
    subprocess.run(cmd, capture_output=True)
    print(f"✅ 音频已保存: {audio_path}")
    return audio_path

def transcribe_audio(audio_path: Path, model: str = "base") -> dict:
    """使用 Whisper 转录音频"""
    print(f"🎤 正在转录音频 (模型: {model})...")
    import whisper
    
    model_obj = whisper.load_model(model)
    result = model_obj.transcribe(str(audio_path), language="zh")
    
    print(f"✅ 转录完成")
    return result

def generate_xiaohongshu_copy(summary: str, desc: str, stats: dict) -> str:
    """生成小红书风格文案"""
    # 提取关键词作为标签
    keywords = []
    for word in ["男人", "女人", "吸引力", "心理", "情感", "穿搭", "技巧", "方法", "秘密", "法则"]:
        if word in summary or word in desc:
            keywords.append(word)
    
    # 生成文案
    copy = f"""✨ {desc[:30]}{'...' if len(desc) > 30 else ''} ✨

---

📖 **核心内容**

{summary[:500]}{'...' if len(summary) > 500 else ''}

---

💡 **关键要点**

• 观点一：掌握核心原则比技巧更重要
• 观点二：行动力决定结果
• 观点三：持续学习是成长的关键

---

🏷️ #{' #'.join(keywords[:5]) if keywords else '干货分享'} #知识分享 #成长笔记

💬 你觉得哪个观点最有启发？评论区聊聊~
"""
    return copy

def generate_cover_image(frames_dir: Path, output_dir: Path, title: str) -> Path:
    """使用ffmpeg生成带标题的封面图"""
    import glob
    
    # 选择中间位置的帧作为封面
    frames = sorted(frames_dir.glob("frame_*.jpg"))
    if not frames:
        return None
    
    # 选择1/3位置的帧（通常内容更丰富）
    cover_frame = frames[len(frames) // 3]
    cover_output = output_dir / "xiaohongshu_cover.jpg"
    
    # 截取标题前15个字符
    short_title = title[:15] + "..." if len(title) > 15 else title
    
    # 使用ffmpeg添加文字覆盖
    # 创建一个简单的封面：添加半透明底部条+白色文字
    cmd = [
        "ffmpeg", "-i", str(cover_frame),
        "-vf", (
            f"drawbox=x=0:y=ih-120:w=iw:h=120:color=black@0.6:t=fill,"
            f"drawtext=text='{short_title}':fontsize=36:fontcolor=white:"
            f"x=(w-text_w)/2:y=h-80:fontfile=C\\\\:/Windows/Fonts/msyh.ttc"
        ),
        "-y", str(cover_output)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, timeout=30)
        if cover_output.exists():
            return cover_output
    except:
        pass
    
    # 如果ffmpeg失败，直接复制原帧
    import shutil
    shutil.copy(cover_frame, cover_output)
    return cover_output

def generate_summary(transcript_text: str, desc: str) -> str:
    """生成500-1000字的内容概要"""
    # 基于转录文本提取关键内容
    text = transcript_text.strip()
    if not text:
        return "无法生成概要：转录文本为空"
    
    # 简单分段处理，提取核心内容
    sentences = []
    for sep in ['。', '，', '、', '\n']:
        text = text.replace(sep, '|')
    parts = [p.strip() for p in text.split('|') if len(p.strip()) > 5]
    
    # 取前面的核心内容作为概要基础
    summary_parts = parts[:50] if len(parts) > 50 else parts
    summary_text = '。'.join(summary_parts)
    
    # 控制在500-1000字
    if len(summary_text) > 1000:
        summary_text = summary_text[:1000] + "..."
    elif len(summary_text) < 200:
        summary_text = transcript_text[:1000] + "..." if len(transcript_text) > 1000 else transcript_text
    
    return summary_text

def generate_report(video_data: dict, transcript: dict, frames: list, output_dir: Path) -> Path:
    """生成分析报告"""
    report_path = output_dir / "report.md"
    
    # 提取关键信息
    desc = video_data.get("desc", "")
    author = video_data.get("author", {})
    stats = video_data.get("statistics", {})
    duration_ms = video_data.get("duration", 0)
    create_time = video_data.get("create_time", 0)
    
    # 商品信息
    anchor_info = video_data.get("anchor_info", {})
    product_info = None
    if anchor_info.get("extra"):
        try:
            extra = json.loads(anchor_info["extra"])
            if extra:
                product_info = extra[0]
        except:
            pass
    
    report = f"""# 视频分析报告

生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📹 视频信息

- **视频ID**: {video_data.get("aweme_id", "N/A")}
- **描述**: {desc}
- **作者**: {author.get("nickname", "N/A")} (@{author.get("unique_id", "N/A")})
- **时长**: {duration_ms / 1000:.1f} 秒
- **发布时间**: {datetime.fromtimestamp(create_time).strftime("%Y-%m-%d %H:%M") if create_time else "N/A"}

## 📊 数据统计

| 指标 | 数值 |
|------|------|
| 👍 点赞 | {stats.get("digg_count", 0):,} |
| 💬 评论 | {stats.get("comment_count", 0):,} |
| ⭐ 收藏 | {stats.get("collect_count", 0):,} |
| 🔄 分享 | {stats.get("share_count", 0):,} |

"""
    
    if product_info:
        price = product_info.get("price", 0) / 100
        sales = product_info.get("sales", 0)
        report += f"""## 🛒 关联商品

- **商品名称**: {product_info.get("title", "N/A")}
- **价格**: ¥{price:.2f}
- **销量**: {sales:,}
- **评价数**: {product_info.get("comment_count", 0):,}

"""

    report += f"""## 📝 内容概要

{generate_summary(transcript.get("text", ""), desc)}

## 🎤 音频转录

```
{transcript.get("text", "转录失败")}
```

### 分段转录

"""
    for seg in transcript.get("segments", []):
        start = seg["start"]
        end = seg["end"]
        text = seg["text"]
        report += f"- [{start:.1f}s - {end:.1f}s] {text}\n"
    
    report += f"""

## 🎞️ 关键帧

共提取 {len(frames)} 个关键帧，保存在 `frames/` 目录。

"""
    for i, frame in enumerate(frames[:5]):  # 只列出前5个
        report += f"- {frame.name}\n"
    if len(frames) > 5:
        report += f"- ... 等 {len(frames)} 个帧\n"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"📄 报告已生成: {report_path}")
    return report_path

def analyze_video(url: str, output_base: Path = OUTPUT_DIR) -> dict:
    """完整的视频分析流程"""
    # 1. 获取视频数据
    video_data = get_video_data(url)
    video_id = video_data["aweme_id"]
    
    # 2. 创建输出目录
    output_dir = output_base / video_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 3. 保存原始数据
    with open(output_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)
    
    # 4. 下载视频
    video_path = download_video(video_data, output_dir)
    
    # 5. 提取关键帧
    frames = extract_keyframes(video_path, output_dir)
    
    # 6. 提取音频并转录
    audio_path = extract_audio(video_path, output_dir)
    transcript = transcribe_audio(audio_path, WHISPER_MODEL)
    
    # 保存转录结果
    with open(output_dir / "transcript.json", "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)
    
    # 7. 生成报告
    report_path = generate_report(video_data, transcript, frames, output_dir)
    
    print(f"\n🎉 分析完成! 结果保存在: {output_dir}")
    
    summary = generate_summary(transcript.get("text", ""), video_data.get("desc", ""))
    
    # 8. 生成小红书文案
    stats = video_data.get("statistics", {})
    xhs_copy = generate_xiaohongshu_copy(summary, video_data.get("desc", ""), stats)
    with open(output_dir / "xiaohongshu.md", "w", encoding="utf-8") as f:
        f.write(xhs_copy)
    print(f"📱 小红书文案已生成: {output_dir / 'xiaohongshu.md'}")
    
    # 9. 生成封面图
    frames_dir = output_dir / "frames"
    cover_path = generate_cover_image(frames_dir, output_dir, video_data.get("desc", "视频内容"))
    if cover_path:
        print(f"🖼️ 封面图已生成: {cover_path}")
    
    return {
        "video_id": video_id,
        "output_dir": str(output_dir),
        "report": str(report_path),
        "frames_count": len(frames),
        "summary": summary,
        "xiaohongshu_copy": xhs_copy,
        "cover_image": str(cover_path) if cover_path else None,
        "transcript": transcript.get("text", "")
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python douyin_analyzer.py <抖音视频链接>")
        print("示例: python douyin_analyzer.py https://v.douyin.com/xxxxx/")
        sys.exit(1)
    
    url = sys.argv[1]
    result = analyze_video(url)
    print(json.dumps(result, ensure_ascii=False, indent=2))
