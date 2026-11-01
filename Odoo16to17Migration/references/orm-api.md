# 16→17 ORM & Python API mapping

Source-verified against Odoo 17.0. Red line: do NOT migrate check_access_rights /
user_has_groups / check_recursion / _name_search / inselect / group_operator /
type='json' here — those are 17→18 (or 17.x) and still valid in 17.0.

## name_get deprecated (still works, warns) — CONFIRMED (PR #122085)

Deprecated since 16.4, removed in 18.0. Migrate during 16→17 to avoid the
DeprecationWarning snowball.

```python
# 16
def name_get(self):
    return [(r.id, f"{r.code} - {r.name}") for r in self]
# 17
display_name = fields.Char(compute='_compute_display_name', store=True)
@api.depends('code', 'name')
def _compute_display_name(self):
    for r in self:
        r.display_name = f"{r.code} - {r.name}"
```

## Hook signatures (cr, registry) → env — CONFIRMED (PR b4a7996)

`pre_init_hook` / `post_init_hook` / `uninstall_hook` now receive `env`.

```python
# 16
def post_init_hook(cr, registry): ...
def uninstall_hook(cr, registry): ...
# 17
def post_init_hook(env): ...
def uninstall_hook(env): ...
```

Replace `cr`→`env.cr`, `registry`→`env.registry` inside.

## get_resource_path removed → file_path — CONFIRMED (tools/misc.py 17.0)

`get_resource_path` is NOT defined in 17.0 `odoo/tools/misc.py`; `file_path`
is (`file_path(file_path, filter_ext=('',), env=None)`). New arg syntax: single
slash-joined path string.

```python
# 16
from odoo.modules.module import get_resource_path
p = get_resource_path('my_mod', 'data', 't.xml')
# 17
from odoo.tools import file_path
p = file_path('my_mod/data/t.xml')
```

## APIs that are UNCHANGED in 17.0 (do not touch)

- `check_access_rights` / `check_access_rule` / `user_has_groups` / `check_recursion`
  — still present; removal is 17→18.
- `_name_search` — still present; removal is 17→18.
- `inselect` domain operator — still present; removed 17.4/18.
- field `group_operator` — still named `group_operator` in 17.0 (renamed
  `aggregator` in 17.2, out of 16→17 scope).
- `@http.route(type='json')` — still `type='json'` in 17.0 (renamed `jsonrpc`
  in 18.1, out of 16→17 scope).
- `mail.channel` — still `mail.channel` in 17.0 (renamed `discuss.channel`
  only in 18.0).
