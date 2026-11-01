# Odoo 迁移烹饪书：12.0 → 13.0

> 本烹饪书是 **12→13** 迁移的事实基准（Fact Baseline）。配套技能见 `Odoo12to13Migration/`。
> 它专为**自定义模块**（CE 与 EE）从 Odoo 12 升级到 13 编写，覆盖所有破坏性（breaking）变更，
> 并明确**版本作用域**——只收 12→13 区间内真实发生的变更，更晚版本的改动一律排除（见第 1 章红线）。
>
> **可信度标记**：`CONFIRMED` = OCA《Migration to version 13.0》官方迁移指南 + Odoo 13.0 源码/提交核对 +
> 社区源（shine-it / Odoo 中文社区 / Oodles / Cybrosys）交叉核实；
> `[verify]` = 单一社区来源或来源间有分歧、待 13.0 实机/源码最终确认。

---

## 目录

1. 导言与版本作用域
2. 头号断裂：会计重写 `account.invoice` → `account.move`
3. ORM / 模型装饰器清理与多记录语义
4. 伙伴与动作：`customer`/`supplier` → `customer_rank`/`supplier_rank`；`src_model`/`multi` → `binding_model`/`binding_view_types`
5. 字段与数据模型：`dp.get_precision`、`track_visibility`、`oldname`、`stock.quant`、`product.product`、`account.tax`、`Binary`
6. 视图 / QWeb / 前端
7. 多公司与环境：`with_company()`、`.env.company`、多公司规则形式
8. 安全与 `res.groups`（12→13 不变）
9. HTTP / 邮件 / 二进制（12→13 基本不变）
10. 模块 / 模型 / 字段映射
11. 测试与校验
12. `upgrade_code` codemod（12→13 无）
13. 迁移实战清单

---

## 1. 导言与版本作用域

Odoo 13.0（2019-10）是一次**"会计大合并 + 旧装饰器出清 + 动作/伙伴模型调整"**的版本。与 11→12（装饰器
与日期类型）、15→16（支付/模型重命名）、16→17（`attrs`/`states` 硬拒）、17→18（`tree`→`list`）相比，
12→13 的破坏面集中在**会计模型合并**（invoice 并入 move）、**剩余旧 API 装饰器移除**、以及
**动作绑定 / 伙伴字段**的重命名。

**本版本对的头号断裂**：`account.invoice` / `account.invoice.line` / `account.voucher` 等模型被合并进
`account.move` / `account.move.line`（社区称为 "accounting-pocalypse"）。

### 版本作用域红线（勿套用更晚版本的改动）

| 更晚版本的改动 | 归属版本 | 在 12→13 中 |
|---|---|---|
| `@api.one` 移除、`from_string` 移除、`parent_path` | 11→12 | ❌ 排除（12 已处理） |
| `ir.actions.*` 访问移除（sudo 化） | 13→14 | ❌ 排除（13 仍能直接读 `ir.actions.*`） |
| `attrs`/`states` 硬拒 | 16→17 | ❌ 排除（13 仍用 `attrs`/`states`） |
| `<tree>` → `<list>` | 17→18 | ❌ 排除（13 仍是 `tree`） |
| `name_get` 移除 / `_name_search` 返回 ids | 17→18 / 13→14 | ❌ 排除（`_name_search` 返回 ids 是 **13→14**） |
| `ir.model*` 访问移除 / `t-raw` 移除 / 资产进 manifest | 14→15 | ❌ 排除 |
| `payment.acquirer` → `payment.provider`、`coupon` → `loyalty` | 15→16 | ❌ 排除 |
| `track_visibility` → `tracking` | **12→13** | ✅ 本版本对（常见误归于 15→16，见第 5 章） |

> **Python 底座**：12.0 / 13.0 均要求 Python 3（无 py2→3 断裂，那属 10→11）。13.0 沿用 Python 3。

### 配套技能参考表（skill references）

本烹饪书的事实基准由 `Odoo12to13Migration/references/` 下的六份映射表承载，二者逐条对齐、零漂移：
`references/orm-api.md`（装饰器清除、`with_user`、多公司、`.env.company`）、
`references/accounting-models.md`（account.move 重写、`customer_rank`、`account.tax`）、
`references/views-qweb.md`（view_type 移除、`binding_view_types`、前端）、
`references/models-mapping.md`（dp.get_precision / track_visibility / oldname / stock.quant / product.product / Binary）、
`references/security.md`（安全不变）、
`references/upgrade-code.md`（无 codemod + migrations/13.0 工作流 + HTTP/邮件不变）。

