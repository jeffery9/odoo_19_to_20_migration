# API Deltas (18 → 19) — runtime, imports, cache/SQL, model API, fields, tests

## 1. Runtime & imports

| Odoo 18 | Odoo 19 | Note |
|---|---|---|
| monolithic `odoo/api.py`, `odoo/models.py`, `odoo/fields.py` | split into `odoo/orm/` **package** | public `from odoo import api, fields, models` re-exported & safe; internal imports gone |
| `from odoo.api import Meta, Params, propagate` | **removed** | reach-into-framework imports |
| `from odoo import registry` | `from odoo.modules.registry import Registry` | SDLC / Cybrosys |
| `odoo/conf/` package | **removed** | use `odoo.tools.config` — **verified** (`odoo/conf` absent in 19.0) |
| `get_module_resource(...)` | **removed** | use `get_resource_from_path` (from `odoo.modules`) or `pathlib` — **verified** (`get_resource_from_path` exported from `odoo.modules`) |
| `from odoo.osv import expression` | **deprecated** (#217708) | use `from odoo import Domain` |
| `from odoo.tools.misc import xlsxwriter` | `import xlsxwriter` | Cybrosys (simplified import) |

## 2. Cache & SQL

- The `SQL(...)` wrapper object (since 17.0, #134677) is unchanged in 18→19.
  Compose SQL with `SQL()`, never f-strings, to avoid injection.
- `_flush_search()` deprecated since 17.1 (#144747) — already the case in 18;
  flushing is done by `execute_query()`. Confirm any override of `_flush_search` is removed.
- Raw `SQL` object used as a domain leaf: 18 tolerated it; 19 is stricter. Prefer
  `Domain.custom(to_sql=lambda table: SQL(...))` (the `Domain.custom` helper landed
  in 19→20 — in 18→19, build the domain explicitly). `[verify]`

## 3. Model API

| Odoo 18 | Odoo 19 | Note |
|---|---|---|
| `create()` single-record | `@api.model_create_multi` expected | no hard warning on undecorated `create` found in source (`odoo/orm/decorators.py`) — `[verify]` |
| `unlink()` | cascade validation stricter | orphaned related records detected |
| `self._cr/_uid/_context` | `self.env.cr/uid/context` | deprecated (#193636) |
| `read_group(...)` | `_read_group(aggregates=...)` | deprecated since 18.2 (#163300) |
| `toggle_active()` | `action_archive()` / `action_unarchive()` | LineScripts |
| `check_field_access_rights(...)` | `_has_field_access(field, mode)` | **corrected**: 19.0 uses `_has_field_access`, not `_check_field_access` (verified) |
| `check_access_rights` / `check_access_rules` | `check_access` / `has_access` / `_filtered_access` | available since 18.0 (#179148) |
| `self._apply_ir_rules(query)` | `self._search(domain, bypass_access=True)` | Cybrosys / ERP24 — `_apply_ir_rules` removed |
| `search()` invalid domain op | raises `ValueError` | was silently ignored in 18 |
| `name_get()` | read `display_name` | deprecated since 16.4 (already in 18) |

## 4. Fields & domains

- `precompute` defaults to **False** (NOT True) for computed fields — `odoo/orm/fields.py`
  declares `precompute: bool = False`. A computed field is precomputed only when you set
  `precompute=True` explicitly. **Corrected**: the "default True" claim is false. Review
  compute methods that assumed eager precompute. (Verified in 19.0 source.)
- `compute_sudo` defaults to the field's `store` value: `False` for non-stored computed
  fields, `True` for stored computed fields and related fields (`attrs['compute_sudo'] =
  attrs.get('compute_sudo', store)` in `odoo/orm/fields.py`). **Corrected**: it is NOT
  unconditionally `True`. (Verified in 19.0 source.)
- Related fields with `store=True`: improved cache invalidation may surface hidden bugs.
- `currency_field` parameter now validates that the referenced field exists.
- `group_operator` → `aggregator`: renamed in **17.2** (#127353) — already in 18,
  **not** a 18→19 change; do not re-touch it here.
- `Domain` API (`from odoo import Domain`) available since 18.1 (#170009):
  prefer `Domain.AND/OR`, `Domain.TRUE/FALSE` over `expression.*`.
- `fields.Property` is **not** a field class in 19.0 — in `odoo/orm/fields_properties.py`
  `Property` is an `abc.Mapping` value-wrapper for `Properties` fields, and `fields.Properties`
  (the field) is **not** deprecated. The `18.5-00-deprecated-properties` codemod targets
  legacy `company_dependent`/`property` usage, not a `fields.Property` class.
  **Corrected**: the "fields.Property deprecated" claim is inaccurate. `[verify]` (confirm
  exact codemod scope against 19.0 tree.)

## 5. Authentication API — CONFIRMED

| Odoo 18 | Odoo 19 |
|---|---|
| `authenticate(request.session.db, creds)` | `authenticate(request.env, creds)` |

(Cybrosys / ERP Consulting 24.) Affects custom auth/controlller code, not normal RPC clients.

## 6. Tests & validation

- Stricter view validation at install: malformed XPath / missing `model` / bad
  `groups` XML-ID raise at install (see views-qweb-owl §2). Add a view-RNG check.
- Run the server with deprecation warnings visible (`--dev=all`) and clear **every**
  `DeprecationWarning` — they are 20.0 hard-breaks.
- `odoo-bin -u <module> --test-tags /<module>` in a 19.0 sandbox; fix domain
  `TypeError`s and view RNG errors last (loudest).
- No 18→19 change to the external JSON-2 / XML-RPC test contracts.

## 7. Grep checklist (pattern → action → see)

`from odoo.api import Meta`→remove (§1) · `from odoo import registry`→`odoo.modules.registry` (§1) ·
`get_module_resource(`→`pathlib`/`get_resource_from_path` (§1) · `@api.returns`→delete (§1) ·
`self._cr`/`self._uid`/`self._context`→`self.env.*` (§3) · `read_group(`→`_read_group(aggregates=)` (§3) ·
`toggle_active`→archive actions (§3) · `_apply_ir_rules(`→`_search(bypass_access=True)` (§3) ·
`from odoo.osv import`→`odoo import Domain` (§1) · `check_field_access_rights(`→`_has_field_access` (§3) ·
`_sql_constraints =`→`models.Constraint` (security-and-orm §3) · `type='json'` route→`jsonrpc` (binary-http-mail §1) ·
`authenticate(request.session.db`→`authenticate(request.env` (§5) · `res.groups.category_id`/`users`/`groups_id`→`privilege_id`/`user_ids`/`group_ids` (modules-mapping §4) ·
`res.partner.mobile`/`sale_line_warn`/`picking_warn`→removed (modules-mapping §4) ·
`uom.category`/`res.partner.title`→removed (modules-mapping §3) ·
`kanban-box`→`card` (views-qweb-owl §3) · `t-esc`→`t-out` (views-qweb-owl §2)
