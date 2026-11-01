# Odoo 迁移烹饪书：14.0 → 15.0

> 本烹饪书是 **14→15** 迁移的事实基准（Fact Baseline）。配套技能见 `Odoo14to15Migration/`。
> 它专为**自定义模块**（CE 与 EE）从 Odoo 14 升级到 15 编写，覆盖所有破坏性（breaking）变更，
> 并明确**版本作用域**——只收 14→15 区间内真实发生的变更，更晚版本的改动一律排除（见第 1 章红线）。
>
> **可信度标记**：`CONFIRMED` = OCA《Migration to version 15.0》官方迁移指南 + Odoo 15.0 源码/提交核对
> （odoo/odoo#69120、#77074、#62031、01875541b1a8 等）+ 多社区源（Odoo 论坛 / Cybrosys / apps.odoo）交叉核实；
> `[verify]` = 单一社区来源或来源间有分歧、待 15.0 实机/源码最终确认。

---

## 目录

1. 导言与版本作用域
2. 头号断裂：QWeb `t-raw` → `t-out` / `t-esc`
3. `ir.model*` 对象访问移除（sudo 化）
4. 邮件模板：Jinja 语法 → QWeb（正文）+ inline_template（subject 等）
5. 前端 / 资产：ES 模块 `.esm.js`、资产声明进 `__manifest__.py`
6. 测试：`SavepointCase` → `TransactionCase`、`Environment.manage()` 不再需要
7. 安全与 `res.groups`（14→15 不变）
8. HTTP / 邮件 / 二进制（其它不变）
9. 模块 / 模型 / 字段映射
10. 测试与校验
11. `upgrade_code` codemod（14→15 无）
12. 迁移实战清单

---

## 1. 导言与版本作用域

Odoo 15.0（2021-10）是一次**"QWeb 净化 + 模型元数访问收紧 + 资产声明入 manifest + 邮件模板 QWeb 化"**
的版本。与 12→13（会计重写）、13→14（`ir.actions.*` 访问 / `attrs` 约束）、16→17（`attrs`/`states` 硬拒）、
17→18（`tree`→`list`）相比，14→15 的破坏面集中在**前端模板语法与资产机制**、**`ir.model*` 读取受限**、
以及**测试基类清理**。

**本版本对的头号断裂**：QWeb 模板的 `t-raw` 指令被移除（改用 `t-out` / `t-esc`）；同时 `ir.model*` 对象的
直接访问被移除（必须 sudo 或通过既有方法）。

### 版本作用域红线（勿套用更晚版本的改动）

| 更晚版本的改动 | 归属版本 | 在 14→15 中 |
|---|---|---|
| `ir.actions.*` 访问移除 | 13→14 | ❌ 排除（14 已处理） |
| `invisible`/`readonly` 动态表达式→`attrs` | 13→14 | ❌ 排除 |
| `_name_search` 返回 ids | 13→14 | ❌ 排除 |
| `attrs`/`states` **硬拒**（改内联表达式） | 16→17 | ❌ 排除 |
| `<tree>` → `<list>` | 17→18 | ❌ 排除 |
| `name_get` **移除** | 17→18 | ❌ 排除 |
| `get_resource_path`→`file_path` | 16→17 | ❌ 排除（14 仍用 get_resource_path） |
| `payment.acquirer`→`payment.provider`、`coupon`→`loyalty` | 15→16 | ❌ 排除 |
| `track_visibility`→`tracking` | **12→13** | ❌ 排除（常被误归 14→15） |
| Python 3.10 底座抬升 | 16→17 | ❌ 排除（15.0 仍兼容 3.8+） |

> **Python 底座**：14.0 / 15.0 均要求 Python 3（15.0 支持 3.8–3.10；3.10 抬升严格化是 **16→17**）。

### 配套技能参考表（skill references）

本烹饪书的事实基准由 `Odoo14to15Migration/references/` 下的六份映射表承载，二者逐条对齐、零漂移：
`references/views-qweb.md`（t-raw→t-out/t-esc、ir.model* 访问移除、esm.js、资产 manifest）、
`references/orm-api.md`（SavepointCase→TransactionCase、Environment.manage 移除、ir.model* 访问）、
`references/http-rpc-mail.md`（Jinja→QWeb 邮件模板、subtype→subtype_xmlid、其它不变）、
`references/models-mapping.md`（资产 key、`qweb` key 移除、t-out/t-esc 对照），
`references/security.md`（res.groups 不变）、
`references/upgrade-code.md`（无 codemod + migrations/15.0 工作流）。

