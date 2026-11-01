# Odoo 迁移烹饪书：7.0 → 8.0（新 API 落地）

> 本烹饪书是 **7→8** 迁移的事实基准（Fact Baseline）。配套技能见 `Odoo7to8Migration/`。
> 它专为**自定义模块**（CE 与 EE）从 Odoo 7 升级到 8 编写，覆盖所有破坏性（breaking）变更，
> 并明确**版本作用域**——只收 7→8 区间内真实发生的变更（即 Odoo 8.0 完成的 "new API" 落地），
> 更晚版本的改动一律排除（见第 1 章红线）。
>
> **可信度标记**：`CONFIRMED` = Odoo odoodays-2014《From V7 to V8: The New API》slides +
> odoo-80api.readthedocs.io + 社区 sed 迁移脚本交叉核实；`[verify]` = 单一社区来源或来源间有分歧、
> 待 8.0 实机/源码最终确认；`[EE-verify]` = 仅企业版且待核实。

---

## 目录

1. 导言与版本作用域
2. 头号断裂：New API 装饰器引入（@api.model / @api.multi / @api.one / @api.depends / @api.constrains / @api.onchange / @api.returns）
3. ORM 环境：self.env 取代 self.pool / self.cr / self.uid / self.context
4. 模型基类：osv.Model / osv.osv → models.Model / models.TransientModel
5. 异常：osv.except_osv / except_orm → UserError
6. 字段声明：_columns / _all_columns → 类属性 fields.Char(...) 与 _fields
7. 报表与前端：QWeb 报表引擎 + Bootstrap / website builder
8. 视图 / QWeb（基本兼容，红线提示）
9. HTTP / 邮件 / 二进制（7→8 不变）
10. 安全与 res.groups（7→8 不变）
11. 模块 / 模型 / 字段映射
12. 测试与校验
13. upgrade_code codemod（7→8 无）
14. 迁移实战清单

---

## 1. 导言与版本作用域

Odoo **8.0（2014-09）** 是 "new API" 正式落地的一次大版本：Odoo 7.0 完全使用旧 API
（`def meth(self, cr, uid, ids, context=None)`、 `self.pool.get(...)`、 `osv.osv` 基类、
`_columns` 字典字段、 `osv.except_osv` 异常），8.0 引入了以 `self.env` / recordsets /
装饰器为核心的新 API，并保留旧 API 的兼容层（渐进迁移）。

**本版本对的头号断裂**：new-API 装饰器（`@api.model`、 `@api.multi`、 `@api.one`、
`@api.depends`、 `@api.constrains`、 `@api.onchange`、 `@api.returns`）正式引入；
`self.env` 取代 `self.pool` / `self.cr` / `self.uid` / `self.context`；
`osv.Model` → `models.Model`； `osv.except_osv` → `UserError`； `_columns` → 类属性字段。

> **关键红线**：7/8 一律使用 `from openerp import ...`（包名 `openerp`）。`openerp`→`odoo`
> 的改名属于 **9→10**，本对**不**涉及，切勿误改 import。

### 版本作用域红线（勿套用更晚版本的改动）

| 更晚版本的改动 | 归属版本 | 在 7→8 中 |
|---|---|---|
| `openerp`→`odoo` 包改名 | 9→10 | ❌ 排除（7/8 仍用 openerp） |
| `@api.one` 完全移除 | 11→12 | ❌ 排除（8.0 仍保留 @api.one） |
| `fields.Date` / `fields.Datetime` 运行时对象化、`from_string` 移除 | 11→12 | ❌ 排除 |
| `ir.actions.act_window.view` 模型移除 | 11→12 | ❌ 排除（8.0 仍有） |
| `account.invoice`→`account.move` | 12→13 | ❌ 排除 |
| `t-field-options`→`t-options` | 11→12 | ❌ 排除 |
| `res.partner.address` 移除、`osv.osv`→`osv.Model` 基类改名 | 6→7 | ❌ 排除（7.0 已完成） |
| Workflow 完全移除 | 11→12 | ❌ 排除（8.0 仍有 workflow） |

