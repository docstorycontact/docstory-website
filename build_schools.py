#!/usr/bin/env python3
"""
build_schools.py — Generate school landing pages for every school in SCHOOLS.
Schools with a data file in content/schools/<slug>.yaml get the full page
(stats dashboard + Program Highlights); the rest get the basic page.
Run from the project root: python3 build_schools.py
"""

import re, math, json, html as html_mod
from pathlib import Path

import yaml

import seo

ROOT = Path(__file__).parent
DATA_DIR = ROOT / 'content' / 'schools'

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
    'uc-irvine-school-of-medicine': dict(
        name='UC Irvine School of Medicine',
        city='Irvine', state='CA', type='md', public=True, founded=1967,
        hospital='UCI Medical Center', class_size=114,
    ),
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
        hospital='Wellstar MCG Health', class_size=230,
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
    'albany-medical-college': dict(
        name='Albany Medical College',
        city='Albany', state='NY', type='md', public=False, founded=1839,
        hospital='Albany Medical Center Hospital', class_size=135,
    ),
    'university-of-oklahoma-college-of-medicine': dict(
        name='University of Oklahoma College of Medicine',
        city='Oklahoma City', state='OK', type='md', public=True, founded=1900,
        hospital='OU Health University of Oklahoma Medical Center', class_size=202,
    ),
    'brody-school-of-medicine': dict(
        name='Brody School of Medicine at East Carolina University',
        city='Greenville', state='NC', type='md', public=True,
        hospital='ECU Health Medical Center', class_size=96,
    ),
    'texas-a-and-m-college-of-medicine': dict(
        name='Texas A&M University Naresh K. Vashisht College of Medicine',
        city='Bryan', state='TX', type='md', public=True, founded=1977,
        hospital='Four Regional Campuses', class_size=200,
    ),
    'midwestern-chicago-college-of-osteopathic-medicine': dict(
        name='Midwestern University Chicago College of Osteopathic Medicine',
        city='Downers Grove', state='IL', type='do', public=False,
        hospital='Chicago-Area Clinical Affiliates', class_size=214,
    ),
}

# ── Full school pages (stats dashboard + Program Highlights) ──────────────────
# A school gets the full page when content/schools/<slug>.yaml exists.
# content/schools/_TEMPLATE.yaml documents every field; all are optional.
#
# PROCESS — to give a school the full page (official sources only; see _TEMPLATE.yaml):
#
#   1. STATS from the school's own site: class profile / admissions statistics page,
#      cost-of-attendance page, facts or "by the numbers" page. Note each page's URL.
#   2. NIH funding is automatic: set `nih_org` and run fetch_nih_funding.py.
#   3. HIGHLIGHTS from content/interviews/<slug>/*.md plus facts confirmed on the
#      school's curriculum, program and hospital pages — written in our own words.
#   4. COPY content/schools/_TEMPLATE.yaml to content/schools/<slug>.yaml, fill it in
#      with a source comment per number, and run this script.
#
# Charts are drawn from the numbers automatically (see render_dashboard).
#
# SKIP: slugs this script must never overwrite (none at the moment).
SKIP = set()


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


KNOWN_STATS = {
    'entering_class', 'cohort_label', 'stats_kind', 'gpa_kind', 'profile_url', 'mcat', 'gpa_science', 'gpa_overall',
    'tuition', 'tuition_in_state', 'tuition_out_of_state', 'cost_year', 'total_cost',
    'total_cost_note', 'tuition_note', 'women_pct', 'out_of_state_pct', 'class_size', 'founded', 'total_students',
    'applied', 'interviewed', 'admitted', 'acceptance_rate', 'enrolled', 'faculty',
    'faculty_label', 'beds', 'beds_label', 'nih_label',
}


FETCHED_DIR = DATA_DIR / 'fetched'
NIH_REPORTER_URL = 'https://reporter.nih.gov/'


def load_fetched(slug):
    """Automatic figures written by fetch_public_data.py (all U.S. government data, public domain).
    Returns (stats, sources, raw) — stats merged into the dashboard, raw for the extra sections."""
    path = FETCHED_DIR / f'{slug}.json'
    if not path.exists():
        return {}, [], {}
    raw = json.loads(path.read_text(encoding='utf-8'))
    stats, sources = {}, []
    nih = raw.get('nih') or {}
    if nih.get('amount'):
        stats.update(nih_funding=nih['amount'], nih_year=nih['fiscal_year'])
        sources.append({'label': 'NIH RePORTER', 'url': NIH_REPORTER_URL})
    if (raw.get('trials') or {}).get('recruiting') is not None:
        sources.append({'label': 'ClinicalTrials.gov', 'url': 'https://clinicaltrials.gov/'})
    if raw.get('hospitals'):
        sources.append({'label': 'CMS Care Compare', 'url': 'https://www.medicare.gov/care-compare/'})
    if raw.get('rent'):
        sources.append({'label': 'U.S. Census ACS', 'url': 'https://data.census.gov/'})
    return stats, sources, raw


def merged_stats(slug, page, school):
    """Hand-sourced numbers from the YAML (each with a cited source) plus fetched NIH funding.
    Founding year and class size fall back to SCHOOLS when the YAML doesn't give them."""
    page = page or {}
    fetched, fetched_sources, _ = load_fetched(slug)
    stats = {'class_size': school.get('class_size'), 'founded': school.get('founded'),
             **fetched, **(page.get('stats') or {})}
    stats['sources'] = list(page.get('sources') or []) + fetched_sources
    # One tuition rate for everyone (typical of private schools) shows as a single bar
    if stats.get('tuition_in_state') and stats.get('tuition_in_state') == stats.get('tuition_out_of_state'):
        stats.setdefault('tuition', stats.pop('tuition_in_state'))
        stats.pop('tuition_out_of_state')
    return stats


def load_school_data(slug):
    """Return the parsed content/schools/<slug>.yaml, or None if the school has no data file."""
    path = DATA_DIR / f'{slug}.yaml'
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    for key in set(data.get('stats') or {}) - KNOWN_STATS:
        print(f'  WARN  {slug}.yaml: unknown stats field "{key}" (typo?)')
    return data


# ── Rendering ─────────────────────────────────────────────────────────────────

