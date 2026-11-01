# Odoo 迁移烹饪书：11.0 → 12.0

> 本烹饪书是 **11→12** 迁移的事实基准（Fact Baseline）。配套技能见 `Odoo11to12Migration/`。
> 它专为**自定义模块**（CE 与 EE）从 Odoo 11 升级到 12 编写，覆盖所有破坏性（breaking）变更，
> 并明确**版本作用域**——只收 11→12 区间内真实发生的变更，更晚版本的改动一律排除（见第 1 章红线）。
>
> **可信度标记**：`CONFIRMED` = OCA《Migration to version 12.0》指南 + 社区源（Cybrosys/Oejia/掘金/CSDN）交叉核实；
> `[verify]` = 单一社区来源或来源间有分歧、待 12.0 实机/源码最终确认。

---

## 目录

1. 导言与版本作用域
2. 头号断裂：`@api.one` 装饰器移除
3. ORM / 模型 API：`fields.Date` 运行时类型革命
4. 模型 API：`@api.model_create_multi` 与 `_parent_store`
5. 动作与 UI：`ir.actions.act_window.view` 移除
6. 字段与数据模型
7. 视图 / QWeb / 前端
8. HTTP / 邮件 / 二进制
9. 安全与 `res.groups`（11→12 不变）
10. 模块 / 模型 / 字段映射
11. 测试与校验
12. `upgrade_code` codemod（11→12 无）
13. 迁移实战清单

---

## 1. 导言与版本作用域

Odoo 12.0（2018-10）是一次**"新 API 收尾 + 日期类型下沉"**的版本。与 15→16（数据模型重命名）、
16→17（视图语法革命）、17→18（`tree`→`list` + 大量移除）、18→19（ORM 拆分）相比，11→12 的破坏面集中在
**装饰器与字段运行时类型**，对 XML/视图改动极小。

**本版本对的头号断裂**：`@api.one` 装饰器被移除；`fields.Date` / `fields.Datetime` 字段的运行时值从
"字符串"变为"真实的 `date` / `datetime` 对象"。这两点会同时引爆大量旧代码。

### 版本作用域红线（勿套用更晚版本的改动）

| 更晚版本的改动 | 归属版本 | 在 11→12 中 |
|---|---|---|
| `account.invoice` → `account.move` | 12→13 | ❌ 排除（12 仍是 invoice） |
| `customer`/`supplier` → `customer_rank`/`supplier_rank` | 12→13 | ❌ 排除 |
| `attrs`/`states` 硬拒 | 16→17 | ❌ 排除（12 仍用 attrs） |
| `tree` → `list` | 17→18 | ❌ 排除（12 仍是 tree） |
| `name_get` 移除 / `get_resource_path` 移除 | 17→18 / 16→17 | ❌ 排除 |
| `payment.acquirer` → `payment.provider` | 15→16 | ❌ 排除 |
| `t-raw` 移除 / `ir.model*` 访问移除 / 资产进 manifest | 14→15 | ❌ 排除 |

> **11.0 已要求 Python 3**，因此 11→12 **无 Python 2 → 3 断裂**（那是 10→11 的事）。

### 配套技能参考表（skill references）

本烹饪书的事实基准由 `Odoo11to12Migration/references/` 下的六份映射表承载，二者逐条对齐、零漂移：
`references/orm-api.md`（api.one / from_string / model_create_multi / parent_path / do_notify）、
`references/views-qweb.md`（act_window.view 移除 / t-field-options）、
`references/models-mapping.md`（11→12 字段模型映射 + 红线排除）、
`references/security.md`（安全不变）、
`references/http-rpc-mail.md`（HTTP/邮件/二进制不变）、
`references/upgrade-code.md`（无 codemod + migrations/12.0 工作流）。

---

## 2. 头号断裂：`@api.one` 装饰器移除  — CONFIRMED

Odoo 12 移除了 `@api.one` 装饰器。此前 `api.one` 会自动把 `self` 拆成单条记录并循环调用，返回值是单条结果的列表。

### Before（11.0，已失效）

```python
class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.one
    def action_do_something(self):
        # self 是单条记录
        self.state = "done"
        return True
```

### After（12.0）

```python
class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_do_something(self):
        # 无装饰器：self 是记录集，方法默认按"多记录"语义执行
        for record in self:
            record.state = "done"
        return True
```

**要点**：

