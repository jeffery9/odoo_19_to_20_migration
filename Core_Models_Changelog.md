# Odoo 核心业务模型变更追踪（5.0 → 20.0）

> 用途：跨版本（**5.0 → 20.0**，共 15 条版本对）跟踪 Odoo **标准核心业务模型**的演变——
> 模型改名、字段增删/改名、模型废弃、关键行为变化——为模块迁移提供"哪里会变"的全局索引。
> 与每个版本对的 `OdooXXtoYYMigration/references/` 关系：**本文件是跨版本全局索引**，
> 各版本对 references 是单版本对的明细实现。两者同源、互为索引。
>
> **来源与核实**：条目优先以本地源码仓库为事实基准——Odoo CE（`/Volumes/ssd-1tb/_repos/odoo`，
> 分支 5.0–20.0）与 EE（`/Volumes/ssd-1tb/_repos/odoo-enterprise`，9.0–20.0）——通过
> `scripts/diff_core_models.py`（本地 git 模式，`git show <ref>:<path>` + AST 提取 `_name`/字段）
> 做模型集 diff 与字段级 diff 复核。凡标注 `CONFIRMED` 且来源含"Odoo N.N 源码"者，均已源码级坐实；
> 早期基于论坛/OCU 拆解的条目已在核对中纠正（如 `is_storable` 自 18.0 已定义于 `stock`、20.0 才上移
> `product`，并非新增、也非 `type` 改名；`move_lines`/`move_ids_without_package` 长期共存、到 19.0 才移除，
> 而非 13→14 改名；`stock.pack.operation` 实为 9→10 移除；`res.partner.mobile` 移除实为 18→19；
> `stock.quant.package`→`stock.package` 与 `hr.contract`→`hr.version` 均属 18→19）。
> 已完成源码级扫描的版本对：12→13、13→14、14→15、15→16、16→17、17→18、18→19、19→20。
> EE 专属模型（`crossovered.budget` 族、`hr.payslip.input.type`）已用 EE 仓库
> （`--repo /Volumes/ssd-1tb/_repos/odoo-enterprise`）复核完毕，`[EE-verify]` 条目已清零。

---

## 0. 范围与对象

- **跟踪对象**：标准 `addons` 中的核心业务模型（会计、销售、采购、库存、伙伴、产品、HR、项目、邮件、支付等）。
- **不跟踪**：纯技术/内部模型（`ir.model.data`、`ir.ui.view` 等结构表，除非直接影响业务访问，如 `ir.model.access`/`ir.access`）；
  纯 API 层变化（方法签名、装饰器）除非伴随模型/字段改名，另见各版本对烹饪书。
- **版本覆盖**：5→6、6→7、7→8、8→9、9→10、10→11、11→12、12→13、13→14、14→15、15→16、16→17、17→18、18→19、19→20。

---

## 1. 图例与版本作用域纪律

| 标记 | 含义 |
|---|---|
| `CONFIRMED` | 已对照目标版本源码/OCA 迁移脚本/官方发布说明核实 |
| `[verify]` | 已知方向正确，但精确字段名/版本需实机或源码复核 |
| `[EE-verify]` | Enterprise 版专属，需对照 EE 对应版本树复核 |
| `codemod:xxx` | Odoo 自带 `odoo-bin upgrade_code --script xxx` 可自动处理（仅 18→20 可用） |
| `OpenUpgrade` | 由社区 OpenUpgrade 脚本处理 DB/数据层 |

> **版本作用域红线（防误归）**：以下变更常被误贴到错误版本对，本追踪严格按"首次出现版本"标注：
> - `account.invoice`→`account.move`：**12→13**（非 11→12 或更早）
> - `res.partner.address` 移除：**6→7**（非 7→8）
> - `osv.osv`→`models.Model` 基类改写：**7→8**（6→7 仅是 `osv.osv`→`osv.Model` 别名过渡）
> - `@api.one` 移除 / `fields.Date` 运行时对象化：**11→12**
> - `<tree>`→`<list>`：**17.5**（17→18 区间但属 17.5 小版本）
> - `_sql_constraints`→`models.Constraint`：**18.1**
> - `ir.model.access.csv`→`security/ir.access.csv`：**19→20**

---

## 2. 核心模型变更事件总表

> 列：模型（旧→新 / 名称）｜版本对｜变更类型｜变更详情｜可信度｜自动化｜来源
> 变更类型：`RENAME`(模型改名) `FIELD-RENAME` `FIELD-ADD` `FIELD-REMOVE` `DEP`(废弃) `BEHAVIOR`(行为变化)

