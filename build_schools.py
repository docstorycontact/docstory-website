#!/usr/bin/env python3
"""
build_schools.py — Generate school landing pages for all 38 schools.
UCI is skipped (handcrafted page already exists).
Run from the project root: python3 build_schools.py
"""

import re, html as html_mod
from pathlib import Path

ROOT = Path(__file__).parent

# ── Static HTML fragments (plain strings — no f-string escaping needed) ───────

TAILWIND_CONFIG = '''<script id="tailwind-config">
    tailwind.config = {
      darkMode:'class',
      theme:{extend:{
        colors:{
          'vibrant-iris':'#9580FF','primary':'#333e4d','slate-gray':'#4A5565',
          'tertiary':'#3d20a3','tertiary-container':'#553dba','surface':'#fcf8ff',
          'surface-dim':'#dbd8e8','surface-variant':'#e3e0f1','surface-container':'#efecfc',
          'surface-container-low':'#f5f2ff','surface-container-high':'#e9e6f6',
          'surface-container-highest':'#e3e0f1','surface-container-lowest':'#ffffff',
          'soft-surface':'#F8FAFB','on-surface':'#1b1b26','on-surface-variant':'#44474c',
          'background':'#fcf8ff','on-background':'#1b1b26','primary-fixed':'#d8e3f7',
          'on-primary-fixed':'#111c2a','on-primary-container':'#becadd','secondary':'#a23d34',
          'secondary-fixed-dim':'#ffb4aa','on-tertiary':'#ffffff','outline':'#75777c',
          'outline-variant':'#c5c6cc','deep-onyx':'#14141F',
        },
        borderRadius:{DEFAULT:'0.25rem',lg:'0.5rem',xl:'0.75rem',full:'9999px'},
        spacing:{xs:'0.5rem',sm:'1rem',md:'1.5rem',lg:'2rem',xl:'4rem',base:'10px',gutter:'20px','margin-desktop':'40px','margin-mobile':'16px'},
        fontFamily:{
          'display-lg':['Inter'],'headline-lg':['Inter'],'headline-md':['Inter'],
          'headline-lg-mobile':['Inter'],'body-lg':['Inter'],'body-md':['Inter'],'label-md':['Plus Jakarta Sans'],
        },
        fontSize:{
          'display-lg':['48px',{lineHeight:'56px',letterSpacing:'-0.02em',fontWeight:'700'}],
          'headline-lg':['32px',{lineHeight:'40px',letterSpacing:'-0.01em',fontWeight:'600'}],
          'headline-md':['20px',{lineHeight:'28px',fontWeight:'600'}],
          'headline-lg-mobile':['24px',{lineHeight:'32px',fontWeight:'600'}],
          'body-lg':['16px',{lineHeight:'24px',fontWeight:'400'}],
          'body-md':['14px',{lineHeight:'20px',fontWeight:'400'}],
          'label-md':['12px',{lineHeight:'16px',letterSpacing:'0.05em',fontWeight:'600'}],
        },
      }},
    }
  </script>'''

EXTERNAL_LINK_SVG = '<svg width="11" height="11" viewBox="0 0 12 12" fill="none"><path d="M10 2H7m3 0v3M10 2L5.5 6.5M3 2H2a1 1 0 00-1 1v7a1 1 0 001 1h7a1 1 0 001-1V9" stroke="#9580FF" stroke-width="1.4" stroke-linecap="round"/></svg>'

# ── School metadata ───────────────────────────────────────────────────────────
# Keys match the slug used in content/interviews/ and schools/