- 模型方法**不加装饰器**即等同于"多记录"语义（旧 `api.multi` 行为）。`@api.multi` 在 12.0 **仍存在但已弃用**，
  建议在 12+ 直接省略或用 `@api.model`（纯模型方法）。
- 若方法原本依赖 `api.one` 的"单记录"语义（如直接访问 `self.name` 而非 `self.ids`），必须改成显式 `for record in self:` 循环。
- 返回值的含义变化：`api.one` 会把结果收集成列表；去掉后方法返回什么就是什么——检查调用方是否依赖列表返回值。

**扫描模式**：`@api.one` 装饰器、`api.one(` 调用。

---

## 3. ORM / 模型 API：`fields.Date` 运行时类型革命  — CONFIRMED

这是第二大连环断裂。在 11.0 及更早，`fields.Date`/`fields.Datetime` 在运行时是**字符串**，
需 `fields.Date.from_string()` / `to_string()` 转换；12.0 起运行时值是**真实的 `date` / `datetime` 对象**。

### Before（11.0）

```python
from odoo import fields

# 运行时 date_str 是 "2024-01-15" 这样的字符串
date_str = record.date_start
dt = fields.Date.from_string(date_str)   # 转成 date 对象才能做运算
fields.Date.to_string(dt + timedelta(days=1))
```

### After（12.0）

```python
from odoo import fields
from datetime import timedelta

# 运行时 record.date_start 已是 date 对象，可直接运算
dt = record.date_start + timedelta(days=1)
# 新工具：字符串 → date/datetime（替代已移除的 from_string）
d = fields.Date.to_date("2024-01-15")
d2 = fields.Datetime.to_datetime("2024-01-15 10:00:00")
```

**要点**：

- `fields.Date.from_string()` / `fields.Datetime.from_string()` 在 12.0 **已移除** → 改用 `fields.Date.to_date()` / `fields.Datetime.to_datetime()`。
- `fields.Date.to_string()` / `to_datetime` 的字符串化方法仍可用（用于写回字符串字段/SQL），但大多数场景下不再需要。
- 任何对日期字段做**字符串切片、正则、`strftime` 之前先转对象**的旧代码都会出问题——现在字段本身就是对象，`str(field)` 会得到 `2024-01-15`，而非此前可能的格式。
- 涉及 `search()` 中日期比较的旧式字符串写法需复核（ORM 现在期待 `date`/`datetime` 或 ISO 字符串）。

**扫描模式**：`from_string`、`to_string(`、`fields.Date.from_string`、`fields.Datetime.from_string`。

---

## 4. 模型 API：`@api.model_create_multi` 与 `_parent_store`  — CONFIRMED

### 4.1 `@api.model_create_multi`（12.0 新增）

12.0 对 `create()` 做了性能优化：现在可单次创建多条记录。覆写 `create` 必须加 `@api.model_create_multi`。

```python
# Before（11.0）：自定义 create 直接写，单条语义
@api.model
def create(self, vals):
    return super().create(vals)

# After（12.0）：覆写 create 必须声明 multi，self 是记录集
@api.model_create_multi
def create(self, vals_list):
    records = super().create(vals_list)
    # 对 records 做后处理
    return records
```

> 若只在 `super().create(...)` 前后加逻辑而**不覆写** `create`，则无需改动——只有显式 `def create(self, ...)` 才受影响。

### 4.2 `_parent_store`：去掉 `parent_left` / `parent_right`

12.0 用 `parent_path` 字符串路径替代经典的左右值字段。

```python
# Before（11.0）
class Category(models.Model):
    _name = "my.category"
    _parent_store = True
    parent_left = fields.Integer(index=True)
    parent_right = fields.Integer(index=True)
    parent_id = fields.Many2one("my.category", ondelete="cascade")

# After（12.0）
class Category(models.Model):
    _name = "my.category"
    _parent_store = True
    parent_id = fields.Many2one("my.category", ondelete="cascade")
    parent_path = fields.Char(index=True)   # 替代 parent_left/parent_right
```

> 迁移数据库时需由 OpenUpgrade 填充 `parent_path`（或安装时 `_parent_store` 自动维护）。

---

## 5. 动作与 UI：`ir.actions.act_window.view` 移除  — CONFIRMED

12.0 移除了 `ir.actions.act_window.view` 模型（该模型用于把窗口动作绑定到特定视图）。

### Before（11.0）

