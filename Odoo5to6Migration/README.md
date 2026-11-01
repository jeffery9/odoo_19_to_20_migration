# Odoo5to6Migration

This is the **5.0 → 6.0** member of the multi-version migration workspace
(see the root README for the full matrix). The 6→7 member and later members
live in their own `OdooXYtoZW Migration/` folders.

A reusable agent skill that migrates custom OpenERP 5.0 addons to 6.0 (CE)
using source-verified manual mappings. Companion cookbook:
`../Odoo_Migration_Cookbook_5_to_6.md`.

## What breaks in 5→6 (headline)

- **Manifest file renamed** — `__terp__.py` (5.0) → `__openerp__.py` (6.0).
- **Manifest keys** — `init_xml` / `update_xml` → `data`; `demo_xml` → `demo`
  (6.0 also adds `test` and `web` keys; old keys deprecated but accepted).
- **New default web client** ships in 6.0 (GTK still works) — [verify]-light.
- **Module structure** — `report/` for reports, `static/` for web assets.
- The old ORM (`from openerp import ...`, `osv.osv`, `cr, uid, ids, context`)
  is **unchanged** in 5→6.

## NO upgrade_code codemod

`odoo/upgrade_code/` does not exist before 18.0 (and the `odoo` package did not
yet exist in 6.0). So **5→6 has zero codemods**. All fixes are manual + DB-level
`migrations/6.0/` scripts (OpenUpgrade).

## Contents

- `SKILL.md` — the skill (frontmatter + workflow + hard rules / red lines)
- `references/` — 6 source-verified mapping tables
  - `orm-api.md` — ORM/Python old-style API (5→6 unchanged) + red-line exclusions
  - `views-qweb.md` — views / QWeb / web client (default in 6.0)
  - `models-mapping.md` — manifest file/key remap + `report/`/`static/` structure
  - `security.md` — res.groups / access rights unchanged in 5→6
  - `http-rpc-mail.md` — HTTP / mail / binary unchanged in 5→6
  - `upgrade-code.md` — codemod status (none) + migrations/6.0 workflow
- `scripts/` — `scan_addon.py` (5→6 scanner), `check_markdown.py`, `normalize_markdown.py`

## Usage

```bash
python3 scripts/scan_addon.py /path/to/addons          # triage (lists 5.0-only APIs)
python3 scripts/scan_addon.py /path/to/addons --addon my_module --json
```

Then apply the manual mappings from `references/*` and re-scan (expect 0).
