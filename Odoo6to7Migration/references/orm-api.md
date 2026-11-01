# 6→7 ORM / 模型 API 映射表（源码核对版）

> 来源：OpenERP 7.0 源码 `openerp.osv` + 官方 Release Notes + 论坛 v6→v7 讨论 + dbi-services 博文。
> 作用域：仅 6→7 破坏性变更。更晚改动（`models.Model` / `@api.*` / `self.env` / `UserError` 取代 `osv.except_osv` → 7→8；`openerp`→`odoo` → 9→10）一律不在本表。

## 1. `osv.osv` → `osv.Model`  — CONFIRMED

- 6.0：模型继承 `osv.osv`（来自 `from openerp.osv import osv`）。
- 7.0：推荐改用 `osv.Model`；`osv.osv` 仍可用但被标记为弃用别名，将在后续版本被压制。
- 向导（transient）模型：`osv.osv_memory` → `osv.TransientModel`。
- 替代写法：

  ```python
  from openerp.osv import osv, fields

  class my_model(osv.Model):
      _name = 'my.model'
      _columns = {'name': fields.char('Name', size=64)}

  class my_wizard(osv.TransientModel):
      _name = 'my.wizard'
      _columns = {'value': fields.float('Value')}
  ```

- 扫描 id：`osv-base`（正则 `osv\.osv\b|osv\.osv_memory|class \w+\(osv\.osv\)|class \w+\(osv\.osv_memory\)`）。

## 2. 方法签名仍是旧 API（`cr, uid, ids, context`）  — CONFIRMED（文档性条目）

- 6→7 继续使用旧 API：方法显式接收 `cr, uid, ids, context=None`，通过 `self.pool.get('model')` 取模型并显式传游标/用户/ID 调用 `browse` / `write` / `create`。
- 6.0/7.0 都用 `from openerp import ...`（包名是 `openerp`，不是 `odoo`）。
- 新 API `@api.model` / `@api.multi` / `@api.one` / `models.Model` / `self.env` 在 **7→8** 才出现——本表不覆盖，也不要在 6→7 提前改写。
- `osv.except_osv` 在 6/7 仍可用；被 `UserError` 取代是 **7→8** 的事。

## 3. 红线（勿套用更晚版本）

- `osv.Model` → `models.Model` / `@api.*` / `self.env` → 7→8；
- `openerp` → `odoo` → 9→10；`__openerp__.py` → `__manifest__.py` → 9→10；
- `@api.one` 移除 / `fields.Date` 对象化 → 11→12。6→7 全部保留旧写法。
