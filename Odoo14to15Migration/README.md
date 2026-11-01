# Odoo14to15Migration

This is the **14→15** member of the multi-version migration workspace
(see the root README for the full matrix). The 13→14 member lives in
`../Odoo13to14Migration/` and the 15→16 member in `../Odoo15to16Migration/`.

A reusable agent skill that migrates custom Odoo 14.0 addons to 15.0 (CE and EE)
using source-verified manual mappings. Companion cookbook:
`../Odoo_Migration_Cookbook_14_to_15.md`.

## What breaks in 14→15 (headline)

- **QWeb `t-raw` deprecated** (removed only in 16.0) — migrate to `t-out`, but note
  `t-out` **escapes by default**: only `markupsafe.Markup` values render as HTML.
  `fields.Html` values are Markup, `Char`/`Text` are not. `t-esc` is deprecated too.
- **`ir.model.data` lookups renamed/removed** — `xmlid_lookup` → `_xmlid_lookup`,
  `xmlid_to_res_id` → `_xmlid_to_res_id`; `_get_id(module, xml_id)`,
  `get_object_reference`, `get_object`, `xmlid_to_object` are **gone**.
  (Note: 15.0 did **not** remove `ir.model` / `ir.model.fields` access — that claim
  is wrong. Different change from the 13→14 `ir.actions.*` tightening.)
- **Mail templates: Jinja → QWeb + inline_template** — `body_html` gets
  `render_engine='qweb'`; `engine='jinja'` raises `ValueError`; subject/email_from/
  email_to use `{{ }}` not `${ }`. Data XML uses `type="html"` — there is no
  `type="qweb"`.
- **Frontend**: ES modules `/** @odoo-module **/` must be renamed `*.esm.js`;
  JS/SCSS assets move from XML into `__manifest__.py` `assets` key. The `qweb`
  manifest key is **silently ignored** (no error) — asset problems show up as
  missing UI, not as a crash.
- **Tests**: `SavepointCase` is a deprecated alias whose base changed from
  `SingleTransactionCase` to `TransactionCase` — switch to `TransactionCase` and
  re-check tests relying on class-level state. `Environment.manage()` is a no-op.
- **Accounting**: journal payment methods become `account.payment.method.line`
  records (`inbound/outbound_payment_method_ids` → `*_payment_method_line_ids`);
  `amount_by_group` → `tax_totals_json`; `tax_exigible` → `always_tax_exigible`.
- **Inventory**: `stock.inventory` / `.line` removed → count on `stock.quant`.

## NO upgrade_code codemod

`odoo/upgrade_code/` does not exist before 18.0, so **14→15 has zero codemods**.
All fixes are manual + DB-level `migrations/15.0/` scripts (OpenUpgrade).

## Contents

- `SKILL.md` — the skill (frontmatter + workflow + model-change checklist + hard rules)
- `references/` — 6 source-verified mapping tables
  - `views-qweb.md` — t-raw/t-esc -> t-out (escaping trap), esm.js, assets manifest
  - `orm-api.md` — ir.model.data method changes, SavepointCase, Environment.manage
  - `models-mapping.md` — directive/asset/API/field-type maps + core model fields
  - `http-rpc-mail.md` — Jinja->QWeb engine, subtype is NOT 14→15, HTTP unchanged
  - `security.md` — res.groups unchanged (15.0)
  - `upgrade-code.md` — codemod status (none) + migrations/15.0 workflow
- `scripts/` — `scan_addon.py` (14→15 scanner), `check_markdown.py`, `normalize_markdown.py`

## Verified against source

Every claim here was re-checked against the Odoo CE 14.0 / 15.0 tree (model-set
diff: 21 models removed, 111 added; field-level diff per model). Community claims
that failed the check — `t-raw` removed in 15.0, `ir.model*` access removed,
`subtype` -> `subtype_xmlid` being a 14→15 change — are documented as
counter-examples in cookbook section 9.3.

## Usage

```bash
python3 scripts/scan_addon.py /path/to/addons          # triage (lists 14-only APIs)
python3 scripts/scan_addon.py /path/to/addons --addon my_module --json
```

Then apply the manual mappings from `references/*` and re-scan (expect 0).
