# Odoo 19.0 迁移烹饪书（18.0 → 19.0）

> **适用范围**：Odoo **18.0 → 19.0** 自定义插件（CE 与 EE）升级。
> **体例说明**：本烹饪书（Cookbook）为原创，无对应外部 PDF 底本，内容基于 Odoo 官方 ORM Changelog（odoo.com/19.0，含 PR 号）与多个社区 18→19 升级文（Cybrosys、SDLC Corp、ERP Consulting 24、Octura、LineScripts、DeployMonkey、mindscript）交叉核实，并与同目录 `Odoo18to19Migration/` 的机器可读映射表（Skill）保持事实一致——本书可读性强，Skill 可被 agent 直接调用。
> **可信度标记**：`CONFIRMED` = 多源交叉核实；`[verify]` = 单一社区来源、待 19.0 源码最终确认；`[EE-verify]` = Enterprise 专属、需对照 EE 19.0 树复核。

---

## 第 0 章 · 导言

### 0.1 为什么是 18→19

Odoo 19 是一次"重底座"的版本：框架层（ORM 包拆分）、前端层（Owl 2→3）、安全模型（`res.groups` 的 category→privilege 重构）、数据模型（UoM / 税种 / 合作伙伴字段大幅改名）同时变动。与 19→20（主要是 XML-ID 与 API 收口）相比，**18→19 的破坏性更广**，建议把迁移当作一次"半重写"来排期。

### 0.2 版本作用域纪律（最重要的一条）

> **变更归属于它首次出现的版本。** 不要把 19→20 才引入的破坏性变更误带进 18→19。

已被显式排除在 18→19 之外、属于更早或更晚版本的改动：

| 变更 | 真实归属版本 | 说明 |
|---|---|---|
| `ir.model.access.csv` → `ir.access.csv` / `operation` 列 | **20.0** | 18→19 的访问文件格式**不变** |
| 模型级 `models.Constraint` 之外的 `account.group` 层级重构（codemod `19.3-00`） | **19.3（Online）** | `--to ≥ 19.3` 才触发，纯 18→19 CE 不跑 |
| `group_operator` → `aggregator` | **17.2** | 18 里已是事实，勿重复改动 |
| `check_access` / `has_access` / `_filtered_access` | **18.0** | 已存在，仅建议优先采用 |
| `Domain` API（`from odoo import Domain`） | **18.1** | 已存在，建议优先采用 |
| `<tree>` → `<list>` | **17.5**（codemod `17.5-01`） | 旧 codemod 属 17→18；但 19.0 **硬拒绝** `<tree>`（见第 4.5 章），18→19 仍须迁移——勿误归为 19→20 |
| `mail.thread.cc` 移除、`mail_post` server-action 重构 | **19→20** | 不在此步 |
| `res.users` 多个 19→20 重命名、`account.group→account.account`（codemod `19.3-00`） | **19→20** | 不在此步 |

### 0.3 推荐工作流（详见第 10 章）

1. **扫描（triage）** → 2. **跑 codemod**（`upgrade_code --from 18.0`）→ 3. **应用人工映射** → 4. **校验**（`-u` + 测试 + 清 DeprecationWarning）→ 5. **出报告**。

---

## 第 1 章 · 框架与运行时

### 1.1 ORM 包拆分（内部导入被移除）— CONFIRMED

Odoo 19 将单体 `odoo/api.py` / `odoo/models.py` / `odoo/fields.py` 拆为 `odoo/orm/` **包**。公共导入向后兼容，但**所有"伸手进框架"的内部导入**被移除。

| 写法（18，已失效） | 写法（19） | 来源 |
|---|---|---|
| `from odoo.api import Meta, Params, propagate` | **删除**——改用公共 `from odoo import api, fields, models` | LineScripts；ORM 包拆分 |
| `from odoo import registry` | `from odoo.modules.registry import Registry` | SDLC / Cybrosys |
| `from odoo.conf import ...` / `odoo/conf/` 包 | **删除**——用 `odoo.tools.config` | LineScripts——**已核实**：19.0 中 `odoo/conf` 不存在（ORM 拆入 `odoo/orm/`） |
| `get_module_resource(...)` | **删除**——用 `odoo.modules.get_resource_from_path`（`odoo.modules` 已导出）或 `pathlib` | LineScripts（`pathlib`）/ Cybrosys（`get_resource_from_path`）——**已核实**：`get_resource_from_path` 在 19.0 由 `odoo.modules` 导出 |
| `from odoo.osv import expression` | **弃用**（#217708）——`from odoo import Domain` | Cybrosys |
| `from odoo.tools.misc import xlsxwriter` | `import xlsxwriter` | Cybrosys（简化导入） |

