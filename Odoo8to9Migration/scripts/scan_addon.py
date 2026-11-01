#!/usr/bin/env python3
"""Scan Odoo addons for 8-only APIs that Odoo 9 renamed/removed.

Part of the odoo_8_to_9_migration skill. Stdlib only.
Usage:
    python3 scan_addon.py /path/to/addons [--addon NAME] [--json] [--quiet]
Exit code: 1 when findings exist (CI gate), 0 when clean.
Each finding carries: file, line, pattern id, the 9.0 replacement, whether a
bundled `odoo-bin upgrade_code` codemod fixes it, and the reference file.

IMPORTANT — version scope / red lines:
  9.0 has NO `upgrade_code` codemod module (the engine only exists from 18.0+).
  So EVERY finding here is 'manual' — there is no automated rewrite for 8->9.
  Also, do NOT flag 9->10 concerns here: the `openerp`->`odoo` package rename
  belongs to 9->10 (8.0 and 9.0 both still use `from openerp import ...`); the
  `@api.one` removal, `fields.Date` runtime object, `parent_path`, and
  `ir.actions.act_window.view` removal belong to 11->12; the new-API decorators
  (`@api.model`/`@api.multi`/`@api.one`) already exist in 8.0. This scanner only
  looks for 8->9 breaks:
    - Community / Enterprise edition split (modules that moved to Enterprise)
    - `osv.except_osv` / `except_orm` -> `openerp.exceptions.UserError`
    - `ir.model` `_is_osv_memory` / `_search_osv_memory` methods removed and the
      `osv_memory` field renamed to `transient`
    - `osv_memory_autovacuum` model renamed to `ir_autovacuum`
"""
import argparse
import json
import re
import sys
from pathlib import Path

# id, extensions, regex, mode(always 'manual' for 8->9), fix, reference
PATTERNS = [
    # --- Community / Enterprise edition split (headline) ----------------------
    # Conservative: only flag a small known set of modules that became
    # Enterprise-only in 9.0 inside `depends` / import lines. Flag [verify].
    ('enterprise-split', {'py', 'xml'}, re.compile(
        r'\b(account_voucher|account_analytic_plan|document|marketing)\b'),
     'manual', "9.0 split Community/Enterprise: module may now be Enterprise-only. "
     "If your module depends on it, confirm the dependency still resolves on CE or "
     "migrate the feature; verify against the 9.0 EE tree [verify] (9.0)", 'models-mapping.md'),

    # --- osv.except_osv / except_orm -> openerp.exceptions.UserError ----------
    ('except-osv', {'py'}, re.compile(r'osv\.except_osv|except_orm'),
     'manual', "replace `osv.except_osv` / `except_orm` with "
     "`from openerp.exceptions import UserError` and `raise UserError(...)` (9.0)", 'orm-api.md'),

    # --- ir.model: osv_memory field -> transient, _is_osv_memory / ------------
    #     _search_osv_memory methods removed -----------------------------------
    ('osv-memory-field', {'py'}, re.compile(r'_is_osv_memory|_search_osv_memory|osv_memory'),
     'manual', "in `ir.model`/`ir_model` the `osv_memory` field is renamed to `transient`; "
     "the methods `_is_osv_memory` and `_search_osv_memory` were removed — drop calls/overrides (9.0)", 'orm-api.md'),

    # --- osv_memory_autovacuum model -> ir_autovacuum -------------------------
    ('autovacuum', {'py', 'xml'}, re.compile(r'osv_memory_autovacuum'),
     'manual', "the `osv_memory_autovacuum` model is renamed to `ir_autovacuum`; "
     "update model references / XML-IDs accordingly (9.0)", 'orm-api.md'),
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
        ids = sorted({f['id'] for f in findings})
        print(f"\nSUMMARY: {len(findings)} finding(s) — ALL manual (9.0 has NO upgrade_code codemod).")
        print(f"Patterns fired: {', '.join(ids) if ids else 'none'}")
        if findings:
            print('NEXT: apply manual mappings from references/* -> git diff review -> re-scan (expect 0). '
                  'Write custom data migrations (e.g. Enterprise-module dependency audit) in module migrations/9.0/.')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
