# Odoo 18.0 迁移烹饪书（17.0 → 18.0）

> **适用范围**：Odoo **17.0 → 18.0** 自定义插件（CE 与 EE）升级。
> **体例说明**：本烹饪书（Cookbook）为原创，无对应外部 PDF 底本，内容基于 Odoo 官方 ORM Changelog（odoo.com/18.0 与 saas-18.2 文档，含 PR 号）、GitHub `odoo/odoo` 18.0 分支源码核实（`odoo/addons/base/models/ir_ui_view.py`、`odoo/models.py`、`odoo/release.py`、`odoo/upgrade_code/` 目录），以及 OCA `maintainer-tools` 的《Migration to version 18.0》、Cybrosys《Odoo 18 v/s Odoo 17》等社区文交叉核实。本书与同目录 `Odoo17to18Migration/` 的机器可读映射表（Skill）保持事实一致——本书可读性强，Skill 可被 agent 直接调用。
> **可信度标记**：`CONFIRMED` = 源码/官方 changelog 多源交叉核实；`[verify]` = 单一社区来源、待 18.0 源码最终确认；`[EE-verify]` = Enterprise 专属、需对照 EE 18.0 树复核。

---

## 第 0 章 · 导言

### 0.1 为什么是 17→18

与 18→19（"重底座"，ORM 包拆分 + Owl 3 + 安全模型重构 + 大量数据模型改名）和 19→20（XML-ID/API 收口）相比，**17→18 是被"移除"主导的一次升级**：Odoo 18 正式删除了 17 仅弃用的旧 API（`name_get`、`check_access_rights`、`user_has_groups`、`check_recursion`、`inselect` 运算符、`<tree>` 视图类型），并引入一批合并/替代 API（`check_access` / `has_access` / `_filtered_access`、`_search_display_name`、`aggregator`、`Domain`）。视图层的 `tree`→`list` 改名是工作量最大、最易遗漏的硬断裂；Python API 的移除次之。数据库转换本身通常顺利，真正的成本在自定义代码。

### 0.2 版本作用域纪律（最重要的一条）

> **变更归属于它首次出现的版本。** 不要把 18→19 才引入的破坏性变更误带进 17→18。

已被显式排除在 17→18 之外、属于**更晚版本（18→19 / 19→20）**的改动——它们将在对应技能中处理：

| 变更 | 真实归属版本 | 说明 |
|---|---|---|
| ORM 包拆分 `odoo/orm/`、`from odoo.api import Meta` 等内部导入移除 | **19.0** | 17→18 的 `from odoo import models, fields, api` 写法不变 |
| `@api.returns` 移除、`odoo/conf` 包移除、`get_module_resource` 移除 | **19.0** | 17→18 这些仍可正常用 |
| Owl 2 → Owl 3（`setup()` 强制化） | **19.0** | 18 仍是 Owl 2，前端组件无需重写 |
| `web_editor` → `html_editor` / `html_builder` | **19.0** | 18 里 `web_editor` 仍在 |
| `res.groups` 的 `category_id`→`privilege_id` 重构、安全文件 `ir.model.access.csv`→`ir.access.csv` | **19.0 / 20.0** | 17→18 的 `res.groups` 与安全文件格式**不变** |
| `t-esc`→`t-out`、`kanban-box`→`card`（Owl 3 重写） | **19.0** `[verify]` | 社区对版本归属有分歧，见第 4 章 |
| `read_group`→`_read_group` 作为硬断裂、`type='json'`→`jsonrpc` | **18.1 / 18.2（Online）** | 见 0.3：18.1 项仍纳入本书，但标注版本 |

**范围约定**：本书把"目标大版本 18"理解为 **18.0 及其 Online 小版本（18.1、18.2）**。因此 18.1 引入的改动（`type='json'`→`jsonrpc`、`Domain` API、`models.Constraint` 声明式约束）也纳入 17→18，并标注其精确小版本——它们对从 17 出发的迁移是新增的。每项变更都标出其首次出现版本，便于核对作用域。

### 0.3 推荐工作流（详见第 10 章）

1. **扫描（triage）** → 2. **跑 codemod**（`upgrade_code --from 17.0`，仅 `17.5-01-tree-to-list`）→ 3. **应用人工映射** → 4. **校验**（`-u` + 测试 + 清 DeprecationWarning）→ 5. **出报告**。

