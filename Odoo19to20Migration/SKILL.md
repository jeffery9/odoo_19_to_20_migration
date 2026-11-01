---
name: odoo_19_to_20_migration
description: Migrates custom Odoo 19.0 addons to 20.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 19 to 20, fix 20.0 deprecations (ir.access.csv, models.Constraint, check_access/has_access, _has_cycle, read_group signature, aggregator, Domain.custom, owl3 t-call order, route jsonrpc, ormcache), run or extend odoo-bin upgrade_code codemods, or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 19-only APIs. Also covers 19-to-20 model changes (stock.scrap removed in favour of stock.move is_scrap, hr.leave.type and payment.provider and mail.thread.cc removed, account.group folded into account.account hierarchy, res.bank merged into res.partner.bank, product_uom renamed uom_id, ir.attachment.datas removed, res.partner company_registry replaced by additional_identifiers).
version: 20.0.1
author: Independent (companion to the Odoo Migration Cookbook I & II)
category: migration
odoo_versions: ["19.0", "20.0"]
tags: [odoo, migration, upgrade, orm, security, views, qweb, owl, testing, codemod, upgrade_code]
---

# Odoo 19 → 20 Migration

## Goal

Take a 19.0 custom addon (or a whole addons tree) to 20.0 with no leftover
19-only API, using automated codemods first and verified manual mappings second.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables from the
  companion cookbooks (Volume I fixed edition + Volume II "Closing the Gaps").
- Upstream trees: github.com/odoo/odoo branches `19.0` and `20.0`.
- Bundled codemods: `odoo/upgrade_code/` + `odoo-bin upgrade_code` (see
  `references/upgrade-code.md`).
- Items tagged **[EE-verify]** are Enterprise-only: they MUST be re-checked
  against the matching Enterprise 20.0 tree before deployment; never present
  them as verified.

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 20.0 replacement, and whether a bundled codemod fixes it.
2. **Codemod first** — on a clean git branch:
   `odoo-bin upgrade_code --from 19.0 --addons-path /path/to/addons --dry-run`,
   then the real run; review `git diff` file by file and commit.
   Codemods rewrite SOURCE only; data upgrades stay in module migrations.
3. **Manual mappings** — for everything the scanner flags as `manual`, apply
   the replacement from the matching reference file:
   - security file & ORM renames → `references/security-and-orm.md`
   - binary/excel/pdf/time, HTTP routes, mail/server actions → `references/binary-http-mail.md`
   - view xpaths, ribbons/icons, kanban cards, QWeb & Owl 3 → `references/views-qweb-owl.md`
   - model/field/xml-id maps per business module → `references/modules-mapping.md`
   - runtime/imports, cache & SQL, model-API deltas, fields/domains, tests → `references/api-deltas-vol2.md`
   - codemod usage & how to write your own scripts → `references/upgrade-code.md`
4. **Validate** — re-run the scanner (expect 0 findings), then:
   `odoo-bin -u <module> --test-tags /<module>` in a 20.0 sandbox; fix view
   validation errors (RNG) and domain `TypeError`s last, they are the loudest.
5. **Report** — summarize per addon: codemod changes, manual edits (with the
   reference anchor used), remaining [EE-verify] items, test status.

## Model changes (core business models)

This is the pair where secondary sources are least reliable. Everything below
is source-verified against the 19.0/20.0 trees.

| Check | 19.0 | 20.0 | Action |
|---|---|---|---|
| `stock.scrap` | model | **removed** → `stock.move` with `is_scrap=True` | `is_scrap` is a **new** 20.0 boolean (on `stock.move`, `stock.move.line`, `stock.lot`) |
| `hr.leave.type` | model | **removed** | `hr.work.entry.type` is *not* a rename target (both exist in 19.0) |
| `hr.version.wizard` / `hr.contract.type` | models | **removed** | |
| EE `hr.payslip.input.type` | model | merged into `hr.salary.rule` | `hr.payslip.input` now hangs off `salary_rule_id`; `code`/`name`/`input_suffix`/`user_instructions` become related. `input_usage_payslip` is a pre-existing boolean, **not** a replacement model |
| `payment.provider` | model | **removed** | Payment stack rewritten; no field-level rename story |
| `mail.thread.cc` | mixin | **removed** | CC folded into standard `mail.thread` |
| `account.group` | model | merged into `account.account` hierarchy | `parent_id` + computed `parent_ids`; codemod `19.3-00-account-groups` |
| `res.bank` | model | merged into `res.partner.bank` | `bank_name`/`bank_bic` become stored fields |
| `product.template.attribute.exclusion` | model | **removed** | Use m2m `excluded_value_ids` on `product.template.attribute.value` |
| `stock.return.picking` | wizard | → `stock.picking._create_return()` | |
| `stock_picking_batch` | module | merged into `stock` | Model name unchanged — only `depends` moves |
| `stock.move.product_uom` | `product_uom` | → `uom_id` | |
| `stock.move.location_final_id` | field | → `forecasted_location_id` | |
| `res.partner.company_registry` | field | **removed** → `additional_identifiers` (JSON) | |
| `res.partner.company_type` | field | **removed** | Use boolean `is_company` |
| `ir.attachment.datas` | field | **removed** | `raw` has coexisted since 17.0 — this is a removal, not a rename |
| `sale.order.state` | `'done'` | that state removed | |
| `mrp.production.show_produce_all` | field | **removed** | Use `button_mark_done` |
| `product.template.is_storable` | defined in `stock` | **relocated** to `product` core | Not a new field; `type` Selection still exists in 20.0 |

**Do not repeat these errors** (all disproved by source): `hr.contract`→
`hr.version`, `hr.expense.sheet`→`hr.expense`, `stock.quant.package`→
`stock.package` and `groups_id`→`group_ids` are **18→19**;
`account.analytic.account.group_id`→`plan_id` is **15→16**; `crossovered.budget`→
`budget.analytic` is **17→18**; `note.note`→`project.task` never existed
(`note.note` is absent in 17/18/19/20); `project.task.user_id`→`user_ids` is
false (`user_ids` exists since 16.0).

Cross-version model index: `Core_Models_Changelog.md`.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 20.0 tree (or the
  mapping tables, which cite their source file). Unverifiable EE ids stay
  flagged, never silently "completed".
- `ir.model.access.csv` and `perm_*` columns are illegal in 20: the file is
  `security/ir.access.csv` with `operation` strings (`cru`, `c`, …) and rule
  domains merged in; `[(1,'=',1)]`-style domains must become empty.
- Never keep `type='json'` routes for web-client calls; external integrations
  keep using JSON-2 `/json/2/<model>/<method>` (still present in 20).
- Long xpaths/code in tables wrap instead of truncating: when you copy a value
  from a clipped source, verify it against the tree before committing.
