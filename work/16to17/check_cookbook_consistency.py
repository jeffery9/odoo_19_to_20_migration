#!/usr/bin/env python3
"""Bidirectional consistency check: Odoo_Migration_Cookbook_16_to_17.md <-> Odoo16to17Migration/references/*.md

Each canonical 16->17 token must appear in BOTH the cookbook (human narrative)
and at least one reference file (machine-readable mapping). Case-insensitive.
Exit code 1 on any missing token (CI gate), 0 when fully aligned.

Stdlib only.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COOKBOOK = ROOT / "Odoo_Migration_Cookbook_16_to_17.md"
REFS_DIR = ROOT / "Odoo16to17Migration" / "references"

# Tokens (lowercased) that MUST appear in both the cookbook and the references.
# These encode the verified 16->17 breaking surface; drift between the two
# artifacts means one was edited without the other.
TOKENS = [
    "attrs",                 # attrs attr removed
    "states",                # states attr removed
    "column_invisible",      # list invisible->column_invisible
    "message_post",          # mail body change
    "body_is_html",          # html flag
    "post_init_hook",        # hook env
    "uninstall_hook",        # hook env
    "get_resource_path",     # removed
    "file_path",             # replacement
    "active_id",             # context rewrite
    "active_model",          # context rewrite
    "active_ids",            # context rewrite
    "o_setting",             # settings panes removed
    "python 3.10",           # runtime floor
    "odoo/upgrade_code/",    # proven absent in 17.0
    "libsass",               # SCSS still compiles in 17.0
    "name_get",              # deprecated (not removed)
    "_compute_display_name", # replacement
    "tree",                  # still valid in 17.0 (scope guard)
    "mail.channel",          # still valid in 17.0
    "group_operator",        # still valid in 17.0
    "web_editor",            # still usable in 17.0
    "bootstrap",             # [verify] frontend scope
    "jquery",                # [verify] frontend scope
    "werkzeug",              # [verify] 2.0.2 floor
]


def main():
    if not COOKBOOK.exists():
        print(f"MISSING cookbook: {COOKBOOK}")
        sys.exit(1)
    cookbook = COOKBOOK.read_text(encoding="utf-8").lower()

    ref_text = ""
    ref_files = sorted(REFS_DIR.glob("*.md")) if REFS_DIR.exists() else []
    for f in ref_files:
        ref_text += f.read_text(encoding="utf-8").lower() + "\n"

    missing_cookbook = [t for t in TOKENS if t not in cookbook]
    missing_refs = [t for t in TOKENS if t not in ref_text]

    print(f"Cookbook: {COOKBOOK.name}  ({len(cookbook)} chars)")
    print(f"References: {len(ref_files)} file(s)  ({len(ref_text)} chars)")
    print(f"Tokens checked: {len(TOKENS)}")

    ok = True
    if missing_cookbook:
        ok = False
        print(f"\n[FAIL] tokens MISSING from cookbook ({len(missing_cookbook)}):")
        for t in missing_cookbook:
            print(f"   - {t}")
    if missing_refs:
        ok = False
        print(f"\n[FAIL] tokens MISSING from references ({len(missing_refs)}):")
        for t in missing_refs:
            print(f"   - {t}")

    # Reverse: ensure every reference file is actually cited by the cookbook
    # (no orphan reference shipped without narrative coverage).
    orphan = []
    for f in ref_files:
        stem = f.stem
        if stem not in cookbook:
            orphan.append(stem)
    if orphan:
        ok = False
        print(f"\n[FAIL] reference files NOT cited in cookbook ({len(orphan)}):")
        for s in orphan:
            print(f"   - references/{s}.md")

    if ok:
        print(f"\nPASS: all {len(TOKENS)} tokens present in BOTH cookbook and "
              f"references; all {len(ref_files)} reference files cited.")
        sys.exit(0)
    else:
        print("\nCONSISTENCY FAILED — fix drift between cookbook and references.")
        sys.exit(1)


if __name__ == "__main__":
    main()