> 17→18 的自动化程度**远低于** 18→19：18.0 树中唯一随版本发布的 codemod 是 `17.5-01-tree-to-list`（视图改名）。其余移除/重命名（name_get、check_access、user_has_groups…）**无 codemod**，必须手工改。

---

## 第 1 章 · 框架与运行时

### 1.1 视图类型 `tree` → `list`（头号硬断裂）— CONFIRMED

Odoo 18 把 `<tree>` 视图类型正式更名为 `<list>`。18.0 的 `ir.ui.view.type` 选单**只含 `list`**（源码核实 `odoo/addons/base/models/ir_ui_view.py` 的 `selection=[('list','List'),('form','Form'),…]`，无 `'tree'`）。以 `<tree>` 为根标签会抛 `ValueError: Wrong value for ir.ui.view.type: 'tree'`。

`upgrade_code` 在 18.0 树中**唯一**内置的脚本就是 `odoo/upgrade_code/17.5-01-tree-to-list.py`（PR #159909）。它会在 **Python / JS / XML** 三处统一改名，但 **不**改含 `tree` 字样的 XML-ID（避免牵连依赖模块）。

**三个易漏位置**（社区经验，任一遗漏都会报同样的 ValueError）：

1. **视图定义**：`<tree>` → `<list>`，含 `editable` / `create` / `default_order` 等属性一并移到 `<list>` 上。
2. **窗口动作的 `view_mode`**：`tree,form` → `list,form`。
3. **继承视图的 XPath**：`//tree/...` → `//list/...`。

```xml
<!-- 17 -->
<record id="view_my_model_tree" model="ir.ui.view">
  <field name="arch" type="xml">
    <tree editable="bottom" colors="red:state=='draft'">
      <field name="name"/>
      <field name="state"/>
    </tree>
  </field>
</record>
<record id="action_my" model="ir.actions.act_window">
  <field name="view_mode">tree,form</field>
</record>

<!-- 18 -->
<record id="view_my_model_tree" model="ir.ui.view">
  <field name="arch" type="xml">
    <list editable="bottom" decoration-danger="state=='draft'">
      <field name="name"/>
      <field name="state"/>
    </list>
  </field>
</record>
<record id="action_my" model="ir.actions.act_window">
  <field name="view_mode">list,form</field>
</record>
```

> **`colors` 属性移除**：旧 `<tree colors="red:cond">` 在 18 不再支持，改用 `decoration-*`（`decoration-danger` / `decoration-success` / `decoration-info` / `decoration-warning` / `decoration-muted` / `decoration-primary` / `decoration-bf` / `decoration-it`）。源码核实 18.0 `ir_ui_view.py` 只处理 `decoration-*`，已无 `colors` 处理分支 —— CONFIRMED（社区共识 + 源码缺失 colors 处理）。
>
> **`tree_view_ref` → `list_view_ref`**：选择特定列表视图的 context key 一并改名（OCA 迁移指南，PR #159909）。
>
> **`string` 属性**：`<tree string="...">` 的标题语义在 18 由动作/字段 `string` 承担；直接在 `<list>` 上的 `string` 应去掉或迁移。

**食谱**：先跑 codemod（见第 9 章），再对 `git diff` 逐文件检查——社区反馈 codemod 偶尔会把 `editable` / `create` / `default_order` 等属性移到标签外导致畸形 XML，必须人眼复核。

### 1.2 运行时要求

- **Python 3.10+**（17 与 18 同为 3.10 地板，无 Python 版本跳跃——与 19→20 的 3.12 不同）。
- **PostgreSQL 14+**（Odoo 18 弃用了 PostgreSQL 12/13 支持，`[verify]`：具体下限以 `odoo/sql_db.py` 的版本校验为准）。迁移前先确认数据库版本。
- **Longpolling → WebSocket**：实时更新（bus/im_livechat）改用 WebSocket 通道，属基础设施变更，自定义代码通常无需改动，但部署架构需跟上。

### 1.3 `upgrade_code` 在 17→18 只做一件事

17→18 没有 18→19 那样的"安全文件格式变更""ORM 包拆分"。18.0 树中 `odoo/upgrade_code/` 仅 `17.5-00-example.py`（模板，非真实 codemod）与 `17.5-01-tree-to-list.py`（真实）。其余破坏面全靠人工映射，见第 2–6 章。