```xml
<record id="action_my_model" model="ir.actions.act_window">
    <field name="name">My Model</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">tree,form</field>
</record>
<record id="act_view_tree" model="ir.actions.act_window.view">
    <field name="act_window_id" ref="action_my_model"/>
    <field name="view_id" ref="my_model_view_tree"/>
    <field name="view_mode">tree</field>
</record>
```

### After（12.0）

```xml
<record id="action_my_model" model="ir.actions.act_window">
    <field name="name">My Model</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">tree,form</field>
    <field name="view_ids" eval="[
        (5, 0, 0),
        (0, 0, {'view_mode': 'tree', 'view_id': ref('my_model_view_tree')}),
        (0, 0, {'view_mode': 'form', 'view_id': ref('my_model_view_form')}),
    ]"/>
</record>
```

**要点**：原 `ir.actions.act_window.view` 记录删除；视图绑定改为动作上的 `view_ids`（o2m）或 `views`（多对多简化写法）。

**扫描模式**：`model="ir.actions.act_window.view"`。

---

## 6. 字段与数据模型

### 6.1 `do_notify` / `do_warning` 移除  — CONFIRMED

11.0 的 `self.do_notify(msg)` / `self.do_warning(msg)` 在 12.0 移除。改用异常或 `message_post`。

```python
# Before（11.0）
self.do_warning("数量不足")

# After（12.0）
raise UserError(_("数量不足"))
# 或在 chatter 提示：
self.message_post(body=_("数量不足"), message_type="notification")
```

### 6.2 其它字段注意点

- `search().ids` 取 id 列表、`search_count()` 计数——这两个在 11/12 均存在，无需改动（属早版本 API）。
- `Binary` 字段默认仍存 `ir.attachment`？——12.0 **尚未**改为默认存附件（那是 13.0 行为），11→12 保持原状。 `[verify]`
- `Selection` 字段：12.0 仍支持 `(key, label)` 元组写法；`selection_add` 的 `ondelete` 强制化是 **14.0** 的事，11→12 不受影响。

---

## 7. 视图 / QWeb / 前端

### 7.1 `t-field-options` → `t-options`  — CONFIRMED

QWeb 模板中 `t-field-options` 重命名为 `t-options`。

```xml
<!-- Before（11.0）-->
<span t-field="record.date" t-field-options='{"widget": "date"}'/>

<!-- After（12.0）-->
<span t-field="record.date" t-options='{"widget": "date"}'/>
```

### 7.2 前端依赖

12.0 对 JS 框架做了小幅升级（Bootstrap 4、jQuery 3 在 12 已就位，更大跃进在 13/14）。自定义 JS widget 若依赖旧 Bootstrap 3 类需复核，但 **11→12 的 JS 断裂远小于 13/14/15**。 `[verify]`

### 7.3 视图属性

`attrs`、`states`、`tree`、`form` 等视图机制在 12.0 **完全保留**（它们的硬拒/重命名发生在 16→17 / 17→18）。
11→12 的 XML 视图几乎无需改动，除非用到了第 5 章的动作绑定。

---

## 8. HTTP / 邮件 / 二进制

- `http.route` 装饰器、`request.env`、`http.Controller` 在 11/12 一致；`type='json'` 仍是 `json`（重命名为 `jsonrpc` 是 **18.1** 的事）。
- 邮件 `message_post`：`body` 默认纯文本/Markdown（HTML 转义处理在 12 与 11 类似；`body_is_html` 参数是 **16→17** 引入）。11→12 邮件 API 基本不变。
- `get_resource_path` / `file_path`：11/12 均使用 `get_resource_path`；`file_path` 是 16→17 的改名。11→12 不受影响。

---

## 9. 安全与 `res.groups`（11→12 不变）

- `ir.model.access.csv`、`ir.rule`、`res.groups` 的写法在 11→12 **不变**。
- `groups` 字段、`implied_ids` 继承链机制一致。
- 安全文件（CSV/XML）**无需改动**。

> **红线**：勿套用 18→19 的 `res.groups` privilege 模型或 19→20 的 `ir.access.csv` 改动——它们都远晚于 12.0。

---

## 10. 模块 / 模型 / 字段映射

