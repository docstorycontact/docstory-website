#!/usr/bin/env python3
"""
fetch_wp_interviews.py
Replace AI-summarized interview content with original verbatim text
fetched from the WordPress.com REST API.

Usage:
  python3 fetch_wp_interviews.py           # dry run -- preview matches, no files changed
  python3 fetch_wp_interviews.py --write   # apply changes to all matched files
"""

import json
import re
import ssl
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

# macOS Python installs often lack the system CA bundle; bypass verification
# for this read-only public API fetch.
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

SITE = "docstoryorg.wordpress.com"
API_BASE = f"https://public-api.wordpress.com/rest/v1.1/sites/{SITE}/posts/"
CONTENT_DIR = Path(__file__).parent / "content" / "interviews"
DRY_RUN = "--write" not in sys.argv


# -----------------------------------------------------------------
#  HTML -> Markdown converter
# -----------------------------------------------------------------

class _Para:
    """One paragraph block with per-character bold tracking."""

    def __init__(self):
        # each chunk: (bold, italic, text, href_or_None)
        self.chunks = []
        self.bold_chars = 0
        self.total_chars = 0

    def add(self, text, bold, italic, href=None):
        self.chunks.append((bold, italic, text, href))
        stripped = text.replace(' ', ' ').strip()
        if stripped:
            self.total_chars += len(stripped)
            if bold:
                self.bold_chars += len(stripped)

    @property
    def is_question(self):
        """True if >= 85% of non-whitespace text is bold."""
        return self.total_chars > 0 and self.bold_chars / self.total_chars >= 0.85

    def to_md(self):
        # Determine question status BEFORE building parts so we skip inline bold markers
        is_q = self.is_question
        parts = []
        for bold, italic, text, href in self.chunks:
            t = text.replace(' ', ' ')
            if href:
                t = f"[{t}]({href})"
            if italic and not is_q:
                t = f"*{t}*"
            if bold and not is_q:       # skip per-chunk bold for question paragraphs
                t = f"**{t}**"
            parts.append(t)

        joined = ''.join(parts)
        joined = re.sub(r'[^\S\n]+', ' ', joined)   # collapse spaces (not newlines)
        joined = re.sub(r' *\n *', '\n', joined)
        joined = joined.strip()

        if is_q:
            return f"**Q: {joined}**"
        return joined


class _WPParser(HTMLParser):
    """Event-driven parser -> flat list of _Para objects."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._paras = []
        self._cur = None
        self._bold = 0
        self._italic = 0
        self._href = None
        self._in_link = False
        self._skip = 0      # depth counter for script/style tags

    def _start_para(self):
        if self._cur is not None and self._cur.total_chars > 0:
            self._paras.append(self._cur)
        self._cur = _Para()

    def _ensure_cur(self):
        if self._cur is None:
            self._cur = _Para()

    def handle_starttag(self, tag, attrs):
        if self._skip:
            self._skip += 1
            return
        if tag in ('script', 'style', 'head'):
            self._skip = 1
            return

        attrs_d = dict(attrs)

        if tag == 'p':
            self._start_para()
        elif tag in ('strong', 'b'):
            self._bold += 1
        elif tag in ('em', 'i'):
            self._italic += 1
        elif tag == 'a':
            self._in_link = True
            self._href = attrs_d.get('href', '')
        elif tag == 'br':
            self._ensure_cur()
            self._cur.add('\n', self._bold > 0, self._italic > 0)
        elif tag == 'hr':
            self._start_para()

    def handle_endtag(self, tag):
        if self._skip:
            self._skip -= 1
            return

        if tag == 'p':
            if self._cur is not None and self._cur.total_chars > 0:
                self._paras.append(self._cur)
            self._cur = _Para()
        elif tag in ('strong', 'b'):
            self._bold = max(0, self._bold - 1)
        elif tag in ('em', 'i'):
            self._italic = max(0, self._italic - 1)
        elif tag == 'a':
            self._in_link = False
            self._href = None

    def handle_data(self, data):
        if self._skip:
            return
        self._ensure_cur()
        href = self._href if self._in_link else None
        self._cur.add(data, self._bold > 0, self._italic > 0, href)

    def get_paras(self):
        if self._cur is not None and self._cur.total_chars > 0:
            self._paras.append(self._cur)
            self._cur = None
        return self._paras


def html_to_md(html_content):
    """Convert WordPress post HTML to markdown Q&A body (bio intro stripped)."""
    parser = _WPParser()
    parser.feed(html_content)
    paras = parser.get_paras()

    # Drop bio intro that precedes the first question paragraph
    first_q = next((i for i, p in enumerate(paras) if p.is_question), None)
    start = first_q if first_q is not None else 0

    lines = []
    for para in paras[start:]:
        text = para.to_md()
        if text:
            lines.append(text)
            lines.append('')    # blank line between blocks

    result = '\n'.join(lines).strip()
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result


# -----------------------------------------------------------------
#  Markdown file helpers
# -----------------------------------------------------------------

def read_md(path):
    """Return (frontmatter_block, body, wp_url_or_None)."""
    text = path.read_text('utf-8')
    m = re.match(r'^---\n(.*?)\n---\n?(.*)', text, re.DOTALL)
    if not m:
        return text, '', None
    fm_inner = m.group(1)
    body = m.group(2).lstrip('\n')
    url_m = re.search(r'^url:\s*"([^"]+)"', fm_inner, re.MULTILINE)
    url = url_m.group(1).rstrip('/') if url_m else None
    return f"---\n{fm_inner}\n---", body, url


def build_h1(fm_str):
    """Build the # Heading from frontmatter fields."""
    name = re.search(r'^name:\s*"([^"]+)"', fm_str, re.MULTILINE)
    year = re.search(r'^year:\s*"([^"]+)"', fm_str, re.MULTILINE)
    school = re.search(r'^school:\s*"([^"]+)"', fm_str, re.MULTILINE)
    name = name.group(1) if name else 'Unknown'
    year = year.group(1) if year else ''
    school = school.group(1) if school else 'Unknown'
    suffix = f", {year}" if year else ''
    return f"# {name}{suffix} — {school}"


