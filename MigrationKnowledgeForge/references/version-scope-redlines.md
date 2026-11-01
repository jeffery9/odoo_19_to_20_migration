# Version-scope red lines (canonical ownership, 5.0 → 20.0)

The #1 source of error when forging a version pair is **mis-attribution**: listing a
breaking change under the wrong X→Y pair. This file is the forge's hard-won,
*verified* ownership table. When instantiating any new pair, consult it first — if a
change is already owned by another pair below, **do not** re-list it as a new break in
your pair (mention it only as "legacy cleanup" if your source version still contains it).

All rows verified against the companion cookbooks / `references/` in this workspace
(`Odoo_Migration_Cookbook_*_to_*.md`, `OdooXXtoYYMigration/references/`) and, where marked
"source:", against a local checkout of `odoo/odoo` (CE 5.0–20.0) and `odoo-enterprise`
(EE 9.0–20.0) using `scripts/diff_core_models.py` (model-set + field-level diff) and
`git grep` on 2026-11-01.

## The discipline (read first)

A change enters the X→Y artifact **only if it first appears at ≥ X.0 and ≤ Y.0**.

- Read the Online/minor number in the official Changelog (e.g. 17.2, 18.1, 18.5,
  19.1, 19.3, 19.4); that minor is where the change *lands*.
- If the introducing version is **< X.0** (X already contains it), do **not** list it
  in X→Y.
- Codemod script prefixes encode the version (`18.1-00-sql-constraint`). A script
  fires in an X→Y run only when its version ∈ [X.0, Y.0].

## Canonical ownership table (who owns which break)

