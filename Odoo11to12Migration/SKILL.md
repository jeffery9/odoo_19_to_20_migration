---
name: odoo_11_to_12_migration
description: Migrates custom Odoo 11.0 addons to 12.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 11 to 12, fix 12.0 hard breaks (@api.one decorator removed, fields.Date/Datetime runtime values become real date/datetime objects with from_string removed, @api.model_create_multi introduced, ir.actions.act_window.view model removed, do_notify/do_warning removed, t-field-options->t-options, parent_left/parent_right->parent_path), or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 11-only APIs. Note 12.0 has NO upgrade_code codemod — all fixes are manual; DB changes handled by OpenUpgrade. Also covers 11-to-12 model changes (ir.actions.act_window.view model removed, use view_ids or the views field on the action).
version: 12.0.1
author: Independent (companion to the Odoo Migration Cookbook series)
category: migration
odoo_versions: ["11.0", "12.0"]
tags: [odoo, migration, upgrade, api.one, date-object, model_create_multi, parent_path, act_window_view, codemod, upgrade_code]
---

# Odoo 11 → 12 Migration

## Goal

Take a 11.0 custom addon (or a whole addons tree) to 12.0 with no leftover
11-only API, using **verified manual mappings** (there is **no** `upgrade_code`
codemod for 11→12 — the tooling ships in 18.0). Database-level changes
(`parent_path` fill, etc.) are applied by **OpenUpgrade** / the official upgrade
service; this skill covers the **code-level** mappings a custom module must make.

> **Scope note.** This skill covers the **11.0 → 12.0** jump only. The 12→13
> skill (`Odoo12to13Migration/`) handles the next step (account.invoice→account.move,
> customer/supplier→customer_rank/supplier_rank, src_model→binding_model,
> stock.quant qty→quantity). Many items that changed *after* 12.0 are listed here
> ONLY where they are explicitly out of 11→12 scope — see the red lines below.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables for the
  11→12 jump. Primary anchors:
  - `OCA Migration to version 12.0` (maintainer-tools wiki) — authoritative
    change list (api.one removal, Date runtime object, parent_path, act_window.view
    removal, do_notify/do_warning removal, t-field-options→t-options).
  - 掘金《Odoo版本升级:Odoo11~Odoo16代码变更》—— Date 运行时对象化、
    `model_create_multi`、`parent_path` 实战说明。
  - CSDN Odoo 代码规范 —— `api.one`/`api.multi` 在 12 的弃用确认。
  - Oejia 技术栈 —— `api.one` 移除、视图属性兼容性。
  - Odoo 11.0 **already required Python 3** — so there is NO Python 2→3 break in
    11→12 (that was 10→11).
- Items tagged **[verify]** come from a single community source or sources that
  disagree (frontend Bootstrap/jQuery version bump, Binary default-to-attachment
  timing) — confirm before relying on them. `[EE-verify]` items are Enterprise-only.

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 12.0 replacement, and notes every item is `manual`
   (no codemod exists for 11→12).
2. **Manual mappings** — for every finding, apply the replacement from the
   matching reference file:
   - ORM & Python API (api.one, from_string, model_create_multi, parent_path,
     do_notify/do_warning) → `references/orm-api.md`
   - views / QWeb (act_window.view removal, t-field-options) → `references/views-qweb.md`
   - module/model/field mapping table → `references/models-mapping.md`
   - security file & `res.groups` (unchanged in 11→12) → `references/security.md`
   - HTTP/RPC/mail/binary (unchanged in 11→12) → `references/http-rpc-mail.md`
   - codemod status & `migrations/12.0/` scripts → `references/upgrade-code.md`
3. **Data migrations** — put custom DB/structure fixes in each module's
   `migrations/12.0/` (`pre-`/`post-`/`end-` scripts, e.g. `parent_path` fill).
   There is no `upgrade_code` run for 11→12.
4. **Validate** — re-run the scanner (expect 0 findings), then
   `odoo-bin -u <module> --test-tags /<module>` in a 12.0 sandbox; fix
   `ImportError` (`api.one`) / `AttributeError` (`from_string`) first.
   Start with `--dev=all` and clear every `DeprecationWarning`.
5. **Report** — summarize per addon: manual edits (with reference anchor used),
   remaining [verify] items, test status.

## Model changes (core business models)

| Check | 11.0 | 12.0 | Action |
|---|---|---|---|
| `ir.actions.act_window.view` model | present | **removed** | Per-view binding is gone. Declare `view_ids` (o2m) or the `views` field on the action instead |

The rest of this pair is API-level (`@api.one` removal, `fields.Date` becoming a
runtime object) and does not move models. Do not drag `account.invoice`→
`account.move` here — that is 12→13.

Cross-version model index: `Core_Models_Changelog.md`.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 12.0 tree (or the
  mapping tables, which cite their source). Unverifiable ids stay flagged,
  never silently "completed".
- **`@api.one` removal is the headline breaking change.** Remove the decorator
  and wrap the body in `for record in self:`; pure model methods use `@api.model`.
  `api.multi` still exists in 12.0 but is deprecated — prefer no decorator.
- **`fields.Date` / `fields.Datetime` runtime values are now real date/datetime
  objects.** `from_string` is removed → use `fields.Date.to_date` /
  `fields.Datetime.to_datetime`. Any string slicing/regex on date fields breaks.
- **`ir.actions.act_window.view` model is removed** — bind views via the action's
  `view_ids` (o2m) or `views`.
- **`do_notify` / `do_warning` are removed** → `raise UserError` / `message_post`.
- **`parent_left` / `parent_right` → `parent_path`** under `_parent_store`.
- **There is NO `upgrade_code` codemod for 11→12** — `odoo/upgrade_code/` does
  not exist in 12.0. Do not tell the user to run `odoo-bin upgrade_code
  --from 11.0`; all code renames are manual, DB changes are OpenUpgrade's job.
- **Do NOT migrate these in 11→12** (they are still valid in 12.0; their
  removal/rename belongs to 12→13 or later): `account.invoice`→`account.move`
  (12→13); `customer`/`supplier`→`customer_rank`/`supplier_rank` (12→13);
  `src_model`→`binding_model` (12→13); `attrs`/`states` hard-reject (16→17);
  `<tree>`→`<list>` (17→18); `name_get` removal (17→18); `get_resource_path`→
  `file_path` (16→17); `payment.acquirer`→`payment.provider` (15→16);
  `t-raw` removal / `ir.model*` removal / assets-in-manifest (14→15).
- **Security file & `res.groups` are UNCHANGED in 11→12.** Keep
  `security/ir.model.access.csv` with `perm_*` columns; do not apply the
  18→19 `res.groups` privilege or 19→20 `ir.access.csv` conversions.
- When copying a value from a clipped/secondary source, verify it against the
  12.0 tree before committing.
