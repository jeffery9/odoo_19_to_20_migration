# Views, QWeb & frontend (17 → 18)

## 1. View type `tree` → `list` — CONFIRMED (codemod `17.5-01-tree-to-list`, PR #159909, 18.0)

18.0 `ir.ui.view.type` selection only contains `list` (no `tree`). Any `<tree>` root tag
raises `ValueError: Wrong value for ir.ui.view.type: 'tree'`.

`odoo/upgrade_code/17.5-01-tree-to-list.py` (ships in the **18.0** tree) renames in
**XML / Python / JS** but skips XML-IDs containing `tree`. Three places to check after the
codemod (community reports `editable`/`create`/`default_order` sometimes land outside the
tag → malformed XML, eyeball the diff):

1. view definition `<tree>` → `<list>` (move `editable`/`create`/`default_order` onto `<list>`)
2. window action `view_mode` `tree,form` → `list,form`
3. inherited views XPath `//tree/...` → `//list/...`

## 2. `colors` attribute removed → `decoration-*` — CONFIRMED

`<tree colors="red:state=='draft'">` → `<list decoration-danger="state=='draft'">`.
Verified against 18.0 `odoo/addons/base/models/ir_ui_view.py`: it handles `decoration-*`
(`attr.startswith('decoration-')`) and has **no** `colors` handling branch.

## 3. `tree_view_ref` → `list_view_ref` — CONFIRMED (OCA 18.0 migration guide, PR #159909)

Context key selecting a specific list view ref.

## 4. Missing fields auto-added as invisible — CONFIRMED (18.0 #137031)

Fields referenced in expressions (`invisible` / `column_invisible` / `readonly` / `required`
/ `context` / `domain`) but not declared in the view are auto-added as invisible fields.
Legacy explicit `invisible="1"` fields can be cleaned up.

## 5. `kanban-box` → `card` — `[verify]` (version scope disputed)

OCA《Migration to version 18.0》lists "kanban-box is replaced by card definition" as an
18.0 change. The 18→19 cookbook (source-verified against 19.0) attributes `kanban-box`→`card`
to the Owl 3 kanban rewrite in 19.0. **Adopt `kanban-box`→`card` now if present in 17 code,
but verify against the 18.0 template** — if 18.0 still uses `kanban-box`, defer to 18→19.

## 6. `states` field attribute removed — `[verify]` (DeployMonkey)

`states="draft,open"` on fields removed; use `invisible`/`readonly` condition expressions.
Not in the 18.0 official changelog; single community source.

## 7. `fields_view_get()` → `get_views()` — `[verify]` (DeployMonkey)

Old `_fields_view_get` removed; use `get_views()`. Not in OCA 18.0 guide; single source.

## 8. Owl framework: still Owl 2 — CONFIRMED

**Odoo 18 keeps Owl 2**; `setup()` rewrite is a 19.0 (Owl 3) break. 17→18 frontend work is
the `tree`→`list` XML/JS rename, not a framework upgrade.