| 模型                                                                | 版本对   | 类型           | 变更详情                                                                                                                                        | 可信度         | 自动化                            | 来源                                                                   |
| ----------------------------------------------------------------- | ----- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ------------------------------ | -------------------------------------------------------------------- |
| `res.partner.address`                                             | 6→7   | DEP          | 模型移除，地址字段合并进 `res.partner`（`street`/`city`/`zip` 等成为 partner 字段）                                                                            | CONFIRMED   | OpenUpgrade                    | Odoo7to8Migration/references/models-mapping.md；6→7 SKILL             |
| `osv.osv`→`osv.Model`                                             | 6→7   | BEHAVIOR     | 旧基类 `osv.osv` 弃用，改用 `osv.Model`（兼容别名）；7→8 再转 `models.Model`                                                                                 | CONFIRMED   | 手工                             | Odoo7to8Migration/references/models-mapping.md                       |
| `osv.osv`/`osv.Model`→`models.Model`                              | 7→8   | RENAME       | 模型基类改写；`osv.osv_memory`→`models.TransientModel`                                                                                             | CONFIRMED   | 手工                             | Odoo7to8Migration/references/models-mapping.md                       |
| `_columns` 字典 → 类属性 `fields.X`                                    | 7→8   | BEHAVIOR     | 字段声明方式由 `_columns={}` 改为类属性（`name = fields.Char(...)`）；字段容器 `_columns`→`_fields`                                                            | CONFIRMED   | 手工(sed)                        | Odoo7to8Migration/references/models-mapping.md                       |
| `self.pool.get('x')`→`self.env['x']`                              | 7→8   | BEHAVIOR     | 取模型方式改写；`osv.except_osv`→`raise UserError`                                                                                                  | CONFIRMED   | 手工                             | Odoo7to8Migration/references/models-mapping.md                       |
| `ir.cron.model`→`model_id`                                        | 10→11 | FIELD-RENAME | 定时动作引用模型字段改名（ref 到 `ir.model`）；建议改用 `code` 字段                                                                                               | CONFIRMED   | 手工                             | Odoo10to11Migration/README.md；Odoo10to11Migration/SKILL.md           |
| `ir.actions.act_window.view` 移除                                   | 11→12 | DEP          | 窗口动作绑定特定视图的模型被移除；视图绑定改动作上的 `view_ids`（o2m）或 `views`                                                                                         | CONFIRMED   | 手工                             | Odoo11to12Migration/references/models-mapping.md                     |
| `stock.pack.operation` 模型移除                                       | 9→10  | MODEL-REMOVE | 8.0/9.0 仍有 `stock.pack.operation`，10.0 起消失；其明细操作职责由 `stock.move.line` 接管（move.line 在 12.0+ 成为标准行模型）                                         | CONFIRMED   | OpenUpgrade                    | Odoo 源码（8/9.0 存在、10.0 起缺失）                                           |
| `account.invoice`→`account.move`                                  | 12→13 | RENAME       | 用 `move_type` 区分(out_invoice/in_invoice/out_refund/in_refund/out_receipt/in_receipt)；`is_invoice()` 辅助                                      | CONFIRMED   | codemod:accounting(部分)         | Odoo12to13Migration/references/accounting-models.md                  |
| `account.invoice.line`→`account.move.line`                        | 12→13 | RENAME       | `invoice_id`→`move_id`；税行并入 `account.move.line`（用 `tax_line_id` 标识）                                                                         | CONFIRMED   | codemod                        | Odoo12to13Migration/references/accounting-models.md                  |
| `account.voucher`→`account.move`                                  | 12→13 | RENAME       | 凭证模型合并进 `account.move`（`*_receipt` 类型）                                                                                                      | CONFIRMED   | OpenUpgrade                    | Odoo12to13Migration/references/accounting-models.md                  |
| `account.invoice.confirm`/`.refund` 向导                            | 12→13 | BEHAVIOR     | → `account.move.post()` / `account.move.reversal()` 方法                                                                                      | CONFIRMED   | 手工                             | Odoo12to13Migration/references/accounting-models.md                  |
| `account.move.amount`→`amount_total`                              | 12→13 | FIELD-RENAME | 金额汇总字段改名                                                                                                                                    | CONFIRMED   | codemod                        | Odoo12to13Migration/references/accounting-models.md                  |
| `account.move.reverse_entry_id`→`reversed_entry_id`               | 12→13 | FIELD-RENAME | 反向凭证关联字段改名                                                                                                                                  | CONFIRMED   | codemod                        | Odoo12to13Migration/references/accounting-models.md                  |
| `res.partner.customer`/`supplier`→`customer_rank`/`supplier_rank` | 12→13 | FIELD-RENAME | 布尔→整数 rank（可累计）；domain `('customer','=',True)`→`('customer_rank','>',0)`                                                                    | CONFIRMED   | codemod                        | Odoo12to13Migration/references/accounting-models.md                  |
| `account.tax.type` 字段变更（待核）                                       | 12→13 | FIELD-RENAME | 原行写 `type`→`type_tax_use` 未获源码支持（`type_tax_use` 自 v9 已有）；真实改名目标/版本待确认                                                                       | [verify]    | codemod                        | Odoo12to13Migration/references/accounting-models.md；源码复核存疑           |
| `hr.employee`→`hr.employee.base`                                  | 12→13 | RENAME       | 员工基类拆分（`hr.employee` 继承 `hr.employee.base`）                                                                                                 | CONFIRMED   | 手工                             | Odoo12to13Migration/references/orm-api.md                            |
| `stock.quant.qty`→`quantity`                                      | 10→11 | FIELD-RENAME | 库存定量字段改名（10.0 仍有 `qty`，11.0 起为 `quantity`；非 12→13）                                                                                          | CONFIRMED   | codemod                        | Odoo 源码（10.0 qty / 11.0 quantity）                                    |
| `product.product.name` 变为 related                                 | 12→13 | BEHAVIOR     | 产品名改为关联模板名（写模板）                                                                                                                             | CONFIRMED   | 手工                             | Odoo12to13Migration/README.md                                        |
| `stock.picking.responsible` 模型移除                                  | 13→14 | MODEL-REMOVE | 调拨负责人向导模型在 14.0 移除；同时新增补货报表模型、`stock.orderpoint.snooze` 等（**无** `move_lines`→`move_ids_without_package` 改名，二者长期共存）                          | CONFIRMED   | 手工                             | Odoo 源码（13→14 模型集 diff）                                              |
| `stock.inventory`/`stock.inventory.line` 模型移除                   | 14→15 | MODEL-REMOVE | 物理盘点单模型移除；盘点改由 `stock.quant`（`inventory_quantity`）+ 15.0 新增的 `stock.inventory.adjustment.name` 承载                                            | CONFIRMED   | OpenUpgrade                    | Odoo 源码（14.0 有、15.0 无；14→15 模型集 diff）                                  |
| `product.template.detailed_type` 新增                             | 14→15 | FIELD-ADD    | 新增 `detailed_type`（consu/product/service）与 `type` 并存，区分"可库存产品"与"消耗品"；该字段 18.0 又被移除                                                               | CONFIRMED   | 手工                             | Odoo 源码（15.0 出现、18.0 消失）                                               |
| `project.milestone`/`project.update` 模型新增                       | 14→15 | MODEL-ADD    | 项目里程碑与项目更新模型新增（项目域从任务扩展到里程碑/状态汇报）                                                                                                          | CONFIRMED   | 手工                             | Odoo 源码（14→15 模型集 diff）                                                 |
| `stock.production.lot`→`stock.lot`                                | 15→16 | RENAME       | 序列号模型改名                                                                                                                                     | CONFIRMED   | OpenUpgrade                    | Odoo_Migration_Cookbook_15_to_16.md（红线引用）                            |
| `payment.acquirer`→`payment.provider`                             | 15→16 | RENAME       | 支付提供商模型改名                                                                                                                                   | CONFIRMED   | OpenUpgrade                    | Odoo_Migration_Cookbook_15_to_16.md（红线引用）                            |
| `coupon`→`loyalty`                                                | 15→16 | RENAME       | 优惠券→会员忠诚模型合并                                                                                                                                | CONFIRMED   | OpenUpgrade                    | Odoo_Migration_Cookbook_15_to_16.md（红线引用）                            |
| `account.analytic.account.group_id`→`plan_id`                     | 15→16 | FIELD-RENAME | 分析账户→分析计划关联改名（15.0 `group_id`、16.0 `plan_id`；原挂 19→20 已纠正）                                                                                 | CONFIRMED   | OpenUpgrade                    | Odoo 源码（13–15 group_id、16.0 plan_id）                                        |
| `account.invoice.send`→`account.move.send`                        | 16→17 | RENAME       | 发票发送向导随 `account.invoice` 退场改为 `account.move.send`（18.0 再拆出 `account.move.send.wizard`）                                                      | CONFIRMED   | 手工                             | Odoo 源码（16.0 有 account.invoice.send、17.0 为 account.move.send）         |
| `account.*.template` 模型族移除                                      | 16→17 | MODEL-REMOVE | 科目表模板模型（`account.tax.template`、`account.fiscal.position.template`、`account.group.template` 等）在 17.0 全部移除，科目表改由 Python/CSV 数据文件定义            | CONFIRMED   | 手工                             | Odoo 源码（16→17 模型集 diff）                                                 |
| `hr.plan`/`hr.plan.activity.type`/`hr.plan.wizard` 移除             | 16→17 | MODEL-REMOVE | 员工入职/活动计划模型族在 17.0 移除（计划改由 `mail.activity.plan` 通用机制承载，CE 内无搬迁）                                                                  | CONFIRMED   | 手工                             | Odoo 源码（16.0 有、17.0 无）                                                   |
| `stock.immediate.transfer` 模型移除                                 | 16→17 | MODEL-REMOVE | "立即转运"向导移除；`stock.picking.immediate_transfer`/`show_validate`/`show_mark_as_todo` 字段同时移除                                                          | CONFIRMED   | 手工                             | Odoo 源码（16→17 模型集 + 字段 diff）                                           |
| `mrp.immediate.production` 模型移除                                 | 16→17 | MODEL-REMOVE | "立即生产"向导移除（生产改由 `mrp.production` 直接动作）                                                                                                        | CONFIRMED   | 手工                             | Odoo 源码（16.0 有、17.0 无）                                                   |
| `res.partner.display_name`→`complete_name`                        | 16→17 | FIELD-RENAME | 伙伴显示名存储字段改名（`_compute_complete_name`）；`translated_display_name` 同时移除                                                                         | CONFIRMED   | 手工                             | Odoo 源码（16.0 display_name / 17.0 complete_name）                            |
| `<tree>`→`<list>`（视图，影响模型列表呈现）                                    | 17.5  | BEHAVIOR     | 列表视图标签改名（属 17→18 区间但 17.5 引入）                                                                                                               | CONFIRMED   | codemod:xml(18→20)             | Odoo_Migration_Cookbook_17_to_18.md（红线）                              |
| ORM 包拆分（`openerp`→`odoo` 子包重组）                                    | 17→18 | BEHAVIOR     | `odoo.osv`/`odoo.orm` 等子包重组，import 路径变化                                                                                                     | CONFIRMED   | 手工                             | Odoo_Migration_Cookbook_17_to_18.md                                  |
| `product.combo`/`product.combo.item` 模型新增                       | 17→18 | MODEL-ADD    | 组合产品（Combo）进入 `product` 核心；17.0 的 `combo_ids` 仅关联 POS 的 `pos.combo`，18.0 起改由 `product.combo` 承载                                                            | CONFIRMED   | 手工                             | Odoo 源码（17.0 point_of_sale/pos.combo → 18.0 product/product_combo.py）        |
| `product.template.detailed_type` 移除                             | 17→18 | FIELD-REMOVE | `detailed_type` 移除，产品类型回归单一 `type`；可库存判定改由 `is_storable`（18.0 起定义在 `stock` 模块）承担                                                          | CONFIRMED   | 手工                             | Odoo 源码（17.0 有、18.0 无）                                                   |
| `stock.assign.serial` 模型移除                                      | 17→18 | MODEL-REMOVE | 批量分配序列号向导移除                                                                                                                                | CONFIRMED   | 手工                             | Odoo 源码（17.0 有、18.0 无）                                                   |
| `account.unreconcile` 模型移除                                      | 17→18 | MODEL-REMOVE | 反核销向导移除（核销撤销改由 `account.move` 的撤销/重置方法承载，无同名替代模型）                                                                               | CONFIRMED   | 手工                             | Odoo 源码（17.0 有、18.0 无）                                                   |
| `mrp.document` 模型移除                                             | 17→18 | MODEL-REMOVE | 制造文档模型移除（CE 与 EE 均无搬迁）                                                                                                                            | CONFIRMED   | 手工                             | Odoo 源码（17.0 有、18.0 无）                                                   |
| `res.partner.has_unreconciled_entries`/`last_time_entries_checked` 移除 | 17→18 | FIELD-REMOVE | 伙伴对账状态标记字段移除（对账状态改由 `account.move` 侧判断）                                                                                                       | CONFIRMED   | 手工                             | Odoo 源码（17→18 字段 diff）                                                    |
| EE `account_budget` 预算模型族重构 → `budget.analytic` 族                | 17→18 | RENAME       | EE `account_budget` 在 18.0 整体重建：移除 `crossovered.budget`、`crossovered.budget.lines`、`account.budget.post`（模型集 diff 显示 kept=0），新增 `budget.analytic`（含 `parent_id` 修订链）、`budget.line`、`budget.report`、`budget.split.wizard`。原挂 19→20 的 `crossovered.budget`→`budget.analytic` 已纠正为 17→18。**注意**：18.0 的 `account_budget/i18n/*.po` 仍残留 `crossovered_budget` 条目，属翻译文件未重生成，非模型存在证据 | CONFIRMED   | 手工                             | EE 源码（17.0 `account_budget/models/account_budget.py`；18.0 `budget_analytic.py`/`budget_line.py`；`diff_core_models.py --scan-modules account_budget`） |
| `_sql_constraints`→`models.Constraint`                            | 18.1  | BEHAVIOR     | 约束声明改为属性（`_code_uniq = models.Constraint(...)`）                                                                                             | CONFIRMED   | codemod:constraints(19→20)     | Odoo19to20Migration/references/security-and-orm.md                   |
| `stock.quant.package`→`stock.package`                             | 18→19 | RENAME       | 包裹模型改名；新增 `stock.package.history`，`stock.package_level` 同时移除（原挂 19→20 的该条已纠正为 18→19）                                                       | CONFIRMED   | OpenUpgrade                    | Odoo 源码（18.0 quant.package / 19.0 stock.package）                            |
| `hr.contract`→`hr.version`                                        | 18→19 | RENAME       | 合同模型随 `hr_contract` 模块并入 `hr`，改名 `hr.version`（19.0）；`hr.employee.base` 同时移除（原挂 19→20 的该条已纠正为 18→19）                                        | CONFIRMED   | OpenUpgrade                    | Odoo 源码（18.0 hr_contract / 19.0 hr.version）                                  |
| `hr.expense.sheet`→`hr.expense`                                   | 18→19 | RENAME       | 费用单模型合并进 `hr.expense`（18.0 仍有 `hr.expense.sheet`、19.0 已无）                                                                                | CONFIRMED   | OpenUpgrade                    | Odoo 源码（18.0 有、19.0 无）                                                   |
| `product.packaging` 模型移除                                        | 18→19 | MODEL-REMOVE | 包装模型移除；`product.template.packaging_ids` 与 `uom_po_id`/`uom_category_id` 同时移除（包装改由 `product.packaging` 之外的新机制/字段承载）                              | CONFIRMED   | OpenUpgrade                    | Odoo 源码（18.0 有、19.0 无；EE 亦无）                                           |
| `res.partner.mobile` 移除                                          | 18→19 | FIELD-REMOVE | 手机号字段移除，统一用 `phone`（此后 19/20 均无 `mobile`；原 19→20 说法版本有误）                                                                                   | CONFIRMED   | OpenUpgrade                    | Odoo 源码（18.0 res_partner.py 有、19.0 无）                                      |
| `stock.picking.move_ids_without_package`/`move_line_ids_without_package` 移除 | 18→19 | FIELD-REMOVE | 调拨行"无包"过滤字段移除（行明细统一走 `move_ids`/`move_line_ids`）；`date`、`group_id`、`has_packages`、`package_level_ids`、`move_line_exist` 同时移除              | CONFIRMED   | OpenUpgrade                    | Odoo 源码（18.0 有、19.0 无）                                                   |
| `procurement.group` 模型移除                                        | 18→19 | MODEL-REMOVE | 采购组模型移除；`stock.move.group_id`、`stock.picking.group_id`、`sale.order.procurement_group_id` 一并移除。**注意**：19.0 新增的 `stock.reference` 并非其改名目标——`stock.reference` 是"库存单据引用链"（`_description = 'Reference between stock documents'`，`move_ids` m2m + `picking_ids` compute），不含采购分组语义；二手资料称改名属误判 | CONFIRMED   | OpenUpgrade                    | Odoo 源码（18.0 有 `procurement.group`/`group_id`，19.0 全无；19.0 `stock_reference.py` 为独立新模型） |
| `stock.reference` 模型新增                                          | 18→19 | MODEL-ADD    | 新增"库存单据引用链"模型（`addons/stock/models/stock_reference.py`），字段 `name` + `move_ids`(m2m) + `picking_ids`(compute)；`stock.move.reference_ids`、`stock.picking.reference_ids`(related) 引用它，用于替代服务端 `origin` 字符串串接补货链。**不是** `procurement.group` 的替代 | CONFIRMED   | 手工                             | Odoo 源码（19.0 新增，18.0 无）                                                |
| `account.fiscal.position.tax` 模型移除                              | 18→19 | MODEL-REMOVE | 税位-税映射模型移除（税位直接映射税标签）                                                                                                                          | CONFIRMED   | OpenUpgrade                    | Odoo 源码（18.0 有、19.0 无）                                                   |
| `project.role`/`project.template.create.wizard` 模型新增             | 18→19 | MODEL-ADD    | 项目角色与项目模板向导新增（权限按角色分配）                                                                                                                     | CONFIRMED   | 手工                             | Odoo 源码（18→19 模型集 diff）                                                  |
| `res.users.groups_id`→`group_ids`                                 | 18→19 | FIELD-RENAME | 用户-组关联字段改名（18.0 仍是 `groups_id`、19.0 起 `group_ids`；原挂 19→20 已纠正）                                                                              | CONFIRMED   | OpenUpgrade                    | Odoo 源码（18.0 vs 19.0 res_users.py）                                          |
| `ir.model.access.csv`→`security/ir.access.csv`                    | 19→20 | RENAME       | 权限文件格式重写：列 `model_id/id`→`model_id`(技术名)、`perm_*`→`operation`(crud/cru...)、支持 domain                                                        | CONFIRMED   | codemod:ir-access              | Odoo19to20Migration/references/security-and-orm.md                   |
| `<record model="ir.rule">` XML                                    | 19→20 | DEP          | 记录规则改由 `ir.access.csv` 承载；XML 写 `ir.rule` 触发 `KeyError: 'ir.rule'`                                                                          | CONFIRMED   | codemod:ir-access              | Odoo19to20Migration/references/security-and-orm.md                   |
| `ir.attachment.datas` 移除（`raw` 早已并存）                          | 19→20 | FIELD-REMOVE | 旧别名 `datas` 在 20.0 移除；`raw` 自 17.0 起即存在（并非 19→20 改名）                                                                                     | CONFIRMED   | codemod                        | Odoo 源码（17–19 有 datas+raw，20 仅 raw）                                       |
| `res.partner.company_registry` 移除 → `additional_identifiers`      | 19→20 | FIELD-REMOVE | 伙伴/公司注册号字段移除，改由 `additional_identifiers`（JSON，按本地化键存多标识）承载（`mobile` 的移除实为 18→19，非本对）                                              | CONFIRMED   | 手工                             | Odoo 20 源码（OCU 拆解）；Odoo19to20Migration/references/modules-mapping.md |
| `product.template.is_storable` 上移                                | 19→20 | BEHAVIOR     | `is_storable` **并非新增**：18.0 起定义在 `stock` 模块（`addons/stock/models/product.py`），20.0 上移到 `product` 核心（`addons/product/models/product_template.py`）；`type` Selection 在 20.0 仍保留                     | CONFIRMED   | 手工                             | Odoo 源码（18.0 stock/product.py → 20.0 product/product_template.py）         |
| `sale.order.state='done'`                                         | 19→20 | FIELD-REMOVE | 销售订单 `done` 状态移除                                                                                                                            | CONFIRMED   | 手工                             | Odoo19to20Migration/references/modules-mapping.md                    |
| `product_uom`/`product_uom_id`→`uom_id`                           | 19→20 | FIELD-RENAME | `stock.move` 等模型单位字段改名（19.0 为 `product_uom`，20.0 起 `uom_id`）                                                                                   | CONFIRMED   | codemod                        | Odoo 源码（19.0 stock_move.py:product_uom → 20.0 uom_id）                         |
| `account.move` 报表 `type`→`move_type`                              | 19→20 | FIELD-RENAME | 凭证类型字段对齐                                                                                                                                    | CONFIRMED   | codemod                        | Odoo19to20Migration/references/modules-mapping.md                    |
| `hr.version.wizard`/`hr.contract.type` 移除                         | 19→20 | MODEL-REMOVE | 19→20 中 `hr.version.wizard`、`hr.contract.type` 模型被移除（原 `hr.contract`→`hr.version` 改名说法不成立：`hr.version` 在 19/20 均存在）                         | CONFIRMED   | 手工                             | Odoo 20 源码 + 19→20 模型集 diff                                          |
| `hr.leave.type` 模型移除                                              | 19→20 | MODEL-REMOVE | 休假类型模型在 20.0 移除（`hr.work.entry.type` 仍保留，并非其改名目标）                                                                                           | CONFIRMED   | 手工                             | Odoo 20 源码（hr.leave.type 19.0 有、20.0 无）                              |
| `hr.payslip.input.type` 模型移除 → 合并进 `hr.salary.rule`               | 19→20 | MODEL-REMOVE | EE `hr_payroll` 中该模型 19.0 尚存（`models/hr_payslip_input_type.py`，含 `code`/`struct_ids`/`country_id`/`is_quantity` 等），20.0 文件与模型一并消失；`hr.payslip.input` 改为直接挂 `salary_rule_id`（required，m2o `hr.salary.rule`），原 `name`/`code`/`input_suffix`/`user_instructions` 全部转为 related 到 salary rule。源码注释：*merged inputs into salary rules*。注意 `input_usage_payslip` 并非替代模型——它是 `hr.salary.rule` 上的既有布尔字段（19.0 已有），20.0 仅用于 input 行的 domain 过滤 | CONFIRMED   | 手工                             | EE 源码（19.0 `hr_payroll/models/hr_payslip_input_type.py`；20.0 该文件缺失、`hr_payslip_input.py` 改 `salary_rule_id`） |
| `stock.scrap` 模型移除                                                | 19→20 | MODEL-REMOVE | 报废模型 `stock.scrap` 在 20.0 移除；报废行为改由 `stock.move` 的 **`is_scrap`** 布尔字段承载（该字段 20.0 新增，见 `stock_move.py`/`stock_move_line.py`/`stock_lot.py`），配额补货走 `should_replenish_scrapped` | CONFIRMED   | 手工                             | Odoo 源码（stock.scrap 19.0 有、20.0 无；`is_scrap` 20.0 有、19.0 无）        |
| `stock.return.picking`→`stock.picking._create_return()`           | 19→20 | BEHAVIOR     | 退货向导改方法                                                                                                                                     | CONFIRMED   | codemod:stock                  | Odoo19to20Migration/references/modules-mapping.md                    |
| `mail.thread.cc` mixin 移除                                         | 19→20 | MODEL-REMOVE | 抄送 mixin `mail.thread.cc` 在 20.0 移除，抄送能力并入标准 `mail.thread`（并非改名为 mail.thread）                                                               | CONFIRMED   | 手工                             | Odoo 20 源码（mail.thread.cc 19.0 有、20.0 无）                             |
| `account.group` 模型移除                                              | 19→20 | MODEL-REMOVE | 科目组模型 `account.group` 在 20.0 移除；科目分组改由 `account.account` 的 `parent_id`/`parent_ids` 层次结构表达                                                  | CONFIRMED   | codemod:19.3-00-account-groups | Odoo 20 源码（account.group 19.0 有、20.0 无）                              |
| `res.bank` → 合并进 `res.partner.bank`                               | 19→20 | RENAME       | `res.bank` 模型移除；银行名称/BIC/地址改存于 `res.partner.bank`（`bank_name`/`bank_bic` 变为存储字段；`acc_number`→`account_number`、`bank_id.name`→`bank_name` 等） | CONFIRMED   | 手工                             | Odoo 20 源码（OCU 拆解）；Odoo19to20Migration/references/modules-mapping.md |
| `payment.provider` 模型移除                                           | 19→20 | MODEL-REMOVE | 支付商模型 `payment.provider` 在 20.0 移除（支付体系重构；原 `state`→`is_published`/`is_live` 改为新模型字段）                                                       | CONFIRMED   | 手工                             | Odoo 20 源码（payment.provider 19.0 有、20.0 无）                           |
| `mrp.production.show_produce_all`                                 | 19→20 | FIELD-REMOVE | 生产单"全部生产"辅助字段移除                                                                                                                             | CONFIRMED   | 手工                             | Odoo19to20Migration/references/modules-mapping.md                    |
| `product.template.attribute.exclusion` 移除                         | 19→20 | DEP          | 变体排除模型移除；排除改为 `product.template.attribute.value` 上的 m2m `excluded_value_ids`（限定同模板值）                                                        | CONFIRMED   | 手工                             | Odoo 20 源码（OCU 拆解）；Odoo19to20Migration/references/modules-mapping.md |
| `stock.move.location_final_id`→`forecasted_location_id`           | 19→20 | FIELD-RENAME | 库存移动最终库位字段改名                                                                                                                                | CONFIRMED   | codemod                        | Odoo 20 源码（OCU 拆解）                                                   |
| `stock.picking.batch` 合并进 `stock`                                 | 19→20 | RENAME       | `stock_picking_batch` 模块并入 `stock`，`stock.picking.batch` 改由 stock 模块提供                                                                      | CONFIRMED   | 手工                             | Odoo 20 源码（OCU 拆解）                                                   |