DASHBOARD_CSS = '''
    /* ── Editorial Stats Dashboard ── */
    .dc-card {
      background: #fff;
      border: 1px solid #ececf4;
      border-radius: 20px;
      box-shadow: 0 1px 2px rgba(31,34,53,.04), 0 12px 32px -16px rgba(91,75,209,.10);
      overflow: hidden;
      font-family: 'Inter', -apple-system, sans-serif;
      font-feature-settings: "cv11","ss01","tnum";
      color: #1f2235;
    }
    .dc-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      padding: 22px 28px 18px;
      border-bottom: 1px solid #ececf4;
      flex-wrap: wrap;
      gap: 8px;
    }
    .dc-header h2 { font-size: 1.375rem; font-weight: 700; color: #1f2235; letter-spacing: -0.02em; margin: 0; }
    .dc-meta { font-size: 0.8125rem; color: #8a8fa6; margin: 3px 0 0; }
    .dc-sdn-link {
      font-size: 0.8125rem; color: #6c5ce7; text-decoration: none;
      display: inline-flex; align-items: center; gap: 4px; white-space: nowrap; flex-shrink: 0;
    }
    .dc-sdn-link:hover { text-decoration: underline; }
    .dc-src { color: #4b4f6b; font-weight: 600; text-decoration: underline; text-decoration-color: #d6d3ef; text-underline-offset: 2px; }
    .dc-src:hover { color: #6c5ce7; }
    .dc-stage {
      display: flex;
      background:
        radial-gradient(900px 480px at 85% -10%, rgba(139,127,255,.12), transparent 60%),
        radial-gradient(700px 360px at -10% 110%, rgba(108,92,231,.08), transparent 60%),
        #faf9ff;
    }
    .dc-col { display: flex; flex-direction: column; flex: 1; }
    .dc-col-l { flex: 1.35; }
    .dc-col-r { flex: 1; }
    .dc-divider-v { width: 1px; background: #ececf4; flex-shrink: 0; }
    .dc-cell { padding: 22px 28px; flex: 1; }
    .dc-cell + .dc-cell { border-top: 1px solid #ececf4; }
    .dc-cell-label {
      font-size: 0.6875rem; font-weight: 700; letter-spacing: 0.08em;
      text-transform: uppercase; color: #8a8fa6; margin-bottom: 10px;
      display: flex; align-items: center; gap: 6px;
    }
    .dc-cell-label::before {
      content: ''; width: 6px; height: 6px; border-radius: 50%;
      background: #8b7fff; flex-shrink: 0;
    }
    /* Selectivity */
    .dc-mcat-big { font-size: 3.25rem; font-weight: 800; color: #1f2235; line-height: 1; letter-spacing: -0.04em; }
    .dc-mcat-unit { font-size: 0.875rem; color: #4b4f6b; margin-left: 8px; font-weight: 400; }
    .dc-good { font-size: 0.8125rem; color: #1f9d6b; font-weight: 600; margin-top: 3px; }
    .dc-selectivity-body { display: flex; gap: 16px; align-items: center; margin-top: 10px; }
    .dc-curve-wrap { flex: 1; min-width: 0; }
    .dc-curve-wrap:only-child { max-width: 420px; }   /* no GPA published: keep the curve at its usual scale */
    .dc-gpa-wrap { flex-shrink: 0; width: 150px; }
    .dc-gpa-row { display: flex; align-items: center; gap: 8px; margin-bottom: 7px; }
    .dc-gpa-num { font-size: 0.9375rem; font-weight: 700; color: #1f2235; width: 34px; letter-spacing: -0.01em; }
    .dc-gpa-bar-bg { flex: 1; height: 4px; background: #e3dfff; border-radius: 2px; overflow: hidden; }
    .dc-gpa-bar-fill { height: 100%; border-radius: 2px; background: #6c5ce7; }
    .dc-gpa-tag { font-size: 0.6875rem; font-weight: 600; color: #8a8fa6; letter-spacing: 0.03em; width: 46px; text-align: right; }
    .dc-gpa-meta { font-size: 0.6875rem; color: #8a8fa6; margin-top: 2px; }
    /* Cost */
    .dc-cost-row { margin-bottom: 12px; }
    .dc-cost-row-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px; }
    .dc-cost-label { font-size: 0.8125rem; color: #4b4f6b; }
    .dc-cost-amt { font-size: 1.25rem; font-weight: 700; color: #1f2235; letter-spacing: -0.02em; }
    .dc-cost-per { font-size: 0.75rem; color: #8a8fa6; font-weight: 400; margin-left: 1px; }
    .dc-cost-bar-bg { height: 5px; background: #eeecfb; border-radius: 3px; overflow: hidden; }
    .dc-cost-bar-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, #8b7fff, #6c5ce7); }
    .dc-cost-bar-fill.dc-cost-strong { background: linear-gradient(90deg, #5b4bd1, #4a3dbf); }
    .dc-cost-note { font-size: 0.6875rem; color: #8a8fa6; margin-top: 6px; }
    /* Class Profile */
    .dc-donuts { display: flex; gap: 16px; align-items: center; margin-bottom: 14px; flex-wrap: wrap; }
    .dc-donut-item { display: flex; align-items: center; gap: 10px; }
    .dc-donut-labels h4 { font-size: 1.375rem; font-weight: 700; color: #1f2235; line-height: 1; letter-spacing: -0.03em; margin: 0; }
    .dc-donut-labels p { font-size: 0.6875rem; font-weight: 600; color: #8a8fa6; letter-spacing: 0.05em; text-transform: uppercase; margin: 2px 0 0; }
    .dc-profile-stats { display: flex; gap: 20px; padding-top: 10px; border-top: 1px solid #f2f1f8; }
    .dc-profile-stat h4 { font-size: 1.75rem; font-weight: 700; color: #1f2235; line-height: 1; letter-spacing: -0.04em; margin: 0; }
    .dc-profile-stat p { font-size: 0.6875rem; font-weight: 600; color: #8a8fa6; letter-spacing: 0.05em; text-transform: uppercase; margin: 3px 0 0; }
    /* Scale & Reach */
    .dc-reach-body { display: flex; gap: 16px; }
    .dc-funnel { flex: 1; min-width: 0; }
    .dc-funnel-row { margin-bottom: 9px; }
    .dc-funnel-label-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
    .dc-funnel-name { font-size: 0.8125rem; color: #4b4f6b; font-weight: 500; }
    .dc-funnel-num { font-size: 0.8125rem; font-weight: 700; color: #1f2235; }
    .dc-funnel-bar-bg { height: 8px; background: #f1efff; border-radius: 4px; overflow: hidden; }
    .dc-funnel-bar-fill { height: 100%; border-radius: 4px; background: #8b7fff; }
    .dc-funnel-note { font-size: 0.6875rem; color: #8a8fa6; margin-top: 4px; }
    .dc-reach-aside { flex-shrink: 0; }
    .dc-reach-stat { margin-bottom: 12px; }
    .dc-reach-stat h4 { font-size: 1.375rem; font-weight: 700; color: #1f2235; line-height: 1; letter-spacing: -0.03em; margin: 0; }
    .dc-reach-stat p { font-size: 0.6875rem; font-weight: 600; color: #8a8fa6; letter-spacing: 0.04em; text-transform: uppercase; margin: 3px 0 0; }
    /* Cost of living */
    .dc-rent { display: flex; justify-content: space-between; align-items: baseline; margin-top: 14px; padding-top: 12px; border-top: 1px dashed #e6e4f2; }
    .dc-cell-label + .dc-rent { margin-top: 0; padding-top: 0; border-top: 0; }
    .dc-rent-label { font-size: 0.8125rem; color: #4b4f6b; }
    .dc-rent-amt { font-size: 1.125rem; font-weight: 700; color: #1f2235; letter-spacing: -0.02em; }
    /* Extra band */
    .dc-more { display: flex; flex-wrap: wrap; gap: 1px; background: #ececf4; border-top: 1px solid #ececf4; }
    .dc-more > .dc-cell { flex: 1 1 300px; background: #fff; border-top: 0; }
    .dc-more > .dc-cell-wide { flex: 2 1 560px; }
    .dc-sub { font-size: 0.6875rem; font-weight: 600; color: #8a8fa6; letter-spacing: 0.04em; text-transform: uppercase; margin: 12px 0 6px; }
    .dc-sub:first-child { margin-top: 0; }
    .dc-foot { font-size: 0.6875rem; color: #8a8fa6; margin-top: 10px; line-height: 1.5; }
    .dc-sites { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 8px 20px; list-style: none; margin: 0; padding: 0; }
    .dc-site { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f2f1f8; }
    .dc-site-name { font-size: 0.8125rem; font-weight: 600; color: #1f2235; line-height: 1.3; }
    .dc-site-meta { font-size: 0.6875rem; color: #8a8fa6; margin-top: 2px; }
    .dc-site-more { font-size: 0.75rem; color: #4b4f6b; margin-top: 10px; line-height: 1.5; }
    .dc-stars { color: #6c5ce7; font-size: 0.75rem; letter-spacing: 1px; white-space: nowrap; flex-shrink: 0; }
    .dc-star-off { color: #e3dfff; }
    .dc-trend { display: flex; align-items: flex-end; gap: 14px; margin-bottom: 4px; }
    .dc-trend h4 { font-size: 1.375rem; font-weight: 700; color: #1f2235; line-height: 1; letter-spacing: -0.03em; margin: 0; }
    .dc-trend p { font-size: 0.6875rem; font-weight: 600; color: #8a8fa6; letter-spacing: 0.04em; text-transform: uppercase; margin: 3px 0 0; }
    .dc-trend .dc-trend-chg { color: #4b4f6b; text-transform: none; letter-spacing: 0; font-weight: 500; }
    .dc-depts { list-style: none; margin: 0; padding: 0; }
    .dc-depts li { display: flex; justify-content: space-between; font-size: 0.8125rem; color: #4b4f6b; padding: 3px 0; }
    .dc-depts span { font-weight: 600; color: #1f2235; }
    .dc-badges, .dc-chips { display: flex; flex-wrap: wrap; gap: 6px; list-style: none; margin: 12px 0 0; padding: 0; }
    .dc-chips { margin-top: 0; }
    .dc-badges li, .dc-chips li { font-size: 0.6875rem; font-weight: 600; color: #5b4bd1; background: #f1efff; border-radius: 9999px; padding: 4px 10px; line-height: 1.4; }
    .dc-chips li { color: #4b4f6b; background: #f4f4f8; }
    .dc-tracks { list-style: none; margin: 0; padding: 0; }
    .dc-tracks li { font-size: 0.8125rem; color: #1f2235; padding: 3px 0; }
    .dc-tracks span { color: #8a8fa6; margin-left: 6px; font-size: 0.75rem; }
    .dc-kvs { margin: 0; }
    .dc-kv { padding: 7px 0; border-bottom: 1px solid #f2f1f8; }
    .dc-kv:last-child { border-bottom: 0; }
    .dc-kv dt { font-size: 0.6875rem; font-weight: 600; color: #8a8fa6; letter-spacing: 0.04em; text-transform: uppercase; }
    .dc-kv dd { font-size: 0.8125rem; color: #1f2235; margin: 2px 0 0; line-height: 1.45; }
    .dc-out { display: flex; flex-wrap: wrap; gap: 4px 24px; }
    .dc-details { border-top: 1px solid #ececf4; }
    .dc-details + .dc-details { border-top-color: #f2f1f8; }
    .dc-details > summary { cursor: pointer; list-style: none; padding: 14px 28px; font-size: 0.8125rem; font-weight: 600; color: #6c5ce7; display: flex; align-items: center; gap: 8px; }
    .dc-details > summary::-webkit-details-marker { display: none; }
    .dc-details > summary::before { content: '+'; display: inline-flex; width: 18px; height: 18px; align-items: center; justify-content: center; border-radius: 50%; background: #f1efff; font-size: 0.875rem; line-height: 1; }
    .dc-details[open] > summary::before { content: '–'; }
    .dc-details > summary:hover { background: #faf9ff; }
    .dc-details > summary:focus-visible { outline: 2px solid #6c5ce7; outline-offset: -2px; }
    .dc-details > .dc-more { border-top: 1px solid #ececf4; }
    .dc-sources { font-size: 0.6875rem; color: #8a8fa6; line-height: 1.7; padding: 14px 28px 16px; border-top: 1px solid #ececf4; margin: 0; }
    .dc-sources .dc-src { font-weight: 500; color: #6b6f88; }
    /* Mobile */
    @media (max-width: 767px) {
      .dc-stage { flex-direction: column; }
      .dc-col-l, .dc-col-r { flex: none; }
      .dc-divider-v { width: 100%; height: 1px; }
      .dc-cell { padding: 18px; }
      .dc-header { padding: 18px; }
      .dc-details > summary, .dc-sources { padding-left: 18px; padding-right: 18px; }
      .dc-mcat-big { font-size: 2.5rem; }
      .dc-selectivity-body { flex-direction: column; gap: 10px; }
      .dc-gpa-wrap { width: 100%; }
    }'''

VOICES_JUMP_CSS = '''
    /* Floating "jump to student interviews" link */
    .voices-jump {
      position: fixed; left: 24px; bottom: 32px; z-index: 40;
      display: inline-flex; align-items: center; gap: 10px;
      padding: 10px 16px 10px 12px; border-radius: 9999px;
      background: #fff; color: #333e4d; text-decoration: none;
      border: 1px solid rgba(149,128,255,.35);
      box-shadow: 0 8px 24px -8px rgba(61,32,163,.25), 0 2px 6px rgba(31,34,53,.06);
      font: 600 13px/1.2 Inter, sans-serif;
      transition: opacity .2s ease-out, transform .2s ease-out, box-shadow .15s ease-out;
    }
    .voices-jump:hover { box-shadow: 0 10px 28px -8px rgba(61,32,163,.35), 0 2px 6px rgba(31,34,53,.08); color: #3d20a3; }
    .voices-jump:focus-visible { outline: 3px solid #9580FF; outline-offset: 3px; }
    .voices-jump-icon {
      width: 28px; height: 28px; border-radius: 50%; background: #9580FF; color: #fff;
      display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;
    }
    .voices-jump-icon svg { animation: voices-nudge 2.2s ease-in-out infinite; }
    .voices-jump-sub { display: block; font-weight: 500; font-size: 11px; color: #4A5565; margin-top: 2px; }
    .voices-jump.is-hidden { opacity: 0; transform: translateY(8px); pointer-events: none; visibility: hidden;
      transition: opacity .2s ease-in, transform .2s ease-in, visibility 0s linear .2s; }
    @keyframes voices-nudge { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(3px); } }
    @media (max-width: 767px) {
      .voices-jump { left: 16px; bottom: 16px; padding: 8px 14px 8px 8px; font-size: 12px; }
      .voices-jump-sub { display: none; }
    }
    @media (prefers-reduced-motion: reduce) {
      .voices-jump, .voices-jump.is-hidden { transition: none; }
      .voices-jump-icon svg { animation: none; }
    }'''

