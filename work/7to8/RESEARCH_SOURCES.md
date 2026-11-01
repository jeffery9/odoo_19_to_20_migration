# 7→8 研究来源与源码核实地图

> 本文件记录 7→8 每条破坏性变更的溯源与核实状态，供修订时复核。

## 已核实（CONFIRMED）

| 变更 | 来源 | 核实方式 |
|---|---|---|
| New-API 装饰器引入（@api.model/@api.multi/@api.one/@api.depends/@api.constrains/@api.onchange/@api.returns） | Odoo odoodays-2014《From V7 to V8: The New API》slides + odoo-80api.readthedocs.io | 8.0 `openerp/api.py` 存在上述装饰器 |
| `self.env` 取代 `self.pool`/`self.cr`/`self.uid`/`self.context`，签名去 `(cr, uid, ids, context)` | odoodays-2014 + odoo-80api | 8.0 引入 Environment / recordsets |
| `osv.Model`/`osv.osv`/`osv.osv_memory` → `models.Model`/`models.TransientModel` | 社区 sed 迁移脚本（OCA openupgrade 8.0） | `openerp.osv.osv` 别名在 8.0 移除 |
| `osv.except_osv`/`except_orm` → `openerp.exceptions.UserError` | odoo-80api + 社区脚本 | 8.0 `openerp/exceptions.py` 有 `UserError` |
| `_columns`/`_all_columns` → 类属性 `fields.Char(...)`，运行期容器 `_fields` | 社区脚本 + 8.0 源码 | 8.0 `openerp/fields.py` 字段为类属性；容器名 `_fields` |
| QWeb 报表引擎 + Bootstrap/website builder 引入 | Odoo 8.0 Release Notes | 8.0 引入 `website` 与 QWeb 报表 |
| 8.0（及更早）无 `odoo/upgrade_code/` 模块 | odoo/odoo 仓库核查 | codemod 引擎 18.0 才出现 |
| 7/8 包名仍为 `openerp`（`openerp`→`odoo` 是 9→10） | 8.0 源码 `openerp/__init__.py` | 9→10 才改名 |

## 待核实（[verify] / [EE-verify]）

| 变更 | 状态 | 备注 |
|---|---|---|
| QWeb 报表迁移细节（RML/Mako 是否仍安装、迁移步骤） | [verify] | 8.0 向后兼容 RML/Mako；迁移属推荐非强制 |
| Bootstrap 具体大版本（3.x） | [verify] | 以 8.0 `addons/web/package.json` 实机为准 |
| EE 安全微调 | [EE-verify] | 企业版 8.0 group 继承链若有微调需对照 EE 树；社区版无变化 |

## 版本作用域红线（已对照确认不属于 7→8）

- `openerp`→`odoo` 包改名 —— 9→10
- `@api.one` 完全移除 —— 11→12
- `fields.Date`/`Datetime` 运行时对象化、`from_string` 移除 —— 11→12
- `ir.actions.act_window.view` 移除 —— 11→12
- `account.invoice`→`account.move` —— 12→13
- `t-field-options`→`t-options` —— 11→12
- `res.partner.address` 移除、`osv.osv`→`osv.Model` 基类改名 —— 6→7
- Workflow 完全移除 —— 11→12（8.0 仍有 workflow）