---

## 第 2 章 · ORM 与模型 API

### 2.1 `name_get()` 被移除 — CONFIRMED（弃用于 16.4 #122085，移除于 18.0）

`name_get` 自 16.4 弃用，18.0 正式删除。任何重写 `name_get` 控制记录显示名的模型都需改写——改用计算字段 `display_name` 或 `_compute_display_name`。

```python
# 17
def name_get(self):
    return [(rec.id, f"{rec.code} - {rec.name}") for rec in self]

# 18
display_name = fields.Char(compute='_compute_display_name', store=True)
@api.depends('code', 'name')
def _compute_display_name(self):
    for rec in self:
        rec.display_name = f"{rec.code} - {rec.name}"
```

### 2.2 `_name_search` → `_search_display_name` — CONFIRMED（18.0 #174967）

按名称搜索在 18 统一为 `_search_display_name`，与其他字段的搜索实现一致。重写名称搜索的模型须迁移。

```python
# 17
@api.model
def _name_search(self, name, args=None, operator='ilike', limit=100):
    ...

# 18
@api.model
def _search_display_name(self, operator, value):
    # 返回匹配 display_name 的 domain
    return [('code', operator, value)]
```

### 2.3 访问权限 API 合并 — CONFIRMED（18.0 #179148）

| Odoo 17 | Odoo 18 | 说明 |
|---|---|---|
| `self.check_access_rights('read')` | `self.check_access('read')` | 权限+规则合并为 `check_access(operation)` |
| `self.check_access_rule('write')` | `self.check_access('write')` | 同上 |
| `self._filter_access_rules('read')` | `self._filtered_access('read')` | 返回有访问权的记录子集 |
| `self._filter_access_rules_python('read')` | `self._filtered_access('read')` | 同上 |
| — | `self.has_access('read')` → `bool` | 新增：返回布尔，便于嵌业务逻辑 |
| `self.env.user.has_group('x')` 之外的 `self.user_has_groups('x')` | **删除** → `self.env.user.has_group('x')` | #151597，方法 `user_has_groups` 在 18 移除 |

```python
# 17
if record.check_access_rights('read') and record.check_access_rule('read'): ...
if self.user_has_groups('base.group_system'): ...

# 18
if record.check_access('read'): ...
if self.env.user.has_group('base.group_system'): ...
```

> 源码核实 18.0 `odoo/models.py`：`check_access_rights` / `check_access_rule` / `user_has_groups` 的 `def` 均已不存在；`check_access`、`_filtered_access`、`has_group` 被调用。

### 2.4 `check_recursion()` → `has_cycle()` — CONFIRMED（OCA 18.0 迁移指南）

判断记录集是否成环的旧方法移除，改用 `has_cycle()`。

```python
# 17
if self.check_recursion(parent='parent_id'): ...
# 18
if self.has_cycle(parent='parent_id'): ...
```

### 2.5 `copy` / `copy_data` 支持多记录 — CONFIRMED（18.0 #154132）

`copy_data` 现在返回**列表**（每条记录一个值字典），`self` 可能是多记录集。若有自定义 `copy_data` / `copy`，需处理 `self` 为多记录的情况。

```python
# 18 正确的多记录写法
def copy_data(self, default=None):
    return [super(MyModel, rec).copy_data(default)[0] for rec in self]
```

### 2.6 字段属性 `group_operator` → `aggregator` — CONFIRMED（17.2 #127353）

> 首次出现于 **17.2（Online）**。对 17.0 CE 源码是新增改动，对 17.2+ 源码已是事实——两种起点都需在 17→18 处理。

```python
# 17
allocated = fields.Float("Allocated %", group_operator='avg')
# 18
allocated = fields.Float("Allocated %", aggregator='avg')
```

17.2 起还可对**未存储的 related 字段**分组/聚合/排序（需 `related_sudo=True` 或 `compute_sudo=True`）。

### 2.7 其他 ORM 行为变更

- **`inselect` 运算符移除**（17.4 #171371）：改用 `in` 配合 `Query` / `SQL` 对象。

  ```python
  # 17
  operator_new = 'inselect' if ... else 'not inselect'
  # 18
  # 用 domain leaf ('field', 'in', query) 或 SQL(...)
  ```

