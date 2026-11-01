---
name: odoo_14_to_15_migration
description: Migrates custom Odoo 14.0 addons to 15.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 14 to 15, fix 15.0 breaking changes (QWeb t-raw deprecated in favour of t-out which HTML-escapes by default unless the value is a Markup instance, ir.model.data public lookups renamed to _xmlid_lookup/_xmlid_to_res_id while _get_id and get_object_reference are removed, mail.template Jinja replaced by QWeb body declared via render_engine plus inline_template {{ }} for subject, ES modules /** @odoo-module **/ renamed *.esm.js, JS/SCSS assets moved from XML templates into the __manifest__.py assets key with the qweb key silently ignored, SavepointCase merged into TransactionCase changing transaction semantics, Environment.manage() turned into a no-op), or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 14-only APIs. Note 15.0 has NO upgrade_code codemod — all fixes are manual; DB changes are handled by OpenUpgrade. Also covers 14-to-15 model changes (stock.inventory removed in favour of stock.quant counting, journal payment methods become account.payment.method.line records, amount_by_group replaced by tax_totals_json, tax_exigible moved to account.move.always_tax_exigible, product.template.lst_price removed, detailed_type added, hr.leave gains multi-employee and overtime deduction, mail.moderation removed, note/narration/description become Html, ir.asset and res.users.settings added).
version: 15.0.2
author: Independent (companion to the Odoo Migration Cookbook series)
category: migration
odoo_versions: ["14.0", "15.0"]
tags: [odoo, migration, upgrade, t-out, ir-model-data, jinja-qweb, esm-js, assets-manifest, savepoint-case, payment-method-line, stock-inventory, codemod, upgrade_code]
---

# Odoo 14 → 15 Migration

## Goal

Take a 14.0 custom addon (or a whole addons tree) to 15.0 with no leftover
14-only API, using **source-verified mappings** (there is **no** `upgrade_code`
codemod for 14→15 — the tooling ships in 18.0). Database-level changes are
applied by **OpenUpgrade** / the official upgrade service; this skill covers the
**code-level** mappings a custom module must make.

> **Scope note.** This skill covers the **14.0 → 15.0** jump only. The 15→16
> skill (`Odoo15to16Migration/`) handles the next step (payment.acquirer ->
> payment.provider, coupon -> loyalty, stock.production.lot -> stock.lot,
> ir_translation -> JSONB). Items that changed *after* 15.0 are listed here
> ONLY where they are explicitly out of 14→15 scope.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables for the
  14→15 jump: `views-qweb.md`, `orm-api.md`, `http-rpc-mail.md`,
  `models-mapping.md`, `security.md`, `upgrade-code.md`.
- **Ground truth is the Odoo CE 14.0 / 15.0 source tree**, not community blog
  posts. Everything in this skill was re-checked with `git show` plus
  model-set / field-level diff. The OCA "Migration to version 15.0" guide was
  used as a lead only: its "removed" wording is wrong for several items —
  `t-raw`, `t-esc`, `SavepointCase` and `Environment.manage()` are **deprecated
  in 15.0**, not removed.
- Do not trust the widely repeated claims that 15.0 "removed ir.model*
  access" or that `subtype` -> `subtype_xmlid` is a 14→15 change. Both were
  disproved against source; see the cookbook's 9.3 counter-example table.

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers and the 15.0 replacement.
2. **Manual mappings** — for every finding, apply the replacement from the
   matching reference file:
   - t-out / t-esc / esm.js / assets manifest → `references/views-qweb.md`
   - SavepointCase / Environment.manage / ir.model.data lookups → `references/orm-api.md`
   - manifest assets key / field-type map → `references/models-mapping.md`
   - Jinja->QWeb mail / render_engine / HTTP unchanged → `references/http-rpc-mail.md`
   - security file & `res.groups` (unchanged) → `references/security.md`
   - codemod status & `migrations/15.0/` scripts → `references/upgrade-code.md`
3. **Data migrations** — put custom DB/structure fixes in each module's
   `migrations/15.0/` (`pre-`/`post-`/`end-` scripts). There is no `upgrade_code` run.
4. **Validate** — re-run the scanner (expect 0 findings), then
   `odoo-bin -u <module> --test-tags /<module>` in a 15.0 sandbox with `--dev=all`.
   **Deprecation warnings only appear with `--dev=all`**, and `t-raw` will NOT
   fail at load — do not rely on runtime errors to detect leftovers. Asset
   problems are silent too: confirm in the browser that the bundle actually
   contains your files.
5. **Report** — summarize per addon: manual edits (with reference anchor used),
   remaining uncertainties, test status, and anything that needed manual
   visual confirmation (assets, rich-text widgets).

## Model changes (core business models)

### Framework and data-access layer

| Check | 14.0 | 15.0 | Action |
|---|---|---|---|
| `t-raw` / `t-esc` | standard directives | **deprecated** (renders + warns; removed in 16.0) | Replace with `t-out`. `t-out` escapes unless the value is `markupsafe.Markup`; `fields.Html` values are Markup, `Char`/`Text` are not — do not blindly copy `t-raw` to `t-out` |
| `ir.model.data` lookups | `xmlid_lookup`, `xmlid_to_res_id`, `_get_id(module, xml_id)`, `get_object_reference`, `get_object`, `xmlid_to_object` | `_xmlid_lookup`, `_xmlid_to_res_id`, `_xmlid_to_res_model_res_id`; the rest **removed** | Prefer `self.env.ref('module.xmlid')`. Else `_xmlid_to_res_id`. **Never "fix" with `_get_id` — it was removed in 15.0** |
| `mail.template` engine | `engine='jinja'` default, plain Html body | `engine='inline_template'` default; `body_html` declares `render_engine='qweb'`; `engine='jinja'` raises `ValueError` | `${ }` → `{{ }}` in subject/email_from; QWeb `t-out` in body. XML uses `type="html"`; `type="qweb"` does not exist |
| manifest assets | `assets` key unused, `qweb` key in 77 modules | `assets` in 179 modules; `qweb` key **silently ignored** | Move all JS/SCSS/QWeb xml into `assets`; the old `assets_backend` template inheritance no longer works |
| test base class | `SavepointCase(SingleTransactionCase)` | `SavepointCase(TransactionCase)` deprecated alias | Switch to `TransactionCase`. Semantics changed: per-method transaction, no class-level savepoint |
| `Environment.manage()` | context manager | warns and yields (no-op) | Delete it |