> 本卷只处理 7→8 区间；任何属于 9→10、11→12、12→13 的条目，仅在本卷"红线"处点名，不展开。

### 配套技能参考表（skill references）

本烹饪书的事实基准由 `Odoo7to8Migration/references/` 下的六份映射表承载，二者逐条对齐、零漂移：
`references/orm-api.md`（装饰器 / self.env / osv.Model / except_osv / 字段属性）、
`references/views-qweb.md`（QWeb 报表 / Bootstrap / 视图兼容）、
`references/models-mapping.md`（字段类型映射 + 红线排除）、
`references/security.md`（安全不变）、
`references/http-rpc-mail.md`（HTTP/邮件/二进制不变）、
`references/upgrade-code.md`（无 codemod + migrations/8.0 工作流）。

---

## 2. 头号断裂：New API 装饰器引入  — CONFIRMED

Odoo 8.0 正式引入 new-API 装饰器集合（`openerp.api` 模块），7.0 代码完全不存在这些装饰器。

- `@api.model` —— 纯模型方法（不依赖具体记录集）。
- `@api.multi` —— 多记录集方法（默认语义）。
- `@api.one` —— 自动把 `self` 拆成单条并循环；**注意返回值是 LIST**（web 客户端对 button
  动作偏好 `@api.multi` + `self.ensure_one()`，避免 list 返回问题）。
- `@api.depends` —— 计算字段依赖声明（替代旧 `_function` 的 `multi`）。
- `@api.constrains` —— Python 约束（替代旧 `_constraints` 元组）。
- `@api.onchange` —— 表单 onchange（替代旧 `_onchange` 字典）。
- `@api.returns` —— 指定返回模型/记录的装饰器（用于 `create` / `copy`）。

导入方式：`from openerp import models, api, fields`。配套映射见 `references/orm-api.md`。

---

## 3. ORM 环境：self.env 取代旧属性  — CONFIRMED

8.0 用 `self.env` 环境对象统一取代旧的游标/用户/上下文散装属性；方法签名去掉
`(cr, uid, ids, context=None)` 四个位置参数，改为操作 **recordsets**。

### Before（7.0，旧 API）

```python
def action_confirm(self, cr, uid, ids, context=None):
    obj = self.pool.get('sale.order')
    obj.write(cr, uid, ids, {'state': 'confirmed'}, context=context)
    return True
```

### After（8.0，new API）

```python
@api.multi
def action_confirm(self):
    self.write({'state': 'confirmed'})
    return True
```

要点：

- `self.pool.get('x')` → `self.env['x']`。
- `self.cr` → `self.env.cr`；`self.uid` → `self.env.uid`；`self.context` → `self.env.context`。
- recordsets 直接支持 `self.write(...)`、 `self.browse(...)`、 `self.search(...)` 等。
- 旧 `@api.one` 返回 LIST 的客户端注意见第 2 节；button 动作推荐 `@api.multi` + `self.ensure_one()`。

---

## 4. 模型基类：osv.Model → models.Model  — CONFIRMED

8.0 移除了 `openerp.osv.osv` 的短别名；模型基类改为 `openerp.models` 下的 `models.Model`
（普通模型）与 `models.TransientModel`（向导）。

### Before（7.0）

```python
from openerp.osv import osv
class MyModel(osv.osv):
    _name = 'my.model'
class MyWizard(osv.osv_memory):
    _name = 'my.wizard'
```

### After（8.0）

```python
from openerp import models, api, fields
class MyModel(models.Model):
    _name = 'my.model'
class MyWizard(models.TransientModel):
    _name = 'my.wizard'
```

注意：`models.TransientModel` 是向导的新基类；`from openerp.osv import orm` 应改为
`from openerp import models`。更多映射见 `references/orm-api.md`。

---

## 5. 异常：osv.except_osv → UserError  — CONFIRMED

8.0 用 `openerp.exceptions.UserError` 取代旧异常工厂：

### Before（7.0）

```python
raise osv.except_osv(_('Error'), _('Invalid value'))
# 或旧式 except_orm
```

### After（8.0）

```python
from openerp.exceptions import UserError
raise UserError(_('Invalid value'))
```

