#!/usr/bin/env python3
"""Build Odoo Migration Cookbook Volume II (companion, gaps & addenda)."""
import html, re

css = re.search(r'<style>(.*?)</style>', open('work/book.html').read(), re.S).group(1)
css = css.replace(".cover-bottom { margin-top: 372pt; }", ".cover-bottom { margin-top: 330pt; }")

def esc(t): return html.escape(t, quote=False)

SEG = {'t': '', 'c': 'chip', 'b': 'b', 'i': 'i', 'cb': 'chip b', 'g': 'b'}

def runs_html(segs, default=12.8):
    out = []
    for kind, txt in segs:
        cls = SEG[kind]
        st = 'font-size:9.8pt' if (kind in ('c', 'cb') and default > 10) else ''
        color = 'color:#8b6914' if kind == 'g' else ''
        attr = ''
        if cls: attr += ' class="%s"' % cls
        if st or color: attr += ' style="%s"' % ';'.join(x for x in (st, color) if x)
        out.append('<span%s>%s</span>' % (attr, esc(txt)))
    return ''.join(out)

def cell_html(lines, default=9.8):
    return '<br/>'.join(runs_html(ln, default) for ln in lines)

O = []
def cover():
    O.append('''<div class="coverpage">
<div class="cover-rule"></div>
<div class="cover-title" style="font-size:27pt">Odoo Migration</div>
<div class="cover-title" style="font-size:27pt">Cookbook — Volume II</div>
<div class="cover-sub" style="font-size:16.5pt">Closing the Gaps: Version 19 to Version 20</div>
<div class="cover-mono">COMMUNITY EDITION AND ENTERPRISE EDITION · COMPANION EDITION · OCTOBER 2026</div>
<div class="cover-bottom">
<div class="cover-line">An independent companion to Volume I</div>
<div class="cover-line">Every entry verified against the odoo/odoo source trees, branches 19.0 and 20.0</div>
</div></div>''')

def h1(tid, txt): O.append('<h1 class="ch pb" id="%s">%s</h1>' % (tid, esc(txt)))
def back(): O.append('<a class="back" href="#contents">BACK TO CONTENTS</a>')
def h2(segs): O.append('<h2>%s</h2>' % runs_html(segs if isinstance(segs, list) else [('b', segs)]))
def h3(txt): O.append('<h3 class="gold">%s</h3>' % esc(txt))
def p(segs): O.append('<p>%s</p>' % runs_html(segs))
def bul(segs): O.append('<ul class="bullets"><li>%s</li></ul>' % runs_html(segs))
def code(lines): O.append('<pre class="code">%s</pre>' % '\n'.join(esc(l) for l in lines))
def table(headers, rows, widths=None):
    s = ['<table><colgroup>']
    n = len(headers)
    ws = widths or [100.0/n]*n
    for w in ws: s.append('<col style="width:%.2f%%"/>' % w)
    s.append('</colgroup><thead><tr>')
    for hcell in headers: s.append('<th>%s</th>' % esc(hcell))
    s.append('</tr></thead><tbody>')
    for r in rows:
        s.append('<tr>')
        for c in r: s.append('<td>%s</td>' % cell_html([c]))
        s.append('</tr>')
    s.append('</tbody></table>')
    O.append(''.join(s))
def hr(): O.append('<hr/>')

T = lambda t: ('t', t)
C = lambda t: ('c', t)
B = lambda t: ('b', t)
L = lambda *segs: list(segs)

