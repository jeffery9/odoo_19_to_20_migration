# 8→9 ORM / Python API 映射表（源码核对版）

> 来源：Odoo 9.0 Release Notes + oejia.net《Odoo 8 到 9 升级分析》+ 8.0/9.0 源码核对。
> 作用域：仅 8→9 破坏性变更。更晚改动（`openerp`→`odoo` 包改名属 9→10；`@api.one` 移除 / `fields.Date` 对象化 / `parent_path` 属 11→12）不在本表。

## 1. 异常体系：`osv.except_osv` / `except_orm` → `openerp.exceptions.UserError`  — CONFIRMED

- 8.0 用 `osv.except_osv`（`from openerp.osv import osv`）与 `except_orm` 别名报错。
- 9.0 统一改用 `openerp.exceptions.UserError`（以及 `ValidationError`）。
- 替换示例：

```python
# 8.0
from openerp.osv import osv
raise osv.except_osv(_('Error'), _('msg'))
raise except_orm(_('Error'), _('msg'))

# 9.0
from openerp.exceptions import UserError
raise UserError(_('msg'))
```

- 扫描 id：`except-osv`（正则 `osv\.except_osv|except_orm`）。

## 2. `ir.model`：`osv_memory` 字段 → `transient`，方法移除  — CONFIRMED

- 字段 `osv_memory`（布尔）改名为 `transient`。
- 方法 `_is_osv_memory` 与 `_search_osv_memory` 在 9.0 移除；调用/覆写需删除。
- 扫描 id：`osv-memory-field`（正则 `_is_osv_memory|_search_osv_memory|osv_memory`）。

## 3. `osv_memory_autovacuum` 模型 → `ir_autovacuum`  — CONFIRMED

- 瞬态记录清理模型从 `osv_memory_autovacuum` 改名为 `ir_autovacuum`。
- 所有 Python 调用、XML-ID、数据文件引用同步改名。
- 扫描 id：`autovacuum`（正则 `osv_memory_autovacuum`）。

## 4. `ir.cron`：新增 `method_direct_trigger`  — CONFIRMED（增量）

- 9.0 在 `ir.cron`（`ir_cron`）新增 `method_direct_trigger` 方法，可从代码直接触发一次任务。
- 非破坏；仅作知识留痕，无需为迁移做修改。

## 5. 旧 API 自动转换与 New API 期望  — CONFIRMED

- 9.0 仍自动转换旧 API（`cr, uid, ids, context`），旧签名可运行。
- New API 装饰器（`@api.model` / `@api.multi` / `@api.one`）在 9.0 仍存在（移除属 11→12）。
- 新代码建议带 `@api.*` 装饰器；不要在 8→9 删除 `@api.one`。

## 6. 红线

- `from openerp`→`from odoo` 包改名 → 9→10；
- `@api.one` 移除、`fields.Date` / `fields.Datetime` 运行时对象化、`from_string` 移除 → 11→12；
- `_parent_store`：`parent_left`/`parent_right` → `parent_path` → 11→12；
- `ir.actions.act_window.view` 移除 → 11→12；
- New API 装饰器、`self.env`、`osv.Model`→`models.Model` → 7→8；
- `account.invoice`→`account.move` → 12→13。
