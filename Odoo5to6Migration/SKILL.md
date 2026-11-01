---
name: odoo_5_to_6_migration
description: Migrates custom OpenERP 5.0 addons to 6.0 (CE). Use when the user asks to upgrade/migrate modules from 5.0 to 6.0, fix 6.0 hard breaks (manifest file renamed __terp__.py -> __openerp__.py, manifest keys init_xml/update_xml/demo_xml -> data/demo/test, new default web client, report/ and static/ module directories), or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 5.0-only APIs. Note 6.0 and earlier have NO upgrade_code codemod (the engine only exists from 18.0) — all fixes are manual; DB changes handled by OpenUpgrade.
version: 6.0.1
author: Independent (companion to the Odoo Migration Cookbook series)
category: migration
odoo_versions: ["5.0", "6.0"]
tags: [openerp, odoo, migration, upgrade, terp-manifest, manifest-keys, web-client, report-dir, codemod, upgrade_code]
---

# OpenERP 5.0 → 6.0 Migration

## Goal

Take a 5.0 custom addon (or a whole addons tree) to 6.0 with no leftover
5.0-only manifest conventions, using **verified manual mappings** (there is
**no** `upgrade_code` codemod for 5→6 — the tooling ships in 18.0). Database-level
changes are applied by **OpenUpgrade** / the official upgrade service; this skill
covers the **code-level** manifest/structure mappings a custom module must make.

> **Scope note.** This skill covers the **5.0 → 6.0** jump only. The 6→7 skill
> handles the next step (`osv.osv`→`osv.Model` base-class rename,
> `res.partner.address` removal). The `__openerp__.py`→`__manifest__.py` rename
> and `openerp`→`odoo` import rename belong to 9→10 — do NOT apply them in 5→6.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables for the
  5→6 jump. Primary anchors:
  - OpenERP 5.0 official docs (doc.odoo.com/5.0) — show `__terp__.py` with
    `init_xml` / `demo_xml` / `update_xml` keys (confirms 5.0 manifest shape).
  - Community docs on `__openerp__.py` evolution (odoo.net.cn et al.) — 6.0
    introduced `__openerp__.py` (replacing `__terp__.py`) plus the simpler
    `data` / `demo` / `test` / `web` keys.
  - OpenERP 6.0 release notes — new default web client; `report/` and `static/`
    module directories.
- Items tagged **[verify]** come from sparse/conflicting community sources or
  framework-level claims not pinned to a solid primary source (web client
  architecture details, `test`/`web` key loading timing, `report/`/`static/`
  sub-path conventions). Confirm against the 6.0 source tree before relying on
  them. `[EE-verify]` items are Enterprise-only (none asserted for 5→6).
- The two **CONFIRMED** anchor facts are: `__terp__.py`→`__openerp__.py` and
  `init_xml`/`update_xml`/`demo_xml`→`data`/`demo`/`test`.

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 6.0 replacement, and notes every item is `manual`
   (no codemod exists for 5→6).
2. **Manual mappings** — for every finding, apply the replacement from the
   matching reference file:
   - manifest file rename + key remap + module structure → `references/models-mapping.md`
   - ORM / Python old-style API (5→6 unchanged) + red lines → `references/orm-api.md`
   - views / QWeb / web client → `references/views-qweb.md`
   - security file & `res.groups` (unchanged in 5→6) → `references/security.md`
   - HTTP/RPC/mail/binary (unchanged in 5→6) → `references/http-rpc-mail.md`
   - codemod status & `migrations/6.0/` scripts → `references/upgrade-code.md`
3. **Data migrations** — put custom DB/structure fixes in each module's
   `migrations/6.0/` (`pre-`/`post-` scripts). There is no `upgrade_code` run
   for 5→6.
4. **Validate** — re-run the scanner (expect 0 findings), then install/update
   the module on a 6.0 instance (`openerp-server -u <module>`); clear any
   `__terp__.py` / `init_xml` / `update_xml` / `demo_xml` deprecation warnings.
5. **Report** — summarize per addon: manual edits (with reference anchor used),
   remaining [verify] items, test status.

## Model changes (core business models)

**None.** 5→6 has no core business model rename, addition or removal. The break
is entirely in packaging metadata (`__terp__.py` → `__openerp__.py`) and view
bootstrap. Do not invent model renames here.

Cross-version model index: `Core_Models_Changelog.md`.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 6.0 tree (or the
  mapping tables, which cite their source). Unverifiable ids stay flagged,
  never silently "completed".
- **Manifest file rename is the headline breaking change.** Rename
  `__terp__.py` → `__openerp__.py`. 6.0 still reads the old name but new code
  must use `__openerp__.py`.
- **Manifest keys `init_xml` / `update_xml` → `data`; `demo_xml` → `demo`.**
  6.0 also adds the `test` and `web` keys; old keys are still accepted but
  deprecated. Do not continue to `__openerp__.py`→`__manifest__.py` (that is
  9→10).
- **Module structure:** 6.0 encourages `report/` for report files and
  `static/` for web-client assets — structural guidance, not a hard break.
- **5→6 is a VERY old pair.** The ORM (`from openerp import ...`, `osv.osv`
  base class, `cr, uid, ids, context` method signatures) is UNCHANGED in 5→6.
  Mark any framework-level claim you cannot pin to a solid source with [verify].
- **There is NO `upgrade_code` codemod for 5→6** — `odoo/upgrade_code/` does
  not exist before 18.0 (it does not even exist in 6.0; the `odoo` package did
  not yet exist). Do not tell the user to run `openerp-server upgrade_code
  --from 5.0`; all manifest renames are manual, DB changes are OpenUpgrade's job.
- **Do NOT migrate these in 5→6** (they are still valid in 6.0, or belong to
  later pairs): `osv.osv`→`osv.Model` base-class rename (6→7);
  `res.partner.address` removal (6→7); `openerp`→`odoo` import rename (9→10);
  `__openerp__.py`→`__manifest__.py` (9→10); `@api.*` new API / `self.env` /
  `fields.Date` object / `@api.one` removal (7→8 / 11→12); `account.invoice`→
  `account.move` (12→13).
- When copying a value from a clipped/secondary source, verify it against the
  6.0 tree before committing.
