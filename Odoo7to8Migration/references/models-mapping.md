# 7→8 模块 / 模型 / 字段映射表（源码核对版）

> 来源：Odoo 8.0 Release Notes + OCA `openupgrade` 8.0 脚本 + 社区 sed 迁移脚本核对。
> 作用域：仅 **7.0 → 8.0**。本版本对**无**大规模模型重命名
> （`account.invoice`→`account.move`、 `stock.quant qty`→`quantity`、 `customer_rank`
> 均不在 7→8）；主要变化是**字段声明方式**与**基类**的改写。

## 7.0 → 8.0 映射总表

| 7.0 | 8.0 | 类别 | 可信度 |
|---|---|---|---|
| `osv.osv` / `osv.Model` 基类 | `models.Model` | 模型基类 | CONFIRMED |
| `osv.osv_memory` / `osv.TransientModel` | `models.TransientModel` | 向导基类 | CONFIRMED |
| `_columns = { 'name': fields.char(...) }` | `name = fields.Char(...)` | 字段声明 | CONFIRMED |
| `self.pool.get('x')` | `self.env['x']` | 取模型 | CONFIRMED |
| `self.cr` / `self.uid` / `self.context` | `self.env.cr` / `self.env.uid` / `self.env.context` | 环境访问 | CONFIRMED |
| `def meth(self, cr, uid, ids, context=None)` | `@api.multi def meth(self)`（recordsets） | 方法签名 | CONFIRMED |
| `osv.except_osv(...)` / `except_orm(...)` | `raise UserError(...)` | 异常 | CONFIRMED |
| `_columns` / `_all_columns` 容器 | `_fields` | 字段容器 | CONFIRMED |
| RML / Mako 报表（`report_type="rml"`） | QWeb 报表（`report_type="qweb-pdf"`） | 报表引擎 | [verify] |

## 字段类型名映射（new-API 字段类）

| 7.0 旧字段工厂（openerp.osv.fields） | 8.0 new-API 字段类 |
|---|---|
| `fields.char(size=64)` | `fields.Char(string=..., size=64)` |
| `fields.text()` | `fields.Text(...)` |
| `fields.boolean()` | `fields.Boolean(...)` |
| `fields.integer()` | `fields.Integer(...)` |
| `fields.float()` | `fields.Float(...)` |
| `fields.date()` / `fields.datetime()` | `fields.Date(...)` / `fields.Datetime(...)` |
| `fields.selection(...)` | `fields.Selection(...)` |
| `fields.many2one(...)` / `one2many` / `many2many` | `fields.Many2one` / `fields.One2many` / `fields.Many2many` |
| `fields.function(...)` / `fields.related(...)` | `fields.*` + `@api.depends` / `compute=` / `related=` |

要点：旧 `fields.function` 计算字段改为 `compute=` + `@api.depends`；旧 `fields.related`
改为 `related=`（自动只读）。`fields.Char` 等 new-API 类统一支持 `string=`、 `required=`、
`default=`、 `index=` 等关键字。

## 本版本对**不涉及**的重大重命名（红线，属更晚版本）

- `account.invoice` → `account.move` —— **12→13**
- `customer` / `supplier` → `customer_rank` / `supplier_rank` —— **12→13**
- `stock.quant` `qty` → `quantity` —— **12→13** `[verify]`
- `src_model` → `binding_model` —— **12→13**
- `ir.actions.act_window.view` 移除 —— **11→12**
- `t-field-options` → `t-options` —— **11→12**
- `payment.acquirer` → `payment.provider` —— **15→16**
- `res.partner.address` 移除 —— **6→7**（7.0 已完成；7→8 不涉及）

## 数据库迁移

- 旧 `_columns` 字典在 8.0 仍被 ORM 内部兼容读取（向后兼容一层），但**正式**改为
  类属性字段声明；表结构（列）通常不变，由 OpenUpgrade 处理列定义微调。
- 新 `@api.constrains` / `@api.depends` 字段无需 DB 结构变更；纯代码层改写。
- 报表从 RML 迁 QWeb 属可选优化，不影响既有 RML 报表安装（`report_type="rml"` 仍可用）。