**食谱**：全局 grep 下面任一模式，逐文件改为公共写法：

```bash
grep -rn "from odoo.api import\|from odoo import registry\|get_module_resource(\|from odoo.osv import\|from odoo.conf" /path/to/addons
```

### 1.2 `@api.returns` 被移除 — CONFIRMED

`@api.returns` 在 19 被删除。它在 18 里本就无效果，直接删掉装饰器即可。

```python
# 18
@api.returns('my.model')
def action_do(self): ...

# 19 —— 直接删掉 @api.returns 行
def action_do(self): ...
```

### 1.3 运行时要求

- **Python 3.11+**（推荐 3.12）；**PostgreSQL 13+**（推荐 15/16）。迁移前先确认运行环境。

---

## 第 2 章 · ORM 与模型 API

### 2.1 SQL 约束 → 声明式属性 — CONFIRMED（codemod `18.1-00-sql-constraint`）

`_sql_constraints` 被声明式模型属性取代（旧写法在 19 被弃用，codemod `18.1-00-sql-constraint` 自动重写）：

```python
# 18
class MyModel(models.Model):
    _name = 'my.model'
    _sql_constraints = [('name_unique', 'UNIQUE(name)', 'Name must be unique.')]

# 19
class MyModel(models.Model):
    _name = 'my.model'
    _name_unique = models.Constraint('UNIQUE(name)', 'Name must be unique.')
    _name_idx    = models.Index('idx_my_model_name', 'name')
```

> 来源：Cybrosys、DeployMonkey、LineScripts（"Constraint / Index / UniqueIndex 表对象取代 _sql_constraints"）。

### 2.2 记录级 API 重命名 — CONFIRMED/部分 `[verify]`

| 18 | 19 | 状态 / 来源 |
|---|---|---|
| `self._cr` | `self.env.cr` | 弃用（#193636），发 `DeprecationWarning` |
| `self._uid` | `self.env.uid` | 弃用（#193636） |
| `self._context` | `self.env.context` | 弃用（#193636） |
| `self.read_group(...)` | `self._read_group(aggregates=...)` | 自 18.2 弃用（#163300），参数 `fields`→`aggregates` |
| `self.toggle_active()` | `self.action_archive()` / `self.action_unarchive()` | LineScripts |
| `self.check_field_access_rights(...)` | `self._has_field_access(field, mode)` | **已纠正**：19.0 `orm/models.py` 调用 `_has_field_access(field, mode)`；社区所称 `_check_field_access` 不存在 |
| `self._apply_ir_rules(query)` | `self._search(domain, bypass_access=True)` | Cybrosys / ERP24——`_apply_ir_rules` 已移除 |

```python
# 18
query = self._where_calc(domain)
self._apply_ir_rules(query)
# 19
query = self._search(domain, bypass_access=True)
```

### 2.3 创建 / 搜索的严格化

- `@api.model_create_multi` 是 `create()` 的推荐装饰器（将单条 dict 归一为列表）。源码复核 `odoo/orm/decorators.py` 表明未装饰的 `create` **不会**硬告警——"强制 / DeprecationWarning"之说**未证实**。保留既有 `@api.model_create_multi` 即可。`[verify]`
- `search()` 遇非法 domain 运算符（如无效 operator）抛 `ValueError`（18 静默忽略）。
- `unlink()` 级联校验更严，孤儿关联记录会被检出。

---

## 第 3 章 · 安全与 res.groups

### 3.1 访问文件格式 18→19 **不变** — CONFIRMED

与 19→20 不同，**18→19 的 `security/ir.model.access.csv` 格式没有任何变化**，仍用 `perm_*` 列：

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_lock,my.lock,model_my_lock,base.group_user,1,1,1,0
```

**切勿**套用 19→20 的 `ir.access.csv` / `operation` 转换——那是 20.0 专属。相应的 codemod `ir-access`（版本 `19.4-00`）在纯 18→19 中**不运行**。

### 3.2 `res.groups` 重构为 privilege 模型 — CONFIRMED

Odoo 19 用 *privilege* 取代 group *category*。多个独立来源（Cybrosys、SDLC、ERP24）+ 真实 19.0 模块 `eh_hr_compat`（硬编码了 16–18→19 的字段翻转）相互印证：

| Odoo 18 | Odoo 19 | 说明 |
|---|---|---|
| `res.groups.category_id` | `res.groups.privilege_id`（新模型 `res.groups.privilege`） | `category_id` 在 19 移除 |
| `res.groups.groups_id` | `res.groups.group_ids` | 隐含组关系改名 |
| `res.groups.users` | `res.groups.user_ids` | 成员关系改名（user 侧的反向） |
| `res.users.groups_id` | `res.users.group_ids` | user 侧组关系改名 |

**规则**：

- 自定义 `res.groups` XML 仍须在引用它们的 `ir.model.access.csv` **之前**加载。
- 记录规则（record rule）的 `groups=` 属性在 19 安装时按既有 group XML-ID 严格校验——悬空的 `groups="x.group_y"` 会在安装时抛错。

```xml
<!-- 18 -->
<record id="group_my" model="res.groups">
  <field name="category_id" ref="base.module_category_..."/>
  <field name="users" eval="[(4, ref('base.user_admin'))]"/>