# Hides the link while the interviews are on screen (or the page is too short to need it)
# and scrolls smoothly unless the visitor prefers reduced motion.
VOICES_JUMP_JS = '''<script>
(function () {
  var link = document.querySelector('.voices-jump');
  var target = document.getElementById('student-voices');
  if (!link || !target) return;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function update() {
    var top = target.getBoundingClientRect().top;
    link.classList.toggle('is-hidden', top < window.innerHeight * 0.85);
  }
  link.addEventListener('click', function (e) {
    e.preventDefault();
    target.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    var heading = target.querySelector('h2');
    if (heading) { heading.setAttribute('tabindex', '-1'); heading.focus({ preventScroll: true }); }
  });
  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  update();
})();
</script>'''

NATIONAL_AVG_MCAT = 502
US_MEDIAN_RENT = 1413          # U.S. median gross rent, Census ACS 2020–2024 (QuickFacts HSG860224)
# Right half of the MCAT bell curve drawn in the dashboard SVG (cubic Bézier, viewBox 200×78)
_CURVE_LEFT  = [(0, 70), (38, 70), (70, 4), (91, 4)]
_CURVE_RIGHT = [(91, 4), (112, 4), (148, 70), (200, 70)]
DONUT_CIRCUMFERENCE = 2 * math.pi * 21   # r=21 → 131.95
FUNNEL_WIDTHS = {'applied': (100, '.45'), 'interviewed': (55, '.6'), 'admitted': (38, '.8'), 'enrolled': (26, None)}   # decorative steps


def _esc(text):
    return html_mod.escape(str(text), quote=False)


def _md_inline(text):
    """Escape text and turn **bold** into the highlight-card strong style."""
    return re.sub(r'\*\*(.+?)\*\*', r'<strong class="text-primary font-semibold">\1</strong>', _esc(text))


def _ordinal(n):
    n = int(n)
    suffix = 'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f'{n}{suffix}'


def _money_k(dollars):
    return f'${dollars / 1000:.1f}K'


def _count(value):
    """Display a count as written in the YAML; plain integers get thousands separators."""
    return f'{value:,}' if isinstance(value, int) else _esc(value)


def _to_number(value):
    digits = re.sub(r'[^\d.]', '', str(value))
    return float(digits) if digits else None


