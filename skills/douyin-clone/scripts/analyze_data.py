# -*- coding: utf-8 -*-
"""
自动数据统计分析（纯数据，不含AI观点）。
读取videos.json和转录文本，输出data_report.md。
"""

import argparse
import collections
import glob
import json
import os
import re
import sys
from datetime import datetime


def load_videos(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def basic_stats(videos):
    """基础数据统计"""
    stats = {"digg_count": [], "comment_count": [], "share_count": [], "collect_count": []}
    for v in videos:
        s = v.get("statistics", {})
        for key in stats:
            stats[key].append(s.get(key, 0))

    lines = ["## 📊 基础数据统计\n"]
    labels = {"digg_count": "❤️ 点赞", "comment_count": "💬 评论", "share_count": "🔄 分享", "collect_count": "⭐ 收藏"}
    lines.append("| 指标 | 总计 | 平均 | 最高 | 中位数 |")
    lines.append("|------|------|------|------|--------|")
    for key, label in labels.items():
        vals = stats[key]
        total = sum(vals)
        avg = total // len(vals) if vals else 0
        max_val = max(vals) if vals else 0
        sorted_vals = sorted(vals)
        median = sorted_vals[len(sorted_vals)//2] if sorted_vals else 0
        lines.append(f"| {label} | {total:,} | {avg:,} | {max_val:,} | {median:,} |")
    return "\n".join(lines)


def tag_stats(videos, top_n=20):
    """高频标签统计"""
    counter = collections.Counter()
    for v in videos:
        for tag in v.get("text_extra", []):
            if tag:
                counter[tag] += 1

    lines = [f"\n## 🏷️ 高频标签 Top{top_n}\n"]
    lines.append("| 排名 | 标签 | 出现次数 |")
    lines.append("|------|------|----------|")
    for i, (tag, count) in enumerate(counter.most_common(top_n), 1):
        lines.append(f"| {i} | #{tag} | {count} |")
    return "\n".join(lines)


def title_patterns(videos):
    """标题模式分类"""
    patterns = {"疑问句": 0, "量化型": 0, "对比型": 0, "其他": 0}
    for v in videos:
        desc = v.get("desc", "")
        if re.search(r'[？?吗呢怎么为什么如何]', desc):
            patterns["疑问句"] += 1
        elif re.search(r'\d+[个条种件步招]', desc):
            patterns["量化型"] += 1
        elif re.search(r'[vs对比还是不如]', desc, re.IGNORECASE):
            patterns["对比型"] += 1
        else:
            patterns["其他"] += 1

    lines = ["\n## 📝 标题模式分类\n"]
    lines.append("| 模式 | 数量 | 占比 |")
    lines.append("|------|------|------|")
    total = len(videos) or 1
    for pattern, count in sorted(patterns.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        lines.append(f"| {pattern} | {count} | {pct:.1f}% |")
    return "\n".join(lines)


def duration_stats(videos):
    """时长分布"""
    buckets = {"0-15秒": 0, "15-30秒": 0, "30-60秒": 0, "1-3分钟": 0, "3分钟+": 0}
    for v in videos:
        dur = v.get("duration", 0)
        if dur <= 0:
            continue
        # duration可能是毫秒
        if dur > 1000:
            dur = dur / 1000
        if dur <= 15:
            buckets["0-15秒"] += 1
        elif dur <= 30:
            buckets["15-30秒"] += 1
        elif dur <= 60:
            buckets["30-60秒"] += 1
        elif dur <= 180:
            buckets["1-3分钟"] += 1
        else:
            buckets["3分钟+"] += 1

    lines = ["\n## ⏱️ 时长分布\n"]
    lines.append("| 时长区间 | 数量 | 占比 |")
    lines.append("|----------|------|------|")
    total = sum(buckets.values()) or 1
    for bucket, count in buckets.items():
        pct = count / total * 100
        lines.append(f"| {bucket} | {count} | {pct:.1f}% |")
    return "\n".join(lines)


def publish_frequency(videos):
    """发布频率统计"""
    monthly = collections.Counter()
    weekday = collections.Counter()
    hourly = collections.Counter()
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

    for v in videos:
        ts = v.get("create_time", 0)
        if ts <= 0:
            continue
        dt = datetime.fromtimestamp(ts)
        monthly[dt.strftime("%Y-%m")] += 1
        weekday[weekday_names[dt.weekday()]] += 1
        hourly[f"{dt.hour:02d}:00"] += 1

    lines = ["\n## 📅 发布频率\n"]

    # 月度
    lines.append("### 月度发布\n")
    lines.append("| 月份 | 发布数 |")
    lines.append("|------|--------|")
    for month, count in sorted(monthly.items()):
        lines.append(f"| {month} | {count} |")

    # 星期
    lines.append("\n### 星期分布\n")
    lines.append("| 星期 | 发布数 |")
    lines.append("|------|--------|")
    for day in weekday_names:
        lines.append(f"| {day} | {weekday.get(day, 0)} |")

    # 时段
    lines.append("\n### 时段分布\n")
    lines.append("| 时段 | 发布数 |")
    lines.append("|------|--------|")
    for hour in sorted(hourly.keys()):
        lines.append(f"| {hour} | {hourly[hour]} |")

    return "\n".join(lines)


def word_frequency(base_dir, top_n=30):
    """高频词统计（jieba分词）"""
    try:
        import jieba
    except ImportError:
        return "\n## 📖 高频词统计\n\n⚠️ 需要安装 jieba: pip install jieba\n"

    all_text = ""
    transcript_files = glob.glob(os.path.join(base_dir, "*/transcript.txt"))
    if not transcript_files:
        return "\n## 📖 高频词统计\n\n⚠️ 未找到转录文件\n"

    for tf in transcript_files:
        with open(tf, "r", encoding="utf-8") as f:
            all_text += f.read() + "\n"

    # 分词
    words = jieba.cut(all_text)
    # 过滤停用词和短词
    stopwords = set("的了是在我你他她它们这那个一不会有就也都还要让被把给对说到着得很太多少大小好坏上下来去过从和与及或但如果因为所以虽然可是然后于是就是因此而且并且或者可以不是没有什么怎么为什么哪里那里这里".replace("", " ").split() + list("，。！？、；：""''（）【】《》…—"))
    counter = collections.Counter()
    for w in words:
        w = w.strip()
        if len(w) >= 2 and w not in stopwords:
            counter[w] += 1

    lines = [f"\n## 📖 高频词统计（Top{top_n}）\n"]
    lines.append(f"共分析 {len(transcript_files)} 个转录文件\n")
    lines.append("| 排名 | 词语 | 出现次数 |")
    lines.append("|------|------|----------|")
    for i, (word, count) in enumerate(counter.most_common(top_n), 1):
        lines.append(f"| {i} | {word} | {count} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="自动数据统计分析（纯数据，不含AI观点）")
    parser.add_argument("-i", "--input", default="videos.json", help="videos.json路径")
    parser.add_argument("-d", "--dir", default=".", help="视频数据根目录（含转录文件）")
    parser.add_argument("-o", "--output", default="data_report.md", help="输出报告路径（默认 data_report.md）")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ 文件不存在: {args.input}")
        sys.exit(1)

    videos = load_videos(args.input)
    author = videos[0].get("author", {}).get("nickname", "未知") if videos else "未知"
    print(f"📊 分析博主: {author}，共 {len(videos)} 个视频")

    sections = [
        f"# 📊 数据统计报告 - {author}\n",
        f"视频总数: {len(videos)}\n",
        basic_stats(videos),
        tag_stats(videos),
        title_patterns(videos),
        duration_stats(videos),
        publish_frequency(videos),
        word_frequency(args.dir),
    ]

    report = "\n".join(sections)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ 报告已保存到 {args.output}")


if __name__ == "__main__":
    main()