---

## 2. 头号断裂：会计重写 `account.invoice` → `account.move`  — CONFIRMED

13.0 把 `account.invoice`、`account.invoice.line`、`account.invoice.tax`、`account.voucher`、
`account.voucher.line` 全部合并进 `account.move` / `account.move.line`。发票/账单/收据现在就是一笔
日记账分录（journal entry），通过 `move_type` 区分。

### 模型级映射

| 12.0 模型 | 13.0 模型 |
|---|---|
| `account.invoice` | `account.move`（`move_type` ∈ {out_invoice, in_invoice, out_refund, in_refund, out_receipt, in_receipt}） |
| `account.invoice.line` | `account.move.line` |
| `account.invoice.tax` | `account.move.line`（用 `tax_line_id` 标识税行） |
| `account.voucher` / `account.voucher.line` | `account.move` / `account.move.line`（`move_type` = `*_receipt`） |
| `account.invoice.confirm` (wizard) | `account.move.post()` |
| `account.invoice.refund` (wizard) | `account.move.reversal` |

### 关键字段映射（invoice → move）

| `account.invoice` 字段 | `account.move` 字段 |
|---|---|
| `number` | `name` |
| `reference` | `ref` |
| `comment` | `narration` |
| `user_id` | `invoice_user_id` |
| `amount_total_signed` | `amount_total_signed` |
| `residual` | `amount_residual` |
| `date_invoice` | `invoice_date` |
| `date_due` | `invoice_date_due` |
| `payment_term_id` | `invoice_payment_term_id` |
| `partner_bank_id` | `invoice_partner_bank_id` |
| `incoterm_id` | `invoice_incoterm_id` |
| `cash_rounding_id` | `invoice_cash_rounding_id` |

> 发票子集通过 `move_type` 或辅助方法 `is_invoice()` 访问；`account.move` 现在多了 `cancel` 状态，
> 业务逻辑需排除它。

### `account.move` / `account.move.line` 自身改名

- `account.move.amount` → `account.move.amount_total`
- `account.move.reverse_entry_id` → `account.move.reversed_entry_id`
- `account.move.line` 新增 `display_type`（`line_section` / `line_note` / `product` 等，**业务查询须排除**）
- 发票行子集：用布尔 `exclude_from_invoice_tab` 标识；税行子集：用 `tax_line_id` 关联字段标识

### 方法改名（迁移脚本常用）

- `account.move._run_post_draft_to_post()` → `_autopost_draft_entries()`
- `account.move.action_account_invoice_payment()` → `action_invoice_register_payment()`
- `account.bank.statement` 上下文键 `edition_mode` → `suspense_moves_mode`

### Before（12.0）

```python
invoice = self.env['account.invoice'].create({
    'partner_id': partner.id,
    'type': 'out_invoice',
    'invoice_line_ids': [(0, 0, {'product_id': p.id, 'price_unit': 10})],
})
invoice.action_invoice_open()
```

### After（13.0）

```python
move = self.env['account.move'].create({
    'partner_id': partner.id,
    'move_type': 'out_invoice',           # 替代旧 type
    'invoice_line_ids': [(0, 0, {         # invoice_line_ids 仍是 o2m，指向 account.move.line
        'product_id': p.id,
        'price_unit': 10,
        'exclude_from_invoice_tab': False,
    })],
})
move.post()                               # 替代 action_invoice_open()
```

**扫描模式**：`account\.invoice`、`account\.invoice\.line`、`account\.voucher`、`action_invoice_open`、
`action_invoice_cancel`、`account_invoice_report`（报告模型大多被 `account.move.line` 报表取代）。

---

## 3. ORM / 模型装饰器清理与多记录语义  — CONFIRMED

13.0 彻底清退了新 API 早期遗留的装饰器（11→12 已移除 `@api.one`，13.0 移除其余）：

### 3.1 移除 `@api.multi` / `@api.returns` / `@api.cr` / `@api.model_cr`