def _curve_y(x):
    """Height of the bell curve at x, so the MCAT marker sits exactly on the line."""
    pts = _CURVE_RIGHT if x >= 91 else _CURVE_LEFT
    lo, hi = 0.0, 1.0
    for _ in range(40):
        t = (lo + hi) / 2
        bx = sum(c * p[0] for c, p in zip(((1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t**2, t**3), pts))
        lo, hi = (t, hi) if bx < x else (lo, t)
    t = lo
    return sum(c * p[1] for c, p in zip(((1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t**2, t**3), pts))


def _cell(label, body):
    return f'''          <div class="dc-cell">
            <div class="dc-cell-label">{label}</div>
{body}
          </div>'''


def _selectivity_cell(s):
    mcat  = s['mcat']
    kind  = s.get('stats_kind', 'median')          # "median", "average", or "reported" when the school doesn't say
    shown = round(mcat)
    delta = shown - NATIONAL_AVG_MCAT
    good  = f'+{delta} above national average' if delta >= 0 else f'{delta} below national average'

    x  = round(min(196, max(4, 91 + delta * 2.64)))
    cy = round(_curve_y(x))
    # Keep the national-average label clear of the school's score label when they're close
    avg_x, avg_anchor = (84, 'middle') if abs(x - 84) > 36 else (x - 12, 'end')
    curve = f'''              <div class="dc-curve-wrap">
                <svg viewBox="0 0 200 78" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;display:block">
                  <path d="M0,70 C38,70 70,4 91,4 C112,4 148,70 200,70" fill="rgba(139,127,255,0.13)"/>
                  <path d="M0,70 C38,70 70,4 91,4 C112,4 148,70 200,70" fill="none" stroke="#8b7fff" stroke-width="1.5"/>
                  <line x1="91" y1="4" x2="91" y2="70" stroke="#b4b8cd" stroke-dasharray="3,2" stroke-width="1"/>
                  <line x1="{x}" y1="{cy + 2}" x2="{x}" y2="70" stroke="#5b4bd1" stroke-width="1.5"/>
                  <circle cx="{x}" cy="{cy}" r="3.5" fill="#5b4bd1"/>
                  <text x="{avg_x}" y="78" text-anchor="{avg_anchor}" font-size="7.5" fill="#8a8fa6" font-family="Inter,sans-serif">nat. avg {NATIONAL_AVG_MCAT}</text>
                  <text x="{x}" y="78" text-anchor="middle" font-size="7.5" fill="#1f2235" font-weight="700" font-family="Inter,sans-serif">{shown}</text>
                </svg>
              </div>'''

    gpa_rows = ''
    for key, tag in (('gpa_science', 'Science'), ('gpa_overall', 'Overall')):
        if s.get(key):
            width = round(min(100, max(2, (s[key] - 3.0) * 100 - 2)))
            gpa_rows += f'''
                <div class="dc-gpa-row">
                  <span class="dc-gpa-num">{s[key]:.2f}</span>
                  <div class="dc-gpa-bar-bg"><div class="dc-gpa-bar-fill" style="width:{width}%"></div></div>
                  <span class="dc-gpa-tag">{tag}</span>
                </div>'''
    gpa = (f'''
              <div class="dc-gpa-wrap">{gpa_rows}
                <div class="dc-gpa-meta">{'Undergraduate GPA' if s.get('gpa_kind', kind) == 'reported' else s.get('gpa_kind', kind).capitalize() + ' undergraduate GPA'}</div>
              </div>''') if gpa_rows else ''

    if s.get('cohort_label'):
        label = f'Selectivity · {_esc(s["cohort_label"])}'
    else:
        label = 'Selectivity' + (f' · Entering class of {s["entering_class"]}' if s.get('entering_class') else '')
    return _cell(label, f'''            <div>
              <span class="dc-mcat-big">{shown}</span><span class="dc-mcat-unit">{'' if kind == 'reported' else kind + ' '}MCAT</span>
              <div class="dc-good">{good}</div>
            </div>
            <div class="dc-selectivity-body">
{curve}{gpa}
            </div>''')


def _cost_row(label, dollars, width, strong=False):
    cls = 'dc-cost-bar-fill dc-cost-strong' if strong else 'dc-cost-bar-fill'
    return f'''            <div class="dc-cost-row">
              <div class="dc-cost-row-head">
                <span class="dc-cost-label">{label}</span>
                <span class="dc-cost-amt">{_money_k(dollars)}<span class="dc-cost-per">/yr</span></span>
              </div>
              <div class="dc-cost-bar-bg"><div class="{cls}" style="width:{width}%"></div></div>
            </div>'''


def _cost_cell(s, is_public):
    notes = []
    if s.get('tuition_in_state') and s.get('tuition_out_of_state'):
        ins, outs = s['tuition_in_state'], s['tuition_out_of_state']
        rows = '\n'.join([
            _cost_row('In-state tuition &amp; fees', ins, int(ins / outs * 100)),
            _cost_row('Out-of-state tuition &amp; fees', outs, 100, strong=True),
        ])
        diff = outs - ins
        notes.append(f'{_money_k(diff)} more per year for non-residents')
    elif s.get('tuition_in_state'):
        rows = _cost_row('In-state tuition &amp; fees', s['tuition_in_state'], 100)
        notes.append('Out-of-state rate not published on the cited page')
    elif s.get('tuition'):
        rows = _cost_row('Annual tuition', s['tuition'], 100)
        notes.append('Same tuition for all students')
    else:
        rows = ''   # rent only: tuition not published on an official page
    if s.get('tuition_note'):          # replaces the default residency note when the school's situation differs
        notes = [_esc(s['tuition_note'])]
    if s.get('total_cost'):
        note = f'~${round(s["total_cost"] / 1000)}K est. 4-year cost of attendance'
        if s.get('total_cost_note'):
            note += f' ({_esc(s["total_cost_note"])})'
        notes.append(note)
    label = ('Cost of Attendance' if rows else 'Cost of Living') + (f' · {_esc(s["cost_year"])}' if s.get('cost_year') else '')
    rent = ''
    if s.get('col'):
        col = s['col']
        ratio = col['median_rent'] / US_MEDIAN_RENT
        rent = (f'\n            <div class="dc-rent"><span class="dc-rent-label">Median rent · {_esc(col["county"])}</span>'
                f'<span class="dc-rent-amt">${col["median_rent"]:,}<span class="dc-cost-per">/mo</span></span></div>'
                f'\n            <div class="dc-cost-note">{ratio:.1f}× the U.S. median (${US_MEDIAN_RENT:,}) · Census ACS {_esc(col.get("acs_year", ""))}</div>')
    note_html = f'\n            <div class="dc-cost-note">{" · ".join(notes)}</div>' if notes else ''
    return _cell(label, rows + note_html + rent)


def _donut(pct, label, color):
    filled = round(pct / 100 * DONUT_CIRCUMFERENCE, 1)
    gap    = round(DONUT_CIRCUMFERENCE - filled, 1)
    return f'''              <div class="dc-donut-item">
                <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
                  <circle cx="28" cy="28" r="21" stroke="#e3dfff" stroke-width="5"/>
                  <circle cx="28" cy="28" r="21" stroke="{color}" stroke-width="5"
                    stroke-dasharray="{filled} {gap}" stroke-linecap="round"
                    transform="rotate(-90 28 28)"/>
                  <text x="28" y="32" text-anchor="middle" font-size="10" font-weight="700" fill="#1f2235" font-family="Inter,sans-serif">{pct}%</text>
                </svg>
                <div class="dc-donut-labels"><h4>{pct}%</h4><p>{label}</p></div>
              </div>'''


def _profile_cell(s, degree):
    donuts = [_donut(s[k], label, color) for k, label, color in
              (('women_pct', 'Women', '#6c5ce7'), ('out_of_state_pct', 'Out-of-State', '#b4b8cd')) if s.get(k)]
    stats = [f'<div class="dc-profile-stat"><h4>{_count(s[k])}</h4><p>{label}</p></div>' for k, label in
             (('class_size', 'Class Size'), ('total_students', f'Total {degree} Students')) if s.get(k)]
    body = ''
    if donuts:
        body += '            <div class="dc-donuts">\n' + '\n'.join(donuts) + '\n            </div>'
    if stats:
        body += ('\n' if body else '') + '            <div class="dc-profile-stats">\n' + \
                '\n'.join('              ' + st for st in stats) + '\n            </div>'
    return _cell('Class Profile', body)


def _money_big(dollars):
    return f'${dollars / 1e9:.1f}B' if dollars >= 1e9 else f'${round(dollars / 1e6)}M'


def _reach_cell(s):
    funnel_rows = []
    stages = (('applied', 'Applied'), ('interviewed', 'Interviewed'), ('admitted', 'Admitted'), ('enrolled', 'Enrolled'))
    for key, label in stages:
        if s.get(key):
            width, opacity = FUNNEL_WIDTHS[key]
            op = f';opacity:{opacity}' if opacity else ''
            funnel_rows.append(f'''                <div class="dc-funnel-row">
                  <div class="dc-funnel-label-row"><span class="dc-funnel-name">{label}</span><span class="dc-funnel-num">{_count(s[key])}</span></div>
                  <div class="dc-funnel-bar-bg"><div class="dc-funnel-bar-fill" style="width:{width}%{op}"></div></div>
                </div>''')
    applied = _to_number(s.get('applied', ''))
    if s.get('acceptance_rate'):
        funnel_rows.append(f'                <div class="dc-funnel-note">{_esc(s["acceptance_rate"])} acceptance rate</div>')
    elif applied and s.get('admitted'):
        funnel_rows.append(f'                <div class="dc-funnel-note">{_to_number(s["admitted"]) / applied * 100:.1f}% of applicants admitted</div>')
    elif applied and s.get('enrolled'):
        funnel_rows.append(f'                <div class="dc-funnel-note">{_to_number(s["enrolled"]) / applied * 100:.1f}% of applicants enrolled</div>')

    aside = []
    if s.get('nih_funding'):
        label = (s.get('nih_label') or 'NIH funding · FY{year}').replace('{year}', str(s['nih_year']))
        aside.append(f'<div class="dc-reach-stat"><h4>{_money_big(s["nih_funding"])}</h4><p>{_esc(label)}</p></div>')
    if s.get('faculty'):
        aside.append(f'<div class="dc-reach-stat"><h4>{_count(s["faculty"])}</h4><p>{_esc(s.get("faculty_label", "Faculty Members"))}</p></div>')
    if s.get('beds'):
        aside.append(f'<div class="dc-reach-stat"><h4>{_count(s["beds"])}</h4><p>{_esc(s.get("beds_label", "Hospital Beds"))}</p></div>')

    body = '            <div class="dc-reach-body">'
    if funnel_rows:
        body += '\n              <div class="dc-funnel">\n' + '\n'.join(funnel_rows) + '\n              </div>'
    if aside:
        body += '\n              <div class="dc-reach-aside">\n' + '\n'.join('                ' + a for a in aside) + '\n              </div>'
    return _cell('Scale &amp; Reach', body + '\n            </div>')


def _source_links(sources):
    return ' · '.join(
        f'<a href="{html_mod.escape(src["url"])}" target="_blank" rel="noopener noreferrer" class="dc-src">{_esc(src["label"])}</a>'
        if src.get('url') else _esc(src['label']) for src in sources)


_CMS_TYPE = {'Acute Care Hospitals': 'Acute care', 'Childrens': "Children's", 'Psychiatric': 'Psychiatric',
             'Acute Care - Veterans Administration': 'VA', 'Critical Access Hospitals': 'Critical access'}
_CMS_OWNER = [('Government', 'Public'), ('Veterans', ''), ('Voluntary', 'Non-profit'), ('Proprietary', 'For-profit'),
              ('Physician', 'For-profit'), ('Tribal', 'Tribal')]
SITES_SHOWN = 6


def _stars(n):
    filled = '★' * n + '<span class="dc-star-off">' + '★' * (5 - n) + '</span>'
    return f'<span class="dc-stars" title="CMS overall hospital rating: {n} of 5" aria-label="CMS rating {n} of 5">{filled}</span>'


def _sites_cell(sites, hospitals):
    rows, rest = [], []
    for i, site in enumerate(sites):
        cms = hospitals.get(str(site.get('cms_id'))) if site.get('cms_id') else None
        if i >= SITES_SHOWN:
            rest.append(_esc(site['name']))
            continue
        tags = []
        if cms:
            if _CMS_TYPE.get(cms.get('type')):
                tags.append(_CMS_TYPE[cms['type']])
            owner = next((label for key, label in _CMS_OWNER if key in (cms.get('ownership') or '')), '')
            if owner:
                tags.append(owner)
            if cms.get('emergency'):
                tags.append('ER')
        if site.get('role'):
            meta = ' · '.join([_esc(site['role'])] + (['ER'] if 'ER' in tags else []))
        else:
            meta = ' · '.join(tags)
        stars = _stars(cms['stars']) if cms and cms.get('stars') else ''
        rows.append(f'''              <li class="dc-site">
                <div><div class="dc-site-name">{_esc(site['name'])}</div><div class="dc-site-meta">{meta}</div></div>
                {stars}
              </li>''')
    more = (f'\n            <p class="dc-site-more">+{len(rest)} more: {", ".join(rest)}</p>') if rest else ''
    rated = any(h and h.get('stars') for h in hospitals.values() if isinstance(h, dict))
    foot = ('\n            <p class="dc-foot">★ CMS overall hospital rating (1–5). Children\'s, cancer and '
            'psychiatric hospitals aren\'t rated.</p>') if rated else ''
    label = f'Clinical Training Sites · {len(sites)}'
    return _cell(label, f'''            <ul class="dc-sites">
{chr(10).join(rows)}
            </ul>{more}{foot}''').replace('<div class="dc-cell">', '<div class="dc-cell dc-cell-wide">', 1)


def _trend_svg(trend):
    years = sorted(trend)
    peak = max(trend.values()) or 1
    bars = []
    for i, y in enumerate(years):
        h = max(3, round(trend[y] / peak * 34))
        x = i * 30
        last = i == len(years) - 1
        bars.append(f'<rect x="{x}" y="{40 - h}" width="20" height="{h}" rx="3" fill="{"#6c5ce7" if last else "#c9c2ff"}"/>'
                    f'<text x="{x + 10}" y="52" text-anchor="middle" font-size="8" fill="#8a8fa6" font-family="Inter,sans-serif">\'{y[-2:]}</text>')
    width = len(years) * 30 - 10
    return (f'<svg viewBox="0 0 {width} 54" width="{width}" height="54" role="img" '
            f'aria-label="NIH funding by fiscal year, {years[0]} to {years[-1]}">{"".join(bars)}</svg>')


def _research_cell(nih, trials, badges, trials_label):
    parts = []
    if nih.get('trend') and len(nih['trend']) > 1:
        years = sorted(nih['trend'])
        first, last = nih['trend'][years[0]], nih['trend'][years[-1]]
        change = f'{(last - first) / first * 100:+.0f}% since FY{years[0]}' if first else ''
        parts.append(f'''            <div class="dc-trend">
              {_trend_svg(nih['trend'])}
              <div><h4>{_money_big(last)}</h4><p>NIH · FY{years[-1]}</p><p class="dc-trend-chg">{change}</p></div>
            </div>''')
    if nih.get('top_departments'):
        depts = ''.join(f'<li>{_esc(d["dept"])}<span>{_money_big(d["amount"])}</span></li>' for d in nih['top_departments'])
        parts.append(f'            <p class="dc-sub">Top NIH-funded departments</p>\n            <ul class="dc-depts">{depts}</ul>')
    chips = [f'<span title="{_esc(b)}">{_esc(b.split(" · ")[0])}</span>' for b in badges]
    if nih.get('mstp'):
        chips.append('NIH-funded MD-PhD (MSTP)')
    if nih.get('ctsa'):
        chips.append('NIH clinical &amp; translational science hub')
    if trials and trials.get('recruiting'):
        chips.append(f'{trials["recruiting"]:,} recruiting clinical trials' + (f' ({_esc(trials_label)})' if trials_label else ''))
    if chips:
        parts.append('            <ul class="dc-badges">' + ''.join(f'<li>{c}</li>' for c in chips) + '</ul>')
    return _cell('Research Depth', '\n'.join(parts))


def _programs_cell(programs):
    out = []
    if programs.get('tracks'):
        out.append('            <p class="dc-sub">Tracks &amp; programs</p>\n            <ul class="dc-tracks">' + ''.join(
            f'<li><strong>{_esc(t["name"])}</strong>' + (f'<span>{_esc(t["note"])}</span>' if t.get('note') else '') + '</li>'
            for t in programs['tracks']) + '</ul>')
    if programs.get('dual_degrees'):
        out.append('            <p class="dc-sub">Dual degrees</p>\n            <ul class="dc-chips">' +
                   ''.join(f'<li>{_esc(d)}</li>' for d in programs['dual_degrees']) + '</ul>')
    return _cell('Programs &amp; Tracks', '\n'.join(out))


def _applying_cell(items):
    rows = ''.join(f'<div class="dc-kv"><dt>{_esc(i["label"])}</dt><dd>{_esc(i["value"])}</dd></div>' for i in items)
    return _cell('Applying', f'            <dl class="dc-kvs">{rows}</dl>')


def _outcomes_cell(o):
    stats = []
    if o.get('match_rate'):
        stats.append((_esc(o['match_rate']), f'Residency match rate · {o.get("match_year", "")}'.rstrip(' ·')))
    if o.get('avg_debt'):
        stats.append((f'${o["avg_debt"]:,}', 'Avg. debt at graduation'))
    if o.get('avg_scholarship'):
        stats.append((f'${o["avg_scholarship"]:,}', 'Avg. scholarship'))
    if o.get('aid_pct'):
        stats.append((f'{o["aid_pct"]}%', 'Receive financial aid'))
    if o.get('scholarship_pct'):
        stats.append((f'{o["scholarship_pct"]}%', 'Receive a scholarship'))
    body = '            <div class="dc-out">' + ''.join(
        f'<div class="dc-reach-stat"><h4>{v}</h4><p>{label}</p></div>' for v, label in stats) + '</div>'
    if o.get('avg_debt_note'):
        body += f'\n            <p class="dc-foot">Debt comparison: {_esc(o["avg_debt_note"])}</p>'
    if o.get('note'):
        body += f'\n            <p class="dc-foot">{_esc(o["note"])}</p>'
    return _cell('Outcomes', body)


def _toggle(names, cells):
    """A collapsed <details> band; the summary names whatever sections are inside."""
    title = (', '.join(names[:-1]) + ' &amp; ' + names[-1]) if len(names) > 1 else names[0]
    title = title[0].upper() + title[1:]
    return (f'\n      <details class="dc-details">\n        <summary>{title}</summary>'
            f'\n        <div class="dc-more">\n' + '\n'.join(cells) + '\n        </div>\n      </details>')


def render_extras(page, raw):
    """Optional bands below the headline stats, each folded into its own toggle so the card
    opens on the key numbers. A band (and each cell in it) appears only when data exists."""
    html = ''
    # Level 2 — clinical training & research
    level2 = []
    if page.get('clinical_sites'):
        level2.append(('clinical training', _sites_cell(page['clinical_sites'], raw.get('hospitals') or {})))
    nih = raw.get('nih') or {}
    if nih or page.get('research_badges') or raw.get('trials'):
        level2.append(('research', _research_cell(nih, raw.get('trials'), page.get('research_badges') or [], page.get('trials_label'))))
    if level2:
        html += _toggle([n for n, _ in level2], [c for _, c in level2])
    # Level 3 — programs, admissions & outcomes
    level3 = []
    if page.get('programs'):
        level3.append(('programs', _programs_cell(page['programs'])))
    if page.get('applying'):
        level3.append(('admissions', _applying_cell(page['applying'])))
    if page.get('outcomes'):
        level3.append(('outcomes', _outcomes_cell(page['outcomes'])))
    if level3:
        html += _toggle([n for n, _ in level3], [c for _, c in level3])
    return html


def render_dashboard(stats, school, extras=''):
    """Editorial stats card. Each cell appears only when its numbers are in the YAML."""
    s = stats
    left, right = [], []
    if s.get('mcat'):
        left.append(_selectivity_cell(s))
    if s.get('tuition') or s.get('tuition_in_state') or s.get('col'):
        left.append(_cost_cell(s, school['public']))
    # Class size alone already shows in the hero line, so the tile needs at least one more figure
    if any(s.get(k) for k in ('women_pct', 'out_of_state_pct', 'total_students')):
        right.append(_profile_cell(s, 'MD' if school['type'] == 'md' else 'DO'))
    if any(s.get(k) for k in ('applied', 'interviewed', 'admitted', 'enrolled', 'nih_funding', 'faculty', 'beds')):
        right.append(_reach_cell(s))

    # Nothing for the right column (no class profile or NIH funding): split the left cells across both
    if not right and len(left) > 1:
        right = [left.pop()]

    cols = []
    if left:
        cols.append('        <div class="dc-col dc-col-l">\n' + '\n'.join(left) + '\n        </div>')
    if right:
        cols.append('        <div class="dc-col dc-col-r">\n' + '\n'.join(right) + '\n        </div>')
    stage = '\n        <div class="dc-divider-v"></div>\n'.join(cols)

    sources = s.get('sources') or []
    meta = 'Official school figures and U.S. government data · sources below' if sources else ''
    footer = (f'\n      <p class="dc-sources">Sources: {_source_links(sources)}</p>') if sources else ''
    link = ''
    if s.get('profile_url'):
        link = f'''
        <a href="{html_mod.escape(s['profile_url'])}"
           target="_blank" rel="noopener noreferrer" class="dc-sdn-link">
          Official class profile
          <svg width="11" height="11" viewBox="0 0 12 12" fill="none"><path d="M10 2H7m3 0v3M10 2L5.5 6.5M3 2H2a1 1 0 00-1 1v7a1 1 0 001 1h7a1 1 0 001-1V9" stroke="#6c5ce7" stroke-width="1.4" stroke-linecap="round"/></svg>
        </a>'''

    return f'''  <!-- STATS DASHBOARD -->
  <div class="max-w-[1200px] mx-auto px-margin-mobile md:px-margin-desktop py-xl">
    <div class="dc-card">
      <div class="dc-header">
        <div>
          <h2>Program Statistics</h2>
          <p class="dc-meta">{meta}</p>
        </div>{link}
      </div>
      <div class="dc-stage">
{stage}
      </div>{extras}{footer}
    </div>
  </div>'''


def render_highlights(highlights, sources=None):
    cards = []
    for h in highlights:
        paras = '\n'.join(
            f'            <p class="font-body-md text-body-md text-slate-gray leading-relaxed">\n'
            f'              {_md_inline(" ".join(str(p).split()))}\n'
            f'            </p>' for p in h.get('paragraphs', []))
        cards.append(f'''        <div class="bg-white border border-primary/5 rounded-xl p-lg shadow-sm flex flex-col gap-md">
          <div class="flex items-center gap-sm">
            <div class="w-10 h-10 rounded-xl bg-vibrant-iris/10 flex items-center justify-center flex-shrink-0">
              <span class="material-symbols-outlined text-vibrant-iris text-[20px]" style="font-variation-settings:&apos;FILL&apos; 1">{_esc(h.get('icon', 'star'))}</span>
            </div>
            <h3 class="font-headline-md text-headline-md text-primary">{_esc(h['title'])}</h3>
          </div>
          <div class="space-y-sm">
{paras}
          </div>
        </div>''')
    source_line = ''
    if sources:
        source_line = (f'\n      <p class="font-body-md text-xs text-slate-gray mt-lg leading-relaxed">'
                       f'Sources: {_source_links(sources)}</p>')
    return f'''  <!-- PROGRAM HIGHLIGHTS -->
  <div class="bg-surface-container-low border-y border-primary/5">
    <div class="max-w-[1200px] mx-auto px-margin-mobile md:px-margin-desktop py-xl">
      <h2 class="font-headline-lg text-headline-lg text-primary mb-lg">Program Highlights</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-lg">
{chr(10).join(cards)}
      </div>{source_line}
    </div>
  </div>'''


def render_voice_card(school_slug, fm, body, student_slug, quote=None):
    iv_name = fm.get('name', 'Anonymous')
    iv_year = fm.get('year', '')
    iv_ug   = fm.get('undergraduate', '')
    iv_home = fm.get('hometown', fm.get('location', ''))

    ug_short = ''
    if iv_ug:
        ug_short = iv_ug.split('(')[0].split(',')[0].strip()

    meta_parts = [p for p in [iv_year, (ug_short + ' undergrad') if ug_short else '', iv_home] if p]
    meta_str = ' · '.join(meta_parts)

    quote  = _esc(' '.join(quote.split())) if quote else extract_quote(body)
    inits  = initials(iv_name)
    iv_url = f'/interviews/{school_slug}/{student_slug}/index.html'

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


def _seo_title_description(name, city, state, degree, stats, n):
    """Search title and snippet built from the same official figures the page shows."""
    has_cost = any(stats.get(k) for k in ('tuition', 'tuition_in_state'))
    title = f'{name}: Student Interviews, Stats & Costs | DocStory' if has_cost else f'{name}: Student Interviews & Stats | DocStory'
    facts = []
    if stats.get('mcat'):
        mcat = round(float(stats['mcat']))
        facts.append(f'average MCAT {mcat}' if stats.get('stats_kind') == 'average' else f'MCAT {mcat}')
    if stats.get('gpa_overall'):
        facts.append(f'GPA {float(stats["gpa_overall"]):.2f}')
    if stats.get('class_size'):
        facts.append(f'class size {stats["class_size"]}')
    ivs = f'{n} student interviews' if n != 1 else 'A student interview'
    base = f'What is {name} ({degree}, {city}, {state}) really like? {ivs} on daily life, curriculum, and culture'
    full = base + (f', plus official figures: {", ".join(facts)}.' if facts else '.')
    return title, (full if len(full) <= 200 else base + '.')


def render_page(school_slug, data, interviews, page=None):
    name     = data['name']
    city     = data['city']
    state    = data['state']
    pub      = 'Public' if data['public'] else 'Private'
    stats    = merged_stats(school_slug, page, data)
    founded  = stats.get('founded') or ''
    hospital = data.get('hospital', '')
    class_sz = stats.get('class_size') or ''
    type_lbl = 'Allopathic (MD)' if data['type'] == 'md' else 'Osteopathic (DO)'
    degree   = 'MD' if data['type'] == 'md' else 'DO'

    page = page or {}
    sub_parts = [_esc(page['location_line']) if page.get('location_line') else f'{city}, {state}']
    if hospital:
        sub_parts.append(f'<span class="text-primary font-medium">{html_mod.escape(hospital, quote=False)}</span>')
    if class_sz:
        sub_parts.append(f'{class_sz} students per class')
    hero_sub = ' · '.join(sub_parts)

    founded_badge = (f'<span class="px-sm py-1 bg-surface-container-high text-slate-gray rounded-full'
                     f' font-label-md text-[11px]">Founded {founded}</span>') if founded else ''

    # Featured quotes from the YAML also set card order; unlisted interviews follow alphabetically
    quotes = page.get('quotes') or {}
    order  = list(quotes)
    interviews = sorted(interviews, key=lambda iv: (order.index(iv[2]) if iv[2] in order else len(order), iv[2]))

    n = len(interviews)
    iv_label   = f'{n} interview{"s" if n != 1 else ""}'
    grid_cols  = 'md:grid-cols-3' if n >= 3 else ('md:grid-cols-2' if n == 2 else 'md:grid-cols-1')
    voices_html = '\n'.join(render_voice_card(school_slug, fm, body, slug, quotes.get(slug)) for fm, body, slug in interviews)

    sdn_url = 'https://www.studentdoctor.net/schools-database/medical-school/'

    has_dashboard = page and (
        any(stats.get(k) for k in ('mcat', 'tuition', 'tuition_in_state', 'nih_funding', 'faculty', 'beds', 'applied', 'women_pct', 'out_of_state_pct'))
        or any(page.get(k) for k in ('clinical_sites', 'programs', 'applying', 'outcomes')))
    if page and (has_dashboard or page.get('highlights')):
        # Full page: dashboard, highlights band, then voices on the plain background
        extra_css = DASHBOARD_CSS if has_dashboard else ''
        short = f' {_esc(page["short_name"])}' if page.get('short_name') else ''
        _, _, raw = load_fetched(school_slug)
        col = dict(page.get('cost_of_living') or {})
        if raw.get('rent'):
            col.update(median_rent=raw['rent']['median_rent'], acs_year=raw['rent']['acs_year'])
        if col.get('median_rent'):
            stats['col'] = col
        sections = [render_dashboard(stats, data, render_extras(page, raw))] if has_dashboard else []
        if page.get('highlights'):
            sections.append(render_highlights(page['highlights'], page.get('highlight_sources')))
        sections.append(f'''  <!-- STUDENT VOICES -->
  <div id="student-voices" class="max-w-[1200px] mx-auto px-margin-mobile md:px-margin-desktop py-xl scroll-mt-[90px]">
    <div class="flex items-baseline justify-between flex-wrap gap-sm mb-lg">
      <div>
        <h2 class="font-headline-lg text-headline-lg text-primary">Student Voices</h2>
        <p class="font-body-md text-xs text-slate-gray mt-1">{iv_label} from current and former{short} students</p>
      </div>
    </div>
    <div class="grid grid-cols-1 {grid_cols} gap-lg">
{voices_html}
    </div>
  </div>''')
        middle = '\n\n'.join(sections)
    else:
        extra_css = ''
        middle = f'''  <!-- STATS PANEL -->
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
  <div id="student-voices" class="bg-surface-container-low border-y border-primary/5 scroll-mt-[90px]">
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
  </div>'''

    page_title, description = _seo_title_description(name, city, state, degree, stats, n)
    page_path = f'/schools/{school_slug}/'
    school_ld = {'@type': 'CollegeOrUniversity', 'name': name,
                 'address': {'@type': 'PostalAddress', 'addressLocality': city, 'addressRegion': state,
                             'addressCountry': 'US'}}
    if founded:
        school_ld['foundingDate'] = str(founded)
    head_seo = seo.head_tags(page_title, description, page_path, jsonld=[
        {'@type': 'WebPage', 'name': page_title.replace(' | DocStory', ''), 'url': seo.url(page_path),
         'description': description, 'about': school_ld, 'publisher': {'@id': seo.SITE_URL + '/#organization'}},
        seo.breadcrumbs([('Home', '/'), ('Schools', '/directory/'), (name, page_path)]),
    ])

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html_mod.escape(page_title)}</title>
  <meta name="description" content="{html_mod.escape(description)}">
  {head_seo}
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
  <link href="/css/style.css" rel="stylesheet">
  {TAILWIND_CONFIG}
  <style>
    .line-clamp-4 {{ display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }}{VOICES_JUMP_CSS}{extra_css}
  </style>
</head>
<body class="bg-background text-on-background font-body-md antialiased flex flex-col min-h-screen selection:bg-vibrant-iris selection:text-white">

<!-- NAV -->
<nav class="bg-surface-container-lowest border-b border-primary/10 sticky top-0 z-50">
  <div class="flex justify-between items-center px-margin-mobile md:px-margin-desktop max-w-[1200px] mx-auto w-full h-[70px]">
    <a href="/index.html" class="flex items-center gap-2 font-bold text-headline-md text-primary">
      <span class="material-symbols-outlined text-vibrant-iris text-2xl" style="font-variation-settings:&apos;FILL&apos; 1">medical_services</span>DocStory
    </a>
    <div class="hidden md:flex items-center gap-lg h-full">
      <a href="/index.html" class="font-body-md text-body-md text-slate-gray hover:text-vibrant-iris transition-colors">Home</a>
      <a href="/directory/index.html" class="font-body-md text-body-md text-vibrant-iris border-b-2 border-vibrant-iris pb-1 font-medium">Interviews</a>
      <a href="/about/index.html" class="font-body-md text-body-md text-slate-gray hover:text-vibrant-iris transition-colors">About</a>
      <a href="/contribute/index.html" class="font-body-md text-body-md text-slate-gray hover:text-vibrant-iris transition-colors">Contribute<span data-get-paid class="ml-1.5 inline-flex items-center align-middle rounded-full bg-[#e8f5ee] text-[#1f7a4d] px-2 py-[3px] text-[11px] leading-none font-semibold tracking-wide whitespace-nowrap">Get Paid!</span></a>
    </div>
    <div class="flex items-center gap-2">
      <button class="bg-vibrant-iris text-white px-md py-xs rounded-full font-label-md text-label-md hover:opacity-90 active:scale-95 transition-all hidden md:block shadow-sm" data-signup>Join Now</button>
    </div>
  </div>
</nav>

<main class="flex-grow">

  <a href="#student-voices" class="voices-jump" aria-label="Jump to {iv_label} from students">
    <span class="voices-jump-icon" aria-hidden="true"><svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M7 2v9M3 7.5L7 11.5l4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
    <span>Student interviews<span class="voices-jump-sub">{iv_label} below</span></span>
  </a>

  <!-- HERO -->
  <div class="bg-surface-container-low border-b border-primary/5">
    <div class="max-w-[1200px] mx-auto px-margin-mobile md:px-margin-desktop pt-lg pb-xl">
      <a href="/directory/index.html" class="inline-flex items-center gap-xs text-slate-gray hover:text-vibrant-iris font-label-md text-label-md transition-colors mb-lg">
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

{middle}

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
        <a href="/about/index.html" class="text-slate-gray hover:text-vibrant-iris underline opacity-80 hover:opacity-100 transition-opacity font-body-md text-body-md">Mission</a>
        <a href="/contribute/index.html" class="text-slate-gray hover:text-vibrant-iris underline opacity-80 hover:opacity-100 transition-opacity font-body-md text-body-md">Contribute</a>
        <a href="#" class="text-slate-gray hover:text-vibrant-iris underline opacity-80 hover:opacity-100 transition-opacity font-body-md text-body-md">Contact Us</a>
        <a href="#" class="text-slate-gray hover:text-vibrant-iris underline opacity-80 hover:opacity-100 transition-opacity font-body-md text-body-md">Privacy Policy</a>
        <a href="#" class="text-slate-gray hover:text-vibrant-iris underline opacity-80 hover:opacity-100 transition-opacity font-body-md text-body-md">Terms of Service</a>
      </nav>
    </div>
  </div>
</footer>

{VOICES_JUMP_JS}
<script src="/js/contribute-config.js?v=2"></script>
<script src="/js/main.js?v=5"></script>
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

        page = load_school_data(slug)
        for missing in set((page or {}).get('quotes') or {}) - {iv[2] for iv in interviews}:
            print(f'  WARN  {slug}.yaml: quote for "{missing}" but no such interview file')
        html = render_page(slug, data, interviews, page)

        out_dir  = schools_dir / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / 'index.html'
        out_file.write_text(html, encoding='utf-8')

        n = len(interviews)
        kind = 'full ' if page else 'basic'
        print(f'  {kind} {str(out_file.relative_to(ROOT)):<65}  ({n} iv{"s" if n > 1 else ""})')
        generated += 1

    write_contribute_data(content_dir)
    warned += write_site_data(content_dir)
    write_sitemap_and_llms(content_dir)
    write_static_heads(content_dir)
    write_prerendered(content_dir)
    warned += write_vercel_config(content_dir)
    print(f'\nDone: {generated} pages generated, {skipped} skipped, {warned} warnings.')


def _norm_text(t):
    """Lowercase letters and digits only, so quote checks ignore punctuation, curly quotes and bold markers."""
    import unicodedata
    t = unicodedata.normalize('NFKD', str(t)).replace('\u2019', "'").replace('\u2018', "'").lower()
    return re.sub(r'[^a-z0-9]+', ' ', t).strip()


def _verified_pros_cons(slug, page, content_dir):
    """Excerpts for the homepage love/change card. Each must appear word for word in the student's
    interview (an ellipsis marks skipped text); anything that doesn't is dropped with a warning."""
    pc = page.get('pros_cons') or {}
    if not pc:
        return None, 0
    out, warnings = {}, 0
    for side in ('love', 'change'):
        items = []
        for item in pc.get(side) or []:
            f = content_dir / slug / f"{item.get('student', '')}.md"
            if not f.exists():
                print(f'  WARN  {slug}.yaml pros_cons: no interview "{item.get("student")}"'); warnings += 1; continue
            fm, body = parse_md(f)
            text = str(item.get('text', '')).strip()
            haystack = _norm_text(body)
            if not text or any(_norm_text(seg) not in haystack for seg in text.replace('**', '').split('…') if _norm_text(seg)):
                print(f'  WARN  {slug}.yaml pros_cons: not verbatim in {f.stem}.md, dropped: "{text[:60]}…"'); warnings += 1; continue
            items.append({'text': text, 'student': fm.get('name', '').split()[0] if fm.get('name') else '',
                          'year': fm.get('year', ''), 'studentSlug': f.stem})
        out[side] = items
    return (out if out.get('love') and out.get('change') else None), warnings


def _year_number(label):
    """'MS2', 'M2', 'OMS-2', 'OSM3', 'MS3 (MD/PhD)' → 2, 2, 2, 3, 3 (None if no year 1–4 found)."""
    m = re.search(r'[1-4]', str(label))
    return int(m.group()) if m else None


def write_site_data(content_dir):
    """Site-wide numbers and featured content for the homepage and directory (js/site-data.js).
    Everything is counted from content/ and the school data files, so nothing on those pages
    needs to be updated by hand. Returns the number of warnings printed."""
    schools, interviews = [], []
    warnings = 0
    for slug, data in SCHOOLS.items():
        iv_files = sorted((content_dir / slug).glob('*.md')) if (content_dir / slug).exists() else []
        page = load_school_data(slug) or {}
        quotes = page.get('quotes') or {}
        city = f"{data['city']}, {data['state']}"
        for f in iv_files:
            fm, _ = parse_md(f)
            q = ' '.join(str(quotes.get(f.stem, '')).split()).strip().strip('"').strip()
            interviews.append({'name': fm.get('name', 'Anonymous'), 'year': fm.get('year', ''),
                               'school': data['name'], 'schoolSlug': slug, 'studentSlug': f.stem,
                               'city': city, 'quote': q})
        entry = {'slug': slug, 'name': data['name'], 'shortName': page.get('short_name') or data['name'],
                 'city': city, 'state': data['state'], 'type': data['type'], 'interviews': len(iv_files)}
        pros_cons, w = _verified_pros_cons(slug, page, content_dir)
        warnings += w
        if pros_cons:
            entry['prosCons'] = pros_cons
        schools.append(entry)

    all_files = sorted(content_dir.glob('**/*.md'))            # includes interviews not tied to a school (misc/)
    by_year = {str(n): 0 for n in range(1, 5)}
    for f in all_files:
        n = _year_number(parse_md(f)[0].get('year', ''))
        if n: by_year[str(n)] += 1
    stats = {
        'schools': len(schools),
        'md': sum(s['type'] == 'md' for s in schools),
        'do': sum(s['type'] == 'do' for s in schools),
        'states': len({s['state'] for s in schools}),
        'interviews': len(all_files),
        'byYear': by_year,
    }
    out = ROOT / 'js' / 'site-data.js'
    out.write_text(
        '// Generated by build_schools.py from content/: do not edit by hand.\n'
        f'window.DOCSTORY_SITE = {json.dumps({"stats": stats, "schools": schools, "interviews": interviews}, indent=1, ensure_ascii=False)};\n',
        encoding='utf-8')
    print(f'  data  {out.relative_to(ROOT)}  ({stats["schools"]} schools, {stats["interviews"]} interviews, {stats["states"]} states)')

    # The directory map needs coordinates for every school; flag any that are missing
    directory = (ROOT / 'directory' / 'index.html').read_text(encoding='utf-8')
    on_map = set(re.findall(r"slug:'([^']+)'", directory))
    for s in schools:
        if s['slug'] not in on_map:
            print(f'  WARN  directory/index.html: no map entry for {s["slug"]} (add name, city, lat, lng)')
            warnings += 1
    return warnings


STATIC_PAGES = [            # hand-written pages to list in the sitemap (contribute/interview/ is noindex)
    ('/', 'Home'),
    ('/directory/', 'School directory and map'),
    ('/about/', 'About DocStory'),
    ('/contribute/', 'Contribute an interview'),
    ('/contribute/terms/', 'Contributor terms and FAQ'),
]


def write_sitemap_and_llms(content_dir):
    """sitemap.xml for search engines and llms.txt (a plain-text site guide for AI assistants).
    Both list every school and interview page, so they stay current with each build."""
    schools, interviews = [], []
    for slug, data in SCHOOLS.items():
        files = sorted((content_dir / slug).glob('*.md')) if (content_dir / slug).exists() else []
        if not files:
            continue
        schools.append((slug, data, len(files)))
        for f in files:
            fm, _ = parse_md(f)
            interviews.append((f'/interviews/{slug}/{f.stem}/', fm.get('name', 'Anonymous'), fm.get('year', ''),
                               data['name'], str(fm.get('date', ''))))
    for f in sorted((content_dir / 'misc').glob('*.md')):
        fm, _ = parse_md(f)
        interviews.append((f'/interviews/misc/{f.stem}/', fm.get('name', 'Anonymous'), fm.get('year', ''),
                           'School not given', str(fm.get('date', ''))))

    urls = [seo.url(path) for path, _ in STATIC_PAGES]
    urls += [seo.url(f'/schools/{slug}/') for slug, _, _ in schools]
    urls += [seo.url(path) for path, *_ in interviews]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f'  <url><loc>{html_mod.escape(u)}</loc></url>' for u in urls]
    sitemap.append('</urlset>')
    (ROOT / 'sitemap.xml').write_text('\n'.join(sitemap) + '\n', encoding='utf-8')

    md = sum(d['type'] == 'md' for _, d, _ in schools)
    lines = [
        '# DocStory',
        '',
        f'> First-hand interviews with medical students about what their schools are really like: '
        f'{len(interviews)} interviews covering {len(schools)} U.S. medical schools ({md} MD, {len(schools) - md} DO). '
        'Each school page pairs the interviews with figures from the school\'s own published class profile '
        'and cost of attendance and, where available, U.S. government data (NIH research funding, ClinicalTrials.gov, CMS hospital '
        'data, Census rent). Run since 2017 by people who were medical students at UC Irvine, Creighton, and the '
        'John A. Burns School of Medicine.',
        '',
        'Interviews are written by the students themselves, mostly in answer to a standard set of questions (typical '
        'day, curriculum, culture, clinical training, advice for applicants), and are edited only for typos and '
        'obvious grammar. Each interview reflects one student\'s experience in the year it was written; the publication date '
        'is shown on the interview page. School pages list the official sources for their figures.',
        '',
        '## Pages',
        '',
    ]
    lines += [f'- [{label}]({seo.url(path)})' for path, label in STATIC_PAGES]
    lines += ['', '## Schools', '']
    for slug, data, n in sorted(schools, key=lambda x: x[1]['name'].lower()):
        kind = 'MD' if data['type'] == 'md' else 'DO'
        lines.append(f'- [{data["name"]}]({seo.url(f"/schools/{slug}/")}): {kind}, {data["city"]}, '
                     f'{data["state"]}; {n} interview{"s" if n != 1 else ""}')
    lines += ['', '## Interviews', '']
    for path, name, year, school, date in sorted(interviews, key=lambda x: (x[3].lower(), x[1].lower())):
        meta = ', '.join(x for x in (str(year), date[:4]) if x)
        lines.append(f'- [{name} — {school}]({seo.url(path)}){f" ({meta})" if meta else ""}')
    lines += ['', '## Contact', '', f'- {seo.CONTACT_EMAIL}', '']
    (ROOT / 'llms.txt').write_text('\n'.join(lines), encoding='utf-8')
    print(f'  seo   sitemap.xml ({len(urls)} URLs), llms.txt')