---

## 2. 头号断裂：QWeb `t-raw` → `t-out` / `t-esc`  — CONFIRMED

15.0 移除了 QWeb 的 `t-raw` 指令（它原样输出不被转义的内容）。现在统一用 `t-out`（不转义）或
`t-esc`（HTML 转义），并可在服务端用 `markupsafe.Markup` 标记可信任的 HTML。

### Before（14.0）

```xml
<div t-raw="0"/>                       <!-- 原样输出 -->
<span t-raw="record.body_html"/>       <!-- 不受转义 -->
```

### After（15.0）

```xml
<div t-out="0"/>                        <!-- 不转义等价于原 t-raw -->
<span t-out="record.body_html"/>        <!-- 不受转义 -->
<span t-esc="record.name"/>             <!-- HTML 转义（替代 t-raw 的安全场景） -->
```

- 服务端：把信任的 HTML 包成 `markupsafe.Markup(html)`，QWeb 用 `t-out` 时不会再双重转义。
- `t-esc` 是大多数场景的安全默认（替代"原本想用 t-raw 但担心转义"的需求）。
- 扫描 id：`t-raw`（正则 `t-raw`）。

---

## 3. `ir.model*` 对象访问移除（sudo 化）  — CONFIRMED

15.0 移除了对 **`ir.model` / `ir.model.fields` / `ir.model.data` / `ir.model.fields.selection`** 等
模型元数据对象的直接访问。自定义代码若直接读这些模型会失败。

### 修复方式

- **需要模型字段信息**：用既有 API（如 `self.env['res.partner']._fields`、模型的 `_fields` 属性、
  `_inherits` 等），或 `sudo()` 后访问。
- **读取 `ir.model.data` 的 xml-id**：用 `self.env['ir.model.data']._xmlid_lookup()` /
  `_get_id()` 等既有方法，而非直接 search。
- 源码依据：odoo/odoo#69120。

### Before（14.0）

```python
fields_info = self.env['ir.model.fields'].search([('model','=','res.partner')])
```

### After（15.0）

```python
fields_info = self.env['ir.model.fields'].sudo().search([('model','=','res.partner')])
# 或优先用模型自身 API：self.env['res.partner']._fields
```

> 注意：这与 **13→14 的 `ir.actions.*` 访问移除** 是**不同对象**——14.0 限制 `ir.actions.*`，
> 15.0 限制 `ir.model*`。两者都要处理，但归属不同版本对。

---

## 4. 邮件模板：Jinja 语法 → QWeb（正文）+ inline_template（subject 等）  — CONFIRMED

15.0 把 `mail.template` 的渲染从 **Jinja** 改为两种新语言：

- **正文 `body_html`**：用 **QWeb**（与视图一致，支持 `t-` 指令）。
- **subject / email_from / email_to 等字段**：用 **inline_template**——类似 Jinja，但表达式包在
  `{{ }}` 中（而非旧的 `${ }`），且仅用于单行字段。

### Before（14.0，Jinja）

```xml
<record id="email_tpl" model="mail.template">
    <field name="subject">Invoice ${object.name}</field>
    <field name="body_html"><![CDATA[<p>Hello ${object.partner_id.name}</p>]]></field>
</record>
```

### After（15.0，QWeb + inline_template）

```xml
<record id="email_tpl" model="mail.template">
    <field name="subject">Invoice {{ object.name }}</field>     <!-- inline_template：{{ }} -->
    <field name="body_html" type="qweb"><![CDATA[
        <p>Hello <t t-out="object.partner_id.name"/></p>          <!-- QWeb 正文 -->
    ]]></field>
</record>
```

**要点**：

- 模板 XML 里正文加 `type="qweb"`（或直接在 QWeb 模板中渲染）。
- `${ ... }` 旧语法在 15.0 不再工作 → 正文用 `t-out`/`t-esc`，单行字段用 `{{ }}`。
- 源码依据：odoo/odoo#77074。
- 扫描 id：`jinja-dollar`（正则 `\$\{` 捕捉旧 Jinja）、`mail-qweb`（正文 `type="qweb"` 化）。

---

## 5. 前端 / 资产：ES 模块 `.esm.js`、资产声明进 `__manifest__.py`  — CONFIRMED

### 5.1 ES 模块需改名 `.esm.js`

