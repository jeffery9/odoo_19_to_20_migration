# Odoo12to13Migration

This is the **12→13** member of the multi-version migration workspace
(see the root README for the full matrix). The 11→12 member lives in
`../Odoo11to12Migration/` and the 13→14 member in `../Odoo13to14Migration/`.

A reusable agent skill that migrates custom Odoo 12.0 addons to 13.0 (CE and EE)
using source-verified manual mappings. Companion cookbook:
`../Odoo_Migration_Cookbook_12_to_13.md`.

## What breaks in 12→13 (headline)

- **Accounting rewrite** — `account.invoice` / `account.invoice.line` /
  `account.invoice.tax` / `account.voucher` merged into `account.move` /
  `account.move.line` (use `move_type`); `action_invoice_open()` → `post()`.
- **Old decorators removed** — `@api.multi` / `@api.returns` / `@api.cr` /
  `@api.model_cr` (methods are multi by default). Non-stored computed fields must
  assign a value in every branch.
- **`res.partner` `customer`/`supplier` → `customer_rank`/`supplier_rank`**
  (integers, can accumulate).
- **Actions** — `ir.actions.act_window.multi` → `binding_view_types`;
  `src_model` → `binding_model_id`.
- **Fields** — `dp.get_precision("X")` → `digits="X"`; `track_visibility=` →
  `tracking=True`; `oldname=` removed; `stock.quant.qty` → `quantity`;
  `product.product.name` now related (write template); `account.tax.type` →
  `type_tax_use`; `Binary` defaults to attachment.
- **Environment** — `sudo(user)` → `with_user(user)`; `.env.user.company_id` →
  `.env.company`; multi-company rules need the `'|'` prefix form.

## NO upgrade_code codemod

`odoo/upgrade_code/` does not exist before 18.0, so **12→13 has zero codemods**.
All fixes are manual + DB-level `migrations/13.0/` scripts (OpenUpgrade).

## Contents

- `SKILL.md` — the skill (frontmatter + workflow + hard rules / red lines)
- `references/` — 6 source-verified mapping tables
  - `orm-api.md` — decorators, with_user, multi-company, .env.company, hr.employee.base
  - `accounting-models.md` — account.move rewrite, customer_rank, account.tax
  - `views-qweb.md` — view_type removal, binding_view_types, frontend
  - `models-mapping.md` — dp.get_precision / track_visibility / oldname / stock.quant / product.product / Binary
  - `security.md` — res.groups / access rights unchanged in 12→13
  - `upgrade-code.md` — codemod status (none) + migrations/13.0 workflow + HTTP/mail unchanged
- `scripts/` — `scan_addon.py` (12→13 scanner), `check_markdown.py`, `normalize_markdown.py`

## Usage

```bash
python3 scripts/scan_addon.py /path/to/addons          # triage (lists 12-only APIs)
python3 scripts/scan_addon.py /path/to/addons --addon my_module --json
```

Then apply the manual mappings from `references/*` and re-scan (expect 0).
