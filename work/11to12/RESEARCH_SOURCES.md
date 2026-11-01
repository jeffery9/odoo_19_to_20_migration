# 11→12 研究来源与源码核实地图

> 本文件记录 11→12 每条破坏性变更的溯源与核实状态，供修订时复核。

## 已核实（CONFIRMED）

| 变更 | 来源 | 核实方式 |
|---|---|---|
| `@api.one` 装饰器移除 | OCA 12.0 指南 + CSDN 代码规范 | 多社区一致；12.0 `odoo/api.py` 不再有 `api.one`（方法默认多记录） |
| `fields.Date`/`Datetime` 运行时对象化，`from_string` 移除 | OCA 12.0 + 掘金 | 12.0 引入 `to_date`/`to_datetime`；`from_string` 删除 |
| `@api.model_create_multi` 12.0 新增 | 掘金 | 覆写 `create` 需加该装饰器 |
| `_parent_store`：`parent_left`/`parent_right` → `parent_path` | OCA 12.0 | 12.0 用 `parent_path` 字符串路径 |
| `ir.actions.act_window.view` 模型移除 | OCA 12.0 | 视图绑定改动作 `view_ids` |
| `do_notify`/`do_warning` 移除 | OCA 12.0 + Oejia | 改 `UserError`/`message_post` |
| `t-field-options` → `t-options` | OCA 12.0 | QWeb 属性改名 |
| 11.0 已要求 Python 3（无 py2→3 断裂） | Odoo 发布说明 | 11→12 非 Python 升级版本 |
| 12.0 无 `odoo/upgrade_code/` 模块 | odoo/odoo 仓库核查 | codemod 引擎 18.0 才出现 |

## 待核实（[verify] / [EE-verify]）

| 变更 | 状态 | 备注 |
|---|---|---|
| 前端 Bootstrap 4 / jQuery 3 版本归属 | [verify] | 12.0 沿用，更大跃进在 13/14；无权威 12.0 前端清单 |
| `Binary` 字段默认存 `ir.attachment` 时机 | [verify] | 社区称 13.0 才默认改附件；11→12 维持原状（待 12.0 源码确认） |
| EE 安全微调 | [EE-verify] | 企业版 12.0 group 继承链若有微调需对照 EE 树；社区版无变化 |

## 版本作用域红线（已对照确认不属于 11→12）

- `account.invoice`→`account.move` —— 12→13
- `customer`/`supplier`→`customer_rank`/`supplier_rank` —— 12→13
- `src_model`→`binding_model` —— 12→13
- `attrs`/`states` 硬拒 —— 16→17
- `<tree>`→`<list>` —— 17→18
- `name_get` 移除 —— 17→18
- `get_resource_path`→`file_path` —— 16→17
- `payment.acquirer`→`payment.provider` —— 15→16
- `t-raw` 移除 / `ir.model*` 移除 / 资产进 manifest —— 14→15