# ================= front matter =================
cover()
O.append('<div class="pb"></div>')
p([T('Volume I collected the 19 → 20 replacements used most often in custom modules: the ') , C('ir.access.csv'), T(' security file, ORM and Python renames, search domains, binary and report handling, view and QWeb xpaths, Owl 3, and the accounting, stock, HR and website mappings. This companion volume deliberately does not repeat them.')])
p([T('Volume II covers the ground Volume I leaves open: the new Python floor and package layout, the moved import surface (') , C('odoo.osv'), T(', '), C('odoo.tools'), T(' re-exports), caching and query objects, the access-check and recursion APIs, the '), C('read_group'), T(' signature overhaul, field and domain breaking changes, and the rewritten testing toolkit.')])
h2('Method')
bul([T('Every entry was verified on 2026-10-11 by comparing the '), C('odoo/odoo'), T(' branches '), C('19.0'), T(' and '), C('20.0'), T(' file by file (release.py, orm package, tools, tests, base and mail models). The verification log is in Appendix A.')])
bul([T('Entries hold for Community and Enterprise alike unless marked '), B('EE'), T('. Enterprise-only modules are out of scope for this volume.')])
bul([T('Code samples are signatures or minimal patterns copied from the 20.0 tree, not full implementations.')])
h2('How to read the tables')
p([T('Left column: what your 19 module contains today. Right column: what 20 accepts. A '), C('monospace chip'), T(' marks code; bold marks keywords.')])

O.append('<h1 class="toc-title pb" id="contents" style="font-size:25.5pt">Contents</h1>')
p([T('Select a chapter to open it.')])
for num, name in [(1, 'Runtime, packaging, and the import surface'),
                  (2, 'Caching, queries, and SQL objects'),
                  (3, 'Model and access API deltas'),
                  (4, 'Fields and domains: breaking changes'),
                  (5, 'Testing and CI toolkit'),
                  (6, 'Grep-driven migration checklist'),
                  (7, 'Automated codemods: odoo-bin upgrade_code'),
                  (8, 'Appendix A — verification log')]:
    O.append('<a class="toc-entry" href="#ch-%d"><span class="tocnum">%d.</span>%s</a>' % (num, num, esc(name)))

# ================= ch 1 =================
h1('ch-1', '1. Runtime, packaging, and the import surface')
back()
h2('Python floor moves to 3.12')
p([T('Odoo 19 runs on Python ≥ 3.10; Odoo 20 raises the floor to '), B('Python ≥ 3.12'), T(' ('), C('odoo/release.py'), T(', '), C('MIN_PY_VERSION'), T('). Core code now uses PEP 695 generic syntax, which only 3.12+ parses:')])
code(['# odoo/addons/base/models/ir_config_parameter.py — 20.0',
      'def get_int[T](self, key: str, default: T = 0) -> int | T:',
      '    ...'])
bul([T('Upgrade CI images, Dockerfiles and '), C('python_requires'), T(' of your addons before attempting the registry upgrade.')])
bul([T('3.12 also removes '), C('distutils'), T(' and tightens '), C('ast'), T('/'), C('inspect'), T(' behaviour; audit legacy setup scripts.')])
h2('Package layout')
table(['Odoo 19', 'Odoo 20'], [
 [L(C('odoo/http.py'), T(' (single module)')), L(C('odoo/http/'), T(' (package). '), C('import odoo.http'), T(' and '), C('from odoo import http'), T(' keep working.'))],
 [L(C('odoo/osv/'), T(' with '), C('expression.py')), L(T('Removed. Domains live in '), C('odoo/orm/domains.py'), T(' (Chapter 4).'))],
 [L(C('odoo/models'), T(', '), C('odoo/fields'), T(', '), C('odoo/api'), T(' shim packages')), L(T('Unchanged shims re-exporting '), C('odoo.orm.*'), T('. '), C('from odoo import models, fields, api'), T(' stays canonical in both versions.'))],
 [L(C('odoo/orm/'), T(' core (models, fields, domains, …)')), L(T('Same package plus new modules '), C('cache.py'), T(', '), C('models_cached.py'), T(', '), C('query.py'), T('.'))],
], widths=[42, 58])
h2('The odoo.tools export surface')
p([T('Several names disappeared from '), C('odoo/tools/__init__.py'), T(' in 20, and binary/SQL names became public:')])
table(['Name in 19 (from odoo.tools)', 'Status in 20'], [
 [L(C('Query')), L(T('No longer exported. Import '), C('from odoo.orm.query import Query'), T('.'))],
 [L(C('ormcache')), L(T('No longer exported from tools. Use '), C('@api.ormcache'), T(' (Chapter 2).'))],
 [L(C('ormcache_context')), L(T('Removed with no replacement.'))],
 [L(C('convert_xml_import'), T(' / '), C('convert_csv_import'), T(' / '), C('convert_sql_import')), L(T('No longer exported; see internals of '), C('odoo/tools/convert.py'), T('.'))],
 [L(T('—')), L(T('Newly public: '), C('SQL'), T(', '), C('BinaryValue'), T(', '), C('BinaryBytes'), T(', '), C('drop_view_if_exists'), T('. The binary classes are defined in '), C('odoo/tools/binary.py'), T(' and were private in 19.'))],
], widths=[42, 58])
code(['# 19',
      'from odoo.tools import Query, ormcache',
      'from odoo.tools.binary import BinaryValue      # private path',
      '',
      '# 20',
      'from odoo import api',
      'from odoo.orm.query import Query',
      'from odoo.tools import BinaryValue, BinaryBytes, SQL'])

