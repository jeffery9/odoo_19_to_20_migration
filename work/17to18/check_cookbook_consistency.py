#!/usr/bin/env python3
"""17->18 Cookbook 与 Skill references 的事实一致性校验（中间产物 · 修订时可复用）。

目的：修订 Cookbook 或 references 任一侧时，防止两边对"17->18 核心变更"的覆盖漂移。
用法：
    python3 work/17to18/check_cookbook_consistency.py
退出码：0 = 一致；1 = 存在漂移（详见输出）。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COOKBOOK = os.path.join(ROOT, "Odoo_Migration_Cookbook_17_to_18.md")
REF_DIR = os.path.join(ROOT, "Odoo17to18Migration", "references")

# 17->18 核心变更 token：必须同时出现在 Cookbook 与 references 中。
# 修订时若新增/移除核心变更，同步维护此列表。
TOKENS = [
    "<list>",
    "decoration-",
    "list_view_ref",
    "name_get",
    "_search_display_name",
    "check_access",
    "_filtered_access",
    "has_group",
    "has_cycle",
    "aggregator",
    "inselect",
    "jsonrpc",
    "type='json'",
    "upgrade_code",
    "17.5-01-tree-to-list",
    "search_fetch",
    "models.Constraint",
    "Domain",
    "kanban-box",
    "states",
    "fields_view_get",
]


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def main():
    if not os.path.exists(COOKBOOK):
        print(f"缺失 Cookbook: {COOKBOOK}")
        return 1
    if not os.path.isdir(REF_DIR):
        print(f"缺失 references 目录: {REF_DIR}")
        return 1

    cookbook = read(COOKBOOK)
    ref_text = ""
    for fn in sorted(os.listdir(REF_DIR)):
        if fn.endswith(".md"):
            ref_text += read(os.path.join(REF_DIR, fn))

    issues = []
    for tok in TOKENS:
        in_cb = tok in cookbook
        in_ref = tok in ref_text
        if in_cb and not in_ref:
            issues.append(f"[cookbook-only] {tok!r} 出现在 Cookbook 但不在 references")
        elif in_ref and not in_cb:
            issues.append(f"[ref-only]      {tok!r} 出现在 references 但不在 Cookbook")

    if issues:
        print("一致性漂移:")
        for it in issues:
            print("  -", it)
        print(f"\n共 {len(issues)} 处漂移；请同步 Cookbook 与 references 后重跑。")
        return 1

    print(f"OK: 全部 {len(TOKENS)} 个核心 token 在 Cookbook 与 references 中一致覆盖。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
