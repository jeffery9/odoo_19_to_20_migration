# Odoo 迁移烹饪书：8.0 → 9.0

> 配套技能：`Odoo8to9Migration/`（SKILL + 6 份参考表 + 扫描器）
> 作用域：仅 **8.0 → 9.0** 破坏性变更。更晚改动（如 9→10 的 `openerp`→`odoo` 包改名、11→12 的 `@api.one` 移除 / `fields.Date` 运行时对象化 / `parent_path` 等）一律不在本卷。

## 目录

1. 导言与版本作用域
2. 头号断裂：Community / Enterprise 版本拆分
3. 异常：`osv.except_osv` / `except_orm` → `openerp.exceptions.UserError`
4. `ir.model`：`osv_memory` 字段 → `transient`，`_is_osv_memory` / `_search_osv_memory` 移除
5. `osv_memory_autovacuum` 模型 → `ir_autovacuum`
6. `ir.cron`：新增 `method_direct_trigger`（增量，非破坏）
7. 旧 API 自动转换与 New API 期望
8. 视图 / QWeb / 前端（Material Design）
9. HTTP / 邮件 / 二进制（基本不变）
10. 模块 / 模型 / 字段映射（Enterprise 拆分）
11. 安全与 `res.groups`（8→9 基本不变）
12. 测试与校验
13. `upgrade_code` codemod（9.0 无）
14. 迁移实战清单
15. 附录 A：研究来源与溯源

---

## 1. 导言与版本作用域

Odoo **9.0（2015-10）** 引入了 **Community（社区版）/ Enterprise（企业版）** 的版本拆分，并对框架做了一批清理：异常体系从 `osv.except_osv` 切换到 `openerp.exceptions.UserError`；`ir.model` 的 `osv_memory` 字段改名为 `transient`，并移除了 `_is_osv_memory` / `_search_osv_memory` 两个方法；`osv_memory_autovacuum` 模型改名为 `ir_autovacuum`；`ir.cron` 新增 `method_direct_trigger` 方法（增量）。本卷只覆盖 **8.0 → 9.0** 区间。

> 注意：8.0 与 9.0 **都仍使用 `from openerp import ...`**。`openerp`→`odoo` 的包改名发生在 **9→10**，不属于本卷。New-API 装饰器（`@api.model` / `@api.multi` / `@api.one`）在 8.0 已经存在，本卷不涉及其移除（那是 11→12）。

### 版本作用域红线（勿套用更晚版本的改动）

- `from openerp import ...` → `from odoo import ...` 包改名 → **9→10**（8/9 都用 `openerp`）。
- `@api.one` 装饰器移除、`fields.Date` / `fields.Datetime` 运行时对象化、`from_string` 移除 → **11→12**。
- `_parent_store`：`parent_left`/`parent_right` → `parent_path` → **11→12**。
- `ir.actions.act_window.view` 模型移除 → **11→12**。
- New-API 装饰器（`@api.model`/`@api.multi`/`@api.one`/`@api.depends`/`@api.constrains`/`@api.onchange`）、`self.env`、`osv.Model`→`models.Model` → **7→8**（8.0 已完成）。
- `account.invoice`→`account.move` → **12→13**。

> 本卷只处理 8→9 区间；任何属于 9→10 / 11→12 / 7→8 / 12→13 的条目，仅在本卷"红线"处点名，不展开。

### 配套技能参考表（skill references）

- `Odoo8to9Migration/references/orm-api.md` —— 异常替换、`ir.model` osv_memory→transient、`ir_autovacuum`、`ir.cron` method_direct_trigger、旧 API 转换。
- `Odoo8to9Migration/references/views-qweb.md` —— 视图 / QWeb / 前端（Material Design 注记）。
- `Odoo8to9Migration/references/models-mapping.md` —— Community/Enterprise 拆分涉及的模块重映射。
- `Odoo8to9Migration/references/security.md` —— `res.groups` / 访问权限在 8→9 基本不变。
- `Odoo8to9Migration/references/http-rpc-mail.md` —— 控制器 / 邮件 / 二进制（基本不变）。
- `Odoo8to9Migration/references/upgrade-code.md` —— 9.0 无 `upgrade_code` codemod，全部手工。

