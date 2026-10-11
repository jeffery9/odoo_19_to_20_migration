# Business-module mappings (19 → 20)

Models / fields / xml-ids per module family. **[EE-verify]** = Enterprise-only,
confirm against the Enterprise 20.0 tree.

## Models
| 19 | 20 |
|---|---|
| `hr.contract` | `hr.version` (contract data via employee versions) |
| `hr.leave.type` | `hr.work.entry.type` |
| `hr.expense.sheet` | `hr.expense` |
| `hr.payslip.input.type` | removed; 20 payroll input design (`input_usage_payslip`) **[EE-verify]** |
| `stock.scrap` | `stock.move` with `is_scrap=True` |
| `stock.return.picking` | `stock.picking._create_return()` |
| `stock.quant.package` | `stock.package` |
| `note.note` | `project.task` (`project_todo`) |
| `mail.thread.cc` | `mail.thread` |
| `res.bank` | Char field or `res.partner.bank` per use |
| `industry_fsm` / `helpdesk_fsm*` / `documents_fsm` | `project` / `helpdesk` / `documents` **[EE-verify]** |
| `stock_picking_batch` | `stock` |
| `website_sale_wishlist` / `website_sale_comparison` | merged into `website_sale` |
| `crossovered.budget(.lines)` | `budget.analytic` / `budget.line` **[EE-verify]** |
| `account.group` | `account.account` hierarchy (`parent_id`, computed `parent_ids`); codemod `19.3-00-account-groups` |
| `account.asset` where `state='model'` | `account.depreciation.model` **[EE-verify]** |
| `mail.tracking.value` (core `mail`) | `mail_tracking` addon |

## Fields
| Model(s) | 19 | 20 |
|---|---|---|
| `sale.order` | `state='done'` | removed |
| `stock.move.line`, `stock.move`, `purchase.order.line`, `mrp.bom`, `repair.order` | `product_uom_id`/`product_uom` | `uom_id` (view xpath `//field[@name='move_ids']/list/field[@name='uom_id']`) |
| `sale.order.line`, `account.move.line` | `product_uom_id` | unchanged |
| `res.partner.bank` | `acc_number`, `acc_holder_name` | `account_number`, `holder_name` |
| `res.partner` | `company_type`, `mobile` | `is_company`, `phone` |
| `res.users` | `groups_id` | `group_ids` |
| `ir.attachment` | `datas` | `raw` |
| `project.task` | `user_id` | `user_ids` |
| `product.template` | `type=='product'` | `is_storable` |
| `hr.leave` | `holiday_status_id` / `holiday_type` | `work_entry_type_id` / `validation_type` |
| `account.analytic.account` | `group_id` | `plan_id` |
| `crm.lead` | `currency_id` | `company_currency` |
| `fleet.vehicle.log.services` | `date` | `date_from`, `date_to` |
| `payment.provider` | `state` | `is_live`, `is_published` |
| `resource.calendar.leaves` | `time_type` | `count_as` |
| `account.move` report | `type` | `move_type` |
| `account.payment` | `state='in_process'` / `'paid'` | `'paid'` / `'reconciled'` |
| `mrp.production` | `show_produce_all` | removed (`button_mark_done`) |

## XML ids & views
| 19 | 20 |
|---|---|
| `project.portal_my_home` | `portal.entry` |
| `industry_fsm.fsm_menu_root` | `project.menu_main_pm` **[EE-verify]** |
| `hr_work_entry.work_entry_type_attendance` | `hr_work_entry.generic_work_entry_type_attendance` |
| legal-leave default | `hr_work_entry.generic_work_entry_type_legal_leave` |
| time-off type form inherit | `hr_holidays.hr_work_entry_type_view_form` (+ field `support_document`, `time_off_selectable`) |
| pay-run kanban | `hr_payroll.hr_payrun_payslip_kanban_card` **[EE-verify]** |
| Enterprise budget form | `account_budget.view_budget_analytic_form` **[EE-verify]** |
| scrap form / batch picking form | `stock.view_scrap_move_form` / `stock.stock_picking_batch_form` (in `stock`) |
| wishlist/compare templates | `website_sale.product_wishlist`, `website_sale.product_compare`, `website_sale.model_product_wishlist` |
| add-to-cart | `a[@id='add_to_cart']`→`button[@name='add_to_cart']`; wraps: `div[@id='add_to_cart_wrap']`, template `website_sale.cta_wrapper`, `#o_wsale_cta_wrapper` |
| `website_sale.product_terms_and_conditions` | removed — xpath after `#o_wsale_product_cta_section` |
| comparison controller | `odoo.addons.website_sale.controllers.cart` |
| EE salary rule `category_id`/`struct_id` | `category_ids`/`struct_ids` / `[(6, 0, [ref(...)])]` **[EE-verify]** |

## Symptom index (quick)
- `KeyError: 'ir.rule'` on install → security file not converted (ch. security-and-orm).
- `Field has no SQL representation` → rule domain on non-stored field.
- `RuntimeError: request not bound` → `request.env`/`request.website` in model/report code.
- Blank Font Awesome icon on website → Material Symbols / `oi` + `data-icon`.
- 500 on public pages with `t-attf-value="#{user.partner_id.email}"` →
  `t-att-value="request.env.user.partner_id.email if not request.env.user._is_public() else ''"`.
- JSON-2 `/json/2` and XML-RPC `/xmlrpc/2` are **still present** in 20 — do not migrate clients away.