- **搜索非存储 related 字段**：18 不再记警告而是**直接抛异常**；若要改写搜索结果，改覆写 `search_fetch`（而非 `search`，因 `search` 未必每次都被调用）。
- **`_flush_search()` 弃用**（17.1 #144747）：刷新交由 `execute_query()` 完成；确认自定义重写已移除。
- **翻译 `_()` 改为 `env._()`**（18.0 #174844）：`self.env._("text")` 更直接、基于环境的语言属性；` LazyTranslate` 工厂提升惰性翻译效率。
- **`_sql_constraints` 同名校验更严**（DeployMonkey `[verify]`）：重复约束名在升级时直接报错；保留唯一命名。
- **日期粒度**（17.3 #159528）：新增 `month_number` / `quarter_number` / `week_number`，可在 `read_group` / `_read_group` / domain 中跨年分组，如 `('date_field.month_number','=','2')`。

---

## 第 3 章 · 安全与 res.groups（17→18 基本不变）

> **关键结论**：17→18 的**安全文件格式与 `res.groups` 模型都不变**。以下仅在"清理 17 代码"时相关，切勿套用 18→19 的 `privilege_id` / `ir.access.csv` 改动（那是 19→20 的事）。

- `security/ir.model.access.csv` 列格式**不变**（`perm_read/perm_write/perm_create/perm_unlink`）。
- `res.groups.category_id` / `groups_id` / `users` 字段**不变**（18→19 才会改）。
- 本步唯一与安全相关的 API 改动是第 2.3 章的 `check_access` / `has_access` / `_filtered_access` 合并——它简化权限检查，但**不改变**模型/字段结构。

---

## 第 4 章 · 视图、QWeb 与前端

### 4.1 `tree` → `list`（视图层头号改动）— CONFIRMED

见第 1.1 章。这是 17→18 视图层 90% 的工作量。

### 4.2 `colors` 属性移除 → `decoration-*` — CONFIRMED（见 1.1，`[verify]` 兜底）

`<tree colors="red:state=='draft'">` → `<list decoration-danger="state=='draft'">`。`decoration-*` 值支持新的 CSS 颜色类（`danger`/`success`/`info`/`warning`/`muted`/`primary`/`bf`/`it`）。

### 4.3 视图中缺失字段自动补 `invisible` — CONFIRMED（18.0 #137031）

在表达式（`invisible` / `column_invisible` / `readonly` / `required` / `context` / `domain`）中引用但视图未声明的字段，18 会**自动作为 invisible 字段加入**。因此遗留的 `invisible="1"` 显式字段多半可删减清理。

### 4.4 窗口动作建议声明 `view_ids` / 字段路径 — CONFIRMED（OCA 18.0 指南）

`ir.actions.act_window` 推荐声明字段路径（`res_model` 上的字段）以获得更友好的 URL；`tree_view_ref` → `list_view_ref`（context key，见 1.1）。

### 4.5 `kanban-box` → `card`（版本归属有分歧，标 `[verify]`）

OCA《Migration to version 18.0》明确列出："The kanban views arch have been simplified: kanban-box is replaced by card definition."——即 18.0 把 kanban 根模板 `kanban-box` 简化为 `card`。**但**本工作台的 18→19 烹饪书（已对 19.0 源码核实）将 `kanban-box`→`card` 归因于 19.0 的 Owl 3 kanban 重写。

> **作用域守卫**：若你的 17 代码出现 `t-name="kanban-box"` 或 kanban 模板里的 `kanban-box` 类名，请在 18.0 实际模板中核实它究竟改为 `card`（18.0 改动）还是仍保留到 19.0 才改。**建议**：现在就按 OCA 指南尝试 `kanban-box`→`card`；若 18.0 模板仍用 `kanban-box`，则保留并在 18→19 步骤处理。两项技能不得冲突——以 18.0 实际源码为准。

### 4.6 `states` 字段属性移除 — `[verify]`（DeployMonkey）

`states="draft,open"` 形式的字段 `states` 属性在 18 被移除，改用 `invisible` / `readonly` 条件表达式。若自定义字段用了 `states`，改为条件属性。`[verify]`：未在 18.0 官方 changelog 中找到明确条目，仅 DeployMonkey 报告。

