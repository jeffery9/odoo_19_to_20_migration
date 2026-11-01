---
name: odoo_15_to_16_migration
description: Migrates custom Odoo 15.0 addons to 16.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 15 to 16, fix 16.0 hard breaks (payment.acquirer->payment.provider and acquirer_id/provider_reference/_handle_feedback_data renames, coupon->loyalty model renames, stock.production.lot->stock.lot / account_analytic.group->account_analytic.plan / mail.channel.partner->mail.channel.member / account.tax.report->account.report renames, ir_translation table removed, track_visibility->tracking, api.multi removed), or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 15-only APIs. Note 16.0 has NO upgrade_code codemod — all fixes are manual; DB renames are handled by OpenUpgrade. Also covers 15-to-16 model changes (stock.production.lot renamed stock.lot, payment.acquirer renamed payment.provider, coupon models renamed loyalty, account.analytic.account group_id renamed plan_id).
version: 16.0.1
author: Independent (companion to the Odoo Migration Cookbook series)
category: migration
odoo_versions: ["15.0", "16.0"]
tags: [odoo, migration, upgrade, payment, loyalty, models, orm, ir_translation, codemod, upgrade_code]
---

# Odoo 15 → 16 Migration

## Goal

Take a 15.0 custom addon (or a whole addons tree) to 16.0 with no leftover
15-only API, using **verified manual mappings** (there is **no** `upgrade_code`
codemod for 15→16 — the tooling ships in 18.0). Database-level renames
(models/fields/modules, `ir_translation`→JSONB, module merges) are applied by
**OpenUpgrade** / the official upgrade service; this skill covers the
**code-level** mappings a custom module must make.