```python
# Before（12.0，仍可用但 13.0 移除）
@api.multi
def do_something(self):
    for rec in self:
        rec.state = 'done'

@api.model_cr
def init(self):
    ...

# After（13.0）
def do_something(self):              # 无装饰器即"多记录"语义（旧 api.multi 行为）
    for rec in self:
        rec.state = 'done'

def init(self):                      # 数据库初始化方法去掉 @api.model_cr
    ...
```

- 所有方法默认多记录，无需 `@api.multi`。`@api.returns` 也移除（ORM 现在统一返回记录集）。
- 扫描 id：`api-decorators`（正则 `@api\.(multi|returns|cr|model_cr)`）。

### 3.2 非存储 computed 字段必须赋值

13.0 要求**非存储 computed 字段**无论如何都要赋值（哪怕是 falsy 值）；存储 computed 字段若不在
compute 中赋值，会保留旧值（不再有隐式默认）。推荐在 compute 开头 `self.x = ...` 预赋值。

### 3.3 `sudo(user)` → `with_user(user)`

```python
# Before（12.0）
record.sudo(user)
# After（13.0）
record.with_user(user)               # 无参 sudo() 仍保留
```

- 扫描 id：`sudo-user`（正则 `sudo\([^)\s]` 即带参调用）。

### 3.4 多公司记录规则新形式

13.0 多公司规则必须写成通用形式，并在 `noupdate="1"` 记录上补迁移脚本：

```python
[('company_id', '=', False), ('company_id', 'in', company_ids)]   # 旧
['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]  # 13.0 新
```

### 3.5 其它 ORM

- `.env.user.company_id` → `.env.company`（取"当前激活公司"）。
  - 扫描 id：`env-user-company`（正则 `\.user\.company_id`）。
- 继承 `hr.employee` 的自定义模块改为继承 `hr.employee.base`（见 odoo/odoo commit c9ca376）。
- `with_company()` 在 13.0 可用（多公司上下文切换），`depends_context('company')` 用于 computed 字段。
  > 注：旧文档有把 `with_company()` 误归为 14.0 的说法；其**引入**在 13.0，14.0 才进一步弃用
  > `force_company`（见 13→14 烹饪书）。

---

## 4. 伙伴与动作：`customer`/`supplier` → `customer_rank`/`supplier_rank`；`src_model`/`multi` → `binding_model`/`binding_view_types`  — CONFIRMED

### 4.1 `res.partner`：`customer` / `supplier` 布尔 → `customer_rank` / `supplier_rank` 整数

```python
# Before（12.0）
partner.customer = True
partner.supplier = True
domain = [('customer', '=', True)]

# After（13.0）
partner.customer_rank = 1     # 整数：可累计（多个渠道各 +1）
partner.supplier_rank = 1
domain = [('customer_rank', '>', 0)]
```

- 布尔 → 整数 rank，支持"客户/供应商"按来源累计，不再是非此即彼。
- 扫描 id：`partner-rank`（正则 `\.customer\b|\.supplier\b` 配合 res.partner 上下文，建议人工复核）。

### 4.2 `ir.actions.act_window`：移除 `multi` 字段 → `binding_view_types`

```xml
<!-- Before（12.0）-->
<record id="action_x" model="ir.actions.act_window">
    <field name="res_model">my.model</field>
    <field name="multi">True</field>          <!-- 指示在哪些视图上出现 -->
</record>

<!-- After（13.0）-->
<record id="action_x" model="ir.actions.act_window">
    <field name="res_model">my.model</field>
    <field name="binding_view_types">form</field>   <!-- list / form / 空(两者) -->
</record>

<!-- 快捷标签写法：binding_views="form" -->
<act_window id="action_x" res_model="my.model" binding_views="form"/>
```

- 扫描 id：`act-window-multi`（正则 `<field name="multi">`）、`binding-view-types`。

### 4.3 `ir.actions.*`：`src_model` → `binding_model_id`（13.0 仍保留 `src_model` 兼容，但 13→14 起访问受限）

12→13 阶段 `src_model` 字段尚可直接使用；但为面向 13→14 做准备，新写动作建议用 `binding_model_id`。
完整移除 `src_model` 访问在 13→14（见该版本对烹饪书）。

---

## 5. 字段与数据模型  — CONFIRMED（除标注外）

### 5.1 `dp.get_precision` 去除 → 直接用 `digits`