### 4.7 `fields_view_get()` → `get_views()` — `[verify]`（DeployMonkey）

旧式 `fields_view_get` / `_fields_view_get` 在 18 移除，改用 `get_views()`。自定义需读取视图结构的代码须迁移。`[verify]`：OCA 18.0 指南未明确列出，仅 DeployMonkey 报告。

### 4.8 前端资源（asset / SCSS）— `[verify]`

DeployMonkey 报告 18 更新了资源打包：部分子 bundle 重组、`web.assets_backend` 保留但子 bundle 调整、主题 SCSS 变量重命名、`__manifest__.py` 的 asset 声明语法更新。自定义前端若依赖特定 bundle 名或旧 SCSS 变量，需复核。`[verify]`：属前端破坏性，建议实机升级时人眼核对。

### 4.9 Owl 框架：仍是 Owl 2 — CONFIRMED（与 18→19 区分）

**Odoo 18 仍使用 Owl 2**，前端组件**无需**重写为 `setup()`（那是 19.0 的 Owl 3 断裂）。17→18 的前端工作量集中在 `tree`→`list` 的 XML/JS 改名，而非框架升级。

---

## 第 5 章 · HTTP、邮件与二进制

### 5.1 控制器 `type='json'` → `type='jsonrpc'` — CONFIRMED（18.1 #183636）

> 首次出现于 **18.1（Online）**。纳入本书（见 0.2 范围约定），因为对从 17 出发的迁移是新增。

```python
# 17 / 18.0
@app.route('/my/endpoint', type='json', auth='user')
def my_endpoint(self): ...
# 18.1+
@app.route('/my/endpoint', type='jsonrpc', auth='user')
def my_endpoint(self): ...
```

- **线协议完全相同**，无需改任何 JavaScript，只改 Python 的 `type=` 值（mindscript 升级审计器："线协议相同，无需改 JS"）。
- 仅 `@http.route(type='json')` 受影响；`type='http'` 不变。外部 `/json/2/...` 与 XML-RPC 端点无 17→18 变化。
- 18.1 起旧别名仍可用但会记 `DeprecationWarning`。

### 5.2 邮件与 server action — 稳定

`mail.thread`、消息/活动 API 在 17→18 基本稳定。`mail.thread.cc` 移除、`mail_post` server-action 重构都是 **19→20** 改动，不在此步。

### 5.3 二进制 / Excel / PDF / 时间

17→18 无报告破坏性变更：`fields.Binary`、PyTZ/`zoneinfo`、`xlsxwriter` 报表渲染、服务端时间辅助均稳定跨版本。

### 5.4 实时通信：Longpolling → WebSocket

bus/im 的实时推送改用 WebSocket（基础设施层），自定义代码一般无需改动，但部署需启用对应通道。

---

## 第 6 章 · 模块 / 模型 / 字段映射（17→18 较轻）

> OCA 18.0 指南明确：**本步聚焦框架变更，不罗列数据模型变更**（后者因模块而异，且极其庞大）。数据模型改名请查 OpenUpgrade 项目的 `upgrade_analysis.txt`。以下仅列框架级、跨模块通用的重命名。

### 6.1 通用字段/属性改名（框架级）— CONFIRMED

| Odoo 17 | Odoo 18 | 版本 | 来源 |
|---|---|---|---|
| `<tree>` 视图类型 | `<list>` | 18.0 | PR #159909（codemod `17.5-01`） |
| `<tree colors="...">` | `<list decoration-*` | 18.0 | 源码核实 |
| `tree_view_ref` (context) | `list_view_ref` (context) | 18.0 | OCA |
| `name_get()` | `display_name` 计算 / `_compute_display_name` | 18.0 | #122085→移除 |
| `_name_search()` | `_search_display_name()` | 18.0 | #174967 |
| `check_access_rights()` / `check_access_rule()` | `check_access(operation)` | 18.0 | #179148 |
| `_filter_access_rules*()` | `_filtered_access(operation)` | 18.0 | #179148 |
| `user_has_groups()` | `self.env.user.has_group()` | 18.0 | #151597 |
| `check_recursion()` | `has_cycle()` | 18.0 | OCA |
| `field.group_operator` | `field.aggregator` | 17.2 | #127353 |
| `domain` 运算符 `inselect` | `in` + `Query`/`SQL` | 17.4 | #171371 |
| `_()`（模块级） | `self.env._()` | 18.0 | #174844 |
| `translations` 取用 | `self.env.translations` | 18.0 | #174844 |
| `@http.route(type='json')` | `@http.route(type='jsonrpc')` | 18.1 | #183636 |
| `copy_data` 单条返回 | `copy_data` 返回列表 | 18.0 | #154132 |

