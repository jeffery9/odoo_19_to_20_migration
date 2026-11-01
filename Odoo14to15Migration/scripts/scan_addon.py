#!/usr/bin/env python3
"""Scan Odoo addons for 14-only / 15-breaking APIs that Odoo 15 changed.

Part of the odoo_14_to_15_migration skill. Stdlib only.
Usage:
    python3 scan_addon.py /path/to/addons [--addon NAME] [--json] [--quiet]
Exit code: 1 when findings exist (CI gate), 0 when clean.
Each finding carries: file, line, pattern id, the 15.0 replacement, whether a
bundled `odoo-bin upgrade_code` codemod fixes it, and the reference file.

IMPORTANT — version scope / red lines:
  15.0 has NO `upgrade_code` codemod module (the engine only exists from 18.0+).
  So EVERY finding here is 'manual' — there is no automated rewrite for 14->15.

  Verified against the Odoo CE 14.0 / 15.0 source tree. Several widely repeated
  claims are WRONG for this version pair and are therefore NOT scanned here:
    * `subtype` -> `subtype_xmlid` is a 13->14 change; 14.0 and 15.0 have the
      same `message_post` signature.
    * 15.0 did NOT remove `ir.model` / `ir.model.fields` access. What changed is
      the `ir.model.data` lookup API (public methods private-ised or dropped).
    * `t-raw` / `t-esc` / `SavepointCase` / `Environment.manage()` are DEPRECATED
      in 15.0, not removed (t-raw is actually removed in 16.0).

  Also do NOT flag 13->14 concerns (ir.actions.* access, attrs, _name_search,
  force_company, TransientModel ACL) nor 15->16 ones (payment.acquirer,
  coupon->loyalty, stock.production.lot->stock.lot).
"""
import argparse
import json
import re
import sys
from pathlib import Path

# id, extensions, regex, mode(always 'manual' for 14->15), fix, reference
PATTERNS = [
    # --- QWeb directives deprecated (removed in 16.0) --------------------
    ('t-raw', {'xml', 'js', 'py'}, re.compile(r't-raw'),
     'manual', "t-raw is DEPRECATED in 15.0 (still renders, warns; removed only in 16.0) — use t-out, but t-out ESCAPES by default: only markupsafe.Markup values render as HTML. fields.Html values are Markup; Char/Text are not", 'views-qweb.md'),

    ('t-esc', {'xml'}, re.compile(r't-esc='),
     'manual', "t-esc is deprecated in 15.0 — use t-out. Plain strings are escaped either way; Markup values are not double-escaped", 'views-qweb.md'),

    # --- ir.model.data lookup API (NOT an access-control change) ---------
    ('ir-model-data-api', {'py'}, re.compile(r'xmlid_lookup|xmlid_to_res_id|xmlid_to_res_model_res_id|xmlid_to_object|get_object_reference'),
     'manual', "ir.model.data lookups were private-ised/removed in 15.0 — prefer env.ref('module.xmlid'), else _xmlid_to_res_id / _xmlid_to_res_model_res_id. xmlid_to_object / get_object_reference were REMOVED; _get_id(module, xml_id) was REMOVED too (do not use it as the fix)", 'orm-api.md'),

    # --- mail rendering engines ------------------------------------------
    ('engine-jinja', {'py'}, re.compile(r"engine\s*=\s*['\"]jinja['\"]"),
     'manual', "engine='jinja' raises ValueError in 15.0 — allowed engines are inline_template / qweb / qweb_view, and the default changed to inline_template", 'http-rpc-mail.md'),

    ('jinja-mail', {'xml', 'py'}, re.compile(r'\$\{'),
     'manual', "Jinja ${...} is gone in 15.0 — body_html renders as QWeb (field declares render_engine='qweb', data XML uses type=\"html\"), single-line fields use inline_template {{ }} (#77074)", 'http-rpc-mail.md'),

    # --- assets moved into __manifest__.py `assets` key ------------------
    ('qweb-key', {'py'}, re.compile(r'[\'"]qweb[\'"]\s*:\s*\['),
     'manual', "the 'qweb' __manifest__.py key is IGNORED in 15.0 (no error, templates silently do not load) — move QWeb template lists and JS/SCSS into the 'assets' key; paths are repo-relative", 'models-mapping.md'),

    # --- test base class --------------------------------------------------
    ('savepoint-case', {'py'}, re.compile(r'SavepointCase'),
     'manual', "SavepointCase is a deprecated alias in 15.0 whose base changed from SingleTransactionCase to TransactionCase — use TransactionCase and re-check tests relying on class-level state (#62031)", 'orm-api.md'),

    ('env-manage', {'py'}, re.compile(r'Environment\.manage'),
     'manual', "Environment.manage() is a no-op in 15.0 (warns and yields) — delete it and create Environment(...) directly", 'orm-api.md'),

    # --- core business models -------------------------------------------
    ('payment-method-m2m', {'py', 'xml'}, re.compile(r'(inbound|outbound)_payment_method_ids'),
     'manual', "journal payment methods became one2many rows in 15.0 — inbound/outbound_payment_method_ids -> *_payment_method_line_ids (model account.payment.method.line, with payment_account_id + sequence)", 'models-mapping.md'),

    ('amount-by-group', {'py', 'xml', 'js'}, re.compile(r'amount_by_group'),
     'manual', "amount_by_group was removed from account.move and sale.order in 15.0 — use tax_totals_json / the tax_totals widget", 'models-mapping.md'),

    ('tax-exigible', {'py', 'xml'}, re.compile(r'tax_exigible'),
     'manual', "account.move.line.tax_exigible was removed in 15.0 — use account.move.always_tax_exigible; tax_fiscal_country_id moved to account.move.tax_country_id", 'models-mapping.md'),

    ('stock-inventory', {'py', 'xml'}, re.compile(r'stock\.inventory'),
     'manual', "stock.inventory / stock.inventory.line were removed in 15.0 — count on stock.quant (inventory_quantity, inventory_quantity_set, inventory_date) + stock.inventory.adjustment.name, then action_apply_inventory()", 'models-mapping.md'),

    ('phone-validation-mixin', {'py'}, re.compile(r'phone\.validation\.mixin'),
     'manual', "phone.validation.mixin was removed in 15.0 — call the phone_validation helpers instead of inheriting the mixin", 'models-mapping.md'),
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
                  'Deprecation warnings (t-raw, SavepointCase) only appear with --dev=all; assets and '
                  'rich-text widgets need a manual visual check.')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
