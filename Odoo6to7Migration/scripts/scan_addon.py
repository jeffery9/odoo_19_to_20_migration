#!/usr/bin/env python3
"""Scan OpenERP addons for 6-only APIs that OpenERP 7 renamed/removed.

Part of the odoo_6_to_7_migration skill. Stdlib only.
Usage:
    python3 scan_addon.py /path/to/addons [--addon NAME] [--json] [--quiet]
Exit code: 1 when findings exist (CI gate), 0 when clean.
Each finding carries: file, line, pattern id, the 7.0 replacement, whether a
bundled `odoo-bin upgrade_code` codemod fixes it, and the reference file.

IMPORTANT — version scope / red lines:
  7.0 has NO `upgrade_code` codemod module (the engine only exists from 18.0+).
  So EVERY finding here is 'manual' — there is no automated rewrite for 6->7.
  Also, do NOT flag 7->8 concerns here: models.Model, @api.*, self.env,
  osv.except_osv->UserError — those belong to the 7->8 skill. This scanner
  only looks for 6->7 breaks (osv.osv->osv.Model, res.partner.address removal,
  __openerp__.py update_xml->data, view version="7.0"/sheet/header/footer).
"""
import argparse
import json
import re
import sys
from pathlib import Path

# id, extensions, regex, mode(always 'manual' for 6->7), fix, reference
PATTERNS = [
    # --- osv.osv -> osv.Model (headline base-class break) --------------------
    ('osv-base', {'py'},
     re.compile(r'osv\.osv\b|osv\.osv_memory|class \w+\(osv\.osv\)|class \w+\(osv\.osv_memory\)'),
     'manual', "replace osv.osv -> osv.Model (and osv.osv_memory -> osv.TransientModel for wizards); "
     "keep `from openerp.osv import osv, fields`. Do NOT switch to odoo (9->10) or models.Model (7->8) (7.0)",
     'orm-api.md'),

    # --- res.partner.address model removed ------------------------------------
    ('partner-address', {'py', 'xml'},
     re.compile(r'res\.partner\.address|res_partner_address'),
     'manual', "res.partner.address is removed in 7.0; addresses merged into res.partner. "
     "Replace all res.partner.address / res_partner_address references with res.partner fields "
     "(street, city, email, phone) (7.0)", 'models-mapping.md'),

    # --- __openerp__.py manifest keys update_xml/init_xml/demo_xml -> data ----
    ('manifest-keys', {'py'},
     re.compile(r"update_xml|init_xml|demo_xml"),
     'manual', "in __openerp__.py fold update_xml / init_xml / demo_xml into the single `data` list "
     "(file name stays __openerp__.py; the rename to __manifest__.py is 9->10) (7.0)", 'models-mapping.md'),

    # --- new web client views: version="7.0" + sheet/header/footer ----------
    ('view-bootstrap', {'xml'},
     re.compile(r'version="7\.0"|<sheet>|<header>|<footer>'),
     'manual', "7.0 views use version=\"7.0\" on the root element and <sheet>/<header>/<footer> layout tags; "
     "HTML is allowed in views (6->7 web client rewrite + Bootstrap). Verify structure completeness (7.0)",
     'views-qweb.md'),
]


def scan(root: Path, addon_filter=None):
    findings = []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        ext = {'.py': 'py', '.xml': 'xml', '.js': 'js', '.csv': 'csv'}.get(path.suffix)
        if not ext:
            continue
        if addon_filter and addon_filter not in path.parts:
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            continue
        seen = set()
        for pid, exts, rx, mode, fix, ref in PATTERNS:
            if ext not in exts:
                continue
            for m in rx.finditer(text):
                line = text.count('\n', 0, m.start()) + 1
                if (pid, line) in seen:
                    continue
                seen.add((pid, line))
                snippet = text[m.start():m.start() + 90].splitlines()[0].strip()
                findings.append({'file': str(path), 'line': line, 'id': pid, 'mode': mode,
                                 'snippet': snippet, 'fix': fix, 'ref': ref})
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('addons_path')
    ap.add_argument('--addon', help='only report files under this addon directory name')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--quiet', action='store_true', help='only print the summary line')
    args = ap.parse_args()

    findings = scan(Path(args.addons_path), args.addon)
    if args.json:
        print(json.dumps(findings, indent=1))
    else:
        by_file = {}
        for f in findings:
            by_file.setdefault(f['file'], []).append(f)
        for fname in sorted(by_file):
            print(f'\n## {fname}')
            for f in sorted(by_file[fname], key=lambda x: x['line']):
                print(f"  L{f['line']:<5} [manual] {f['id']}: {f['snippet']}")
                if not args.quiet:
                    print(f"         -> {f['fix']}  (ref: references/{f['ref']})")
        print(f"\nSUMMARY: {len(findings)} finding(s) — ALL manual (7.0 has NO upgrade_code codemod).")
        if findings:
            print('NEXT: apply manual mappings from references/* -> git diff review -> re-scan (expect 0). '
                  'Write custom data migrations (e.g. res_partner_address merge) in module migrations/7.0/.')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