# ================= ch 2 =================
h1('ch-2', '2. Caching, queries, and SQL objects')
back()
h2('ormcache moves to the api module')
p([T('The decorator class lives in '), C('odoo/orm/cache.py'), T(' in 20 (it was in '), C('odoo/tools/cache.py'), T(' in 19) and is re-exported through '), C('odoo.api'), T(':')])
code(['# 19',
      'from odoo.tools import ormcache, ormcache_context',
      '',
      'class MyModel(models.Model):',
      '    @ormcache(\'name\')',
      '    def _get_id_by_name(self, name): ...',
      '',
      '# 20',
      'from odoo import api',
      '',
      'class MyModel(models.Model):',
      "    @api.ormcache('name')            # or: @api.ormcache(cache='stable')",
      '    def _get_id_by_name(self, name): ...'])
bul([C('ormcache_context'), T(' is gone. Fold the context values you cached on into explicit method arguments so they become part of the cache key.')])
bul([T('Cache introspection moved with it: '), C('odoo.orm.cache.get_cache_size'), T(', '), C('get_cache_key_counter'), T(', '), C('log_ormcache_stats'), T('.')])
bul([T('Invalidation also changed name: the '), C('registry.clear_cache()'), T(' calls scattered in 19 code become '), C('self.env.transaction.invalidate_ormcache()'), T(' in 20 — exactly what the bundled codemod '), C('19.4-00-ormcache-on-transaction'), T(' rewrites (Chapter 7).')])
h2('Query and SQL')
p([C('Query'), T(' (the ORM query builder) is defined in '), C('odoo/orm/query.py'), T(' in 20; in 19 it reached you through the '), C('odoo.tools'), T(' re-export. The '), C('SQL'), T(' composable class is unchanged in '), C('odoo/tools/sql.py'), T(' and is now a public '), C('odoo.tools'), T(' export.')])
code(['# odoo/sql_db.py — 20.0',
      'def execute(self, query: SQL | typing.LiteralString | psql.Composable,',
      '            params=None, log_exceptions: bool = True) -> None:',
      '    if isinstance(query, SQL):',
      '        assert params is None, "Unexpected parameters for SQL query object"'])
bul([T('Plain string queries still execute ('), C('LiteralString'), T('), but pairing an '), C('SQL'), T(' object with '), C('params'), T(' is now an assertion error — build parameters into the '), C('SQL'), T(' composable.')])