---

## 2. 头号断裂：Community / Enterprise 版本拆分  — CONFIRMED（含 [verify] / [EE-verify]）

9.0 把 Odoo 拆分为 **Community** 与 **Enterprise** 两个版本。大量过去在核心的模块被移到了付费的 **Enterprise** 版。对自定义模块的实际影响主要是两类：

1. 如果自定义模块 `depends` 了一个变成 Enterprise-only 的模块，那么该依赖现在需要 Enterprise 版才能满足。
2. 部分 XML-ID / 模型随模块迁移而移动。

### 常见变为 Enterprise-only 的模块（[verify] / [EE-verify]，以 9.0 EE 树为准）

| 模块 | 去向 | 标注 |
|---|---|---|
| `account_voucher`（凭证） | Enterprise | [EE-verify] |
| `account_analytic_plan`（分析会计计划） | Enterprise | [EE-verify] |
| `document`（文档管理） | Enterprise | [EE-verify] |
| `marketing`（营销） | Enterprise | [EE-verify] |
| `crm` 的部分企业特性 | Enterprise | [EE-verify] |
| `hr` 的部分企业特性 | Enterprise | [EE-verify] |
| `website` 的部分企业特性 | Enterprise | [EE-verify] |

> 自定义模块若 `depends` 上述模块，升级到 9.0 前需确认在 Community 版是否仍可用，否则需迁移功能或明确要求 Enterprise。扫描 id：`enterprise-split`（保守匹配已知集合 `account_voucher|account_analytic_plan|document|marketing`，命中即标 [verify]）。

---

## 3. 异常：`osv.except_osv` / `except_orm` → `openerp.exceptions.UserError`  — CONFIRMED

8.0 中报错常用 `osv.except_osv` 或 `except_orm`；9.0 统一改用 `openerp.exceptions.UserError`（以及 `ValidationError` 等）。

### Before（8.0）

```python
from openerp.osv import osv

raise osv.except_osv(_('Error'), _('Something wrong'))
# 旧式 ORM 异常别名
raise except_orm(_('Error'), _('Something wrong'))
```

### After（9.0）

```python
from openerp.exceptions import UserError

raise UserError(_('Something wrong'))
```

要点：

- `osv.except_osv` → `from openerp.exceptions import UserError` + `raise UserError(...)`。
- `except_orm` 同样是旧 ORM 异常别名，一并改为 `UserError`（或 `ValidationError`，语义更贴切时）。
- 扫描 id：`except-osv`（正则 `osv\.except_osv|except_orm`）。

---

## 4. `ir.model`：`osv_memory` 字段 → `transient`，`_is_osv_memory` / `_search_osv_memory` 移除  — CONFIRMED

`ir.model`（`ir_model`）模型在 9.0 做了清理：

- 字段 `osv_memory`（布尔，标记瞬态模型）改名为 `transient`。
- 方法 `_is_osv_memory` 与 `_search_osv_memory` 被移除。任何对这两个方法的调用或覆写都需删除。

### Before（8.0）

```python
# 覆写或调用 ir.model 的瞬态判定
def _is_osv_memory(self, cr, uid, ids, field_name, arg, context=None):
    ...
# 字段名为 osv_memory
'model': fields.boolean('osv_memory'),
```

### After（9.0）

```python
# 字段改名 transient
'model': fields.boolean('transient'),
# 删除 _is_osv_memory / _search_osv_memory 覆写
```

要点：

- 字段 `osv_memory` → `transient`（在自定义代码里若读取/写入该字段名须同步）。
- 方法 `_is_osv_memory`、`_search_osv_memory` 已不存在，删除覆写与调用。
- 扫描 id：`osv-memory-field`（正则 `_is_osv_memory|_search_osv_memory|osv_memory`）。

---

## 5. `osv_memory_autovacuum` 模型 → `ir_autovacuum`  — CONFIRMED