```python
# Before（12.0）
import odoo.addons.decimal_precision as dp
x = fields.Float(digits=dp.get_precision("Product Price"))

# After（13.0）
x = fields.Float(digits="Product Price")     # 直接用字符串精度键
```

- 13.0 不再需要 import `decimal_precision`；`digits` 接受精度类别字符串。
- 扫描 id：`dp-get-precision`（正则 `dp\.get_precision`）。

### 5.2 `track_visibility` → `tracking`

```python
# Before（12.0）
name = fields.Char(track_visibility="onchange")
# After（13.0）
name = fields.Char(tracking=True)            # 或用 tracking=10 指定优先级
```

> **版本归属澄清**：`track_visibility` → `tracking` **首现于 13.0**（OCA 13.0 官方指南明确）。
> 部分旧资料误将其归入 15→16；本工作台以 13.0 为准，15→16 不再重复。

- 扫描 id：`track_visibility`（正则 `track_visibility=`）。

### 5.3 `oldname` 字段属性移除

```python
# Before（12.0）：字段改名后留 oldname 过渡
amount = fields.Monetary(oldname="price_amount")
# After（13.0）：oldname 不再支持 —— 用 openupgradelib 的 rename_fields 写迁移脚本
amount = fields.Monetary()
```

- 扫描 id：`oldname`（正则 `\boldname\s*=`）。

### 5.4 `stock.quant`：`qty` → `quantity`  — CONFIRMED

```python
# Before（12.0）
quant.qty
# After（13.0）
quant.quantity
```

### 5.5 `product.product`：`name` 变为 related 字段  — CONFIRMED（源码核对）

13.0 起 `product.product.name` 是 `product.template.name` 的 related 字段（store=True）。
**不能再直接给变体写 `product.name`**，应改 `product_template_id.name`：

```python
# Before（12.0）：可给变体单独写 name
variant.write({'name': '红色款'})
# After（13.0）：变体 name 跟随模板，写模板
variant.product_template_id.write({'name': '红色款'})
```

### 5.6 `account.tax`：`type` → `type_tax_use`  — CONFIRMED

```python
# Before（12.0）：type 取值 sale/purchase
tax.type
# After（13.0）：type_tax_use 取值 sale/purchase/none
tax.type_tax_use
```

### 5.7 `Binary` 字段默认存附件  — CONFIRMED

13.0 起 `Binary` 字段默认 `attachment=True`（存到 `ir.attachment`，不再直接进数据库列）。
自定义模块若依赖旧"入库列"行为需显式 `attachment=False`。

> 注：11→12 的旧 `[verify]`（Binary 默认改附件时机）在 13.0 得到确认——归属 **12→13**，非 11→12。

---

## 6. 视图 / QWeb / 前端

### 6.1 动作窗口 XML 移除 `view_type`  — CONFIRMED

```xml
<!-- Before（12.0）：view_type 冗余（自 11.0 起 tree 已不支持）-->
<record id="action_x" model="ir.actions.act_window">
    <field name="view_type">form</field>
</record>
<!-- After（13.0）：直接删除 view_type（始终 form）-->
```

- 扫描 id：`view-type`（正则 `view_type`）。

### 6.2 前端依赖（中等断裂）  — [verify]

13.0 前端框架小幅升级：

- **jQuery 3.x / Bootstrap 4.x / FontAwesome 5.x** 就位；FA 图标改名（如 `area-chart` → `chart-area`、
  `address-book-o` → `address-book`），自定义模板/SCSS 需复核。
- **JavaScript：jQuery Promise (`$.Deferred`) → 原生 `Promise`**（OCA 13.0 明确要求）。
- 更大的前端跃进（Owl 框架、QWeb `t-raw` 移除）在 **14→15**，不在 12→13。

### 6.3 视图机制

`attrs`、`states`、`tree`、`form`、`kanban` 在 12→13 **完全保留**（它们的收紧/重命名分别在
13→14 与 16→17 / 17→18）。12→13 的 XML 视图几乎只需处理动作绑定与 `view_type`。

---

## 7. 多公司与环境

- `with_company()`：13.0 引入，切换多公司上下文（替代旧的 `with_context(force_company=...)` 部分用法，
  但 `force_company` 在 13.0 仍可用，14.0 才弃用）。
- `.env.user.company_id` → `.env.company`（见第 3.5 章）。
- `depends_context('company')`：computed 字段声明依赖 company 上下文。
- 多公司记录规则新形式见第 3.4 章。

