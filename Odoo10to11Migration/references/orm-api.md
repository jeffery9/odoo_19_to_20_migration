# 10→11 ORM / Python API 映射表（源码核对版）

> 来源：Odoo 官方 `python3.rst`（11.0）+ OCA 10.0 指南 + 社区经验帖（Anil Kesariya 等）+ 11.0 源码核对。
> 作用域：仅 10→11 破坏性变更。更晚改动（`@api.one` 移除、`fields.Date` 对象化、`parent_path`）属 11→12，不在本表。

## 1. Python 3 强制  — CONFIRMED

- 11.0 是首个**仅 Python 3**（≥3.5）的 LTS；10.0 仍双兼容。
- 必须改写：`print` 语句→`print()`；`iteritems/itervalues/iterkeys`→`items/values/keys`；`has_key`→`in`；`unicode/basestring`→`str`；`xrange`→`range`；`except E, e:`→`except E as e:`；`StringIO/cStringIO`→`io.StringIO/io.BytesIO`；`urllib/urllib2`→`urllib.request`/`werkzeug.urls`；整除用 `//`。
- `openerp.tools.pycompat` 垫片（`izip/imap/ifilter/unichr/text_type/string_types/to_native`）在 11.0 移除，不可再依赖。
- 同目录相对导入强制：`from . import sub`。
- 扫描 id：`py2-syntax`（正则覆盖 `print\s+["'\w]|iteritems|itervalues|has_key|basestring|\bxrange\b|except\s+\w+\s*,\s*\w+\s*:|StringIO|cStringIO|urllib2`）。

## 2. 包命名空间 `openerp` → `odoo`  — CONFIRMED（9→10 主改名，11.0 清别名）

- 9→10 已要求 `from openerp` → `from odoo`；11.0 删除 `openerp` 兼容别名，残留即 `ImportError`。
- 扫描 id：`openerp-import`（正则 `from openerp|import openerp`）。

## 3. 工作流（Workflow）完全移除  — CONFIRMED

- 11.0 移除工作流引擎；`workflow` XML、`type="workflow"` 按钮、`signal_workflow()` 全部失效。
- 替代：状态字段 + `@api.multi` 方法 + `<button type="object">`。
- 扫描 id：`workflow`（正则 `\bworkflow\b|signal_workflow|type="workflow"`）。

## 4. 报表 API 重写  — CONFIRMED

- `render_html(self, docids, data)` → `get_report_values(self, docids, data=None)`，直接 `return` 渲染上下文 dict。
- `self.env['report'].get_action(...)` → `self.env.ref(<action_xmlid>).report_action(self, data=...)`。
- `get_html()` → `render_qweb_html()`。
- 扫描 id：`report-api`（正则 `render_html|get_action|get_html`）。

## 5. `ir.cron`：`model` → `model_id`  — CONFIRMED

- `model`（字符串 eval）→ `model_id`（ref 到 `ir.model`）；新增强 `code` 字段直接写 Python。
- 扫描 id：`ir-cron-model`（正则 `name="model"` 配合 `model="ir.cron"`，或 `model\s*=\s*eval=.*'[^']*'` 在 cron 记录内）。

## 红线（勿套用更晚版本）

- `@api.one` 移除 → 11→12；`fields.Date`/`Datetime` 对象化 → 11→12；
- `ir.actions.act_window.view` 移除 → 11→12；`do_notify/do_warning` 移除 → 11→12；
- `t-field-options`→`t-options` → 11→12；`parent_path` → 11→12；
- `from openerp`→`from odoo` 主改名 → 9→10；`__openerp__.py`→`__manifest__.py` → 9→10。
