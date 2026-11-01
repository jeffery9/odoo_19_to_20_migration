---
name: odoo_12_to_13_migration
description: Migrates custom Odoo 12.0 addons to 13.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 12 to 13, fix 13.0 hard breaks (account.invoice/account.voucher merged into account.move with move_type, @api.multi/@api.returns/@api.cr/@api.model_cr decorators removed, res.partner customer/supplier booleans -> customer_rank/supplier_rank, ir.actions.act_window multi -> binding_view_types and src_model -> binding_model_id, dp.get_precision -> digits, track_visibility -> tracking, oldname removed, stock.quant qty -> quantity, product.product name now related, account.tax type -> type_tax_use, Binary defaults to attachment, sudo(user) -> with_user, .env.user.company_id -> .env.company), or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 12-only APIs. Note 13.0 has NO upgrade_code codemod — all fixes are manual; DB changes handled by OpenUpgrade. Also covers 12-to-13 accounting model changes (account.invoice and account.voucher merged into account.move, account.invoice.line into account.move.line, partner customer and supplier booleans replaced by customer_rank and supplier_rank).
version: 13.0.1
author: Independent (companion to the Odoo Migration Cookbook series)
category: migration
odoo_versions: ["12.0", "13.0"]
tags: [odoo, migration, upgrade, account-move, api-multi, customer-rank, binding-model, dp-precision, track-visibility, oldname, codemod, upgrade_code]
---

# Odoo 12 → 13 Migration

## Goal

Take a 12.0 custom addon (or a whole addons tree) to 13.0 with no leftover
12-only API, using **verified manual mappings** (there is **no** `upgrade_code`
codemod for 12→13 — the tooling ships in 18.0). Database-level changes
(account.move data migration, oldname renames, Binary attachment) are applied by
**OpenUpgrade** / the official upgrade service; this skill covers the
**code-level** mappings a custom module must make.

> **Scope note.** This skill covers the **12.0 → 13.0** jump only. The 13→14
> skill (`Odoo13to14Migration/`) handles the next step (invisible/readonly
> dynamic-expression → attrs, _name_search returns ids, force_company removed,
> ir.actions.* access via sudo, selection_add ondelete). Many items that changed
> *after* 13.0 are listed here ONLY where they are explicitly out of 12→13 scope.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables for the
  12→13 jump. Primary anchors:
  - `OCA Migration to version 13.0` (maintainer-tools wiki) — authoritative
    change list (decorator removal, track_visibility→tracking, oldname removal,
    dp.get_precision→digits, multi→binding_view_types, sudo(user)→with_user,
    .env.user.company_id→.env.company, multi-company rule form, hr.employee.base).
  - Odoo "accounting-pocalypse" commit notes — account.invoice/account.voucher
    merged into account.move/account.move.line (field & method mapping).
  - shine-it《如何升级到odoo13》/ Oodles —— Binary default-to-attachment, FA
    icon renames, jQuery Promise→native Promise, --upgrade-path CLI.
- Items tagged **[verify]** come from a single community source or sources that
  disagree (frontend FA/JQuery specifics) — confirm before relying on them.
  `[EE-verify]` items are Enterprise-only.

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 13.0 replacement, and notes every item is `manual`
   (no codemod exists for 12→13).
2. **Manual mappings** — for every finding, apply the replacement from the
   matching reference file:
   - decorators / with_user / multi-company / .env.company / hr.employee.base →
     `references/orm-api.md`
   - account.move rewrite / customer_rank / account.tax →
     `references/accounting-models.md`
   - view_type removal / binding_view_types / frontend →
     `references/views-qweb.md`
   - dp.get_precision / track_visibility / oldname / stock.quant / product.product /
     Binary → `references/models-mapping.md`
   - security file & `res.groups` (unchanged in 12→13) → `references/security.md`
   - codemod status & `migrations/13.0/` scripts → `references/upgrade-code.md`
     (also covers HTTP/mail unchanged).
3. **Data migrations** — put custom DB/structure fixes in each module's
   `migrations/13.0/` (`pre-`/`post-`/`end-` scripts, e.g. account.move data
   move, oldname renames, Binary attachment). There is no `upgrade_code` run.
4. **Validate** — re-run the scanner (expect 0 findings), then
   `odoo-bin -u <module> --test-tags /<module>` in a 13.0 sandbox; fix
   `ImportError`/`AttributeError` (`account.invoice`, `@api.multi`) first.
   Start with `--dev=all` and clear every `DeprecationWarning`.
