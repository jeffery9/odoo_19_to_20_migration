# 14→15 字段 / 资产 / API 映射表（源码核对版）

> 来源：Odoo CE 14.0 / 15.0 源码树复核（`git show` + 模型集/字段级 diff）。
> OCA《Migration to version 15.0》仅作线索——其「removed」措辞对 `t-raw`/`t-esc`/
> `SavepointCase`/`Environment.manage()` 均不成立（实为 deprecated）。
> 作用域：仅 14→15。

## 1. QWeb 指令：`t-raw` / `t-esc` → `t-out`  — CONFIRMED

15.0 里 `t-raw`、`t-esc` 都被标记 deprecated（可渲染 + 写 warning），**16.0 才彻底移除**。
`t-out` 编译为 `escape(content)`，转义与否取决于**值的类型**：

| 14.0 | 15.0 | 语义 |
|---|---|---|
| `<t t-raw="expr"/>` | `<t t-out="expr"/>`，expr 为 `Markup` | 原样输出（等价旧 t-raw） |
| `<t t-raw="expr"/>` | `<t t-out="expr"/>`，expr 为普通 `str` | **会被转义**（不等价！页面不报错但格式丢失） |
| `<t t-esc="expr"/>` | `<t t-out="expr"/>` | 转义输出 |
| 服务端拼的 HTML | `markupsafe.Markup(html)` + `t-out` | 避免双重转义 |

判断口径：值来自 `fields.Html`（`body_html`/`description`/`narration`/`comment`）→ 直接 `t-out`；
值来自 `Char`/`Text` → 需要渲染 HTML 时才包 `Markup`。

## 2. `__manifest__.py` 资产声明  — CONFIRMED

| 14.0 | 15.0 |
|---|---|
| XML `<template>` 内 `<link>`/`<script>` 资产 | 移入 manifest `assets` 键 |
| manifest `'qweb': [...]` 键（14.0 有 77 个模块在用） | 删除；**被静默忽略，不报错** |
| `<template id="assets_backend" inherit_id="web.assets_backend">` | 不再生效（`web.assets_backend` 已非可继承 QWeb 视图） |
| 路径相对模块目录 | 路径相对仓库根目录（支持 glob） |
| — | 新增 `ir.asset` 模型承接资产记录 |

## 3. ES 模块文件改名  — CONFIRMED

| 14.0 | 15.0 |
|---|---|
| `static/src/js/foo.js`（`/** @odoo-module **/`） | `static/src/js/foo.esm.js`（并改资产引用） |

## 4. `ir.model.data` 查询 API  — CONFIRMED

| 14.0 | 15.0 | 备注 |
|---|---|---|
| `xmlid_lookup(xmlid)` | `_xmlid_lookup(xmlid)` | 返回 `(id, res_model, res_id)` |
| `xmlid_to_res_id(xmlid, ...)` | `_xmlid_to_res_id(xmlid, ...)` | 取 id |
| `xmlid_to_res_model_res_id(xmlid, ...)` | `_xmlid_to_res_model_res_id(xmlid, ...)` | 返回 `(res_model, res_id)` |
| `xmlid_to_object(...)` | — | 移除 |
| `_get_id(module, xml_id)` | — | **移除**；用 `_xmlid_lookup("m.x")[0]` |
| `get_object_reference(module, xml_id)` | — | **移除**；用 `_xmlid_to_res_model_res_id` |
| `get_object(module, xml_id)` | — | 移除 |
| `check_object_reference(...)` | `check_object_reference(...)` | 保留 |

首选 `self.env.ref('module.xmlid')`（两个版本都在、行为未变）。

## 5. `mail.template` 渲染引擎  — CONFIRMED

| | 14.0 | 15.0 |
|---|---|---|
| `_render_template` 默认 engine | `jinja` | `inline_template` |
| 允许值 | `jinja`、`qweb` | `inline_template`、`qweb`、`qweb_view` |
| 传 `engine='jinja'` | 正常 | 抛 `ValueError` |
| `body_html` 定义 | `fields.Html('Body', translate=True, sanitize=False)` | 加 `render_engine='qweb'` |
| 数据 XML 写法 | `type="html"`（少量 `type="xml"`） | `type="html"`（`type="xml"` 已无；`type="qweb"` 从来不存在） |
| `_render_template_jinja` / `_render_jinja_eval_context` | 存在 | **不存在** |

## 5.1 移除的模型（会直接 `KeyError`）  — CONFIRMED

`phone.validation.mixin`、`mail.moderation`、`project.task.create.sale.order`、`calendar.contacts`、
`closing.balance.confirm.wizard`、`export.computed.binary`、`lunch.product.report`、
`website.mass_mailing.popup`。

- `phone.validation.mixin` 影响面最大：很多伙伴/员工模块继承它做电话校验，
  15.0 改为调用 `phone_validation` 工具函数（`phone_format` / `phone_parse`）。
- `mail.moderation` 移除时，`mail.message` 的 `moderation_status`/`moderator_id`/`need_moderation`
  也一并消失。

## 6. 字段类型：`Text` → `Html`  — CONFIRMED

| 模型.字段 | 14.0 | 15.0 |
|---|---|---|
| `account.move.narration` | Text | Html |
| `sale.order.note` | Text | Html |
| `product.template.description` | Text | Html |
| `res.partner.comment` | Text | Html |
| `stock.picking.note` | Text | Html |

## 7. 核心业务模型字段  — CONFIRMED

| 14.0 | 15.0 | 类别 |
|---|---|---|
| `account.journal.inbound_payment_method_ids`(m2m) | `inbound_payment_method_line_ids`(o2m) | 结构变化 |
| `account.journal.outbound_payment_method_ids`(m2m) | `outbound_payment_method_line_ids`(o2m) | 结构变化 |
| — | `account.payment.method.line`（`payment_method_id`/`payment_account_id`/`sequence`/`journal_id`） | 新模型 |
| `account.move.amount_by_group`(Binary) | `tax_totals_json`(Char) | 字段移除 |
| `sale.order.amount_by_group`(Binary) | `tax_totals_json`(Char) | 字段移除 |
| `account.move.line.tax_exigible` | `account.move.always_tax_exigible` | 字段上移 |
| `account.move.line.tax_fiscal_country_id` | `account.move.tax_country_id`/`tax_country_code` | 字段上移 |
| `account.move.tax_cash_basis_move_id` | `tax_cash_basis_origin_move_id` | 改名 |
| `product.template.lst_price` | 移除（仅 `product.product.lst_price`） | 字段移除 |
| — | `product.template.detailed_type` | 新增（18.0 又移除） |
| `stock.inventory` / `.line` | 移除 → `stock.quant`（`inventory_quantity*`/`inventory_date`）+ `stock.inventory.adjustment.name` | 模型移除 |
| `hr.leave.payslip_status` | 移除；新增 `employee_ids`/`multi_employee`/`overtime_id`/`overtime_deductible` | 结构调整 |

## 红线

- `payment.acquirer`→`payment.provider`、`coupon`→`loyalty`、`stock.production.lot`→`stock.lot` → 15→16；
- `ir_translation`→JSONB → 15→16；`attrs`/`states` 硬拒 → 16→17；
- `subtype`→`subtype_xmlid` → **13→14**（14.0 起 `message_post` 已无 `subtype` 参数）；
- `t-raw` 的**彻底移除** → **15→16**（15.0 仅 deprecated）；
- 「15.0 移除 `ir.model*` 访问」不成立：`ir.model` / `ir.model.fields` 的 search 与 `_fields` 在 15.0 正常。