### 6.2 模块改名（manifest `depends`）— 17→18 基本无

与 18→19（web_editor 拆分）不同，**17→18 没有核心模块改名**。`web_editor` 在 18 仍可用（19 才拆）。第三方应用是主要阻塞点：每个付费/OCA 应用都需有 18.0 分支，否则无法完成升级（ODIWARE 指南）。

### 6.3 数据模型改名 — 见 OpenUpgrade

`account.*` / `stock.*` / `hr.*` 等业务模型字段改名属 18→19 或模块特定迁移，不在本书范围。建议直接查阅 OCA OpenUpgrade 的 `upgrade_analysis.txt`（按核心模块拆分）。

### 6.4 症状 → 修复索引

| 18 安装/运行时症状 | 可能原因 | 修复锚点 |
|---|---|---|
| `ValueError: Wrong value for ir.ui.view.type: 'tree'` | `<tree>` 未改 `<list>` | 第 1.1 / 4.1 章 |
| 列表行不着色 | `colors="..."` 未改 `decoration-*` | 第 1.1 / 4.2 章 |
| 安装时 `AttributeError: name_get` / 视图显示名异常 | `name_get` 已移除 | 第 2.1 章 |
| 按名称搜索失效 | `_name_search` 已移除 | 第 2.2 章 |
| `AttributeError: check_access_rights` | 改用 `check_access` | 第 2.3 章 |
| `AttributeError: user_has_groups` | 改用 `env.user.has_group` | 第 2.3 章 |
| `AttributeError: check_recursion` | 改用 `has_cycle` | 第 2.4 章 |
| 字段 `group_operator` 告警/失效 | 改用 `aggregator` | 第 2.6 章 |
| 搜索非存储 related 字段抛异常 | 改覆写 `search_fetch` | 第 2.7 章 |
| 路由 import 时记弃用 | `type='json'`→`jsonrpc` | 第 5.1 章 |
| 窗口动作仍显示 tree 视图 | `view_mode` 未改 | 第 1.1 章 |
| 继承视图 XPath 失效 | `//tree` 未改 `//list` | 第 1.1 章 |

---

## 第 7 章 · 缓存 / SQL、字段与域

### 7.1 SQL 安全拼接 — CONFIRMED（17.0 引入，18 沿用）

`SQL(...)` 包装对象自 17.0（#134677）引入，17→18 **不变**。务必用 `SQL()` 组合 SQL，绝不拼接 f-string，避免注入。`inselect` 运算符已在 17.4 移除（见 2.7），改用 `SQL(..., field, [values])` 或 domain `in`。

### 7.2 字段与域

- `aggregator`（17.2）取代 `group_operator`（见 2.6）。
- `Domain` API（`from odoo import Domain`，18.1 #170009）：优先用 `Domain.AND` / `Domain.OR` / `Domain.TRUE` / `Domain.FALSE` 替代 `expression.AND/OR`。
- 声明式约束/索引（`models.Constraint` / `models.Index`，18.1 #175783）：**可选**新写法，覆盖旧 `_sql_constraints`；非强制。

  ```python
  # 18.1+ 可选
  _name_unique = models.Constraint('UNIQUE(name)', 'Name must be unique.')
  ```

  > 注意：`_sql_constraints` 在 17→18 **仍可正常工作**，声明式 `models.Constraint` 是 18.1 起的可选现代写法，不强求。18→19 的 codemod `18.1-00-sql-constraint` 才会自动重写它。

- 非存储 related 字段搜索抛出而非警告（见 2.7）。
- `_read_group` 新签名自 16.3（#110737）已在 17 使用；18.2 起 `read_group` 被弃用、推荐 `_read_group`（属 18.2 Online，纳入本书范围约定）。

---

## 第 8 章 · 认证 / 测试与校验

