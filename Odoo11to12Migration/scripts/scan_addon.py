#!/usr/bin/env python3
"""Scan Odoo addons for 11-only APIs that Odoo 12 renamed/removed.

Part of the odoo_11_to_12_migration skill. Stdlib only.
Usage:
    python3 scan_addon.py /path/to/addons [--addon NAME] [--json] [--quiet]
Exit code: 1 when findings exist (CI gate), 0 when clean.
Each finding carries: file, line, pattern id, the 12.0 replacement, whether a
bundled `odoo-bin upgrade_code` codemod fixes it, and the reference file.

IMPORTANT — version scope / red lines:
  12.0 has NO `upgrade_code` codemod module (the engine only exists from 18.0+).
  So EVERY finding here is 'manual' — there is no automated rewrite for 11->12.
  Also, do NOT flag 12->13 concerns here: account.invoice->account.move,
  customer/supplier->customer_rank/supplier_rank, src_model->binding_model,
  stock.quant qty->quantity — those belong to the 12->13 skill. This scanner
  only looks for 11->12 breaks (api.one removal, Date runtime object,
  model_create_multi, parent_path, ir.actions.act_window.view removal,
  do_notify/do_warning removal, t-field-options->t-options).
"""
import argparse
import json
import re
import sys
from pathlib import Path

# id, extensions, regex, mode(always 'manual' for 11->12), fix, reference
PATTERNS = [
    # --- @api.one removal (headline break) ----------------------------------
    ('api-one', {'py'}, re.compile(r'@api\.one|api\.one\b'),
     'manual', "remove @api.one decorator; methods are multi by default — wrap body in `for record in self:` (removed in 12.0)", 'orm-api.md'),

    # --- fields.Date/Datetime runtime object (headline break) ---------------
    ('date-from-string', {'py'}, re.compile(r'\.from_string\s*\('),
     'manual', "replace fields.Date.from_string/fields.Datetime.from_string with fields.Date.to_date/fields.Datetime.to_datetime (from_string removed in 12.0); date fields are now real date/datetime objects", 'orm-api.md'),

    # --- ir.actions.act_window.view model removal ----------------------------
    ('act-window-view', {'xml'}, re.compile(r'model\s*=\s*["\']ir\.actions\.act_window\.view["\']'),
     'manual', "delete ir.actions.act_window.view records; bind views via the action's view_ids (o2m) / views (12.0)", 'views-qweb.md'),

    # --- do_notify / do_warning removal -------------------------------------
    ('do-notify', {'py'}, re.compile(r'\bdo_notify\b|\bdo_warning\b'),
     'manual', "replace self.do_notify/do_warning with raise UserError(...) or self.message_post(...) (removed in 12.0)", 'orm-api.md'),

    # --- QWeb t-field-options -> t-options -----------------------------------
    ('t-field-options', {'xml'}, re.compile(r't-field-options'),
     'manual', "rename QWeb attribute t-field-options -> t-options (12.0)", 'views-qweb.md'),

    # --- _parent_store: drop parent_left/parent_right ------------------------
    ('parent-left-right', {'py'}, re.compile(r'parent_left|parent_right'),
     'manual', "remove parent_left/parent_right fields; add parent_path = fields.Char(index=True, store=True) under _parent_store (12.0)", 'orm-api.md'),
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
        print(f"\nSUMMARY: {len(findings)} finding(s) — ALL manual (12.0 has NO upgrade_code codemod).")
        if findings:
            print('NEXT: apply manual mappings from references/* -> git diff review -> re-scan (expect 0). '
                  'Write custom data migrations (e.g. parent_path fill) in module migrations/12.0/.')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
