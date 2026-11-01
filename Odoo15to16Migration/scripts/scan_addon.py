#!/usr/bin/env python3
"""Scan Odoo addons for 15-only APIs that Odoo 16 renamed/removed.

Part of the odoo_15_to_16_migration skill. Stdlib only.
Usage:
    python3 scan_addon.py /path/to/addons [--addon NAME] [--json] [--quiet]
Exit code: 1 when findings exist (CI gate), 0 when clean.
Each finding carries: file, line, pattern id, the 16.0 replacement, whether a
bundled `odoo-bin upgrade_code` codemod fixes it, and the reference file.

IMPORTANT — version scope / red lines:
  16.0 has NO `upgrade_code` codemod module (verified: odoo/upgrade_code is
  absent in the 16.0 branch). So EVERY finding here is 'manual' — there is no
  automated rewrite for 15->16. Also, do NOT flag 16->17 concerns here:
  attrs/states REMOVAL, tree->list, name_get REMOVAL, get_resource_path->
  file_path, hooks env arg — those belong to the 16->17 skill. This scanner
  only looks for 15->16 breaks (payment.acquirer->provider, coupon->loyalty,
  model renames stock.lot/account_analytic.plan/mail.channel.member/account.report,
  ir_translation removal, track_visibility->tracking, api.multi removal).
"""
import argparse
import json
import re
import sys
from pathlib import Path

# id, extensions, regex, mode(always 'manual' for 15->16), fix, reference
PATTERNS = [
    # --- payment system restructure (headline break) ----------------------
    ('pay-acquirer-model', {'py', 'xml'}, re.compile(r'payment\.acquirer\b'),
     'manual', "rename model payment.acquirer -> payment.provider (payment restructure 16.0)", 'payment-loyalty.md'),
    ('pay-acquirer-id', {'py', 'xml'}, re.compile(r'\bacquirer_id\b'),
     'manual', "rename field acquirer_id -> provider_id (payment 16.0)", 'payment-loyalty.md'),
    ('pay-acquirer-ref', {'py', 'xml'}, re.compile(r'\bacquirer_reference\b|\bacquirer_ref\b'),
     'manual', "rename acquirer_reference -> provider_reference / acquirer_ref -> provider_ref (payment 16.0)", 'payment-loyalty.md'),
    ('pay-feedback-method', {'py'}, re.compile(r'_handle_feedback_data|_process_feedback_data'),
     'manual', "rename _handle_feedback_data/_process_feedback_data -> _handle_notification_data/_process_notification_data (payment 16.0)", 'payment-loyalty.md'),
    ('pay-acquirer-field-val', {'py', 'xml'}, re.compile(r"'payment\.acquirer'|\"payment\.acquirer\""),
     'manual', "xmlid/ref payment.payment_acquirer_* -> payment.payment_provider_* (payment 16.0)", 'payment-loyalty.md'),

    # --- coupon -> loyalty + module/model renames -------------------------
    ('loy-coupon-model', {'py', 'xml'}, re.compile(r'coupon\.(program|reward|rule|coupon)\b'),
     'manual', "rename coupon.program/reward/rule/coupon -> loyalty.program/reward/rule/card (coupon->loyalty 16.0)", 'payment-loyalty.md'),
    ('dep-coupon', {'py'}, re.compile(r"'(coupon|sale_coupon|website_sale_coupon|pos_coupon|pos_gift_card)'"),
     'manual', "manifest depends: coupon/sale_coupon/website_sale_coupon/pos_coupon/pos_gift_card -> loyalty/sale_loyalty/website_sale_loyalty/pos_loyalty (16.0)", 'models-mapping.md'),
    ('model-stock-lot', {'py', 'xml'}, re.compile(r'stock\.production\.lot\b'),
     'manual', "rename model stock.production.lot -> stock.lot (16.0)", 'models-mapping.md'),
    ('model-analytic-plan', {'py', 'xml'}, re.compile(r'account_analytic\.group\b'),
     'manual', "rename model account_analytic.group -> account_analytic.plan (16.0)", 'models-mapping.md'),
    ('model-channel-member', {'py', 'xml'}, re.compile(r'mail\.channel\.partner\b'),
     'manual', "rename model mail.channel.partner -> mail.channel.member (16.0)", 'models-mapping.md'),
    ('model-tax-report', {'py', 'xml'}, re.compile(r'account\.tax\.report\b'),
     'manual', "rename account.tax.report/account.tax.report.line -> account.report/account.report.line (16.0)", 'models-mapping.md'),
    ('field-user-type-id', {'py', 'xml'}, re.compile(r'\buser_type_id\b'),
     'manual', "rename account.account.user_type_id -> account_type (selection) (16.0)", 'models-mapping.md'),
    ('dep-fetchmail', {'py'}, re.compile(r"'(fetchmail|fetchmail_gmail|fetchmail_outlook)'"),
     'manual', "manifest depends: fetchmail* -> mail/google_gmail/microsoft_outlook (module merge 16.0)", 'models-mapping.md'),
    ('dep-pad', {'py'}, re.compile(r"'(pad|pad_project)'"),
     'manual', "manifest depends: pad/pad_project -> web_editor/project (module merge 16.0)", 'models-mapping.md'),

    # --- translation storage refactor -------------------------------------
    ('orm-ir-translation', {'py', 'xml'}, re.compile(r'ir_translation\b|ir\.translation\b'),
     'manual', "ir_translation table removed in 16.0; translations now JSONB columns — rewrite direct reads/writes (16.0)", 'models-mapping.md'),

    # --- orm / python api ------------------------------------------------
    ('orm-track-visibility', {'py'}, re.compile(r'track_visibility'),
     'manual', "replace track_visibility='always'/'onchange' with tracking=True / tracking='field' (removed in 16.0)", 'orm-api.md'),
    ('orm-api-multi', {'py'}, re.compile(r'@api\.multi|api\.multi\b'),
     'manual', "remove @api.multi decorator (methods are multi by default); api.multi removed in 16.0 (ImportError otherwise)", 'orm-api.md'),

    # --- [verify] website controller routing ------------------------------
    ('http-website-true', {'py'}, re.compile(r"website\s*=\s*True"),
     'manual', "review @http.route(website=True,...) — website module restructured in 16.0 (verify against 16.0 bundle)", 'orm-api.md'),
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
        print(f"\nSUMMARY: {len(findings)} finding(s) — ALL manual (16.0 has NO upgrade_code codemod).")
        if findings:
            print('NEXT: apply manual mappings from references/* -> git diff review -> re-scan (expect 0). '
                  'Run OpenUpgrade/DB migration for automated model/field renames. Write custom data migrations in module migrations/16.0/.')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