- **安装时视图校验更严**：畸形 XPath / 缺失字段引用会在安装时抛错（见第 4.3 章自动补字段）。加一道视图 RNG 检查。
- 以可见弃用警告启动服务（`--dev=all`），清掉**每一个** `DeprecationWarning`——它们是 18→19 的硬断裂前兆（Owl 3、ORM 包拆分等）。
- 在 18.0 沙箱跑 `odoo-bin -u <module> --test-tags /<module>`；domain `TypeError` 与视图 RNG 错误放最后修（最"吵"）。
- 17→18 对外部 JSON-2 / XML-RPC 测试契约**无改动**。

---

## 第 9 章 · upgrade_code codemod

### 9.1 运行 codemod

`odoo-bin upgrade_code` 是 Odoo 自带源码重写工具。17→18 **只需从 18.0 安装**对 17 源码运行——但 18.0 树中唯一有效的脚本是 `17.5-01-tree-to-list`：

```bash
# 先 dry-run，在干净 git 分支上
odoo-bin upgrade_code --from 17.0 \
  --addons-path /path/to/addons --dry-run

# 再真实运行（只重写 tree→list）
odoo-bin upgrade_code --from 17.0 \
  --addons-path /path/to/addons

# 也可单跑该脚本
odoo-bin --addons-path=${YOUR_PROJECT} upgrade_code \
  --script 17.5-01-tree-to-list.py
```

- Codemod 只重写 **Python/XML/JS 源码**，不做数据迁移；数据升级留在模块 `migrations/18.0/` 脚本。
- 逐文件审查 `git diff` 并在专用分支提交（社区反馈：`editable` / `create` / `default_order` 属性有时被移到标签外导致畸形 XML，必须人眼复核）。

### 9.2 哪些脚本对 17→18 真正运行

18.0 树 `odoo/upgrade_code/` 目录清单（已核实）：

| Script | 重写内容 | 是否对 17→18 生效 |
|---|---|---|
| `17.5-00-example.py` | 模板示例，**非真实 codemod** | 否 |
| `17.5-01-tree-to-list.py` | `<tree>`→`<list>`（XML/Python/JS 三处，跳过含 tree 的 XML-ID） | **是（唯一）** |

> **作用域守卫**：`18.1-00-sql-constraint`、`18.1-02-route-jsonrpc`、`18.5-*` 等脚本**不在 18.0 树**中（它们随 19.0 发布，供 18→19 使用）。17→18 的 `type='json'`→`jsonrpc`（18.1）和 `models.Constraint`（18.1）**没有 codemod**，须手工改（见第 5.1 / 7.2 章）。

### 9.3 Codemod 修不了、需手工的项

- `name_get` → `display_name` / `_search_display_name`（第 2.1–2.2 章）。
- `check_access_rights`/`check_access_rule`/`user_has_groups`/`check_recursion` → 新 API（第 2.3–2.4 章）。
- `group_operator` → `aggregator`（第 2.6 章）。
- `colors` → `decoration-*`（第 1.1 章）。
- `type='json'` → `type='jsonrpc'`（第 5.1 章）。
- `kanban-box` → `card`（第 4.5 章，`[verify]` 版本归属）。
- `states` / `fields_view_get` / asset-SCSS（第 4.6–4.8 章，`[verify]`）。

### 9.4 Scanner 契约

随附的 `Odoo17to18Migration/scripts/scan_addon.py`（版本无关，从 19→20 技能逐字复制）标记发现项并打印 18.0 替换 + 是否有 codemod 覆盖：

```bash
python3 Odoo17to18Migration/scripts/scan_addon.py /path/to/addons --addon my_module --json
# 退出码 1 = 有发现项
```

### 9.5 写自己的脚本

要新增自定义 17→18 重写，放到 18.0 `odoo/upgrade_code/` 布局下（或本地 `migrations/18.0/` 的 pre/init 数据脚本）再跑。每个脚本单一职责、幂等；提交结果 `git diff` 时附上相关 `references/*.md` 的锚点。

---

## 第 10 章 · 迁移实战清单

### 10.1 Grep 速查（pattern → 动作 → 见章节）

