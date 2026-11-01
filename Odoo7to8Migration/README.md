# Odoo7to8Migration

This is the **7→8** member of the multi-version migration workspace
(see the root README for the full matrix). The 8→9 / 10→11 member lives in
`../Odoo10to11Migration/` and the 11→12 member in `../Odoo11to12Migration/`.

A reusable agent skill that migrates custom Odoo 7.0 addons to 8.0 (CE and EE)
using source-verified manual mappings (the famous "new API" migration). Companion
cookbook: `../Odoo_Migration_Cookbook_7_to_8.md`.

## What breaks in 7→8 (headline)

- **New-API decorators introduced** — `@api.model`, `@api.multi`, `@api.one`,
  `@api.depends`, `@api.constrains`, `@api.onchange`, `@api.returns`.
  Add them; drop `(cr, uid, ids, context)` signatures in favour of recordsets.
- **`self.env` replaces `self.pool` / `self.cr` / `self.uid` / `self.context`**;
  methods operate on recordsets.
- **`osv.Model` / `osv.osv` / `osv.osv_memory` → `models.Model` /
  `models.TransientModel`** (the `osv` alias removed in 8.0). Import
  `from openerp import models, api, fields`.
- **`osv.except_osv` / `except_orm` → `openerp.exceptions.UserError`**.
- **Fields become class attributes:** `_columns` / `_all_columns` →
  `name = fields.Char(...)`; runtime container is `_fields`.
- **QWeb report engine + Bootstrap / website builder introduced** in 8.0
  (RML/Mako deprecated but still runnable).

## NO upgrade_code codemod

`odoo/upgrade_code/` does not exist before 18.0, so **7→8 has zero codemods**.
All fixes are manual + DB-level `migrations/8.0/` scripts (OpenUpgrade).

## Contents

- `SKILL.md` — the skill (frontmatter + workflow + hard rules / red lines)
- `references/` — 6 source-verified mapping tables
  - `orm-api.md` — decorators, self.env, osv.Model->models.Model, except_osv->UserError, fields-attr
  - `views-qweb.md` — QWeb reports, Bootstrap, view compatibility
  - `models-mapping.md` — 7→8 field/model mapping + red-line exclusions
  - `security.md` — res.groups / access rights unchanged in 7→8
  - `http-rpc-mail.md` — HTTP / mail / binary unchanged in 7→8
  - `upgrade-code.md` — codemod status (none) + migrations/8.0 workflow
- `scripts/` — `scan_addon.py` (7→8 scanner), `check_markdown.py`, `normalize_markdown.py`

## Usage

```bash
python3 scripts/scan_addon.py /path/to/addons          # triage (lists 7-only APIs)
python3 scripts/scan_addon.py /path/to/addons --addon my_module --json
```

Then apply the manual mappings from `references/*` and re-scan (expect 0).
