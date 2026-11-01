---
name: odoo_14_to_15_migration
description: Migrates custom Odoo 14.0 addons to 15.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 14 to 15, fix 15.0 hard breaks (QWeb t-raw removed -> use t-out/t-esc + markupsafe.Markup, ir.model*/ir.model.fields/ir.model.data direct access removed -> use sudo or model APIs, mail.template Jinja syntax replaced by QWeb body + inline_template {{ }} for subject/email_from/email_to, ES modules /** @odoo-module **/ must be renamed *.esm.js, JS/SCSS assets moved from XML templates into __manifest__.py assets key (qweb key removed), SavepointCase alias removed -> TransactionCase, Environment.manage() no longer needed, subtype -> subtype_xmlid [verify]), or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 14-only APIs. Note 15.0 has NO upgrade_code codemod — all fixes are manual; DB changes handled by OpenUpgrade. Also covers 14-to-15 model changes (stock.inventory and stock.inventory.line removed in favour of stock.quant counting, product.template.detailed_type added, project.milestone and project.update added).
version: 15.0.1
author: Independent (companion to the Odoo Migration Cookbook series)
category: migration
odoo_versions: ["14.0", "15.0"]
tags: [odoo, migration, upgrade, t-raw, ir-model, jinja-qweb, esm-js, assets-manifest, savepoint-case, codemod, upgrade_code]
---

# Odoo 14 → 15 Migration

## Goal

Take a 14.0 custom addon (or a whole addons tree) to 15.0 with no leftover
14-only API, using **verified manual mappings** (there is **no** `upgrade_code`
codemod for 14→15 — the tooling ships in 18.0). Database-level changes are
applied by **OpenUpgrade** / the official upgrade service; this skill covers the
**code-level** mappings a custom module must make.

> **Scope note.** This skill covers the **14.0 → 15.0** jump only. The 15→16
> skill (`Odoo15to16Migration/`) handles the next step (payment.acquirer ->
> payment.provider, coupon -> loyalty, stock.production.lot -> stock.lot,
> ir_translation -> JSONB, track_visibility -> tracking [no, that is 12->13],
> api.multi removal). Many items that changed *after* 15.0 are listed here
> ONLY where they are explicitly out of 14→15 scope.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables for the
  14→15 jump. Primary anchors:
  - `OCA Migration to version 15.0` (maintainer-tools wiki) — authoritative
    change list (t-raw -> t-out/t-esc + markupsafe.Markup, ir.model* access
    removal #69120, Jinja -> QWeb/inline_template #77074, .esm.js rename, assets
    into manifest assets key / qweb key removed, SavepointCase -> TransactionCase
    #62031, Environment.manage() removal).
  - odoo/odoo commits 01875541b1a8 (t-raw), #69120 (ir.model*), #77074 (Jinja),
    #62031 (SavepointCase).
- Items tagged **[verify]** come from a single community source or sources that
  disagree (subtype -> subtype_xmlid) — confirm before relying on them.
  `[EE-verify]` items are Enterprise-only.

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 15.0 replacement, and notes every item is `manual`.
2. **Manual mappings** — for every finding, apply the replacement from the
   matching reference file:
   - t-raw / esm.js / assets manifest / ir.model* access → `references/views-qweb.md`
   - SavepointCase / Environment.manage / ir.model* access → `references/orm-api.md`
   - t-out/t-esc cheat / manifest assets key → `references/models-mapping.md`
   - Jinja->QWeb mail / subtype -> subtype_xmlid / HTTP unchanged →
     `references/http-rpc-mail.md`
   - security file & `res.groups` (unchanged) → `references/security.md`
   - codemod status & `migrations/15.0/` scripts → `references/upgrade-code.md`
3. **Data migrations** — put custom DB/structure fixes in each module's
   `migrations/15.0/` (`pre-`/`post-`/`end-` scripts). There is no `upgrade_code`
   run.
4. **Validate** — re-run the scanner (expect 0 findings), then
   `odoo-bin -u <module> --test-tags /<module>` in a 15.0 sandbox with `--dev=all`
   (QWeb will reject `t-raw` at load; SavepointCase/Environment.manage raise
   DeprecationWarning). Fix `ImportError`/`AttributeError` first.
5. **Report** — summarize per addon: manual edits (with reference anchor used),
   remaining [verify] items, test status.

## Model changes (core business models)

| Check | 14.0 | 15.0 | Action |
|---|---|---|---|
| `stock.inventory` / `stock.inventory.line` | models | **removed** | Counting moves onto `stock.quant` (`inventory_quantity`) with `stock.inventory.adjustment.name` naming each batch. Rewrite `env['stock.inventory']` → `env['stock.quant']` + `action_apply_inventory()`; export historical counts before upgrading |
| `product.template.detailed_type` | absent | **added** (`consu`/`product`/`service`) | New parallel field; `type` still exists. If the migration target is ≥18.0, write `is_storable` instead — `detailed_type` is removed again in 18.0 |
| `project.milestone` / `project.update` | absent | **added** | Project domain grows beyond tasks; evaluate replacing custom milestone models |

The inventory change is a **working-model shift**, not a table swap: "open a
count document → enter quantities → validate" becomes "edit quants → apply in
bulk". Update SOPs and training, not just code.

Cross-version model index: `Core_Models_Changelog.md`.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 15.0 tree (or the
  mapping tables, which cite their source). Unverifiable ids stay flagged,
  never silently "completed".
- **`t-raw` is removed** — use `t-out` (no escape, equals old t-raw) or `t-esc`
  (HTML-escape). Wrap trusted server HTML in `markupsafe.Markup` for `t-out`.
- **`ir.model*` direct access is removed** (`ir.model`, `ir.model.fields`,
  `ir.model.data`) — use `sudo()` or the model's own API (`_fields`,
  `_xmlid_lookup`, `_get_id`). This is a DIFFERENT object from the 13→14
  `ir.actions.*` removal.
- **Mail templates: Jinja is gone** — body_html becomes QWeb (`type="qweb"`,
  use `t-out`/`t-esc`); subject/email_from/email_to use inline_template with
  `{{ }}` instead of `${ }`.
- **ES modules must be renamed `*.esm.js`** (any file with `/** @odoo-module **/`).
- **Assets move into `__manifest__.py` `assets` key**; the `qweb` manifest key is
  removed; QWeb `.xml` links go into `web.assets_qweb`; paths are repo-relative.
- **`SavepointCase` alias removed** — use `TransactionCase`.
- **`Environment.manage()` is gone** — create `Environment(...)` directly.
- **There is NO `upgrade_code` codemod for 14→15** — `odoo/upgrade_code/` does
  not exist in 15.0. Do not run `odoo-bin upgrade_code --from 14.0`.
- **Do NOT migrate these in 14→15** (still valid in 15.0; belong to 15→16 or
  later): `payment.acquirer`->`payment.provider` (15→16); `coupon`->`loyalty`
  (15→16); `stock.production.lot`->`stock.lot` (15→16); `ir_translation`->JSONB
  (15→16); `attrs`/`states` hard-reject (16→17); `get_resource_path`->`file_path`
  (16→17); `<tree>`->`<list>` (17→18); `name_get` removal (17→18); `track_visibility`->`tracking`
  (12→13).
- **Security file & `res.groups` are UNCHANGED in 14→15**; do not apply the
  18→19 `res.groups` privilege or 19→20 `ir.access.csv` conversions.
- When copying a value from a clipped/secondary source, verify it against the
  15.0 tree before committing.