5. **Report** — summarize per addon: manual edits (with reference anchor used),
   remaining [verify] items, test status.

## Model changes (core business models)

The accounting rupture. Ten source-verified changes; all must be handled.

| Check | 12.0 | 13.0 | Action |
|---|---|---|---|
| `account.invoice` | model | → `account.move` | Use `move_type` (`out_invoice`/`in_invoice`/`out_refund`/`in_refund`/`out_receipt`/`in_receipt`) to distinguish; `is_invoice()` helper |
| `account.invoice.line` | model | → `account.move.line` | `invoice_id` → `move_id`; tax lines folded into the same model, identified by `tax_line_id` |
| `account.voucher` | model | merged into `account.move` | Becomes `*_receipt` move types |
| `account.invoice.confirm` / `.refund` wizards | models | → methods | `account.move.post()` / `account.move.reversal()` |
| `account.move.amount` | field | → `amount_total` | Rename everywhere incl. reports |
| `account.move.reverse_entry_id` | field | → `reversed_entry_id` | Rename |
| `res.partner.customer` / `supplier` | booleans | → `customer_rank` / `supplier_rank` (int) | Domains become `('customer_rank','>',0)`; ranks accumulate |
| `hr.employee` | model | split: inherits `hr.employee.base` | Keep inheriting `hr.employee`; only touch `hr.employee.base` if you extend the base |
| `product.product.name` | stored | related to template | Writes go to the template |
| `account.tax.type` → `type_tax_use` | — | `[verify]` | Source does not support this rename (`type_tax_use` exists since v9). Do not apply blindly |

Cross-version model index: `Core_Models_Changelog.md`.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 13.0 tree (or the
  mapping tables, which cite their source). Unverifiable ids stay flagged,
  never silently "completed".
- **Accounting rewrite is the headline breaking change.** `account.invoice`,
  `account.invoice.line`, `account.invoice.tax`, `account.voucher`,
  `account.voucher.line` are GONE. Use `account.move` with `move_type`
  (out_invoice/in_invoice/out_refund/in_refund/out_receipt/in_receipt) and
  `account.move.line`. `action_invoice_open()` → `account.move.post()`.
- **`@api.multi` / `@api.returns` / `@api.cr` / `@api.model_cr` removed** — drop
  them; methods are multi by default. Non-stored computed fields must assign a
  value in every branch.
- **`res.partner` `customer`/`supplier` booleans → `customer_rank`/`supplier_rank`
  integers**; membership domain becomes `('customer_rank','>',0)`.
- **`ir.actions.act_window` `multi` → `binding_view_types`**; `src_model` →
  `binding_model_id` (13.0 still reads src_model, but prefer binding_model_id).
- **`dp.get_precision("X")` → `digits="X"`**; **`track_visibility=` →
  `tracking=True`** (first appeared in 13.0, not 15→16); **`oldname=` removed**
  (use openupgradelib rename_fields in migrations).
- **`sudo(user)` → `with_user(user)`**; **`.env.user.company_id` → `.env.company`**.
- **`stock.quant.qty` → `quantity`**; **`product.product.name` is now related to
  the template** (write `product_template_id.name`, not the variant);
  **`account.tax.type` → `type_tax_use`**; **`Binary` now defaults to attachment**.
- **There is NO `upgrade_code` codemod for 12→13** — `odoo/upgrade_code/` does
  not exist in 13.0. Do not tell the user to run `odoo-bin upgrade_code
  --from 12.0`; all code renames are manual, DB changes are OpenUpgrade's job.
- **Do NOT migrate these in 12→13** (they are still valid in 13.0; their
  removal/rename belongs to 13→14 or later): `ir.actions.*` direct read
  (13→14); `attrs`/`states` hard-reject (16→17); `<tree>`→`<list>` (17→18);
  `name_get` removal (17→18); `ir.model*` access removal (14→15); `t-raw`
  removal / assets-in-manifest (14→15); `payment.acquirer`→`payment.provider`
  (15→16); `coupon`→`loyalty` (15→16).
- **Security file & `res.groups` are UNCHANGED in 12→13.** Keep
  `security/ir.model.access.csv`; do not apply the 18→19 `res.groups` privilege
  or 19→20 `ir.access.csv` conversions.
- When copying a value from a clipped/secondary source, verify it against the
  13.0 tree before committing.
