# 18→19 研究来源查证地图（中间产物 · 修订时复用）

> 本文件是 18→19 迁移 **Cookbook（`Odoo_Migration_Cookbook_18_to_19.md`）** 与 **Skill（`Odoo18to19Migration/`）** 的"查证地图"。
> 用途：将来修订（核实 `[verify]` 项、补充内容、或把 Cookbook 渲染成 PDF）时，直接按本图去对应来源复核，无需从零检索。
> 所有变更最终须对照 `github.com/odoo/odoo` 的 **`18.0` / `19.0`** 分支（EE 项对照 Enterprise 19.0 树）确认。

## 一、官方来源（odoo.com/19.0 ORM Changelog 及 PR）

| PR | 变更 | 归属版本 | 状态 |
|---|---|---|---|
| #193636 | `record._cr/_uid/_context` 弃用（→ `env.cr/uid/context`） | 19.0 | CONFIRMED |
| #217708 | `odoo.osv` 弃用（→ `from odoo import Domain`） | 19.0 | CONFIRMED |
| #163300 | `read_group` → `_read_group(aggregates=)` | 18.2 | CONFIRMED（18 起弃用） |
| #183636 | 控制器 `type='json'` → `type='jsonrpc'` | 18.1 | CONFIRMED |
| #170009 | `Domain` API（`from odoo import Domain`） | 18.1 | CONFIRMED |
| #179148 | `check_access` / `has_access` / `_filtered_access` | 18.0 | CONFIRMED |
| #191549 | 等式归一化（`=` 等价于 `in`） | 18.3 | CONFIRMED |
| #134677 | `SQL(...)` 包装对象 | 17.0 | CONFIRMED（18→19 不变） |
| #144747 | `_flush_search` 弃用 | 17.1 | CONFIRMED（18 起） |
| #127353 | `group_operator` → `aggregator` | 17.2 | **排除**（非 18→19） |

## 二、社区来源（交叉核实 · 各机构证实的 18→19 变更）

- **Cybrosys**：`web_editor→html_editor/html_builder`、`res.groups` privilege（`category_id→privilege_id` 等）、`_sql_constraints→models.Constraint`、UoM 字段改名（`factor_inv→relative_factor` 等）、`res.partner.title` 删除、`res.partner.mobile` 删除、`res.users.groups_id→group_ids`、`authenticate()` 签名、`t-esc→t-out`、`odoo.osv` 弃用、`registry` 导入、`xlsxwriter` 导入。
- **SDLC Corp**：`res.groups` privilege、`uom.category` 删除、`stock.quant.package→stock.package`、`procurement.group→stock.reference`、`hr.contract→hr.version`、`web_editor` 拆分、`_sql_constraints→Constraint`、`tax_id→tax_ids`、`product_uom→product_uom_id`、`kanban-box→card`。
- **ERP Consulting 24**：`res.groups` privilege、`web_editor` 拆分、`_sql_constraints→Constraint`、`tax_id→tax_ids`、`product_uom→product_uom_id`、`_apply_ir_rules→_search`、`authenticate()`、`kanban-box→card`、`res.partner.title` 删除。
- **Octura**：`uom.category` 删除、UoM 字段改名。
- **LineScripts**：`odoo/orm` 包拆分、内部 import 移除（`from odoo.api import ...`）、`@api.returns` 移除、`_sql_constraints→Constraint`、`toggle_active→action_archive/unarchive`、`get_module_resource` 移除、`odoo/conf` 移除、`registry` 导入、XML view 向后兼容、`web_editor` 拆分、`t-set` hoist（codemod `19.1-00`，属 19.x Online）、`account*` EE 模块改名。
- **DeployMonkey**：`@api.model_create_multi` 强制、`web_editor` 拆分、`_sql_constraints→Constraint`、`precompute` 默认化。
- **mindscript**：`res.city` `zip→zipcode`、`res.partner.mobile` 删除、`type='json'` 线协议不变（仅 Python `type=` 值改）、external RPC 弃用注记、upgrade-auditor（`target='inline'` 移除注记）。
- **真实 19.0 模块 `eh_hr_compat`**：硬编码 16–18→19 字段翻转（`res.groups` `category_id→privilege_id`、`groups_id→group_ids`、`users→user_ids`；`res.users` `groups_id→group_ids`）——**强证据**，印证 privilege 模型重构。

