# 14→15 研究来源与源码核实地图

> 本文件记录 14→15 每条破坏性变更的溯源与核实状态，供修订时复核。

## 已核实（CONFIRMED）

| 变更 | 来源 | 核实方式 |
|---|---|---|
| QWeb `t-raw` 移除 → `t-out`/`t-esc` | OCA 15.0 + odoo/odoo 01875541b1a8 | `t-out` 等价于旧 `t-raw`（不转义），`t-esc` HTML 转义；可信 HTML 包 `markupsafe.Markup` |
| `ir.model*` 对象直接访问移除（`ir.model`/`ir.model.fields`/`ir.model.data`） | OCA 15.0 + odoo/odoo#69120 | 改用 `sudo()` 或模型自身 API（`_fields`/`_xmlid_lookup`/`_get_id`）；与 13→14 的 `ir.actions.*` 移除是不同对象 |
| `mail.template` Jinja → QWeb 正文 + `inline_template` | OCA 15.0 + odoo/odoo#77074 | 正文 `type="qweb"` 用 `t-out`/`t-esc`；subject/email_from/email_to 用 `{{ }}` 替代 `${ }` |
| ES 模块须改名 `*.esm.js` | OCA 15.0 官方指南 | 任何带 `/** @odoo-module **/` 的 JS 必须 `.esm.js` 后缀 |
| 资产声明移入 `__manifest__.py` `assets` 键（`qweb` 键移除） | OCA 15.0 官方指南 | JS/SCSS 从 XML 模板移入 `assets`（`web.assets_qweb`/`web.assets_backend` 等），路径仓库相对 |
| `SavepointCase` 别名移除 → `TransactionCase` | OCA 15.0 + odoo/odoo#62031 | 测试基类改用 `TransactionCase` |
| `Environment.manage()` 不再需要 | OCA 15.0 官方指南 | 直接 `Environment(cr, uid, context)` |
| 15.0 无 `odoo/upgrade_code/` 模块 | odoo/odoo 仓库核查 | codemod 引擎 18.0 才出现；14→15 全部人工 |
| 安全文件与 `res.groups` 14→15 不变 | OCA 15.0 官方指南 | 不套用 18→19 `res.groups` 权限改造 |

## 待核实（[verify]）

| 变更 | 状态 | 备注 |
|---|---|---|
| `subtype` → `subtype_xmlid` | [verify] | 仅单一社区源且存在分歧；使用前需确认目标为 xmlid |
| EE 前端资产细节（企业版 15.0 资产分包） | [EE-verify] | 对照 EE 15.0 树复核社区版结论可复用性 |

## 版本作用域红线（已对照确认不属于 14→15）

- `account.invoice`→`account.move` / `customer_rank` / `binding_view_types` —— 12→13
- `ir.actions.*` 访问移除 / `invisible`/`readonly` 动态表达式 → `attrs` —— 13→14
- `payment.acquirer`→`payment.provider` / `coupon`→`loyalty` / `stock.production.lot`→`stock.lot` / `ir_translation`→JSONB —— 15→16
- `attrs`/`states` 硬拒 —— 16→17
- `<tree>`→`<list>` / `name_get` 移除 —— 17→18
- `track_visibility`→`tracking` —— 12→13（常被误归 14→15）
- `res.groups` 权限改造 / `ir.access.csv` —— 18→19、19→20