</record>
<!-- 19 -->
<record id="group_my" model="res.groups">
  <field name="privilege_id" ref="base.privilege_..."/>
  <field name="user_ids" eval="[(4, ref('base.user_admin'))]"/>
</record>
```

---

## 第 4 章 · 视图、QWeb 与 Owl 3

### 4.1 Owl 2.x → Owl 3.x（前端，最高工作量）— CONFIRMED

Odoo 19 客户端框架升级到 **Owl 3**——这是 18→19 最大的人工工作量区。自定义 JS 组件关键破坏点：

| Odoo 18（Owl 2） | Odoo 19（Owl 3） | 说明 |
|---|---|---|
| 基于构造函数的初始化 | **`setup()` 模式强制化** | 构造器初始化在 19 抛错 |
| 旧的 `useState` 状态模式 | 新响应式模型（`useState` 语义精炼） | 审查状态用法 |
| 部分生命周期钩子 | 钩子重命名/合并 | 审查 `onWillStart` / `onMounted` |
| 仅 dev 环境的 prop 校验 | **生产环境强制 prop 校验** | 坏 props 现在会在生产崩溃 |
| `useEffect` 旧清理 | `useEffect` 清理精炼 | 确保清理逻辑执行 |

**食谱**：重写所有自定义组件为纯 `setup()`；审计 `static/src/**/*.js` 下每个自定义 widget。QWeb 模板语法对 Owl 3 仅有**轻微**兼容改动，多数模板可沿用，但需重测。

### 4.2 QWeb 模板改动 — CONFIRMED

| Odoo 18 | Odoo 19 | 来源 |
|---|---|---|
| `t-esc` | `t-out` | Cybrosys（"用 t-out 替换 t-esc"） |
| 被 `t-call` / `t-snippet-call` 消费的 `t-set` 块 | `t-set` 必须**提升到 call 之前** | LineScripts（对应 codemod `19.1-00-t-call`，属 19.x Online，非纯 18→19 CE） |
| 网站片段的 Font Awesome `fa-` 图标名 | Material Symbols / `oi` + `data-icon` | 方向与 19→20 一致 |

> `t-esc`→`t-out` 被多个 18→19 指南标记；即便仍能渲染，也视为 19 兼容的必做清理。

### 4.3 Kanban 卡片模板名：`kanban-box` → `card` — CONFIRMED

社区 18→19 表（SDLC、ERP24）报告 kanban 卡片模板名 `t-name="kanban-box"` → `t-name="card"`（Owl-3 kanban 重写）。自定义 kanban 卡片相应改名（对照 19.0 `web` 的 kanban 模板确认）。

### 4.4 视图架构与校验（向后兼容，校验更严）

XML 视图语法**向后兼容**——18→19 无新增强制标签或属性改名（LineScripts："XML view syntax fully backward-compatible"）。但以下更严校验由社区报告（在 19.0 安装上确认，`[verify]`）：

- 视图 `<record>` 应声明 `model`（省略可能在安装时抛错）——**19.0 `ir_ui_view.py` 显示 `model` 非 `required`，此说未证实**。`[verify]`
- XPath 表达式校验更严（畸形 xpath 抛错）。`[verify]`
- 视图字段上的 `groups=` 按既有 group XML-ID 在安装时校验。`[verify]`
- 无 `name` 属性的 `oe_button_box` 不再支持——**19.0 `ir_ui_view.py` 中未见此校验**，疑似非真实 18→19 改动。`[verify]`

### 4.5 `<tree>` → `<list>` — **CONFIRMED（19.0 移除）**

19.0 的视图 `type` 选单仅含 `list`（无 `tree`）；以 `<tree>` 为根标签会抛 `Invalid view type: 'tree' ... Allowed types are: ...`。须将 `<tree>` → `<list>` 迁移。这是**真实的 18→19 破坏性变更**（旧 `tree→list` codemod 属更早版本，但 19.0 的硬拒绝才是迁移时真正踩到的点）。

### 4.6 窗口动作：`target='inline'` 移除 — **CONFIRMED**

`ir.actions.act_window.target` 在 19.0 仅接受 `current`、`new`、`fullscreen`、`main`（无 `inline`）。已通过 `odoo/addons/base/models/ir_actions.py` 源码核实。扫描 XML/Python 动作定义中的 `target='inline'` 并重指向合法值之一。

### 4.7 模块依赖：`web_editor` → `html_editor` / `html_builder` — CONFIRMED

`web_editor` 在 19 **消失**——拆分为 `html_editor` 与 `html_builder`（LineScripts、DeployMonkey、SDLC、ERP24）。任何 manifest `'depends': ['web_editor']` 都会安装失败。重指向：

| Odoo 18 depends | Odoo 19 depends |
|---|---|
| `web_editor` | `html_editor`（富文本）和/或 `html_builder`（站点构建器） |

> 站点构建器拆分是 `html_builder`；富文本字段用 `html_editor`。完整模块改名见第 6 章。

---

## 第 5 章 · HTTP、邮件与二进制

### 5.1 控制器：`type='json'` → `type='jsonrpc'` — CONFIRMED

18.1（#183636）引入：JSON 控制器 `type` 由 `json` 改名为 `jsonrpc`。在 19 中**旧别名仍可用但 import 时记录 `DeprecationWarning`**，计划在后续版本移除。codemod `18.1-02-route-jsonrpc` 执行重写。

```python
# 18
@app.route('/my/endpoint', type='json', auth='user')
def my_endpoint(self): ...

