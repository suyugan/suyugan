#!/usr/bin/env python3
"""
Publish article to WeChat Official Account via API
"""
import sys
import json
import requests
from typing import Optional, List

API_URL = "https://wx.limyai.com/api/openapi/wechat-publish"

def publish_article(
    api_key: str,
    wechat_appid: str,
    title: str,
    content: str,
    summary: Optional[str] = None,
    cover_image: Optional[str] = None,
    main_images: Optional[List[str]] = None,
    author: Optional[str] = None,
    content_format: str = "markdown",
    article_type: str = "news"
) -> dict:
    """
    Publish article to WeChat Official Account

    Args:
        api_key: API key for authentication
        wechat_appid: WeChat Official Account AppID
        title: Article title (max 64 chars)
        content: Article content (markdown or HTML)
        summary: Article summary (max 120 chars, optional)
        cover_image: Cover image URL (optional, required for newspic without main_images)
        main_images: List of main image URLs (optional, max 20, required for newspic without cover_image)
        author: Author name (optional)
        content_format: Content format - "markdown" or "html" (default: markdown)
        article_type: Article type - "news" or "newspic" (default: news)

    Returns:
        dict with success status and publication data
    """
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "wechatAppid": wechat_appid,
        "title": title,
        "content": content,
        "contentFormat": content_format,
        "articleType": article_type
    }

    # Add optional fields if provided
    if summary:
        payload["summary"] = summary
    if cover_image:
        payload["coverImage"] = cover_image
    if main_images:
        payload["mainImages"] = main_images
    if author:
        payload["author"] = author

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 publish_article.py <json_config_file>", file=sys.stderr)
        print("JSON config should contain: api_key, wechat_appid, title, content, and optional fields", file=sys.stderr)
        sys.exit(1)

    config_file = sys.argv[1]

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading config file: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract required fields
    api_key = config.get("api_key")
    wechat_appid = config.get("wechat_appid")
    title = config.get("title")
    content = config.get("content")

    if not all([api_key, wechat_appid, title, content]):
        print("Missing required fields: api_key, wechat_appid, title, content", file=sys.stderr)
        sys.exit(1)

    # Extract optional fields
    result = publish_article(
        api_key=api_key,
        wechat_appid=wechat_appid,
        title=title,
        content=content,
        summary=config.get("summary"),
        cover_image=config.get("cover_image"),
        main_images=config.get("main_images"),
        author=config.get("author"),
        content_format=config.get("content_format", "markdown"),
        article_type=config.get("article_type", "news")
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if not result.get("success"):
        sys.exit(1)

if __name__ == "__main__":
    main()
