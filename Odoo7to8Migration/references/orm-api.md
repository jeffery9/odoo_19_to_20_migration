# 7→8 ORM / 模型 API 映射表（新 API 落地版）

> 来源：Odoo odoodays-2014《From V7 to V8: The New API》slides + odoo-80api.readthedocs.io
> + 社区 sed 迁移脚本（OCA `openupgrade` / Odoo 社区论坛）+ 8.0 源码核对。
> 作用域：仅 **7.0 → 8.0** 破坏性变更——即 Odoo 8.0 完成的 "new API" 落地。
> 更晚改动（`openerp`→`odoo` 改名、 `@api.one` 移除、 `fields.Date` 运行时对象化、
> `account.invoice`→`account.move`、 `t-field-options`→`t-options`）一律不在本表（见红线）。

## 1. New API 装饰器引入  — CONFIRMED

Odoo 8.0 正式引入一套 new-API 装饰器（`openerp.api` 模块），7.0 代码完全不存在：

- `@api.model` —— 纯模型方法（不依赖具体记录）。
- `@api.multi` —— 多记录集方法（默认语义，等价于旧 `api.multi`）。
- `@api.one` —— 自动把 `self` 拆成单条并循环；**注意返回值是 LIST**（web 客户端对
  button 动作偏好 `@api.multi` + `self.ensure_one()`，避免 list 返回问题）。
- `@api.depends` —— 计算字段依赖声明（替代旧 `_function`/`_classic_write` 的 `multi` 参数）。
- `@api.constrains` —— Python 约束（替代旧 `_constraints` 元组写法）。
- `@api.onchange` —— 表单 onchange（替代旧 `_onchange` 字典）。
- `@api.returns` —— 指定返回模型/记录的装饰器（用于 `create`/`copy` 等）。

导入方式：`from openerp import models, api, fields`。扫描 id：`api-decorators`
（正则 `@api\.(model|multi|one|depends|constrains|onchange|returns)`）。

## 2. `self.env` 取代 `self.pool` / `self.cr` / `self.uid` / `self.context`  — CONFIRMED

8.0 用 `self.env` 环境对象统一取代旧的游标/用户/上下文散装属性；方法签名去掉
`(cr, uid, ids, context=None)` 四个位置参数，改为操作 **recordsets**（记录集）。

- 7.0 旧写法：`def meth(self, cr, uid, ids, context=None): obj = self.pool.get('x'); ...`
- 8.0 新写法：`@api.multi def meth(self): recs = self; ...` 或 `@api.model`。
- 取游标：`self.env.cr`（替代 `self.cr`）；取用户：`self.env.uid`；取上下文：`self.env.context`。
- `self.pool.get('model')` → `self.env['model']`。

扫描 id：`self-pool`（正则 `self\.pool\b|self\.cr\b|self\.uid\b|self\.context\b`
及 `(cr, uid, ids, context)`）。

## 3. `osv.Model` → `models.Model`（`osv` 别名移除）  — CONFIRMED

8.0 移除了 `openerp.osv.osv` 的短别名；模型基类改为 `openerp.models` 下的 `models.Model`
与 `models.TransientModel`（向导）。

- 7.0：`class MyModel(osv.osv): _name = 'my.model'` 或 `class MyModel(osv.Model):`、
  `osv.osv_memory`（向导）、`from openerp.osv import orm`。
- 8.0：`class MyModel(models.Model): _name = 'my.model'`、`models.TransientModel`、
  `from openerp import models, api, fields`。

扫描 id：`osv-model`（正则 `osv\.osv\b|osv\.osv_memory|from openerp\.osv import orm|osv\.Model|osv\.TransientModel`）。

## 4. `osv.except_osv` / `except_orm` → `UserError`  — CONFIRMED

8.0 用 `openerp.exceptions.UserError`（亦可 `except_orm` 的等价替代）取代旧异常：

- 7.0：`raise osv.except_osv(_('Title'), _('message'))` 或 `except_orm(...)`。
- 8.0：`from openerp.exceptions import UserError; raise UserError(_('message'))`。

> 注意：8.0 仍保留 `Warning`（= `UserError` 别名）与 `RedirectWarning`，按需使用；
> 但 `osv.except_osv` 已删除。

扫描 id：`except-osv`（正则 `osv\.except_osv|except_orm`）。

## 5. 字段改为类属性：`_columns` → `fields.Char(...)`  — CONFIRMED

8.0 引入 new-style 字段，直接在类体上声明为类属性；旧的 `_columns` / `_all_columns`
字典写法被废弃（运行期字段容器统一为 `_fields`）。

- 7.0：`_columns = { 'name': fields.char('Name', size=64) }`。
- 8.0：`name = fields.Char(string='Name', size=64)`；`from openerp import fields`。
- 旧 `fields.char` / `fields.text` 等函数式字段工厂（来自 `openerp.osv.fields`）应改为
  `fields.Char` / `fields.Text` 等 new-API 字段类。
- 运行期对象上字段容器名为 `_fields`（替代 `_columns` / `_all_columns`）。

扫描 id：`fields-attr`（正则 `_columns\b|_all_columns\b`）。

## 6. `@api.one` 返回 LIST 的客户端注意  — CONFIRMED（非扫描断点，仅文档）

`@api.one` 包裹的方法，web 客户端调用时返回值是单条结果的 **list**，不像旧
`@api.multi` 那样直接返回记录。对 button 动作方法，推荐改用
`@api.multi` + `self.ensure_one()` 以拿到干净的返回值，避免前端拿到 list 包装。

## 红线（勿套用更晚版本、或不属于本对的改动）

- `openerp`→`odoo` 包改名 —— **9→10**（7/8 一律用 `from openerp import ...`）。
- `@api.one` 完全移除 —— **11→12**（8.0 仍保留 `@api.one`）。
- `fields.Date` / `fields.Datetime` 运行时对象化、`from_string` 移除 —— **11→12**。
- `ir.actions.act_window.view` 模型移除 —— **11→12**（8.0 仍为 act_window.view）。
- `account.invoice`→`account.move` —— **12→13**。
- `t-field-options`→`t-options` —— **11→12**。
- `res.partner.address` 移除、`osv.osv`→`osv.Model` 基类改名 —— **6→7**（7.0 已完成；
  7→8 只做 `osv.Model`→`models.Model`，**不是** `osv.osv`→`osv.Model`）。
- Workflow 在 8.0 **仍然存在**（11.0 才完全移除）——勿在 7→8 提前删除 workflow。
