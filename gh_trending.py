import urllib.request, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def search(q):
    url = f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page=10"
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    data = json.loads(urllib.request.urlopen(req, timeout=10).read())
    for r in data.get("items",[]):
        desc = (r['description'] or 'N/A')[:120]
        print(f"{r['full_name']} | *{r['stargazers_count']} | {desc} | {r['language']}")

print("=== NEW REPOS (created today) ===")
search("created:%3E2026-02-07")

print("\n=== AI/LLM HOT ===")
search("stars:%3E500+pushed:%3E2026-02-07+topic:llm")

print("\n=== TRENDING TOOLS ===")
search("stars:%3E1000+pushed:%3E2026-02-07+topic:developer-tools")
