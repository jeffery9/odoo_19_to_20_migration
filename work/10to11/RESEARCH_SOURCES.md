# 10→11 研究来源与源码核实地图

> 本文件记录 10→11 每条破坏性变更的溯源与核实状态，供修订时复核。

## 已核实（CONFIRMED）

| 变更 | 来源 | 核实方式 |
|---|---|---|
| 11.0 仅支持 Python 3（≥3.5），10.0 双兼容 | Odoo 官方 `python3.rst`（11.0） | 文档明确"first LTS to drop Python 2" |
| Python 2 语法清单（print/iteritems/has_key/xrange/unicode/basestring/StringIO/urllib2/except E,e/整除） | Odoo 官方 `python3.rst` | 标准库迁移表 |
| `openerp.tools.pycompat` 垫片（izip/imap/ifilter/unichr/text_type/string_types/to_native）11.0 移除 | coopdevs OCB 镜像 `doc/python3.rst` | git blame 指向 odoo/odoo#28519 |
| `openerp` 包兼容别名 11.0 移除（主改名 9→10） | OCA 10.0 指南 + stackguides ImportError 案例 | 源码 `odoo/__init__.py` 无 `openerp` |
| 工作流（Workflow）11.0 完全移除 | Odoo 论坛 v10→v11 经验帖 | "Workflow has been completely removed from v11" |
| 报表 `render_html`→`get_report_values`、`get_action`→`report_action`、`get_html`→`render_qweb_html` | Odoo 论坛 v10→v11（Anil Kesariya） | Before/After 代码示例 |
| `ir.cron` `model`→`model_id`（ref ir.model） | Odoo 论坛 v10→v11 | cron 字段示例 |
| 模块改名 `sale`→`sale_management`、`account_accountant`→`account_invoicing` | Odoo 论坛 v10→v11 | 模块清单 |
| 模块合并 `account_tax_cash_basis`→`account`、`report`→`web` | Odoo 论坛 v10→v11 | 合并说明 |
| `base.group_configuration`→`base.group_system` | OCA 10.0 指南 | "base.group_configuration has been renamed to base.group_system" |
| 11.0 无 `odoo/upgrade_code/` 模块（引擎 18.0 才出现） | odoo/odoo 仓库核查 | codemod 引擎可用性 |

## 待核实（[verify] / [EE-verify]）

| 变更 | 状态 | 备注 |
|---|---|---|
| 前端 Bootstrap 具体大版本号（3→4？） | [verify] | 无官方 10→11 前端清单；以 11.0 源码 `package.json` / `web` 资产为准 |
| EE 专属模块在 11.0 的归属微调 | [EE-verify] | 企业版 11.0 的 module 列表若有调整需对照 EE 树 |

## 版本作用域红线（已对照确认不属于 10→11）

- `@api.one` 移除 / `fields.Date` 对象化 / `parent_path` / `ir.actions.act_window.view` 移除 / `do_notify`/`do_warning` 移除 / `t-field-options`→`t-options` —— **11→12**
- `from openerp`→`from odoo` 主改名 / `__openerp__.py`→`__manifest__.py` / `select=True`→`index=True` / group 模块化 —— **9→10**
- `account.invoice`→`account.move` —— **12→13**
