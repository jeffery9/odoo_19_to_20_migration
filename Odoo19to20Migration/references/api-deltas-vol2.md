# Volume-II API deltas (runtime, cache, model API, fields, tests)

## Runtime & imports

- Python floor: 19 ≥ 3.10 → **20 ≥ 3.12** (`odoo/release.py MIN_PY_VERSION`); core uses PEP 695 generics.
- `odoo/http.py` → `odoo/http/` package (imports unchanged); `odoo/osv/` **removed**;
  `odoo.models|fields|api` are shim packages in both versions → `from odoo import models, fields, api` stays canonical.
- `odoo.tools` export surface in 20: **removed** `Query`, `ormcache`, `ormcache_context`,
  `convert_xml_import/csv/sql`; **added** `SQL`, `BinaryValue`, `BinaryBytes`, `drop_view_if_exists`.
  Replacements: `from odoo.orm.query import Query`; `@api.ormcache`; converts are internal.

## Cache & SQL

- `from odoo.tools import ormcache` (19) → `@api.ormcache(...)` (20; class in `odoo/orm/cache.py`,
  optional `cache='stable'`); `ormcache_context` removed — fold context into explicit args.
- Introspection: `odoo.orm.cache.get_cache_size / get_cache_key_counter / log_ormcache_stats`.
- Invalidation: `registry.clear_cache()` → `self.env.transaction.invalidate_ormcache()`
  (codemod `19.4-00-ormcache-on-transaction`).
- `cr.execute` (20): `SQL | LiteralString | Composable`; `params` must be None with `SQL`.

## Model API deltas

| 19 | 20 |
|---|---|
| `check_access_rule(op)` | folded into `check_access(op)` / `has_access(op)` |
| `_filter_access_rules(op)` / `..._python(op)` | internal `_access_domain(op)`; python filter gone |
| `check_field_access_rights(...)` | `check_field_access(field, op)` / `has_field_access(field, op)` with `Literal['read','write']` |
| `toggle_active()` | removed → `action_archive`/`action_unarchive` |
| `_check_recursion()` / `_check_m2m_recursion(f)` | `_has_cycle(field_name=None)` (exists in 19 — adopt early) |
| `copy_translations(records)` | removed, no public replacement |

## Fields & domains

- `group_operator=` removed (19 warned "Since Odoo 18…") → `aggregator=`.
- Domain leaf with raw SQL: 19 DeprecationWarning → 20 `TypeError` → `Domain.custom(to_sql=lambda table: SQL(...))`.
- `odoo.osv.expression` helpers → `Domain`: `AND/OR` → `Domain.AND/OR`; `is_false(m,d)` → `Domain(d).is_false()`;
  `normalize_domain` internal; `combine` → `&`/`|`; `distribute_not`/`prettify_domain` gone.

## Testing & CI

- `registry_enter_test_mode()/registry_leave_test_mode()` → `with self.registry_test_mode():`.
- `assertQueriesContain` removed; `assertQueries`/`assertQueryCount` remain; new matcher `QueryLike`
  (family: `Like`, `WhitespaceInsensitive`, `Approx`).
- **New** `MockHTTPClient` context manager (patches `requests.sessions.Session.send`, nestable):
  match by `method`/`url`/`matcher(request)`; responses via `return_json`/`return_body`,
  `return_status`/`return_headers`; assertions `assert_called(n)`, `assert_called_once()`, `assert_not_called()`.
- HttpCase additions: `self.session`, `update_session(**)`, `update_session_context(**)`, `csrf_token()`,
  `file_read(path) -> BinaryBytes`, `mock_datetime_and_now(dt)`, `response.raise_for_status()` with Odoo payload.

## Grep checklist (pattern → action, see=reference)

`group_operator=`→`aggregator=`(this file) · `check_access_rights(`→`has_access/check_access`(security-and-orm) ·
`check_access_rule(`→`check_access`(this file) · `toggle_active`→archive actions(security-and-orm) ·
`_check_recursion(`→`_has_cycle(`(this file) · `from odoo.osv import`→`odoo.orm.domains`(security-and-orm) ·
`tools import ormcache`→`api.ormcache`(this file) · `ormcache_context`→drop(this file) ·
`tools import Query`→`odoo.orm.query`(this file) · `read_group(…lazy=`→new signature(security-and-orm) ·
`type='json'` route→`jsonrpc`(binary-http-mail) · `ir.model.access.csv`→`ir.access.csv`(security-and-orm) ·
`assertQueriesContain`→`assertQueries`+`QueryLike`(this file) · `registry_enter_test_mode`→ctx(this file) ·
`copy_translations(`→delete(this file) · `pytz`→`datetime.UTC/zoneinfo`(security-and-orm) ·
`registry.clear_cache`→`env.transaction.invalidate_ormcache`(this file).