SCHOOLS = {
    'harvard-medical-school': dict(
        name='Harvard Medical School',
        city='Boston', state='MA', type='md', public=False, founded=1782,
        hospital='Massachusetts General Hospital', class_size=165,
    ),
    'yale-school-of-medicine': dict(
        name='Yale School of Medicine',
        city='New Haven', state='CT', type='md', public=False, founded=1810,
        hospital='Yale New Haven Hospital', class_size=100,
    ),
    'johns-hopkins-school-of-medicine': dict(
        name='Johns Hopkins School of Medicine',
        city='Baltimore', state='MD', type='md', public=False, founded=1893,
        hospital='Johns Hopkins Hospital', class_size=120,
    ),
    'duke-university-school-of-medicine': dict(
        name='Duke University School of Medicine',
        city='Durham', state='NC', type='md', public=False, founded=1930,
        hospital='Duke University Medical Center', class_size=105,
    ),
    'weill-cornell-medical-college': dict(
        name='Weill Cornell Medical College',
        city='New York', state='NY', type='md', public=False, founded=1898,
        hospital='NewYork-Presbyterian / Weill Cornell', class_size=101,
    ),
    'northwestern-feinberg-school-of-medicine': dict(
        name='Northwestern Feinberg School of Medicine',
        city='Chicago', state='IL', type='md', public=False, founded=1859,
        hospital='Northwestern Memorial Hospital', class_size=164,
    ),
    'university-of-alabama-birmingham': dict(
        name='UAB Heersink School of Medicine',
        city='Birmingham', state='AL', type='md', public=True, founded=1945,
        hospital='UAB Hospital', class_size=175,
    ),
    # uc-irvine-school-of-medicine is SKIPPED (handcrafted page)
    'university-of-massachusetts-medical-school': dict(
        name='UMass Chan Medical School',
        city='Worcester', state='MA', type='md', public=True, founded=1962,
        hospital='UMass Memorial Medical Center', class_size=124,
    ),
    'uc-san-diego-school-of-medicine': dict(
        name='UC San Diego School of Medicine',
        city='La Jolla', state='CA', type='md', public=True, founded=1967,
        hospital='UC San Diego Health', class_size=134,
    ),
    'mayo-clinic-school-of-medicine': dict(
        name='Mayo Clinic Alix School of Medicine',
        city='Rochester', state='MN', type='md', public=False, founded=1972,
        hospital='Mayo Clinic', class_size=50,
    ),
    'tulane-university-school-of-medicine': dict(
        name='Tulane University School of Medicine',
        city='New Orleans', state='LA', type='md', public=False, founded=1834,
        hospital='Tulane Medical Center', class_size=192,
    ),
    'drexel-university-college-of-medicine': dict(
        name='Drexel University College of Medicine',
        city='Philadelphia', state='PA', type='md', public=False, founded=1848,
        hospital='Tower Health / Lehigh Valley Health Network', class_size=252,
    ),
    'creighton-university-school-of-medicine': dict(
        name='Creighton University School of Medicine',
        city='Omaha', state='NE', type='md', public=False, founded=1892,
        hospital='CHI Health Creighton University Medical Center', class_size=116,
    ),
    'morsani-college-of-medicine': dict(
        name='USF Health Morsani College of Medicine',
        city='Tampa', state='FL', type='md', public=True, founded=1971,
        hospital='Tampa General Hospital', class_size=175,
    ),
    'rosalind-franklin-university': dict(
        name='Chicago Medical School at Rosalind Franklin University',
        city='North Chicago', state='IL', type='md', public=False, founded=1912,
        hospital='Captain James A. Lovell Federal Health Care Center', class_size=200,
    ),
    'usc-keck-school-of-medicine': dict(
        name='USC Keck School of Medicine',
        city='Los Angeles', state='CA', type='md', public=False, founded=1885,
        hospital='Keck Hospital of USC', class_size=180,
    ),
    'western-university-osteopathic': dict(
        name='Western University College of Osteopathic Medicine of the Pacific',
        city='Pomona', state='CA', type='do', public=False, founded=1977,
        hospital='Multiple Teaching Affiliates', class_size=220,
    ),
    'virginia-commonwealth-university': dict(
        name='VCU School of Medicine',
        city='Richmond', state='VA', type='md', public=True, founded=1838,
        hospital='VCU Medical Center', class_size=215,
    ),
    'kentucky-college-of-osteopathic-medicine': dict(
        name='Kentucky College of Osteopathic Medicine',
        city='Pikeville', state='KY', type='do', public=False, founded=1997,
        hospital='Various Appalachian Teaching Sites', class_size=175,
    ),
    'medical-college-of-wisconsin': dict(
        name='Medical College of Wisconsin',
        city='Milwaukee', state='WI', type='md', public=False, founded=1893,
        hospital='Froedtert Hospital', class_size=204,
    ),
    'wayne-state-school-of-medicine': dict(
        name='Wayne State University School of Medicine',
        city='Detroit', state='MI', type='md', public=True, founded=1868,
        hospital='Detroit Medical Center', class_size=290,
    ),
    'baylor-college-of-medicine': dict(
        name='Baylor College of Medicine',
        city='Houston', state='TX', type='md', public=False, founded=1900,
        hospital='Texas Medical Center Hospitals', class_size=185,
    ),
    'ut-health-science-center': dict(
        name='University of Tennessee Health Science Center College of Medicine',
        city='Memphis', state='TN', type='md', public=True, founded=1911,
        hospital='Methodist Le Bonheur Healthcare', class_size=175,
    ),
    'ucla-geffen-school-of-medicine': dict(
        name='David Geffen School of Medicine at UCLA',
        city='Los Angeles', state='CA', type='md', public=True, founded=1951,
        hospital='Ronald Reagan UCLA Medical Center', class_size=180,
    ),
    'university-of-florida-college-of-medicine': dict(
        name='University of Florida College of Medicine',
        city='Gainesville', state='FL', type='md', public=True, founded=1956,
        hospital='UF Health Shands Hospital', class_size=140,
    ),
    'florida-state-university-college-of-medicine': dict(
        name='Florida State University College of Medicine',
        city='Tallahassee', state='FL', type='md', public=True, founded=2000,
        hospital='Multiple Regional Campuses', class_size=120,
    ),
    'medical-college-of-georgia': dict(
        name='Medical College of Georgia at Augusta University',
        city='Augusta', state='GA', type='md', public=True, founded=1828,
        hospital='Augusta University Medical Center', class_size=230,
    ),
    'california-university-of-science-and-medicine': dict(
        name='California University of Science and Medicine',
        city='Colton', state='CA', type='md', public=False, founded=2018,
        hospital='Arrowhead Regional Medical Center', class_size=60,
    ),
    'indiana-university-school-of-medicine': dict(
        name='Indiana University School of Medicine',
        city='Indianapolis', state='IN', type='md', public=True, founded=1903,
        hospital='Indiana University Health', class_size=355,
    ),
    'southern-illinois-university-school-of-medicine': dict(
        name='Southern Illinois University School of Medicine',
        city='Springfield', state='IL', type='md', public=True, founded=1970,
        hospital='Memorial Medical Center', class_size=72,
    ),
    'touro-college-of-osteopathic-medicine': dict(
        name='Touro College of Osteopathic Medicine',
        city='Middletown', state='NY', type='do', public=False, founded=2007,
        hospital='Multiple Teaching Affiliates', class_size=285,
    ),
    'university-of-cincinnati-college-of-medicine': dict(
        name='University of Cincinnati College of Medicine',
        city='Cincinnati', state='OH', type='md', public=True, founded=1819,
        hospital='UC Health University of Cincinnati Medical Center', class_size=175,
    ),
    'new-york-medical-college': dict(
        name='New York Medical College',
        city='Valhalla', state='NY', type='md', public=False, founded=1860,
        hospital='Westchester Medical Center', class_size=200,
    ),
    'university-of-miami-miller-school-of-medicine': dict(
        name='University of Miami Miller School of Medicine',
        city='Miami', state='FL', type='md', public=False, founded=1952,
        hospital='Jackson Memorial Hospital', class_size=215,
    ),
    'university-of-iowa-carver-college-of-medicine': dict(
        name='University of Iowa Carver College of Medicine',
        city='Iowa City', state='IA', type='md', public=True, founded=1870,
        hospital='University of Iowa Hospitals & Clinics', class_size=150,
    ),
    'eastern-virginia-medical-school': dict(
        name='Eastern Virginia Medical School',
        city='Norfolk', state='VA', type='md', public=True, founded=1973,
        hospital='Sentara Norfolk General Hospital', class_size=110,
    ),
    'rush-medical-college': dict(
        name='Rush Medical College',
        city='Chicago', state='IL', type='md', public=False, founded=1837,
        hospital='Rush University Medical Center', class_size=120,
    ),
    'tcu-burnett-school-of-medicine': dict(
        name='TCU Burnett School of Medicine',
        city='Fort Worth', state='TX', type='md', public=False, founded=2019,
        hospital='Baylor Scott & White All Saints Medical Center', class_size=60,
    ),
}

