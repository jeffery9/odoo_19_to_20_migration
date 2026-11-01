# Odoo 迁移烹饪书：13.0 → 14.0

> 本烹饪书是 **13→14** 迁移的事实基准（Fact Baseline）。配套技能见 `Odoo13to14Migration/`。
> 它专为**自定义模块**（CE 与 EE）从 Odoo 13 升级到 14 编写，覆盖所有破坏性（breaking）变更，
> 并明确**版本作用域**——只收 13→14 区间内真实发生的变更，更晚版本的改动一律排除（见第 1 章红线）。
>
> **可信度标记**：`CONFIRMED` = OCA《Migration to version 14.0》官方迁移指南 + 14.0 源码/提交核对
> （odoo/odoo#53335、commit f0481392 / 1f48130 等）+ 社区源交叉核实；
> `[verify]` = 单一社区来源或来源间有分歧、待 14.0 实机/源码最终确认。

---

## 目录

1. 导言与版本作用域
2. 头号断裂：`ir.actions.*` 访问移除（sudo 化）与 `_for_xml_id`
3. 视图语法：`invisible` / `readonly` 动态表达式 → `attrs`
4. ORM / 模型 API：`_name_search` 返回 ids、`_compute_display_name` → `name_get`、`with_context(force_company=)` → `with_company`、`Char` 的 `size` 移除、瞬态模型 ACL、记录规则全局字段
5. 字段与数据模型：`selection_add` 必须 `ondelete`、`string` 属性在列表视图显示为文本
6. 库存（[verify]）：`stock.picking` 字段改名
7. 安全与 `res.groups`（13→14 不变；TransientModel 需显式 ACL）
8. HTTP / 邮件 / 二进制（13→14 基本不变）
9. 模块 / 模型 / 字段映射
10. 测试与校验
11. `upgrade_code` codemod（13→14 无）
12. 迁移实战清单

---

## 1. 导言与版本作用域

Odoo 14.0（2020-10）是一次**"视图表达式收紧 + 动作访问 sudo 化 + ORM 接口微调"**的版本。与 12→13
（会计重写）、15→16（支付/模型重命名）、16→17（`attrs`/`states` 硬拒）、17→18（`tree`→`list`）相比，
13→14 的破坏面集中在**视图属性约束**、**`ir.actions.*` 读取受限**、以及**若干 ORM 接口语义变化**。

**本版本对的头号断裂**：`ir.actions.*` 对象的直接访问被移除（必须 sudo 或通过 `/web/action/load`、
`_for_xml_id`）；同时视图的 `invisible`/`readonly` 不再接受动态表达式（如 `state=='draft'`），必须改用 `attrs`。

### 版本作用域红线（勿套用更晚版本的改动）

| 更晚版本的改动 | 归属版本 | 在 13→14 中 |
|---|---|---|
| `account.invoice`→`account.move`、`customer_rank`、`binding_view_types` | 12→13 | ❌ 排除（13 已处理） |
| `attrs`/`states` **硬拒**（改为内联表达式） | 16→17 | ❌ 排除（14 仍用 `attrs`/`states`） |
| `<tree>` → `<list>` | 17→18 | ❌ 排除（14 仍是 `tree`） |
| `name_get` **移除** | 17→18 | ❌ 排除（14 反而要求用 `name_get`） |
| `ir.model*` 访问移除 / `t-raw` 移除 / 资产进 manifest | 14→15 | ❌ 排除 |
| `SavepointCase`/`Environment.manage` 移除 | 14→15 | ❌ 排除（14 仍可用） |
| `payment.acquirer`→`payment.provider`、`coupon`→`loyalty` | 15→16 | ❌ 排除 |
| `track_visibility`→`tracking` | **12→13** | ❌ 排除（常见于 14→15 误传，实为 13.0） |

> **Python 底座**：13.0 / 14.0 均要求 Python 3。14.0 仍兼容 Python 3.6+（Python 3.10 抬升是 **16→17**）。

### 配套技能参考表（skill references）

本烹饪书的事实基准由 `Odoo13to14Migration/references/` 下的六份映射表承载，二者逐条对齐、零漂移：
`references/orm-api.md`（_name_search / name_get / with_company / Char size / TransientModel / 记录规则）、
`references/views-qweb.md`（ir.actions.* 访问移除、invisible/readonly→attrs、前端）、
`references/models-mapping.md`（selection_add ondelete、string 属性、stock.picking [verify]）、
`references/security.md`（res.groups 不变 + TransientModel ACL）、
`references/http-rpc-mail.md`（HTTP/邮件/二进制不变）、
`references/upgrade-code.md`（无 codemod + migrations/14.0 工作流）。

---

## 2. 头号断裂：`ir.actions.*` 访问移除（sudo 化）与 `_for_xml_id`  — CONFIRMED