> 说明：第 2 节只收录**有源码依据**的业务模型 / 字段级变更；纯 API、框架与视图层变化（如 11→12 `@api.one` 移除、16→17 Owl 2、17→18 `<tree>`→`<list>`）不入表，见各自烹饪书与 `references/`。所有条目已用本地 CE 仓库 `git grep` / `diff_core_models.py` 复核；未能源码坐实的显式标 `[verify]`，需 EE 源码的标 `[EE-verify]`。

---

## 3. 按版本对汇总（业务模型视角）

- **5→6**：无模型层重命名；仅 manifest 键迁移（`__terp__.py`→`__openerp__.py`）。业务模型不变。
- **6→7**：`res.partner.address` 移除（合并入 `res.partner`）；`osv.osv`→`osv.Model` 基类过渡。
- **7→8**：New API 落地——基类 `models.Model`、字段类属性声明、`self.env`、记录集、`UserError`；模型**结构不变**，是声明方式革命。
- **8→9**：Community/Enterprise 拆分；无大规模模型重命名。
- **9→10**：`openerp`→`odoo` 包改名；无模型重命名。
- **10→11**：Python 3 + Workflow 移除 + QWeb 报表 API 重写；`ir.cron.model`→`model_id` 字段改名。
- **11→12**：`@api.one` 移除、`fields.Date` 对象化；**`ir.actions.act_window.view` 模型移除**（视图绑定改动作 `view_ids`）。
- **12→13**：**会计"浩劫"**——`account.invoice`/`account.voucher` 合并进 `account.move`；`res.partner` rank 化（`customer`/`supplier`→`customer_rank`/`supplier_rank`）；`account.move.amount`→`amount_total`、`reverse_entry_id`→`reversed_entry_id`；`hr.employee.base` 基类拆分；另 **`stock.pack.operation` 模型移除（9→10，由 `stock.move.line` 接管）**、`stock.quant.qty`→`quantity`（实为 10→11）。
- **13→14**：库存/MRP 重构——新增补货报表、`stock.orderpoint.snooze` 等；`stock.picking.responsible` 模型移除（`move_lines` 与 `move_ids_without_package` 自 12.0 起长期共存，**并非 13→14 改名**，二者到 19.0 才一并移除）。
- **14→15**：**盘点模型换代**——`stock.inventory`/`stock.inventory.line` 移除（盘点改 `stock.quant` + `stock.inventory.adjustment.name`）；`product.template.detailed_type` 新增（18.0 又移除）；`project.milestone`/`project.update`、`hr.departure.reason`、`stock.storage.category` 等新增。
- **15→16**：`stock.production.lot`→`stock.lot`、`payment.acquirer`→`payment.provider`、`coupon`→`loyalty`。
- **16→17**：**科目表去模型化**——`account.*.template` 模型族移除（科目表改 Python/CSV 数据）；`account.invoice.send`→`account.move.send`；`hr.plan` 族、`stock.immediate.transfer`、`mrp.immediate.production` 移除；`res.partner.display_name`→`complete_name`。
- **17→18**（含 17.5）：`<tree>`→`<list>`；ORM 子包重组；**组合产品**`product.combo` 新增、`product.template.detailed_type` 移除；`stock.assign.serial`、`account.unreconcile`、`mrp.document` 移除；**EE 预算模型族整体重建**——`crossovered.budget`/`crossovered.budget.lines`/`account.budget.post` 移除，改由 `budget.analytic`/`budget.line`/`budget.report`/`budget.split.wizard` 承载（kept=0，属重写而非改名）。
- **18→19**（含 18.1）：**模型大搬迁**——`stock.quant.package`→`stock.package`、`hr.contract`→`hr.version`（`hr_contract` 并入 `hr`）、`hr.expense.sheet`→`hr.expense`、`res.users.groups_id`→`group_ids`；`product.packaging`、`procurement.group`（连带 `stock.move.group_id`/`stock.picking.group_id`/`sale.order.procurement_group_id`）、`stock.package_level`、`account.fiscal.position.tax`、`hr.employee.base` 移除；`stock.reference`（单据引用链，非 procurement.group 替代）、`project.role`/`project.template.create.wizard` 新增；`res.partner.mobile`、`stock.picking.move_ids_without_package` 移除；`_sql_constraints`→`models.Constraint`（18.1）；`upgrade_code` codemod 开始可用。
- **19→20**：**又一轮大规模模型变更**——字段改名：`stock.move.location_final_id`→`forecasted_location_id`、`stock.move.product_uom`→`uom_id`、权限文件 `ir.model.access.csv`→`security/ir.access.csv`；字段移除：`ir.attachment.datas`（`raw` 早已并存）、`res.partner.company_type`、`mrp.production.show_produce_all`；**模型移除**：`account.group`、`stock.scrap`、`hr.leave.type`、`hr.version.wizard`、`mail.thread.cc`、`payment.provider`、`res.bank`、`product.template.attribute.exclusion`、`stock.return.picking`；**新增/合并**：`is_storable` 从 `stock` 上移 `product` 核心（非新增）、`res.partner.additional_identifiers`、`stock.picking.batch` 并入 `stock`（模型保留）；`res.partner.company_registry` 移除（改 `additional_identifiers`）（多可 codemod 自动）。

