#!/usr/bin/env python3
"""
小红书笔记搜索脚本

功能：
    根据关键词搜索小红书笔记，支持多页获取，输出 JSON 格式数据

使用方法：
    python xhs_search.py "关键词" --pages 3 --output notes.json
    python xhs_search.py "AI绘画" --pages 2 --sort popularity_descending

依赖安装：
    pip install requests
"""

import argparse
import json
import sys
from dataclasses import dataclass

import requests


# ==================== 配置 ====================

DAJIALA_API_URL = "https://www.dajiala.com/fbmain/monitor/v3/xhs"
DAJIALA_API_KEY = ""


# ==================== 数据模型 ====================

@dataclass
class Author:
    user_id: str
    nickname: str
    avatar: str


@dataclass
class XiaohongshuNote:
    id: str
    title: str
    cover: str
    type: str
    liked_count: int
    collected_count: int
    comment_count: int
    shared_count: int
    author: Author
    images: list[str]
    engagement_rate: float

    @property
    def url(self) -> str:
        return f"https://www.xiaohongshu.com/explore/{self.id}"

    @property
    def total_engagement(self) -> int:
        return self.liked_count + self.collected_count + self.comment_count

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "cover": self.cover,
            "type": self.type,
            "liked_count": self.liked_count,
            "collected_count": self.collected_count,
            "comment_count": self.comment_count,
            "shared_count": self.shared_count,
            "author": {
                "user_id": self.author.user_id,
                "nickname": self.author.nickname,
                "avatar": self.author.avatar,
            },
            "images": self.images,
            "engagement_rate": self.engagement_rate,
            "url": self.url,
            "total_engagement": self.total_engagement,
        }


# ==================== API 调用 ====================

def search_xiaohongshu_notes(
    keyword: str,
    page: int = 1,
    sort: str = "general",
    note_type: str = "all",
    note_time: str = "不限",
    note_range: str = "不限",
) -> dict:
    params = {
        "key": DAJIALA_API_KEY,
        "type": 1,
        "keyword": keyword,
        "page": page,
        "sort": sort,
        "note_type": note_type,
        "note_time": note_time,
        "note_range": note_range,
        "proxy": "",
    }

    response = requests.post(
        DAJIALA_API_URL,
        headers={"Content-Type": "application/json"},
        json=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def search_xiaohongshu_notes_multi_page(
    keyword: str,
    max_pages: int = 3,
    sort: str = "general",
    note_type: str = "all",
    note_time: str = "不限",
    note_range: str = "不限",
) -> dict:
    all_items = []
    first_page_data = None

    for page in range(1, max_pages + 1):
        print(f"正在获取第 {page}/{max_pages} 页...", file=sys.stderr)
        try:
            data = search_xiaohongshu_notes(
                keyword=keyword,
                page=page,
                sort=sort,
                note_type=note_type,
                note_time=note_time,
                note_range=note_range,
            )

            if page == 1:
                first_page_data = data

            items = data.get("items", [])
            all_items.extend(items)

            if not data.get("has_more", False):
                break

        except Exception as e:
            print(f"获取第 {page} 页失败: {e}", file=sys.stderr)
            if page == 1:
                raise
            continue

    if first_page_data:
        first_page_data["items"] = all_items
        return first_page_data

    return {"items": all_items, "code": 0, "has_more": False}


# ==================== 数据转换 ====================

def parse_count(value) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        value = value.strip()
        if value.endswith("万"):
            return int(float(value[:-1]) * 10000)
        try:
            return int(value)
        except ValueError:
            return 0
    return 0


def convert_to_xiaohongshu_note(item: dict) -> XiaohongshuNote | None:
    note_card = item.get("note_card")
    if not note_card:
        return None

    interact_info = note_card.get("interact_info", {})
    user_info = note_card.get("user", {})
    cover_info = note_card.get("cover", {})
    image_list = note_card.get("image_list", [])

    liked_count = parse_count(interact_info.get("liked_count", 0))
    collected_count = parse_count(interact_info.get("collected_count", 0))
    comment_count = parse_count(interact_info.get("comment_count", 0))
    shared_count = parse_count(interact_info.get("shared_count", 0))

    total_engagement = liked_count + collected_count + comment_count
    estimated_views = max(liked_count * 10, 1)
    engagement_rate = (total_engagement / estimated_views) * 100

    images = []
    for img in image_list:
        info_list = img.get("info_list", [])
        if info_list:
            url = info_list[0].get("url", "")
            if url:
                images.append(url)

    return XiaohongshuNote(
        id=item.get("id", ""),
        title=note_card.get("display_title", "无标题"),
        cover=cover_info.get("url_default", "") or cover_info.get("url_pre", ""),
        type=note_card.get("type", "image"),
        liked_count=liked_count,
        collected_count=collected_count,
        comment_count=comment_count,
        shared_count=shared_count,
        author=Author(
            user_id=user_info.get("user_id", ""),
            nickname=user_info.get("nickname", "") or user_info.get("nick_name", ""),
            avatar=user_info.get("avatar", ""),
        ),
        images=images,
        engagement_rate=engagement_rate,
    )


def convert_api_response(response: dict) -> list[XiaohongshuNote]:
    items = response.get("items", [])
    notes = []
    for item in items:
        note = convert_to_xiaohongshu_note(item)
        if note:
            notes.append(note)
    return notes


# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(description="小红书笔记搜索工具")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("--pages", type=int, default=2, help="获取页数（默认2，每页约20条）")
    parser.add_argument(
        "--sort",
        choices=["general", "popularity_descending", "time_descending"],
        default="general",
        help="排序方式",
    )
    parser.add_argument(
        "--type",
        choices=["all", "image", "video"],
        default="all",
        help="笔记类型",
    )
    parser.add_argument(
        "--time",
        choices=["不限", "一天内", "一周内", "一月内", "三月内"],
        default="不限",
        help="发布时间范围",
    )
    parser.add_argument(
        "--range",
        choices=["不限", "0-1000", "1000-5000", "5000-1w", "1w+"],
        default="不限",
        help="点赞数范围",
    )
    parser.add_argument("--output", "-o", help="输出到 JSON 文件")

    args = parser.parse_args()

    try:
        response = search_xiaohongshu_notes_multi_page(
            keyword=args.keyword,
            max_pages=args.pages,
            sort=args.sort,
            note_type=args.type,
            note_time=args.time,
            note_range=getattr(args, "range"),
        )
        notes = convert_api_response(response)
    except Exception as e:
        print(f"搜索失败: {e}", file=sys.stderr)
        sys.exit(1)

    output_data = {
        "keyword": args.keyword,
        "total_count": len(notes),
        "search_params": {
            "pages": args.pages,
            "sort": args.sort,
            "type": args.type,
            "time": args.time,
            "range": getattr(args, "range"),
        },
        "notes": [n.to_dict() for n in notes],
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {args.output}", file=sys.stderr)
    else:
        print(json.dumps(output_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
