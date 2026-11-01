---
name: odoo_6_to_7_migration
description: Migrates custom OpenERP 6.0 addons to 7.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 6 to 7, fix 7.0 hard breaks (osv.osv -> osv.Model and osv.osv_memory -> osv.TransientModel for wizards, res.partner.address model removed/merged into res.partner, __openerp__.py manifest update_xml -> data with init_xml/demo_xml consolidated, view version="7.0" + sheet/header/footer + Bootstrap CSS), or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 6-only APIs. NOTE 6/7 use the openerp package (NOT odoo) and the OLD API signatures (cr, uid, ids, context) — the new API (@api.*, models.Model, self.env) arrives in 7->8, NOT here. 7.0 has NO upgrade_code codemod — all fixes are manual; DB changes handled by OpenUpgrade.
version: 7.0.1
author: Independent (companion to the Odoo Migration Cookbook series)
category: migration
odoo_versions: ["6.0", "7.0"]
tags: [odoo, openerp, migration, upgrade, osv-model, partner-address, manifest-data, view-bootstrap, codemod, upgrade_code]
---

# Odoo 6 → 7 Migration

## Goal

Take a 6.0 custom addon (or a whole addons tree) to 7.0 with no leftover
6-only API, using **verified manual mappings** (there is **no** `upgrade_code`
codemod for 6→7 — the tooling ships in 18.0). Database-level changes
(`res_partner_address` merged into `res.partner`, field structure) are applied
by **OpenUpgrade** / the official upgrade service; this skill covers the
**code-level** mappings a custom module must make.

> **Scope note.** This skill covers the **6.0 → 7.0** jump only. The 7→8
> skill handles the next step (`models.Model`, `@api.*`, `self.env`,
> `osv.except_osv`→`UserError`). The `openerp`→`odoo` rename and
> `__openerp__.py`→`__manifest__.py` file rename belong to **9→10** — 6/7 keep
> the `openerp` package and the `__openerp__.py` filename (only the *keys*
> inside it change).

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables for the
  6→7 jump. Primary anchors:
  - OpenERP 7.0 Release Notes ("not just an update", new web client, Bootstrap,
    address merge) — headline changes.
  - Odoo forum v6→v7 threads + dbi-services 6→7 blog — `osv.osv`→`osv.Model`,
    `res.partner.address` removal, `update_xml`→`data`, `version="7.0"`/`sheet`.
  - 7.0 source verification: `openerp.osv.osv` deprecated alias; `osv.Model` /
    `osv.TransientModel` recommended; `res.partner` now holds address fields;
    `__openerp__.py` only recognizes the `data` key.
- Items tagged **[verify]** come from a single community source or sources that
  disagree (Bootstrap exact major version) — confirm before relying on them.
  `[EE-verify]` items are Enterprise-only.

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 7.0 replacement, and notes every item is `manual`
   (no codemod exists for 6→7).
2. **Manual mappings** — for every finding, apply the replacement from the
   matching reference file:
   - ORM & Python base class (`osv.osv`→`osv.Model`, `osv.osv_memory`→
     `osv.TransientModel`, OLD API `cr, uid, ids, context`) → `references/orm-api.md`
   - views / QWeb / frontend (`version="7.0"`, `sheet`/`header`/`footer`,
     Bootstrap) → `references/views-qweb.md`
   - model/field mapping (`res.partner.address` merge, `update_xml`→`data`) →
     `references/models-mapping.md`
   - security file & `res.groups` (unchanged in 6→7) → `references/security.md`
   - HTTP/RPC/mail/binary (unchanged in 6→7) → `references/http-rpc-mail.md`
   - codemod status & `migrations/7.0/` scripts → `references/upgrade-code.md`
3. **Data migrations** — put custom DB/structure fixes in each module's
   `migrations/7.0/` (`pre-`/`post-` scripts, e.g. `res_partner_address` merge).
   There is no `upgrade_code` run for 6→7.
4. **Validate** — re-run the scanner (expect 0 findings), then
   `openerp-server -u <module> --test-enable` in a 7.0 sandbox; fix
   `ImportError` (`res.partner.address` model missing) / `AttributeError`
   (old `address_*` helpers) first. Start with `--debug` and clear every
   `DeprecationWarning` (`osv.osv` alias).
5. **Report** — summarize per addon: manual edits (with reference anchor used),
   remaining [verify] items, test status.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 7.0 tree (or the
  mapping tables, which cite their source). Unverifiable ids stay flagged,
  never silently "completed".
- **`osv.osv` → `osv.Model` is the headline base-class change.** Wizards:
  `osv.osv_memory` → `osv.TransientModel`. Keep
  `from openerp.osv import osv, fields`; do NOT switch to `odoo` (that is 9→10)
  and do NOT switch to `models.Model` (that is 7→8).
- **`res.partner.address` is REMOVED in 7.0** — addresses are merged into
  `res.partner`; use `res.partner` fields directly (street, city, email, phone).
  Remove every `res.partner.address` / `res_partner_address` reference.
- **Manifest `__openerp__.py`: `update_xml` → `data`** (and fold `init_xml` /
  `demo_xml` into `data` too). Do NOT rename the file to `__manifest__.py`
  (that is 9→10).
- **Views get `version="7.0"`** on the root element and use `<sheet>` /
  `<header>` / `<footer>`; HTML is allowed in views. This is a layout/attribute
  change, not a model change.
- **Keep the OLD API signatures `cr, uid, ids, context`** — 6→7 does NOT
  introduce `@api.*`, `self.env`, or `models.Model`. Do not "modernize" method
  signatures to the new API; that belongs to 7→8 and changes semantics.
- **There is NO `upgrade_code` codemod for 6→7** — `odoo/upgrade_code/` does
  not exist in 7.0. Do not tell the user to run `odoo-bin upgrade_code
  --from 6.0`; all code renames are manual, DB changes are OpenUpgrade's job.
- **Do NOT migrate these in 6→7** (they are still valid in 7.0; their
  removal/rename belongs to 7→8 or later): `osv.Model`→`models.Model` /
  `@api.*` / `self.env` / `osv.except_osv`→`UserError` (7→8); `openerp`→`odoo`
  (9→10); `__openerp__.py`→`__manifest__.py` (9→10); `@api.one` removal /
  `fields.Date` runtime object (11→12).
- When copying a value from a clipped/secondary source, verify it against the
  7.0 tree before committing.
