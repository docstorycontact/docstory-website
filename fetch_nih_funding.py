#!/usr/bin/env python3
"""
fetch_nih_funding.py — refresh the automatic "NIH funding" figure on school pages.

Source: NIH RePORTER (https://reporter.nih.gov), U.S. government data in the public domain.
For every school whose content/schools/<slug>.yaml sets `nih_org` (the organization name
exactly as RePORTER spells it, e.g. HARVARD MEDICAL SCHOOL), this totals the NIH awards made
to that organization's medical school ("SCHOOLS OF MEDICINE" unit) in the latest complete
federal fiscal year and writes content/schools/fetched/<slug>.json for build_schools.py.

If a request fails, the previous figure is kept. Run from the project root:
    python3 fetch_nih_funding.py [slug ...]
"""

import json
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

import yaml

ROOT      = Path(__file__).parent
DATA_DIR  = ROOT / 'content' / 'schools'
OUT_DIR   = DATA_DIR / 'fetched'
API_URL   = 'https://api.reporter.nih.gov/v2/projects/search'
PAGE_SIZE = 500
ORG_TYPE  = 'SCHOOLS OF MEDICINE'


def latest_complete_fiscal_year(today=None):
    """Federal fiscal years end Sept 30; give RePORTER until December to finish loading awards."""
    today = today or date.today()
    return today.year if today.month == 12 else today.year - 1


def search(org_name, fiscal_year, offset):
    body = json.dumps({
        'criteria': {'fiscal_years': [fiscal_year], 'org_names': [org_name]},
        'include_fields': ['Organization', 'OrganizationType', 'AwardAmount'],
        'offset': offset, 'limit': PAGE_SIZE,
    }).encode()
    req = urllib.request.Request(API_URL, data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def nih_total(org_name, fiscal_year):
    """Sum award amounts for the org's medical-school unit, paging through all results."""
    total, projects, offset = 0, 0, 0
    while True:
        data = search(org_name, fiscal_year, offset)
        for r in data.get('results', []):
            org = r.get('organization') or {}
            if org.get('org_name') == org_name and (r.get('organization_type') or {}).get('name') == ORG_TYPE:
                total += r.get('award_amount') or 0
                projects += 1
        offset += PAGE_SIZE
        if offset >= data.get('meta', {}).get('total', 0):
            return total, projects
        time.sleep(1)   # NIH asks API users to stay at or below one request per second


def main():
    wanted = set(sys.argv[1:])
    fiscal_year = latest_complete_fiscal_year()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    changes = []
    for path in sorted(DATA_DIR.glob('*.yaml')):
        slug = path.stem
        if slug.startswith('_') or (wanted and slug not in wanted):
            continue
        org = (yaml.safe_load(path.read_text(encoding='utf-8')) or {}).get('nih_org')
        if not org:
            continue
        out = OUT_DIR / f'{slug}.json'
        record = json.loads(out.read_text(encoding='utf-8')) if out.exists() else {}
        prev = record.get('nih', {})
        try:
            amount, projects = nih_total(org, fiscal_year)
        except Exception as exc:
            print(f'  FAIL  {slug}: {exc} — keeping previous figure')
            continue
        if not projects:
            print(f'  WARN  {slug}: no {ORG_TYPE} awards found for "{org}" in FY{fiscal_year} — keeping previous figure')
            continue
        record['nih'] = {'org_name': org, 'fiscal_year': fiscal_year, 'amount': amount,
                         'projects': projects, 'fetched': date.today().isoformat()}
        out.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        if (prev.get('amount'), prev.get('fiscal_year')) != (amount, fiscal_year):
            changes.append(f'{slug}: NIH FY{prev.get("fiscal_year", "—")} ${prev.get("amount", 0):,} → FY{fiscal_year} ${amount:,}')
        print(f'  ok    {slug}  FY{fiscal_year}  ${amount:,}  ({projects} awards)')
        time.sleep(1)
    print(f'\n{len(changes)} figure(s) changed.')
    for line in changes:
        print('  • ' + line)


if __name__ == '__main__':
    main()