---

## 4. 红线排除（常见误归，本追踪不记入其他版本对）

| 变更 | 真实归属 | 易误归为 |
|---|---|---|
| `account.invoice`→`account.move` | 12→13 | 11→12 / 10→11 |
| `res.partner.address` 移除 | 6→7 | 7→8 |
| `osv.osv`→`models.Model` | 7→8 | 6→7 |
| `@api.one` 移除 / `fields.Date` 对象化 | 11→12 | 12→13 |
| `stock.production.lot`→`stock.lot` | 15→16 | 14→15 / 16→17 |
| `payment.acquirer`→`payment.provider` | 15→16 | 14→15 |
| `<tree>`→`<list>` | 17.5 | 17→18 整段 |
| `_sql_constraints`→`models.Constraint` | 18.1 | 18→19 |
| `ir.model.access.csv`→`security/ir.access.csv` | 19→20 | 18→19 |
| `parent_path` / `ir.actions.act_window.view` 移除 | 11→12 | 12→13 |
| `crossovered.budget`→`budget.analytic`（EE 预算族） | 17→18 | 19→20 |
| `hr.payslip.input.type` 移除（EE 工资单） | 19→20 | 18→19 |
| `procurement.group`→`stock.reference` | **非改名**：前者 18→19 移除，后者同版本新增，语义不同 | 当成 18→19 改名 |
| `note.note`→`project.task` | **不成立**：17/18/19/20 均无 `note.note` 模型 | 19→20 |

