#!/usr/bin/env python3
"""Scan Odoo addons for 13-only / 14-breaking APIs that Odoo 14 renamed/removed.

Part of the odoo_13_to_14_migration skill. Stdlib only.
Usage:
    python3 scan_addon.py /path/to/addons [--addon NAME] [--json] [--quiet]
Exit code: 1 when findings exist (CI gate), 0 when clean.
Each finding carries: file, line, pattern id, the 14.0 replacement, whether a
bundled `odoo-bin upgrade_code` codemod fixes it, and the reference file.

IMPORTANT — version scope / red lines:
  14.0 has NO `upgrade_code` codemod module (the engine only exists from 18.0+).
  So EVERY finding here is 'manual' — there is no automated rewrite for 13->14.
  Also, do NOT flag 14->15 concerns here: ir.model* access removal, t-raw removal,
  Jinja->QWeb mail templates, assets-in-manifest, SavepointCase/Environment.manage
  removal — those belong to the 14->15 skill. This scanner only looks for 13->14
  breaks (ir.actions.* access, invisible/readonly dynamic expr, _name_search ids,
  _compute_display_name, force_company, Char size, selection_add ondelete,
  TransientModel ACL, stock.picking field rename [verify]).
"""
import argparse
import json
import re
import sys
from pathlib import Path

# id, extensions, regex, mode(always 'manual' for 13->14), fix, reference
PATTERNS = [
    # --- ir.actions.* direct access removal ----------------------------------
    ('ir-actions-access', {'py', 'xml'}, re.compile(r'self\.env\[[\'"]ir\.actions|env\.ref\([\'"]ir\.actions'),
     'manual', "ir.actions.* direct access removed in 14.0 — use env['ir.actions.*']._for_xml_id('module.action_id') or .sudo(); frontend via /web/action/load", 'views-qweb.md'),

    # --- invisible/readonly dynamic expression -> attrs -----------------------
    ('invisible-expr', {'xml'}, re.compile(r'(invisible|readonly)="[^"]*(==|!=|<=|>=|<|>|\{|\&gt;|\&lt;)'),
     'manual', "invisible/readonly dynamic expressions (e.g. state=='draft') are rejected in 14.0 — move into attrs domain; only context.get('...') stays inline", 'views-qweb.md'),

    # --- _name_search returns ids --------------------------------------------
    ('name-search', {'py'}, re.compile(r'_name_search'),
     'manual', "_name_search must return a list of ids in 14.0 (no longer (id, name) tuples) — return self.search(...).ids", 'orm-api.md'),

    # --- _compute_display_name -> name_get -----------------------------------
    ('compute-display-name', {'py'}, re.compile(r'_compute_display_name'),
     'manual', "override name_get (+ @api.depends) instead of _compute_display_name in 14.0", 'orm-api.md'),

    # --- force_company -> with_company ---------------------------------------
    ('force-company', {'py'}, re.compile(r'force_company'),
     'manual', "replace with_context(force_company=...) with with_company(company) in 14.0", 'orm-api.md'),

    # --- Char size attribute removed -----------------------------------------
    ('char-size', {'py'}, re.compile(r'fields\.Char\([^)]*size\s*='),
     'manual', "remove size= attribute from fields.Char in 14.0 (no longer restricts length)", 'models-mapping.md'),

    # --- selection_add requires ondelete -------------------------------------
    ('selection-ondelete', {'py'}, re.compile(r'selection_add\s*='),
     'manual', "selection_add in 14.0 must declare ondelete={'value': 'set null'|'cascade'} for every added value", 'models-mapping.md'),

    # --- stock.picking field renames ([verify]) -------------------------------
    ('stock-picking-rename', {'py'}, re.compile(r'\.move_line_ids\b|\.move_lines\b'),
     'manual', "stock.picking.move_lines -> move_ids_without_package / move_line_ids -> move_line_ids_without_package in 14.0 [verify] — confirm against 14.0 stock.picking source", 'models-mapping.md'),
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
        print(f"\nSUMMARY: {len(findings)} finding(s) — ALL manual (14.0 has NO upgrade_code codemod).")
        if findings:
            print('NEXT: apply manual mappings from references/* -> git diff review -> re-scan (expect 0). '
                  'Write custom data migrations (selection option migration) in module migrations/14.0/.')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
