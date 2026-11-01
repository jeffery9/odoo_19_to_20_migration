# Reference: Model / module renames & translation refactor (15 → 16)

Scope: **15.0 → 16.0 only.** DB-side renames are performed automatically by OpenUpgrade's
16.0 scripts (incl. domains, filters, server actions). This file lists the **code-side**
`_inherit`/`_name`/`env[...]`/`xmlid`/`depends` changes a custom module must make.

## Model renames  [CONFIRMED — OCU 15→16 diff]

| 15.0 | 16.0 |
|---|---|
| `stock.production.lot` | `stock.lot` |
| `account_analytic.group` | `account_analytic.plan` |
| `mail.channel.partner` | `mail.channel.member` |
| `account.tax.report` | `account.report` |
| `account.tax.report.line` | `account.report.line` |
| `account.account(.template).user_type_id` | `account_type` (selection field) |

Fix: rename every `env['<model>']`, `_inherit`/`_name`, `env.ref('...')`, and domain reference.
`user_type_id` → `account_type` on `account.account`/`account.account.template`.

## Module merges  [CONFIRMED — OCU]

| 15 `depends` | 16 `depends` |
|---|---|
| `fetchmail` / `fetchmail_gmail` / `fetchmail_outlook` | `mail` / `google_gmail` / `microsoft_outlook` |
| `pad` / `pad_project` | `web_editor` / `project` (pad merges into rich-text editor) |
| `coupon*` | `loyalty*` (see payment-loyalty.md) |
| `account_payment` | auto-installed (takes over payment fields/views/menus) |

Also consolidated: 6 EDI submodules → `account_edi_ubl_cii`; `project.account`/`sale_project_account`
→ `sale_project`/`project`; `account.sale.timesheet` → `sale_project`. (23 modules merged total per OCU.)

## Translation storage: `ir_translation` removed  [CONFIRMED — OCU]

16.0 removes the `ir_translation` table; translated values live in **JSONB columns** on each model.

- OpenUpgrade / official upgrade service migrates `ir_translation` rows → JSONB automatically.
- Custom code that **directly reads/writes `ir_translation`** (custom translation import/export,
  report translation logic) must be rewritten to use field translation values
  (field access under `context={'lang': ...}` or `odoo.tools.translate`).
- `[verify]` exact rewrite for custom translation-sync scripts → confirm on 16.0 instance.

## Red line

`attrs` / `states` / `<tree>` / `name_get` / `get_resource_path` are **still valid in 16** (see
views-qweb.md / orm-api.md scope notes) — do NOT rename them here; they belong to 16→17 / 17→18.
