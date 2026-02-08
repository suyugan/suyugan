import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

repos = [
    'KeygraphHQ/shannon',
    'openai/skills',
    'microsoft/litebox',
    'p-e-w/heretic',
    'obra/superpowers',
    'OpenBMB/MiniCPM-o',
    'aquasecurity/trivy',
    'wavetermdev/waveterm',
    'viarotel-org/escrcpy',
    'ComposioHQ/awesome-claude-skills',
    'likec4/likec4',
    'gitbutlerapp/gitbutler',
]

for repo in repos:
    try:
        req = urllib.request.Request(
            f'https://api.github.com/repos/{repo}',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            stars = data.get('stargazers_count', '?')
            lang = data.get('language', '?')
            created = data.get('created_at', '?')[:10]
            print(f'{repo}: stars={stars} | lang={lang} | created={created}')
    except Exception as e:
        print(f'{repo}: ERROR {e}')
