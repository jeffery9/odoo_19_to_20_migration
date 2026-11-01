#!/usr/bin/env python3
"""Consistency checker: Odoo_Migration_Cookbook_9_to_10.md  <->  Odoo9to10Migration/references/*.md

Exit 0 when every core token appears in BOTH the cookbook and at least one reference
file, and all expected reference files exist and are named by the cookbook. Exit 1 otherwise.

Discipline: a fact asserted in the cookbook must be carried by the skill references
(no drift), and every skill reference must be anchored in the cookbook.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COOKBOOK = ROOT / "Odoo_Migration_Cookbook_9_to_10.md"
REFS_DIR = ROOT / "Odoo9to10Migration" / "references"

# Core tokens that MUST appear in both the cookbook and at least one reference.
TOKENS = [
    "openerp", "odoo", "__manifest__.py", "__openerp__.py", "select", "index = True",
    "base.group_system", "base.group_configuration", "@api.multi", "copy",
    "sales_team", "sales_team.group_sale_salesman", "hr.group_hr_user",
    "hr.group_hr_manager", "menu_human_resources_configuration",
    "product.prod_config_main", "sale.prod_config_main", "<odoo>",
]

EXPECTED_REFS = [
    "orm-api.md", "views-qweb.md", "models-mapping.md",
    "security.md", "http-rpc-mail.md", "upgrade-code.md",
]

REF_ANCHORS = [f"references/{r}" for r in EXPECTED_REFS]  # cookbook should name these


def main():
    errors = []
    if not COOKBOOK.exists():
        print(f"MISSING cookbook: {COOKBOOK}"); sys.exit(1)
    cookbook_text = COOKBOOK.read_text(encoding="utf-8")

    ref_files = sorted(REFS_DIR.glob("*.md"))
    ref_texts = {f.name: f.read_text(encoding="utf-8") for f in ref_files}

    # 1) expected refs exist
    for r in EXPECTED_REFS:
        if r not in ref_texts:
            errors.append(f"missing reference file: {r}")

    # 2) token coverage (cookbook AND >=1 reference)
    for tok in TOKENS:
        in_cb = tok in cookbook_text
        in_ref = any(tok in t for t in ref_texts.values())
        if not in_cb:
            errors.append(f"token '{tok}' MISSING from cookbook")
        if not in_ref:
            errors.append(f"token '{tok}' MISSING from all references")

    # 3) cookbook names every reference file (no orphan reference)
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


if __name__ == "__main__":
    main()