---

## 8. 安全与 `res.groups`（12→13 不变）  — CONFIRMED

- `ir.model.access.csv`、`ir.rule`、`res.groups` 的写法在 12→13 **不变**。
- `groups` 字段、`implied_ids` 继承链、`category_id` 机制一致。
- 安全文件（CSV/XML）**无需改动**。

> **红线**：勿套用 18→19 的 `res.groups` privilege 模型或 19→20 的 `ir.access.csv` 改动——远晚于 13.0。

---

## 9. HTTP / 邮件 / 二进制（12→13 基本不变）  — CONFIRMED

- `http.route`、`request.env`、`http.Controller` 在 12/13 一致；`type='json'` 仍是 `json`
  （重命名为 `jsonrpc` 是 **18.1**）。
- 邮件 `mail.template`：`body_html` 仍用 **Jinja** 语法（Jinja→QWeb 重写是 **14→15**）。
  `subtype` → `subtype_xmlid` 改名也是 **14→15**，不在 12→13。
- `message_post(body=..., message_type=...)` 行为一致。
- `get_resource_path` 在 12/13 仍使用（`file_path` 是 **16→17** 的改名）。

---

## 10. 模块 / 模型 / 字段映射

| 12.0 | 13.0 | 类别 | 可信度 |
|---|---|---|---|
| `account.invoice` / `.line` / `.tax` | `account.move` / `account.move.line` | 模型合并 | CONFIRMED |
| `account.voucher` / `.line` | `account.move` / `account.move.line` | 模型合并 | CONFIRMED |
| `account.invoice.action_invoice_open` | `account.move.post()` | 方法 | CONFIRMED |
| `account.move.amount` | `account.move.amount_total` | 字段改名 | CONFIRMED |
| `res.partner.customer` / `.supplier` | `customer_rank` / `supplier_rank` | 字段重类型 | CONFIRMED |
| `ir.actions.act_window.multi` | `binding_view_types` | 字段改名 | CONFIRMED |
| `ir.actions.*.src_model` | `binding_model_id` | 字段改名 | CONFIRMED（13.0 仍兼容，13→14 收紧） |
| `@api.multi` / `.returns` / `.cr` / `.model_cr` | 移除（默认多记录） | 装饰器 | CONFIRMED |
| `sudo(user)` | `with_user(user)` | 方法改名 | CONFIRMED |
| `dp.get_precision("X")` | `digits="X"` | 工具函数 | CONFIRMED |
| `track_visibility="onchange"` | `tracking=True` | 字段属性 | CONFIRMED |
| `oldname="x"` | 移除（rename_fields 迁移） | 字段属性 | CONFIRMED |
| `stock.quant.qty` | `stock.quant.quantity` | 字段改名 | CONFIRMED |
| `product.product.name`（可写） | related（写模板） | 字段语义 | CONFIRMED |
| `account.tax.type` | `account.tax.type_tax_use` | 字段改名 | CONFIRMED |
| `Binary` 默认 `attachment=True` | 存附件（默认） | 字段存储 | CONFIRMED |
| `.env.user.company_id` | `.env.company` | 环境属性 | CONFIRMED |
| 视图 `view_type` 属性 | 移除（始终 form） | XML 属性 | CONFIRMED |
| 多公司规则 `company_id='='False'` 组合 | 前置 `'\|'` 形式 | 规则 | CONFIRMED |
| 前端 FA 图标 `area-chart` | `chart-area` | 前端资源 | [verify] |

**本版本对不涉及**的重大重命名（红线）：`payment.acquirer`→`payment.provider`（15→16）、
`coupon`→`loyalty`（15→16）、`stock.production.lot`→`stock.lot`（15→16）、
`ir.model*` 访问移除（14→15）、`t-raw` 移除（14→15）、`attrs`/`states` 硬拒（16→17）。

---

## 11. 测试与校验

- `TransactionCase` / `SavepointCase` 在 12/13 均可用（`SavepointCase` 别名**移除是 15.0**，13.0 无影响）。
- `Environment.manage()` 仍需要（移除是 **15.0**）。
- 导入：Python 依赖在 `__manifest__.py` 用 **PyPI 发行名**而非 import 名（odoo/odoo PR #25549）。
- 校验：`odoo-bin -u <module> --test-tags /<module>`，开启 `--dev=all` 清除所有 `DeprecationWarning`
  （重点是 `@api.multi` 残留、computed 字段未赋值警告）。
