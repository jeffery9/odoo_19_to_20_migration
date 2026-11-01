# 15→16 待核实追踪表（work/15to16）

核查日期：2026-11-01。本文记录 15→16 交付物中标记为 `[verify]` / `[EE-verify]` 的项，
及已通过 16.0 源码核实、确认**排除**出 15→16 作用域的项（防止越界修改）。

## A. 已源码核实、确认"不在 15→16 作用域"的项（红线，勿改）

| 变更 | 16.0 源码证据 | 真实归属 |
|---|---|---|
| 视图 `attrs` / `states` 硬拒 | `ir_ui_view.py` L82–96 仍处理为 modifiers | 16→17（17.0） |
| `<tree>`→`<list>` | `ir_ui_view.py` L237 `('tree','Tree')` 仍合法 | 17→18（18.0） |
| `name_get` / `_name_search` / `check_access_rights` / `user_has_groups` / `check_recursion` 移除 | `models.py` 仍定义（L1574/L1651/L3523/L1472） | 17→18（18.0） |
| `get_resource_path` 移除 → `file_path` | `modules/module.py` L280 仍存在 | 16→17（17.0） |
| `type='color'` 字段类型移除 | `fields.py`（15.0/16.0）均无 `color` 类型类 | 早于 15（已不在 15 代码中使用） |

## B. `[verify]` 项（单一社区来源或来源分歧，待 16.0 实机/源码确认）

| # | 项 | 当前处理 | 建议核实方式 |
|---|---|---|---|
| V1 | `@http.route(website=True, ...)` 网站模块重构 | 标 `[verify]`，建议 16.0 实机复核路由 | 在 16.0 起服务 + `--dev=all`，访问自定义网站控制器，确认 `website=True` 路由解析 |
| V2 | 记录规则 `global` 属性行为变化（"适用于所有用户含超级用户"） | 标 `[verify]`，建议复核 `ir.rule` | 对照 16.0 `ir.rule` 计算逻辑，验证含 `global` 的自定义规则影响范围 |
| V3 | `t-raw` 指令在 16.0 移除 | 标 `[verify]`（未能对 16.0 `qweb.py` 源码核实——路径 404，目录重构） | 在 16.0 模板用 `t-raw` 触发，确认报错后改 `t-esc` |
| V4 | `fields.Html` 精细化 sanitize（`sanitize_tags`/`sanitize_attributes`/`sanitize_style`/`sanitize_formatted`） | 标 `[verify]`，建议显式设 `sanitize=False` 若依赖原始 HTML | 对照 16.0 `fields.Html` 定义确认参数名 |
| V5 | 遗留 widget→Owl 2 清理细节 | 标 `[verify]`，非硬断裂 | 对照 16.0 前端 bundle 确认 widget registry 弃用状态 |
| V6 | PostgreSQL 下限（12+ vs 13/14） | 标 `[verify]` | 对照 16.0 `odoo/sql_db.py` 版本校验 |
| V7 | 自定义 `ir_translation` 直读写脚本改写 | 标 `[verify]`（表移除已 CONFIRMED，改写方式待确认） | 在 16.0 用 `context={'lang':...}` 字段翻译机制重写 |

## C. `[EE-verify]` 项（Enterprise 专属，需对照 EE 16.0 树）

| # | 项 | 当前处理 |
|---|---|---|
| E1 | 支付 EE 连接器（`payment_*` EE 模块）改名 | 标 `[EE-verify]`，对照 EE 16.0 树复核 `payment.provider` 派生模型/方法 |
| E2 | 优惠券/礼品卡 EE 扩展（`loyalty` 派生） | 标 `[EE-verify]`，对照 EE 16.0 树复核 `loyalty.*` 派生模型 |
| E3 | EE 安全/权限微调 | 标 `[EE-verify]`，CE 层面无变化，EE 待核 |

## D. 修订 SOP

- 任何 `[verify]` 项被 16.0 实机/源码确认后：① 在 `Odoo_Migration_Cookbook_15_to_16.md` 把标记降级为 `CONFIRMED` 并补源码锚点；② 同步更新 `Odoo15to16Migration/references/*.md` 对应段落；③ 重跑 `work/15to16/check_cookbook_consistency.py` 确认无漂移；④ 在本文 B/C 表勾掉该项。
- 任何新发现需新增 `[verify]`：先入本文 B 表，再进交付物，禁止以确证语气陈述单一来源结论。
- 作用域红线（A 表）改动需先在 `MigrationKnowledgeForge/references/odoo-version-pairs.md` 的版本作用域纪律中修正，再回灌本技能。