---

## 5. 配套脚本 `scripts/diff_core_models.py`

本仓库提供跨版本模型/字段 diff 工具，对标 `MigrationKnowledgeForge/scripts/branch_diff.py`。**首选本地 git 模式**（无需联网，直接读本机 checkout 的真实源码）：

```bash
CE=/Volumes/ssd-1tb/_repos/odoo
EE=/Volumes/ssd-1tb/_repos/odoo-enterprise

# 1) 模型集 diff：某模块在两个版本间新增/移除了哪些 _name
python3 scripts/diff_core_models.py --repo "$CE" --ref-a 12.0 --ref-b 13.0 \
    --scan-modules account

# 2) 字段级 diff：单个核心模型（自动按 _name/_inherit 定位所有相关文件并聚合字段）
python3 scripts/diff_core_models.py --repo "$CE" --ref-a 13.0 --ref-b 14.0 \
    --model stock.picking

# 3) 模型集 diff + 指定模型的字段 diff 一次完成
python3 scripts/diff_core_models.py --repo "$CE" --ref-a 19.0 --ref-b 20.0 \
    --scan-modules account,sale,stock,product --focus-models account.move,res.partner

# 4) EE 专属模型（如工资单输入类型）
python3 scripts/diff_core_models.py --repo "$EE" --ref-a 19.0 --ref-b 20.0 \
    --model hr.payslip.input.type
```