# ================= ch 3 =================
h1('ch-3', '3. Model and access API deltas')
back()
p([T('Signatures below were read from '), C('odoo/orm/models.py'), T(' on both branches. Volume I covers '), C('check_access_rights'), T(' → '), C('check_access'), T('/'), C('has_access'), T('; the remaining renames are listed here.')])
table(['Odoo 19', 'Odoo 20'], [
 [L(C('check_access_rule(operation)')), L(T('Removed. Record rules are enforced inside '), C('check_access(operation)'), T(' / '), C('has_access(operation)'), T('.'))],
 [L(C('_filter_access_rules(op)'), T(' / '), C('_filter_access_rules_python(op)')), L(T('Internal successor '), C('_access_domain(op)'), T(' returns the rule domain; the Python-side filter method is gone. Treat both as private.'))],
 [L(C('check_field_access_rights(fields, operation, ...)')), L(C('check_field_access(field, operation)'), T(' and '), C('has_field_access(field, operation)'), T(' — per-field checks with '), C("Literal['read','write']"), T('.'))],
 [L(C('toggle_active()')), L(T('Removed with the '), C('toggle_active'), T(' window action; call '), C('action_archive'), T(' / '), C('action_unarchive'), T(' (Volume I, Ch. 2).'))],
 [L(C('_check_recursion()'), T(' / '), C('_check_m2m_recursion(field)')), L(C('_has_cycle(field_name=None)'), T(' — already present in 19, so adopt it before migrating.'))],
 [L(C('copy_translations(records)')), L(T('Removed; translation copy is handled internally, no public replacement.'))],
 [L(C('read_group(domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True)')), L(C('read_group(domain, groupby=(), aggregates=(), having=(), offset=0, limit=None, order=None)'), T(' returning '), C('list[tuple]'), T('.'))],
], widths=[44, 56])
h3('READ_GROUP BEFORE AND AFTER')
code(['# 19 — lazy dict-based API',
      "groups = env['sale.order'].read_group(",
      "    domain, ['amount_total'], ['state'], lazy=False)",
      '',
      '# 20 — explicit groupby + aggregate specs, tuples back',
      'rows = env[\'sale.order\'].read_group(',
      "    domain,",
      "    groupby=['state'],",
      "    aggregates=['amount_total:sum', '__count'])",
      'for state, total, count in rows: ...'])
bul([T('Aggregate specs use the '), C('field:agg'), T(' syntax ('), C('sum'), T(', '), C('avg'), T(', '), C('min'), T(', '), C('max'), T(', '), C('array_agg'), T(', …); '), C('__count'), T(' replaces the old '), C('state_count'), T(' key.')])
bul([T('The '), C('having'), T(' parameter accepts a domain on aggregated values — new in the public API.')])

# ================= ch 4 =================
h1('ch-4', '4. Fields and domains: breaking changes')
back()
h2('group_operator is gone — use aggregator')
p([T('19 still accepts '), C('group_operator'), T(' but warns '), I if False else B('“Since Odoo 18, \'group_operator\' is deprecated, use \'aggregator\' instead”'), T('. In 20 the keyword no longer exists:')])
code(['# 19 (DeprecationWarning)          # 20',
      'total = fields.Monetary(          total = fields.Monetary(',
      '    group_operator=\'sum\')             aggregator=\'sum\')'])
h2('Raw SQL in domain leaves now raises')
p([T('Passing an '), C('SQL'), T(' object as a domain leaf value warns in 19 ('), C('“Since 19.0, use Domain.custom(to_sql=…)”'), T(') and raises '), C('TypeError'), T(' in 20 ('), C('“Unexpected SQL in condition …, use Domain.custom() instead”'), T('):')])
code(['# 20 — odoo/orm/fields.py docstring pattern',
      'domain = Domain.custom(',
      '    to_sql=lambda table: SQL(',
      '        "(%s IS NULL OR %s = %s)",',
      '        table.company_id, table.company_id, company_id))'])
