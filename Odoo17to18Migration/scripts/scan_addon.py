#!/usr/bin/env python3
"""Scan Odoo addons for 17-only APIs that Odoo 18 removed/renamed.

Part of the odoo_17_to_18_migration skill. Stdlib only.
Usage:
    python3 scan_addon.py /path/to/addons [--addon NAME] [--json] [--quiet]
Exit code: 1 when findings exist (CI gate), 0 when clean.
Each finding carries: file, line, pattern id, the 18.0 replacement, whether a
bundled `odoo-bin upgrade_code` codemod fixes it, and the reference file.

Note: 17->18 ships only ONE bundled codemod (17.5-01-tree-to-list). Everything
else below is 'manual' — there is no codemod for name_get / check_access /
user_has_groups / group_operator / json->jsonrpc in the 17->18 flow (those
codemods, where they exist, ship in the 19.0 tree for the 18->19 step).
"""
import argparse
import json
import re
import sys
from pathlib import Path

# id, extensions, regex, mode(auto=codemod exists | manual), fix, reference
PATTERNS = [
    # --- views / qweb ----------------------------------------------------
    ('view-tree-tag', {'xml'}, re.compile(r'<tree(\s|>|/)'),
     'auto', '<list> (codemod 17.5-01-tree-to-list)', 'views-qweb.md'),
    ('view-list-colors', {'xml'}, re.compile(r'\bcolors\s*='),
     'manual', "decoration-* (decoration-danger/success/info/warning/muted/primary)", 'views-qweb.md'),
    ('view-tree-view-ref', {'xml', 'py'}, re.compile(r'tree_view_ref'),
     'manual', 'list_view_ref', 'views-qweb.md'),
    ('view-states-attr', {'xml'}, re.compile(r'\bstates\s*='),
     'manual', 'replace field states="..." with invisible/readonly condition (states attr removed)', 'views-qweb.md'),
    ('view-fields-view-get', {'py'}, re.compile(r'\.fields_view_get\('),
     'manual', 'get_views()', 'views-qweb.md'),
    ('view-kanban-box', {'xml', 'js'}, re.compile(r'kanban-box'),
     'manual', 'card (version scope disputed: OCA=18.0, 18->19 cookbook=19.0 Owl3; verify against 18.0 template)', 'views-qweb.md'),
    # --- orm / python -----------------------------------------------------
    ('orm-name-get', {'py'}, re.compile(r'def\s+name_get\b'),
     'manual', 'display_name computed field / _compute_display_name', 'orm-api.md'),
    ('orm-name-search', {'py'}, re.compile(r'def\s+_name_search\b'),
     'manual', '_search_display_name(operator, value)', 'orm-api.md'),
    ('orm-check-access-rights', {'py'}, re.compile(r'\.check_access_rights\('),
     'manual', 'check_access(op) / has_access(op)', 'orm-api.md'),
    ('orm-check-access-rule', {'py'}, re.compile(r'\.check_access_rule\('),
     'manual', 'folded into check_access(op)', 'orm-api.md'),
    ('orm-filter-access-rules', {'py'}, re.compile(r'_\.?filter_access_rules'),
     'manual', '_filtered_access(op)', 'orm-api.md'),
    ('orm-user-has-groups', {'py'}, re.compile(r'\.user_has_groups\('),
     'manual', 'self.env.user.has_group(...)', 'orm-api.md'),
    ('orm-check-recursion', {'py'}, re.compile(r'_?check_recursion\(|\._check_m2m_recursion\('),
     'manual', 'has_cycle(field_name=None)', 'orm-api.md'),
    ('orm-group-operator', {'py'}, re.compile(r'\bgroup_operator\s*='),
     'manual', "aggregator='sum' (renamed in 17.2)", 'orm-api.md'),
    ('orm-inselect', {'py'}, re.compile(r'inselect'),
     'manual', "use 'in' with a Query/SQL object (operator removed in 17.4)", 'orm-api.md'),
    ('orm-copy-data', {'py'}, re.compile(r'def\s+copy_data\b'),
     'manual', 'return a LIST of value dicts; self may be a multi-recordset (18.0 #154132)', 'orm-api.md'),
    # --- http / rpc / mail ------------------------------------------------
    ('http-route-json', {'py'}, re.compile(r"type\s*=\s*['\"]json['\"]"),
     'manual', "type='jsonrpc' for web-client routes (codemod 18.1-02-route-jsonrpc ships in 19 tree; manual for 17->18)", 'http-rpc-mail.md'),
]

EXT_MAP = {'.py': 'py', '.xml': 'xml', '.csv': 'csv', '.js': 'js'}


def scan(root: Path, addon_filter=None):
    findings = []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        ext = EXT_MAP.get(path.suffix)
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
                tag = 'codemod' if f['mode'] == 'auto' else 'manual '
                print(f"  L{f['line']:<5} [{tag}] {f['id']}: {f['snippet']}")
                if not args.quiet:
                    print(f"         → {f['fix']}  (ref: references/{f['ref']})")
        auto = sum(1 for f in findings if f['mode'] == 'auto')
        print(f"\nSUMMARY: {len(findings)} finding(s) — {auto} fixable by "
              f"`odoo-bin upgrade_code --from 17.0` (tree->list only), {len(findings) - auto} manual.")
        if findings:
            print('NEXT: upgrade_code --from 17.0 --dry-run → real run → git diff review → manual mappings → re-scan (expect 0).')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