`except_orm` 也被 `UserError` 取代；`Warning`（= `UserError` 别名）与 `RedirectWarning`
仍可用。扫描 id：`except-osv`（正则 `osv\.except_osv|except_orm`）。

---

## 6. 字段声明：_columns → 类属性字段  — CONFIRMED

8.0 引入 new-style 字段，直接在类体上声明为类属性；旧的 `_columns` / `_all_columns`
字典写法被废弃（运行期字段容器统一为 `_fields`）。

### Before（7.0）

```python
_columns = {
    'name': fields.char('Name', size=64),
    'active': fields.boolean('Active'),
}
```

### After（8.0）

```python
name = fields.Char(string='Name', size=64)
active = fields.Boolean(string='Active')
```

要点：

- 旧 `fields.char(...)` / `fields.text(...)`（来自 `openerp.osv.fields`）改为
  `fields.Char(...)` / `fields.Text(...)` 等 new-API 字段类（`references/models-mapping.md` 有完整类型表）。
- 旧 `fields.function` 计算字段 → `compute=` + `@api.depends`；旧 `fields.related` → `related=`。
- 运行期对象上字段容器名为 `_fields`（替代 `_columns` / `_all_columns`）。
- 扫描 id：`fields-attr`（正则 `_columns\b|_all_columns\b`）。

---

## 7. 报表与前端：QWeb 报表 + Bootstrap  — CONFIRMED（[verify] 细节）

Odoo 8.0 把报表引擎重心从 RML / OpenOffice / Mako 转向 **QWeb**（HTML+QWeb 模板，
`report_type="qweb-pdf"` / `report_type="qweb-html"`）。同时引入 **website builder** 与
基于 **Bootstrap** 的前端框架。

- 7.0 报表多用 RML（`report_type="rml"` / `"mako"`，由 `ir.actions.report.xml` 定义）。
- 8.0 新增 QWeb 报表：`<report id="..." model="..." name="..." file="module.report_tpl"
  report_type="qweb-pdf" string="..."/>`。
- RML / Mako 在 8.0 仍可运行（向后兼容），迁移到 QWeb 属推荐而非强制。
- `[verify]` Bootstrap 具体大版本（3.x）以 8.0 `addons/web/package.json` 实机为准。
- 扫描 id：`qweb-report`（保守正则命中 `report_type="rml"` / `"mako"` 即提示 deprecated）。

---

## 8. 视图 / QWeb（基本兼容）  — CONFIRMED

8.0 的 form / tree / kanban 视图语法与 7.0 高度兼容：`<tree>`、 `<field>`、 `attrs`、
`states`、 `<button type="object"|"action">`、 `<notebook>` 等均保留。本对**没有**
`tree`→`list`（17→18）、 `t-raw` 移除（14→15）、 `t-field-options`→`t-options`（11→12）
等视图破坏。Workflow 按钮（`<button type="workflow">`）在 8.0 仍存在（11.0 才移除）。
`ir.actions.act_window.view` 模型在 8.0 仍然存在（11→12 才移除）。详见 `references/views-qweb.md`。

---

## 9. HTTP / 邮件 / 二进制（7→8 不变）  — CONFIRMED

- 控制器：`from openerp import http`（7.0 已是 `openerp` 包），`http.Controller` / `route()`
  接口 7→8 无破坏性变更（注意包名仍是 `openerp`，不是 `odoo`）。
- 邮件：`message_post(...)` 在 7/8 行为一致；`body_is_html`（16→17）、`subtype`→`subtype_xmlid`（14→15）均不在本对。
- 二进制：`Binary` 默认存 `ir.attachment` 的时机在 13.0，7→8 维持原状。
- `get_resource_path` 在 7/8 仍使用（重命名为 `file_path` 是 16→17）。
- 详见 `references/http-rpc-mail.md`。

---

## 10. 安全与 res.groups（7→8 不变）  — CONFIRMED