14.0 移除了对 `ir.actions.*` 模型对象的直接访问（`ir.actions.act_window` /
`ir.actions.server` / `ir.actions.client` / `ir.actions.report` 等）。自定义代码若直接
`self.env['ir.actions.act_window'].search(...)` 或 `env.ref('...')` 读取动作会失败。

### 修复方式

- **需要读取动作字典**：用 `self.env['ir.actions.act_window']._for_xml_id('module.action_xml_id')`
  （返回 action dict，不触碰受限访问）。
- **确需操作动作记录**：用 `sudo()` 提升权限后访问。
- **通过控制器**：走 `/web/action/load` 端点（前端/HTTP 场景）。

### Before（13.0，仍可用）

```python
action = self.env.ref('my_module.action_my_model').read()[0]
# 或
action = self.env['ir.actions.act_window'].search([('res_model','=','my.model')])
```

### After（14.0）

```python
# 读取动作定义字典（推荐）
action = self.env['ir.actions.act_window']._for_xml_id('my_module.action_my_model')

# 必须操作记录时
action = self.env['ir.actions.act_window'].sudo().search([('res_model','=','my.model')])
```

> 源码依据：odoo/odoo#53335。注意这与 **15.0 的 `ir.model*` 访问移除** 是**不同对象**——
> 13→14 限制的是 `ir.actions.*`，14→15 才限制 `ir.model*`。

---

## 3. 视图语法：`invisible` / `readonly` 动态表达式 → `attrs`  — CONFIRMED

14.0 收紧了视图属性：`<field>` / `<page>` / `<group>` 上的 `invisible` 与 `readonly` **不再支持动态表达式**
（如 `state=='draft'`、`x>0`）；这类条件必须改用 `attrs`。**唯一例外**是直接 context 查询，如
`invisible="context.get('invisible')"` 仍合法。

### Before（13.0）

```xml
<field name="discount" invisible="partner_type == 'b2c'" readonly="state == 'done'"/>
```

### After（14.0）

```xml
<field name="discount" attrs="{'invisible': [('partner_type','=','b2c')],
                                'readonly': [('state','=','done')]}"/>
<!-- 仅 context 直查可保留 -->
<field name="x" invisible="context.get('hide_x')"/>
```

**要点**：

- `state=='draft'` 这类表达式必须整体搬进 `attrs` 的 domain 列表。
- `attrs` 在 14.0 **完全保留且是推荐写法**（它直到 **16→17** 才被进一步"硬拒"为内联表达式）。
- 扫描 id：`invisible-expr`（正则 `(invisible|readonly)="[^"]*(==|!=|<=|>=|<|>|\{)` 捕捉动态表达式）。

---

## 4. ORM / 模型 API  — CONFIRMED（除标注外）

### 4.1 `_name_search` 返回 ids 列表  — CONFIRMED

14.0 起覆写 `_name_search` 必须**返回 id 列表**（不再返回 `(id, display_name)` 元组列表）。

```python
# Before（13.0）：返回 (id, name) 元组
def _name_search(self, name, args, operator='ilike', limit=100):
    return self.name_get()

# After（14.0）：仅返回 ids
def _name_search(self, name, args, operator='ilike', limit=100):
    return self.search([('name','ilike',name)] + args, limit=limit).ids
```

- 扫描 id：`name-search`（正则 `_name_search`）。源码：odoo/odoo commit 1f48130。

### 4.2 `_compute_display_name` 覆盖 → 改用 `name_get`  — CONFIRMED

14.0 若想自定义 `display_name`，应覆写 `name_get` 并在其上加 `@api.depends`（对应计算字段）；
若要 stored `display_name`，则覆写 `name_search`。直接覆写 `_compute_display_name` 不再生效。

```python
# After（14.0）
@api.depends('firstname', 'lastname')
def name_get(self):
    res = []
    for rec in self:
        res.append((rec.id, f"{rec.firstname} {rec.lastname}"))
    return res
```

- 扫描 id：`compute-display-name`（正则 `_compute_display_name`）。

### 4.3 `with_context(force_company=...)` → `with_company(...)`  — CONFIRMED

```python
# Before（13.0）
records = self.with_context(force_company=company.id)
# After（14.0）
records = self.with_company(company)
```

> 注：`with_company()` 在 **13.0 引入**，但 `force_company` 在 **14.0 才弃用**（13.0 仍可用）。

- 扫描 id：`force-company`（正则 `force_company`）。

### 4.4 `Char` 字段移除 `size=X` 属性  — CONFIRMED

```python
# Before（13.0）
code = fields.Char(size=16)
# After（14.0）：size 不再有效（不再限制字符串长度）
code = fields.Char()
```