# ── Handcrafted school pages ──────────────────────────────────────────────────
# These schools have full editorial pages (stats dashboard + program highlights)
# built by hand rather than generated by this script.
#
# PROCESS — to add a new handcrafted dashboard page for any school:
#
#   1. FETCH STATS from SDN:
#      Navigate to studentdoctor.net/schools-database/medical-school/
#      Search for the school. Click through to its detail page.
#      Record: MCAT (avg), GPA overall, tuition IS/OOS, enrollment,
#              gender %, faculty count, hospital beds.
#      Detail URL pattern: .../detail/<CODE>/<slug>
#
#   2. SUPPLEMENT from AAMC MSAR (aamc.org/data-reports/interactive-data):
#      Science/BCPM GPA (often not on SDN), class size, gender breakdown,
#      applicants, interviews granted, enrolled.
#
#   3. READ INTERVIEWS from content/interviews/<school-slug>/*.md
#      Note distinctive program features, student quotes, and unique activities
#      for the Program Highlights section.
#
#   4. COPY the UC Irvine page as a template:
#      cp schools/uc-irvine-school-of-medicine/index.html schools/<slug>/index.html
#      Then replace all UCI-specific data, stats, program highlights, and
#      student voice cards with the new school's content.
#
#   5. ADD the slug to the SKIP set below.
#
# Dashboard stats reference:
#   MCAT curve marker x-position: x ≈ 91 + (median_mcat - 502) * 2.64
#   GPA bar width %:              width ≈ (gpa - 3.0) * 100 - 2
#   Women donut dasharray:        filled = pct/100 * 131.95, gap = 131.95 - filled
#
SKIP = {
    'uc-irvine-school-of-medicine',   # Handcrafted — full dashboard + program highlights
    'usc-keck-school-of-medicine',    # Handcrafted — full dashboard + program highlights
}