8.0 负责清理瞬态（wizard）记录的自动化模型名为 `osv_memory_autovacuum`；9.0 改名为 `ir_autovacuum`（挂在 `ir` 命名空间下，与 `ir.cron` 等系统模型一致）。

### Before（8.0）

```python
self.env['osv_memory_autovacuum']._gc_wizard_records()
```

### After（9.0）

```python
self.env['ir_autovacuum']._gc_wizard_records()
```

要点：

- 所有对 `osv_memory_autovacuum` 模型的引用（Python 调用、XML-ID、数据文件）改名 `ir_autovacuum`。
- 扫描 id：`autovacuum`（正则 `osv_memory_autovacuum`）。

---

## 6. `ir.cron`：新增 `method_direct_trigger`  — CONFIRMED（增量，非破坏）

9.0 在 `ir.cron`（`ir_cron`）上新增了 `method_direct_trigger` 方法，允许从代码直接触发一次定时任务（无需等待间隔）。这是**增量**变更，不破坏既有代码，但值得记录以便迁移时利用：

```python
self.env.ref('my_module.my_cron').method_direct_trigger()
```

> 本卷无需为它做修改，仅作知识留痕；真正的破坏性修复集中在第 3/4/5 节与第 2 节的 Enterprise 拆分。

---

## 7. 旧 API 自动转换与 New API 期望  — CONFIRMED

9.0 仍保留对旧 API（`cr, uid, ids, context` 参数风格）的**自动转换**——旧式方法签名在 9.0 还能跑。但官方期望自定义模块使用 **New API**（`@api.model` / `@api.multi` / `@api.one` 等装饰器 + `self.env`）。

要点：

- `@api.one` / `@api.multi` / `@api.model` 在 9.0 **仍然存在**（它们的移除是 11→12，不属本卷）。
- 新写方法应带 `@api.*` 装饰器；遗留旧 API 方法在 9.0 仍可运行，但建议逐步迁移到 New API。
- 不要在 8→9 阶段删除 `@api.one`（那是 11→12 的事）。

---

## 8. 视图 / QWeb / 前端（Material Design）  — CONFIRMED（含 [verify]）

9.0 引入了 **Material Design** 风格的新 UI（Odoo 9 Release Notes 明确提及 UI 全面 Material 化）。视图层面：

- 视图标签（`<form>` / `<tree>` / `<field>`）语法 8→9 基本兼容，无破坏性改动。
- QWeb 模板 `t-*` 指令语义保持。
- 前端整体换肤为 Material Design，自定义 CSS / 模板若硬编码了旧样式类名，可能需要适配。

> `[verify]` Material Design 的具体落地细节（哪些类名变化、SCSS 变量）以 9.0 源码 `web` 模块资产为准；本卷仅作 UI 提示，不展开破坏性清单。

---

## 9. HTTP / 邮件 / 二进制（基本不变）  — CONFIRMED

- 控制器：`from openerp import http`（8.0 已是 `openerp` 包），`http.Controller` / `route()` 接口 8→9 无破坏性变更。
- 邮件：`mail.template` 渲染仍用 QWeb；接口结构 8→9 基本不变。
- 二进制字段：`fields.Binary` 用法不变；默认存 `ir.attachment` 的时机在 13.0，8→9 维持原状。

---

## 10. 模块 / 模型 / 字段映射（Enterprise 拆分）  — CONFIRMED

除第 2 节 Community/Enterprise 拆分外，8→9 模型层无大规模重命名（`account.invoice`→`account.move` 属于 12→13，不属本卷）。需要关注的：

| 项目 | 8.0 | 9.0 | 备注 |
|---|---|---|---|
| `osv.except_osv` / `except_orm` | 存在 | `openerp.exceptions.UserError` | 第 3 节 |
| `ir.model` `osv_memory` 字段 | `osv_memory` | `transient` | 第 4 节 |
| `ir.model` `_is_osv_memory` / `_search_osv_memory` | 存在 | 移除 | 第 4 节 |
| `osv_memory_autovacuum` 模型 | 存在 | `ir_autovacuum` | 第 5 节 |
| `ir.cron` `method_direct_trigger` | 无 | 新增（增量） | 第 6 节 |
| `account_voucher` / `document` 等模块 | Community | Enterprise-only | 第 2 节 [EE-verify] |

