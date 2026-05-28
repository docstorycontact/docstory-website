#!/usr/bin/env python3
"""
build.py — generates static HTML interview pages from markdown content files.
Run from the project root: python3 build.py
"""

import os
import re
import json
import yaml
import markdown
from pathlib import Path
from datetime import datetime

CONTENT_DIR = Path("content/interviews")
OUTPUT_DIR  = Path("interviews")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_file(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
    if not match:
        return {}, text
    meta = yaml.safe_load(match.group(1)) or {}
    body = match.group(2).strip()
    return meta, body


def initials(name):
    parts = str(name).split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return parts[0][:2].upper() if parts else "??"


def school_type_tag(meta):
    year = str(meta.get("year", ""))
    school = str(meta.get("school", "")).lower()
    if year.startswith("O") or "osteopathic" in school or "do" in school:
        return ("Osteopathic (DO)", "bg-primary-fixed text-primary")
    return ("Allopathic (MD)", "bg-surface-container-low text-vibrant-iris")


def format_date(date_str):
    try:
        return datetime.strptime(str(date_str), "%Y-%m-%d").strftime("%B %Y")
    except Exception:
        return str(date_str)


def preprocess_body(body):
    """Strip the first # heading (already shown in article header), then convert
    **Q: ...** question lines into ### headings before markdown parsing."""
    # Remove the top-level h1 (first line starting with a single #)
    body = re.sub(r"^# .+\n?", "", body, count=1)
    body = re.sub(r"^\*\*Q: (.+?)\*\*\s*$", r"### \1", body, flags=re.MULTILINE)
    return body.strip()


def md_to_html(body):
    processed = preprocess_body(body)
    return markdown.markdown(processed, extensions=["extra"])


def slug_from_path(path):
    """Return (school_slug, student_slug) from a content path."""
    rel = path.relative_to(CONTENT_DIR)
    parts = rel.parts
    school_slug  = parts[0] if len(parts) > 1 else "misc"
    student_slug = parts[-1].replace(".md", "")
    return school_slug, student_slug


# ---------------------------------------------------------------------------
# Collect all interview data
# ---------------------------------------------------------------------------

def load_all_interviews():
    interviews = []
    for md_path in sorted(CONTENT_DIR.glob("**/*.md")):
        meta, body = parse_file(md_path)
        school_slug, student_slug = slug_from_path(md_path)
        interviews.append({
            "meta": meta,
            "body": body,
            "school_slug":  school_slug,
            "student_slug": student_slug,
            "path": md_path,
        })
    return interviews


def related_interviews(current, all_interviews, n=3):
    """Return up to n other interviews, preferring same school."""
    same_school = [
        iv for iv in all_interviews
        if iv["school_slug"] == current["school_slug"]
        and iv["student_slug"] != current["student_slug"]
    ]
    others = [
        iv for iv in all_interviews
        if iv["school_slug"] != current["school_slug"]
        and iv["student_slug"] != current["student_slug"]
    ]
    pool = same_school + others
    return pool[:n]


# ---------------------------------------------------------------------------
# HTML templates
# ---------------------------------------------------------------------------

NAV_ITEMS = """
      <a href="{root}index.html"  class="font-body-md text-body-md text-slate-gray hover:text-vibrant-iris transition-colors">Home</a>
      <a href="{root}directory/index.html" class="font-body-md text-body-md text-slate-gray hover:text-vibrant-iris transition-colors">Schools</a>
      <a href="{root}directory/index.html" class="font-body-md text-body-md text-vibrant-iris border-b-2 border-vibrant-iris pb-1 font-medium">Interviews</a>
      <a href="{root}about/index.html" class="font-body-md text-body-md text-slate-gray hover:text-vibrant-iris transition-colors">About</a>
"""

def related_card(iv, root):
    name = iv["meta"].get("name", "Anonymous")
    school = iv["meta"].get("school", iv["school_slug"].replace("-", " ").title())
    year = iv["meta"].get("year", "")
    ini = initials(name)
    url = f'{root}interviews/{iv["school_slug"]}/{iv["student_slug"]}/index.html'
    return f"""
          <li>
            <a href="{url}" class="flex items-start gap-sm group">
              <div class="w-8 h-8 rounded-full bg-tertiary-fixed flex-shrink-0 flex items-center justify-center text-tertiary font-bold text-xs">{ini}</div>
              <div>
                <div class="font-label-md text-label-md text-primary group-hover:text-vibrant-iris transition-colors">{school}</div>
                <div class="font-body-md text-xs text-slate-gray">{name} · {year}</div>
              </div>
            </a>
          </li>"""


def render_interview_page(iv, all_interviews):
    meta         = iv["meta"]
    body_html    = md_to_html(iv["body"])
    school_slug  = iv["school_slug"]
    student_slug = iv["student_slug"]

    root      = "../../" if school_slug != "misc" else "../"
    name      = meta.get("name", "Anonymous")
    school    = meta.get("school", school_slug.replace("-", " ").title())
    year      = meta.get("year", "")
    undergrad = meta.get("undergraduate", "")
    hometown  = meta.get("hometown", "")
    age       = meta.get("age", "")
    date_str  = format_date(meta.get("date", ""))
    ini       = initials(name)
    type_label, type_cls = school_type_tag(meta)
    rel       = related_interviews(iv, all_interviews)
    rel_html  = "".join(related_card(r, root) for r in rel)

    facts = ""
    if school:
        facts += f'<li class="flex justify-between items-start pb-sm border-b border-primary/5"><span class="font-body-md text-body-md text-slate-gray">School</span><span class="font-body-md text-body-md text-primary font-medium text-right max-w-[60%]">{school}</span></li>\n'
    if year:
        facts += f'<li class="flex justify-between items-center pb-sm border-b border-primary/5"><span class="font-body-md text-body-md text-slate-gray">Year</span><span class="font-body-md text-body-md text-primary font-medium">{year}</span></li>\n'
    if undergrad:
        facts += f'<li class="flex justify-between items-start pb-sm border-b border-primary/5"><span class="font-body-md text-body-md text-slate-gray">Undergrad</span><span class="font-body-md text-body-md text-primary font-medium text-right max-w-[60%]">{undergrad}</span></li>\n'
    if hometown:
        facts += f'<li class="flex justify-between items-center pb-sm border-b border-primary/5"><span class="font-body-md text-body-md text-slate-gray">Hometown</span><span class="font-body-md text-body-md text-primary font-medium">{hometown}</span></li>\n'
    if age:
        facts += f'<li class="flex justify-between items-center pb-sm border-b border-primary/5"><span class="font-body-md text-body-md text-slate-gray">Age</span><span class="font-body-md text-body-md text-primary font-medium">{age}</span></li>\n'
    if date_str:
        facts += f'<li class="flex justify-between items-center"><span class="font-body-md text-body-md text-slate-gray">Published</span><span class="font-body-md text-body-md text-primary font-medium">{date_str}</span></li>\n'

    page_title = f"{name}, {year} — {school} | DocStory" if year else f"{name} — {school} | DocStory"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title}</title>
  <meta name="description" content="Read {name}'s first-hand experience at {school}, covering curriculum, culture, and life as a medical student.">
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
  <link href="{root}css/style.css" rel="stylesheet">
  <script id="tailwind-config">
    tailwind.config = {{
      darkMode:'class',
      theme:{{extend:{{
        colors:{{
          'vibrant-iris':'#9580FF','primary':'#333e4d','slate-gray':'#4A5565',
          'tertiary':'#3d20a3','tertiary-container':'#553dba','surface':'#fcf8ff',
          'surface-container':'#efecfc','surface-container-low':'#f5f2ff',
          'surface-container-high':'#e9e6f6','surface-container-highest':'#e3e0f1',
          'surface-container-lowest':'#ffffff','soft-surface':'#F8FAFB',
          'on-surface':'#1b1b26','on-surface-variant':'#44474c','background':'#fcf8ff',
          'on-background':'#1b1b26','primary-fixed':'#d8e3f7','secondary':'#a23d34',
          'secondary-fixed-dim':'#ffb4aa','tertiary-fixed':'#e6deff',
          'tertiary-fixed-dim':'#c9beff','outline':'#75777c','outline-variant':'#c5c6cc',
        }},
        borderRadius:{{DEFAULT:'0.25rem',lg:'0.5rem',xl:'0.75rem',full:'9999px'}},
        spacing:{{xs:'0.5rem',sm:'1rem',md:'1.5rem',lg:'2rem',xl:'4rem',base:'10px',gutter:'20px','margin-desktop':'40px','margin-mobile':'16px'}},
        fontFamily:{{
          'display-lg':['Inter'],'headline-lg':['Inter'],'headline-md':['Inter'],
          'body-lg':['Inter'],'body-md':['Inter'],'label-md':['Plus Jakarta Sans'],
        }},
        fontSize:{{
          'display-lg':['48px',{{lineHeight:'56px',letterSpacing:'-0.02em',fontWeight:'700'}}],
          'headline-lg':['32px',{{lineHeight:'40px',letterSpacing:'-0.01em',fontWeight:'600'}}],
          'headline-md':['20px',{{lineHeight:'28px',fontWeight:'600'}}],
          'body-lg':['16px',{{lineHeight:'24px',fontWeight:'400'}}],
          'body-md':['14px',{{lineHeight:'20px',fontWeight:'400'}}],
          'label-md':['12px',{{lineHeight:'16px',letterSpacing:'0.05em',fontWeight:'600'}}],
        }},
      }}}},
    }}
  </script>
  <style>
    .interview-body h1 {{ font-size: 1.5rem; font-weight: 600; color: #333e4d; margin: 2rem 0 0.5rem; }}
    .interview-body h2 {{ font-size: 1.25rem; font-weight: 600; color: #333e4d; margin: 2rem 0 0.5rem; }}
    .interview-body h3 {{
      font-size: 0.875rem; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.06em; color: #9580FF; margin: 2rem 0 0.5rem;
    }}
    .interview-body p  {{ color: #4A5565; line-height: 1.75; margin-bottom: 1rem; }}
    .interview-body strong {{ color: #333e4d; }}
    .interview-body ul, .interview-body ol {{ color: #4A5565; padding-left: 1.5rem; margin-bottom: 1rem; }}
    .interview-body li {{ margin-bottom: 0.25rem; line-height: 1.7; }}
    .interview-body blockquote {{
      border-left: 4px solid #9580FF; padding: 0.5rem 1.5rem;
      margin: 1.5rem 0; background: #f5f2ff; border-radius: 0 0.5rem 0.5rem 0;
      font-style: italic; color: #333e4d;
    }}
  </style>
  <script defer src="https://cdn.vercel-insights.com/v1/script.js"></script>
</head>
<body class="bg-background text-on-background font-body-md antialiased flex flex-col min-h-screen selection:bg-vibrant-iris selection:text-white">

<!-- NAV -->
<nav class="bg-surface-container-lowest border-b border-primary/10 sticky top-0 z-50">
  <div class="flex justify-between items-center px-margin-desktop py-base max-w-[1200px] mx-auto w-full h-[70px]">
    <a href="{root}index.html" class="flex items-center gap-2 font-bold text-headline-md text-primary">
      <span class="material-symbols-outlined text-vibrant-iris text-2xl" style="font-variation-settings:'FILL' 1">medical_services</span>DocStory
    </a>
    <div class="hidden md:flex items-center gap-lg h-full">
      {NAV_ITEMS.format(root=root)}
    </div>
    <div class="flex items-center gap-2">
      <button class="bg-vibrant-iris text-white px-md py-xs rounded-full font-label-md text-label-md hover:opacity-90 active:scale-95 transition-all hidden md:block shadow-sm">Join Now</button>
      <button id="mobile-menu-toggle" class="md:hidden text-primary hover:text-vibrant-iris">
        <span class="material-symbols-outlined text-[28px]">menu</span>
      </button>
    </div>
  </div>
</nav>

<!-- CONTENT -->
<main class="flex-grow max-w-[1200px] mx-auto px-margin-mobile md:px-margin-desktop py-xl w-full">

  <nav aria-label="breadcrumb" class="mb-lg">
    <a href="{root}directory/index.html" class="inline-flex items-center gap-xs text-slate-gray hover:text-vibrant-iris font-label-md text-label-md transition-colors">
      <span class="material-symbols-outlined text-[16px]">arrow_back</span>
      Back to Directory
    </a>
  </nav>

  <div class="flex flex-col lg:flex-row gap-xl">

    <!-- Main Article -->
    <article class="flex-1 min-w-0">
      <header class="mb-lg">
        <div class="flex flex-wrap items-center gap-xs mb-md">
          <span class="px-sm py-xs rounded-full font-label-md text-label-md {type_cls}">Student Interview</span>
          <span class="px-sm py-xs rounded-full font-label-md text-label-md {type_cls}">{type_label}</span>
        </div>
        <h1 class="font-headline-lg text-headline-lg text-primary mb-md leading-tight">{name}, {year} — {school}</h1>
        <div class="flex items-center gap-sm pb-md border-b border-primary/5">
          <div class="w-12 h-12 rounded-full bg-tertiary-fixed flex items-center justify-center text-tertiary font-bold text-base">{ini}</div>
          <div>
            <div class="font-label-md text-label-md text-primary">{name}</div>
            <div class="font-body-md text-xs text-slate-gray">{year} at {school} · {date_str}</div>
          </div>
        </div>
      </header>

      <div class="interview-body">
        {body_html}
      </div>
    </article>

    <!-- Sidebar -->
    <aside class="lg:w-72 flex-shrink-0 flex flex-col gap-md">
      <div class="bg-soft-surface border border-primary/10 rounded-xl p-lg shadow-sm">
        <h2 class="font-headline-md text-headline-md text-primary mb-md flex items-center gap-xs">
          <span class="material-symbols-outlined text-vibrant-iris">info</span>Quick Facts
        </h2>
        <ul class="space-y-md">
          {facts}
        </ul>
      </div>

      <div class="bg-white border border-primary/10 rounded-xl p-lg shadow-sm">
        <h2 class="font-headline-md text-headline-md text-primary mb-md">More Interviews</h2>
        <ul class="space-y-sm">
          {rel_html}
        </ul>
      </div>
    </aside>

  </div>
</main>

<!-- FOOTER -->
<footer class="bg-surface-container-low border-t border-primary/10 mt-auto">
  <div class="grid grid-cols-1 md:grid-cols-3 gap-lg px-margin-desktop py-xl max-w-[1200px] mx-auto">
    <div class="flex flex-col gap-sm">
      <div class="flex items-center gap-2 font-bold text-headline-md text-primary">
        <span class="material-symbols-outlined text-vibrant-iris" style="font-variation-settings:'FILL' 1">medical_services</span>DocStory
      </div>
      <p class="font-body-md text-body-md text-slate-gray opacity-80">© 2026 DocStory. Empowering the next generation of medical professionals.</p>
    </div>
    <div class="flex flex-col gap-sm md:col-start-3 md:items-end">
      <nav class="flex flex-wrap gap-md md:justify-end">
        <a href="{root}about/index.html" class="text-slate-gray hover:text-vibrant-iris underline opacity-80 hover:opacity-100 transition-opacity font-body-md text-body-md">Mission</a>
        <a href="#" class="text-slate-gray hover:text-vibrant-iris underline opacity-80 hover:opacity-100 transition-opacity font-body-md text-body-md">Contact Us</a>
        <a href="#" class="text-slate-gray hover:text-vibrant-iris underline opacity-80 hover:opacity-100 transition-opacity font-body-md text-body-md">Privacy Policy</a>
        <a href="#" class="text-slate-gray hover:text-vibrant-iris underline opacity-80 hover:opacity-100 transition-opacity font-body-md text-body-md">Terms of Service</a>
      </nav>
    </div>
  </div>
</footer>

<script src="{root}js/main.js"></script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Doodle manifest
# ---------------------------------------------------------------------------

DOODLES_DIR = Path("doodles")
DOODLE_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif"}


def sync_doodle_manifest():
    """Scan doodles/ and regenerate doodles/index.json.
    Drop any image file into doodles/ and re-run build.py to include it."""
    if not DOODLES_DIR.exists():
        return
    files = sorted(
        f.name for f in DOODLES_DIR.iterdir()
        if f.is_file()
        and f.suffix.lower() in DOODLE_EXTENSIONS
        and not f.name.startswith(".")
    )
    manifest = DOODLES_DIR / "index.json"
    manifest.write_text(json.dumps(files, indent=2) + "\n", encoding="utf-8")
    print(f"  ✓  doodles/index.json ({len(files)} doodle{'s' if len(files) != 1 else ''})")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build():
    sync_doodle_manifest()
    all_interviews = load_all_interviews()
    built = 0

    for iv in all_interviews:
        school_slug  = iv["school_slug"]
        student_slug = iv["student_slug"]

        out_dir = OUTPUT_DIR / school_slug / student_slug
        out_dir.mkdir(parents=True, exist_ok=True)

        html = render_interview_page(iv, all_interviews)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"  ✓  interviews/{school_slug}/{student_slug}/index.html")
        built += 1

    print(f"\nDone — {built} interview pages generated.")


if __name__ == "__main__":
    build()