_SEO_BLOCK = re.compile(r'  <title>.*?</title>\n(?:  <meta name="description"[^\n]*\n)?'
                        r'(?:  <!-- seo -->.*?<!-- /seo -->\n)?', re.S)


def write_static_heads(content_dir):
    """Title, description, canonical, link-preview tags and JSON-LD for the hand-written pages.
    Counts come from content/, so the descriptions never go stale."""
    n_schools = sum(1 for slug in SCHOOLS if (content_dir / slug).exists() and any((content_dir / slug).glob('*.md')))
    n_interviews = len(list(content_dir.glob('**/*.md')))
    states = len({d['state'] for slug, d in SCHOOLS.items() if (content_dir / slug).exists()})
    pages = {
        'index.html': (
            'DocStory: Medical Students on What Their Schools Are Really Like',
            f'Read {n_interviews} first-hand interviews with medical students at {n_schools} U.S. MD and DO schools, '
            'paired with official class profiles, costs, and research data.',
            [{'@type': 'WebSite', '@id': seo.SITE_URL + '/#website', 'name': 'DocStory', 'url': seo.SITE_URL + '/',
              'publisher': {'@id': seo.SITE_URL + '/#organization'}}]),
        'directory/index.html': (
            'Medical School Directory: Student Interviews by School | DocStory',
            f'Browse {n_schools} U.S. medical schools in {states} states on a map or by name. Filter MD and DO '
            'programs and read interviews with students at each school.',
            [{'@type': 'CollectionPage', 'name': 'Medical school directory', 'url': seo.url('/directory/')},
             seo.breadcrumbs([('Home', '/'), ('Schools', '/directory/')])]),
        'about/index.html': (
            'About DocStory',
            'DocStory was started in 2017 by medical students who wanted balanced, detailed information about '
            'medical schools. We share interviews with current students in their own words.',
            [{'@type': 'AboutPage', 'name': 'About DocStory', 'url': seo.url('/about/'),
              'about': {'@id': seo.SITE_URL + '/#organization'}},
             seo.breadcrumbs([('Home', '/'), ('About', '/about/')])]),
        'contribute/index.html': (
            'Share Your Med School Story: Contribute to DocStory',
            'Current medical students: answer 8–10 questions about your school in your own words and get paid '
            'once your interview is verified and published on DocStory.',
            [seo.breadcrumbs([('Home', '/'), ('Contribute', '/contribute/')])]),
        'contribute/terms/index.html': (
            'Contributor Terms | DocStory',
            'The terms for contributing a student interview to DocStory: eligibility, verification, payment, '
            'editing, and removal.',
            [seo.breadcrumbs([('Home', '/'), ('Contribute', '/contribute/'), ('Terms', '/contribute/terms/')])]),
        'contribute/interview/index.html': (
            'Your Interview: Contribute to DocStory',
            'Choose 8–10 questions about your medical school and answer them in your own words.',
            []),
    }
    for rel, (title, desc, jsonld) in pages.items():
        path = ROOT / rel
        text = path.read_text(encoding='utf-8')
        noindex = rel == 'contribute/interview/index.html'
        tags = seo.head_tags(title, desc, '/' + rel, jsonld=jsonld, robots='noindex' if noindex else None)
        if rel == 'index.html':
            tags += f'\n  <meta name="msvalidate.01" content="{seo.BING_SITE_VERIFICATION}">'
        block = (f'  <title>{html_mod.escape(title, quote=False)}</title>\n'
                 f'  <meta name="description" content="{html_mod.escape(desc)}">\n'
                 f'  <!-- seo -->\n  {tags}\n  <!-- /seo -->\n')
        new, count = _SEO_BLOCK.subn(lambda m: block, text, count=1)
        if not count:
            print(f'  WARN  {rel}: no <title> found for SEO tags')
            continue
        if noindex:
            new = new.replace('  <meta name="robots" content="noindex">\n', '', 1)
        if new != text:
            path.write_text(new, encoding='utf-8')
    print(f'  seo   head tags for {len(pages)} static pages')


