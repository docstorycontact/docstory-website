#!/usr/bin/env python3
"""
build_css.py — builds the site's Tailwind stylesheets into css/tw/<group>.css.

The pages used to load Tailwind's in-browser compiler (cdn.tailwindcss.com), which builds the CSS
on every visit. This script runs that same compiler once, in headless Chrome, and saves the result,
so visitors download a small finished stylesheet instead.

Each page type has its own Tailwind settings in tailwind/<group>.config.js. The script collects
every class-like word from the site's source (HTML, JS and the Python page templates), so classes
that JavaScript adds later (the signup box, form steps, directory cards) are included too.

Run it after changing classes or Tailwind settings, then rebuild the pages:
    python3 build_css.py && python3 build.py && python3 build_schools.py
Needs Google Chrome and an internet connection (to load the compiler once).
"""
import hashlib, json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).parent
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CDN = 'https://cdn.tailwindcss.com/3.4.17?plugins='
PLUGINS = 'forms,container-queries'
# The interview form styles its own inputs and dropdowns; the in-browser compiler never applied the forms
# plugin's base styles there, so leaving the plugin out keeps that page exactly as visitors saw it.
GROUP_PLUGINS = {'contribute-interview': 'container-queries'}
GROUPS = ['home', 'about', 'directory', 'contribute', 'contribute-interview', 'legal', 'schools', 'interviews']
SKIP_DIRS = {'.git', '.screenshots', 'docs', 'node_modules', 'interviews', 'schools', 'css', 'tailwind', 'content', 'doodles', 'images', 'brand_assets'}
SKIP_FILES = {'site-data.js', 'contribute-data.js', 'llms.txt', 'sitemap.xml'}
TOKEN = re.compile(r'^!?-?[a-z@\[][a-z0-9_\-:/.\[\]#%,()&>+~!*]*$', re.I)


def source_files():
    for p in ROOT.rglob('*'):
        rel = p.relative_to(ROOT)
        if p.is_file() and rel.parts[0] not in SKIP_DIRS and p.suffix in ('.html', '.js', '.py') and p.name not in SKIP_FILES:
            yield p
    # one generated page of each kind carries everything the Python templates can produce
    yield ROOT / 'schools' / 'uc-irvine-school-of-medicine' / 'index.html'
    yield ROOT / 'interviews' / 'rush-medical-college' / 'emily-he' / 'index.html'


def class_tokens():
    tokens = set()
    for p in source_files():
        text = p.read_text(encoding='utf-8', errors='ignore')
        for word in re.split(r'[\s"\'`<>{}=;]+', text):
            if 3 <= len(word) <= 100 and TOKEN.match(word) and not word.startswith(('http', '//', 'www.')):
                tokens.add(word)
    return sorted(tokens)


def compile_group(group, tokens):
    cfg = (ROOT / 'tailwind' / f'{group}.config.js').read_text(encoding='utf-8')
    page = (f'<!doctype html><html><head><meta charset="utf-8"><script src="{CDN}{GROUP_PLUGINS.get(group, PLUGINS)}"></script>'
            f'<script>{cfg}</script></head><body><div class="{" ".join(tokens)}"></div></body></html>')
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(page)
        path = f.name
    dom = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--virtual-time-budget=10000', '--dump-dom', 'file://' + path],
                         capture_output=True, text=True, timeout=120).stdout
    Path(path).unlink(missing_ok=True)
    styles = [s for s in re.findall(r'<style[^>]*>(.*?)</style>', dom, re.S) if '--tw-' in s]
    if not styles:
        sys.exit(f'build_css: Tailwind produced no CSS for {group} (offline, or Chrome missing?)')
    css = max(styles, key=len)
    css = css.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&').replace('&quot;', '"')
    css = re.sub(r'/\*(?!!).*?\*/', '', css, flags=re.S)          # drop comments, keep the license line
    css = re.sub(r'\n\s*\n+', '\n', css).strip() + '\n'
    out = ROOT / 'css' / 'tw' / f'{group}.css'
    out.write_text(f'/* Built by build_css.py from tailwind/{group}.config.js. Do not edit by hand. */\n' + css, encoding='utf-8')
    return out, len(css)


def main():
    tokens = class_tokens()
    print(f'  css   {len(tokens)} candidate class names from the source')
    versions = {}
    for g in GROUPS:
        out, size = compile_group(g, tokens)
        versions[g] = hashlib.md5(out.read_bytes()).hexdigest()[:8]
        print(f'  css   {out.relative_to(ROOT)}  ({size // 1024} KB)')
    (ROOT / 'tailwind' / 'versions.json').write_text(json.dumps(versions, indent=1) + '\n', encoding='utf-8')
    link_pages(versions)


STATIC_PAGES = {
    'index.html': 'home', 'about/index.html': 'about', 'directory/index.html': 'directory',
    'contribute/index.html': 'contribute', 'contribute/interview/index.html': 'contribute-interview',
    'contribute/terms/index.html': 'legal', 'privacy/index.html': 'legal',
}


def link_tag(group, versions):
    return f'<link rel="stylesheet" href="/css/tw/{group}.css?v={versions[group]}">'


def link_pages(versions):
    """Point the hand-written pages at their stylesheet (the page builders do the generated ones)."""
    for rel, group in STATIC_PAGES.items():
        path = ROOT / rel
        text = path.read_text(encoding='utf-8')
        new = re.sub(r'\s*<script src="https://cdn\.tailwindcss\.com[^"]*"></script>', '', text)
        new = re.sub(r'\s*<script id="tailwind-config">.*?</script>', '', new, flags=re.S)
        new = re.sub(r'\s*<link rel="stylesheet" href="/css/tw/[^"]+">', '', new)
        # Last in <head>, where the in-browser compiler used to inject its styles, so the cascade is unchanged
        new = new.replace('</head>', '  ' + link_tag(group, versions) + '\n</head>', 1)
        if new != text:
            path.write_text(new, encoding='utf-8')
            print(f'  css   linked {rel}')


if __name__ == '__main__':
    main()