# ── Parsing ───────────────────────────────────────────────────────────────────

def parse_md(path):
    """Return (front_matter_dict, body_str) for a markdown file."""
    text = path.read_text(encoding='utf-8')
    fm = {}
    body = text
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            for line in parts[1].splitlines():
                if ':' in line:
                    k, _, v = line.partition(':')
                    fm[k.strip()] = v.strip().strip('"')
            body = parts[2].strip()
    return fm, body


def extract_quote(body):
    """Pull first substantial quoted passage or paragraph from interview body."""
    for m in re.finditer(r'"([^"]{80,})"', body):
        text = m.group(1)[:300]
        return html_mod.escape('“' + text + ('…”' if len(m.group(1)) > 300 else '”'), quote=False)
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('**Q') or line.startswith('---'):
            continue
        line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
        line = re.sub(r'\*(.+?)\*', r'\1', line)
        line = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', line)
        if len(line) >= 80:
            text = line[:300]
            return html_mod.escape(text + ('…' if len(line) > 300 else ''), quote=False)
    return 'Read this interview to learn more about the student experience at this school.'


def initials(name):
    parts = name.strip().split()
    if not parts:
        return '?'
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


# ── Rendering ─────────────────────────────────────────────────────────────────

def render_voice_card(school_slug, fm, body, student_slug):
    iv_name = fm.get('name', 'Anonymous')
    iv_year = fm.get('year', '')
    iv_ug   = fm.get('undergraduate', '')
    iv_home = fm.get('hometown', fm.get('location', ''))

    ug_short = ''
    if iv_ug:
        ug_short = iv_ug.split('(')[0].split(',')[0].strip()

    meta_parts = [p for p in [iv_year, (ug_short + ' undergrad') if ug_short else '', iv_home] if p]
    meta_str = ' · '.join(meta_parts)

    quote  = extract_quote(body)
    inits  = initials(iv_name)
    iv_url = f'../../interviews/{school_slug}/{student_slug}/index.html'

    return f'''      <a href="{iv_url}"
         class="bg-white border border-primary/5 rounded-xl p-lg shadow-sm hover:border-vibrant-iris/30 hover:shadow-md transition-all group block">
        <div class="flex items-center gap-sm mb-md">
          <div class="w-10 h-10 rounded-full bg-surface-container-high flex items-center justify-center font-bold text-primary text-sm flex-shrink-0 group-hover:bg-vibrant-iris/10 group-hover:text-vibrant-iris transition-colors">{inits}</div>
          <div>
            <div class="font-semibold text-primary text-sm group-hover:text-vibrant-iris transition-colors leading-tight">{html_mod.escape(iv_name, quote=False)}</div>
            <div class="font-body-md text-[11px] text-slate-gray mt-0.5">{html_mod.escape(meta_str, quote=False)}</div>
          </div>
        </div>
        <p class="font-body-md text-xs text-slate-gray leading-relaxed line-clamp-4">{quote}</p>
        <div class="mt-sm font-label-md text-[11px] text-vibrant-iris font-semibold group-hover:underline transition-all">Read Interview →</div>
      </a>'''


