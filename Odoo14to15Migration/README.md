# Odoo14to15Migration

This is the **14→15** member of the multi-version migration workspace
(see the root README for the full matrix). The 13→14 member lives in
`../Odoo13to14Migration/` and the 15→16 member in `../Odoo15to16Migration/`.

A reusable agent skill that migrates custom Odoo 14.0 addons to 15.0 (CE and EE)
using source-verified manual mappings. Companion cookbook:
`../Odoo_Migration_Cookbook_14_to_15.md`.

## What breaks in 14→15 (headline)

- **QWeb `t-raw` removed** — use `t-out` (no escape) or `t-esc` (escape); server
  HTML wrapped in `markupsafe.Markup`.
- **`ir.model*` direct access removed** — `ir.model`/`ir.model.fields`/
  `ir.model.data` must be read via `sudo()` or model APIs. (Different object
  from the 13→14 `ir.actions.*` removal.)
- **Mail templates: Jinja → QWeb + inline_template** — `body_html` becomes QWeb
  (`type="qweb"`); subject/email_from/email_to use `{{ }}` not `${ }`.
- **Frontend**: ES modules `/** @odoo-module **/` must be renamed `*.esm.js`;
  JS/SCSS assets move from XML into `__manifest__.py` `assets` key (the `qweb`
  key is removed).
- **Tests**: `SavepointCase` alias removed → `TransactionCase`;
  `Environment.manage()` no longer needed.

## NO upgrade_code codemod

`odoo/upgrade_code/` does not exist before 18.0, so **14→15 has zero codemods**.
All fixes are manual + DB-level `migrations/15.0/` scripts (OpenUpgrade).

## Contents

- `SKILL.md` — the skill (frontmatter + workflow + hard rules / red lines)
- `references/` — 6 source-verified mapping tables
  - `views-qweb.md` — t-raw->t-out/t-esc, ir.model* access, esm.js, assets manifest
  - `orm-api.md` — ir.model* access, SavepointCase->TransactionCase, Environment.manage
  - `models-mapping.md` — t-out/t-esc cheat, manifest assets/qweb key
  - `http-rpc-mail.md` — Jinja->QWeb mail, subtype->subtype_xmlid, HTTP unchanged
  - `security.md` — res.groups unchanged (15.0)
  - `upgrade-code.md` — codemod status (none) + migrations/15.0 workflow
- `scripts/` — `scan_addon.py` (14→15 scanner), `check_markdown.py`, `normalize_markdown.py`

## Usage

```bash
python3 scripts/scan_addon.py /path/to/addons          # triage (lists 14-only APIs)
python3 scripts/scan_addon.py /path/to/addons --addon my_module --json
```

Then apply the manual mappings from `references/*` and re-scan (expect 0).
