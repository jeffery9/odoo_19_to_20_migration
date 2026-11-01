# ORM & model API (17 → 18)

## 1. `name_get()` removed — CONFIRMED (deprecated 16.4 #122085, removed 18.0)

Any `def name_get` override must move to a computed `display_name` (or `_compute_display_name`).

```python
# 17                                   # 18
def name_get(self): ...               display_name = fields.Char(compute='_compute_display_name', store=True)
```

## 2. `_name_search` → `_search_display_name` — CONFIRMED (18.0 #174967)

```python
# 17                                            # 18
@api.model                                     @api.model
def _name_search(self, name, operator=...): ... def _search_display_name(self, operator, value): ...
```

## 3. Access-rights/rule methods merged — CONFIRMED (18.0 #179148)

| 17 | 18 | note |
|---|---|---|
| `self.check_access_rights(op)` | `self.check_access(op)` | combined rights+rules |
| `self.check_access_rule(op)` | `self.check_access(op)` | combined |
| `self._filter_access_rules(op)` | `self._filtered_access(op)` | returns permitted subset |
| `self._filter_access_rules_python(op)` | `self._filtered_access(op)` | combined |
| — | `self.has_access(op)` → `bool` | new convenience |
| `self.user_has_groups('x')` | `self.env.user.has_group('x')` | #151597, method removed |

> 18.0 `odoo/models.py`: `def`s for `check_access_rights` / `check_access_rule` /
> `user_has_groups` are gone; `check_access` / `_filtered_access` / `has_group` are called.

## 4. `check_recursion()` → `has_cycle()` — CONFIRMED (OCA 18.0 guide)

`self.check_recursion(parent='parent_id')` → `self.has_cycle(parent='parent_id')`.

## 5. `copy` / `copy_data` multi-record — CONFIRMED (18.0 #154132)

`copy_data` returns a **list** (one dict per record); `self` may be a multi-recordset.
Custom overrides must handle `self` as multi.

## 6. Field attribute `group_operator` → `aggregator` — CONFIRMED (17.2 #127353)

```python
allocated = fields.Float("Allocated %", group_operator='avg')   # 17
allocated = fields.Float("Allocated %", aggregator='avg')        # 18
```

Also: group/aggregate/sort by **non-stored related fields** now possible (needs `related_sudo`/`compute_sudo`).

## 7. `inselect` operator removed — CONFIRMED (17.4 #171371)

Use `in` with a `Query` / `SQL` object instead of the `inselect`/`not inselect` operators.

## 8. Translations via `env._()` — CONFIRMED (18.0 #174844)

Module-level `_("text")` → `self.env._("text")`. `self.env.translations` also available.

## 9. Search behavior changes — CONFIRMED

- Searching **non-stored related fields** now **raises** (was a warning). To modify search
  results, override `search_fetch` (not `search`, which is not always called).
- `_flush_search()` deprecated since 17.1 (#144747); flushing via `execute_query()`.

## 10. Optional modern APIs (adopt, not forced)

- `Domain` API: `from odoo import Domain` (18.1 #170009) — prefer `Domain.AND/OR`, `Domain.TRUE/FALSE`.
- Declarative constraints/indexes: `models.Constraint` / `models.Index` (18.1 #175783).
  `_sql_constraints` **still works** in 17→18; the codemod that auto-rewrites it (`18.1-00-sql-constraint`)
  ships in the **19.0** tree, not the 17→18 flow.
- `SQL(...)` wrapper (17.0 #134677) unchanged — keep using it; avoid f-string SQL.
