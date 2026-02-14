#!/usr/bin/env python3
"""
Free publish a draft article on WeChat Official Account.
Uses WeChat official API to submit a draft for free publishing.

Usage:
  python scripts/free_publish.py <media_id> [--appid XX --appsecret XX]

If appid/appsecret not provided, reads from environment or defaults.
"""
import sys
import json
import argparse
import requests

# Default credentials (苏煜淦公众号)
DEFAULT_APPID = "wx9a447fddc9ba6a59"
DEFAULT_APPSECRET = "REDACTED_WECHAT_SECRET"


def get_access_token(appid: str, appsecret: str) -> str:
    """Get WeChat API access token."""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={appsecret}"
    resp = requests.get(url)
    data = resp.json()
    if "access_token" not in data:
        raise Exception(f"Failed to get access_token: {data}")
    return data["access_token"]


def free_publish(access_token: str, media_id: str) -> dict:
    """Submit a draft for free publishing (发布)."""
    url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"
    payload = {"media_id": media_id}
    resp = requests.post(url, json=payload)
    return resp.json()


def get_publish_status(access_token: str, publish_id: str) -> dict:
    """Check free publish status."""
    url = f"https://api.weixin.qq.com/cgi-bin/freepublish/get?access_token={access_token}"
    payload = {"publish_id": publish_id}
    resp = requests.post(url, json=payload)
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Free publish WeChat draft")
    parser.add_argument("media_id", help="Draft media_id from publish_article.py")
    parser.add_argument("--appid", default=DEFAULT_APPID)
    parser.add_argument("--appsecret", default=DEFAULT_APPSECRET)
    parser.add_argument("--check", help="Check publish status by publish_id")
    args = parser.parse_args()

    print("Getting access token...")
    token = get_access_token(args.appid, args.appsecret)

    if args.check:
        print(f"Checking publish status for {args.check}...")
        result = get_publish_status(token, args.check)
    else:
        print(f"Submitting draft {args.media_id} for free publish...")
        result = free_publish(token, args.media_id)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result.get("errcode", 0) != 0:
        print(f"\nError: {result.get('errmsg', 'unknown')}", file=sys.stderr)
        sys.exit(1)
    else:
        publish_id = result.get("publish_id")
        if publish_id:
            print(f"\n✅ 已提交发布！publish_id: {publish_id}")
            print(f"可用以下命令查询发布状态：")
            print(f"  python scripts/free_publish.py {args.media_id} --check {publish_id}")


if __name__ == "__main__":
    main()
