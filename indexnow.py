#!/usr/bin/env python3
"""
indexnow.py — tells Bing (and other IndexNow search engines) which DocStory pages just changed,
so new interviews get crawled in days instead of weeks. Bing's index also feeds ChatGPT search.

Run by .github/workflows/indexnow.yml after each successful production deploy on Vercel:
    python3 indexnow.py --changed <old-commit> <new-commit>     # pages whose files changed
    python3 indexnow.py --all                                   # every page in sitemap.xml
Add --dry-run to print the URLs without sending anything.
"""
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import seo

ROOT = Path(__file__).parent
KEY = '114ff42d2d6463cb03a98ad82e412e19'          # proves we own the site: served at /<KEY>.txt
ENDPOINT = 'https://api.indexnow.org/indexnow'


def sitemap_urls():
    return re.findall(r'<loc>([^<]+)</loc>', (ROOT / 'sitemap.xml').read_text(encoding='utf-8'))


def changed_urls(old, new):
    files = subprocess.run(['git', 'diff', '--name-only', old, new], capture_output=True, text=True,
                           check=True, cwd=ROOT).stdout.split()
    listed = set(sitemap_urls())
    urls = [seo.url(f) for f in files if f == 'index.html' or f.endswith('/index.html')]
    return [u for u in urls if u in listed]


def main(argv):
    dry = '--dry-run' in argv
    argv = [a for a in argv if a != '--dry-run']
    if argv[:1] == ['--all']:
        urls = sitemap_urls()
    elif argv[:1] == ['--changed'] and len(argv) == 3:
        urls = changed_urls(argv[1], argv[2])
    else:
        sys.exit(__doc__)
    if not urls:
        print('IndexNow: no listed pages changed, nothing to send.')
        return
    print(f'IndexNow: {len(urls)} URL(s)')
    for u in urls:
        print('  ' + u)
    if dry:
        return
    host = seo.SITE_URL.split('://', 1)[1]
    body = json.dumps({'host': host, 'key': KEY, 'keyLocation': f'{seo.SITE_URL}/{KEY}.txt',
                       'urlList': urls[:10000]}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f'IndexNow: HTTP {r.status} (200 or 202 means accepted)')


if __name__ == '__main__':
    main(sys.argv[1:])
