# 9→10 研究来源与源码核实地图

> 本文件记录 9→10 每条破坏性变更的溯源与核实状态，供修订时复核。

## 已核实（CONFIRMED）

| 变更 | 来源 | 核实方式 |
|---|---|---|
| `openerp` 包 → `odoo`（10.0 不再有 `openerp` 包） | OCA `Migration to version 10.0` | "rename openerp module to odoo"/源码 `odoo/__init__.py` 无 `openerp` |
| `__openerp__.py` → `__manifest__.py`（清单文件改名） | OCA 10.0 指南 | 10.0 清单加载器只识别 `__manifest__.py` |
| 字段 `select = True` → `index = True` | OCA 10.0 指南 | 字段建索引属性改名 |
| 视图继承字符串选择器收紧；`<openerp>`/`<data>` 根包装 → `<odoo>` | OCA 10.0 指南 + 10.0 源码 | 视图继承要求属性选择器 |
| `base.group_configuration` → `base.group_system` | OCA 10.0 指南 | "base.group_configuration has been renamed to base.group_system" |
| `copy` 方法 `@api.one` → `@api.multi` | OCA 10.0 指南 | "Change decorator of copy method ... from @api.one to @api.multi" |
| 安全组模块化：`base.group_sale_*`→`sales_team.*`、`base.group_hr_*`→`hr.*`、`menu_hr_configuration`→`menu_human_resources_configuration`、`website.salesteam_website_sales`→`sales_team.salesteam_website_sales`、`product.prod_config_main`→`sale.prod_config_main` | OCA 10.0 指南 | 组从 `base` 迁移到业务模块 |
| 10.0 及更早无 `odoo/upgrade_code/` 模块（引擎 18.0 才出现） | odoo/odoo 仓库核查 | codemod 引擎可用性 |

## 待核实（[verify] / [EE-verify]）

| 变更 | 状态 | 备注 |
|---|---|---|
| 安全组模块化是否覆盖全部 OCA 官方列表（有无遗漏的 `base.group_*`） | [verify] | 以 OCA `Migration to version 10.0` 完整清单为准，本卷已列 8 项 |
| EE 专属模块在 10.0 的归属微调 | [EE-verify] | 企业版 10.0 的 module 列表若有调整需对照 EE 树 |

## 版本作用域红线（已对照确认不属于 9→10）

- `@api.one` 完全移除 / `fields.Date` 对象化 / `ir.actions.act_window.view` 移除 / `t-field-options`→`t-options` —— **11→12**
- Python 3 强制 / 工作流移除 / 报表 `render_html`→`get_report_values` / 模块改名 `sale`→`sale_management` —— **10→11**
- `account.invoice`→`account.move` —— **12→13**