以 `/** @odoo-module **/` 开头的 JS 文件（ES module）必须改名，使文件名以 **`.esm.js`** 结尾
（同时更新资产引用），以便 ESLint 兼容。

```text
static/src/js/foo.js      ->  static/src/js/foo.esm.js
```

- 扫描 id：`odoo-module-esm`（正则 `@odoo-module` 在 `.js` 文件，且文件名非 `.esm.js`）。

### 5.2 资产声明移入 manifest

15.0 起，JS / SCSS 链接从 XML 模板移入 `__manifest__.py` 的 **`assets`** 键；**不再有 `qweb` 键**
（所有 QWeb `.xml` 链接进 `web.assets_qweb`）。路径相对于仓库根目录（非模块目录）。

```python
# __manifest__.py（15.0）
{
    'assets': {
        'web.assets_backend': ['my_module/static/src/js/foo.esm.js',
                               'my_module/static/src/scss/foo.scss'],
        'web.assets_qweb': ['my_module/static/src/xml/**/*'],
    },
}
```

- 旧 `<template>` 中 `<link>`/`<script>` 资产节点删除；`qweb` 键删除。
- 可用 glob（`**/*`）避免逐个声明。
- 扫描 id：`qweb-key`（正则 `'qweb'` 在 `__manifest__.py`）。

---

## 6. 测试：`SavepointCase` → `TransactionCase`、`Environment.manage()` 不再需要  — CONFIRMED

### 6.1 `SavepointCase` 别名移除

15.0 移除 `SavepointCase` 别名（它与 `TransactionCase` 已是同一行为）。直接改用 `TransactionCase`。

```python
# Before（14.0）：SavepointCase（别名，15.0 移除）
class MyTest(SavepointCase): ...
# After（15.0）
class MyTest(TransactionCase): ...
```

- 扫描 id：`savepoint-case`（正则 `SavepointCase`）。源码：odoo/odoo#62031。

### 6.2 `Environment.manage()` 不再需要

```python
# Before（14.0）
with Environment.manage():
    env = Environment(...)
# After（15.0）：直接创建 Environment，无需 manage()
env = Environment(...)
```

- 扫描 id：`env-manage`（正则 `Environment\.manage`）。
- 注：`Environment.manage()` 在 15.0 之前已逐步弃用，15.0 正式移除。
  （11→12 烹饪书已注明其移除属 15.0，与此一致。）

---

## 7. 安全与 `res.groups`（14→15 不变）  — CONFIRMED

- `ir.model.access.csv`、`ir.rule`、`res.groups` 的写法在 14→15 **不变**。
- 注意：**15.0 访问 `ir.model*` 受限**（见第 3 章），但这不影响 `ir.model.access` 的正常写法。
- 安全文件（CSV/XML）**无需改动**。

> **红线**：勿套用 18→19 的 `res.groups` privilege 模型或 19→20 的 `ir.access.csv` 改动——远晚于 15.0。

---

## 8. HTTP / 邮件 / 二进制（其它不变）  — CONFIRMED

- `http.route`、`request.env`、`http.Controller` 在 14/15 一致；`type='json'` 仍是 `json`
  （重命名为 `jsonrpc` 是 **18.1**）。
- 邮件 `message_post(body=..., message_type=...)` 行为一致；`subtype` → `subtype_xmlid` 改名见下。
- `get_resource_path` 在 14/15 仍使用（`file_path` 是 **16→17** 改名）。
- `Binary` 字段默认存储行为 14/15 一致（默认存 `ir.attachment` 自 **13.0** 起）。

### 8.1 `subtype` → `subtype_xmlid`（[verify]，常见 14→15 归属）

15.0 邮件 `message_post` / `mail.template` 的 `subtype` 字段改为 `subtype_xmlid`（引用 xml-id 而非
subtype 对象/字符串）。OCA 15.0 核心指南未逐条列，但社区迁移资料普遍将其归入 14→15；建议以 15.0
源码核对。

- 扫描 id：`subtype-xmlid`（正则 `subtype=` 在邮件上下文）。

---

## 9. 模块 / 模型 / 字段映射