def _fill(text, name, inner):
    """Replace what sits between <!-- prerender:name --> and <!-- /prerender:name -->."""
    pat = re.compile(rf'(<!-- prerender:{name} -->).*?(<!-- /prerender:{name} -->)', re.S)
    if not pat.search(text):
        print(f'  WARN  prerender marker "{name}" not found')
        return text
    return pat.sub(lambda m: m.group(1) + inner + m.group(2), text, count=1)


def write_prerendered(content_dir):
    """Static copies of the homepage and directory content that JavaScript normally draws, so search
    engines and AI crawlers that don't run scripts still see the schools, counts, and featured interviews.
    The page scripts replace these copies on load, so visitors see the same thing as before."""
    e = lambda t: html_mod.escape(str(t), quote=True)
    site = json.loads((ROOT / 'js' / 'site-data.js').read_text(encoding='utf-8')
                      .split('window.DOCSTORY_SITE = ', 1)[1].rstrip().rstrip(';'))
    st = site['stats']
    ini = lambda name: ''.join(p[0] for p in str(name).split())[:2].upper()

    # Homepage: coverage counter + three featured interview cards (the first quoted ones; JS rotates weekly)
    coverage = (f'\n      <div class="font-display-lg text-display-lg text-primary leading-none">{st["schools"]}</div>'
                f'\n      <div class="mt-[4px] mb-xs"><span class="inline-flex items-center gap-[2px] text-[11px] font-semibold '
                f'text-emerald-600 bg-emerald-50 px-[8px] py-[2px] rounded-full">{st["md"]} MD · {st["do"]} DO</span></div>'
                f'\n      <div class="font-body-md text-[13px] font-medium text-primary">Medical schools</div>'
                f'\n      <div class="font-body-md text-[12px] text-slate-gray mt-[2px]">Student interviews from MD and DO '
                f'programs in {st["states"]} states.</div>\n')
    types = {sc['slug']: sc['type'] for sc in site['schools']}
    cards = []
    for iv in [iv for iv in site['interviews'] if iv['quote']][:3]:
        cards.append(f'''
      <a href="interviews/{iv['schoolSlug']}/{iv['studentSlug']}/index.html" class="bg-white rounded-xl border border-primary/10 overflow-hidden hover:shadow-[0_4px_20px_rgb(0,0,0,0.06)] transition-shadow group cursor-pointer flex flex-col">
        <div class="h-40 bg-surface-container relative">
          <div class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
          <div class="absolute bottom-sm left-sm right-sm text-white">
            <span class="bg-vibrant-iris px-2 py-1 rounded text-[10px] font-label-md mb-1 inline-block uppercase tracking-wider">{types.get(iv['schoolSlug'], 'md').upper()}</span>
            <div class="font-headline-md text-headline-md leading-tight line-clamp-2">{e(iv['school'])}</div>
          </div>
        </div>
        <div class="p-md flex flex-col gap-md flex-1">
          <div class="flex items-center gap-sm">
            <div class="w-8 h-8 rounded-full bg-vibrant-iris/15 flex items-center justify-center text-vibrant-iris font-bold text-xs">{e(ini(iv['name']))}</div>
            <div>
              <div class="font-label-md text-label-md text-primary">{e(iv['name'])}</div>
              <div class="font-body-md text-[12px] text-slate-gray">{e(iv['year'])} · {e(iv['city'])}</div>
            </div>
          </div>
          <p class="font-body-md text-body-md text-slate-gray italic line-clamp-3">“{e(iv['quote'])}”</p>
        </div>
      </a>''')
    path = ROOT / 'index.html'
    text = path.read_text(encoding='utf-8')
    new = _fill(_fill(text, 'coverage', coverage), 'featured', ''.join(cards) + '\n')
    if new != text:
        path.write_text(new, encoding='utf-8')

    # Directory: the school cards, in the same order and markup as the map list
    path = ROOT / 'directory' / 'index.html'
    text = path.read_text(encoding='utf-8')
    counts = {sc['slug']: sc['interviews'] for sc in site['schools']}
    entries = re.findall(r"\{ id:'([^']+)',\s*name:'([^']+)',\s*city:'([^']+)',\s*type:'(md|do)'.*?slug:'([^']+)'", text)
    items = []
    for sid, name, city, kind, slug in entries:
        n = counts.get(slug, 0)
        items.append(f'''
<article id="card-{sid}" data-school-id="{sid}" class="bg-white border border-primary/5 rounded-xl p-4 shadow-sm hover:border-vibrant-iris/30 hover:shadow-md transition-all cursor-pointer group">
      <div class="flex items-center gap-3 mb-2">
        <div class="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-primary flex-shrink-0 group-hover:bg-vibrant-iris/10 group-hover:text-vibrant-iris transition-colors">
          <span class="material-symbols-outlined">school</span>
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="font-headline-md text-sm font-semibold text-primary group-hover:text-vibrant-iris transition-colors leading-tight">{e(name)}</h3>
          <p class="font-body-md text-xs text-slate-gray mt-0.5">{e(city)} · {kind.upper()}</p>
        </div>
      </div>
      <div class="mt-2 pt-2 border-t border-primary/5 flex items-center justify-between">
        <span class="font-body-md text-[11px] text-slate-gray">{n} interview{"s" if n != 1 else ""}</span>
        <a href="/schools/{slug}/index.html" class="font-label-md text-[10px] font-semibold text-vibrant-iris hover:underline">View →</a>
      </div>
    </article>''')
    new = _fill(text, 'count', f'Showing {len(entries)} results.')
    new = _fill(new, 'schools', ''.join(items) + '\n')
    if new != text:
        path.write_text(new, encoding='utf-8')
    print(f'  seo   prerendered homepage counters + {len(cards)} cards, {len(entries)} directory cards')


