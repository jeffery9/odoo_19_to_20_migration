---
name: odoo_10_to_11_migration
description: Migrates custom Odoo 10.0 addons to 11.0 (CE and EE). Use when the user asks to upgrade/migrate modules from 10 to 11, fix 11.0 hard breaks (Python 3 mandatory — print/iteritems/has_key/unicode/xrange/StringIO/urllib2 syntax, openerp→odoo compat alias removed, Workflow engine fully removed, QWeb report API render_html→get_report_values + get_action→report_action, ir.cron model→model_id, module renames sale→sale_management & account_accountant→account_invoicing, module merges account_tax_cash_basis→account & report→web, base.group_configuration→base.group_system), or validate a migrated addon. Also use when reviewing migration diffs or grepping for leftover 10-only APIs. Note 11.0 has NO upgrade_code codemod — all fixes are manual; DB changes handled by OpenUpgrade.
version: 11.0.1
author: Independent (companion to the Odoo Migration Cookbook series)
category: migration
odoo_versions: ["10.0", "11.0"]
tags: [odoo, migration, upgrade, python3, workflow-removed, report-api, odoo-namespace, codemod, upgrade_code]
---

# Odoo 10 → 11 Migration

## Goal

Take a 10.0 custom addon (or a whole addons tree) to 11.0 with no leftover
10-only API, using **verified manual mappings** (there is **no** `upgrade_code`
codemod for 10→11 — the tooling ships in 18.0). Database-level changes
(Workflow table cleanup, structure) are applied by **OpenUpgrade** / the official
upgrade service; this skill covers the **code-level** mappings a custom module
must make.

> **Scope note.** This skill covers the **10.0 → 11.0** jump only. The 11→12
> skill (`Odoo11to12Migration/`) handles the next step (`@api.one` removal,
> `fields.Date` runtime object, `parent_path`, `ir.actions.act_window.view`
> removal). The `openerp`→`odoo` import rename (9→10) is already done by 10.0,
> but 11.0 removes the last `openerp` compat alias — see below.

## Sources (authoritative)

- `references/*.md` in this skill — condensed, source-verified tables for the
  10→11 jump. Primary anchors:
  - Odoo 官方 `python3.rst`（11.0）— Python 3 强制、pycompat 垫片移除。
  - OCA `Migration to version 10.0` — `openerp`→`odoo`、`__openerp__.py`→`__manifest__.py`、group 模块化（9→10 主线，10→11 仅清别名）。
  - Odoo 论坛 v10→v11 经验帖（Anil Kesariya / Niyas Raphy）— Python3 语法、Workflow 移除、报表 `render_html`→`get_report_values`/`get_action`→`report_action`、`sale`→`sale_management`、`account_accountant`→`account_invoicing`、`account_tax_cash_basis`/`report` 合并、`ir.cron` model→model_id。
  - 11.0 源码核对：`odoo/__init__.py` 无 `openerp` 别名；`openerp.tools.pycompat` 移除 izip/imap/ifilter/unichr/text_type/string_types/to_native。
- Items tagged **[verify]** come from a single community source or sources that
  disagree (frontend Bootstrap major version) — confirm before relying on them.
  `[EE-verify]` items are Enterprise-only.

## Workflow

1. **Triage** — run the bundled scanner over the addons path:
   `python3 scripts/scan_addon.py /path/to/addons` (add `--json` for machines,
   `--addon NAME` to narrow). Read the report; it groups findings by file with
   line numbers, the 11.0 replacement, and notes every item is `manual`
   (no codemod exists for 10→11).
2. **Manual mappings** — for every finding, apply the replacement from the
   matching reference file:
   - Python 3 语法 / 包命名空间 / Workflow / 报表 API / ir.cron → `references/orm-api.md`
   - 视图 / QWeb / 前端 → `references/views-qweb.md`
   - 模块重命名 / 合并映射 → `references/models-mapping.md`
   - 安全组微调（`base.group_configuration`→`base.group_system`）→ `references/security.md`
   - HTTP/RPC/邮件/二进制（基本不变）→ `references/http-rpc-mail.md`
   - codemod 状态 & `migrations/11.0/` 脚本 → `references/upgrade-code.md`
3. **Data migrations** — put custom DB/structure fixes in each module's
   `migrations/11.0/` (`pre-`/`post-` scripts, e.g. Workflow 残留数据清理).
   There is no `upgrade_code` run for 10→11.
4. **Validate** — `python3 -m py_compile **/*.py` (catch Python 3 syntax),
   re-run the scanner (expect 0 findings), then
   `odoo-bin -u <module> --test-tags /<module>` in an 11.0 sandbox; fix
   `ImportError` (`openerp` / `print` / `iteritems`) / `AttributeError`
   (`signal_workflow` / `render_html`) first. Start with `--dev=all`.
5. **Report** — summarize per addon: manual edits (with reference anchor used),
   remaining [verify] items, test status.

## Hard rules

- Do not invent XML-IDs or method names: look them up in the 11.0 tree (or the
  mapping tables, which cite their source). Unverifiable ids stay flagged,
  never silently "completed".
- **Python 3 is the headline breaking change.** 11.0 runs only on Python ≥3.5.
  Rewrite `print` statements, `iteritems`/`has_key`/`xrange`/`unicode`/`basestring`/
  `StringIO`/`urllib2`/`except E, e` and integer division. py2-only `pycompat`
  shims are gone.
- **Workflow is fully removed.** Delete `workflow` XML, `type="workflow"` buttons,
  and `signal_workflow()` calls; replace with state fields + `@api.multi` methods
  + `<button type="object">`.
- **QWeb report API rewritten.** `render_html`→`get_report_values`,
  `get_action`→`report_action`, `get_html`→`render_qweb_html`.
- **`ir.cron.model`→`model_id`** (ref to `ir.model`); prefer `code` field.
- **Module renames/merges:** `sale`→`sale_management`,
  `account_accountant`→`account_invoicing`; merges `account_tax_cash_basis`→`account`,
  `report`→`web`. Update `depends` and merged-module XML-ID references.
- **`base.group_configuration`→`base.group_system`.** Also finish any 9→10
  group modularization (`base.group_sale_salesman`→`sales_team.*`,
  `base.group_hr_user`→`hr.*`) left undone.
- **There is NO `upgrade_code` codemod for 10→11** — `odoo/upgrade_code/`
  does not exist in 11.0. Do not tell the user to run `odoo-bin upgrade_code
  --from 10.0`; all code renames are manual, DB changes are OpenUpgrade's job.
- **Do NOT migrate these in 10→11** (they are still valid in 11.0; their
  removal/rename belongs to 11→12 or earlier): `@api.one` removal (11→12);
  `fields.Date`/`Datetime` runtime object (11→12); `ir.actions.act_window.view`
  removal (11→12); `do_notify`/`do_warning` removal (11→12); `t-field-options`→
  `t-options` (11→12); `parent_path` (11→12); `from openerp`→`from odoo` main
  rename (9→10); `__openerp__.py`→`__manifest__.py` (9→10).
- When copying a value from a clipped/secondary source, verify it against the
  11.0 tree before committing.
