#!/usr/bin/env python3
"""
fetch_public_data.py — refresh the automatic figures on school pages.

Every source here is U.S. government data (public domain), so nothing needs a license:
  • NIH RePORTER        reporter.nih.gov        — NIH funding (5-year trend), top-funded
                                                   departments, NIH-funded MD-PhD (MSTP) and
                                                   clinical-translational (CTSA) awards
  • ClinicalTrials.gov  clinicaltrials.gov      — trials currently recruiting
  • CMS Care Compare    data.cms.gov            — hospital type, ownership, ER, star rating
                                                   for each listed clinical site
  • Census ACS          api.census.gov          — county median gross rent
                                                   (needs a free key in CENSUS_API_KEY)

For each content/schools/<slug>.yaml it reads `nih_org`, `trials_sponsor`, `clinical_sites[].cms_id`
and `cost_of_living.fips`, then writes content/schools/fetched/<slug>.json for build_schools.py.
A source that fails keeps its previous values. Run from the project root:
    python3 fetch_public_data.py [slug ...]
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

ROOT      = Path(__file__).parent
DATA_DIR  = ROOT / 'content' / 'schools'
OUT_DIR   = DATA_DIR / 'fetched'
NIH_API   = 'https://api.reporter.nih.gov/v2/projects/search'
CT_API    = 'https://clinicaltrials.gov/api/v2/studies'
CMS_API   = 'https://data.cms.gov/provider-data/api/1/datastore/query/xubh-q36u/0'
CENSUS_API = 'https://api.census.gov/data/{year}/acs/acs5'
ORG_TYPE  = 'SCHOOLS OF MEDICINE'
TREND_YEARS = 5


def latest_complete_fiscal_year(today=None):
    """Federal fiscal years end Sept 30; give RePORTER until December to finish loading awards."""
    today = today or date.today()
    return today.year if today.month == 12 else today.year - 1


def get_json(url, body=None):
    headers = {'Content-Type': 'application/json'} if body else {}
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


# ── NIH RePORTER ──────────────────────────────────────────────────────────────

def nih_projects(org_name, fiscal_year):
    """All projects for an organization in one fiscal year (paged, ≤1 request/second)."""
    results, offset = [], 0
    while True:
        data = get_json(NIH_API, {
            'criteria': {'fiscal_years': [fiscal_year], 'org_names': [org_name]},
            'include_fields': ['Organization', 'OrganizationType', 'AwardAmount', 'ActivityCode', 'ProjectTitle'],
            'offset': offset, 'limit': 500,
        })
        results += [r for r in data.get('results', []) if (r.get('organization') or {}).get('org_name') == org_name]
        offset += 500
        time.sleep(1)
        if offset >= data.get('meta', {}).get('total', 0):
            return results


def fetch_nih(org_name):
    latest = latest_complete_fiscal_year()
    trend, depts, flags = {}, Counter(), set()
    for fy in range(latest - TREND_YEARS + 1, latest + 1):
        projects = nih_projects(org_name, fy)
        med = [p for p in projects if (p.get('organization_type') or {}).get('name') == ORG_TYPE]
        trend[str(fy)] = sum(p.get('award_amount') or 0 for p in med)
        if fy == latest:
            for p in med:
                depts[(p.get('organization') or {}).get('dept_type') or 'Other'] += p.get('award_amount') or 0
            for p in projects:   # training/hub awards may sit outside the medical-school unit
                title, code = (p.get('project_title') or '').upper(), p.get('activity_code')
                if code == 'T32' and 'MEDICAL SCIENTIST' in title:
                    flags.add('mstp')
                if code in ('UL1', 'UM1') and 'CLINICAL' in title and 'TRANSLATIONAL' in title:
                    flags.add('ctsa')
    top = [{'dept': d.title().replace('/', ' / '), 'amount': a} for d, a in depts.most_common(3) if d != 'Other']
    return {'org_name': org_name, 'fiscal_year': latest, 'amount': trend[str(latest)],
            'trend': trend, 'top_departments': top, 'mstp': 'mstp' in flags, 'ctsa': 'ctsa' in flags}


# ── ClinicalTrials.gov ────────────────────────────────────────────────────────

def fetch_trials(sponsor):
    query = urllib.parse.urlencode({'query.spons': f'"{sponsor}"', 'filter.overallStatus': 'RECRUITING',
                                    'countTotal': 'true', 'pageSize': 1, 'fields': 'NCTId'})
    return {'sponsor': sponsor, 'recruiting': get_json(f'{CT_API}?{query}').get('totalCount', 0)}


# ── CMS hospital data ─────────────────────────────────────────────────────────

def fetch_cms(cms_id):
    query = urllib.parse.urlencode({'conditions[0][property]': 'facility_id',
                                    'conditions[0][value]': cms_id, 'limit': 1})
    rows = get_json(f'{CMS_API}?{query}').get('results', [])
    if not rows:
        return None
    r = rows[0]
    stars = r.get('hospital_overall_rating')
    return {'name': r.get('facility_name'), 'city': r.get('citytown'), 'type': r.get('hospital_type'),
            'ownership': r.get('hospital_ownership'), 'emergency': r.get('emergency_services') == 'Yes',
            'stars': int(stars) if str(stars).isdigit() else None}


# ── Census ACS ────────────────────────────────────────────────────────────────

def fetch_rent(fips, key):
    """Median gross rent for a county (5-digit FIPS) from the newest ACS 5-year release."""
    for year in range(date.today().year - 1, date.today().year - 4, -1):
        query = urllib.parse.urlencode({'get': 'NAME,B25064_001E', 'for': f'county:{fips[2:]}',
                                        'in': f'state:{fips[:2]}', 'key': key})
        try:
            rows = get_json(CENSUS_API.format(year=year) + '?' + query)
            return {'median_rent': int(rows[1][1]), 'acs_year': f'{year - 4}–{year}', 'county': rows[1][0]}
        except Exception:
            continue
    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    wanted = set(sys.argv[1:])
    census_key = os.environ.get('CENSUS_API_KEY')
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(DATA_DIR.glob('*.yaml')):
        slug = path.stem
        if slug.startswith('_') or (wanted and slug not in wanted):
            continue
        page = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
        out = OUT_DIR / f'{slug}.json'
        record = json.loads(out.read_text(encoding='utf-8')) if out.exists() else {}
        print(f'{slug}')

        jobs = []
        if page.get('nih_org'):
            jobs.append(('nih', lambda: fetch_nih(page['nih_org'])))
        if page.get('trials_sponsor'):
            jobs.append(('trials', lambda: fetch_trials(page['trials_sponsor'])))
        sites = [s['cms_id'] for s in page.get('clinical_sites') or [] if s.get('cms_id')]
        if sites:
            jobs.append(('hospitals', lambda: {cid: fetch_cms(str(cid)) for cid in sites}))
        fips = (page.get('cost_of_living') or {}).get('fips')
        if fips and census_key:
            jobs.append(('rent', lambda: fetch_rent(str(fips), census_key)))
        elif fips:
            print('  skip  rent: set CENSUS_API_KEY to fetch automatically (YAML value is used meanwhile)')

        for name, job in jobs:
            try:
                value = job()
            except Exception as exc:
                print(f'  FAIL  {name}: {exc} — keeping previous values')
                continue
            if not value:
                print(f'  WARN  {name}: no data returned — keeping previous values')
                continue
            if name == 'hospitals':
                for cid, info in value.items():
                    if info is None:
                        print(f'  WARN  CMS id {cid} not found')
            value['fetched'] = date.today().isoformat()
            changed = {k: v for k, v in value.items() if k != 'fetched' and record.get(name, {}).get(k) != v}
            record[name] = value
            print(f'  ok    {name}' + (f'  (changed: {", ".join(changed)})' if changed and name in record else ''))
        out.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
