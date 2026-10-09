"""
DocStory — search & sharing metadata shared by build.py and build_schools.py.

Every page gets: a canonical URL on www.docstory.org, Open Graph / Twitter tags for link
previews, and schema.org JSON-LD so search engines and AI tools can tell what the page is
(an interview by a student at a school, a school profile, the organization itself).
"""
import html
import json

SITE_URL = 'https://www.docstory.org'
SITE_NAME = 'DocStory'
OG_IMAGE = SITE_URL + '/images/og-default.png'
CONTACT_EMAIL = 'docstory.contact@gmail.com'
BING_SITE_VERIFICATION = 'AF26F8B55DCF9964E6198B219F49D353'   # Bing Webmaster Tools ownership check (homepage only)

ORGANIZATION = {
    '@type': 'Organization',
    '@id': SITE_URL + '/#organization',
    'name': SITE_NAME,
    'url': SITE_URL + '/',
    'logo': SITE_URL + '/images/icon-512.png',
    'foundingDate': '2017',
    'email': CONTACT_EMAIL,
    'description': ('Interviews with current medical students about what their schools are really like, '
                    'paired with official school figures and U.S. government data.'),
}


def url(path):
    """Canonical URL for a site path: '/schools/rush-medical-college/' → https://www.docstory.org/schools/…/"""
    path = '/' + path.lstrip('/')
    if path.endswith('index.html'):
        path = path[:-len('index.html')]
    return SITE_URL + path


def breadcrumbs(items):
    """items: [(name, path), …] from the home page down to the current page."""
    return {
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': name, 'item': url(path)}
            for i, (name, path) in enumerate(items)
        ],
    }


def clip(text, limit=158):
    """Trim to a search-snippet-friendly length on a word boundary."""
    text = ' '.join(str(text).split())
    if len(text) <= limit:
        return text
    return text[:limit - 1].rsplit(' ', 1)[0].rstrip(',;:—-') + '…'


def head_tags(title, description, path, og_type='website', jsonld=(), image=OG_IMAGE, robots=None):
    """HTML for <head>: canonical, social preview tags, and JSON-LD blocks. Title/description are plain text."""
    e = lambda s: html.escape(str(s), quote=True)
    canonical = url(path)
    lines = [
        f'<link rel="canonical" href="{canonical}">',
        '<link rel="icon" type="image/png" sizes="48x48" href="/images/favicon-48.png">',
        '<link rel="apple-touch-icon" href="/images/apple-touch-icon.png">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(description)}">',
        f'<meta property="og:url" content="{canonical}">',
        f'<meta property="og:image" content="{image}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{e(title)}">',
        f'<meta name="twitter:description" content="{e(description)}">',
        f'<meta name="twitter:image" content="{image}">',
    ]
    if robots:
        lines.append(f'<meta name="robots" content="{robots}">')
    graph = [ORGANIZATION] + [dict(block) for block in jsonld]
    payload = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=1)
    payload = payload.replace('</', '<\\/')          # never let a value close the <script> early
    lines.append(f'<script type="application/ld+json">\n{payload}\n</script>')
    return '\n  '.join(lines)
