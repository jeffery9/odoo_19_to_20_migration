# 13→14 研究来源与源码核实地图

> 本文件记录 13→14 每条破坏性变更的溯源与核实状态，供修订时复核。

## 已核实（CONFIRMED）

| 变更 | 来源 | 核实方式 |
|---|---|---|
| `ir.actions.*` 直接访问移除 | OCA 14.0 + odoo/odoo#53335 | 用 `_for_xml_id` / `sudo()` / `/web/action/load` |
| `invisible`/`readonly` 动态表达式→`attrs` | OCA 14.0 官方指南 | 仅 context 直查可用；14.0 加载视图即校验 |
| `_name_search` 返回 ids | OCA 14.0 + commit 1f48130 | 不再返回 (id,name) 元组 |
| `_compute_display_name`→`name_get` | OCA 14.0 官方指南 | 加 `@api.depends` |
| `with_context(force_company=)`→`with_company` | OCA 14.0 | 14.0 弃用 force_company |
| `Char` `size=X` 属性移除 | OCA 14.0 官方指南 | size 不再限制长度 |
| `selection_add` 必须 `ondelete=` | OCA 14.0 + commit f0481392 | 每个旧值指定 set null/cascade |
| `string` 属性在 list 显示为文本 | OCA 14.0 官方指南 | 建议改用 title |
| 记录规则全局字段赋值行移除 | OCA 14.0 官方指南 | computed global 字段 |
| TransientModel 需显式 ACL | OCA 14.0 官方指南 | 向导模型补访问权 |
| 14.0 无 `odoo/upgrade_code/` 模块 | odoo/odoo 仓库核查 | codemod 引擎 18.0 才出现 |

## 待核实（[verify] / [EE-verify]）

| 变更 | 状态 | 备注 |
|---|---|---|
| `stock.picking.move_lines`→`move_ids_without_package`、`move_line_ids`→`move_line_ids_without_package` | [verify] | OC14.0 核心指南未逐条列；待 14.0 `stock.picking` 源码核实 |
| EE 安全微调（企业版 14.0 group 继承） | [EE-verify] | 对照 EE 14.0 树复核 |

## 版本作用域红线（已对照确认不属于 13→14）

- `account.invoice`→`account.move` / `customer_rank` / `binding_view_types` —— 12→13
- `ir.model*` 访问移除 / `t-raw` 移除 / 资产进 manifest —— 14→15
- `SavepointCase`/`Environment.manage` 移除 —— 14→15
- `attrs`/`states` 硬拒 —— 16→17
- `<tree>`→`<list>` / `name_get` 移除 —— 17→18
- `payment.acquirer`→`payment.provider` / `coupon`→`loyalty` —— 15→16
- `track_visibility`→`tracking` —— 12→13（常被误归 14→15）
