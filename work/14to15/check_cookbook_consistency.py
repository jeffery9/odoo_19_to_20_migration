#!/usr/bin/env python3
"""Consistency checker: Odoo_Migration_Cookbook_14_to_15.md  <->  Odoo14to15Migration/references/*.md

Exit 0 when every core token appears in BOTH the cookbook and at least one reference
file, and all expected reference files exist. Exit 1 otherwise.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COOKBOOK = ROOT / "Odoo_Migration_Cookbook_14_to_15.md"
REFS_DIR = ROOT / "Odoo14to15Migration" / "references"

TOKENS = [
    # QWeb directives + the escaping trap
    "t-raw", "t-out", "t-esc", "Markup",
    # data-access API (the real 14→15 break, not an access-control change)
    "ir.model.fields", "_xmlid_lookup", "_xmlid_to_res_id",
    # mail rendering engines
    "inline_template", "mail.template", "render_engine", "#77074",
    # frontend / assets
    ".esm.js", "@odoo-module", "qweb",
    # tests (deprecated, NOT removed)
    "SavepointCase", "TransactionCase", "Environment.manage",
    # red-line check: belongs to 13→14, must stay documented as such
    "subtype_xmlid", "message_post",
    # core business models
    "payment_method_line_ids", "amount_by_group", "tax_exigible",
    "stock.inventory", "phone.validation.mixin", "detailed_type",
    # tooling
    "upgrade_code",
]

EXPECTED_REFS = [
    "orm-api.md", "views-qweb.md", "models-mapping.md",
    "security.md", "http-rpc-mail.md", "upgrade-code.md",
]

REF_ANCHORS = [f"references/{r}" for r in EXPECTED_REFS]


def main():
    errors = []
    if not COOKBOOK.exists():
        print(f"MISSING cookbook: {COOKBOOK}"); sys.exit(1)
    cookbook_text = COOKBOOK.read_text(encoding="utf-8")

    ref_files = sorted(REFS_DIR.glob("*.md"))
    ref_texts = {f.name: f.read_text(encoding="utf-8") for f in ref_files}

    for r in EXPECTED_REFS:
        if r not in ref_texts:
            errors.append(f"missing reference file: {r}")

    for tok in TOKENS:
        in_cb = tok in cookbook_text
        in_ref = any(tok in t for t in ref_texts.values())
        if not in_cb:
            errors.append(f"token '{tok}' MISSING from cookbook")
        if not in_ref:
            errors.append(f"token '{tok}' MISSING from all references")

    for anchor in REF_ANCHORS:
        if anchor not in cookbook_text:
            errors.append(f"cookbook does not reference '{anchor}'")

    if errors:
        print("CONSISTENCY FAILED:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print(f"CONSISTENCY OK: {len(TOKENS)} tokens aligned across cookbook + "
          f"{len(EXPECTED_REFS)} references; all references anchored.")
    sys.exit(0)


if __name__ == '__main__':
    main()
