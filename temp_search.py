# -*- coding: utf-8 -*-
from duckduckgo_search import DDGS

query = "淘宝闪购 抖音"
print(f"搜索: {query}\n")

with DDGS() as ddgs:
    results = list(ddgs.text(query, region='cn-zh', max_results=10))
    print(f"找到 {len(results)} 条结果\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}")
        print(f"   URL: {r['href']}")
        body = r['body'][:150] if len(r['body']) > 150 else r['body']
        print(f"   摘要: {body}")
        print()
