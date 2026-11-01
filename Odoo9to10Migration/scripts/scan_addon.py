#!/usr/bin/env python3
"""Scan Odoo addons for 9-only APIs that Odoo 10 renamed/removed.

Part of the odoo_9_to_10_migration skill. Stdlib only.
Usage:
    python3 scan_addon.py /path/to/addons [--addon NAME] [--json] [--quiet]
Exit code: 1 when findings exist (CI gate), 0 when clean.
Each finding carries: file, line, pattern id, the 10.0 replacement, whether a
bundled `odoo-bin upgrade_code` codemod fixes it, and the reference file.

IMPORTANT — version scope / red lines:
  10.0 and earlier have NO `upgrade_code` codemod module (the engine only
  exists from 18.0+). So EVERY finding here is 'manual' — there is no automated
  rewrite for 9->10.
  Also, do NOT flag 10->11 concerns here: Python 3 mandatory, Workflow removal,
  QWeb report API rewrite, module rename/merge, base.group_configuration->
  base.group_system (that is THIS pair's group rename, but the bigger
  group-modularization also belongs here). Do NOT flag 11->12 concerns:
  @api.one removal, fields.Date runtime object, parent_path,
  ir.actions.act_window.view removal, do_notify/do_warning removal,
  t-field-options->t-options. This scanner only looks for 9->10 breaks
  (openerp->odoo package rename, __openerp__.py->__manifest__.py,
  select=True->index=True, XML string selectors / <openerp>/<data> root -> <odoo>,
  base.group_configuration->base.group_system, copy @api.one->@api.multi,
  security-group modularization base.* -> sales_team.* / hr.*).
"""
import argparse
import json
import re
import sys
from pathlib import Path

# id, extensions, regex, mode(always 'manual' for 9->10), fix, reference
PATTERNS = [
    # --- openerp package rename (headline break) ------------------------------
    ('openerp-import', {'py'}, re.compile(r'from openerp|import openerp'),
     'manual', "replace `from openerp` / `import openerp` with `from odoo` / "
     "`import odoo` (openerp package no longer exists in 10.0) (10.0)", 'orm-api.md'),

    # --- __openerp__.py -> __manifest__.py ------------------------------------
    ('manifest-rename', {'py'}, re.compile(r'__openerp__'),
     'manual', "rename `__openerp__.py` -> `__manifest__.py` (and update any "
     "references to the manifest filename) (10.0)", 'orm-api.md'),

    # --- select = True -> index = True ----------------------------------------
    ('select-index', {'py'}, re.compile(r'select\s*=\s*True|select\s*=\s*1'),
     'manual', "replace field `select = True` / `select=1` with `index = True` "
     "(10.0)", 'orm-api.md'),

    # --- XML string selectors / <openerp>/<data> root -> <odoo> ---------------
    ('xml-selector', {'xml'}, re.compile(
        r'select\s*=\s*"|position\s*=\s*"after"|<openerp>|<data>'),
     'manual', "replace XML inherit string/position selectors with attribute "
     "selectors (usually name); replace <openerp>/<data> root wrappers with "
     "<odoo>. Review <data> hits to confirm they are root wrappers (10.0)", 'views-qweb.md'),

    # --- base.group_configuration -> base.group_system ------------------------
    ('group-config', {'xml', 'csv', 'py'}, re.compile(r'base\.group_configuration'),
     'manual', "rename security group base.group_configuration -> base.group_system (10.0)", 'security.md'),

    # --- copy method @api.one -> @api.multi -----------------------------------
    ('copy-decorator', {'py'}, re.compile(
        r'@api\.one[\s\S]{0,200}?def\s+copy|def\s+copy[\s\S]{0,200}?@api\.one'),
     'manual', "change the `copy` method decorator from @api.one to @api.multi "
     "(add self.ensure_one() / for record in self: if it assumed a singleton) (10.0)", 'orm-api.md'),

    # --- security-group modularization: base.* -> sales_team.* / hr.* ----------
    ('group-move', {'xml', 'csv', 'py'}, re.compile(
        r'base\.group_sale_salesman\b|base\.group_sale_salesman_all_leads|'
        r'base\.group_sale_manager|base\.group_hr_user|base\.group_hr_manager|'
        r'menu_hr_configuration|website\.salesteam_website_sales|'
        r'product\.prod_config_main'),
     'manual', "repoint modularized security ids: base.group_sale_* -> "
     "sales_team.*, base.group_hr_* -> hr.*, menu_hr_configuration -> "
     "menu_human_resources_configuration, website.salesteam_website_sales -> "
     "sales_team.salesteam_website_sales, product.prod_config_main -> "
     "sale.prod_config_main (10.0)", 'security.md'),
]


def scan(root: Path, addon_filter=None):
    findings = []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        # filename-based detection (manifest rename / openerp compat alias)
        if path.name == '__openerp__.py':
            findings.append({'file': str(path), 'line': 1, 'id': 'manifest-rename',
                             'mode': 'manual',
                             'snippet': '__openerp__.py (manifest file)',
                             'fix': "rename `__openerp__.py` -> `__manifest__.py` (10.0)",
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
        print(f"\nSUMMARY: {len(findings)} finding(s) — ALL manual (10.0 has NO upgrade_code codemod).")
        if findings:
            print('NEXT: apply manual mappings from references/* -> git diff review -> re-scan (expect 0). '
                  'Write custom data migrations (e.g. group-id repointing) in module migrations/10.0/.')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
