#!/usr/bin/env python3
"""Scan Odoo addons for 7-only APIs that Odoo 8 renamed/removed (the "new API" migration).

Part of the odoo_7_to_8_migration skill. Stdlib only.
Usage:
    python3 scan_addon.py /path/to/addons [--addon NAME] [--json] [--quiet]
Exit code: 1 when findings exist (CI gate), 0 when clean.
Each finding carries: file, line, pattern id, the 8.0 replacement, whether a
bundled `odoo-bin upgrade_code` codemod fixes it, and the reference file.

IMPORTANT — version scope / red lines:
  8.0 has NO `upgrade_code` codemod module (the engine only exists from 18.0+).
  So EVERY finding here is 'manual' — there is no automated rewrite for 7->8.
  Also, do NOT flag 9->10 concerns here: openerp->odoo package rename belongs to
  9->10 (7/8 still use `from openerp import ...`). This scanner only looks for
  7->8 breaks (new-API decorators, self.pool/self.cr/self.uid/self.context and
  (cr, uid, ids, context) signatures, osv.Model->models.Model, osv.except_osv->
  UserError, _columns->_fields/fields-as-attributes, RML/Mako report engines).
"""
import argparse
import json
import re
import sys
from pathlib import Path

# id, extensions, regex, mode(always 'manual' for 7->8), fix, reference
PATTERNS = [
    # --- new-API decorators introduced in 8.0 --------------------------------
    ('api-decorators', {'py'}, re.compile(r'@api\.(model|multi|one|depends|constrains|onchange|returns)'),
     'manual', "8.0 introduces the new-API decorators; ensure methods use them and drop old (cr, uid, ids, context) signatures in favour of recordsets / self.env (added in 8.0)", 'orm-api.md'),

    # --- self.pool / self.cr / self.uid / self.context + old signatures -------
    ('self-pool', {'py'}, re.compile(r'self\.pool\b|self\.cr\b|self\.uid\b|self\.context\b|\(cr, uid, ids, context\)'),
     'manual', "replace self.pool/self.cr/self.uid/self.context and (cr, uid, ids, context) signatures with the new API: use self.env, recordsets, and drop the old positional args (8.0)", 'orm-api.md'),

    # --- osv.Model / osv.osv / osv.osv_memory -> models.Model -----------------
    ('osv-model', {'py'}, re.compile(r'osv\.osv\b|osv\.osv_memory\b|from openerp\.osv import orm|osv\.Model\b|osv\.TransientModel\b'),
     'manual', "replace osv.Model/osv.TransientModel/osv.osv/osv.osv_memory with models.Model/models.TransientModel; `from openerp.osv import orm` -> `from openerp import models` (8.0 removed the osv alias)", 'orm-api.md'),

    # --- osv.except_osv / except_orm -> UserError -----------------------------
    ('except-osv', {'py'}, re.compile(r'osv\.except_osv|except_orm'),
     'manual', "replace osv.except_osv / except_orm with openerp.exceptions.UserError (raise UserError(...)) (8.0)", 'orm-api.md'),

    # --- old _columns / _all_columns dict -> new-style class attributes -------
    ('fields-attr', {'py'}, re.compile(r'_columns\b|_all_columns\b'),
     'manual', "replace old-style _columns/_all_columns dict with new-style class-attribute fields (name = fields.Char(...)); _columns becomes _fields (8.0)", 'orm-api.md'),

    # --- RML / Mako report engines deprecated in favour of QWeb --------------
    ('qweb-report', {'xml'}, re.compile(r'report_type\s*=\s*["\'](?:rml|mako)["\']'),
     'manual', "8.0 moves reports toward QWeb (report_type='qweb-pdf'/'qweb-html'); RML/Mako report_type is deprecated — migrate <report> definitions to QWeb (8.0) [verify]", 'views-qweb.md'),
]


def scan(root: Path, addon_filter=None):
    findings = []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        ext = {'.py': 'py', '.xml': 'xml', '.js': 'js'}.get(path.suffix)
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
        print(f"\nSUMMARY: {len(findings)} finding(s) — ALL manual (8.0 has NO upgrade_code codemod).")
        if findings:
            print('NEXT: apply manual mappings from references/* -> git diff review -> re-scan (expect 0). '
                  'Write custom data migrations in module migrations/8.0/ (OpenUpgrade executes).')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
