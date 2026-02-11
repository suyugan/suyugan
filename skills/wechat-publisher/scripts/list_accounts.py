#!/usr/bin/env python3
"""
Fetch WeChat Official Account list via API
"""
import sys
import json
import requests

API_URL = "https://wx.limyai.com/api/openapi/wechat-accounts"

def list_accounts(api_key: str) -> dict:
    """
    Fetch all authorized WeChat Official Accounts

    Args:
        api_key: API key for authentication

    Returns:
        dict with success status and account data
    """
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 list_accounts.py <api_key>", file=sys.stderr)
        sys.exit(1)

    api_key = sys.argv[1]
    result = list_accounts(api_key)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if not result.get("success"):
        sys.exit(1)

if __name__ == "__main__":
    main()
