#!/usr/bin/env python3
"""Scan Odoo addons for 16-only APIs that Odoo 17 removed/renamed.

Part of the odoo_16_to_17_migration skill. Stdlib only.
Usage:
    python3 scan_addon.py /path/to/addons [--addon NAME] [--json] [--quiet]
Exit code: 1 when findings exist (CI gate), 0 when clean.
Each finding carries: file, line, pattern id, the 17.0 replacement, whether a
bundled `odoo-bin upgrade_code` codemod fixes it, and the reference file.

IMPORTANT — version scope / red lines:
  17.0 has NO `upgrade_code` codemod module (verified: odoo/upgrade_code is
  absent in the 17.0 branch). So EVERY finding here is 'manual' — there is no
  automated rewrite for 16->17. Also, do NOT flag 17->18 concerns here:
  tree->list, name_get REMOVAL, check_access_rights/user_has_groups/
  check_recursion REMOVAL, inselect REMOVAL, group_operator->aggregator,
  type='json'->jsonrpc — those belong to the 17->18 skill. This scanner only
  looks for 16->17 breaks (attrs/states, column_invisible, settings views,
  hooks env, get_resource_path->file_path, active_* context, message_post body).
"""
import argparse
import json
import re
import sys
from pathlib import Path

# id, extensions, regex, mode(always 'manual' for 16->17), fix, reference
PATTERNS = [
    # --- views / qweb ----------------------------------------------------
    ('view-attrs-xml', {'xml'}, re.compile(r'\battrs\s*='),
     'manual', "rewrite as inline invisible=/readonly=/required= Python expr (attrs attr rejected since 17.0)", 'views-qweb.md'),
    ('view-states-xml', {'xml'}, re.compile(r'\bstates\s*='),
     'manual', "remove states=; use invisible=/readonly= condition (states attr rejected since 17.0)", 'views-qweb.md'),
    ('view-col-invisible', {'xml'}, re.compile(r'invisible\s*=\s*["\']1["\']'),
     'manual', "if inside a tree/list view use column_invisible='1' (invisible='1' shows an empty column in 17)", 'views-qweb.md'),
    ('view-settings-pane', {'xml'}, re.compile(r'o_setting_(right|left)_pane'),
     'manual', "remove o_setting_right_pane / o_setting_left_pane divs; use <setting> (res.config.settings simplified)", 'views-qweb.md'),
    ('view-app-setting-block', {'xml'}, re.compile(r'app_setting_block'),
     'manual', "replace app_setting_block with <block> (res.config.settings simplified)", 'views-qweb.md'),
    ('view-active-context', {'xml'}, re.compile(r'active_(id|ids|model)'),
     'manual', "replace active_id->id, active_model->hardcoded model name; rewrite active_ids per intent (context warning since 17.0)", 'views-qweb.md'),
    ('view-t-attf', {'xml'}, re.compile(r't-attf-'),
     'manual', "use t-att=\"f'...'\" f-string expression (t-attf- deprecated since Owl 2 / 16; verify)", 'views-qweb.md'),
    # --- orm / python -----------------------------------------------------
    ('orm-name-get', {'py'}, re.compile(r'def\s+name_get\b'),
     'manual', "_compute_display_name + display_name stored field (name_get deprecated since 16.4, removed in 18)", 'orm-api.md'),
    ('hook-init-cr-registry', {'py'}, re.compile(r'def\s+(pre_init_hook|post_init_hook|uninstall_hook)\s*\([^)]*(cr|registry)'),
     'manual', "change signature to def hook(env): (hook arg is now env since 17.0)", 'orm-api.md'),
    ('orm-get-resource-path', {'py'}, re.compile(r'get_resource_path'),
     'manual', "from odoo.tools import file_path; file_path('module/path/file.xml') (get_resource_path removed in 17.0)", 'orm-api.md'),
    ('http-message-post-body', {'py'}, re.compile(r'message_post\s*\('),
     'manual', "body now defaults to text/Markdown; pass body_is_html=True for HTML (message_post body format change 17.0)", 'http-rpc-mail.md'),
    # --- frontend [verify] ------------------------------------------------
    ('fe-jquery', {'js', 'xml'}, re.compile(r'(?<![\w$.])\$\s*\(|jQuery\s*\('),
     'manual', "if jQuery removed in your 17.0 bundle, rewrite to native/Owl (version scope disputed: verify against web.assets_frontend)", 'views-qweb.md'),
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
                    print(f"         → {f['fix']}  (ref: references/{f['ref']})")
        print(f"\nSUMMARY: {len(findings)} finding(s) — ALL manual (17.0 has NO upgrade_code codemod).")
        if findings:
            print('NEXT: apply manual mappings from references/* → git diff review → re-scan (expect 0). '
                  'Write data migrations in module migrations/17.0/.')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
