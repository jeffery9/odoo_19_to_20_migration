# Odoo11to12Migration

This is the **11→12** member of the multi-version migration workspace
(see the root README for the full matrix). The 12→13 member lives in
`../Odoo12to13Migration/` and the 15→16 member in `../Odoo15to16Migration/`.

A reusable agent skill that migrates custom Odoo 11.0 addons to 12.0 (CE and EE)
using source-verified manual mappings. Companion cookbook:
`../Odoo_Migration_Cookbook_11_to_12.md`.

## What breaks in 11→12 (headline)

- **`@api.one` removed** — drop the decorator, wrap body in `for record in self:`
  (or `@api.model` for pure-model methods). `api.multi` still exists but deprecated.
- **`fields.Date` / `fields.Datetime` runtime values become real `date`/`datetime`
  objects** — `from_string` removed → use `fields.Date.to_date` /
  `fields.Datetime.to_datetime`. String slicing on date fields breaks.
- **`@api.model_create_multi` introduced** — override `create()` with it.
- **`ir.actions.act_window.view` model removed** — bind views via the action's `view_ids`.
- **`do_notify` / `do_warning` removed** → `raise UserError` / `message_post`.
- **`_parent_store`: `parent_left`/`parent_right` → `parent_path`**.
- **QWeb `t-field-options` → `t-options`**.

## NO upgrade_code codemod

`odoo/upgrade_code/` does not exist before 18.0, so **11→12 has zero codemods**.
All fixes are manual + DB-level `migrations/12.0/` scripts (OpenUpgrade).

## Contents

- `SKILL.md` — the skill (frontmatter + workflow + hard rules / red lines)
- `references/` — 6 source-verified mapping tables
  - `orm-api.md` — api.one, from_string, model_create_multi, parent_path, do_notify/do_warning
  - `views-qweb.md` — act_window.view removal, t-field-options→t-options
  - `models-mapping.md` — 11→12 field/model mapping + red-line exclusions
  - `security.md` — res.groups / access rights unchanged in 11→12
  - `http-rpc-mail.md` — HTTP / mail / binary unchanged in 11→12
  - `upgrade-code.md` — codemod status (none) + migrations/12.0 workflow
- `scripts/` — `scan_addon.py` (11→12 scanner), `check_markdown.py`, `normalize_markdown.py`

## Usage

```bash
python3 scripts/scan_addon.py /path/to/addons          # triage (lists 11-only APIs)
python3 scripts/scan_addon.py /path/to/addons --addon my_module --json
```

Then apply the manual mappings from `references/*` and re-scan (expect 0).
