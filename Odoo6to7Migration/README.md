# Odoo6to7Migration

This is the **6→7** member of the multi-version migration workspace
(see the root README for the full matrix). The 7→8 member (new API) will live in
`../Odoo7to8Migration/` and the 10→11 member in `../Odoo10to11Migration/`.

A reusable agent skill that migrates custom OpenERP 6.0 addons to 7.0 (CE and EE)
using source-verified manual mappings. Companion cookbook:
`../Odoo_Migration_Cookbook_6_to_7.md`.

## What breaks in 6→7 (headline)

- **`osv.osv` → `osv.Model`** (and `osv.osv_memory` → `osv.TransientModel` for
  wizards). `osv` becomes a deprecated alias. Keep `from openerp.osv import osv`.
- **`res.partner.address` REMOVED** — addresses merged into `res.partner`;
  use `res.partner` fields directly (street, city, email, phone).
- **Manifest `__openerp__.py`: `update_xml` → `data`** (fold `init_xml` /
  `demo_xml` into `data` too). File is NOT renamed (that is 9→10).
- **Views: `version="7.0"` + `<sheet>` / `<header>` / `<footer>` + Bootstrap**;
  HTML allowed in views.
- **OLD API (`cr, uid, ids, context`) still used in 6→7** — the new API
  (`@api.*`, `models.Model`, `self.env`) arrives in **7→8**, NOT here.

## NO upgrade_code codemod

`odoo/upgrade_code/` does not exist before 18.0, so **6→7 has zero codemods**.
All fixes are manual + DB-level `migrations/7.0/` scripts (OpenUpgrade).

## Contents

- `SKILL.md` — the skill (frontmatter + workflow + hard rules / red lines)
- `references/` — 6 source-verified mapping tables
  - `orm-api.md` — osv.osv→osv.Model, osv.osv_memory→osv.TransientModel, OLD API signatures
  - `views-qweb.md` — version="7.0", sheet/header/footer, Bootstrap frontend
  - `models-mapping.md` — res.partner.address merge, update_xml→data mapping
  - `security.md` — res.groups / access rights unchanged in 6→7
  - `http-rpc-mail.md` — HTTP / mail / binary unchanged in 6→7
  - `upgrade-code.md` — codemod status (none) + migrations/7.0 workflow
- `scripts/` — `scan_addon.py` (6→7 scanner), `check_markdown.py`, `normalize_markdown.py`

## Usage

```bash
python3 scripts/scan_addon.py /path/to/addons          # triage (lists 6-only APIs)
python3 scripts/scan_addon.py /path/to/addons --addon my_module --json
```

Then apply the manual mappings from `references/*` and re-scan (expect 0).
