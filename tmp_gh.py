import json, sys, urllib.request, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=10).read())

# New repos this week with 100+ stars
print("=== NEW REPOS (created after 2026-02-10, 100+ stars) ===")
try:
    d = fetch("https://api.github.com/search/repositories?q=created:%3E2026-02-10+stars:%3E50&sort=stars&order=desc&per_page=15")
    for r in d.get("items", []):
        print(f"{r['full_name']} | ⭐{r['stargazers_count']} | {(r['description'] or 'N/A')[:120]} | {r['language'] or '-'}")
except Exception as e:
    print(f"Error: {e}")

# Top AI/LLM repos active today
print("\n=== AI/LLM ACTIVE TODAY ===")
try:
    d = fetch("https://api.github.com/search/repositories?q=topic:llm+pushed:%3E2026-02-16&sort=stars&order=desc&per_page=10")
    for r in d.get("items", []):
        print(f"{r['full_name']} | ⭐{r['stargazers_count']} | {(r['description'] or 'N/A')[:120]}")
except Exception as e:
    print(f"Error: {e}")

# Top dev tools active today
print("\n=== DEV TOOLS ACTIVE TODAY ===")
try:
    d = fetch("https://api.github.com/search/repositories?q=topic:developer-tools+pushed:%3E2026-02-16&sort=stars&order=desc&per_page=8")
    for r in d.get("items", []):
        print(f"{r['full_name']} | ⭐{r['stargazers_count']} | {(r['description'] or 'N/A')[:120]}")
except Exception as e:
    print(f"Error: {e}")
