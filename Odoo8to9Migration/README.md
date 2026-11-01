# Odoo8to9Migration

This is the **8→9** member of the multi-version migration workspace
(see the root README for the full matrix). The 9→10 member lives in
`../Odoo9to10Migration/` and the 10→11 member in `../Odoo10to11Migration/`.

A reusable agent skill that migrates custom Odoo 8.0 addons to 9.0 (CE and EE)
using source-verified manual mappings. Companion cookbook:
`../Odoo_Migration_Cookbook_8_to_9.md`.

> 8.0 and 9.0 **both use `from openerp import ...`** — the `openerp`→`odoo`
> rename is **9→10**, NOT this pair. New-API decorators (`@api.model` /
> `@api.multi` / `@api.one`) already exist in 8.0.

## What breaks in 8→9 (headline)

- **Community / Enterprise edition split** — modules like `account_voucher`,
  `account_analytic_plan`, `document`, `marketing` (and parts of `crm`/`hr`/
  `website`) became Enterprise-only. Audit every `depends` entry [EE-verify].
- **`osv.except_osv` / `except_orm` → `openerp.exceptions.UserError`**.
- **`ir.model` (`ir_model`): `osv_memory` field → `transient`**; methods
  `_is_osv_memory` / `_search_osv_memory` removed.
- **`osv_memory_autovacuum` model → `ir_autovacuum`**.
- **`ir.cron` gained `method_direct_trigger`** (additive, not a break).

## NO upgrade_code codemod

`odoo/upgrade_code/` / `openerp/upgrade_code/` does not exist before 18.0, so
**8→9 has zero codemods**. All fixes are manual + DB-level `migrations/9.0/`
scripts (OpenUpgrade).

## Contents

- `SKILL.md` — the skill (frontmatter + workflow + hard rules / red lines)
- `references/` — 6 source-verified mapping tables
  - `orm-api.md` — except_osv→UserError, osv_memory→transient, ir_autovacuum, ir.cron method_direct_trigger, old API
  - `views-qweb.md` — views / QWeb / Material Design UI note
  - `models-mapping.md` — Community/Enterprise split module mapping
  - `security.md` — res.groups / access rights unchanged in 8→9
  - `http-rpc-mail.md` — HTTP / mail / binary unchanged in 8→9
  - `upgrade-code.md` — codemod status (none) + migrations/9.0 workflow
- `scripts/` — `scan_addon.py` (8→9 scanner), `check_markdown.py`, `normalize_markdown.py`

## Usage

```bash
python3 scripts/scan_addon.py /path/to/addons          # triage (lists 8-only APIs)
python3 scripts/scan_addon.py /path/to/addons --addon my_module --json
```

Then apply the manual mappings from `references/*` and re-scan (expect 0).
