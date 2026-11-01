# 9→10 ORM / Python API 映射表（源码核对版）

> 来源：OCA `Migration to version 10.0` + Odoo 10.0 源码核对。
> 作用域：仅 9→10 破坏性变更。更晚改动（`@api.one` 移除、`fields.Date` 对象化、Python 3 强制）属 11→12 / 10→11，不在本表。

## 1. 包改名 `openerp` → `odoo`  — CONFIRMED

- 9.0 框架包为 `openerp`；10.0 正式改名为 `odoo`，`openerp` 包不再有效。
- 所有 `from openerp import ...` / `import openerp` 改为 `from odoo import ...` / `import odoo`。
- `openerp.addons.*` 路径改为 `odoo.addons.*`；控制器 `from openerp import http` 改为 `from odoo import http`。
- 扫描 id：`openerp-import`（正则 `from openerp|import openerp`）。

## 2. 清单文件 `__openerp__.py` → `__manifest__.py`  — CONFIRMED

- 模块声明文件改名；9.0 的 `__openerp__.py` 在 10.0 不被识别。
- 字典键（`name`/`depends`/`data`/`version` 等）格式不变，仅文件名变化。
- 扫描 id：`manifest-rename`（正则 `__openerp__`，并检测文件名 `__openerp__.py`）。

## 3. 字段索引 `select = True` → `index = True`  — CONFIRMED

- 字段建索引属性 `select = True` / `select=1` 改为 `index = True`。
- 扫描 id：`select-index`（正则 `select\s*=\s*True|select\s*=\s*1`）。

## 4. `copy` 方法装饰器 `@api.one` → `@api.multi`  — CONFIRMED

- OCA 明确要求 `copy` 方法的 `@api.one` 改为 `@api.multi`。
- 方法体若假设单记录，加 `self.ensure_one()` 或 `for record in self:`。
- 注意：不要将 `@api.one` 与 `@api.onchange` 混用（9.0/10.0 上会崩溃），仅作提醒，不属扫描模式。
- 扫描 id：`copy-decorator`（正则 `@api\.one[\s\S]{0,200}?def\s+copy|def\s+copy[\s\S]{0,200}?@api\.one`）。

## 红线（勿套用更晚版本）

- `@api.one` 完全移除 → 11→12；`fields.Date`/`Datetime` 运行时对象化、`from_string` 移除 → 11→12；
- Python 3 强制、工作流移除、报表 `render_html`→`get_report_values` → 10→11；
- `account.invoice`→`account.move` → 12→13；`t-field-options`→`t-options` → 11→12。
