---
name: odoo_8_to_9_migration
description: Migrates custom Odoo 8.0 addons to 9.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 8 to 9, fix 9.0 hard breaks (Community/Enterprise edition split — modules like account_voucher/account_analytic_plan/document/marketing became Enterprise-only, osv.except_osv/except_orm->openerp.exceptions.UserError, ir.model osv_memory field->transient with _is_osv_memory/_search_osv_memory removed, osv_memory_autovacuum model->ir_autovacuum, ir.cron method_direct_trigger added), or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 8-only APIs. NOTE 8.0 and 9.0 both still use `from openerp import ...` (the openerp->odoo rename is 9->10, NOT this pair); @api.one/@api.multi/@api.model already exist in 8.0. 9.0 has NO upgrade_code codemod — all fixes are manual; DB changes handled by OpenUpgrade.
version: 9.0.1
author: Independent (companion to the Odoo Migration Cookbook series)
category: migration
odoo_versions: ["8.0", "9.0"]
tags: [odoo, migration, upgrade, enterprise-split, user-error, osv-memory, transient, ir-autovacuum, codemod, upgrade_code]
---

# Odoo 8 → 9 Migration

## Goal

Take a 8.0 custom addon (or a whole addons tree) to 9.0 with no leftover
8-only API, using **verified manual mappings** (there is **no** `upgrade_code`
codemod for 8→9 — the tooling ships in 18.0). Database-level changes
(Enterprise module split, field/structure) are applied by **OpenUpgrade** / the
official upgrade service; this skill covers the **code-level** mappings a
custom module must make.

> **Scope note.** This skill covers the **8.0 → 9.0** jump only. The 9→10
> skill handles the next step (`openerp`→`odoo` package rename,
> `__openerp__.py`→`__manifest__.py`, group modularization). The `@api.one`
> removal / `fields.Date` runtime object / `parent_path` belong to **11→12**,
> not this pair. 8.0 and 9.0 **both** use `from openerp import ...`.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables for the
  8→9 jump. Primary anchors:
  - Odoo 9.0 Release Notes (2015) — Community/Enterprise edition split,
    Material Design UI.
  - oejia.net《Odoo 8 到 9 升级分析》—— `osv.except_osv`→`UserError`,
    `ir.model` `osv_memory`→`transient` + method removal,
    `osv_memory_autovacuum`→`ir_autovacuum`, Enterprise module moves.
  - 8.0 / 9.0 源码核对 — `openerp.exceptions.UserError`, `ir.model`
    `transient` field, `ir_autovacuum` model, `ir.cron` `method_direct_trigger`.
- Items tagged **[verify]** come from a single community source or sources that
  disagree (Material Design class specifics). Confirm before relying on them.
  `[EE-verify]` items are Enterprise-only (module move targets).

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 9.0 replacement, and notes every item is `manual`
   (no codemod exists for 8→9).
2. **Manual mappings** — for every finding, apply the replacement from the
   matching reference file:
   - exception / ir.model / ir_autovacuum / ir.cron → `references/orm-api.md`
   - views / QWeb / Material Design → `references/views-qweb.md`
   - Community/Enterprise module split mapping → `references/models-mapping.md`
   - security file & `res.groups` (unchanged in 8→9) → `references/security.md`
   - HTTP/RPC/mail/binary (unchanged in 8→9) → `references/http-rpc-mail.md`
   - codemod status & `migrations/9.0/` scripts → `references/upgrade-code.md`
3. **Data migrations** — put custom DB/structure fixes in each module's
   `migrations/9.0/` (`pre-`/`post-` scripts, e.g. Enterprise dependency audit,
   `osv_memory`→`transient` history data). There is no `upgrade_code` run for
   8→9.
4. **Validate** — re-run the scanner (expect 0 findings), then
   `openerp-bin -u <module> --test-enable` in a 9.0 sandbox (Python 2.7); fix
   `ImportError` (`osv.except_osv`) / `AttributeError` (`_is_osv_memory` /
   `osv_memory_autovacuum`) first. Start with `--debug`.
5. **Report** — summarize per addon: manual edits (with reference anchor used),
   remaining [verify]/[EE-verify] items, test status.

## Model changes (core business models)

**No core business model rename or removal.** 8→9 is the Community/Enterprise
split; the model-layer work is confined to the `ir.model` bookkeeping and
transient machinery:

| Check | 8.0 | 9.0 | Action |
|---|---|---|---|
| `ir.model.osv_memory` | field present | → `transient` | Rename in any module reading it directly |
| `_is_osv_memory` / `_search_osv_memory` | present | removed | Replace with `_transient` equivalents |
| `osv_memory_autovacuum` model | present | → `ir_autovacuum` | Repoint XML-IDs and crons |

Do not pull `stock.pack.operation` removal or `account.invoice`→`account.move`
into this pair — they belong to 9→10 and 12→13 respectively.

Cross-version model index: `Core_Models_Changelog.md`.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 9.0 tree (or the
  mapping tables, which cite their source). Unverifiable ids stay flagged,
  never silently "completed".
- **Community/Enterprise split is the headline breaking change.** Audit every
  `depends` entry: if it names a module that became Enterprise-only
  (`account_voucher`, `account_analytic_plan`, `document`, `marketing`, parts of
  `crm`/`hr`/`website`), the dependency now requires Enterprise — confirm and
  flag [EE-verify]; do not silently drop the dependency.
- **`osv.except_osv` / `except_orm` → `openerp.exceptions.UserError`.** Replace
  both with `from openerp.exceptions import UserError` + `raise UserError(...)`.
- **`ir.model` (`ir_model`): the `osv_memory` field is renamed `transient`; the
  methods `_is_osv_memory` and `_search_osv_memory` are removed** — drop any
  override/call.
- **`osv_memory_autovacuum` model → `ir_autovacuum`** — update model references
  and XML-IDs.
- **`ir.cron` gained `method_direct_trigger`** (additive, 9.0) — not a break,
  just available.
- **8.0 and 9.0 both use `from openerp import ...`.** Do NOT rename `openerp`
  to `odoo` here — that package rename is **9→10**, not this pair.
- **`@api.one` / `@api.multi` / `@api.model` already exist in 8.0** and are NOT
  removed in 9.0 (their removal is 11→12). Do not strip `@api.one` during 8→9.
- **There is NO `upgrade_code` codemod for 8→9** — `odoo/upgrade_code/` /
  `openerp/upgrade_code/` does not exist in 9.0. Do not tell the user to run
  `openerp-bin upgrade_code --from 8.0`; all code renames are manual, DB changes
  are OpenUpgrade's job.
- **Do NOT migrate these in 8→9** (they are still valid in 9.0; their
  removal/rename belongs to a later pair): `openerp`→`odoo` package rename
  (9→10); `@api.one` removal / `fields.Date`/`Datetime` runtime object /
  `from_string` removal / `parent_path` / `ir.actions.act_window.view` removal
  (11→12); New-API decorators / `self.env` / `osv.Model`→`models.Model` (7→8);
  `account.invoice`→`account.move` (12→13).
- When copying a value from a clipped/secondary source, verify it against the
  9.0 tree before committing.
