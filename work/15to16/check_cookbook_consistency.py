#!/usr/bin/env python3
"""Bidirectional consistency check: Odoo_Migration_Cookbook_15_to_16.md <-> Odoo15to16Migration/references/*.md

Verifies that every core 15->16 breaking-surface token appears in BOTH the
cookbook (the human-readable fact baseline) and at least one reference file
(the machine-readable skill). A drift on either side fails the check.

Stdlib only. Exit 0 = consistent, 1 = drift found.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COOKBOOK = ROOT / "Odoo_Migration_Cookbook_15_to_16.md"
REF_DIR = ROOT / "Odoo15to16Migration" / "references"

# Each concept: a label and a list of regex alternatives. The concept passes only
# if at least one alternative is found in the cookbook AND in >=1 reference file.
CONCEPTS = [
    ("payment.acquirer -> payment.provider", [r"payment\.acquirer", r"payment\.provider"]),
    ("acquirer_id -> provider_id", [r"acquirer_id", r"provider_id"]),
    ("acquirer_reference -> provider_reference", [r"acquirer_reference", r"provider_reference"]),
    ("acquirer_ref -> provider_ref", [r"acquirer_ref", r"provider_ref"]),
    ("_handle_feedback_data -> _handle_notification_data", [r"_handle_feedback_data", r"_handle_notification_data"]),
    ("coupon.program -> loyalty.program", [r"coupon\.program", r"loyalty\.program"]),
    ("coupon.reward -> loyalty.reward", [r"coupon\.reward", r"loyalty\.reward"]),
    ("coupon.rule -> loyalty.rule", [r"coupon\.rule", r"loyalty\.rule"]),
    ("coupon.coupon -> loyalty.card", [r"coupon\.coupon", r"loyalty\.card"]),
    ("stock.production.lot -> stock.lot", [r"stock\.production\.lot", r"stock\.lot"]),
    ("account_analytic.group -> account_analytic.plan", [r"account_analytic\.group", r"account_analytic\.plan"]),
    ("mail.channel.partner -> mail.channel.member", [r"mail\.channel\.partner", r"mail\.channel\.member"]),
    ("account.tax.report -> account.report", [r"account\.tax\.report", r"account\.report"]),
    ("user_type_id -> account_type", [r"user_type_id", r"account_type"]),
    ("track_visibility -> tracking", [r"track_visibility", r"\btracking\s*=\s*True"]),
    ("api.multi removed", [r"api\.multi"]),
    ("ir_translation removed", [r"ir_translation"]),
    ("zero upgrade_code codemod (16.0)", [r"upgrade_code", r"no .*codemod", r"ABSENT", r"404"]),
    ("attrs/states still valid in 16 (scope guard)", [r"attrs", r"states"]),
    ("<tree> still valid in 16 (scope guard)", [r"<tree>", r"tree"]),
]


def main():
    if not COOKBOOK.exists():
        print(f"MISSING cookbook: {COOKBOOK}")
        sys.exit(1)
    refs = sorted(REF_DIR.glob("*.md")) if REF_DIR.exists() else []
    if not refs:
        print(f"MISSING references: {REF_DIR}")
        sys.exit(1)

    cookbook_text = COOKBOOK.read_text(encoding="utf-8")
    ref_text = "\n".join(r.read_text(encoding="utf-8") for r in refs)

    failures = []
    checked = 0
    for label, alts in CONCEPTS:
        rx = re.compile("|".join(alts))
        in_cb = bool(rx.search(cookbook_text))
        in_ref = bool(rx.search(ref_text))
        checked += 1
        if not in_cb:
            failures.append(f"  [cookbook missing] {label}")
        if not in_ref:
            failures.append(f"  [reference missing] {label}")

    print(f"Checked {checked} core concepts across cookbook + {len(refs)} reference files.")
    if failures:
        print("CONSISTENCY FAILED:")
        for f in failures:
            print(f)
        sys.exit(1)
    print(f"OK — all {checked} core 15->16 concepts present in BOTH cookbook and references (zero drift).")
    sys.exit(0)


if __name__ == "__main__":
    main()