- `ir.model.access.csv` 列结构（`perm_read` / `perm_write` / `perm_create` / `perm_unlink`）7/8 一致。
- `ir.rule`、 `res.groups`（`implied_ids` 继承链、 `category_id`）机制一致。
- 安全 XML 无需改动。注意 7→8 的模型基类改写若波及继承安全逻辑的自定义模型，那是 ORM 层改写，不是安全文件改动。
- 详见 `references/security.md`。

---

## 11. 模块 / 模型 / 字段映射

除第 4/6 节的基类与字段声明改写外，7→8 模型层无大规模重命名（`account.invoice`→`account.move`
属于 12→13，不属本卷）。需要关注的：

| 项目 | 7.0 | 8.0 | 备注 |
|---|---|---|---|
| 模型基类 | `osv.osv` / `osv.Model` | `models.Model` | 第 4 节 |
| 向导基类 | `osv.osv_memory` | `models.TransientModel` | 第 4 节 |
| 字段声明 | `_columns` 字典 | 类属性 `fields.Char(...)` | 第 6 节 |
| 字段容器 | `_columns` / `_all_columns` | `_fields` | 第 6 节 |
| 异常 | `osv.except_osv` | `UserError` | 第 5 节 |
| 取模型 | `self.pool.get('x')` | `self.env['x']` | 第 3 节 |
| 报表引擎 | RML / Mako | QWeb（推荐） | 第 7 节 |

---

## 12. 测试与校验

1. 用 **Python 2.7**（7/8 仍是 Python 2 时代；Python 3 强制是 11.0 的事）启动 8.0 实例。
2. `python3 Odoo7to8Migration/scripts/scan_addon.py /path/to/addons` 跑扫描，逐条处理
   `api-decorators` / `self-pool` / `osv-model` / `except-osv` / `fields-attr` / `qweb-report`
   发现项（全部 `manual`，无 codemod）。
3. 安装模块：先清 `ImportError`（`osv` 基类、 `osv.except_osv`、 `from openerp.osv import orm`）；
   再清 `AttributeError`（`self.pool`、 旧 `(cr, uid, ids, context)` 调用点）。
4. `python3 -m py_compile **/*.py` 全量编译，确保无语法错误。
5. `odoo-bin -u <module> --test-tags /<module>` 跑测试；`--dev=all` 下清除 `DeprecationWarning`。

---

## 13. upgrade_code codemod（7→8 无）  — CONFIRMED

`odoo/upgrade_code/` 引擎自 **18.0** 才出现。7→8 **没有任何 `upgrade_code` 脚本**——所有
代码改名、new-API 改写、报表迁移均为**手工**。数据库级变更（极少量列/结构微调）由
**OpenUpgrade** 或官方升级服务处理；本卷只覆盖自定义模块的**代码级**映射。详见
`references/upgrade-code.md`。

---

## 14. 迁移实战清单

- [ ] 模型基类：`osv.osv` / `osv.osv_memory` / `osv.Model` / `osv.TransientModel` → `models.Model` / `models.TransientModel`；`from openerp.osv import orm` → `from openerp import models`。
- [ ] 字段声明：`_columns` / `_all_columns` 字典 → 类属性 `fields.Char(...)` 等；旧 `fields.function` → `compute=` + `@api.depends`，`fields.related` → `related=`。
- [ ] 方法签名：`(cr, uid, ids, context=None)` → 加 `@api.multi` / `@api.model` 并用 recordsets；`self.pool.get('x')` → `self.env['x']`；`self.cr/uid/context` → `self.env.*`。
- [ ] 异常：`osv.except_osv` / `except_orm` → `from openerp.exceptions import UserError; raise UserError(...)`。
- [ ] button 动作：旧 `@api.one` 返回 LIST 问题 → 改用 `@api.multi` + `self.ensure_one()`（如适用）。
- [ ] 报表：`report_type="rml"` / `"mako"` → 评估迁 QWeb（推荐，[verify] 细节）。
- [ ] 切勿误改：`from openerp` → `from odoo`（属 9→10，本对保留 openerp）；勿删 workflow / `ir.actions.act_window.view`（8.0 仍在）。
- [ ] 重扫扫描器期望 0 发现；跑测试通过；DB 微调写入 `migrations/8.0/`（OpenUpgrade）。