> **Scope note.** This skill covers the **15.0 → 16.0** jump only. The 16→17
> skill (`Odoo16to17Migration/`) handles the next step (attrs/states hard-rejected,
> tree still valid, get_resource_path→file_path, hooks env arg). Many items that
> changed *after* 16.0 (attrs/states removal in 17, tree→list in 18, ORM split in
> 19) are listed here ONLY where they are explicitly out of 15→16 scope — see the
> red lines below.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables for the
  15→16 jump. Primary anchors:
  - OCU (Odoo Community Upgrade)《Migrate Odoo 15 to 16》structural diff
    (14 model renames, 23 module merges, 42 field renames, 138 constraint changes;
    `payment.acquirer`→`payment.provider`, `coupon`→`loyalty`, `ir_translation`
    removed, `stock.production.lot`→`stock.lot`, `account_analytic.group`→
    `account_analytic.plan`, `mail.channel.partner`→`mail.channel.member`,
    `account.tax.report`→`account.report`, `account_payment` auto-install).
  - oejia《Odoo 16 关键变化》(payment field/method renames; GitHub docs PR #1981).
  - DeployMonkey《Migrate Odoo 15 to 16》(track_visibility→tracking, website
    routing, group_expand, record-rule global, legacy-widget→Owl 2).
  - GitHub `odoo/odoo` branch `16.0` source (verified `release.py` version_info
    (16,0,0); `ir_ui_view.py` still processes attrs/states (L82-96) and tree is a
    valid type (L237); `models.py` keeps name_get/user_has_groups/check_access_rights;
    `modules/module.py` keeps get_resource_path; `api.py` has NO api.multi;
    `odoo/upgrade_code/` is ABSENT).
- Items tagged **[EE-verify]** are Enterprise-only: re-check against the
  matching EE 16.0 tree before deployment. Items tagged **[verify]** come from
  a single community source or sources that disagree (website routing, record-rule
  global, t-raw, html sanitize) — confirm before relying on them.

## Workflow

1. **DB migration** — run OpenUpgrade (community) or the official upgrade service
   (Enterprise) on a copy of the v15 database. This auto-renames models/fields/
   modules, migrates `ir_translation`→JSONB, merges modules, adds constraints.
2. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 16.0 replacement, and notes every item is `manual`
   (no codemod exists for 15→16).
3. **Manual mappings** — for every finding, apply the replacement from the
   matching reference file:
   - payment restructure + coupon→loyalty → `references/payment-loyalty.md`
   - other model/module renames + `ir_translation` → `references/models-mapping.md`
   - ORM & Python API (track_visibility, api.multi, website routing) → `references/orm-api.md`
   - views / QWeb (unchanged in 16; t-raw/html sanitize [verify]) → `references/views-qweb.md`
   - security file & `res.groups` (unchanged in 15→16) → `references/security.md`
   - codemod status & `migrations/16.0/` scripts → `references/upgrade-code.md`
4. **Data migrations** — put custom DB/structure fixes in each module's
   `migrations/16.0/` (`pre-`/`post-`/`end-` scripts). There is no
   `upgrade_code` run for 15→16.
5. **Validate** — re-run the scanner (expect 0 findings), then
   `odoo-bin -u <module> --test-tags /<module>` in a 16.0 sandbox; fix
   `Model not available` / `ImportError` (`api.multi`) / `TypeError` first.
   Start with `--dev=all` and clear every `DeprecationWarning`.
6. **Report** — summarize per addon: manual edits (with reference anchor used),
   remaining [EE-verify]/[verify] items, test status.

## Model changes (core business models)

| Check | 15.0 | 16.0 | Action |
|---|---|---|---|
| `stock.production.lot` | model | → `stock.lot` | Rename all references, XML-IDs and inheritance |
| `payment.acquirer` | model | → `payment.provider` | Also `acquirer_id`→`provider_id`, `acquirer_reference`→`provider_reference`, `_handle_feedback_data`→`_handle_notification_data` |
| `coupon` / `sale_coupon` | models + modules | → `loyalty` / `sale_loyalty` | `coupon.program`→`loyalty.program`, `coupon.reward`→`loyalty.reward`, `coupon.rule`→`loyalty.rule`, `coupon.coupon`→`loyalty.card`; update `depends` too |
| `account.analytic.account.group_id` | `group_id` | → `plan_id` | Field rename (module also renamed `account_analytic.group`→`account_analytic.plan`). **This is 15→16, not 19→20.** Check `account.analytic.line` references as well |

Cross-version model index: `Core_Models_Changelog.md`.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 16.0 tree (or the
  mapping tables, which cite their source). Unverifiable ids stay flagged,
  never silently "completed".
- **`payment.acquirer` → `payment.provider` is the headline breaking change.**
  Rename the model, the fields (`acquirer_id`→`provider_id`,
  `acquirer_reference`→`provider_reference`, `acquirer_ref`→`provider_ref`), the
  connector method (`_handle_feedback_data`→`_handle_notification_data`), and the
  xmlid prefix (`payment_acquirer_*`→`payment_provider_*`).
- **`coupon` → `loyalty`** — rename `coupon.program/reward/rule/coupon` to
  `loyalty.program/reward/rule/card` and module `depends` accordingly.
- **`ir_translation` table is removed in 16.0** — translations are JSONB columns.
  Rewrite any code that directly reads/writes `ir_translation`.
- **There is NO `upgrade_code` codemod for 15→16** — `odoo/upgrade_code/` does
  not exist in 16.0. Do not tell the user to run `odoo-bin upgrade_code
  --from 15.0`; DB renames are OpenUpgrade's job, code renames are manual.
- **Views are almost unchanged in 15→16.** `attrs`/`states` and `<tree>` are
  STILL valid (verified ir_ui_view.py L82-96 / L237). Do NOT rewrite attrs→inline
  expr, do NOT rename tree→list, do NOT use column_invisible — those are 16→17 /
  17→18 steps. Only `[verify]` items (t-raw, html sanitize) may apply.
- **Do NOT migrate these in 15→16** (they are still valid in 16.0; their
  removal/rename belongs to 16→17 or later): `name_get` / `_name_search` /
  `check_access_rights` / `user_has_groups` / `check_recursion` (removed only in
  18); `get_resource_path` (removed only in 17); `attrs`/`states` (rejected only
  in 17); `<tree>`→`<list>` (only in 18); `web_editor` (split only in 19).
- **Security file & `res.groups` are UNCHANGED in 15→16.** Keep
  `security/ir.model.access.csv` with `perm_*` columns; do not apply the
  19→20 `ir.access.csv`/`privilege_id` conversion.
- Python 3.8/3.9/3.10 are all supported (no Python floor change from 15) — but
  confirm the runtime and dependencies (Werkzeug 2.x) before migrating.
- When copying a value from a clipped/secondary source, verify it against the
  16.0 tree before committing.
