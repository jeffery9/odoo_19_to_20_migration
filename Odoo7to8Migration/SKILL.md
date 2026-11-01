---
name: odoo_7_to_8_migration
description: Migrates custom Odoo 7.0 addons to 8.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 7 to 8, fix 8.0 hard breaks (the "new API" landing — new-API decorators @api.model/@api.multi/@api.one/@api.depends/@api.constrains/@api.onchange/@api.returns introduced, self.env replaces self.pool/self.cr/self.uid/self.context and (cr, uid, ids, context) signatures, osv.Model/osv.osv/osv.osv_memory -> models.Model/models.TransientModel, osv.except_osv/except_orm -> UserError, _columns/_all_columns -> class-attribute fields.Char(...) with _fields, QWeb report engine + Bootstrap/website builder introduced), or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 7-only APIs. Note 8.0 and earlier have NO upgrade_code codemod (the engine only exists from 18.0) — all fixes are manual; DB changes handled by OpenUpgrade.
version: 8.0.1
author: Independent (companion to the Odoo Migration Cookbook series)
category: migration
odoo_versions: ["7.0", "8.0"]
tags: [odoo, migration, upgrade, new-api, api-decorators, self-env, models-model, user-error, fields-attr, qweb-report, codemod, upgrade_code]
---

# Odoo 7 → 8 Migration

## Goal

Take a 7.0 custom addon (or a whole addons tree) to 8.0 with no leftover
7-only API, using **verified manual mappings** (there is **no** `upgrade_code`
codemod for 7→8 — the tooling ships in 18.0). Database-level changes are
applied by **OpenUpgrade** / the official upgrade service; this skill covers
the **code-level** mappings a custom module must make — i.e. the famous
"new API" migration.

> **Scope note.** This skill covers the **7.0 → 8.0** jump only. 7/8 use the
> `openerp` package name (`from openerp import ...`); the `openerp`→`odoo`
> rename is **9→10**, NOT this pair. The OLD API (`def meth(self, cr, uid, ids,
> context=None)`) is what 7.0 code uses; 8.0 *adds* the NEW API (it does not
> remove the old one). The next step (8→9) and beyond are handled by their own
> skills (`Odoo10to11Migration/` etc.). Many items that changed *after* 8.0 are
> listed here ONLY where they are explicitly out of 7→8 scope — see the red lines.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables for the
  7→8 jump. Primary anchors:
  - Odoo odoodays-2014《From V7 to V8: The New API》slides — the new-API
    decorators, `self.env`, recordsets, drop of `(cr, uid, ids, context)`.
  - odoo-80api.readthedocs.io — new-API reference (decorators, fields,
    `models.Model` / `models.TransientModel`, `openerp.exceptions.UserError`).
  - Community sed migration scripts (OCA `openupgrade` 8.0, Odoo community
    forum) — `osv.Model`→`models.Model`, `_columns`→class-attribute fields,
    `osv.except_osv`→`UserError` mapping.
  - 8.0 source check: `openerp.api` module exists; `openerp.osv.osv` alias
    removed; `openerp.exceptions.UserError` present.
- Items tagged **[verify]** come from a single community source or sources that
  disagree (QWeb report migration details, Bootstrap 3 exact version) — confirm
  before relying on them. `[EE-verify]` items are Enterprise-only.

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 8.0 replacement, and notes every item is `manual`
   (no codemod exists for 7→8).
2. **Manual mappings** — for every finding, apply the replacement from the
   matching reference file:
   - new-API decorators / `self.env` / `osv.Model`→`models.Model` /
     `osv.except_osv`→`UserError` / `_columns`→field attributes → `references/orm-api.md`
   - QWeb reports / Bootstrap / views compatibility → `references/views-qweb.md`
   - field-type mapping + model red-line exclusions → `references/models-mapping.md`
   - security file & `res.groups` (unchanged in 7→8) → `references/security.md`
   - HTTP/RPC/mail/binary (unchanged in 7→8) → `references/http-rpc-mail.md`
   - codemod status & `migrations/8.0/` scripts → `references/upgrade-code.md`
3. **Data migrations** — put custom DB/structure fixes in each module's
   `migrations/8.0/` (OpenUpgrade executes). There is no `upgrade_code` run for 7→8.
4. **Validate** — re-run the scanner (expect 0 findings), then
   `odoo-bin -u <module> --test-tags /<module>` in an 8.0 sandbox; fix
   `ImportError` (`osv` base class / `osv.except_osv` / `from openerp.osv import orm`)
   / `AttributeError` (`self.pool`) first. Start with `--dev=all` and clear every
   `DeprecationWarning`.
5. **Report** — summarize per addon: manual edits (with reference anchor used),
   remaining [verify] items, test status.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 8.0 tree (or the
  mapping tables, which cite their source). Unverifiable ids stay flagged,
  never silently "completed".
- **The "new API" is the headline migration.** Add `@api.model` / `@api.multi`
  (and `@api.depends` / `@api.constrains` / `@api.onchange` where applicable),
  switch method signatures from `(cr, uid, ids, context=None)` to recordsets,
  and replace `self.pool.get('x')` with `self.env['x']`, `self.cr/uid/context`
  with `self.env.*`. The old API still works in 8.0 (compat layer) but new code
  must use the new one.
- **`@api.one` returns a LIST** — for button actions prefer `@api.multi` +
  `self.ensure_one()` to avoid the list-wrapping surprise in the web client.
- **`osv.Model` / `osv.osv` / `osv.osv_memory` → `models.Model` /
  `models.TransientModel`.** Import `from openerp import models, api, fields`
  (the `osv` alias is removed in 8.0). `from openerp.osv import orm` is gone.
- **`osv.except_osv` / `except_orm` → `openerp.exceptions.UserError`**
  (`raise UserError(...)`).
- **Fields become class attributes:** `_columns` / `_all_columns` dict →
  `name = fields.Char(...)` etc.; the runtime container is `_fields`.
- **8.0 introduces QWeb reports + Bootstrap/website builder** — RML/Mako report
  engines are deprecated (still runnable) and should be migrated to QWeb
  (`report_type="qweb-pdf"`). Keep this `[verify]`-light; RML/Mako still install.
- **There is NO `upgrade_code` codemod for 7→8** — `odoo/upgrade_code/` does
  not exist in 8.0 (or any version before 18.0). Do not tell the user to run
  `odoo-bin upgrade_code --from 7.0`; all code renames are manual, DB changes are
  OpenUpgrade's job.
- **Do NOT migrate these in 7→8** (they are still valid in 8.0; their
  removal/rename belongs to a later pair): `openerp`→`odoo` (9→10); `@api.one`
  full removal (11→12); `fields.Date`/`Datetime` runtime object + `from_string`
  removal (11→12); `ir.actions.act_window.view` removal (11→12);
  `account.invoice`→`account.move` (12→13); `t-field-options`→`t-options`
  (11→12); `res.partner.address` removal / `osv.osv`→`osv.Model` rename (6→7,
  already done by 7.0). Workflow is STILL present in 8.0 — do not remove it.
- When copying a value from a clipped/secondary source, verify it against the
  8.0 tree before committing.
