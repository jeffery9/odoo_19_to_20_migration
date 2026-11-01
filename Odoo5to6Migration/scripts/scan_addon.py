#!/usr/bin/env python3
"""Scan OpenERP addons for 5.0-only manifest conventions that 6.0 renamed.

Part of the odoo_5_to_6_migration skill. Stdlib only.
Usage:
    python3 scan_addon.py /path/to/addons [--addon NAME] [--json] [--quiet]
Exit code: 1 when findings exist (CI gate), 0 when clean.
Each finding carries: file, line, pattern id, the 6.0 replacement, whether a
bundled `openerp-server upgrade_code` codemod fixes it, and the reference file.

IMPORTANT — version scope / red lines:
  6.0 and earlier have NO `upgrade_code` codemod module (the engine only exists
  from 18.0+, and the `odoo` package did not yet exist in 6.0). So EVERY finding
  here is 'manual' — there is no automated rewrite for 5->6.
  Also, do NOT flag later concerns here: osv.osv->osv.Model and
  res.partner.address removal (6->7); openerp->odoo and __openerp__.py->
  __manifest__.py (9->10); @api.* / self.env / fields.Date object (7->8, 11->12);
  account.invoice->account.move (12->13). This scanner only looks for 5->6 breaks:
  __terp__.py -> __openerp__.py, and init_xml/update_xml/demo_xml ->
  data/demo/test.
"""
import argparse
import json
import re
import sys
from pathlib import Path

# id, extensions, regex, mode(always 'manual' for 5->6), fix, reference
PATTERNS = [
    # --- manifest file renamed __terp__.py -> __openerp__.py (headline break) -
    ('terp-manifest', {'py'}, re.compile(r'__terp__\.py'),
     'manual', "rename the module manifest file __terp__.py -> __openerp__.py "
     "(6.0 still reads the old name but new code must use __openerp__.py) (6.0)", 'models-mapping.md'),

    # --- manifest keys init_xml/update_xml/demo_xml -> data/demo/test ----------
    ('manifest-keys', {'py'}, re.compile(r"'init_xml'|'update_xml'|'demo_xml'"),
     'manual', "rename manifest keys: init_xml+update_xml -> data (merge both "
     "lists), demo_xml -> demo. 6.0 also adds 'test' and 'web' keys; old keys "
     "still accepted but deprecated (6.0)", 'models-mapping.md'),
]


def scan(root: Path, addon_filter=None):
    findings = []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        # filename-based detection (manifest rename __terp__.py -> __openerp__.py)
        if path.name == '__terp__.py':
            findings.append({'file': str(path), 'line': 1, 'id': 'terp-manifest',
                             'mode': 'manual',
                             'snippet': '__terp__.py (manifest file)',
                             'fix': "rename `__terp__.py` -> `__openerp__.py` (6.0)",
                             'ref': 'orm-api.md'})
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
        print(f"\nSUMMARY: {len(findings)} finding(s) — ALL manual (6.0 and earlier have NO upgrade_code codemod).")
        if findings:
            print('NEXT: apply manual mappings from references/* -> git diff review -> re-scan (expect 0). '
                  'Write custom data migrations (e.g. structure fixes) in module migrations/6.0/.')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
