# Security & ORM (18 → 19)

## 1. Security: `ir.model.access.csv` is UNCHANGED in 18→19

Unlike the 19→20 step, **the access-file format does not change** between 18 and
19. Both use `security/ir.model.access.csv` with the `perm_*` columns:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_lock,my.lock,model_my_lock,base.group_user,1,1,1,0
```

Do **not** apply the 19→20 `ir.access.csv` / `operation` conversion here — that
is a 20.0-only change. The `odoo-bin upgrade_code --script ir-access` codemod is
therefore **not** relevant to 18→19.

## 2. `res.groups` redesign (privilege model) — CONFIRMED

Odoo 19 replaces group *categories* with *privileges*. Corroborated by multiple
independent sources (Cybrosys, SDLC Corp, ERP Consulting 24) and a real 19.0
module `eh_hr_compat` which hard-codes the 16–18→19 field flips:

| Odoo 18 | Odoo 19 | Note |
|---|---|---|
| `res.groups.category_id` | `res.groups.privilege_id` (new model `res.groups.privilege`) | `category_id` removed in 19 |
| `res.groups.groups_id` | `res.groups.group_ids` | implied-groups relation renamed |
| `res.groups.users` | `res.groups.user_ids` | member relation renamed (inverse of user-side) |
| `res.users.groups_id` | `res.users.group_ids` | user-side groups relation renamed |

Rules:
- Custom `res.groups` XML must still load before any `ir.model.access.csv` referencing them.
- Record-rule `groups=` attribute validates against existing group XML-IDs at install
  (sources agree this is stricter in 19) — a dangling `groups="x.group_y"` raises at install.

## 3. SQL constraints → model attributes — CONFIRMED (codemod `18.1-00-sql-constraint`)

`_sql_constraints` is replaced by declarative model attributes
(codemod `18.1-00-sql-constraint` performs the rewrite; old format is deprecated):

```python
# 18
_sql_constraints = [('name_unique', 'UNIQUE(name)', 'Name must be unique.')]
# 19
_name_unique = models.Constraint('UNIQUE(name)', 'Name must be unique.')
_name_idx    = models.Index('idx_my_model_name', 'name')
```

(Corroborated by Cybrosys, DeployMonkey, LineScripts "Constraint / Index / UniqueIndex
table objects to replace _sql_constraints".)

## 4. ORM & Python renames (CE+EE unless noted)

| Odoo 18 | Odoo 19 | Source / note |
|---|---|---|
| `from odoo.api import Meta, Params, propagate` (internal) | **removed** — use public `from odoo import api, fields, models` | LineScripts; ORM split into `odoo/orm/` package (public re-exports stay safe) |
| `from odoo import registry` | `from odoo.modules.registry import Registry` | SDLC Corp / Cybrosys |
| `from odoo.conf import ...` / `odoo/conf/` package | **removed** — use `odoo.tools.config` | LineScripts — **verified**: `odoo/conf` absent in 19.0 (ORM split to `odoo/orm/`) |
| `get_module_resource(...)` | **removed** — use `odoo.modules.get_resource_from_path` (exported from `odoo.modules`) or `pathlib` | LineScripts (`pathlib`); Cybrosys (`get_resource_from_path`) — **verified**: `get_resource_from_path` is exported from `odoo.modules` in 19.0 |
| `@api.returns` | **removed** — delete the decorator | LineScripts (had no effect in 18 either); Cybrosys |
| `self._cr` | `self.env.cr` | deprecated in 19 (#193636), emits `DeprecationWarning` |
| `self._uid` | `self.env.uid` | deprecated in 19 (#193636) |
| `self._context` | `self.env.context` | deprecated in 19 (#193636) |
| `self.read_group(...)` | `self._read_group(...)` | deprecated since 18.2 (#163300); arg `fields`→`aggregates` |
| `self.toggle_active()` | `self.action_archive()` / `self.action_unarchive()` | LineScripts |
| `self.check_field_access_rights(...)` | `self._has_field_access(field, mode)` | LineScripts — **corrected**: 19.0 `orm/models.py` calls `_has_field_access(field, mode)`; the claimed `_check_field_access` does NOT exist |
| `self._apply_ir_rules(query)` | `self._search(domain, bypass_access=True)` | Cybrosys / ERP Consulting 24 — `_apply_ir_rules` removed |
| `from odoo.osv import expression` | `from odoo import Domain` / `Domain.OR` | `odoo.osv` deprecated in 19 (#217708); Cybrosys |

```python
# 18
query = self._where_calc(domain)
self._apply_ir_rules(query)
# 19
query = self._search(domain, bypass_access=True)
```

- `@api.model_create_multi` is the expected decorator for `create()` (it normalizes a
  single dict into a list). Source review of `odoo/orm/decorators.py` shows **no hard
  warning** when `create` is called undecorated — the "mandatory / DeprecationWarning"
  claim is **unconfirmed**. Keep `@api.model_create_multi` where present. `[verify]`
- `check_access` / `has_access` / `_filtered_access` exist since 18.0 (#179148);
  prefer them over `check_access_rights` going forward (the latter still works in
  18→19 but is on the deprecation path).

## 5. Search & domains

- `Domain` API (`from odoo import Domain`) available since 18.1 (#170009):
  prefer `Domain.AND/OR`, `Domain.TRUE`/`Domain.FALSE`.
- Equality normalization (18.3, #191549): `=` is equivalent to `in`.
- `read_group` → `_read_group` with `aggregates=` (see §4); old `read_group` warns.
- `group_operator` was renamed to `aggregator` in **17.2** (#127353) — already in 18,
  **not** a 18→19 change; do not re-touch it here.
- `search()` with an invalid domain operator raises `ValueError` (stricter than 18).