h2('odoo.osv.expression → odoo.orm.domains')
table(['Odoo 19 (odoo.osv.expression)', 'Odoo 20 (odoo.orm.domains / Domain)'], [
 [L(C('from odoo.osv import expression')), L(T('Import error — the '), C('odoo/osv'), T(' package is removed. Use '), C('from odoo.orm.domains import Domain'), T('.'))],
 [L(C('expression.AND(ds)'), T(' / '), C('expression.OR(ds)')), L(C('Domain.AND(ds)'), T(' / '), C('Domain.OR(ds)'), T(', or the '), C('&'), T(' / '), C('|'), T(' operators.'))],
 [L(C('expression.is_false(model, domain)')), L(C('Domain(d).is_false()'), T(' / '), C('.is_true()'), T(', plus '), C('Domain.TRUE'), T(' / '), C('Domain.FALSE'), T('.'))],
 [L(C('expression.normalize_domain(d)')), L(T('Internal: '), C('Domain'), T(' objects normalize on construction.'))],
 [L(C('expression.combine(op, unit, zero, ds)')), L(T('Use Python operators on '), C('Domain'), T(' instances.'))],
 [L(C('expression.distribute_not'), T(', '), C('prettify_domain')), L(T('Removed (were internal helpers).'))],
], widths=[44, 56])

# ================= ch 5 =================
h1('ch-5', '5. Testing and CI toolkit')
back()
h2('Registry test mode is a context manager')
code(['# 19',
      'self.registry_enter_test_mode()',
      'try:',
      '    ...',
      'finally:',
      '    self.registry_leave_test_mode()',
      '',
      '# 20',
      'with self.registry_test_mode():',
      '    ...'])
h2('Query assertions')
bul([C('assertQueriesContain'), T(' is removed; '), C('assertQueries'), T(' and '), C('assertQueryCount'), T(' remain.')])
bul([T('New matcher '), C('QueryLike'), T(' joins the family '), C('Like'), T(' / '), C('WhitespaceInsensitive'), T(' / '), C('Approx'), T(' for parameterized or reformatted SQL expectations.')])
h2('MockHTTPClient — new in 20')
p([T('A composable context manager that patches '), C('requests.sessions.Session.send'), T(':')])
code(['from odoo.tests.common import MockHTTPClient',
      '',
      "with MockHTTPClient('POST', 'https://api.example.com/v1/items',",
      '                    return_json={"id": 1}) as mock:',
      "    self.env['my.integration'].push_items()",
      'mock.assert_called_once()'])
bul([T('Matching: '), C('method'), T(', '), C('url'), T(' (host+path prefix, query optional), or a '), C('matcher(request)'), T(' predicate for headers/body.')])
bul([T('Responses from '), C('return_json'), T(' (sets '), C('application/json'), T(') or '), C('return_body'), T('; '), C('return_status'), T('/'), C('return_headers'), T(' accept callables. Mocks nest: unmatched requests fall through to the outer mock or real ') , C('requests'), T('.')])
bul([T('Call assertions: '), C('mock.assert_called(n_times)'), T(', '), C('assert_called_once()'), T(', '), C('assert_not_called()'), T('.')])
h2('HttpCase additions')
table(['Helper (20.0)', 'Purpose'], [
 [L(C('self.session')), L(T('Current '), C('Session'), T(' of the test browser (new; 19 had no accessor).'))],
 [L(C('update_session(**items)'), T(' / '), C('update_session_context(**items)')), L(T('Mutate and persist session values (and its context) between requests.'))],
 [L(C('csrf_token()')), L(T('Fetch a CSRF token for forged form posts.'))],
 [L(C('file_read(path)')), L(T('Classmethod returning file contents as '), C('BinaryBytes'), T(' — pairs with the binary API of Volume I Ch. 4.'))],
 [L(C('mock_datetime_and_now(dt)')), L(T('Patches '), C('datetime'), T(' helpers '), I if False else T('and'), T(' '), C('env.cr.now()'), T(' together, for sync-style tests.'))],
 [L(C('response.raise_for_status()')), L(T('Overridden to surface the Odoo error payload in the exception text.'))],
], widths=[40, 60])