def render_page(school_slug, data, interviews):
    name     = data['name']
    city     = data['city']
    state    = data['state']
    pub      = 'Public' if data['public'] else 'Private'
    founded  = data.get('founded', '')
    hospital = data.get('hospital', '')
    class_sz = data.get('class_size', '')
    type_lbl = 'Allopathic (MD)' if data['type'] == 'md' else 'Osteopathic (DO)'
    degree   = 'MD' if data['type'] == 'md' else 'DO'

    sub_parts = [f'{city}, {state}']
    if hospital:
        sub_parts.append(f'<span class="text-primary font-medium">{html_mod.escape(hospital, quote=False)}</span>')
    if class_sz:
        sub_parts.append(f'{class_sz} students per class')
    hero_sub = ' · '.join(sub_parts)

    founded_badge = (f'<span class="px-sm py-1 bg-surface-container-high text-slate-gray rounded-full'
                     f' font-label-md text-[11px]">Founded {founded}</span>') if founded else ''

    n = len(interviews)
    iv_label   = f'{n} interview{"s" if n != 1 else ""}'
    grid_cols  = 'md:grid-cols-3' if n >= 3 else ('md:grid-cols-2' if n == 2 else 'md:grid-cols-1')
    voices_html = '\n'.join(render_voice_card(school_slug, fm, body, slug) for fm, body, slug in interviews)

    sdn_url = 'https://www.studentdoctor.net/schools-database/medical-school/'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html_mod.escape(name)} — School Profile | DocStory</title>
  <meta name="description" content="Explore {html_mod.escape(name)} — program stats, curriculum highlights, research, and real student interview experiences.">
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
  <link href="../../css/style.css" rel="stylesheet">
  {TAILWIND_CONFIG}
  <style>
    .line-clamp-4 {{ display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }}
  </style>
  <script defer src="https://cdn.vercel-insights.com/v1/script.js"></script>
</head>
<body class="bg-background text-on-background font-body-md antialiased flex flex-col min-h-screen selection:bg-vibrant-iris selection:text-white">

