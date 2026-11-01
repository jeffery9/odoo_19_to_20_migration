---
name: odoo_9_to_10_migration
description: Migrates custom Odoo 9.0 addons to 10.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 9 to 10, fix 10.0 hard breaks (package rename from openerp to odoo, __openerp__.py to __manifest__.py, select=True to index=True on fields, XML inherit string position/xpath selectors -> attribute selectors + <openerp>/<data> root wrappers -> <odoo>, base.group_configuration -> base.group_system, copy method @api.one -> @api.multi, security-group modularization base.group_sale_* -> sales_team.* and base.group_hr_* -> hr.*), or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 9-only APIs. Note 10.0 and earlier have NO upgrade_code codemod — the engine only exists from 18.0 — all fixes are manual; DB changes handled by OpenUpgrade.
version: 10.0.1
author: Independent (companion to the Odoo Migration Cookbook series)
category: migration
odoo_versions: ["9.0", "10.0"]
tags: [odoo, migration, upgrade, openerp-to-odoo, manifest-rename, select-to-index, xml-selector, security-groups, codemod, upgrade_code]
---

# Odoo 9 → 10 Migration

## Goal

Take a 9.0 custom addon (or a whole addons tree) to 10.0 with no leftover
9-only API, using **verified manual mappings** (there is **no** `upgrade_code`
codemod for 9→10 — the tooling ships in 18.0). Database-level changes
(field/model structure) are applied by **OpenUpgrade** / the official
upgrade service; this skill covers the **code-level** mappings a custom module
must make.

> **Scope note.** This skill covers the **9.0 → 10.0** jump only. The
> headline break is the `openerp`→`odoo` package rename and the
> `__openerp__.py`→`__manifest__.py` manifest rename (both 9→10). The 10→11
> skill (`Odoo10to11Migration/`) handles the next step (Python 3 mandatory,
> Workflow removal, QWeb report API rewrite); the 11→12 skill handles
> `@api.one` removal and `fields.Date` runtime object. 10→11 only removes the
> last `openerp` compat alias left over from this pair.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables for the
  9→10 jump. Primary anchors:
  - OCA `Migration to version 10.0` — `openerp`→`odoo`, `__openerp__.py`→`__manifest__.py`, `select=True`→`index=True`, `base.group_configuration`→`base.group_system`, `copy` method `@api.one`→`@api.multi`, security-group modularization.
  - OCA `Migration to version 9.0` — baseline that 9.0 is still the `openerp` package era.
  - Odoo 10.0 source check — `odoo/__init__.py` has no `openerp` package; the manifest loader only recognises `__manifest__.py`.
- Items tagged **[verify]** come from a single community source or sources that
  disagree — confirm before relying on them. `[EE-verify]` items are
  Enterprise-only.

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 10.0 replacement, and notes every item is `manual`
   (no codemod exists for 9→10).
2. **Manual mappings** — for every finding, apply the replacement from the
   matching reference file:
   - 包改名 / 清单改名 / `select`→`index` / `copy` 装饰器 / `@api.one`+`@api.onchange` 警告 → `references/orm-api.md`
   - 视图 / XML 选择器清理 / `<openerp>`/`<data>`→`<odoo>` → `references/views-qweb.md`
   - 模块 / 模型 / 字段映射（9→10 无大规模重命名）→ `references/models-mapping.md`
   - 安全组微调（`base.group_configuration`→`base.group_system`）+ 安全组模块化 → `references/security.md`
   - HTTP/RPC/邮件/二进制（基本不变，`openerp.http`→`odoo.http`）→ `references/http-rpc-mail.md`
   - codemod 状态 & `migrations/10.0/` 脚本 → `references/upgrade-code.md`
3. **Data migrations** — put custom DB/structure fixes in each module's
   `migrations/10.0/` (`pre-`/`post-` scripts, e.g. group-id repointing).
   There is no `upgrade_code` run for 9→10.
4. **Validate** — `python3 -m py_compile **/*.py` (catch syntax), re-run the scanner (expect 0 findings), then run `odoo-bin -u <module> --test-tags /<module>` in a 10.0 sandbox; fix `ImportError` (`openerp` package,
   `__openerp__.py` missing) / `External ID not found` (`base.group_configuration`,
   old `base.group_*` ids) first. Start with `--dev=all`.
5. **Report** — summarize per addon: manual edits (with reference anchor used),
   remaining [verify] items, test status.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 10.0 tree (or the
  mapping tables, which cite their source). Unverifiable ids stay flagged,
  never silently "completed".
- **`openerp`→`odoo` package rename is the headline breaking change.** 10.0 has
  no `openerp` package. Rewrite every `from openerp import ...` / `import
  openerp` to `from odoo ...` / `import odoo`, including `openerp.addons.*`
  paths and `from openerp import http`.
- **`__openerp__.py`→`__manifest__.py`.** Rename the module manifest file
  (`git mv`). The dict keys are unchanged.
- **`select = True`→`index = True`** on field definitions (also `select=1`).
- **XML inherit selectors tighten.** Replace string `position`/text `xpath`
  selectors with attribute selectors (usually `name`); wrap views in `<odoo>`
  instead of `<openerp>`/`<data>` root wrappers. Do not disturb legitimate
  `name=` attributes.
- **`base.group_configuration`→`base.group_system`.** Also complete the 10.0
  security-group modularization: `base.group_sale_*`→`sales_team.*`,
  `base.group_hr_*`→`hr.*`, `menu_hr_configuration`→`menu_human_resources_configuration`,
  `website.salesteam_website_sales`→`sales_team.salesteam_website_sales`,
  `product.prod_config_main`→`sale.prod_config_main`.
- **`copy` method `@api.one`→`@api.multi`.** Add `self.ensure_one()` /
  `for record in self:` if the body assumed a singleton. Do NOT combine
  `@api.one` with `@api.onchange` (crashes on 9.0/10.0).
- **There is NO `upgrade_code` codemod for 9→10** (nor for any target ≤17.0) —
  `odoo/upgrade_code/` does not exist before 18.0. Do not tell the user to run
  `odoo-bin upgrade_code --from 9.0`; all code renames are manual, DB changes
  are OpenUpgrade's job.
- **Do NOT migrate these in 9→10** (they are still valid in 10.0; their
  removal/rename belongs to 10→11 or 11→12): Python 3 mandatory + py2 syntax
  (10→11); Workflow removal + QWeb report `render_html`→`get_report_values`
  (10→11); `@api.one` full removal (11→12); `fields.Date`/`Datetime` runtime
  object (11→12); `ir.actions.act_window.view` removal (11→12);
  `t-field-options`→`t-options` (11→12); `account.invoice`→`account.move`
  (12→13).
- When copying a value from a clipped/secondary source, verify it against the
  10.0 tree before committing.