# ================= ch 6 =================
h1('ch-6', '6. Grep-driven migration checklist')
back()
p([T('Run these greps over every custom addon; the right-hand side is the 20-clean replacement (volume reference where the topic is covered in depth).')])
table(['grep pattern', 'action in 20', 'see'], [
 [L(C('group_operator=')), L(T('Rename kwarg to '), C('aggregator=')), L(T('II.4'))],
 [L(C('check_access_rights(')), L(C('has_access('), T(' or '), C('check_access(')), L(T('I.2'))],
 [L(C('check_access_rule(')), L(C('check_access(')), L(T('II.3'))],
 [L(C('check_field_access_rights(')), L(C('has_field_access('), T(' / '), C('check_field_access(')), L(T('II.3'))],
 [L(C('toggle_active')), L(C('action_archive'), T(' / '), C('action_unarchive')), L(T('I.2'))],
 [L(C('_check_recursion(')), L(C('_has_cycle(')), L(T('II.3'))],
 [L(C('from odoo.osv import')), L(C('from odoo.orm.domains import Domain')), L(T('II.4'))],
 [L(C('tools import ormcache')), L(C('api.ormcache')), L(T('II.2'))],
 [L(C('ormcache_context')), L(T('Drop; explicit cache-key arguments')), L(T('II.2'))],
 [L(C('tools import Query')), L(C('odoo.orm.query import Query')), L(T('II.2'))],
 [L(C('convert_xml_import')), L(T('Internal only; reimplement via '), C('odoo.tools.convert'), T(' APIs')), L(T('II.1'))],
 [L(C('read_group('), T(' with '), C('lazy=')), L(T('New '), C('groupby/aggregates'), T(' signature')), L(T('II.3'))],
 [L(C("type='json'"), T(' route')), L(C("type='jsonrpc'")), L(T('I.5'))],
 [L(C('ir.model.access.csv')), L(C('ir.access.csv')), L(T('I.1'))],
 [L(C('assertQueriesContain')), L(C('assertQueries'), T(' + '), C('QueryLike')), L(T('II.5'))],
 [L(C('registry_enter_test_mode')), L(C('registry_test_mode()'), T(' context')), L(T('II.5'))],
 [L(C('copy_translations(')), L(T('Delete call; no replacement')), L(T('II.3'))],
 [L(C('pytz')), L(C('datetime.UTC'), T(' / '), C('zoneinfo')), L(T('I.2'))],
], widths=[34, 48, 18])


# ================= ch 7 upgrade_code =================
h1('ch-7', '7. Automated codemods: odoo-bin upgrade_code')
back()
p([T('Odoo ships a codemod repository at '), C('odoo/upgrade_code/'), T('. Each script is named '), C('{version}-{seq}-{name}.py'), T(' and exposes '), C('upgrade(file_manager)'), T('; the '), C('upgrade_code'), T(' CLI command (present in both 19 and 20, also runnable standalone) rewrites your addon sources in place — '), C('.py'), T(', '), C('.js'), T(', '), C('.css'), T(', '), C('.scss'), T(', '), C('.xml'), T(', '), C('.csv'), T(', '), C('.po'), T(', '), C('.pot'), T('.')])
h2('Running it')
code(['# all scripts for the 19 → 20 span, on your addons',
      'odoo-bin upgrade_code --from 19.0 --addons-path /path/to/addons',
      '',
      '# a single script (substring match is accepted)',
      'odoo-bin upgrade_code --script ir-access --addons-path /path/to/addons',
      '',
      '# standalone, without odoo-bin (resolved paths required)',
      'python3 odoo/cli/upgrade_code.py --from 19.0 --addons-path /path/to/addons'])
