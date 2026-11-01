---
name: odoo_18_to_19_migration
description: Migrates custom Odoo 18.0 addons to 19.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 18 to 19, fix 19.0 deprecations (odoo/orm package split, @api.returns removal, web_editor split into html_editor/html_builder, record._cr/_uid/_context deprecation, read_group→_read_group, type='json'→jsonrpc, odoo.osv deprecation, res.groups privilege model, Owl 3, module/model renames), run or extend odoo-bin upgrade_code codemods, or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 18-only APIs. Also covers 18-to-19 model changes (stock.quant.package renamed stock.package, hr.contract renamed hr.version, hr.expense.sheet merged into hr.expense, procurement.group and its group_id chain removed, product.packaging removed, res.users groups_id renamed group_ids, stock.reference added).
version: 19.0.1
author: Independent (companion to the Odoo Migration Cookbook I & II)
category: migration
odoo_versions: ["18.0", "19.0"]
tags: [odoo, migration, upgrade, orm, security, views, qweb, owl, testing, codemod, upgrade_code]
---

# Odoo 18 → 19 Migration

## Goal

Take an 18.0 custom addon (or a whole addons tree) to 19.0 with no leftover
18-only API, using automated codemods first and verified manual mappings second.

> **Scope note.** This skill covers the **18.0 → 19.0** jump only. The 19→20
> skill (`Odoo19to20Migration/`) handles the next step; do not mix their
> mappings. Many items already changed *before* 19 (e.g. `aggregator`
> rename in 17.2, `Domain` API in 18.1, `type='json'`→`jsonrpc` in 18.1,
> `check_access`/`has_access` in 18.0) are listed here only where they are
> still *relevant to cleaning up 18 code*, never as if they were new in 19.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables for the
  18→19 jump. Primary anchors:
  - Odoo ORM Changelog: `odoo.com/documentation/19.0/developer/reference/backend/orm/changelog.html`
    (PRs #193636, #217708, #163300, #183636, #170009, #175783, #179148, #174967).
  - Multiple community 18→19 upgrade write-ups, cross-checked against each other.
- Upstream trees: github.com/odoo/odoo branches `18.0` and `19.0`.
- Bundled codemods: `odoo/upgrade_code/` + `odoo-bin upgrade_code` (see
  `references/upgrade-code.md`).
- Items tagged **[EE-verify]** are Enterprise-only: they MUST be re-checked
  against the matching Enterprise 19.0 tree before deployment; never present
  them as verified. Items tagged **[verify]** are reported by community
  upgrade guides but not yet confirmed against the 19.0 source — confirm
  before relying on them.

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 19.0 replacement, and whether a bundled codemod fixes it.
2. **Codemod first** — on a clean git branch, from a **19.0** installation:
   `odoo-bin upgrade_code --from 18.0 --addons-path /path/to/addons --dry-run`,
   then the real run; review `git diff` file by file and commit.
   Codemods rewrite SOURCE only; data upgrades stay in module migrations.
   Note: 18→19 is lighter on codemods than 19→20 (the security-file format
   does **not** change in 18→19), so most fixes are manual.
3. **Manual mappings** — for everything the scanner flags as `manual`, apply
   the replacement from the matching reference file:
   - security file & res.groups / ORM renames → `references/security-and-orm.md`
   - binary/excel/pdf/time, HTTP routes, mail, SQL reports → `references/binary-http-mail.md`
   - view xpaths, Owl 3, kanban cards, QWeb → `references/views-qweb-owl.md`
   - module/model/field maps per business module → `references/modules-mapping.md`
   - runtime/imports, cache & SQL, model-API deltas, fields/domains, tests → `references/api-deltas-vol2.md`
   - codemod usage & how to write your own scripts → `references/upgrade-code.md`
4. **Validate** — re-run the scanner (expect 0 findings), then:
   `odoo-bin -u <module> --test-tags /<module>` in a 19.0 sandbox; fix view
   validation errors (RNG) and domain `TypeError`s last, they are the loudest.
   Also start the server with deprecation warnings enabled (`--dev=all` /
   log-level) and clear every `DeprecationWarning` — those are 20.0's hard-breaks.
5. **Report** — summarize per addon: codemod changes, manual edits (with the
   reference anchor used), remaining [EE-verify]/[verify] items, test status.

## Model changes (core business models)

| Check | 18.0 | 19.0 | Action |
|---|---|---|---|
| `stock.quant.package` | model | → `stock.package` | Rename; `stock.package.history` added, `stock.package_level` removed |
| `hr.contract` | model (`hr_contract` module) | → `hr.version` (`hr_contract` merged into `hr`) | Rename all inheritance and references |
| `hr.expense.sheet` | model | merged into `hr.expense` | Drop the sheet layer |
| `res.users.groups_id` | field | → `group_ids` | **18→19, not 19→20** |
| `procurement.group` | model | **removed** | Also removes `stock.move.group_id`, `stock.picking.group_id`, `sale.order.procurement_group_id`. The whole grouping chain dies — rebuild reports on `origin`/`sale_id` |
| `product.packaging` | model | **removed** | `product.template.packaging_ids` goes too |
| `stock.picking.move_ids_without_package` / `move_line_ids_without_package` | fields | **removed** | Use `move_ids` / `move_line_ids` |
| `account.fiscal.position.tax` | model | **removed** | Fiscal positions map tax tags directly |
| `res.partner.mobile` | field | **removed** | Use `phone` |
| — | — | **added**: `stock.reference`, `project.role`, `project.template.create.wizard` | `stock.reference` is a *document reference chain* (m2m to `stock.move`, computed `picking_ids`) — it is **not** a replacement for `procurement.group` |

Common mis-attribution: `stock.quant.package`→`stock.package`, `hr.contract`→
`hr.version`, `hr.expense.sheet`→`hr.expense` and `groups_id`→`group_ids` are
all **18→19**. Do not list them under 19→20.

Cross-version model index: `Core_Models_Changelog.md`.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 19.0 tree (or the
  mapping tables, which cite their source). Unverifiable EE ids stay flagged,
  never silently "completed".
- The **security file format is unchanged in 18→19**: it stays
  `security/ir.model.access.csv` with `perm_read/perm_write/perm_create/perm_unlink`
  columns. Do **not** apply the 19→20 `ir.access.csv`/`operation` conversion here.
- `web_editor` no longer exists in 19: repoint `depends` to `html_editor`
  and/or `html_builder`; do not keep `'depends': ['web_editor']`.
- `@api.returns` is removed in 19 — delete it (it had no effect in 18 either).
- Internal framework imports are gone: `from odoo.api import Meta, Params,
  propagate`, the `odoo/conf/` package, and `get_module_resource` are removed.
  Use public imports (`from odoo import api, fields, models`) and `pathlib`.
- Owl 2 → Owl 3 on the frontend: components must use `setup()`; review every
  custom JS widget. This is the highest-effort area for 18→19.
- Python: Odoo 19 requires **Python 3.11+** (3.12 recommended); PostgreSQL
  **13+** (15/16 recommended). Verify the runtime before migrating.
- When copying a value from a clipped/secondary source, verify it against the
  19.0 tree before committing.
