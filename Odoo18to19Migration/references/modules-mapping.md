# Modules / Models / Fields Mapping (18 → 19)

Per-module rename/removal map plus a symptom index. Rows confirmed by ≥2 independent
sources (Cybrosys, SDLC Corp, ERP Consulting 24, Octura, LineScripts, plus the real
19.0 module `eh_hr_compat`) are marked **CONFIRMED**; the rest carry `[verify]` /
`[EE-verify]`.

## 1. Module renames (manifest `depends` repoint) — CONFIRMED

| Odoo 18 module | Odoo 19 module | Edition | Source |
|---|---|---|---|
| `web_editor` | `html_editor` + `html_builder` | CE | LineScripts + SDLC + Cybrosys + ERP24 |
| `account_auto_transfer` | `account_transfer` | EE | LineScripts — `[EE-verify]` |
| `account_disallowed_expenses` | `account_fiscal_categories` | EE | LineScripts — `[EE-verify]` |
| `hr_work_entry_contract_*` | dropped `contract` infix (e.g. `hr_work_entry_*`) | EE | LineScripts — `[EE-verify]` |

> Other EE module renames are possible; re-check against the Enterprise 19.0 tree.

## 2. Model renames — `[verify]`

| Odoo 18 model | Odoo 19 model | Source |
|---|---|---|
| `stock.quant.package` | `stock.package` | SDLC Corp |
| `procurement.group` | `stock.reference` | SDLC Corp |

## 3. Removed models — CONFIRMED

| Model | Note |
|---|---|
| `res.partner.title` | removed in 19 (Cybrosys, ERP24) — update modules referencing it |
| `uom.category` | removed in 19 (Octura, SDLC, Cybrosys) — see UoM field renames below |

## 4. Field renames / removals — CONFIRMED unless noted

| Model | Odoo 18 field | Odoo 19 field | Source |
|---|---|---|---|
| `res.groups` | `category_id` | `privilege_id` (`res.groups.privilege`) | Cybrosys/SDLC/eh_hr_compat |
| `res.groups` | `groups_id` | `group_ids` | Cybrosys/eh_hr_compat |
| `res.groups` | `users` | `user_ids` | eh_hr_compat |
| `res.users` | `groups_id` | `group_ids` | eh_hr_compat (16–18→19 flip) |
| `account.move.line` | `tax_id` | `tax_ids` (m2m) | Cybrosys/SDLC/ERP24 |
| `account.move.line` | `product_uom` | `product_uom_id` | Cybrosys/SDLC/ERP24 |
| `uom.uom` | `factor_inv` | `relative_factor` | SDLC/Octura/Cybrosys |
| `uom.uom` | `category_id` | `relative_uom_id` | SDLC/Octura/Cybrosys |
| `uom.uom` | `uom_type` | removed | Octura |
| `res.city` | `zip` | `zipcode` | mindscript |
| `res.partner` | `mobile` | removed (merged into `phone`) | Cybrosys + mindscript |
| `res.partner` | `picking_warn` | removed | Cybrosys |
| `res.partner` | `last_website_so_id` | removed | Cybrosys |
| `res.partner` | `sale_line_warn` | removed | Cybrosys |
| `website` / shop | `website.pricelist_id` | `request.pricelist` | Cybrosys |
| `fleet.vehicle.log.services` | `date` | `date_from` / `date_to` | Cybrosys |
| `hr.contract` | — | `hr.version` (contract data via employee versions) | SDLC — `[verify]` (19.0 addon path relocated; not source-confirmed this pass) |
| `hr.candidate` | — | `hr.applicant` | SDLC — `[verify]` **scope risk**: `hr.candidate`→`hr.applicant` predates 18.0; likely NOT an 18→19-specific change — confirm before relying on it |

> Scope guard: `res.partner.bank.acc_number→account_number`, `res.users` many
> 19→20 renames, `account.group→account.account` (codemod `19.3-00`) are **19→20**
> changes — they belong to the 19→20 skill, **not** 18→19. The `account.group`
> hierarchy change only triggers when `--to ≥ 19.3` (Online), not a pure 18→19 CE run.

## 5. Symptom → fix index

| Symptom during 19 install/runtime | Likely cause | Fix anchor |
|---|---|---|
| Module fails to install: `depends` unresolved | `web_editor` (or renamed EE module) | §1 |
| `ImportError` at load: `from odoo.api import ...` | internal import removed | security-and-orm §4 |
| `ImportError`: `get_module_resource` | helper removed | security-and-orm §4 |
| `DeprecationWarning`: `self._cr/_uid/_context` | use `self.env.*` | security-and-orm §4 |
| `DeprecationWarning`: `read_group(` | use `_read_group(aggregates=...)` | security-and-orm §4/§5 |
| JS widget errors / blank screens | Owl 2 → Owl 3 | views-qweb-owl §1 |
| `@api.returns` syntax/traceback | decorator removed | security-and-orm §4 |
| Route logs deprecation on import | `type='json'` → `type='jsonrpc'` | binary-http-mail §1 |
| Group XML references fail (`groups_id`/`users`/`category_id`) | `res.groups` renames | §4 |
| `KeyError` on `res.partner.title` / `uom.category` | model removed | §3 |
| `AttributeError` on `mobile` / `sale_line_warn` / `picking_warn` | field removed | §4 |
| Action `target='inline'` rejected | target removed | views-qweb-owl §5 |
| Kanban card not rendering | `kanban-box` → `card` | views-qweb-owl §3 |
