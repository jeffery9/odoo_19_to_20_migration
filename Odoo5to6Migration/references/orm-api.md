# 5→6 ORM / Python API 映射表（源码核对版）

> 来源：OpenERP 5.0/6.0 源码核对（`openerp.osv` / `openerp` 包）+ OCA 版本变更史。
> 作用域：仅 5→6。**ORM 层在 5→6 基本不变**——旧式写法继续有效。

## 1. ORM 写法在 5→6 不变  — CONFIRMED

- 5.0 与 6.0 都使用 `from openerp import ...`、`from openerp.osv import osv`
  与 `osv.osv` 基类，方法签名为 `def method(self, cr, uid, ids, context=None)`。
- 这些在 5→6 **不改动**；请勿在 5→6 顺手改成更晚的写法。
- 6.0 仍是 `openerp` 包（不是 `odoo`）；`openerp`→`odoo` 改名属 9→10。

## 2. 红线（勿套用更晚版本）

- `osv.osv` → `osv.Model` 基类改名 → **6→7**（5→6 仍是 `osv.osv`）。
- `cr, uid, ids, context` 旧签名 → 新 API `self.env` / `@api.model` / `@api.multi`
  → **7→8**，其中 `@api.one` 移除 → **11→12**。
- `fields.Date` / `fields.Datetime` 运行时对象化、`from_string` 移除 → **11→12**。

## 3. [verify] 框架级断言

- 5.0/6.0 文档零散，任何无法钉死到扎实来源的 ORM 行为差异一律标注 [verify]；
  以 6.0 源码 `openerp/osv/osv.py` / `openerp/modules/` 为最终核对基准。
