#!/usr/bin/env python3
"""Scan Odoo addons for 10-only APIs that Odoo 11 renamed/removed.

Part of the odoo_10_to_11_migration skill. Stdlib only.
Usage:
    python3 scan_addon.py /path/to/addons [--addon NAME] [--json] [--quiet]
Exit code: 1 when findings exist (CI gate), 0 when clean.
Each finding carries: file, line, pattern id, the 11.0 replacement, whether a
bundled `odoo-bin upgrade_code` codemod fixes it, and the reference file.

IMPORTANT — version scope / red lines:
  11.0 has NO `upgrade_code` codemod module (the engine only exists from 18.0+).
  So EVERY finding here is 'manual' — there is no automated rewrite for 10->11.
  Also, do NOT flag 11->12 concerns here: @api.one removal, fields.Date runtime
  object, parent_path, ir.actions.act_window.view removal, do_notify/do_warning
  removal, t-field-options->t-options — those belong to the 11->12 skill. This
  scanner only looks for 10->11 breaks (Python 3 syntax, openerp alias removal,
  Workflow removal, QWeb report API rewrite, ir.cron model->model_id, module
  rename/merge, base.group_configuration->base.group_system).
"""
import argparse
import json
import re
import sys
from pathlib import Path

# id, extensions, regex, mode(always 'manual' for 10->11), fix, reference
PATTERNS = [
    # --- Python 2 leftover syntax (Python 3 mandatory in 11.0) ----------------
    ('py2-syntax', {'py'}, re.compile(
        r'print\s+["\'\w(]|iteritems|itervalues|iterkeys|has_key|'
        r'\bbasestring\b|\bxrange\b|except\s+\w+\s*,\s*\w+\s*:|'
        r'StringIO|cStringIO|urllib2'),
     'manual', "rewrite Python 2 syntax for Python 3: print statement->print(), "
     "iteritems/itervalues/iterkeys->items/values/keys, has_key->'in', "
     "basestring/unicode->str, xrange->range, except E, e:->except E as e:, "
     "StringIO/cStringIO->io.StringIO/io.BytesIO, urllib2->urllib.request/werkzeug.urls. "
     "pycompat shims removed in 11.0 (11.0)", 'orm-api.md'),

    # --- openerp compat alias removed in 11.0 ---------------------------------
    ('openerp-import', {'py'}, re.compile(r'from openerp|import openerp'),
     'manual', "replace `from openerp` / `import openerp` with `from odoo` / `import odoo` "
     "(the openerp compat alias is removed in 11.0; main rename was 9->10) (11.0)", 'orm-api.md'),

    # --- Workflow fully removed in 11.0 ---------------------------------------
    ('workflow', {'py', 'xml'}, re.compile(r'\bworkflow\b|signal_workflow|type="workflow"'),
     'manual', "remove workflow XML, type=\"workflow\" buttons and signal_workflow() calls; "
     "replace with state fields + @api.multi methods + <button type=\"object\"> (11.0)", 'orm-api.md'),

    # --- QWeb report API rewrite (render_html/get_action/get_html) ------------
    ('report-api', {'py'}, re.compile(r'render_html|get_action|get_html'),
     'manual', "rewrite QWeb report call: render_html->get_report_values (return dict), "
     "self.env['report'].get_action->self.env.ref(xmlid).report_action, get_html->render_qweb_html (11.0)", 'orm-api.md'),

    # --- ir.cron model -> model_id --------------------------------------------
    ('ir-cron-model', {'xml'}, re.compile(r'<record[^>]*model="ir\.cron"[\s\S]*?name="model"'),
     'manual', "in ir.cron records replace <field name=\"model\" eval=\"'model'\"> with "
     "<field name=\"model_id\" ref=\"model_xxx\"/> (or switch to state=\"code\" + code field) (11.0)", 'orm-api.md'),

    # --- module rename sale -> sale_management, account_accountant -> account_invoicing
    ('module-rename', {'py', 'xml'}, re.compile(r'\baccount_accountant\b|\bsale\b(?![a-z_])'),
     'manual', "update depends/imports: sale->sale_management, account_accountant->account_invoicing (11.0)", 'models-mapping.md'),

    # --- module merge account_tax_cash_basis -> account, report -> web --------
    ('module-merge', {'py', 'xml'}, re.compile(r'\baccount_tax_cash_basis\b|\breport\b'),
     'manual', "merged modules: account_tax_cash_basis->account, report->web. Update depends and "
     "migrated XML-ID prefixes accordingly (11.0)", 'models-mapping.md'),

    # --- base.group_configuration -> base.group_system ------------------------
    ('group-config', {'xml', 'csv', 'py'}, re.compile(r'base\.group_configuration'),
     'manual', "rename security group base.group_configuration -> base.group_system (11.0)", 'security.md'),
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
        print(f"\nSUMMARY: {len(findings)} finding(s) — ALL manual (11.0 has NO upgrade_code codemod).")
        if findings:
            print('NEXT: apply manual mappings from references/* -> git diff review -> re-scan (expect 0). '
                  'Write custom data migrations (e.g. workflow cleanup) in module migrations/11.0/.')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
