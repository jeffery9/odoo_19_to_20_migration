---
name: odoo_13_to_14_migration
description: Migrates custom Odoo 13.0 addons to 14.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 13 to 14, fix 14.0 hard breaks (ir.actions.* direct access removed - use sudo/_for_xml_id//web/action/load, invisible/readonly dynamic expressions like state=='draft' rejected - must use attrs, _name_search now returns ids not (id,name) tuples, _compute_display_name override replaced by name_get, with_context(force_company=) -> with_company, Char size attribute removed, selection_add requires ondelete, TransientModel needs explicit ACL, stock.picking move_lines/move_line_ids rename [verify]), or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 13-only APIs. Note 14.0 has NO upgrade_code codemod — all fixes are manual; DB changes handled by OpenUpgrade.
version: 14.0.1
author: Independent (companion to the Odoo Migration Cookbook series)
category: migration
odoo_versions: ["13.0", "14.0"]
tags: [odoo, migration, upgrade, ir-actions, invisible-attrs, name-search, name-get, with-company, selection-ondelete, codemod, upgrade_code]
---

# Odoo 13 → 14 Migration

## Goal

Take a 13.0 custom addon (or a whole addons tree) to 14.0 with no leftover
13-only API, using **verified manual mappings** (there is **no** `upgrade_code`
codemod for 13→14 — the tooling ships in 18.0). Database-level changes
(selection option migrations, etc.) are applied by **OpenUpgrade** / the official
upgrade service; this skill covers the **code-level** mappings a custom module
must make.

> **Scope note.** This skill covers the **13.0 → 14.0** jump only. The 14→15
> skill (`Odoo14to15Migration/`) handles the next step (ir.model* access removal,
> t-raw removal, Jinja->QWeb mail templates, assets in manifest, SavepointCase/
> Environment.manage removal). Many items that changed *after* 14.0 are listed
> here ONLY where they are explicitly out of 13→14 scope.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables for the
  13→14 jump. Primary anchors:
  - `OCA Migration to version 14.0` (maintainer-tools wiki) — authoritative
    change list (ir.actions.* access removal via sudo/_for_xml_id, invisible/
    readonly dynamic-expression -> attrs, _name_search returns ids,
    _compute_display_name -> name_get, force_company -> with_company, Char size
    removal, selection_add ondelete, TransientModel explicit ACL).
  - odoo/odoo commits f0481392 (selection_add ondelete), 1f48130 (_name_search
    ids), #53335 (ir.actions.* access removal).
- Items tagged **[verify]** come from a single community source or sources that
  disagree (stock.picking field rename) — confirm before relying on them.
  `[EE-verify]` items are Enterprise-only.

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 14.0 replacement, and notes every item is `manual`.
2. **Manual mappings** — for every finding, apply the replacement from the
   matching reference file:
   - ir.actions.* access / invisible-attrs / frontend → `references/views-qweb.md`
   - _name_search / name_get / force_company / record rules → `references/orm-api.md`
   - selection_add ondelete / Char size / string attr / stock.picking →
     `references/models-mapping.md`
   - security file & `res.groups` (unchanged; TransientModel ACL) →
     `references/security.md`
   - HTTP/mail unchanged + red lines → `references/http-rpc-mail.md`
   - codemod status & `migrations/14.0/` scripts → `references/upgrade-code.md`
3. **Data migrations** — put custom DB/structure fixes in each module's
   `migrations/14.0/` (`pre-`/`post-`/`end-` scripts, e.g. selection option
   migration). There is no `upgrade_code` run.
4. **Validate** — re-run the scanner (expect 0 findings), then
   `odoo-bin -u <module> --test-tags /<module>` in a 14.0 sandbox with `--dev=all`
   (QWeb will reject invalid invisible/readonly expressions at load). Fix
   `ImportError`/`AttributeError` first.
5. **Report** — summarize per addon: manual edits (with reference anchor used),
   remaining [verify] items, test status.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 14.0 tree (or the
  mapping tables, which cite their source). Unverifiable ids stay flagged,
  never silently "completed".
- **`ir.actions.*` direct access is removed** — read action dicts with
  `_for_xml_id('module.action_id')`; operate records with `sudo()`; frontend via
  `/web/action/load`. This is a DIFFERENT object from the 15.0 `ir.model*`
  removal.
- **`invisible`/`readonly` dynamic expressions are rejected** (e.g.
  `state=='draft'`) — move them into `attrs` domain. Only `context.get('...')`
  direct queries stay inline. `attrs` itself is still valid in 14.0 (it is
  hard-rejected only in 16→17).
- **`_name_search` returns ids** (not `(id, name)` tuples).
- **`_compute_display_name` override is dead** — override `name_get` + `@api.depends`.
- **`force_company` is gone** — use `with_company(company)`.
- **`Char(size=...)` size is ignored** — drop it.
- **`selection_add` needs `ondelete`** for every added value.
- **TransientModel (wizard) needs an explicit ACL** in `security/ir.model.access.csv`.
- **There is NO `upgrade_code` codemod for 13→14** — `odoo/upgrade_code/` does
  not exist in 14.0. Do not run `odoo-bin upgrade_code --from 13.0`.
- **Do NOT migrate these in 13→14** (still valid in 14.0; belong to 14→15 or
  later): `ir.model*` access removal (14→15); `t-raw` removal / assets-in-manifest
  (14→15); `SavepointCase`/`Environment.manage` removal (14→15); `attrs`/`states`
  hard-reject (16→17); `<tree>`→`<list>` (17→18); `name_get` removal (17→18);
  `payment.acquirer`→`payment.provider` (15→16).
- **Security file & `res.groups` are UNCHANGED in 13→14** (except wizard ACLs);
  do not apply the 18→19 `res.groups` privilege or 19→20 `ir.access.csv`
  conversions.
- When copying a value from a clipped/secondary source, verify it against the
  14.0 tree before committing.
