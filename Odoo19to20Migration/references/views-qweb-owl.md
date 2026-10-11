# Views, QWeb, Owl 3 (19 → 20)

## Kanban → cards

| Odoo 19 | Odoo 20 |
|---|---|
| `project.view_project_kanban` body | `project.view_project_card` |
| `project.view_task_kanban` card/footer | `project.view_task_card`, xpath `//t[@t-name='card']//footer` |
| kanban template name | `t-name="card"` |
| `project.view_task_kanban` uses | `card_ids="%(project.view_task_card)d"` |

## Ribbons & button icons

| Odoo 19 | Odoo 20 |
|---|---|
| `<button icon="fa-check"/>` | `<button icon="check"/>` — names from `web/icons.py` |
| ribbon `text="Archived" bg_color="bg-info"` | `title="Archived" bg_color="text-bg-info"` + `invisible="active"` |
| Font Awesome classes on website snippets (`fa fa-…`) | Material Symbols ligature; web client: `oi` + `data-icon` rendering |
| `iconFromString` with `fa-` names | does not draw; use `oi`/`data-icon` |

## Form/view xpaths (verified against 20.0 CE views)

| Form | 19 xpath | 20 |
|---|---|---|
| Analytic account | `//header` | no header — insert `<header>` with workflow buttons |
| Timesheet | add `button_box` | `div[@name='button_box']` already exists |
| Calendar event | `button_box` | no button_box — buttons in `//sheet/widget[@name='web_ribbon']` area |
| Employee | `oe_title` | `//h1` or `//h1[hasclass('o_employee_form_header_info')]` |
| Job | `user_id` | after `department_id`; form already uses `recruiter_id` |
| CRM | `//div[hasclass('oe_title')]/div` | `//div[hasclass('oe_title')]` |
| Maintenance request | `archive_equipment_request`/`user_id` | `//header`; assignees `user_ids` |
| Invoice totals | `@class='oe_subtotal_footer'` | `//group[hasclass('oe_subtotal_footer')]` |
| Partner list / search | `complete_name` / `group[@name='group_by']` | `display_name` / `//search/group` |
| User preferences | `group[@name='preferences']` | `//page[@name='preferences']` |
| Product / action | `product.product_variant_easy_edit_view` / `product.product_normal_action` | removed / `product.product_variant_action` |
| Sale config menu | `sale.prod_config_main` | `sale.menu_sale_config` |
| Project form | `group[@name='extra_settings']` | `//page[@name='settings']` |
| Timesheet kanban footer | `footer[@class='mt-0 pt-0']` | `div[@name='ts_footer']` |
| Activity popup / POS session | `company_id` / `move_id` | after `summary` / `user_id` |
| POS receipt | Owl `ReceiptHeader`/`pos-receipt-contact` | `point_of_sale.pos_order_receipt` |
| Sale form / portal sidebar | `show_update_fpos` / `navspy` | `fiscal_position_id` / `div#sale_order_sidebar_button` |
| Invoice/sale/purchase lines | `product_id`/`name` direct | inside `<column name="product_and_description">`; `//list/field[@name='product_id']` does not match; xpath a direct list child (`quantity`, `product_qty`, `analytic_distribution`, `account_id`) |

Notes: view type/tag is `<list>` since 19 (no `<tree>` anywhere); `[class='X']` is an exact
match — convert inherits only once the 20 parent class string no longer equals `X`;
`string`/`title` are not valid inherit selectors — use `hasclass(...)`, `name`, `id`, `t-call`;
xpath cannot enter a `t-call` body — inherit the called template or xpath the `t-call` node.

## QWeb & reports

- wkhtmltopdf no longer assumed inside `web`: modules `base_report_wkhtmltox` /
  `base_report_paper_muncher` (verify availability in your deployment).
- `<img t-attf-src="data:image/png;base64,#{rec.img}"/>` →
  `<img t-att-src="image_data_uri(rec.img) if rec.img else '/web/static/img/placeholder.png"/>`.
- `_render_qweb_pdf` takes the report **action** xmlid.

## Owl 3

- `t-set` nodes consumed by a `t-call`/`t-snippet-call` attribute must be hoisted
  **before** the call (codemod `19.1-00-t-call`).
- `DropdownItem` takes `attrs=`; `href=` and `dataset=` are invalid props.
- Full JS migration helper: `odoo-bin upgrade_code --script owl3-migration`
  (not part of any version range — run explicitly).