### Core business models

| Check | 14.0 | 15.0 | Action |
|---|---|---|---|
| `stock.inventory` / `stock.inventory.line` | models | **removed** | Counting moves onto `stock.quant` (`inventory_quantity`, `inventory_quantity_set`, `inventory_diff_quantity`, `inventory_date`) with `stock.inventory.adjustment.name` naming each batch. Rewrite `env['stock.inventory']` → `env['stock.quant']` + `action_apply_inventory()`; export historical counts first |
| `account.journal.*_payment_method_ids` | many2many to `account.payment.method` | `*_payment_method_line_ids` one2many to new `account.payment.method.line` | Rewrite code/views; each line can own `payment_account_id` and `sequence` |
| `account.move.amount_by_group` / `sale.order.amount_by_group` | Binary | **removed** → `tax_totals_json` | Templates reading the tax-group breakdown break; use the `tax_totals` widget |
| `account.move.line.tax_exigible` | Boolean | **removed** → `account.move.always_tax_exigible` | Move tax-exigibility logic from line to move. `tax_fiscal_country_id` also removed → `account.move.tax_country_id` |
| `product.template.lst_price` | field on template | **removed** (only `product.product.lst_price`) | Use `product_variant_id.lst_price` |
| `product.template.detailed_type` | absent | **added** (`consu`/`product`/`service`) | Parallel field; `type` still exists. If target ≥18.0 write `is_storable` instead — `detailed_type` is removed again in 18.0 |
| `hr.leave` | one employee per leave | `employee_ids` m2m + `multi_employee`, `overtime_id`/`overtime_deductible`, `attachment_ids`; `payslip_status` removed | Re-check approval code that assumes a single `employee_id` |
| `mail.moderation` + `mail.message.moderation_status`/`moderator_id`/`need_moderation`/`channel_ids` | present | **removed** | Delete reads; `reaction_ids` and `author_guest_id` are the new neighbours |
| `phone.validation.mixin` | mixin | **removed** | Call `phone_validation` helpers instead of inheriting |
| `note`/`narration`/`description`/`comment` | Text | **Html** | Review widgets and any plain-text assumption (`strip_tags`, newline splitting) |
| `ir.asset`, `res.users.settings`, `crm.team.member`, `stock.storage.category`/`.capacity`, `stock.package.type` | absent | **added** | Prefer the standard models over custom tables |

The inventory change is a **working-model shift**, not a table swap: "open a
count document → enter quantities → validate" becomes "edit quants → apply in
bulk". Update SOPs and training, not just code.

Cross-version model index: `Core_Models_Changelog.md`.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 15.0 tree (or the
  mapping tables, which cite their source). Unverifiable ids stay flagged,
  never silently "completed".
- **`t-raw` is deprecated, not removed** (it is removed in 16.0). Replace with
  `t-out`, but remember **`t-out` escapes by default** — only `Markup` values
  render as HTML. Wrap trusted server HTML in `markupsafe.Markup`.
- **`ir.model.data` lookups were renamed/removed** — use `self.env.ref()` or
  `_xmlid_to_res_id` / `_xmlid_to_res_model_res_id`. `_get_id(module, xml_id)`,
  `get_object_reference` and `get_object` do not exist in 15.0.
  This is a DIFFERENT change from the 13→14 `ir.actions.*` tightening.
- **Mail templates: Jinja is gone** — body is QWeb (declared by
  `render_engine='qweb'` on the field), subject/email_from/email_to use
  inline_template with `{{ }}`. `engine='jinja'` raises `ValueError`.
- **ES modules must be renamed `*.esm.js`** (any file with `/** @odoo-module **/`).
- **Assets move into `__manifest__.py` `assets` key**; the `qweb` manifest key is
  ignored (no error), `web.assets_backend` is no longer an inheritable QWeb view.
- **`SavepointCase` is a deprecated alias whose base class changed** — switch to
  `TransactionCase` and re-check tests that relied on class-level state.
- **`Environment.manage()` is a no-op** — delete it.
- **There is NO `upgrade_code` codemod for 14→15** — `odoo/upgrade_code/` does
  not exist in 15.0. Do not run `odoo-bin upgrade_code --from 14.0`.
- **Do NOT migrate these in 14→15** (still valid in 15.0; belong to another pair):
  `payment.acquirer`->`payment.provider` (15→16); `coupon`->`loyalty` (15→16);
  `stock.production.lot`->`stock.lot` (15→16); `ir_translation`->JSONB (15→16);
  `attrs`/`states` hard-reject (16→17); `get_resource_path`->`file_path` (16→17);
  `<tree>`->`<list>` (17→18); `name_get` removal (17→18);
  `track_visibility`->`tracking` (12→13); `subtype`->`subtype_xmlid` (13→14).
- **Security file & `res.groups` are UNCHANGED in 14→15**; do not apply the
  18→19 `res.groups` privilege or 19→20 `ir.access.csv` conversions.
- When copying a value from a clipped/secondary source, verify it against the
  15.0 tree before committing.