| Breaking change | Owned by | Evidence / where proven |
|---|---|---|
| `__terp__.py` → `__openerp__.py`; `init_xml`/`update_xml`/`demo_xml` → `data`/`demo`/`test` | **5 → 6** | `Odoo5to6Migration/` scanner `terp-manifest` + `manifest-keys` |
| `osv.osv` → `osv.Model` base-class rename (begins) | **6 → 7** | `Odoo6to7Migration/references/` |
| `res.partner.address` model **removed** | **6 → 7** | `Odoo6to7Migration/` scanner `partner-address` |
| manifest `update_xml` → `data` finalized; view bootstrap class changes | **6 → 7** | `Odoo6to7Migration/` scanner `manifest-keys`/`view-bootstrap` |
| `osv` → `models` import; full New API (`self.env`, `@api.*`, recordsets) | **7 → 8** | `Odoo7to8Migration/references/models-mapping.md` |
| `osv.except_osv` → `UserError`; field class attributes on model | **7 → 8** | `Odoo7to8Migration/` scanner `except-osv`/`fields-attr` |
| Community / Enterprise **split** begins; `osv_memory` → `transient` | **8 → 9** | `Odoo8to9Migration/` scanner `enterprise-split`/`osv-memory-field` |
| `base.group_*` modularisation (group moves) | **8 → 9** | `Odoo8to9Migration/` scanner `group-move` |
| `openerp` → `odoo` **package rename** | **9 → 10** | `Odoo9to10Migration/` scanner `openerp-import` + `manifest-rename` |
| `__openerp__.py` → `__manifest__.py` | **9 → 10** | `Odoo9to10Migration/` (filename block) |
| `select`/`copy` decorator & `xml` selector manifest changes | **9 → 10** | `Odoo9to10Migration/` scanner `select-index`/`copy-decorator`/`xml-selector` |
| **Python 3 mandatory**; **Workflow fully removed** | **10 → 11** | `Odoo10to11Migration/` scanner `py2-syntax`/`workflow` |
| QWeb report API rewrite (`render_html` → `get_report_values`) | **10 → 11** | `Odoo10to11Migration/` scanner `report-api` |
| `ir.cron` `model` → `model_id`; module renames/merges (`sale`→`sale_management`, `account_tax_cash_basis`→`account`) | **10 → 11** | `Odoo10to11Migration/` scanner `ir-cron-model`/`module-rename`/`module-merge` |
| `base.group_configuration` → `base.group_system` | **10 → 11** | `Odoo10to11Migration/` scanner `group-config` |
| `@api.one` **removed** (headline); `fields.Date` runtime object | **11 → 12** | `Odoo11to12Migration/` |
| `@api.model_create_multi`, `_parent_store`; `ir.actions.act_window.view` removed | **11 → 12** | `Odoo11to12Migration/` |
| `t-field-options` → `t-options` | **11 → 12** | `Odoo11to12Migration/` (view refs) |
| `account.invoice` / `account.invoice.line` → `account.move` / `account.move.line` | **12 → 13** | `Odoo12to13Migration/references/accounting-models.md` |
| `account.voucher` → merged into `account.move` | **12 → 13** | `Odoo12to13Migration/` |
| `stock.picking` model additions/removals (replenishment reports, `stock.orderpoint.snooze`; `stock.picking.responsible` removed) — **NOT** a `move_lines`→`move_ids_without_package` rename (both coexist since ≤12.0; source-verified) | **13 → 14** | `Odoo13to14Migration/`; re-check via `diff_core_models.py --repo <local> --model stock.picking` |
| `stock.inventory` / `stock.inventory.line` models **removed** (counts move to `stock.quant` + `stock.inventory.adjustment.name`) | **14 → 15** | source: present 14.0, absent 15.0 |
| `product.template.detailed_type` **added** (removed again at 18.0 — see 17→18 row) | **14 → 15** | source: absent 14.0, present 15.0 |
| `project.milestone` / `project.update`; `hr.work.location`; `stock.storage.category` models added | **14 → 15** | source: model-set diff |
| `stock.production.lot` → `stock.lot`; `payment.acquirer` → `payment.provider`; `coupon` → `loyalty` | **15 → 16** | `Odoo_Migration_Cookbook_15_to_16.md` |
| `account.*.template` model family **removed** (chart templates become Python/CSV data) | **16 → 17** | source: present 16.0, absent 17.0 |
| `account.invoice.send` → `account.move.send` | **16 → 17** | source: 16.0 invoice_send.py, 17.0 move_send.py |
| `hr.plan` / `hr.plan.activity.type` / `hr.plan.wizard` **removed** (generic `mail.activity.plan` remains) | **16 → 17** | source: present 16.0, absent 17.0 |
| `stock.immediate.transfer`; `mrp.immediate.production` wizards **removed** | **16 → 17** | source: present 16.0, absent 17.0 |
| `res.partner.display_name` → `complete_name` (field) | **16 → 17** | source: 16.0 vs 17.0 res_partner.py |
| `product.combo` / `product.combo.item` models **added** (17.0 only had POS `pos.combo`) | **17 → 18** | source: absent 17.0, present 18.0 in `product` |
| `product.template.detailed_type` **removed** | **17 → 18** | source: present 17.0, absent 18.0 |
| `stock.assign.serial`; `account.unreconcile`; `mrp.document` models **removed** | **17 → 18** | source: present 17.0, absent 18.0 (CE and EE) |
| **EE** `account_budget` model family **rewritten**: `crossovered.budget`, `crossovered.budget.lines`, `account.budget.post` removed → `budget.analytic`, `budget.line`, `budget.report`, `budget.split.wizard` added (kept=0) | **17 → 18** | source: EE 17.0 `account_budget/models/account_budget.py`; EE 18.0 `budget_analytic.py`/`budget_line.py`; `diff_core_models.py --repo <EE> --scan-modules account_budget`. NB: 18.0 `i18n/*.po` still names `crossovered_budget` — stale translations, not model evidence |
| `stock.quant.package` → `stock.package` (+ `stock.package.history`; `stock.package_level` removed) | **18 → 19** | source: present 18.0, absent 19.0 |
| `hr.contract` → `hr.version` (`hr_contract` merged into `hr`; `hr.employee.base` removed) | **18 → 19** | source: 18.0 hr_contract, 19.0 hr_version |
| `hr.expense.sheet` → `hr.expense` | **18 → 19** | source: present 18.0, absent 19.0 |
| `product.packaging` model **removed** (+ `product.template.packaging_ids`) | **18 → 19** | source: present 18.0, absent 19.0 / EE |
| `res.partner.mobile` field **removed** (use `phone`) | **18 → 19** | source: present 18.0, absent 19.0 |
| `stock.picking.move_ids_without_package` / `move_line_ids_without_package` / `date` / `group_id` **removed** | **18 → 19** | source: present 18.0, absent 19.0 |
| `procurement.group`; `account.fiscal.position.tax` models **removed** | **18 → 19** | source: present 18.0, absent 19.0 |
| `res.users.groups_id` → `group_ids` (field renamed) | **18 → 19** | source: 18.0 `groups_id`, 19.0 `group_ids` |
| `is_storable` **relocated** `stock` → `product` core (field exists since 18.0) | **19 → 20** | source: 18.0 stock/product.py, 20.0 product/product_template.py |
| `account.group`; `stock.scrap`; `hr.leave.type`; `hr.version.wizard`; `hr.contract.type`; `mail.thread.cc`; `payment.provider`; `res.bank`; `product.template.attribute.exclusion` models **removed** | **19 → 20** | source: present 19.0, absent 20.0 |
| **EE** `hr.payslip.input.type` model **removed**, input types **merged into `hr.salary.rule`** (`hr.payslip.input` now hangs off `salary_rule_id`; `name`/`code`/`input_suffix`/`user_instructions` become related) | **19 → 20** | source: EE 19.0 `hr_payroll/models/hr_payslip_input_type.py` vs EE 20.0 (file gone; `hr_payslip_input.py` uses `salary_rule_id`). NB: `input_usage_payslip` is a pre-existing boolean on `hr.salary.rule` (19.0 already has it), NOT a replacement model |
| `tree` → `list` view type (codemod ships in **18** tree) | **17 → 18** (landed 17.5) | `odoo-version-pairs.md` matrix |
| ORM → `odoo/orm` shim packages (`from odoo import models` still works) | **19** (shim in 19, split in 19) | `Odoo19to20Migration/` + `odoo-version-pairs.md` |
| `read_group` signature overhaul; `Domain`/`Query`/cache relocation | **19 → 20** | `Odoo19to20Migration/references/` |
| Python floor 3.10 → **3.12** | **20.0** | `odoo-version-pairs.md` |
| `odoo/osv` **removed** | **20.0** | `Odoo19to20Migration/` |
| `ir.model.access.csv` → `security/ir.access.csv` (headline 19→20) | **19 → 20** (landed 19.4) | `Odoo19to20Migration/references/security-and-orm.md` |
| `res.partner.company_type` **removed** (boolean `is_company` governs); `company_registry` → `additional_identifiers` | **19 → 20** | `Odoo19to20Migration/` |

