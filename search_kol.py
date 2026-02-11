# -*- coding: utf-8 -*-
from duckduckgo_search import DDGS

queries = [
    "乔木 AI twitter 推特",
    "归藏 AI twitter 即刻",
    "宝玉 dotey AI"
]

with DDGS() as ddgs:
    for q in queries:
        print(f"=== {q} ===")
        results = list(ddgs.text(q, max_results=5))
        for r in results:
            print(r["title"])
            print(r["href"])
            print()