def write_vercel_config(content_dir):
    """vercel.json: permanent redirects so old addresses keep working and pass their Google ranking on.
    - docstory-website.vercel.app (Vercel's default address) → www.docstory.org
    - every page of the old WordPress site (content/redirects.yaml + each interview's `url:` line)
    Returns the number of warnings printed."""
    data = yaml.safe_load((ROOT / 'content' / 'redirects.yaml').read_text(encoding='utf-8'))
    rules, seen, warnings = [], set(), 0

    def add(old, new, exact=False):
        old = '/' + old.strip('/')
        if old in seen:
            return
        seen.add(old)
        # "(/.*)?" also catches the trailing slash, ?amp copies, comment pages and image attachments
        rules.append({'source': old + ('(/)?' if exact else '(/.*)?'), 'destination': new, 'permanent': True})

    for f in sorted(content_dir.glob('*/*.md')):              # old interview posts
        fm, _ = parse_md(f)
        old = re.sub(r'^https?://[^/]+', '', str(fm.get('url') or ''))
        if re.match(r'^/\d{4}/\d{2}/\d{2}/', old):
            add(old, f'/interviews/{f.parent.name}/{f.stem}/')
    for tag, new in (data.get('tags') or {}).items():
        add(f'/tag/{tag}', new)
    for old, slug in (data.get('schools') or {}).items():
        new = f'/schools/{slug}/' if slug else '/directory/'
        if slug and slug not in SCHOOLS:
            print(f'  WARN  redirects.yaml: unknown school slug {slug}')
            warnings += 1
        for path in (old, f'{old}-2', f'medical-student-interviews/{old}', f'medical-student-interviews/{old}-2', f'tag/{old}'):
            add(path, new)
        add(f'interviews/{old}', new, exact=True)            # exact: real interview pages live below /interviews/<slug>/
    for slug in SCHOOLS:                                       # /interviews/<slug>/ on its own → the school page
        add(f'interviews/{slug}', f'/schools/{slug}/', exact=True)
        add(f'tag/{slug}', f'/schools/{slug}/')
    for old, new in (data.get('paths') or {}).items():
        add(old, new)

    # Never shadow a real page or file on the current site
    for r in rules:
        base = r['source'].rsplit('(', 1)[0].lstrip('/')
        exact = r['source'].endswith('(/)?')
        if (ROOT / base).is_file() or (not exact and (ROOT / base).exists()) or (ROOT / base / 'index.html').is_file():
            print(f'  WARN  redirect {r["source"]} would hide an existing page')
            warnings += 1
        if not (ROOT / r['destination'].strip('/') / 'index.html').is_file() and r['destination'] != '/':
            print(f'  WARN  redirect {r["source"]} points at missing page {r["destination"]}')
            warnings += 1

    host = {'source': '/:path(.*)', 'has': [{'type': 'host', 'value': 'docstory-website.vercel.app'}],
            'destination': seo.SITE_URL + '/:path', 'permanent': True}
    (ROOT / 'vercel.json').write_text(json.dumps({'redirects': [host] + rules}, indent=2) + '\n', encoding='utf-8')
    print(f'  seo   vercel.json ({len(rules)} old-address redirects)')
    return warnings


def write_contribute_data(content_dir):
    """School list + published-interview counts for the contribute form (js/contribute-data.js).
    The form uses the counts to decide whether a school is still eligible for paid interviews."""
    schools = []
    for slug, data in SCHOOLS.items():
        iv_dir = content_dir / slug
        count = len(list(iv_dir.glob('*.md'))) if iv_dir.exists() else 0
        schools.append({'slug': slug, 'name': data['name'], 'type': data['type'], 'interviews': count})
    schools.sort(key=lambda s: s['name'].lower())
    out = ROOT / 'js' / 'contribute-data.js'
    out.write_text(
        '// Generated by build_schools.py: do not edit by hand. Rebuild after adding interviews.\n'
        f'window.DOCSTORY_SCHOOLS = {json.dumps(schools, indent=1, ensure_ascii=False)};\n',
        encoding='utf-8')
    print(f'  data  {out.relative_to(ROOT)}  ({len(schools)} schools)')


if __name__ == '__main__':
    main()