- `size` 属性被忽略（ODoo 不再用它限制存储长度）。
- 扫描 id：`char-size`（正则 `fields\.Char\([^)]*size\s*=`）。

### 4.5 瞬态模型（TransientModel）需显式 ACL  — CONFIRMED

14.0 起向导（`TransientModel`）**需要显式安全 ACL**（以及可选记录规则），不能再隐式访问。
在 `security/ir.model.access.csv` 中为向导模型补一行访问权。

### 4.6 记录规则移除全局字段赋值行  — CONFIRMED

记录规则中原本的全局字段赋值行（针对 computed `global` 字段）需移除——该字段现在是 computed。

---

## 5. 字段与数据模型

### 5.1 `selection_add` 必须带 `ondelete=`  — CONFIRMED

14.0 起通过 `selection_add` 给 Selection 字段追加选项时，**必须**为每个旧值指定卸载时的处理
（`ondelete`），否则迁移/卸载会报错。

```python
# Before（13.0）
state = fields.Selection(selection_add=[("foo", "Foo")])
# After（14.0）
state = fields.Selection(selection_add=[("foo", "Foo")],
                         ondelete={"foo": "set null"})   # 或 "cascade"
```

- 源码：odoo/odoo commit f0481392。
- 扫描 id：`selection-ondelete`（正则 `selection_add=`）。

### 5.2 `string` 属性在列表视图显示为文本  — CONFIRMED（轻微）

14.0 起 `<field>` 的 `string` 属性在**列表（tree）视图**中直接显示为文本（而非悬浮 tooltip），
占用更多屏幕空间。建议改用 `title` 属性保留旧"悬浮提示"行为。

### 5.3 库存字段改名（[verify]）

14.0 库存进一步重构：`stock.picking` 的 `move_lines` → `move_ids_without_package`、
`move_line_ids` → `move_line_ids_without_package`（支持"整包移动"语义）。

```python
# 可能需改动（[verify]）
picking.move_lines          # 13.0
picking.move_ids_without_package   # 14.0（[verify]）
```

> 标注 `[verify]`：OCA 14.0 核心迁移指南未逐条列出库存字段改名，且涉及 stock 子模块；建议在
> 14.0 实机/源码（`stock.picking` 模型）核对后固化。

---

## 6. 库存（见 5.3，[verify]）

`stock.picking` 字段改名（5.3）归属 14.0 但需实机确认，统一放在此处并以 `[verify]` 标注。

---

## 7. 安全与 `res.groups`（13→14 不变；TransientModel 需显式 ACL）  — CONFIRMED

- `ir.model.access.csv`、`ir.rule`、`res.groups` 的写法在 13→14 **不变**（除第 4.5 的 TransientModel ACL）。
- `groups` 字段、`implied_ids` 继承链、`category_id` 机制一致。
- 安全文件（CSV/XML）**基本无需改动**，仅向导模型需补 ACL。

> **红线**：勿套用 18→19 的 `res.groups` privilege 模型或 19→20 的 `ir.access.csv` 改动——远晚于 14.0。

---

## 8. HTTP / 邮件 / 二进制（13→14 基本不变）  — CONFIRMED

- `http.route`、`request.env`、`http.Controller` 在 13/14 一致；`type='json'` 仍是 `json`
  （重命名为 `jsonrpc` 是 **18.1**）。
- 邮件 `mail.template`：`body_html` 仍用 **Jinja** 语法（Jinja→QWeb 重写是 **14→15**）；
  `subtype` → `subtype_xmlid` 改名也是 **14→15**，不在 13→14。
- `message_post(body=..., message_type=...)` 行为一致。
- `get_resource_path` 在 13/14 仍使用（`file_path` 是 **16→17** 改名）。
- `ir.actions.*` 访问移除见第 2 章（属于视图/动作范畴，非 HTTP）。

---

## 9. 模块 / 模型 / 字段映射

| 13.0 | 14.0 | 类别 | 可信度 |
|---|---|---|---|
| 直接访问 `ir.actions.*` 记录 | `sudo()` / `_for_xml_id` / `/web/action/load` | 访问方式 | CONFIRMED |
| `invisible="state=='draft'"` 动态表达式 | `attrs` domain | 视图属性 | CONFIRMED |
| `readonly="x>0"` 动态表达式 | `attrs` domain | 视图属性 | CONFIRMED |
| `_name_search` 返回 `(id,name)` 元组 | 返回 `ids` 列表 | ORM 方法 | CONFIRMED |
| 覆写 `_compute_display_name` | 覆写 `name_get` + `@api.depends` | ORM 方法 | CONFIRMED |
| `with_context(force_company=...)` | `with_company(...)` | 环境 | CONFIRMED |
| `fields.Char(size=16)` | 移除 `size` | 字段属性 | CONFIRMED |
| `selection_add=[("foo","Foo")]` | `+ ondelete={"foo":"set null"}` | 字段属性 | CONFIRMED |
| `<field string="x">` 在 list 显示文本 | 改用 `title` | 视图属性 | CONFIRMED |
| TransientModel 隐式 ACL | 显式 ACL | 安全 | CONFIRMED |
| `stock.picking.move_lines` | `move_ids_without_package` | 字段改名 | [verify] |
| `stock.picking.move_line_ids` | `move_line_ids_without_package` | 字段改名 | [verify] |

