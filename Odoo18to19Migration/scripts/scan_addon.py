#!/usr/bin/env python3
"""Scan Odoo addons for 19-only APIs that Odoo 20 removed/renamed.

Part of the odoo_19_to_20_migration skill. Stdlib only.
Usage:
    python3 scan_addon.py /path/to/addons [--addon NAME] [--json] [--quiet]
Exit code: 1 when findings exist (CI gate), 0 when clean.
Each finding carries: file, line, pattern id, the 20.0 replacement, whether a
bundled `odoo-bin upgrade_code` codemod fixes it, and the reference file.
"""
import argparse
import json
import re
import sys
from pathlib import Path

# id, extensions, regex, mode(auto=codemod exists | manual), fix, reference
PATTERNS = [
    # --- security ---------------------------------------------------------
    ('sec-file-name', {'csv'}, re.compile(r'^id,name,model_id:id,group_id:id,perm_read', re.M),
     'manual', 'rename file to security/ir.access.csv; columns id,name,model_id,group_id/id,operation,domain; merge ir.rule XML; or run codemod 19.4-00-ir-access', 'security-and-orm.md'),
    ('sec-perm-cols', {'csv'}, re.compile(r'perm_(read|write|create|unlink)'),
     'manual', 'perm_* columns are illegal in 20: use operation strings (crud, cru, cr, …)', 'security-and-orm.md'),
    ('sec-irule-xml', {'xml'}, re.compile(r'<record[^>]*model=["\']ir\.rule["\']'),
     'auto', 'ir.rule XML merged into ir.access.csv domain column (codemod 19.4-00-ir-access)', 'security-and-orm.md'),
    ('sec-true-domain', {'csv', 'xml'}, re.compile(r"\[\s*\(\s*1\s*,\s*['\"]=['\"]\s*,\s*1\s*\)\s*\]"),
     'manual', '[(1,"=",1)]-style domains fail 20 validation: use empty domain', 'security-and-orm.md'),
    # --- orm / python -----------------------------------------------------
    ('orm-sql-constraints', {'py'}, re.compile(r'\b_sql_constraints\s*='),
     'auto', '_name = models.Constraint(\'sql\', \'msg\') (codemod 18.1-00-sql-constraint)', 'security-and-orm.md'),
    ('orm-fields-view-get', {'py'}, re.compile(r'\.fields_view_get\('),
     'manual', 'self._get_view(...)', 'security-and-orm.md'),
    ('orm-check-access-rights', {'py'}, re.compile(r'\.check_access_rights\('),
     'manual', 'check_access(op) (raises) / has_access(op) (bool)', 'security-and-orm.md'),
    ('orm-check-access-rule', {'py'}, re.compile(r'\.check_access_rule\('),
     'manual', 'folded into check_access(op)', 'api-deltas-vol2.md'),
    ('orm-field-access-rights', {'py'}, re.compile(r'\.check_field_access_rights\('),
     'manual', 'check_field_access(field, op) / has_field_access(field, op)', 'api-deltas-vol2.md'),
    ('orm-user-has-groups', {'py'}, re.compile(r'\.user_has_groups\('),
     'manual', 'self.env.user.has_groups(...)', 'security-and-orm.md'),
    ('orm-self-context', {'py'}, re.compile(r'\bself\._context\b'),
     'manual', 'self.env.context', 'security-and-orm.md'),
    ('orm-user-company', {'py'}, re.compile(r'env\.user\.company_id\b'),
     'manual', 'self.env.company', 'security-and-orm.md'),
    ('orm-toggle-active', {'py'}, re.compile(r'\.toggle_active\('),
     'manual', 'action_archive / action_unarchive', 'security-and-orm.md'),
    ('orm-check-recursion', {'py'}, re.compile(r'\._check_recursion\(|\._check_m2m_recursion\('),
     'manual', '_has_cycle(field_name=None) (available since 19)', 'api-deltas-vol2.md'),
    ('orm-copy-translations', {'py'}, re.compile(r'\.copy_translations\('),
     'manual', 'removed in 20, no public replacement: delete the call', 'api-deltas-vol2.md'),
    ('orm-read-group-lazy', {'py'}, re.compile(r'read_group\([^\n]*?lazy\s*='),
     'manual', 'read_group(domain, groupby=(), aggregates=(), having=(), …) -> list[tuple]', 'security-and-orm.md'),
    ('orm-rec-names-search-list', {'py'}, re.compile(r'_rec_names_search\s*=\s*\['),
     'auto', 'tuple form (codemod 19.5-00-tuple-rec_names_search)', 'api-deltas-vol2.md'),
    # --- domains / imports ------------------------------------------------
    ('imp-osv-expression', {'py'}, re.compile(r'from\s+odoo\.osv\s+import|odoo\.osv\.expression'),
     'manual', 'from odoo.orm.domains import Domain (odoo.osv removed)', 'security-and-orm.md'),
    ('imp-tools-ormcache', {'py'}, re.compile(r'from\s+odoo\.tools\s+import[^\n#]*\bormcache\b'),
     'auto', '@api.ormcache (codemod 19.4-00-ormcache-on-transaction covers clear_cache; decorator move is manual)', 'api-deltas-vol2.md'),
    ('imp-ormcache-context', {'py'}, re.compile(r'\bormcache_context\b'),
     'manual', 'removed: fold context values into explicit cache-key arguments', 'api-deltas-vol2.md'),
    ('imp-tools-query', {'py'}, re.compile(r'from\s+odoo\.tools\s+import[^\n#]*\bQuery\b'),
     'manual', 'from odoo.orm.query import Query', 'api-deltas-vol2.md'),
    ('imp-convert-imports', {'py'}, re.compile(r'\bconvert_(xml|csv|sql)_import\b'),
     'manual', 'no longer exported from odoo.tools (internal odoo/tools/convert.py)', 'api-deltas-vol2.md'),
    ('imp-private-binary', {'py'}, re.compile(r'from\s+odoo\.tools\.binary\s+import'),
     'manual', 'public in 20: from odoo.tools import BinaryValue, BinaryBytes', 'binary-http-mail.md'),
    # --- fields -----------------------------------------------------------
    ('fld-group-operator', {'py'}, re.compile(r'\bgroup_operator\s*='),
     'manual', "aggregator='sum' (group_operator removed in 20)", 'api-deltas-vol2.md'),
    ('fld-domain-raw-sql', {'py'}, re.compile(r'SQL\([^)]*\)[^\n]*#.*domain|domain\s*=\s*\[[^\]]*SQL\('),
     'manual', 'Domain.custom(to_sql=lambda table: SQL(...)): raw SQL leaves raise TypeError in 20', 'api-deltas-vol2.md'),
    # --- http / mail / binary --------------------------------------------
    ('http-route-json', {'py'}, re.compile(r"type\s*=\s*['\"]json['\"]"),
     'auto', "type='jsonrpc' for web-client routes (codemod 18.1-02-route-jsonrpc); JSON-2 /json/2 stays for external APIs", 'binary-http-mail.md'),
    ('http-request-env', {'py'}, re.compile(r'\brequest\.env\b'),
     'manual', 'use env in report parsers/models: request may be unbound (RuntimeError)', 'binary-http-mail.md'),
    ('http-request-website', {'py'}, re.compile(r'\brequest\.website\b'),
     'manual', 'self.env.website (context["website_id"])', 'binary-http-mail.md'),
    ('mail-post-state', {'py', 'xml'}, re.compile(r'state=["\']?mail_post|"mail_post"'),
     'manual', 'server-action mail state replaced by mail_post_method', 'binary-http-mail.md'),
    ('bin-xlwt', {'py'}, re.compile(r'\bxlwt\b'),
     'manual', "xlsxwriter + io.BytesIO({'in_memory': True}) + BinaryBytes", 'binary-http-mail.md'),
    ('bin-pypdf2', {'py'}, re.compile(r'\bPyPDF2\b'),
     'manual', 'from odoo.tools.pdf import PdfFileWriter, PdfFileReader', 'binary-http-mail.md'),
    ('bin-pytz', {'py'}, re.compile(r'^\s*(import|from)\s+pytz\b', re.M),
     'manual', 'datetime.UTC and zoneinfo', 'security-and-orm.md'),
    ('bin-render-qweb-template', {'py'}, re.compile(r'_render_qweb_pdf\(\s*[\'"][a-z_\.]+[\'"]\s*\)'),
     'manual', 'pass the report ACTION xmlid, not the template xmlid', 'binary-http-mail.md'),
    # --- views / qweb / owl ----------------------------------------------
    ('view-tree-tag', {'xml'}, re.compile(r'<tree(\s|>|/)'),
     'auto', '<list> (codemod 17.5-01-tree-to-list)', 'views-qweb-owl.md'),
    ('view-date-filter-attrs', {'xml'}, re.compile(r'\b(start_month|end_month|start_year|end_year)\s*='),
     'auto', 'range attrs on date search filters removed (codemod 20.0-00-search-date-filters)', 'views-qweb-owl.md'),
    ('view-base64-file', {'xml'}, re.compile(r'type=["\']base64["\'][^>]*file='),
     'auto', '20 loading form for base64 payloads (codemod 19.3-00-base64-in-xml)', 'views-qweb-owl.md'),
    ('view-fa-icon', {'xml', 'js'}, re.compile(r'icon=["\']fa-|class=["\'][^"\']*fa\s+fa-'),
     'manual', 'web client: oi + data-icon / web/icons.py names; website: Material Symbols ligature', 'views-qweb-owl.md'),
    ('view-ribbon-old', {'xml'}, re.compile(r'bg_color=["\']bg-'),
     'manual', 'title="…" + bg_color="text-bg-*" (+ invisible="active" for Archived)', 'views-qweb-owl.md'),
    ('owl-legacy-rpc', {'js'}, re.compile(r'this\._rpc\('),
     'manual', 'use the orm service: this.env.services.orm.…', 'views-qweb-owl.md'),
    # --- cache / tests ----------------------------------------------------
    ('cache-clear-cache', {'py'}, re.compile(r'registry\.clear_cache'),
     'auto', 'self.env.transaction.invalidate_ormcache() (codemod 19.4-00-ormcache-on-transaction)', 'api-deltas-vol2.md'),
    ('test-queries-contain', {'py'}, re.compile(r'\bassertQueriesContain\b'),
     'manual', 'assertQueries / assertQueryCount + QueryLike matchers', 'api-deltas-vol2.md'),
    ('test-registry-mode', {'py'}, re.compile(r'registry_(enter|leave)_test_mode'),
     'manual', 'with self.registry_test_mode():', 'api-deltas-vol2.md'),
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
        # file-name level check
        if path.name == 'ir.model.access.csv':
            findings.append({'file': str(path), 'line': 1, 'id': 'sec-file-name', 'mode': 'manual',
                             'snippet': 'file name ir.model.access.csv',
                             'fix': PATTERNS[0][4], 'ref': PATTERNS[0][5]})
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
              f"`odoo-bin upgrade_code --from 19.0`, {len(findings) - auto} manual.")
        if findings:
            print('NEXT: upgrade_code --dry-run → real run → git diff review → manual mappings → re-scan (expect 0).')
    sys.exit(1 if findings else 0)


if __name__ == '__main__':
    main()