<!-- NAV -->
<nav class="bg-surface-container-lowest border-b border-primary/10 sticky top-0 z-50">
  <div class="flex justify-between items-center px-margin-mobile md:px-margin-desktop max-w-[1200px] mx-auto w-full h-[70px]">
    <a href="../../index.html" class="flex items-center gap-2 font-bold text-headline-md text-primary">
      <span class="material-symbols-outlined text-vibrant-iris text-2xl" style="font-variation-settings:&apos;FILL&apos; 1">medical_services</span>DocStory
    </a>
    <div class="hidden md:flex items-center gap-lg h-full">
      <a href="../../index.html" class="font-body-md text-body-md text-slate-gray hover:text-vibrant-iris transition-colors">Home</a>
      <a href="../../directory/index.html" class="font-body-md text-body-md text-vibrant-iris border-b-2 border-vibrant-iris pb-1 font-medium">Schools</a>
      <a href="../../directory/index.html" class="font-body-md text-body-md text-slate-gray hover:text-vibrant-iris transition-colors">Interviews</a>
      <a href="../../about/index.html" class="font-body-md text-body-md text-slate-gray hover:text-vibrant-iris transition-colors">About</a>
    </div>
    <div class="flex items-center gap-2">
      <button class="bg-vibrant-iris text-white px-md py-xs rounded-full font-label-md text-label-md hover:opacity-90 active:scale-95 transition-all hidden md:block shadow-sm">Join Now</button>
    </div>
  </div>
</nav>

<main class="flex-grow">

  <!-- HERO -->
  <div class="bg-surface-container-low border-b border-primary/5">
    <div class="max-w-[1200px] mx-auto px-margin-mobile md:px-margin-desktop pt-lg pb-xl">
      <a href="../../directory/index.html" class="inline-flex items-center gap-xs text-slate-gray hover:text-vibrant-iris font-label-md text-label-md transition-colors mb-lg">
        <span class="material-symbols-outlined text-[16px]">arrow_back</span>
        Back to Directory
      </a>
      <div class="flex flex-wrap gap-xs mb-md">
        <span class="px-sm py-1 bg-vibrant-iris/10 text-vibrant-iris rounded-full font-label-md text-[11px] font-semibold">{type_lbl}</span>
        <span class="px-sm py-1 bg-surface-container-high text-slate-gray rounded-full font-label-md text-[11px]">{pub}</span>
        {founded_badge}
        <span class="px-sm py-1 bg-surface-container-high text-slate-gray rounded-full font-label-md text-[11px]">{city}, {state}</span>
      </div>
      <h1 class="font-display-lg text-[36px] md:text-display-lg text-primary leading-tight tracking-tight">{html_mod.escape(name, quote=False)}</h1>
      <p class="font-body-lg text-body-lg text-slate-gray mt-sm">{hero_sub}</p>
    </div>
  </div>

  <!-- STATS PANEL -->
  <div class="max-w-[1200px] mx-auto px-margin-mobile md:px-margin-desktop py-xl">
    <div class="bg-white border border-primary/5 rounded-2xl shadow-sm overflow-hidden">
      <div class="flex items-center justify-between gap-lg p-lg border-b border-surface-container-high flex-wrap">
        <div>
          <h2 class="font-headline-md text-headline-md text-primary">Program Statistics</h2>
          <p class="font-body-md text-body-md text-slate-gray mt-1">MCAT/GPA medians, acceptance rates, class profile, and cost of attendance.</p>
        </div>
        <a href="{sdn_url}" target="_blank" rel="noopener noreferrer"
           class="inline-flex items-center gap-2 bg-vibrant-iris/10 text-vibrant-iris hover:bg-vibrant-iris/20 transition-colors px-md py-xs rounded-full font-label-md text-label-md whitespace-nowrap flex-shrink-0">
          View on Student Doctor Network
          {EXTERNAL_LINK_SVG}
        </a>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 divide-x divide-y divide-surface-dim/40">
        <div class="p-lg">
          <div class="font-label-md text-[11px] text-slate-gray uppercase tracking-wider mb-2">Degree</div>
          <div class="text-2xl font-bold text-primary tracking-tight">{degree}</div>
        </div>
        <div class="p-lg">
          <div class="font-label-md text-[11px] text-slate-gray uppercase tracking-wider mb-2">Status</div>
          <div class="text-2xl font-bold text-primary tracking-tight">{pub}</div>
        </div>
        <div class="p-lg">
          <div class="font-label-md text-[11px] text-slate-gray uppercase tracking-wider mb-2">Founded</div>
          <div class="text-2xl font-bold text-primary tracking-tight">{founded if founded else '—'}</div>
        </div>
        <div class="p-lg">
          <div class="font-label-md text-[11px] text-slate-gray uppercase tracking-wider mb-2">Class Size</div>
          <div class="text-2xl font-bold text-primary tracking-tight">{class_sz if class_sz else '—'}<span class="text-sm font-normal text-slate-gray ml-1">students</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- STUDENT VOICES -->
  <div class="bg-surface-container-low border-y border-primary/5">
    <div class="max-w-[1200px] mx-auto px-margin-mobile md:px-margin-desktop py-xl">
      <div class="flex items-baseline justify-between flex-wrap gap-sm mb-lg">
        <div>
          <h2 class="font-headline-lg text-headline-lg text-primary">Student Voices</h2>
          <p class="font-body-md text-xs text-slate-gray mt-1">{iv_label} from current and former students</p>
        </div>
      </div>
      <div class="grid grid-cols-1 {grid_cols} gap-lg">
{voices_html}
      </div>
    </div>
  </div>