| 14.0 | 15.0 | 类别 | 可信度 |
|---|---|---|---|
| QWeb `t-raw` | `t-out` / `t-esc`（+ `Markup`） | 模板指令 | CONFIRMED |
| 直接访问 `ir.model*` 记录 | `sudo()` / 既有模型 API | 访问方式 | CONFIRMED |
| 邮件模板 Jinja（`${ }` / body_html） | QWeb 正文 + inline_template（`{{ }}`） | 邮件渲染 | CONFIRMED |
| ES module `foo.js`（`@odoo-module`） | `foo.esm.js` | 前端文件 | CONFIRMED |
| 资产在 XML `<template>` / `qweb` 键 | `__manifest__.py` `assets` 键 | 资产机制 | CONFIRMED |
| `SavepointCase` | `TransactionCase` | 测试基类 | CONFIRMED |
| `with Environment.manage():` | 直接 `Environment(...)` | 测试/环境 | CONFIRMED |
| `mail.template` `subtype=` | `subtype_xmlid=` | 邮件字段 | [verify] |

**本版本对不涉及**的重大重命名（红线）：`payment.acquirer`→`payment.provider`（15→16）、
`coupon`→`loyalty`（15→16）、`stock.production.lot`→`stock.lot`（15→16）、
`ir_translation`→JSONB（15→16，本工作台将其归入 15→16 烹饪书）、
`attrs`/`states` 硬拒（16→17）、`tree`→`list`（17→18）、`name_get` 移除（17→18）、
`track_visibility`→`tracking`（12→13）。

### 9.1 核心领域模型变更（本版本对必查）— CONFIRMED

上表是框架级改名。14→15 另有 3 条核心业务模型变更，均由 14.0 / 15.0 源码模型集 diff 核实，与 `Core_Models_Changelog.md` 同源。它们不属于"框架改名"，容易被框架清单漏掉，但影响面集中在中大型客户的库存与项目流程。

#### 9.1.1 盘点模型换代（库存头号断裂）

`stock.inventory` 与 `stock.inventory.line` 在 15.0 **整体移除**。盘点不再是一张独立单据，改为在 `stock.quant` 上直接录入 `inventory_quantity`，并新增 `stock.inventory.adjustment.name` 给这批调整命名。

| 14.0 | 15.0 | 说明 |
|---|---|---|
| `stock.inventory`（盘点单） | 移除 | 盘点改 `stock.quant` 的盘点模式 |
| `stock.inventory.line` | 移除 | 明细即 quant 行的 `inventory_quantity` |
| — | `stock.quant.inventory_quantity` | 已有字段，15.0 起成为盘点主入口 |
| — | `stock.inventory.adjustment.name` | 新增，给一次盘点批次命名 |

**影响面**：所有依赖"盘点单"的业务都断——自定义盘点报表、按 `inventory_id` 聚合的统计、盘点审批流、以及任何 `env['stock.inventory']` 的代码。

**迁移动作**：

1. 代码层：`env['stock.inventory']` 全部改为 `env['stock.quant']` + `action_apply_inventory()`；
2. 数据层：历史盘点单数据在 15.0 无载体，升级前导出归档（OpenUpgrade 会把在途盘点转录为 quant 调整，但不保留单据号语义）；
3. 自定义盘点报表改用 `stock.quant` 的 `inventory_quantity_set` + `stock.inventory.adjustment.name` 组合；
4. 盘点审批流（若有）需在新模型上重建，因为没有"单据状态"可挂。

> 这条常被误判成"只是换了个表"。实际是**作业范式变化**：从"开单—录数—审核—过账"变成"直接改 quant—批量应用"。相关培训与 SOP 也要改。

#### 9.1.2 产品类型细分字段新增

15.0 新增 `product.template.detailed_type`（`consu`/`product`/`service`），与既有的 `type` 并存，用来区分"可库存产品"与"消耗品"。

**注意**：这是**新增**，不是改名——`type` 在 15.0 仍然存在且是主字段。该字段随后在 **18.0 被移除**，所以从 14 一路升到 20 的话，会先加后删，不要在中间版本把逻辑永久绑到 `detailed_type` 上。

**迁移动作**：15.0 起若需要"可库存"判断，用 `detailed_type == 'product'`；但若目标版本 ≥18.0，直接写 `is_storable`，省一次返工。

#### 9.1.3 项目里程碑与项目更新模型新增

`project.milestone`、`project.update` 在 15.0 新增。项目域从"只有任务"扩展到"任务 + 里程碑 + 状态汇报"。

**迁移动作**：自定义项目看板若自建了里程碑表，评估迁移到 `project.milestone`；`project.update` 提供周期性状态汇报，可替代自建的周报模型。