```
<tree                        → <list（第 1.1 / 4.1 章）
colors="                     → decoration-*（第 1.1 章）
tree_view_ref                → list_view_ref（第 1.1 章）
view_mode.*tree             → list（第 1.1 章）
//tree                      → //list（XPath，第 1.1 章）
def name_get                → display_name 计算（第 2.1 章）
def _name_search            → _search_display_name（第 2.2 章）
check_access_rights(        → check_access(（第 2.3 章）
check_access_rule(          → check_access(（第 2.3 章）
_filter_access_rules        → _filtered_access(（第 2.3 章）
user_has_groups(            → env.user.has_group(（第 2.3 章）
check_recursion(            → has_cycle(（第 2.4 章）
group_operator=             → aggregator=（第 2.6 章）
inselect                   → in + Query/SQL（第 2.7 章）
module-level _(            → self.env._(（第 2.7 章）
type='json' 路由            → jsonrpc（第 5.1 章，18.1）
kanban-box                 → card（第 4.5 章，[verify]）
states= 字段属性            → invisible/readonly 条件（第 4.6 章，[verify]）
fields_view_get(           → get_views(（第 4.7 章，[verify]）
depends: ['web_editor']     → 18 仍可用，勿动（见第 4.9 章）
```

### 10.2 端到端工作流

1. **Triage（扫描）**：`python3 Odoo17to18Migration/scripts/scan_addon.py /path/to/addons`——按文件分组列出发现项、行号、18.0 替换、是否被 codemod 覆盖。
2. **Codemod（仅 tree→list）**：干净 git 分支上，从 18.0 安装跑 `odoo-bin upgrade_code --from 17.0 --dry-run` 再真实跑；逐文件审查 `git diff`（重点查 `editable`/`create`/`default_order` 是否畸形）。
3. **人工映射**：对 scanner 标 `manual` 的项，套用对应章节替换（视图 → 第 1.1/4 章；ORM/API → 第 2 章；HTTP → 第 5.1 章；字段属性 → 第 2.6/7.2 章）。
4. **校验**：重跑 scanner（期望 0 发现）；`odoo-bin -u <module> --test-tags /<module>`；用 `--dev=all` 启动清掉每个 `DeprecationWarning`（它们是 18→19 硬断裂）；最后修 domain `TypeError` 与视图 RNG 错误。
5. **报告**：逐模块汇总——codemod 改动、人工编辑（附所用章节锚点）、剩余 `[verify]`/`[EE-verify]` 项、测试状态。

---

## 溯源附录（Provenance）

- **官方 ORM Changelog**：`odoo.com/documentation/18.0/developer/reference/backend/orm/changelog.html` 与 saas-18.2 版（PR #122085, #127353, #137031, #144747, #151597, #154132, #159528, #159909, #170009, #171371, #174844, #174967, #175783, #179148, #183636）。
- **GitHub 18.0 源码核实**：`odoo/addons/base/models/ir_ui_view.py`（`type` 选单仅含 `list`、处理 `decoration-*`、无 `colors`）；`odoo/models.py`（`check_access`/`_search_display_name`/`has_group` 存在，`name_get`/`_name_search`/`check_access_rights`/`user_has_groups`/`check_recursion` 的 `def` 已移除）；`odoo/release.py`（`version_info = (18, 0, 0, ...)`）；`odoo/upgrade_code/`（仅 `17.5-00-example.py` 与 `17.5-01-tree-to-list.py`）。
- **社区交叉核实**：OCA `maintainer-tools`《Migration to version 18.0》；Cybrosys《Odoo 18 v/s Odoo 17》；ODIWARE《17 to 18 Migration Guide》；DeployMonkey《Odoo 18 Breaking Changes》。
- **核查日期**：2026-11-01。
- **诚实标注**：`[verify]` 项（PG 地板、kanban-box 版本归属、states 属性、fields_view_get、asset/SCSS）源自单一社区来源，已注明待 18.0 源码最终确认，未以确证语气陈述。

---

*本烹饪书（单卷）覆盖 17.0 → 18.0 的视图层（tree→list 头号改动）、ORM/模型 API（name_get/check_access/user_has_groups/check_recursion 移除与替代）、字段属性（aggregator）、HTTP 路由（jsonrpc）、以及有限的 codemod 面。机器可读的映射表与扫描器见同目录 `Odoo17to18Migration/`。下一跳 18→19（Owl 3 / ORM 包拆分 / 安全模型重构）由对应技能处理。*
