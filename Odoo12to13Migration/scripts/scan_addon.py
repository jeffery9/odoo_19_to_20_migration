#!/usr/bin/env python3
"""Scan Odoo addons for 12-only / 13-breaking APIs that Odoo 13 renamed/removed.

Part of the odoo_12_to_13_migration skill. Stdlib only.
Usage:
    python3 scan_addon.py /path/to/addons [--addon NAME] [--json] [--quiet]
Exit code: 1 when findings exist (CI gate), 0 when clean.
Each finding carries: file, line, pattern id, the 13.0 replacement, whether a
bundled `odoo-bin upgrade_code` codemod fixes it, and the reference file.

IMPORTANT — version scope / red lines:
  13.0 has NO `upgrade_code` codemod module (the engine only exists from 18.0+).
  So EVERY finding here is 'manual' — there is no automated rewrite for 12->13.
  Also, do NOT flag 13->14 concerns here: ir.actions.* access removal,
  invisible/readonly dynamic-expression -> attrs, _name_search returns ids,
  force_company removal, selection_add ondelete — those belong to the 13->14
  skill. This scanner only looks for 12->13 breaks (account.move merge,
  old decorators, customer_rank, binding_view_types, dp.get_precision,
  track_visibility, oldname, stock.quant quantity, product.product name related,
  account.tax type_tax_use, sudo(user)->with_user, .env.user.company_id, view_type).
"""
import argparse
import json
import re
import sys
from pathlib import Path

# id, extensions, regex, mode(always 'manual' for 12->13), fix, reference
PATTERNS = [
    # --- @api.multi / @api.returns / @api.cr / @api.model_cr removal --------
    ('api-decorators', {'py'}, re.compile(r'@api\.(multi|returns|cr|model_cr)'),
     'manual', "remove @api.multi/@api.returns/@api.cr/@api.model_cr — methods are multi by default in 13.0; wrap body in `for rec in self:` (removed in 13.0)", 'orm-api.md'),

    # --- dp.get_precision -> digits="..." ------------------------------------
    ('dp-get-precision', {'py'}, re.compile(r'dp\.get_precision'),
     'manual', "replace fields.Float(digits=dp.get_precision('X')) with fields.Float(digits='X') (decimal_precision import no longer needed, 13.0)", 'models-mapping.md'),

    # --- track_visibility -> tracking ---------------------------------------
    ('track-visibility', {'py'}, re.compile(r'track_visibility\s*='),
     'manual', "replace track_visibility='onchange' with tracking=True (or tracking=N); track_visibility removed in 13.0", 'models-mapping.md'),

    # --- oldname field attribute removal ------------------------------------
    ('oldname', {'py'}, re.compile(r'\boldname\s*='),
     'manual', "remove oldname= field attribute (no longer supported in 13.0); use openupgradelib rename_fields in migrations/13.0/", 'models-mapping.md'),

    # --- accounting merge: account.invoice / account.voucher ----------------
    ('account-invoice', {'py', 'xml'}, re.compile(r'account\.invoice\b|account\.voucher\b|action_invoice_open|action_invoice_cancel|account_invoice_report'),
     'manual', "account.invoice / account.invoice.line / account.invoice.tax / account.voucher merged into account.move / account.move.line in 13.0; use move_type; action_invoice_open()->post()", 'accounting-models.md'),

    # --- res.partner customer/supplier -> customer_rank/supplier_rank --------
    ('partner-rank', {'py', 'xml'}, re.compile(r'\.customer\b|\.supplier\b|customer_rank|supplier_rank'),
     'manual', "res.partner.customer/supplier booleans -> customer_rank/supplier_rank integers; domain ('customer','=',True) -> ('customer_rank','>',0) (13.0)", 'accounting-models.md'),

    # --- src_model -> binding_model_id --------------------------------------
    ('src-model', {'py', 'xml'}, re.compile(r'src_model'),
     'manual', "ir.actions.* src_model field -> binding_model_id (13.0 still reads src_model but prefer binding_model_id for 13->14 compatibility)", 'views-qweb.md'),

    # --- ir.actions.act_window multi -> binding_view_types -------------------
    ('act-window-multi', {'xml'}, re.compile(r'name\s*=\s*["\']multi["\']'),
     'manual', "replace <field name=\"multi\">True</field> with <field name=\"binding_view_types\">list|form</field> (removed in 13.0); accelerator tag uses binding_views", 'views-qweb.md'),

    # --- view_type attribute on action window removed -----------------------
    ('view-type', {'xml'}, re.compile(r'view_type'),
     'manual', "remove view_type attribute from ir.actions.act_window XML (always form since 11.0, dropped in 13.0)", 'views-qweb.md'),

    # --- sudo(user) -> with_user(user) --------------------------------------
    ('sudo-user', {'py'}, re.compile(r'sudo\([^)\s]'),
     'manual', "replace sudo(user) with with_user(user); parameterless sudo() still valid (13.0)", 'orm-api.md'),

    # --- .env.user.company_id -> .env.company -------------------------------
    ('env-user-company', {'py'}, re.compile(r'\.user\.company_id'),
     'manual', "replace self.env.user.company_id with self.env.company (current active company, 13.0)", 'orm-api.md'),

    # --- stock.quant qty -> quantity ----------------------------------------
    ('stock-quant-qty', {'py'}, re.compile(r'stock\.quant\b'),
     'manual', "stock.quant.qty -> stock.quant.quantity (field renamed in 13.0); review all .qty accesses on quants", 'models-mapping.md'),

    # --- account.tax type -> type_tax_use -----------------------------------
    ('tax-type', {'py', 'xml'}, re.compile(r'type_tax_use|\.type\b'),
     'manual', "account.tax.type -> account.tax.type_tax_use (sale/purchase/none) in 13.0; review .type on account.tax", 'accounting-models.md'),
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
        print(f"\nSUMMARY: {len(findings)} finding(s) — ALL manual (13.0 has NO upgrade_code codemod).")
        if findings:
            print('NEXT: apply manual mappings from references/* -> git diff review -> re-scan (expect 0). '
                  'Write custom data migrations (account.move data, oldname renames, Binary attachment) '
                  'in module migrations/13.0/.')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