---

## 11. 安全与 `res.groups`（8→9 基本不变）  — CONFIRMED

- `security/ir.model.access.csv` 列结构（`perm_read` / `perm_write` / `perm_create` / `perm_unlink`）在 8→9 **不变**。
- `res.groups` 模型与 `implied_ids` 机制 8→9 无破坏性改动。
- 唯一需要留意的是第 2 节的 Enterprise 拆分：若自定义模块的安全规则依赖了变为 Enterprise-only 的模块，需一并审视。

---

## 12. 测试与校验

1. 用 **Python 2.7**（8.0/9.0 均为 Python 2）启动 9.0 实例；注意 9.0 仍非 Python 3。
2. `python3 Odoo8to9Migration/scripts/scan_addon.py /path/to/addons` 跑扫描，逐条处理 `enterprise-split` / `except-osv` / `osv-memory-field` / `autovacuum` 发现项（全部 `manual`，无 codemod）。
3. 安装模块：先清 `ImportError`（`osv.except_osv` 引用）；再清 `AttributeError`（`_is_osv_memory` / `osv_memory_autovacuum` 调用）。
4. `python2 -m py_compile **/*.py` 全量编译（9.0 仍是 Python 2）。
5. `openerp-bin -u <module> --test-enable` 跑测试；`--debug` 下清除 `DeprecationWarning`。

---

## 13. `upgrade_code` codemod（9.0 无）  — CONFIRMED

`odoo/upgrade_code/` 引擎自 **18.0** 才出现。9.0（以及 8.0）源码树中**不存在** `odoo/upgrade_code/` 或 `openerp/upgrade_code/` 模块。因此 8→9 的全部代码迁移（异常替换、`ir.model` 字段/方法改名、`osv_memory_autovacuum`→`ir_autovacuum`、Enterprise 依赖审计）均为**手工**映射，无自动重写脚本。数据库级变更（字段/模型结构）由 **OpenUpgrade** 或官方升级服务处理；本卷只覆盖自定义模块的**代码级**映射。

---

## 14. 迁移实战清单

- [ ] 审计 `depends`：凡 `account_voucher` / `account_analytic_plan` / `document` / `marketing` 等依赖，确认是否变 Enterprise-only（[verify]）。
- [ ] `osv.except_osv` / `except_orm` 全部改为 `from openerp.exceptions import UserError` + `raise UserError(...)`。
- [ ] `ir.model`：`osv_memory` 字段 → `transient`；删除 `_is_osv_memory` / `_search_osv_memory` 覆写与调用。
- [ ] `osv_memory_autovacuum` 全部引用 → `ir_autovacuum`。
- [ ] 遗留旧 API 方法在 9.0 仍可运行，但新代码改用 `@api.*` 装饰器（勿在 8→9 删除 `@api.one`）。
- [ ] 前端若硬编码旧样式，按 Material Design 适配（[verify]）。
- [ ] 重扫扫描器期望 0 发现；跑测试通过。

---

## 附录 A：研究来源与溯源

- Odoo 9.0 Release Notes（2015）：Community / Enterprise 版本拆分、Material Design UI。
- oejia.net 技术栈文章《Odoo 8 到 9 升级分析》：异常体系 `osv.except_osv`→`UserError`、`ir.model` osv_memory→transient、方法移除、`osv_memory_autovacuum`→`ir_autovacuum`、Enterprise 模块迁移。
- 8.0 / 9.0 源码核对：`openerp.exceptions.UserError` 可用；`ir.model` 字段 `transient`、方法移除；`ir_autovacuum` 模型存在；`ir.cron` `method_direct_trigger` 新增。
- OpenUpgrade 9.0 迁移脚本：处理数据库级结构变更（字段/模型）。
- 版本作用域红线对照：9→10 包改名（`openerp`→`odoo`）、11→12 `@api.one` 移除 / `fields.Date` 对象化 / `parent_path`、7→8 New API 引入、12→13 `account.invoice`→`account.move`。