- CLI：13.0 新增 `--upgrade-path` 参数（OpenUpgrade 多版本路径迁移）。

---

## 12. `upgrade_code` codemod（12→13 无）  — CONFIRMED

`odoo-bin upgrade_code` 的 codemod 引擎**从 18.0 才存在**（17.0 及更早均无 `odoo/upgrade_code/` 模块）。
因此 **12→13 零 codemod**，全部为手工改动 + 数据库级 `migrations/13.0/` 脚本（由 OpenUpgrade 处理）。

> ⚠️ **勿让用户跑 `upgrade_code --from 12.0`**——13.0 安装中该命令不存在，会报命令未找到。

---

## 13. 迁移实战清单

1. **扫描（triage）**：用 `Odoo12to13Migration/scripts/scan_addon.py` 找出 `@api.multi`/`@api.returns`/
   `@api.cr`/`@api.model_cr`、`dp.get_precision`、`track_visibility`、`oldname`、`account.invoice`、
   `src_model`、动作 `multi`、`view_type`、`sudo(user)`、`.user.company_id`。
2. **会计重写**：`account.invoice` → `account.move`（含 `move_type`）；`action_invoice_open` → `post()`；
   报表改查 `account.move.line`；字段改名（`amount`→`amount_total` 等）。
3. **装饰器**：删 `@api.multi`/`@api.returns`/`@api.cr`/`@api.model_cr`；补非存储 computed 字段赋值。
4. **伙伴/动作**：`customer`/`supplier` → `customer_rank`/`supplier_rank`；`multi` → `binding_view_types`；
   `src_model` → `binding_model_id`。
5. **字段**：`dp.get_precision`→`digits`、`track_visibility`→`tracking`、`oldname` 移除（写 rename 迁移）；
   `stock.quant.qty`→`quantity`、`account.tax.type`→`type_tax_use`、`product.product.name` 改写模板。
6. **环境**：`sudo(user)`→`with_user`、`.user.company_id`→`.env.company`、多公司规则加 `'|'` 前缀。
7. **视图**：删 `view_type`；前端 FA 图标改名、jQuery Promise→原生 Promise（按需）。
8. **DB 迁移**：模块 `migrations/13.0/` 写 `account.move` 数据搬移、`oldname` 重命名字段、Binary 附件落库等脚本。
9. **校验**：`-u` + 测试 + 清 `DeprecationWarning`；数据库迁移由 OpenUpgrade 的 `migrations/13.0/` 承接。
10. **出报告**：列出每处改动、残留 `[verify]` 项、未覆盖的自定义前端资源。

---

## 附录 A：研究来源与溯源

- **OCA《Migration to version 13.0》**（maintainer-tools wiki）——权威变更清单（装饰器清除、`track_visibility`→
  `tracking`、`oldname` 移除、`dp.get_precision`→`digits`、`multi`→`binding_view_types`、多公司规则形式、
  `sudo(user)`→`with_user`、`.env.user.company_id`→`.env.company`、hr.employee.base、jQuery→Promise）。
- **Odoo 社区"accounting-pocalypse"提交说明**（shuzhiduo / Odoo 论坛）——account.invoice 合并进 account.move 的
  完整字段与方法映射。
- **shine-it《如何升级到odoo13》**——12→13 开发对比（Binary 默认存附件、dp.get_precision 去除、view_type 移除、
  binding_view_types、前端 FA/jQuery 版本、--upgrade-path）。
- **Oodles《Migration in Odoo 13》**——装饰器清理、oldname 移除、FA 图标改名、multi→binding_view_types。
- **版本作用域红线**：对照 11→12 / 15→16 / 16→17 / 17→18 烹饪书，确认 account.move、customer_rank、tree→list、
  name_get 移除、`ir.model*` 移除、payment.provider 等**均不属于 12→13 首发**（`track_visibility`→`tracking` 常被
  误归 15→16，本工作台以 13.0 官方指南校正）。

> 标注 `[verify]` 的项（前端 FA 图标、jQuery 版本归属细节）为单一社区来源或存在分歧，建议在 13.0 实机上以
> `grep` 源码最终确认后再固化到技能 references。