| 11.0 | 12.0 | 说明 |
|---|---|---|
| `@api.one` 装饰的方法 | 无装饰器 / `@api.model` | 移除 `api.one`，改显式循环 |
| `fields.Date.from_string(x)` | `fields.Date.to_date(x)` | 字符串→对象工具改名 |
| `fields.Datetime.from_string(x)` | `fields.Datetime.to_datetime(x)` | 同上 |
| `date` 字段运行时值 = 字符串 | = `date` 对象 | 类型下沉 |
| `ir.actions.act_window.view` 记录 | 动作上 `view_ids` | 模型移除 |
| `do_notify(msg)` / `do_warning(msg)` | `raise UserError` / `message_post` | 方法移除 |
| `parent_left`/`parent_right` + `_parent_store` | `parent_path` | 左右值→路径 |
| `t-field-options` | `t-options` | QWeb 属性改名 |

**本版本对不涉及**的重大重命名（红线）：`account.invoice`→`account.move`（12→13）、
`payment.acquirer`→`payment.provider`（15→16）、`stock.production.lot`→`stock.lot`（15→16）、
`customer`/`supplier`→`customer_rank`/`supplier_rank`（12→13）。

---

## 11. 测试与校验

- 测试继承：`TransactionCase` / `SavepointCase` 在 11/12 均可用；`SavepointCase` 别名移除是 **15.0** 的事。
- `Environment.manage()` 仍需要（移除是 **15.0**）。
- `with_context(force_company=...)` 仍可用（改用 `with_company()` 是 **14.0**）。
- 校验：`odoo-bin -u <module> --test-tags /<module>`，开启 `--dev=all` 清除所有 `DeprecationWarning`。

---

## 12. `upgrade_code` codemod（11→12 无）  — CONFIRMED

`odoo-bin upgrade_code` 的 codemod 引擎**从 18.0 才存在**（17.0 及更早均无 `odoo/upgrade_code/` 模块）。
因此 **11→12 零 codemod**，全部为手工改动 + 数据库级 `migrations/12.0/` 脚本（由 OpenUpgrade 处理）。

> ⚠️ **勿让用户跑 `upgrade_code --from 11.0`**——该命令在 12.0 安装中根本不存在，会报命令未找到。

---

## 13. 迁移实战清单

1. **扫描（triage）**：用 `Odoo11to12Migration/scripts/scan_addon.py` 找出 `@api.one`、`from_string`、
   `ir.actions.act_window.view`、`do_notify`/`do_warning`、`t-field-options`、`parent_left`/`parent_right`。
2. **装饰器**：`@api.one` → 去装饰器 + 显式 `for record in self:`；覆写 `create` 加 `@api.model_create_multi`。
3. **日期类型**：`from_string/to_string` → `to_date/to_datetime`；删除对日期字段做字符串处理的旧逻辑。
4. **动作绑定**：删除 `ir.actions.act_window.view` 记录，改用动作 `view_ids`。
5. **父子结构**：`_parent_store` 模型去掉 `parent_left`/`parent_right`，加 `parent_path`。
6. **通知/警告**：`do_notify`/`do_warning` → `UserError` / `message_post`。
7. **QWeb**：`t-field-options` → `t-options`。
8. **校验**：`-u` + 测试 + 清 `DeprecationWarning`；数据库迁移由 OpenUpgrade 的 `migrations/12.0/` 承接（parent_path 填充等）。
9. **出报告**：列出每处改动、残留 `[verify]` 项、未覆盖的自定义 JS（如需）。

---

## 附录 A：研究来源与溯源

- **OCA《Migration to version 12.0》**（maintainer-tools wiki）——权威变更清单（api.one 移除、Date 类型、parent_path 等）。
- **掘金《Odoo版本升级:Odoo11~Odoo16代码变更》**——Date 运行时对象化、`model_create_multi`、`parent_path` 实战说明。
- **CSDN Odoo 代码规范**——`api.one`/`api.multi` 在 12 的弃用确认。
- **Oejia 技术栈**——`api.one` 移除、视图属性兼容性。
- **版本作用域红线**：对照 15→16 / 16→17 / 17→18 / 18→19 烹饪书，确认 account.move、customer_rank、tree→list、name_get 移除、get_resource_path、payment.provider 等**均不属于 11→12**。

> 标注 `[verify]` 的项（前端 Bootstrap/jQuery 版本归属、Binary 默认存附件时机）为单一社区来源或存在分歧，
> 建议在 12.0 实机上以 `grep` 源码最终确认后再固化到技能 references。