## Counter-examples — things that LOOK like a break but are NOT owned by the pair you might think

These must **not** be dragged into the named pair; they belong where stated:

- `ir.model.access.csv` conversion → **19.4 / 19→20** (NOT 18→19).
- `models.Constraint` as a *requirement* → optional since **18.1** (NOT a hard 18→19 break).
- `check_access` / `has_access` → **18.0** (already present in 18, not new in 18→19).
- `Domain` API → **18.1** (NOT 19→20).
- `group_operator` → `aggregator` rename → **17.2** (NOT 19→20).
- `tree` → `list` → **17.5** (codemod ships in the 18 tree; NOT 19→20).
- ORM package split + shim → **19** (NOT 18→19 as a full break).
- Owl 3 framework + `res.groups` privilege changes → **19** (NOT 19→20 as new).
- `openerp` → `odoo` rename → **9→10** (11.0 only cleans leftover aliases — do NOT list it as an 11→12 break).
- `@api.one` removal / `fields.Date` runtime / `parent_path` / `ir.actions.act_window.view` removal → **11→12** (NOT 12→13).
- `account.invoice` → `account.move` → **12→13** (NOT 11→12, NOT 13→14).
- `stock.quant.package` → `stock.package` and `hr.contract` → `hr.version` → **18→19** (NOT 19→20; both pairs are present-then-absent across 18.0/19.0).
- `hr.expense.sheet` → `hr.expense` → **18→19** (NOT 19→20).
- `res.partner.mobile` field removal → **18→19** (NOT 19→20; 19.0 already has no `mobile`).
- `stock.picking.move_lines` / `move_lines` vs `move_ids_without_package` → **never a rename**: both coexist 12.0–18.0 and are removed together in **19.0** (NOT 13→14).
- `product.template.detailed_type` → added **15.0**, removed **18.0** (NOT a 19→20 `type` rename).
- `product.template.is_storable` → defined in the **`stock`** module since **18.0**, relocated to `product` core at **20.0**; it is NOT a new 19→20 field, and `type` (Selection) still exists in 20.0.
- `note.note` → `project.task` → **not a real change** (no `note.note` model exists in 17.0/18.0/19.0); do not list it anywhere.
- `stock.quant.qty` → `quantity` → **10→11** (already `quantity` from 11.0; NOT 12→13).
- `account.tax.type` → `type_tax_use` → **unsupported by source** (`type_tax_use` exists since v9); keep out of tables or mark `[verify]`.
- `res.users.groups_id` → `group_ids` → **18→19** (18.0 still `groups_id`, 19.0 `group_ids`; NOT 19→20).
- `account.analytic.account.group_id` → `plan_id` → **15→16** (16.0 `plan_id`; NOT 19→20, NOT 17→18).
- `project.task.user_id` → `user_ids` → **not a 19→20 change** (`user_ids` "Assignees" already exists at 16.0); do not list it.
- `ir.attachment.datas` → `raw` → **not a rename**: `raw` exists from 17.0 onward; `datas` is simply **removed at 20.0** (list as FIELD-REMOVE).
- `stock.move.product_uom` → `uom_id` → **19→20** (correct pair; the old name is `product_uom`, not `product_uom_id`).
- `crossovered.budget` → `budget.analytic` → **17→18** (NOT 19→20). The whole EE `account_budget` family was rebuilt at 18.0 (`kept=0`); 19.0 and 20.0 already use `budget.analytic` only.
- `hr.payslip.input.type` removal → **19→20** (correct pair, EE only). It was **merged into `hr.salary.rule`**, not renamed to a new input-type model; `input_usage_payslip` is an older boolean field on `hr.salary.rule`, so citing it as "the replacement" is wrong. Also not owned by 18→19.
- Stale `i18n/*.po` entries are **not** model evidence: 18.0 `account_budget/i18n/*.po` still contains `crossovered_budget` long after the `.py` models were removed. Always `git grep` the `*.py` sources.

## How to extend this file

When a new pair is forged and a breaking change is confirmed (S1–S3, see
`source-diff-mining.md`), add the row here with its owning pair + evidence path. If a
change is *discovered* to belong to a different pair than initially thought, correct the
row and patch the offending cookbook/skill back (per the strict two-artifact order in
`SKILL.md`). Keep this file the single canonical source of "who owns what".
