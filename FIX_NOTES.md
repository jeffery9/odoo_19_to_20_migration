# 修复说明 — Odoo_Migration_Cookbook_19_to_20

修复产物:`Odoo_Migration_Cookbook_19_to_20_fixed.pdf`(50 页,A4,与原版式同风格)

## 一、问题原因

原 PDF 由 HeadlessChrome 打印生成,所有表格与代码块都放在**横向滚动容器**(`overflow-x: auto`,原 PDF 表格下方甚至印有滚动条)中。打印时容器只保留可视区域,右边界在 **x ≈ 547.7pt** 处硬裁切,导致:

- 10 个页面(原页码 7、16、22、23、33、36、37、40、42、54)的表格右列内容被截断;
- 4 处代码块行尾被截断;
- 被裁掉的文字在 PDF 内容流中即已缺失(并非隐藏),因此无法从原 PDF 直接复制恢复。

## 二、修复方法

1. 用 PyMuPDF 按几何信息(色块、边框、字体、坐标)从原 PDF 反向提取完整文档模型(章节、段落、代码块、表格单元格、项目符号);跨页拆分的 5 张表格按表头自动合并。
2. 对每个被裁切的单元格/代码行进行补全(依据见下表)。
3. 以 WeasyPrint 重新排版渲染:表格改为页宽固定布局 + 单元格内自动换行(`overflow-wrap: anywhere`),代码块 `pre-wrap`,从根本上消除裁切。校验结果:**全篇 0 个越界文本span**(原版有 45 处)。
4. 按用户要求抹除 Probuse Consulting Service Pvt. Ltd. 的全部信息(见第四节)。

## 三、补全清单(33 处表格 + 3 处代码行)

依据来源标记:
- **【源码】** = 已在 Odoo 20.0 Community 源码(github.com/odoo/odoo,分支 20.0)中核实;
- **【md】** = 取自上传的 `Odoo_Migration_Cookbook_19_to_20_2col.md` 附录 "Mapping tables / Recovery";
- **【重构】** = 原文无法逐字恢复,按语义与上下文补全,建议人工复核。

| 位置(原页) | 补全后内容 | 依据 |
|---|---|---|
| p7 ORM 表 | `_name = models.Constraint('sql', 'msg')` | 【md】+【源码】odoo/orm/model_classes.py |
| p7 | `self.has_access('read') (bool)` | 【源码】orm/models.py `def has_access(...) -> bool`;`(bool)` 为【重构】 |
| p7 | `self.env.user.has_groups('sales_team.group_sale_manager')` | 【md】(参数与左列一致) |
| p7 | `get_int / get_str / get_bool`、`set_str / set_bool / set_float` | 【源码】base/models/ir_config_parameter.py |
| p7 | `action_archive / action_unarchive` | 【md】 |
| p8 代码 | `('code_uniq', ...)` 行保持完整(仅溢出色块,未丢字) | 校验 |
| p14 代码 | `... else '/web/static/img/placeholder.png"/>` | 【重构】(Odoo 惯用占位图路径) |
| p16 设置 xpath | `//page[@name='preferences']//group[@name='other_preferences']` | 【md】 |
| p20 代码 | `... invisible="active"/>` | 【md】+【源码】calendar_views.xml |
| p22 视图表 | `no header — insert <header> with workflow buttons` | 【重构】 |
| p22 | `div[@name='button_box'] already exists` | 【md】 |
| p22 | `//sheet/widget[@name='web_ribbon']` | 【源码】calendar/analytic 视图 |
| p22 | `//h1 or //h1[hasclass('o_employee_form_header_info')]` | 【源码】hr/views/hr_employee_views.xml |
| p22 | `after department_id ; form already uses recruiter_id` | 【源码】hr_job_views.xml +【重构】措辞 |
| p22 | `//group[hasclass('oe_subtotal_footer')]` | 【源码】account/views/account_move_views.xml |
| p22 | `product.product_variant_action` | 【md】+【源码】product_views.xml |
| p23 | `point_of_sale.pos_order_receipt` | 【源码】point_of_sale/receipt/pos_order_receipt.xml |
| p23 | `div#sale_order_sidebar_button` | 【源码】sale/views/sale_portal_templates.xml |
| p33 | `//field[@name='move_ids']/list/field[@name='uom_id']` | 【md】+【源码】stock_move_views.xml |
| p36 | `hr_holidays.hr_work_entry_type_view_form` + `support_document` | 【源码】hr_holidays/views/hr_work_entry_type_views.xml |
| p36 | `hr_work_entry.generic_work_entry_type_attendance` / `..._legal_leave` | 【源码】hr_work_entry/data/hr_work_entry_type_data.xml |
| p36 | `( count_as='absence' , time_off_selectable )` | 【源码】同上 hr_holidays 视图 |
| p36 | `removed; input_usage_payslip on the salary structure`(EE) | 【重构】,Enterprise 源码不公开,需复核 |
| p36 | `category_ids / struct_ids / [(6, 0, [ref(...)])]` | 【重构】(命令三元组惯用写法) |
| p37/p54 | `hr_payroll.hr_payrun_payslip_kanban_card`(EE) | 【md】(命名模式推断,需 Enterprise 复核) |
| p41 代码 | `... if not request.env.user._is_public() else ''"/>` | 【重构】 |
| p42 | `website_sale.cta_wrapper`、`#o_wsale_cta_wrapper` | 【源码】website_sale/templates/product_page_templates.xml |
| p42 | `removed — xpath after #o_wsale_product_cta_section` | 【源码】同上 |
| p42 | `website_sale.product_wishlist , website_sale.product_compare` | 【源码】wishlist/comparison_templates.xml |
| p42 | `odoo.addons.website_sale.controllers.cart` | 【源码】website_sale/controllers/ 目录 |
| p42 | `oi + data-icon rendering` | 【md】 |
| p54 | `account_budget.view_budget_analytic_form`(EE) | 【md】(同页 45 的完整 xmlid 互证) |
| p54 | `still present (preferred external API); XML-RPC /xmlrpc/2 still present` | 【md】 |

## 四、Probuse 信息抹除

已删除(全文检索 0 命中):封面出版商行、地址(Ahmedabad / SAKAR IX / Ashram Road)、网站(probuse.com、probuseappdemo.com)、邮箱(contact@probuse.com)、电话、"Published by …"、"About the publisher" 整节、版权声明行、封底联系块(Middle East/GCC、Europe contact)。
保留:作者姓名;作者简介中与公司相关的句子已改写(如 "Mr. Mustufa Rangwala has worked in the Odoo / OpenERP ecosystem since the early versions…")。

## 五、中间产物(work/ 目录)

- `model.json` — 提取+补全后的文档模型;`book.html` — 排版源文件;`extract.py / patch_model.py / build_html.py` — 可复现脚本;`odoo20/` — 用于核实的 Odoo 20.0 源码片段。
