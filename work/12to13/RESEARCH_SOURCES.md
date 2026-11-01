# 12→13 研究来源与源码核实地图

> 本文件记录 12→13 每条破坏性变更的溯源与核实状态，供修订时复核。

## 已核实（CONFIRMED）

| 变更 | 来源 | 核实方式 |
|---|---|---|
| `account.invoice`/`.line`/`.tax`/`account.voucher` 合并进 `account.move`/`account.move.line` | OCA 13.0 + Odoo accounting-pocalypse 提交说明 | 多社区一致；13.0 移除旧模型，`move_type` 区分 |
| `account.move.amount`→`amount_total`、`reverse_entry_id`→`reversed_entry_id` | OCA 13.0 / 提交说明 | 字段改名 |
| `res.partner` `customer`/`supplier`→`customer_rank`/`supplier_rank` | OCA 13.0 + shine-it | 布尔→整数 rank |
| `ir.actions.act_window.multi`→`binding_view_types`、`src_model`→`binding_model_id` | OCA 13.0 | 动作绑定字段改名 |
| `@api.multi`/`@api.returns`/`@api.cr`/`@api.model_cr` 移除 | OCA 13.0 官方指南 | 13.0 清退旧装饰器 |
| `dp.get_precision`→`digits` | OCA 13.0 | 直接字符串精度键 |
| `track_visibility`→`tracking` | OCA 13.0 官方指南 | **首现 13.0**（校正误归 15→16 的旧说法） |
| `oldname` 字段属性移除 | OCA 13.0 | 用 openupgradelib rename_fields |
| `sudo(user)`→`with_user(user)` | OCA 13.0 | 无参 sudo() 保留 |
| `.env.user.company_id`→`.env.company` | OCA 13.0 | 环境属性改名 |
| 多公司规则 `'|'` 前缀形式 | OCA 13.0 | 规则写法 |
| `hr.employee`→`hr.employee.base` | OCA 13.0（commit c9ca376） | 继承基模型 |
| `stock.quant.qty`→`quantity` | OCA 13.0 + 11→12 红线确认 | 字段改名 |
| `product.product.name` 变 related | 13.0 源码核对 | 写模板而非变体 |
| `account.tax.type`→`type_tax_use` | 13.0 源码核对 | 字段改名 |
| `Binary` 默认存附件（`attachment=True`） | shine-it + 13.0 核对 | 确认 11→12 旧 [verify] 归属 12→13 |
| 视图 `view_type` 移除 | OCA 13.0 | 始终 form |
| 13.0 无 `odoo/upgrade_code/` 模块 | odoo/odoo 仓库核查 | codemod 引擎 18.0 才出现 |

## 待核实（[verify] / [EE-verify]）

| 变更 | 状态 | 备注 |
|---|---|---|
| 前端 FontAwesome 5 图标改名清单（`area-chart`→`chart-area` 等） | [verify] | 13.0 启用 FA5；完整改名清单待 13.0 资产实机确认 |
| JavaScript jQuery Promise→原生 Promise 的范围 | [verify] | OCA 13.0 要求替换；具体文件范围待前端实机确认 |
| EE 安全微调 | [EE-verify] | 企业版 13.0 group 继承链若有微调需对照 EE 树 |

## 版本作用域红线（已对照确认不属于 12→13）

- `@api.one`/`from_string`/`parent_path` —— 11→12
- `ir.actions.*` 访问移除（sudo 化） —— 13→14
- `_name_search` 返回 ids —— 13→14
- `attrs`/`states` 硬拒 —— 16→17
- `<tree>`→`<list>` —— 17→18
- `name_get` 移除 —— 17→18
- `ir.model*` 访问移除 / `t-raw` 移除 / 资产进 manifest —— 14→15
- `payment.acquirer`→`payment.provider` / `coupon`→`loyalty` / `stock.production.lot`→`stock.lot` —— 15→16
