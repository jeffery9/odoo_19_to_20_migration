#!/usr/bin/env python3
"""Scan Odoo addons for 14-only / 15-breaking APIs that Odoo 15 renamed/removed.

Part of the odoo_14_to_15_migration skill. Stdlib only.
Usage:
    python3 scan_addon.py /path/to/addons [--addon NAME] [--json] [--quiet]
Exit code: 1 when findings exist (CI gate), 0 when clean.
Each finding carries: file, line, pattern id, the 15.0 replacement, whether a
bundled `odoo-bin upgrade_code` codemod fixes it, and the reference file.

IMPORTANT — version scope / red lines:
  15.0 has NO `upgrade_code` codemod module (the engine only exists from 18.0+).
  So EVERY finding here is 'manual' — there is no automated rewrite for 14->15.
  Also, do NOT flag 13->14 concerns here: ir.actions.* access removal,
  invisible/readonly dynamic-expression -> attrs, _name_search returns ids,
  _compute_display_name, force_company, Char size, selection_add ondelete,
  TransientModel ACL, stock.picking field rename — those belong to the 13->14
  skill. This scanner only looks for 14->15 breaks:
    t-raw removal (-> t-out/t-esc + markupsafe.Markup)            #01875541b1a8
    ir.model* direct access removal (ir.model, ir.model.fields,  #69120
        ir.model.data) -> sudo() / model API
    mail.template Jinja -> QWeb body + inline_template {{ }}      #77074
    ES modules -> *.esm.js rename (/** @odoo-module **/)
    JS/SCSS assets from XML templates -> __manifest__.py assets  (qweb key removed)
    SavepointCase -> TransactionCase                             #62031
    Environment.manage() removal
    subtype -> subtype_xmlid [verify]
"""
import argparse
import json
import re
import sys
from pathlib import Path

# id, extensions, regex, mode(always 'manual' for 14->15), fix, reference
PATTERNS = [
    # --- t-raw removed (-> t-out / t-esc) --------------------------------
    ('t-raw', {'xml', 'js', 'py'}, re.compile(r't-raw'),
     'manual', "t-raw removed in 15.0 — use t-out (no escape, equals old t-raw) or t-esc (HTML-escape); wrap trusted server HTML in markupsafe.Markup for t-out", 'views-qweb.md'),

    # --- ir.model* direct access removal (#69120) ------------------------
    ('ir-model-access', {'py', 'xml'}, re.compile(r'[\'"]ir\.model(?:\.fields|\.data)?[\'"]'),
     'manual', "ir.model / ir.model.fields / ir.model.data direct access removed in 15.0 (#69120) — use sudo() or the model's own API (_fields, _xmlid_lookup, _get_id). NOTE: this is a DIFFERENT object from the 13->14 ir.actions.* removal", 'orm-api.md'),

    # --- mail.template Jinja -> QWeb / inline_template (#77074) ----------
    ('jinja-mail', {'xml', 'py'}, re.compile(r'\$\{'),
     'manual', "Jinja/Python-format ${...} in mail.template replaced by QWeb (type='qweb', body uses t-out/t-esc) + inline_template {{ }} for subject/email_from/email_to in 15.0 (#77074)", 'http-rpc-mail.md'),

    # --- assets moved into __manifest__.py `assets` key; `qweb` key gone --
    ('qweb-key', {'py'}, re.compile(r'[\'"]qweb[\'"]\s*:\s*\['),
     'manual', "the 'qweb' __manifest__.py key is removed in 15.0 — move QWeb template lists and JS/SCSS assets into the 'assets' key (web.assets_qweb / web.assets_backend / web.assets_frontend). Paths are repo-relative", 'models-mapping.md'),

    # --- SavepointCase -> TransactionCase (#62031) -----------------------
    ('savepoint-case', {'py'}, re.compile(r'SavepointCase'),
     'manual', "SavepointCase alias removed in 15.0 (#62031) — use TransactionCase", 'orm-api.md'),

    # --- Environment.manage() removal ------------------------------------
    ('env-manage', {'py'}, re.compile(r'Environment\.manage\(|env\.manage\(|\.manage\(\)'),
     'manual', "Environment.manage() no longer needed in 15.0 — create Environment(cr, uid, context) directly", 'orm-api.md'),

    # --- subtype -> subtype_xmlid [verify] -------------------------------
    ('subtype-xmlid', {'py', 'xml'}, re.compile(r'subtype\s*='),
     'manual', "message_post/message_notify/notify subtype= -> subtype_xmlid= in 15.0 [verify] — single community source disagrees; confirm target is an xmlid before relying on it", 'http-rpc-mail.md'),
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

        # --- path-aware: ES modules must be renamed *.esm.js -------------
        if ext == 'js' and '/** @odoo-module **/' in text and not str(path).endswith('.esm.js'):
            findings.append({'file': str(path), 'line': 1, 'id': 'odoo-module-esm',
                             'mode': 'manual',
                             'snippet': '/** @odoo-module **/ (file is not *.esm.js)',
                             'fix': "rename the file to *.esm.js in 15.0 — any JS carrying /** @odoo-module **/ must be an ES module with the .esm.js suffix",
                             'ref': 'views-qweb.md'})

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
        print(f"\nSUMMARY: {len(findings)} finding(s) — ALL manual (15.0 has NO upgrade_code codemod).")
        if findings:
            print('NEXT: apply manual mappings from references/* -> git diff review -> re-scan (expect 0). '
                  'Write custom data migrations (subtype_xmlid xmlid, asset moves) in module migrations/15.0/.')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