## 三、修订核实入口

- **CE 差异**：`github.com/odoo/odoo` 分支 `18.0` vs `19.0`（grep 模型 / 字段 / 方法名）。
- **EE 差异**：Enterprise 19.0 树（账户 / HR 模块改名）。
- **codemod 清单**：`odoo/upgrade_code/`——脚本名前缀即版本（`18.1-00-sql-constraint`），据此前缀判断某脚本是否属于 18→19（`--to ≤ 19.0` 才生效）。
- **一致性校验**：修订后跑 `python3 work/18to19/check_cookbook_consistency.py`，确保 Cookbook 与 Skill references 不漂移。

## 四、19.0 源码核实记录（2026-11-01，本轮"完善 18→19"）

> 方法：抓取 `raw.githubusercontent.com/odoo/odoo/19.0` 的源码交叉验证。注意 19.0 已将单体 `odoo/api.py`、`odoo/models.py`、`odoo/fields.py` 迁至 **`odoo/orm/`** 包（`decorators.py`/`models.py`/`fields.py`/`fields_properties.py`），`odoo/conf` 包整体移除；社区插件（stock/hr 等）路径在 19.0 已迁移，公开 raw 无法定位，故 stock/hr 模型改名未源码核实。

### 已确认 / 纠正（关闭追踪表 #1,#2,#3,#6,#7,#12,#13,#18）

| 项 | 核实文件（19.0） | 结论 |
|---|---|---|
| `odoo/conf` 移除 | `odoo/conf/__init__.py` → **404** | 移除，用 `odoo.tools.config` |
| `get_module_resource` 替代 | `odoo/modules/__init__.py` 导出 `get_resource_from_path` | 用 `get_resource_from_path` / `pathlib` |
| `check_field_access_rights` 改名 | `odoo/orm/models.py` 调用 `_has_field_access(field, mode)` | → `_has_field_access`；社区称 `_check_field_access` 不实 |
| `precompute` 默认值 | `odoo/orm/fields.py`：`precompute: bool = False` | 默认 **False**（非 True） |
| `compute_sudo` 默认值 | `odoo/orm/fields.py`：`attrs['compute_sudo'] = attrs.get('compute_sudo', store)` | 跟随 `store`，非一律 True |
| `<tree>` 移除 | `odoo/addons/base/models/ir_ui_view.py`：`type` 选单仅 `list` | `<tree>` 报 `Invalid view type` |
| `target='inline'` 移除 | `odoo/addons/base/models/ir_actions.py`：`target` 选单 `current/new/fullscreen/main` | `inline` 非法 |
| `fields.Property` | `odoo/orm/fields_properties.py`：`Property` 为 `abc.Mapping`；字段是 `fields.Properties`（未弃用） | "fields.Property 弃用"之说不实 |
| `odoo.osv` 弃用 | `odoo/osv/__init__.py`：`warnings.warn("Since 19.0, odoo.osv is deprecated use odoo.fields.Domain")` | 用 `odoo.fields.Domain`（与 #217708 一致） |

### 未证实 / 保留 `[verify]`（追踪表 #4,#5,#8,#9,#10,#11,#14,#15,#16,#17 + E1–E4）

- `@api.model_create_multi` 强制：复核 `odoo/orm/decorators.py`，`model_create_multi` 仅把单 dict 归一为列表，**未见硬告警**——疑不实。
- `<record>` 须声明 `model` / `oe_button_box` 无 `name` 不被支持：复核 `ir_ui_view.py`，`model` 非 `required`、全文无 `oe_button_box`——疑非真实 18→19 改动。
- `stock.quant.package→stock.package`、`procurement.group→stock.reference`、`hr.contract→hr.version`、`hr.candidate→hr.applicant`：因 19.0 社区插件路径迁移，公开 raw 无法定位；`hr.candidate→hr.applicant` 尤其疑为早于 18.0 的改名（作用域风险）。
- EE 模块改名（E1–E4）：仅社区(LineScripts)来源，需对照 EE 19.0 树。