### 9.2 本章与其他文档的关系

| 需求 | 去处 |
|---|---|
| 某业务模块的逐字段改名 | OpenUpgrade `upgrade_analysis.txt` |
| 跨版本模型演变全局索引 | `Core_Models_Changelog.md` |
| 本对框架级改名 | 本章主表 |

---

## 10. 测试与校验

- 测试继承：`TransactionCase` 在 14/15 均可用（`SavepointCase` 别名**移除是 15.0**）。
- `Environment.manage()` 移除（15.0）。
- 校验：`odoo-bin -u <module> --test-tags /<module>`，开启 `--dev=all` 清除 `DeprecationWarning`
  （重点是 `t-raw`、`SavepointCase`、`Environment.manage` 警告）。
- 前端：`odoo-bin -u <module> --dev=all` 校验 QWeb（`t-raw` 会报错）与资产加载。

---

## 11. `upgrade_code` codemod（14→15 无）  — CONFIRMED

`odoo-bin upgrade_code` 的 codemod 引擎**从 18.0 才存在**（17.0 及更早均无 `odoo/upgrade_code/` 模块）。
因此 **14→15 零 codemod**，全部为手工改动 + 数据库级 `migrations/15.0/` 脚本（由 OpenUpgrade 处理）。

> ⚠️ **勿让用户跑 `upgrade_code --from 14.0`**——15.0 安装中该命令不存在，会报命令未找到。

---

## 12. 迁移实战清单

1. **扫描（triage）**：用 `Odoo14to15Migration/scripts/scan_addon.py` 找出 `t-raw`、`ir.model*`
   直接访问、`${ }` Jinja、`@odoo-module` 的 `.js`、`SavepointCase`、`Environment.manage`、
   manifest `qweb` 键、`subtype=`。
2. **QWeb**：`t-raw` → `t-out`（不转义）/ `t-esc`（转义）；服务端信任 HTML 用 `markupsafe.Markup`。
3. **ir.model***：直接读 `ir.model`/`ir.model.fields`/`ir.model.data` → `sudo()` 或模型自身 API。
4. **邮件模板**：`${ }` Jinja → 正文 `type="qweb"` + `t-out`；subject 等 → `{{ }}` inline_template。
5. **前端**：`@odoo-module` 的 JS 改名 `.esm.js`；资产从 XML 移入 `__manifest__.py` 的 `assets` 键，删 `qweb` 键。
6. **测试**：`SavepointCase` → `TransactionCase`；删 `Environment.manage()`。
7. **邮件（[verify]）**：`subtype=` → `subtype_xmlid=`（确认 15.0 源码）。
8. **DB 迁移**：模块 `migrations/15.0/` 写数据脚本（如需）。
9. **校验**：`-u` + 测试 + 清 `DeprecationWarning`；视图/QWeb 加载校验 `t-raw` 合法性。
10. **出报告**：列出每处改动、残留 `[verify]` 项（subtype）。

---

## 附录 A：研究来源与溯源

- **OCA《Migration to version 15.0》**（maintainer-tools wiki）——权威变更清单（`t-raw`→`t-out`/`t-esc` +
  `markupsafe.Markup`、ir.model* 访问移除 #69120、Jinja→QWeb/inline_template #77074、`.esm.js` 改名、
  资产进 manifest `assets` 键（移除 `qweb` 键）、`SavepointCase`→`TransactionCase` #62031、
  `Environment.manage()` 移除）。
- **Odooo 论坛 / Cybrosys / apps.odoo 社区**（core changes v14→v15 汇总帖）——交叉验证上述条目。
- **odoo/odoo 提交** 01875541b1a8（`t-raw` 移除）、#69120（ir.model*）、#77074（Jinja→QWeb）、
  #62031（SavepointCase）。
- **版本作用域红线**：对照 12→13 / 13→14 / 15→16 / 16→17 / 17→18 烹饪书，确认 account.move、
  `ir.actions.*` 访问、`attrs` 硬拒、`tree`→`list`、`name_get` 移除、`get_resource_path`、
  payment.provider 等**均不属于 14→15 首发**（`track_visibility`→`tracking` 实属 12→13）。

> 标注 `[verify]` 的项（邮件 `subtype`→`subtype_xmlid`）为社区普遍归入 14→15 但 OCA 核心指南未逐条列者，
> 建议以 15.0 源码最终确认后再固化到技能 references。
