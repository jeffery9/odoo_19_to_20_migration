# 14→15 研究来源与源码核实地图

> 本文件记录 14→15 每条破坏性变更的溯源与核实状态，供修订时复核。
> **2026-11 修订**：全表按 Odoo CE 14.0 / 15.0 源码树重核，推翻了 5 条原有结论
> （原表以 OCA 指南措辞为准，把「弃用」当成了「移除」）。

## 核实方法（本轮）

| 手法 | 命令/做法 | 用途 |
|---|---|---|
| 模型集 diff | `git grep -h -oE "_name *= *['\"][a-z][a-z0-9_]*(\.[a-z0-9_]+)+['\"]" <ref> -- '*.py'` 后 `comm` | 全库模型增减（14.0 927 → 15.0 1017，移除 21 / 新增 111） |
| 字段级 diff | `scripts/diff_core_models.py --repo <CE> --ref-a 14.0 --ref-b 15.0 --model <m>` | 单模型字段增删/改类型 |
| 定点核验 | `git show <ref>:<path>` + 导出后检索 | 读实现（`qweb.py`、`ir_model.py`、`api.py`、`tests/common.py`） |
| 版本追溯 | 同一定点在 11.0/12.0/13.0/16.0/17.0 重复 | 判定「首次出现/移除」的真实版本对 |

> **踩过的坑**：`git grep` 必须单双引号都查（`_name = "..."` 与 `_name = '...'` 并存）；
> 提取模型集合时必须包含 `odoo/addons/`（否则漏掉 `ir.actions.todo` 这类 base 模型，
> 误判成"已移除"）。

## 已核实（CONFIRMED）

| 变更 | 源码依据 | 核实结论 |
|---|---|---|
| QWeb `t-raw` / `t-esc` → `t-out` | 15.0 `base/models/qweb.py` 的 `_compile_directive_raw` / `_compile_directive_esc` | **两者均 deprecated**（渲染 + warning），16.0 才无 `t-raw` 字样 |
| `t-out` 转义语义 | 15.0 `qweb.py` `yield str(escape(content))`；`t-raw` 分支 `content = Markup(content)` | `t-out` **默认转义**，仅 `Markup` 值不转义；`t-raw` 靠内部包 Markup 保住旧语义 |
| `ir.model.data` 查询 API | 14.0/15.0 `ir_model.py` 方法集对比 | `xmlid_lookup`/`xmlid_to_res_id`/`xmlid_to_res_model_res_id` 加下划线；`_get_id(module, xml_id)`、`get_object_reference`、`get_object`、`xmlid_to_object` **移除**；`check_object_reference` 保留 |
| `ir.model*` 访问控制 | 14.0 vs 15.0 `ir_model.py` 全文 diff | **无「禁止访问」变更**；原「访问移除」结论证伪 |
| `mail.template` 渲染引擎 | 15.0 `mail_render_mixin.py` `_render_template(engine='inline_template')`；`mail_template.py` `body_html = fields.Html(..., render_engine='qweb')` | 默认 engine `jinja`→`inline_template`；允许值改为 `inline_template`/`qweb`/`qweb_view`；传 `jinja` 抛 `ValueError`；`_render_template_jinja` 消失 |
| 模板 XML 的 `type` | 15.0 全库 XML 统计 | `type="qweb"` **零出现**；`type="html"` 58 处；14.0 的 `type="xml"`（9 处）在 15.0 消失 |
| ES 模块须改名 `*.esm.js` | OCA 15.0 指南（工具链约定，未单独源码核验） | 保持原结论 |
| 资产声明移入 manifest `assets` | manifest 统计：CE 14.0 assets=0/qweb=77 → 15.0 assets=179/qweb=1；EE 14.0 assets=0/qweb=77 → 15.0 assets=135/qweb=2 | 结论成立；但 `qweb` 键是**静默忽略**而非报错（`l10n_ae_pos` 仍留着） |
| `ir.asset` 模型 | 15.0 `odoo/addons/base/models/ir_asset.py`（14.0 无）；EE 15.0 `documents/data/ir_asset.xml` | 15.0 新增，承接资产记录 |
| `SavepointCase` | 15.0 `odoo/tests/common.py`：`class SavepointCase(TransactionCase)` + `DeprecationWarning`；14.0 为 `SavepointCase(SingleTransactionCase)` | **未移除**，是弃用别名且**基类已变**（事务语义变化） |
| `Environment.manage()` | 15.0 `odoo/api.py`：`warn(...)` + `yield` | **未移除**，变 no-op |
| 15.0 无 `odoo/upgrade_code/` | 仓库核查 | codemod 引擎 18.0 才出现；14→15 全部人工 |
| 安全文件与 `res.groups` 不变 | 未发现 14→15 相关改动 | 保持原结论 |

## 核心模型变更（源码 diff 得出，17 条）