# 19
@app.route('/my/endpoint', type='jsonrpc', auth='user')
def my_endpoint(self): ...
```

- **线协议完全相同**，因此**无需改动任何 JavaScript**——只改 Python 的 `type=` 值（mindscript 升级审计器："线协议相同，无需改 JS"）。
- 仅 `@http.route(type='json')` 受影响；`type='http'` 不受影响。外部 `JSON-2`（`/json/2/...`）与 XML-RPC 端点无 18→19 变化。

### 5.2 认证 API：`authenticate()` — CONFIRMED

| Odoo 18 | Odoo 19 |
|---|---|
| `authenticate(request.session.db, creds)` | `authenticate(request.env, creds)` |

（Cybrosys / ERP24。）影响自定义 auth/controller 代码；普通 RPC 客户端不受影响。

### 5.3 外部 RPC 弃用（仅提醒，非断裂）

依 Odoo 外部 RPC API 参考：自 **19.0** 起，XML-RPC 与 JSON-RPC 端点（`/xmlrpc`、`/xmlrpc/2`、`/jsonrpc`）被**弃用**（db 服务在 20.0 移除；common/object 计划于 22.0）。对 18→19 仅是*警告*——集成仍可用。外部集成复核建议在 19→20 步骤处理。

### 5.4 二进制 / Excel / PDF / 时间

18→19 无报告破坏性变更：`fields.Binary`、PyTZ/`zoneinfo` 用法、Excel/PDF 报表渲染、服务端时间辅助均稳定跨版本。（`pytz`→`zoneinfo` 指引属 19→20。）若模块通过 `web_editor` 渲染报表，见 4.7 的 `web_editor`→`html_editor`/`html_builder` 改名（它改变报表模板的编辑器依赖）。

### 5.5 邮件与 server action

邮件线程与 `mail.thread` API 在 18→19 稳定；`mail.thread.cc` 移除是 **19→20** 改动，不在此步。Server action 与自动化动作保持签名。（`mail_post` server-action `state` 重构属 19→20。）

---

## 第 6 章 · 模块 / 模型 / 字段映射

> 已确认行（≥2 独立来源：Cybrosys、SDLC、ERP24、Octura、LineScripts + 真实 19.0 模块 `eh_hr_compat`）标 **CONFIRMED**；其余标 `[verify]` / `[EE-verify]`。

### 6.1 模块改名（manifest `depends` 重指向）— CONFIRMED

| Odoo 18 module | Odoo 19 module | 版本 | 来源 |
|---|---|---|---|
| `web_editor` | `html_editor` + `html_builder` | CE | LineScripts + SDLC + Cybrosys + ERP24 |
| `account_auto_transfer` | `account_transfer` | EE | LineScripts `[EE-verify]` |
| `account_disallowed_expenses` | `account_fiscal_categories` | EE | LineScripts `[EE-verify]` |
| `hr_work_entry_contract_*` | 去掉 `contract` 中缀（如 `hr_work_entry_*`） | EE | LineScripts `[EE-verify]` |

> 其他 EE 模块改名有可能；需对照 Enterprise 19.0 树复核。

### 6.2 模型改名与新增 — CONFIRMED

| Odoo 18 model | Odoo 19 model | 类型 | 来源 |
|---|---|---|---|
| `stock.quant.package` | `stock.package` | 改名 | 源码核实（18.0 quant_package.py / 19.0 stock_package.py） |
| `hr.expense.sheet` | `hr.expense` | 合并 | 源码核实（18.0 有 sheet、19.0 无） |
| `hr.contract` | `hr.version` | 改名 | 源码核实（18.0 hr_contract / 19.0 hr_version） |
| — | `stock.reference` | **新增** | 源码核实（19.0 `addons/stock/models/stock_reference.py`） |
| — | `project.role`、`project.template.create.wizard` | **新增** | 源码核实（18→19 模型集 diff） |

> **纠错：`procurement.group` 不是改名为 `stock.reference`。**
> 部分二手资料（SDLC 等）把 `procurement.group`→`stock.reference` 列为改名，源码核实**不成立**：
> `procurement.group` 是采购分组（把同一销售单的 moves 聚合成 picking），19.0 **直接移除**；
> 而 `stock.reference` 是 19.0 **新增**的"库存单据引用链"模型（`_description = 'Reference between stock documents'`，
> 字段为 `name` + `move_ids` m2m + `picking_ids` compute），用途是替代服务端 `origin` 字符串、
> 串起补货链上的单据引用关系。两者语义不同，不能当作改名互换。

### 6.3 已移除模型 — CONFIRMED

| Model | 说明 |
|---|---|
| `res.partner.title` | 19 移除（Cybrosys、ERP24）——更新引用它的模块 |
| `uom.category` | 19 移除（Octura、SDLC、Cybrosys）——见 6.4 UoM 字段改名 |
| `procurement.group` | 19 移除（源码：18.0 `stock_rule.py` 有、19.0 无）——**连同引用字段一并移除**，见 6.3.1 |
| `product.packaging` | 19 移除（18.0 有、19.0 无，EE 亦无）——包装改由 UoM/包装层级新机制承载 |
| `account.fiscal.position.tax` | 19 移除（18.0 有、19.0 无）——税位直接映射税标签 |

#### 6.3.1 采购组的移除连带面（库存头号断裂）

`procurement.group` 移除不只是少一个模型，`group_id` 这条链全断：

| 18.0 | 19.0 | 说明 |
|---|---|---|
| `procurement.group` 模型 | 移除 | 无同名替代 |
| `stock.move.group_id`（m2o → procurement.group） | 移除 | 移动行不再挂采购组 |
| `stock.picking.group_id` | 移除 | 调拨单不再挂采购组 |
| `sale.order.procurement_group_id` | 移除 | 销售单不再显式持有采购组 |
| — | `stock.reference`（新增） | 仅承接"单据引用链"，**不含**采购分组语义 |

**影响面**：所有按采购组聚合的报表、拣货批次逻辑、`group_id` 相关的 domain 与 group by 全部失效。这是 18→19 库存侧最容易踩的一条——因为它看起来"只是删了个模型"，实际删掉了整条分组链。

**迁移动作**：

1. 报表层：按 `group_id` 聚合的改按 `origin` 或 `sale_id`（经 `move.sale_line_id.order_id`）；
2. 代码层：`move.group_id` / `picking.group_id` 全部删除引用，需要"同源单据"语义时改用 `stock.reference`；
3. 数据层：历史采购组数据无载体，如需保留统计口径，升级前导出 `procurement_group` 与 `stock_move.group_id` 映射；
4. `stock.reference` 的用法：`picking.reference_ids`（related to `move_ids.reference_ids`），可用来串补货链。

### 6.4 字段改名 / 移除 — CONFIRMED（除非注明）

| Model | 18 field | 19 field | 来源 |
|---|---|---|---|
| `res.groups` | `category_id` | `privilege_id`（`res.groups.privilege`） | Cybrosys/SDLC/eh_hr_compat |
| `res.groups` | `groups_id` | `group_ids` | Cybrosys/eh_hr_compat |
| `res.groups` | `users` | `user_ids` | eh_hr_compat |
| `res.users` | `groups_id` | `group_ids` | eh_hr_compat（16–18→19 翻转） |
| `account.move.line` | `tax_id` | `tax_ids`（m2m） | Cybrosys/SDLC/ERP24 |
| `account.move.line` | `product_uom` | `product_uom_id` | Cybrosys/SDLC/ERP24 |
| `uom.uom` | `factor_inv` | `relative_factor` | SDLC/Octura/Cybrosys |
| `uom.uom` | `category_id` | `relative_uom_id` | SDLC/Octura/Cybrosys |
| `uom.uom` | `uom_type` | removed | Octura |
| `res.city` | `zip` | `zipcode` | mindscript |
| `res.partner` | `mobile` | removed（并入 `phone`） | Cybrosys + mindscript |
| `res.partner` | `picking_warn` | removed | Cybrosys |
| `res.partner` | `last_website_so_id` | removed | Cybrosys |
| `res.partner` | `sale_line_warn` | removed | Cybrosys |
| `website` / shop | `website.pricelist_id` | `request.pricelist` | Cybrosys |
| `fleet.vehicle.log.services` | `date` | `date_from` / `date_to` | Cybrosys |
| `hr.contract` | — | `hr.version`（合同数据走员工版本） | 源码核实（18.0 hr_contract / 19.0 hr_version） |
| `hr.candidate` | — | `hr.applicant` | SDLC `[verify]` **作用域风险**：`hr.candidate`→`hr.applicant` 早于 18.0，疑非 18→19 专属改动——采用前请确认 |
| `stock.picking` | `move_ids_without_package` | removed | 源码核实（18.0 有、19.0 无） |
| `stock.picking` | `move_line_ids_without_package` | removed | 源码核实（18.0 有、19.0 无） |
| `stock.picking` | `has_packages` / `package_level_ids` / `move_line_exist` / `date` | removed | 源码核实（18→19 字段 diff） |
| `product.template` | `packaging_ids` | removed | 随 `product.packaging` 一并移除 |

> **作用域守卫**：`res.partner.bank.acc_number→account_number`、`res.users` 多个 19→20 改名、`account.group→account.account`（codemod `19.3-00`）都是 **19→20** 改动——归属 19→20 技能，**不**在此步。`account.group` 层级仅在 `--to ≥ 19.3`（Online）触发，非纯 18→19 CE 运行。

### 6.5 症状 → 修复索引

| 19 安装/运行时症状 | 可能原因 | 修复锚点 |
|---|---|---|
| 模块安装失败：`depends` 无法解析 | `web_editor`（或改名的 EE 模块） | §6.1 |
| 加载时 `ImportError`：`from odoo.api import ...` | 内部导入已移除 | 第 1.1 章 |
| 加载时 `ImportError`：`get_module_resource` | helper 已移除 | 第 1.1 章 |
| `DeprecationWarning`：`self._cr/_uid/_context` | 改用 `self.env.*` | 第 2.2 章 |
| `DeprecationWarning`：`read_group(` | 改用 `_read_group(aggregates=...)` | 第 2.2 章 |
| JS widget 报错 / 白屏 | Owl 2 → Owl 3 | 第 4.1 章 |
| `@api.returns` 语法/traceback | 装饰器已移除 | 第 1.2 章 |
| 路由 import 时记弃用 | `type='json'` → `type='jsonrpc'` | 第 5.1 章 |
| 组 XML 引用失败（`groups_id`/`users`/`category_id`） | `res.groups` 改名 | §6.4 |
| `KeyError`：`res.partner.title` / `uom.category` | 模型已移除 | §6.3 |
| `AttributeError`：`mobile` / `sale_line_warn` / `picking_warn` | 字段已移除 | §6.4 |
| 动作 `target='inline'` 被拒 | target 已移除 | 第 4.6 章 |
| Kanban 卡片不渲染 | `kanban-box` → `card` | 第 4.3 章 |
| `Model 'procurement.group' is not available` / `group_id` 不存在 | 采购组模型及 `group_id` 链整体移除 | §6.3.1 |
| `Model 'product.packaging' is not available` | 包装模型移除 | §6.3 |
| 费用单相关模型报错 | `hr.expense.sheet` 已并入 `hr.expense` | §6.2 |
| 按"无包裹行"筛选失效 | `move_ids_without_package` 移除 | §6.4 |
| 税位-税映射报错 | `account.fiscal.position.tax` 移除 | §6.3 |

---

## 第 7 章 · 缓存 / SQL、字段与域

### 7.1 缓存与 SQL

- `SQL(...)` 包装对象（自 17.0，#134677）在 18→19 **不变**。务必用 `SQL()` 组合 SQL，绝不拼接 f-string，避免注入。
- `_flush_search()` 自 17.1（#144747）弃用——18 已是如此；刷新由 `execute_query()` 完成。确认任何对 `_flush_search` 的重写已移除。
- 把裸 `SQL` 对象当 domain leaf：18 容忍，19 更严。优先用 `Domain.custom(to_sql=lambda table: SQL(...))`（该 helper 在 **19→20** 落地——在 18→19 中显式构建 domain）。`[verify]`

### 7.2 字段与域

- `precompute` 在 computed 字段上默认 **False**（非 True）——`odoo/orm/fields.py` 声明 `precompute: bool = False`。仅当显式 `precompute=True` 才预计算。**已纠正**："默认 True"之说不实。审查假设惰性计算的 compute 方法。（19.0 源码核实。）
- `compute_sudo` 默认跟随字段 `store`：`False`（非存储 computed 字段）、`True`（stored computed / related 字段，`attrs['compute_sudo'] = attrs.get('compute_sudo', store)`）。**已纠正**：并非无条件 `True`。（19.0 源码核实。）
- `store=True` 的 related 字段：缓存失效改进可能暴露隐藏 bug。
- `currency_field` 参数现校验被引用字段是否存在。
- `Domain` API（`from odoo import Domain`）自 18.1（#170009）可用：优先用 `Domain.AND/OR`、`Domain.TRUE/FALSE` 替代 `expression.*`。
- `fields.Property` **不是** 19.0 的字段类——`odoo/orm/fields_properties.py` 中 `Property` 是 `abc.Mapping` 的值包装器，真正字段是 `fields.Properties`（**未弃用**）。codemod `18.5-00-deprecated-properties` 针对的是旧式 `company_dependent`/`property` 用法，而非 `fields.Property` 类。**已纠正**："fields.Property 弃用"之说不准确。`[verify]`（精确作用域以 19.0 树为准）
- 等式归一化（18.3，#191549）：`=` 等价于 `in`。

---

## 第 8 章 · 认证 / 测试与校验

### 8.1 认证 API（重述，见第 5.2 章）

`authenticate(request.session.db, creds)` → `authenticate(request.env, creds)`（Cybrosys / ERP24），影响自定义 auth/controller 代码。

### 8.2 测试与校验

- **安装时视图校验更严**：畸形 XPath / 缺失 `model` / 错误 `groups` XML-ID 会在安装时抛错（见第 4.4 章）。加一道视图 RNG 检查。
- 以可见弃用警告启动服务（`--dev=all`），清掉**每一个** `DeprecationWarning`——它们是 20.0 的硬断裂。
- 在 19.0 沙箱跑 `odoo-bin -u <module> --test-tags /<module>`；domain `TypeError` 与视图 RNG 错误放最后修（最"吵"）。
- 18→19 对外部 JSON-2 / XML-RPC 测试契约**无改动**。

---

## 第 9 章 · upgrade_code codemod

### 9.1 运行 codemod

`odoo-bin upgrade_code` 是 Odoo 自带源码重写工具（19.0 内置）。18→19 须从 **19.0 安装**对 18 源码运行：

```bash
# 先 dry-run，在干净 git 分支上
odoo-bin upgrade_code --from 18.0 \
  --addons-path /path/to/addons --dry-run

# 再真实运行
odoo-bin upgrade_code --from 18.0 \
  --addons-path /path/to/addons

# 限定单个模块
odoo-bin upgrade_code --from 18.0 --addons-path /path/to/addons -m my_module
```

- Codemod 只重写 **Python/XML 源码**，不做数据迁移；数据升级留在模块 `migrations/19.0/` 脚本。
- 逐文件审查 `git diff` 并在专用分支提交。

### 9.2 哪些脚本对 18→19 真正运行

`upgrade_code` 选取版本 `∈ [--from, --to]` 的脚本。对**纯 18.0 → 19.0 CE**（`--from 18.0 --to 19.0`），仅版本 `≤ 19.0` 的脚本生效。19.0 `odoo/upgrade_code/` 清单中，18→19 相关脚本：

| Script | 重写内容 |
|---|---|
| `18.1-00-sql-constraint` | `_sql_constraints = [...]` → `models.Constraint(...)`（第 2.1 章） |
| `18.1-02-route-jsonrpc` | 路由 `type='json'` → `type='jsonrpc'`（第 5.1 章） |
| `18.2 / 18.3 l10n` | 图表模板记录；财税科目税映射（`tax_src_id`/`tax_dest_id` → alternative-tax 列） |
| `18.5-00-domain-dynamic-dates` | 域中内联一元负号常量 |
| `18.5-00-no-tax-tag-invert` | 税 `formula` 符号修正 |
| `18.5-00-deprecated-properties` | 旧式 `company_dependent`/`property` 用法（第 7.2 章，scope 已纠正：`fields.Property` 非字段类） |

> **作用域守卫**：脚本 `19.1-00-t-call`（Owl 3 `t-set` 提升）、`19.3-00-account-groups`、`19.3-00-account-report-foldable`、`19.3-00-base64-in-xml`、`19.4-00-ir-access` 等版本 **> 19.0**，纯 18→19 CE **不运行**。它们仅在 `--to ≥ 19.x`（Online）或继续升级到 20.0 时生效——在对应技能中处理。

### 9.3 Codemod 修不了、需手工的项

- `web_editor` → `html_editor`/`html_builder` manifest 重指向（§6.1）。
- Owl 2 → Owl 3 JS 重写 + `t-esc`→`t-out` / `t-set` 提升（第 4.1–4.2 章）。
- `@api.returns` 移除、`odoo/orm` 包内部导入移除（第 1.1–1.2 章）。
- `res.groups` / `res.users` 字段改名与模型/字段改名（§6.3–6.4）。
- `_apply_ir_rules` → `_search`、`authenticate()` 签名（第 2.2 章、第 5.2 章）。
- 弃用清理（`self._cr`→`self.env.cr` 等）——部分可能脚本化，需核实。

### 9.4 Scanner 契约

随附的 `Odoo18to19Migration/scripts/scan_addon.py`（从 19→20 技能逐字复制，版本无关）标记发现项并打印 19.0 替换 + 是否有 codemod 覆盖：

```bash
python3 Odoo18to19Migration/scripts/scan_addon.py /path/to/addons --addon my_module --json
# 退出码 1 = 有发现项
```

### 9.5 写自己的脚本

要新增自定义 18→19 重写，放到 19.0 `odoo/upgrade_code/` 布局下（或本地 `migrations/19.0/` 的 pre/init 数据脚本）再跑。每个脚本单一职责、幂等；提交结果 `git diff` 时附上相关 `references/*.md` 的锚点。

---

## 第 10 章 · 迁移实战清单

### 10.1 Grep 速查（pattern → 动作 → 见章节）

```
from odoo.api import Meta        → 删除（第 1.1 章）
from odoo import registry        → odoo.modules.registry（第 1.1 章）
get_module_resource(             → pathlib / get_resource_from_path（第 1.1 章）
@api.returns                     → 删除（第 1.2 章）
self._cr / self._uid / self._context → self.env.*（第 2.2 章）
read_group(                      → _read_group(aggregates=)（第 2.2 章）
toggle_active                   → archive actions（第 2.2 章）
_apply_ir_rules(                 → _search(bypass_access=True)（第 2.2 章）
from odoo.osv import            → odoo import Domain（第 1.1 章）
check_field_access_rights(       → _has_field_access（第 2.2 章）
_sql_constraints =              → models.Constraint（第 2.1 章）
type='json' 路由                 → jsonrpc（第 5.1 章）
authenticate(request.session.db  → authenticate(request.env（第 5.2 章）
res.groups.category_id/users/groups_id → privilege_id/user_ids/group_ids（§6.4）
res.partner.mobile/sale_line_warn/picking_warn → 已移除（§6.4）
uom.category / res.partner.title → 已移除（§6.3）
kanban-box                      → card（第 4.3 章）
t-esc                           → t-out（第 4.2 章）
depends: ['web_editor']          → html_editor / html_builder（§6.1）
```

### 10.2 端到端工作流

1. **Triage（扫描）**：`python3 Odoo18to19Migration/scripts/scan_addon.py /path/to/addons`——按文件分组列出发现项、行号、19.0 替换、是否被 codemod 覆盖。
2. **Codemod 优先**：干净 git 分支上，从 19.0 安装跑 `odoo-bin upgrade_code --from 18.0 --dry-run` 再真实跑；逐文件审查 `git diff` 并提交。注意 18→19 的 codemod 比 19→20 **少**（安全文件格式不变），多数修复是手工。
3. **人工映射**：对 scanner 标 `manual` 的项，套用对应章节替换（安全/ORM → 第 1–3 章；HTTP/邮件 → 第 5 章；视图/Owl → 第 4 章；模块/字段 → 第 6 章；缓存/字段/域 → 第 7 章）。
4. **校验**：重跑 scanner（期望 0 发现）；`odoo-bin -u <module> --test-tags /<module>`；用 `--dev=all` 启动清掉每个 `DeprecationWarning`（它们是 20.0 硬断裂）；最后修 domain `TypeError` 与视图 RNG 错误。
5. **报告**：逐模块汇总——codemod 改动、人工编辑（附所用章节锚点）、剩余 `[EE-verify]`/`[verify]` 项、测试状态。

---

*本烹饪书（单卷）覆盖 18.0 → 19.0 的框架、ORM、安全、视图/Owl、HTTP/邮件、模块/字段映射、缓存/SQL、测试与 codemod 全流程。机器可读的映射表与扫描器见同目录 `Odoo18to19Migration/`。*
