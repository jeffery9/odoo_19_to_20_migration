# Security & ORM (19 → 20)

## 1. The security file: `ir.model.access.csv` + `ir.rule` XML → `security/ir.access.csv`
Odoo 20 loads **only** `ir.access.csv`. `ir.model.access.csv` is ignored and
`<record model="ir.rule">` in XML raises `KeyError: 'ir.rule'`.

19 (`security/ir.model.access.csv`):
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_lock,lock,model_my_lock,base.group_user,1,1,1,0
```
20 (`security/ir.access.csv`):
```csv
id,name,model_id,group_id/id,operation,domain
access_my_lock,my.lock,my.lock,base.group_user,cru,
```

| Column | Odoo 20 meaning |
|---|---|
| `model_id` | technical model name (`sale.order`), not `module.model_x` |
| `group_id/id` | group XML id; empty = global rule |
| `operation` | `crud`, `cru`, `cr`, … — never `rc`, never `perm_*` columns |
| `domain` | record-rule domain, or empty |

Further rules on this file:
- 19 `model_id/id` → 20 `model_id` (technical name, no module prefix).
- Domains `[(1,'=',1)]` / `[('1','=','1')]` fail validation → use empty domain.
- Domain on a non-stored field raises *Field has no SQL representation* → use stored field/path.
- Company domain `('company_id','in',company_ids+[False])` fails →
  `['|',('company_id','=',False),('company_id','in',company_ids)]`.
- Custom `res.groups` XML must be listed in the manifest **before** `ir.access.csv`.
- Codemod: `odoo-bin upgrade_code --script ir-access` performs this merge
  (incl. `ref()` refs, true/false domains, exclusive groups).

## 2. ORM & Python renames (CE+EE unless noted)

| Odoo 19 | Odoo 20 |
|---|---|
| `_sql_constraints = [('name','sql','msg')]` | `_name = models.Constraint('sql','msg')` (attr name = constraint name) |
| `self.fields_view_get(...)` | `self._get_view(...)` |
| `self.check_access_rights('read')` | `self.check_access('read')` (raises) / `self.has_access('read')` (bool) |
| `self.check_access_rights('read', raise_exception=False)` | `self.has_access('read')` (bool) |
| `self.user_has_groups('x.group_y')` | `self.env.user.has_groups('x.group_y')` |
| `self._context` | `self.env.context` |
| `self.env.user.company_id` | `self.env.company` |
| `ir.config_parameter.get_param/set_param` | typed: `get_int/get_str/get_bool/get_float`, `set_int/set_str/set_bool/set_float` |
| `pytz` | `datetime.UTC` and `zoneinfo` |
| window action `toggle_active` | `action_archive` / `action_unarchive` |
| `write(archive=True)` | `write(active=False)` |
| `mail.thread.cc` | `mail.thread` |

Constraint example (20):
```python
_code_uniq = models.Constraint(
    'unique(code, company_id)',
    'Code must be unique per company.',
)
```

## 3. Search & domains
- `_name_search` → `_rec_names_search` (tuple in 20, codemod `19.5`) and/or `_search_display_name`.
- `from odoo.osv import expression` → **import error**; use `from odoo.orm.domains import Domain`.
- `expression.AND/OR` → `Domain.AND/OR` (or `&`/`|`); `expression.is_false(m,d)` → `Domain(d).is_false()`;
  `TRUE/FALSE` → `Domain.TRUE` / `Domain.FALSE` (`FALSE_DOMAIN` → `Domain.FALSE`).
- `_search_display_name` signature: `(self, name, domain=None, operator='ilike', limit=None, order=None)`.
- `_read_group_stage_ids(self, stages, domain, order)` → drop `order`.
- View modifiers `in 'x'`/`not in 'x'` → `== 'x'`/`!= 'x'` (tuple membership `('a','b')` stays valid).
- Raw `SQL` object as domain leaf: 19 warns, 20 raises `TypeError` → `Domain.custom(to_sql=lambda table: SQL(...))`.
- `read_group`: 19 `(domain, fields, groupby, offset, limit, orderby, lazy)` →
  20 `(domain, groupby=(), aggregates=(), having=(), offset=0, limit=None, order=None) -> list[tuple]`;
  aggregates use `field:agg` specs plus `__count`.
