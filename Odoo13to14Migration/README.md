# Odoo13to14Migration

This is the **13→14** member of the multi-version migration workspace
(see the root README for the full matrix). The 12→13 member lives in
`../Odoo12to13Migration/` and the 14→15 member in `../Odoo14to15Migration/`.

A reusable agent skill that migrates custom Odoo 13.0 addons to 14.0 (CE and EE)
using source-verified manual mappings. Companion cookbook:
`../Odoo_Migration_Cookbook_13_to_14.md`.

## What breaks in 13→14 (headline)

- **`ir.actions.*` direct access removed** — read action dicts via
  `_for_xml_id('module.action_id')`; operate records with `sudo()`; frontend via
  `/web/action/load`. (Different object from the 15.0 `ir.model*` removal.)
- **`invisible`/`readonly` dynamic expressions rejected** (`state=='draft'`) —
  move into `attrs` domain; only `context.get('...')` stays inline. `attrs` still
  valid in 14.0 (hard-rejected only in 16→17).
- **ORM**: `_name_search` returns ids (not tuples); `_compute_display_name`
  override dead → `name_get`; `force_company` → `with_company`.
- **Fields**: `Char(size=...)` size ignored; `selection_add` requires `ondelete`.
- **Security**: TransientModel (wizard) needs an explicit ACL.
- **Stock (verify)**: `stock.picking.move_lines` → `move_ids_without_package`
  (`move_line_ids` → `move_line_ids_without_package`).

## NO upgrade_code codemod

`odoo/upgrade_code/` does not exist before 18.0, so **13→14 has zero codemods**.
All fixes are manual + DB-level `migrations/14.0/` scripts (OpenUpgrade).

## Contents

- `SKILL.md` — the skill (frontmatter + workflow + hard rules / red lines)
- `references/` — 6 source-verified mapping tables
  - `orm-api.md` — _name_search, name_get, with_company, record rules
  - `views-qweb.md` — ir.actions.* access removal, invisible/readonly->attrs, frontend
  - `models-mapping.md` — selection_add ondelete, Char size, string attr, stock.picking
  - `security.md` — res.groups unchanged + TransientModel explicit ACL
  - `http-rpc-mail.md` — HTTP/mail/binary unchanged + red lines
  - `upgrade-code.md` — codemod status (none) + migrations/14.0 workflow
- `scripts/` — `scan_addon.py` (13→14 scanner), `check_markdown.py`, `normalize_markdown.py`

## Usage

```bash
python3 scripts/scan_addon.py /path/to/addons          # triage (lists 13-only APIs)
python3 scripts/scan_addon.py /path/to/addons --addon my_module --json
```

Then apply the manual mappings from `references/*` and re-scan (expect 0).