**本版本对不涉及**的重大重命名（红线）：`payment.acquirer`→`payment.provider`（15→16）、
`coupon`→`loyalty`（15→16）、`stock.production.lot`→`stock.lot`（15→16）、
`ir.model*` 访问移除（14→15）、`t-raw` 移除（14→15）、`attrs`/`states` 硬拒（16→17）、`tree`→`list`（17→18）。

---

## 10. 测试与校验

- `TransactionCase` / `SavepointCase` 在 13/14 均可用（`SavepointCase` 别名**移除是 15.0**，14.0 无影响）。
- `Environment.manage()` 仍需要（移除是 **15.0**）。
- 校验：`odoo-bin -u <module> --test-tags /<module>`，开启 `--dev=all` 清除 `DeprecationWarning`。
- 视图：用 `odoo-bin -u <module> --dev=all` 让 QWeb 在加载时校验属性合法性（`invisible` 动态表达式会报错）。

---

## 11. `upgrade_code` codemod（13→14 无）  — CONFIRMED

`odoo-bin upgrade_code` 的 codemod 引擎**从 18.0 才存在**（17.0 及更早均无 `odoo/upgrade_code/` 模块）。
因此 **13→14 零 codemod**，全部为手工改动 + 数据库级 `migrations/14.0/` 脚本（由 OpenUpgrade 处理）。

> ⚠️ **勿让用户跑 `upgrade_code --from 13.0`**——14.0 安装中该命令不存在，会报命令未找到。

---

## 12. 迁移实战清单

1. **扫描（triage）**：用 `Odoo13to14Migration/scripts/scan_addon.py` 找出 `ir.actions.*` 直接访问、
   `invisible`/`readonly` 动态表达式、`_name_search`、`_compute_display_name`、
   `force_company`、`Char` 的 `size`、`selection_add`、`stock.picking` 旧字段名。
2. **动作访问**：直接读 `ir.actions.*` → `_for_xml_id()` 或 `sudo()`；前端走 `/web/action/load`。
3. **视图**：`invisible="state=='draft'"` 等动态表达式 → `attrs` domain（仅 context 直查保留）。
4. **ORM**：`_name_search` 返回 `ids`；`_compute_display_name` → `name_get`；`force_company` → `with_company`；
   删 `Char` 的 `size`；`selection_add` 补 `ondelete`。
5. **安全**：为 TransientModel（向导）补显式 ACL；记录规则移除全局字段赋值行。
6. **库存（[verify]）**：核对 `stock.picking.move_lines`/`move_line_ids` 是否需在 14.0 改名。
7. **DB 迁移**：模块 `migrations/14.0/` 写数据脚本（如 selection 选项迁移）。
8. **校验**：`-u` + 测试 + 清 `DeprecationWarning`；视图加载校验 `invisible`/`readonly` 合法性。
9. **出报告**：列出每处改动、残留 `[verify]` 项（库存字段改名）。

---

## 附录 A：研究来源与溯源

- **OCA《Migration to version 14.0》**（maintainer-tools wiki）——权威变更清单（`invisible`/`readonly`
  动态表达式→attrs、`selection_add` 的 `ondelete`、记录规则全局字段移除、`Char` `size` 移除、
  `_compute_display_name`→`name_get`、`_name_search` 返回 ids、`with_context(force_company)`→`with_company`、
  `ir.actions.*` 访问移除（#53335）、TransientModel 显式 ACL、`string` 属性行为变化）。
- **odoo/odoo 提交** f0481392（`selection_add` ondelete）、1f48130（`_name_search` 返回 ids）、
  6835aeb0（`src_model`→`binding_model`/`binding_view_types` 后续，12→13 已覆盖）。
- **版本作用域红线**：对照 12→13 / 15→16 / 16→17 / 17→18 烹饪书，确认 account.move、`attrs` 硬拒、
  `name_get` 移除、`ir.model*` 移除、`t-raw` 移除、payment.provider 等**均不属于 13→14 首发**。

> 标注 `[verify]` 的项（`stock.picking` 字段改名）为需实机确认的库存子模块改动，建议以 14.0 源码
> （`stock.picking` 模型定义）最终确认后再固化到技能 references。
