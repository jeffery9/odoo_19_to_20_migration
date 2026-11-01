# 15→16 研究来源查证地图（work/15to16）

核查日期：2026-11-01。目标：锁定 Odoo **15.0 → 16.0** 真实破坏性变更，并严格划清版本作用域
（不属于 15→16 的改动一律排除，交后续技能处理）。

## 一、16.0 源码核实（GitHub `odoo/odoo` 分支 `16.0`）

| 文件 | 核实结论 | 作用域含义 |
|---|---|---|
| `odoo/release.py` | `version_info = (16, 0, 0, FINAL, 0, '')` | 确认 16.0；Python 地板未变（15/16 均 3.8/3.9/3.10） |
| `odoo/addons/base/models/ir_ui_view.py` | 第 82–96 行仍 `attrs = node.attrib.pop('attrs')` 并转 modifiers；第 237 行 `type` 选单含 `('tree','Tree')` | **`attrs`/`states` 在 16.0 仍有效**；`<tree>` 仍是合法视图类型 → 二者属 16→17/17→18，不在 15→16 |
| `odoo/models.py` | 第 1574 行 `def name_get`、第 1651 行 `def _name_search`、第 1472 行 `def user_has_groups`、第 3523 行 `def check_access_rights` 仍存在 | **这些 API 在 16.0 仍存在** → 移除属 17→18，不在 15→16 |
| `odoo/modules/module.py` | 第 280 行 `def get_resource_path(...)` 仍存在 | **`get_resource_path` 在 16.0 仍存在** → 移除属 16→17，不在 15→16 |
| `odoo/api.py` | `api.multi` 已不存在 | **`api.multi` 在 16.0 移除** → 15→16 需删除装饰器 |
| `odoo/upgrade_code` | 目录列举返回 404（模块不存在） | **16.0 无任何 codemod** → 15→16 全手工 + OpenUpgrade 做 DB 重命名 |
| `odoo/fields.py`（15.0 与 16.0） | 均无 `track_visibility` / `tracking` 关键字（机制在 `mail` mixin） | `track_visibility`→`tracking` 的替换以社区指南为准（见下） |

## 二、社区来源（框架级清单 + 结构差异）

| 来源 | 关键结论 | 可信度 |
|---|---|---|
| **OCU（Odoo Community Upgrade）《Migrate Odoo 15 to 16》** | 15→16 结构差异：14 模型改名、23 模块合并、42 字段改名、138 约束变更；`payment.acquirer`→`payment.provider`、`coupon`→`loyalty`、`ir_translation` 移除→JSONB、`stock.production.lot`→`stock.lot`、`account_analytic.group`→`account_analytic.plan`、`mail.channel.partner`→`mail.channel.member`、`account.tax.report`→`account.report`、`account.account.user_type_id`→`account_type`、`account_payment` 自动安装接管支付字段/视图/菜单 | CONFIRMED（结构统计 + 多源一致） |
| **oejia《Odoo 16 关键变化》** | 支付字段/方法改名明细：`acquirer_id`→`provider_id`、`provider`→`code`、`acquirer_reference`→`provider_reference`、`_handle_feedback_data`→`_handle_notification_data`（GitHub 文档 PR #1981） | CONFIRMED |
| **DeployMonkey《Migrate Odoo 15 to 16》** | `track_visibility`→`tracking=True`（"deprecated in v14, removed in v16"）、`@http.route(website=True)` 网站模块重构需复核、`group_expand` 看板分组、记录规则 `global` 行为变化、遗留 widget→Owl 2 持续迁移 | `track_visibility`=CONFIRMED（多指南一致）；其余为 `[verify]`（单一来源） |
| **Braincuber《Database Migration in Odoo》** | 提及 `@api.multi removed in v13+` | 与源码（16.0 api.py 无 api.multi）一致 |

## 三、与更早版本技能的作用域对账（避免重复/越界）

- 15→16 不含：视图 `attrs`/`states` 硬拒（16→17）、`<tree>`→`<list>`（17→18）、`name_get` 等移除（17→18）、
  `get_resource_path`→`file_path`（16→17）、Owl 3（19）、`web_editor` 拆分（19）、`res.groups` privilege / `ir.access.csv`（19/20）、
  `type='json'`→`jsonrpc`（18.1）、`group_operator`→`aggregator`（17.2）、SCSS 移除（晚于 17）。
- 15→16 独有：支付系统重构、优惠券→忠诚度、翻译表移除、批量模型/模块改名、`track_visibility`→`tracking`、`api.multi` 移除。

## 四、诚实标注汇总（见 VERIFY_TRACKER.md）

`[verify]`：网站 `website=True` 路由、记录规则 `global` 行为、`t-raw` 移除、`fields.Html` 精细化 sanitize、
遗留 widget→Owl 2 清理、PG 下限、自定义翻译脚本改写。
`[EE-verify]`：支付 EE 连接器改名、优惠券/礼品卡 EE 扩展、EE 安全微调。