bul([C('--from'), T(' and '), C('--script'), T(' are mutually exclusive and one is required; '), C('--to'), T(' defaults to the running release and both bounds are inclusive — selection is by the version prefix of the script file name.')])
bul([C('--glob'), T(' narrows the file set; '), C('--dry-run'), T(' prints the '), C('updated:'), T(' / '), C('deleted:'), T(' list without writing. The command exits with code 1 when any file changed, which makes it usable as a CI gate.')])
bul([T('The docstring is explicit: scripts are best-effort helpers for the heavy lifting, '), B('not silver bullets'), T(' — review the diff in a git checkout before upgrading the registry.')])
h2('The script contract (write your own)')
code(['def upgrade(file_manager):',
      "    files = [f for f in file_manager if f.path.suffix == '.py']",
      '    for fileno, file in enumerate(files, start=1):',
      '        content = file.content            # lazy read',
      "        file.content = content.replace('old_api(', 'new_api(')",
      '        file_manager.print_progress(fileno, len(files))'])
bul([T('File objects expose '), C('path'), T(' (pathlib), '), C('addon'), T(' and a lazy '), C('content'), T(' property; assigning an unchanged value is a no-op, assigning '), C('None'), T(' deletes the file on save.')])
bul([T('The manager adds '), C('get_modules()'), T(', '), C('get_file(module, name)'), T(', '), C('add_to_summary(msg)'), T(' (printed at the end) and '), C('print_progress(current, total, file_name)'), T('.')])
bul([T('Custom scripts must live inside '), C('odoo/upgrade_code/'), T(' — '), C('--script'), T(' resolves candidates there and refuses paths outside it, so drop your team rewrites into that directory (or call '), C('migrate()'), T(' from Python).')])
h2('Scripts selected for a 19 → 20 run')
table(['Script', 'What it rewrites'], [
 [L(C('17.5-01-tree-to-list')), L(T('View mode '), C('tree'), T(' → '), C('list'), T(' in '), C('view_mode'), T('/binding fields and archs (the rename already landed in 19).'))],
 [L(C('18.1-00-sql-constraint')), L(C('_sql_constraints = [...]'), T(' → '), C('models.Constraint(...)'), T(' assignments (Volume I, Ch. 2).'))],
 [L(C('18.1-02-route-jsonrpc')), L(T('Route kwarg '), C("type='json'"), T(' → '), C("type='jsonrpc'"), T(' (Volume I, Ch. 5).'))],
 [L(C('18.2 / 18.3 l10n scripts')), L(T('Chart-template records and fiscal-position tax mappings ('), C('tax_src_id'), T('/'), C('tax_dest_id'), T(' → alternative-tax columns).'))],
 [L(C('18.5-00-domain-dynamic-dates')), L(T('Inlines unary-minus constants ('), C('-1'), T(') inside domains; '), C('18.5-00-no-tax-tag-invert'), T(' fixes tax '), C('formula'), T(' signs; '), C('18.5-00-deprecated-properties'), T(' cleans deprecated property fields.'))],
 [L(C('19.1-00-t-call')), L(T('Hoists '), C('t-set'), T(' nodes ahead of the '), C('t-call'), T('/'), C('t-snippet-call'), T(' that consumes them — Owl 3 evaluation order (Volume I, Ch. 9).'))],
 [L(C('19.3-00-account-groups')), L(C('account.group'), T(' CSV/data → '), C('account.account'), T(' hierarchy with a computed '), C('parent_id'), T(' column (Volume I, Ch. 10).'))],
 [L(C('19.3-00-account-report-foldable')), L(T('Normalizes the '), C('foldable'), T(' value of account report XML nodes to a boolean.'))],
 [L(C('19.3-00-base64-in-xml')), L(T('Migrates inline '), C('type="base64" … file='), T(' XML payloads to the 20 loading form.'))],
 [L(C('19.4-00-ir-access')), L(T('Merges '), C('ir.model.access.csv'), T(' plus '), C('<record model="ir.rule">'), T(' XML into '), C('security/ir.access.csv'), T(' with '), C('crud'), T(' operation strings and normalized domains (Volume I, Ch. 1).'))],
 [L(C('19.4-00-ormcache-on-transaction')), L(C('registry.clear_cache'), T(' → '), C('transaction.invalidate_ormcache'), T(' (this chapter’s sibling, Ch. 2).'))],
 [L(C('19.5-00-tuple-rec_names_search')), L(C("_rec_names_search = ['name']"), T(' → tuple form.'))],
 [L(C('20.0-00-search-date-filters')), L(T('Drops '), C('start_month'), T('/'), C('end_month'), T('-style range attributes from '), C('date'), T(' search filters — no longer parsed, rejected by the RNG.'))],
], widths=[34, 66])
bul([C('owl3-migration.py'), T(', '), C('tools_etree.py'), T(' and '), C('tools_js_expressions.py'), T(' carry no version prefix: they never enter a '), C('--from/--to'), T(' range. The first is the Owl 3 JavaScript migration to trigger explicitly with '), C('--script owl3-migration'), T('; the other two are helper libraries the scripts import ('), C('from odoo.upgrade_code.tools_etree import …'), T(').')])
h2('Suggested workflow')
bul([T('Run '), C('upgrade_code --from 19.0 --dry-run'), T(' first; then the real run on a clean git branch; review '), C('git diff'), T(' file by file.')])
bul([T('Commit the codemod result '), B('before'), T(' the registry upgrade ('), C('-u'), T('): the scripts fix source code, not database rows — data upgrades remain the job of each module’s '), C('pre/post'), T(' migration scripts.')])
bul([T('Re-run your test suite; the codemods cannot judge semantics (e.g. an '), C('ir.rule'), T(' domain that 20 validates differently, Volume I, Ch. 1).')])