def url_slug(url):
    """Extract the last non-empty path segment (the WP post slug)."""
    return url.rstrip('/').rsplit('/', 1)[-1]


# -----------------------------------------------------------------
#  API fetching
# -----------------------------------------------------------------

def fetch_all_posts():
    posts = []
    offset = 0
    while True:
        url = (
            f"{API_BASE}?number=100&offset={offset}"
            "&status=publish&fields=ID,slug,URL,title,content,date"
        )
        print(f"  Fetching posts {offset}-{offset + 100}...")
        with urllib.request.urlopen(url, timeout=30, context=_SSL_CTX) as r:
            data = json.loads(r.read())
        batch = data.get('posts', [])
        posts.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
    return posts


# -----------------------------------------------------------------
#  Main
# -----------------------------------------------------------------

def main():
    if DRY_RUN:
        print("DRY RUN -- pass --write to apply changes.\n")

    print("Indexing local markdown files...")
    by_url = {}
    by_slug = {}
    for f in CONTENT_DIR.rglob("*.md"):
        _, _, url = read_md(f)
        if url:
            norm = url.rstrip('/')
            by_url[norm] = f
            by_slug[url_slug(norm)] = f
    print(f"  {len(by_url)} files with WordPress URLs.\n")

    print("Fetching WordPress posts...")
    all_posts = fetch_all_posts()
    print(f"  {len(all_posts)} published posts.\n")

    # Group by base slug to detect duplicates (e.g. "jonathan-carnino-ms1-2" groups with "jonathan-carnino-ms1")
    posts_by_slug = {}
    for p in all_posts:
        s = url_slug(p['URL'])
        base = re.sub(r'-\d+$', '', s)
        posts_by_slug.setdefault(base, []).append(p)

    updated = []
    unmatched_wp = []
    processed_ids = set()

    for slug_base, group in posts_by_slug.items():
        group.sort(key=lambda p: url_slug(p['URL']))   # primary (non-suffixed) first

        primary = group[0]
        wp_url_norm = primary['URL'].rstrip('/')
        md_path = (
            by_url.get(wp_url_norm)
            or by_slug.get(slug_base)
            or by_slug.get(url_slug(wp_url_norm))
        )

        if md_path is None:
            for p in group:
                if p['ID'] not in processed_ids:
                    unmatched_wp.append(p)
                    processed_ids.add(p['ID'])
            continue

        combined_parts = []
        for p in group:
            processed_ids.add(p['ID'])
            part = html_to_md(p['content'])
            if part:
                combined_parts.append(part)

        if len(combined_parts) > 1:
            new_body = '\n\n---\n\n'.join(combined_parts)
            print(f"  NOTE: combining {len(group)} posts for {primary['title']}")
        else:
            new_body = combined_parts[0] if combined_parts else ''

        fm_str, _, _ = read_md(md_path)
        h1 = build_h1(fm_str)
        new_content = f"{fm_str}\n\n{h1}\n\n{new_body}\n"

        if DRY_RUN:
            preview = new_body[:500].replace('\n', ' | ')
            print(f"  WOULD UPDATE: {md_path.relative_to(CONTENT_DIR.parent.parent)}")
            print(f"    WP:  [{primary['ID']}] {primary['title']}")
            if len(group) > 1:
                print(f"    IDs: {[p['ID'] for p in group]}")
            print(f"    >>   {preview}\n")
        else:
            md_path.write_text(new_content, 'utf-8')
            label = f" (combined {len(group)} posts)" if len(group) > 1 else ''
            print(f"  ok  {md_path.relative_to(CONTENT_DIR.parent.parent)}{label}")

        updated.append(str(md_path))

    verb = "Would update" if DRY_RUN else "Updated"
    print(f"\n{verb}: {len(updated)}/{len(by_url)} files")

    if unmatched_wp:
        print(f"\nWordPress posts with NO local file ({len(unmatched_wp)}) -- need new markdown files:")
        for p in unmatched_wp:
            print(f"  [{p['ID']}] {p['title']}")
            print(f"        {p['URL']}")

    unmatched_local = [
        (url, path)
        for url, path in by_url.items()
        if (url_slug(url) not in posts_by_slug
            and url_slug(url) not in {url_slug(p['URL']) for p in all_posts})
    ]
    if unmatched_local:
        print(f"\nLocal files with NO matching WordPress post ({len(unmatched_local)}):")
        for url, path in unmatched_local:
            print(f"  {path.relative_to(CONTENT_DIR.parent.parent)}")
            print(f"        {url}")


if __name__ == '__main__':
    main()
