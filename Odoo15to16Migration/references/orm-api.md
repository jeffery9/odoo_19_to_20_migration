# Reference: ORM & Python API (15 → 16)

Scope: **15.0 → 16.0 only.**

## `track_visibility` → `tracking`  [CONFIRMED (community: DeployMonkey + OCA 16 guide)]

`track_visibility` field attribute removed in 16.0 (deprecated in 14). Replace with `tracking`.

```python
# 15
name = fields.Char(track_visibility='always')
state = fields.Selection(track_visibility='onchange')
# 16
name = fields.Char(tracking=True)
state = fields.Selection(tracking=True)          # or tracking='field_name'
```

Scope note: `odoo/fields.py` (16.0) and `odoo/models.py` (16.0) contain no `track_visibility` /
`tracking` keyword (the mechanism lives in the `mail` mixin), but multiple migration guides
confirm `track_visibility` is unusable in 16.0 and `tracking` is the replacement. Treat as
CONFIRMED-from-community; the mechanism's home is the `mail` module.

## `api.multi` removed  [CONFIRMED — source: 16.0 `odoo/api.py` has no `api.multi`]

```python
# 15 (breaks on 16: ImportError: cannot import name 'multi' from 'odoo.api')
@api.multi
def action_do(self): ...
# 16
def action_do(self): ...          # methods are multi by default
```

Low-priority cleanup, but it blocks server start if present. Delete the decorator.

## Selection `group_expand`  [CONFIRMED — community: DeployMonkey]

New in 16.0 (additive, not breaking). Fixes kanban grouping that "loses" missing options:

```python
state = fields.Selection([...], group_expand='_expand_states')
def _expand_states(self, states, domain, order): ...
```

## `[verify]` `@http.route(website=True, ...)` — website module restructured

DeployMonkey: website module restructured in 16.0; controllers using `website=True` need review.
Verify routing against your 16.0 `website` bundle before assuming breakage. Source: single
community guide, not source-verified → `[verify]`.

## Red line — APIs still present in 16 (do NOT change here)

Verified in 16.0 source: `name_get` (models.py L1574), `_name_search` (L1651),
`user_has_groups` (L1472), `check_access_rights` (L3523), `get_resource_path` (modules/module.py L280),
`attrs`/`states` (ir_ui_view.py L82-96), `<tree>` (ir_ui_view.py L237). Their removal/rename belongs
to 16→17 / 17→18 — handled by those skills.