# ================= ch 8 appendix =================
h1('ch-8', '8. Appendix A — verification log')
back()
p([T('Branches compared on 2026-10-11: '), C('odoo/odoo@19.0'), T(' and '), C('odoo/odoo@20.0'), T('.')])
bul([C('odoo/release.py'), T(' — '), C('MIN_PY_VERSION'), T(' (3,10) vs (3,12).')])
bul([C('odoo/'), T(' directory listings — '), C('osv'), T(' present in 19 only; '), C('http.py'), T(' → '), C('http/'), T('; '), C('orm/'), T(' gains '), C('cache.py'), T(', '), C('models_cached.py'), T(', '), C('query.py'), T('.')])
bul([C('odoo/tools/__init__.py'), T(' — export diff (Query, ormcache, convert_* removed; SQL, BinaryValue, BinaryBytes, drop_view_if_exists added).')])
bul([C('odoo/orm/models.py'), T(' — method-set diff (access checks, '), C('_has_cycle'), T(', '), C('read_group'), T(' signatures).')])
bul([C('odoo/orm/fields.py'), T(' — '), C('group_operator'), T(' warning in 19, absence in 20; '), C('Domain.custom'), T(' deprecation → '), C('TypeError'), T('.')])
bul([C('odoo/orm/domains.py'), T(' vs '), C('odoo/osv/expression.py'), T(' — helper mapping.')])
bul([C('odoo/tests/common.py'), T(' — test-mode context manager, '), C('MockHTTPClient'), T(', '), C('QueryLike'), T(', HttpCase session helpers.')])
bul([C('odoo/sql_db.py'), T(' — '), C('execute()'), T(' signature accepting '), C('SQL | LiteralString | Composable'), T('.')])
bul([C('odoo/cli/upgrade_code.py'), T(' and the '), C('odoo/upgrade_code/'), T(' script list on both branches — command flags, file-manager contract and per-script behaviour quoted in Chapter 7.')])
p([T('Enterprise-only deltas (payroll, budget, field service, helpdesk) are not verifiable from the public tree and are intentionally left to Volume I’s mapping tables and your Enterprise source review.')])

html_doc = '''<!DOCTYPE html><html><head><meta charset="utf-8"/>
<title>Odoo Migration Cookbook — Volume II: Closing the Gaps (19 → 20)</title>
<style>%s</style></head><body>
<div class="panel"></div>
%s
</body></html>''' % (css, '\n'.join(O))
open('work/book2.html', 'w').write(html_doc)
print('book2.html bytes:', len(html_doc))