</main>

<!-- FOOTER -->
<footer class="bg-surface-container-low border-t border-primary/10 mt-auto">
  <div class="grid grid-cols-1 md:grid-cols-3 gap-lg px-margin-mobile md:px-margin-desktop py-xl max-w-[1200px] mx-auto">
    <div class="flex flex-col gap-sm">
      <div class="flex items-center gap-2 font-bold text-headline-md text-primary">
        <span class="material-symbols-outlined text-vibrant-iris" style="font-variation-settings:&apos;FILL&apos; 1">medical_services</span>DocStory
      </div>
      <p class="font-body-md text-body-md text-slate-gray opacity-80">&copy; 2026 DocStory. Empowering the next generation of medical professionals.</p>
    </div>
    <div class="flex flex-col gap-sm md:col-start-3 md:items-end">
      <nav class="flex flex-wrap gap-md md:justify-end">
        <a href="../../about/index.html" class="text-slate-gray hover:text-vibrant-iris underline opacity-80 hover:opacity-100 transition-opacity font-body-md text-body-md">Mission</a>
        <a href="#" class="text-slate-gray hover:text-vibrant-iris underline opacity-80 hover:opacity-100 transition-opacity font-body-md text-body-md">Contact Us</a>
        <a href="#" class="text-slate-gray hover:text-vibrant-iris underline opacity-80 hover:opacity-100 transition-opacity font-body-md text-body-md">Privacy Policy</a>
        <a href="#" class="text-slate-gray hover:text-vibrant-iris underline opacity-80 hover:opacity-100 transition-opacity font-body-md text-body-md">Terms of Service</a>
      </nav>
    </div>
  </div>
</footer>

<script src="../../js/main.js"></script>
</body>
</html>'''


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    content_dir = ROOT / 'content' / 'interviews'
    schools_dir = ROOT / 'schools'

    generated = 0
    skipped   = 0
    warned    = 0

    for slug, data in SCHOOLS.items():
        if slug in SKIP:
            print(f'  skip  {slug}  (handcrafted)')
            skipped += 1
            continue

        iv_dir = content_dir / slug
        if not iv_dir.exists():
            print(f'  WARN  {slug}: interviews directory not found')
            warned += 1
            continue

        iv_files = sorted(iv_dir.glob('*.md'))
        if not iv_files:
            print(f'  WARN  {slug}: no .md files found')
            warned += 1
            continue

        interviews = []
        for f in iv_files:
            fm, body = parse_md(f)
            interviews.append((fm, body, f.stem))

        html = render_page(slug, data, interviews)

        out_dir  = schools_dir / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / 'index.html'
        out_file.write_text(html, encoding='utf-8')

        n = len(interviews)
        print(f'  write {str(out_file.relative_to(ROOT)):<65}  ({n} iv{"s" if n > 1 else ""})')
        generated += 1

    print(f'\nDone: {generated} pages generated, {skipped} skipped, {warned} warnings.')


if __name__ == '__main__':
    main()