见 `Core_Models_Changelog.md` 第 2 节 14→15 区块与烹饪书 9.1。要点：

- `stock.inventory` / `.line` 移除 → `stock.quant` 盘点字段（`inventory_quantity`/`inventory_quantity_set`/`inventory_diff_quantity`/`inventory_date`）+ `stock.inventory.adjustment.name`；同期新增 `stock.inventory.conflict`/`warning`/`request.count`
- 会计支付方式行化：`account.journal.inbound/outbound_payment_method_ids`(m2m) → `*_payment_method_line_ids`(o2m)，新增 `account.payment.method.line`
- `amount_by_group`（`account.move` / `sale.order`）移除 → `tax_totals_json`；`tax_cash_basis_move_id` → `tax_cash_basis_origin_move_id`
- `account.move.line.tax_exigible` 移除 → `account.move.always_tax_exigible`；`tax_fiscal_country_id` → move 级 `tax_country_id`
- `product.template.lst_price` 移除（仅 `product.product` 保留）；`detailed_type` 新增（18.0 再移除）
- `hr.leave` 多人休假（`employee_ids`/`multi_employee`）+ 加班抵扣（`overtime_id`/`overtime_deductible`）+ 附件；`payslip_status` 移除
- `mail.moderation` 移除；`mail.message` 的 `moderation_status`/`moderator_id`/`need_moderation`/`channel_ids` 移除，新增 `reaction_ids`/`author_guest_id`
- 移除：`phone.validation.mixin`、`project.task.create.sale.order`、`calendar.contacts`、`closing.balance.confirm.wizard`、`export.computed.binary`、`lunch.product.report`、`website.mass_mailing.popup`
- 新增：`ir.asset`、`res.users.settings`(+`.volumes`)、`crm.team.member`、`stock.storage.category`/`.capacity`、`stock.package.type`、`stock.replenishment.info`、`hr.leave.accrual.plan`/`.level`、`hr.contract.history`/`hr.contract.type`、`project.collaborator`
- 横切：`account.move.narration`、`sale.order.note`、`product.template.description`、`res.partner.comment`、`stock.picking.note` 由 `Text` → `Html`

## 被证伪 / 已订正（rejected）

| 原结论 | 证伪依据 |
|---|---|
| `t-raw` 在 15.0 被移除 | 15.0 `qweb.py` 保留 `_compile_directive_raw`（warning + 仍编译）；16.0 才为零 |
| `t-out` 等价旧 `t-raw`（不转义） | `t-out` 编译为 `escape(content)`；`t-raw` 分支额外 `Markup(content)` 才保住不转义 |
| `ir.model*` 直接访问被移除（#69120） | `ir_model.py` 两版 diff 无访问控制变化；`ir.model`/`ir.model.fields` 的 search 与 `_fields` 在 15.0 正常 |
| 用 `_get_id()` 修 `ir.model.data` | `_get_id(module, xml_id)` 本身在 15.0 被移除 |
| `SavepointCase` 别名在 15.0 移除 | 15.0 仍定义该类，只是弃用 + 基类改为 `TransactionCase` |
| `Environment.manage()` 在 15.0 移除 | 15.0 仍定义，改为 warn + yield |
| `mail.template` 正文 XML 写 `type="qweb"` | 15.0 全库 XML 中 `type="qweb"` 零出现；引擎由字段参数 `render_engine` 声明 |
| `subtype` → `subtype_xmlid` 属 14→15 | `message_post` 签名：13.0 有 `subtype`，14.0/15.0 均为 `subtype_xmlid`+`subtype_id`，故属 **13→14** |
| manifest `qweb` 键在 15.0 会报错 | 被静默忽略；官方 `l10n_ae_pos` 至今仍带该键且不报错 |

## 待核实

（本轮无遗留。EE 侧资产机制已用 EE 14.0/15.0 树核实：与 CE 同构——`assets` 键从 0 → 135，`qweb` 残留 2。）

## 版本作用域红线（已对照确认不属于 14→15）

- `account.invoice`→`account.move` / `customer_rank` / `binding_view_types` —— 12→13
- `ir.actions.*` 访问移除 / `invisible`/`readonly` 动态表达式 → `attrs` —— 13→14
- `subtype`→`subtype_xmlid` —— **13→14**
- `track_visibility`→`tracking` —— 12→13（常被误归 14→15）
- `payment.acquirer`→`payment.provider` / `coupon`→`loyalty` / `stock.production.lot`→`stock.lot` / `ir_translation`→JSONB —— 15→16
- `t-raw` 的**彻底移除** —— **15→16**
- `attrs`/`states` 硬拒 / `get_resource_path`→`file_path` / Python 3.10 底座 —— 16→17
- `<tree>`→`<list>` / `name_get` 移除 —— 17→18
- `res.groups` 权限改造 / `ir.access.csv` —— 18→19、19→20