脚本会自动定位模块目录（通过 `__manifest__.py`/`__openerp__.py` 反查，兼容 `addons/`、`odoo/addons/`、EE 根目录等任何布局）、兼容 `origin/7.0` 之类仅远端分支，并对旧 py2 语法（`except X, e:`）做正则兜底。输出：

- **模型集 diff**：模块内 `_name` 的新增 / 移除（并对同名尾段给出可能的改名提示）；
- **字段级 diff**：逐模型 `fields.X` 的**新增 / 移除 / 类型变更**；
- 均为 Markdown 就绪，可直接并入第 2 节总表。

> 无本地仓库时可用网络兜底：省略 `--repo`，改用 `--ref-a/--ref-b --pairs "old:new"`（拉取 GitHub raw 或 `--base-url` 内网镜像）；离线 `--self-test` 可验证 AST 逻辑。

---

## 6. 如何持续维护

1. 每新增/更新一个版本对（如未来 20→21），把该对 `references/` 中确认的业务模型变更**追加到第 2 节总表**，并同步第 3 节汇总。
2. 不确定归属的条目统一标 `[verify]`，并在对应 `work/<version>/VERIFY_TRACKER.md` 登记。
3. 用 `scripts/diff_core_models.py` 对争议模型做源码级复核，复核通过后把 `[verify]` 升级为 `CONFIRMED`。
4. 守住第 1 节与第 4 节的版本作用域红线，禁止把变更误归到非首现版本。
