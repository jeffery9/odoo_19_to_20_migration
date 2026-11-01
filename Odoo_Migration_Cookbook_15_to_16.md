# Odoo 16.0 迁移烹饪书（15.0 → 16.0）

> **适用范围**：Odoo **15.0 → 16.0** 自定义插件（CE 与 EE）升级。
> **体例说明**：本烹饪书（Cookbook）为原创，无对应外部 PDF 底本，内容基于 OCA `maintainer-tools`《Migration to version 16.0》框架级清单（社区 wiki 与 GitHub 文档 PR #1981）、OCU（Odoo Community Upgrade）15→16 结构差异统计（模型/模块/字段改名映射）、以及 GitHub `odoo/odoo` 16.0 分支源码核实（`odoo/release.py` 的 `version_info=(16,0,0,...)`、`odoo/addons/base/models/ir_ui_view.py` 的 `attrs`/`states` 在 16.0 仍被处理（第 82–96 行）、`tree` 仍是合法视图类型（第 237 行）、`odoo/models.py` 的 `name_get`/`_name_search`/`check_access_rights`/`user_has_groups` 仍存在、`odoo/modules/module.py` 的 `get_resource_path` 仍存在、`odoo/api.py` 的 `api.multi` 已不存在、`odoo/upgrade_code` 在 16.0 返回 404）交叉核实。本书与同目录 `Odoo15to16Migration/` 的机器可读映射表（Skill）保持事实一致。
> **可信度标记**：`CONFIRMED` = 源码/官方 changelog 多源交叉核实；`[verify]` = 单一社区来源或来源间有分歧、待 16.0 实机/源码最终确认；`[EE-verify]` = Enterprise 专属、需对照 EE 16.0 树复核。
>
> **配套技能**：同目录 `Odoo15to16Migration/` 提供机器可读映射表与扫描器，含 `references/payment-loyalty.md`、`references/models-mapping.md`、`references/orm-api.md`、`references/views-qweb.md`、`references/security.md`、`references/upgrade-code.md` 与 `scripts/scan_addon.py`。本书为可读叙事，技能可被 agent 直接调用，两者事实一致。

---

## 第 0 章 · 导言

### 0.1 为什么是 15→16

与 18→19（"重底座"：ORM 包拆分 + Owl 3 + 安全模型重构）、17→18（"移除主导"：`name_get`/`tree→list` 等被删）、16→17（"视图语法革命"：`attrs`/`states` 硬拒）相比，**15→16 是一次"数据模型重命名 + 支付/优惠券系统重构"主导的迁移**：

- **支付系统重写（最高频、最易阻塞）**：`payment.acquirer` 模型整体改名为 `payment.provider`，连带字段 `acquirer_id`→`provider_id`、`provider`→`code`、`acquirer_reference`→`provider_reference`、方法 `_handle_feedback_data`→`_handle_notification_data` 等全部改名。任何引用支付模型的自定义代码、server action、domain、报表都会断。
- **优惠券引擎重建为忠诚度引擎**：`coupon` 模块整体改为 `loyalty`，`coupon.program`→`loyalty.program`、`coupon.reward`→`loyalty.reward`、`coupon.rule`→`loyalty.rule`、`coupon.coupon`→`loyalty.card`，且礼品卡并入忠诚度。
- **翻译存储重构**：`ir_translation` 表在 16.0 被移除，翻译值直接写入各模型的 JSONB 列。这是**数据库级**变更（由 OpenUpgrade / 官方升级服务处理），但自定义翻译相关代码需复核。
- **大量模块合并与模型改名**：`fetchmail`→`mail`、`pad`→`web_editor`、`account_analytic.group`→`account_analytic.plan`、`stock.production.lot`→`stock.lot`、`mail.channel.partner`→`mail.channel.member`、`account.tax.report`→`account.report` 等 14 个模型改名、23 个模块合并。
- **没有任何 `upgrade_code` codemod**：16.0 分支**不含 `odoo/upgrade_code/` 模块**（源码核实：该路径在 16.0 返回 404），所以 15→16 **全部靠人工映射 + 数据库迁移脚本**。

### 0.2 版本作用域纪律（最重要的一条）

> **变更归属于它首次出现的版本。** 不要把 16→17 / 17→18 / 18→19 / 19→20 才引入的破坏性变更误带进 15→16。

已被显式排除在 15→16 之外、属于**更晚版本**的改动——它们由对应技能处理：

| 变更 | 真实归属版本 | 说明 |
|---|---|---|
| 视图类型 `tree` → `list`（`<tree>` 硬拒） | **17→18（18.0）** | 15→16 中 `<tree>` **仍是合法视图类型**（16.0 源码 `ir_ui_view.py` 第 237 行 `type` 选单含 `('tree','Tree')`），**不要**在 15→16 改名 |
| 视图属性 `attrs` / `states` 硬拒 | **16→17（17.0）** | 15→16 中 `attrs`/`states` **仍被处理**（16.0 源码 `ir_ui_view.py` 第 82–96 行把它们转成 modifiers），**不要**在 15→16 改写 |
| `name_get` / `_name_search` / `check_access_rights` / `user_has_groups` / `check_recursion` / `inselect` 运算符**移除** | **17→18（18.0）** | 15→16 中这些 API **仍存在**（16.0 `models.py` 仍定义 `name_get` 第 1574 行、`user_has_groups` 第 1472 行、`check_access_rights` 第 3523 行等）；移除属 17→18 |
| `get_resource_path` 移除 → `file_path` | **16→17（17.0）** | 15→16 中 `get_resource_path` **仍存在**（`odoo/modules/module.py` 第 280 行），**不要**在 15→16 改写 |
| Owl 2 → Owl 3（`setup()` 强制化） | **19.0** | 15/16 均为 Owl 2，无需重写组件 |
| `web_editor` → `html_editor` / `html_builder` | **19.0** | 15/16 中 `web_editor` 仍在 |
| `res.groups` 的 `category_id`→`privilege_id` 重构、安全文件 `ir.model.access.csv`→`ir.access.csv` | **19.0 / 20.0** | 15→16 的 `res.groups` 与安全文件格式**不变** |
| `type='json'`→`jsonrpc`、字段 `group_operator`→`aggregator` | **17.2 / 18.1（Online 小版本）** | 15→16 不适用 |
| SCSS 编译移除 | **晚于 17.0** | 16.0 仍编译 SCSS |

**范围约定**：本书把"目标大版本 16"理解为 **16.0**。16.x 的 Online 小版本改动不纳入 15→16。每项变更都标出首次出现版本，便于核对作用域。

### 0.3 推荐工作流（详见第 11 章）

1. **数据库迁移**（OpenUpgrade 或官方升级服务）→ 2. **扫描（triage）** 自定义模块 → 3. **应用人工映射**（支付/优惠券/模型改名）→ 4. **校验**（`-u` + 测试 + 清 `DeprecationWarning`）→ 5. **出报告**。

> 15→16 是"数据库结构迁移 + 代码映射"双线：数据库侧靠 OpenUpgrade（自动化重命名模型/字段/模块），代码侧靠本书映射 + 随附扫描器识别。

---

## 第 1 章 · 框架与运行时

### 1.1 Python 3.8 / 3.9 / 3.10 地板 — CONFIRMED

Odoo 16.0 要求 **Python 3.8、3.9 或 3.10**（15.0 同样支持 3.8/3.9/3.10，故 Python 地板**未变**——15→16 通常无需升级 Python，与 16→17（要求 3.10+）不同）。源码核实：16.0 `release.py`（`version_info = (16, 0, 0, FINAL, 0, '')`）。

- `requirements.txt` 锁定依赖下限（Werkzeug、lxml、psycopg2、MarkupSafe 等）。升级前按目标 Python 小版本对齐依赖。

### 1.2 数据库与依赖

- **PostgreSQL 12+**：16.0 需 PostgreSQL 12 或以上（`[verify]`：具体下限以 `odoo/sql_db.py` 的版本校验为准；社区另有报告 13）。升级前确认数据库版本。
- **Werkzeug 2.x**：16.0 锁定 Werkzeug 2.x（15 同代）。若 15 代码用了 Werkzeug 1.x 专属 API（`werkzeug.contrib` 已移除、`werkzeug.urls` 位置变动），控制器可能报错（`[verify]`，与 16→17 同性质但 16 地板已明确）。

### 1.3 没有任何 `upgrade_code` codemod — CONFIRMED

16.0 分支**没有 `odoo/upgrade_code/` 模块**（GitHub 目录列举 + 该路径在 16.0 返回 404）。因此：

- 不存在 `odoo-bin upgrade_code --from 15.0` 这类自动化改写工具对 15→16 生效。
- 代码级映射（支付/优惠券/模型改名）靠本书第 2–8 章的人工映射 + 随附扫描器识别；**数据库级**重命名（模型/字段/模块）由 OpenUpgrade 的 16.0 脚本自动完成。
- 数据/结构升级脚本放在各模块的 `migrations/16.0/` 目录（`pre-` / `post-` / `end-` 钩子），属手动编写，见第 10 章。

---

## 第 2 章 · 支付系统重构（头号硬断裂）

### 2.1 `payment.acquirer` → `payment.provider` — CONFIRMED（多源）

16.0 将支付提供商模型从 `payment.acquirer` 重命名为 `payment.provider`，并连带重命名字段与方法。这是 15→16 **最易阻塞自定义模块**的改动（OCU、oejia 技术分享、GitHub 文档 PR #1981 一致确认）。

```python
# 15
provider = self.env['payment.acquirer'].browse(acquirer_id)
tx = self.env['payment.transaction'].search([('acquirer_id', '=', acq_id)])
# 16
provider = self.env['payment.provider'].browse(provider_id)
tx = self.env['payment.transaction'].search([('provider_id', '=', prov_id)])
```

**连带字段/方法改名**（oejia 技术分享）：

| Odoo 15 | Odoo 16 | 说明 |
|---|---|---|
| `payment.acquirer` | `payment.provider` | 模型改名 |
| `acquirer_id` | `provider_id` | 字段改名（transaction / token / 各业务单据） |
| `payment.acquirer` 字段 `provider`（值如 `'stripe'`） | `code` | 原 `provider` 字段改名 `code`（注意：旧 `provider` 是字段值来源，新 `code` 是字段名） |
| `acquirer_reference` | `provider_reference` | transaction 字段 |
| `acquirer_ref` | `provider_ref` | token 字段 |
| `account.payment.method.line.payment_acquirer_id` | `payment_provider_id` |  |
| `_handle_feedback_data` | `_handle_notification_data` | 支付连接器方法 |
| `_process_feedback_data` | `_process_notification_data` | 支付连接器方法 |

> **manifest `depends`**：若模块 `depends` 含 `payment` 且直接 import `payment.acquirer` 相关，全部改用 `payment.provider`。原有 `payment` 模块的支付字段/视图/菜单在 16.0 部分迁移到新自动安装的 `account_payment` 模块（OCU：23 模块合并之一，`account_payment` 自动安装接管支付字段/视图/菜单）——引用旧位置需更新。

### 2.2 支付相关代码改写清单

- 所有 `env['payment.acquirer']` / `env.ref('payment.payment_acquirer_...')` → `payment.provider` / `payment.payment_provider_...`。
- 所有 domain / server action / 报表中 `acquirer_id` → `provider_id`、`acquirer_reference` → `provider_reference`。
- 自定义支付连接器（继承 `payment.acquirer` 的模型）改为继承 `payment.provider`，方法 `_handle_feedback_data` → `_handle_notification_data`。
- `[EE-verify]`：Enterprise 支付连接器（`payment_*` EE 模块）的改名需对照 EE 16.0 树复核。

---

## 第 3 章 · 优惠券 → 忠诚度 + 模块/模型改名

### 3.1 `coupon` → `loyalty` — CONFIRMED（OCU）

16.0 用统一的**忠诚度引擎**取代独立优惠券引擎，并吸收礼品卡与电子钱包：

| Odoo 15 | Odoo 16 | 说明 |
|---|---|---|
| `coupon.coupon` | `loyalty.card` | 模型改名 |
| `coupon.program` | `loyalty.program` | 模型改名 |
| `coupon.reward` | `loyalty.reward` | 模型改名 |
| `coupon.rule` | `loyalty.rule` | 模型改名 |
| `coupon` / `sale_coupon` / `sale_coupon_delivery` / `website_sale_coupon` / `website_sale_coupon_delivery` / `pos_sale_gift_card` / `pos_coupon` / `pos_gift_card` | `loyalty` / `sale_loyalty` / `sale_loyalty_delivery` / `website_sale_loyalty` / `website_sale_loyalty_delivery` / `pos_sale_loyalty` / `pos_loyalty` | 模块改名/合并 |

- 自定义继承 `coupon.*` 模型的代码改为 `loyalty.*`；`coupon.program` 的 `promo_applicability`→`applies_on`、`maximum_use_number`→`max_usage`、`discount_percentage`→`discount`、`discount_type`→`discount_mode`（loyalty 家族字段改名，OCU）需一并更新。
- `[EE-verify]`：EE 优惠券/礼品卡相关扩展需对照 EE 16.0 树。

### 3.2 其他模块合并与模型改名 — CONFIRMED（OCU）

| Odoo 15 | Odoo 16 | 类型 |
|---|---|---|
| `fetchmail` / `fetchmail_gmail` / `fetchmail_outlook` | `mail` / `google_gmail` / `microsoft_outlook` | 模块合并 |
| `pad` / `pad_project` | `web_editor` / `project`（pad 功能并入富文本编辑器） | 模块合并 |
| `account_analytic.group` | `account_analytic.plan` | 模型改名（新分析计划系统） |
| `stock.production.lot` | `stock.lot` | 模型改名 |
| `mail.channel.partner` | `mail.channel.member` | 模型改名 |
| `account.tax.report` / `account.tax.report.line` | `account.report` / `account.report.line` | 模型改名（税务报告引擎重建） |
| `account.account(.template).user_type_id` | `account_type`（selection 字段） | 字段改名（会计科目类型） |
| `project.account` / `sale_project_account` 等 | 合并入 `sale_project` / `project` | 模块合并 |
| 6 个 EDI 子模块 | `account_edi_ubl_cii` | 模块合并 |

> 数据库侧的模型/字段重命名由 OpenUpgrade 16.0 脚本自动完成（含 domain、filter、server action 中的引用更新，OCU 确认）。**代码侧**需在自定义模块里把 `env[...]`、import、XML `ref`、inherit 的 `_inherit`/`_name` 同步改名。

---

## 第 4 章 · 翻译存储重构（ir_translation → JSONB）

### 4.1 `ir_translation` 表移除 — CONFIRMED（OCU）

16.0 **移除 `ir_translation` 表**，翻译值直接写入各模型的 **JSONB 列**（与每个翻译字段同行）。这是数据库级变更：

- OpenUpgrade / 官方升级服务会自动把 `ir_translation` 行迁移到对应模型的 JSONB 翻译列。
- 自定义模块若**直接读写 `ir_translation` 表**（如自定义翻译导入/导出、报表翻译逻辑），需改写——改为操作字段的翻译值（通过 `odoo.tools.translate` 或字段的 `context={'lang': ...}` 机制），不再直接 `INSERT/UPDATE ir_translation`。
- `[verify]`：自定义翻译同步脚本（如对接外部 TM 系统）的具体改写方式，以 16.0 实机为准。

---

## 第 5 章 · ORM 与 Python API

### 5.1 `track_visibility` 移除 → `tracking` — CONFIRMED（社区，DeployMonkey + OCA 16 指南）

`track_visibility` 字段属性在 16.0 被移除（DeployMonkey："deprecated in v14, removed in v16"），改用 `tracking` 属性：

```python
# 15
name = fields.Char(string="Name", track_visibility='always')
state = fields.Selection(track_visibility='onchange')

# 16
name = fields.Char(string="Name", tracking=True)
state = fields.Selection(tracking=True)          # 或 tracking='field_name' 指定触发字段
```

> **作用域守卫**：源码核实 `odoo/fields.py`（16.0）与 `odoo/models.py`（16.0）均未直接定义 `track_visibility`/`tracking` 关键字（该机制由 `mail` 模块 mixin 处理，故 16.0 fields.py 不含 'track' 字样）；但多份社区迁移指南一致确认 `track_visibility` 在 16.0 不可用、`tracking` 为替代。若你的 15 模块仍用 `track_visibility`，**必须**改为 `tracking`。列为 `CONFIRMED`（社区多源），机制位置以 `mail` 模块为准。

### 5.2 `api.multi` 已移除 — CONFIRMED（源码核实）

`api.multi` 在 16.0 `odoo/api.py` 中**已不存在**（自 13.0 起弃用为 no-op、16.0 移除）。任何仍 `from odoo import api; @api.multi` 的 15 代码在 16.0 会 `ImportError`：

```python
# 15（旧，16 会 ImportError）
@api.multi
def action_do(self): ...

# 16（多记录方法默认即多记录，去掉装饰器）
def action_do(self): ...
```

> 15 代码若沿用 `@api.multi` 多因历史遗留；15→16 直接删除该装饰器即可（方法默认按多记录处理）。低优先级清理项，但会阻断启动，须修。

### 5.3 选择字段 `group_expand` — CONFIRMED（社区，DeployMonkey）

16.0 选择字段支持 `group_expand` 参数，用于看板分组时展开缺失的选项：

```python
state = fields.Selection([...], group_expand='_expand_states')
def _expand_states(self, states, domain, order): ...
```

这是**新增能力**（非破坏性）；若 15 看板分组行为异常（DeployMonkey 报告"Kanban views empty: Column grouping behavior changed"），可加 `group_expand` 修复。

### 5.4 `[verify]` 控制器 `website=True` 路由变化

DeployMonkey 指出 16.0 `website` 模块重构，`@http.route(website=True, ...)` 的网站参数需复核。若自定义网站控制器用 `website=True`，在 16.0 实机验证路由是否仍解析（`[verify]`：来源单一，未做 16.0 源码级确认；旧 `website` 模块结构在 16 调整）。

### 5.5 15→16 **未移除**的 ORM API（版本作用域提醒）

下列 API 在 15→16 **仍然存在**（它们的"移除"属于 17→18，勿在 15→16 提前改）：

- `name_get` / `_name_search` / `check_access_rights` / `check_access_rule` / `user_has_groups` / `check_recursion` — 16 中仍可用（16.0 `models.py` 仍定义）；17→18 才移除。
- `get_resource_path` — 16 中仍存在（`odoo/modules/module.py` 第 280 行）；16→17 才移除。
- `attrs` / `states` 视图属性 — 16 中仍被处理（16.0 `ir_ui_view.py` 第 82–96 行）；16→17 才硬拒。
- `<tree>` 视图类型 — 16 中仍合法（16.0 `ir_ui_view.py` 第 237 行）；17→18 才改 `list`。

> **红线**：15→16 不要动上述 API；它们的迁移由 16→17 / 17→18 技能统一负责，避免重复/越界修改。

---

## 第 6 章 · 视图与 QWeb 前端

### 6.1 视图属性在 15→16 **基本不变**

与 16→17（`attrs`/`states` 硬拒）不同，**15→16 的视图 XML 语法几乎不变**：

- `attrs` / `states` 在 16.0 仍有效（见第 5.5 章源码核实）——**不要**在 15→16 改写它们；那是 16→17 的事。
- `<tree>` 在 16.0 仍合法——**不要**改为 `<list>`；那是 17→18 的事。
- 列表字段 `invisible="1"` → `column_invisible="1"` 属 **16→17（17.0）**，不在 15→16 范围（见 16→17 烹饪书第 2.2 章）。

### 6.2 `[verify]` `t-raw` 移除 / `t-esc` 现状

`t-raw` 指令在 16.0 已被移除（此前 14.0 弃用），改用 `t-esc`（安全转义）或 `t-out`（19.0 才引入的 `t-esc` 继任者）。若 15 代码仍用 `t-raw`，改为 `t-esc`（`[verify]`：未能对 16.0 `odoo/tools/qweb.py` 做源码级核实——该路径在 16.0 返回 404，目录结构变更；以社区共识为准）。

### 6.3 `[verify]` `html` 字段精细化 sanitize

16.0 `fields.Html` 在原有 `sanitize=True/False` 基础上细化出 `sanitize_tags` / `sanitize_attributes` / `sanitize_style` / `sanitize_formatted` 选项（默认仍净化）。若自定义 `html` 字段依赖未净化的原始 HTML，需显式设 `sanitize=False` 或精细化参数（`[verify]`，未做 16.0 源码级确认）。

### 6.4 Owl 2 与遗留组件（无版本切换）

15 与 16 **均为 Owl 2**（Owl 2 自 15.0 引入），15→16 **无 Owl 版本切换**。但 DeployMonkey 提示 16.0 持续从遗留 widget 迁移到 Owl 2：

- 遗留 widget registry 仍可用但弃用；新组件应继承 `@odoo/owl` 的 `Component`。
- 服务注入取代旧 `require()` 模式；资源打包方式变化——核对模块 `__manifest__.py` 的 `assets` 声明（`[verify]`：Owl 2 写法细节以 16.0 前端实机为准，非 15→16 硬断裂）。

---

## 第 7 章 · 安全与 res.groups（15→16 基本不变）

> **关键结论**：15→16 的**安全文件格式与 `res.groups` 模型都不变**。以下仅在"清理 15 代码"时相关，切勿套用 19→20 的 `privilege_id` / `ir.access.csv` 改动（那是 18→19 之后的事）。

- `security/ir.model.access.csv` 列格式**不变**（`perm_read/perm_write/perm_create/perm_unlink`）。
- `res.groups.category_id` / `groups_id` / `users` 字段**不变**。
- `[verify]` 记录规则 `global` 属性行为：DeployMonkey 称 16.0 中 `global` 属性"现在意味着规则适用于所有用户（含超级用户）"。若自定义 `ir.rule` 用了 `global`，在 16.0 实机复核其影响范围——属 `[verify]`（单一社区来源）。
- `[EE-verify]`：Enterprise 专属安全/权限行为在 15→16 若有微调，需对照 EE 16.0 树复核；CE 层面无变化。

---

## 第 8 章 · 模块 / 模型 / 字段映射（15→16 总表）

> OCU 统计：15→16 共 **14 个模型改名、23 个模块合并、42 个字段改名**、138 个约束变更。数据库侧重命名由 OpenUpgrade 自动完成；下表聚焦**自定义模块代码需同步改名**的框架级/高频项。

### 8.1 高频模型/字段改名（自定义代码必改）

| Odoo 15 | Odoo 16 | 版本 | 来源 |
|---|---|---|---|
| `payment.acquirer` | `payment.provider` | 16.0 | oejia / OCU / PR #1981 |
| `acquirer_id` | `provider_id` | 16.0 | oejia |
| `acquirer_reference` | `provider_reference` | 16.0 | oejia |
| `acquirer_ref` | `provider_ref` | 16.0 | OCU |
| `payment.acquirer.provider`（字段值） | `code` | 16.0 | oejia |
| `_handle_feedback_data` | `_handle_notification_data` | 16.0 | oejia |
| `coupon.program` | `loyalty.program` | 16.0 | OCU |
| `coupon.reward` | `loyalty.reward` | 16.0 | OCU |
| `coupon.rule` | `loyalty.rule` | 16.0 | OCU |
| `coupon.coupon` | `loyalty.card` | 16.0 | OCU |
| `account_analytic.group` | `account_analytic.plan` | 16.0 | OCU |
| `stock.production.lot` | `stock.lot` | 16.0 | OCU |
| `mail.channel.partner` | `mail.channel.member` | 16.0 | OCU |
| `account.tax.report` | `account.report` | 16.0 | OCU |
| `account.tax.report.line` | `account.report.line` | 16.0 | OCU |
| `account.account.user_type_id` | `account_type` | 16.0 | OCU |
| `track_visibility='always'` | `tracking=True` | 16.0 | DeployMonkey + OCA |
| `@api.multi` 装饰器 | 删除装饰器（方法默认多记录） | 16.0 | 源码核实（api.py 无 api.multi） |
| `ir_translation` 表 | 移除 → JSONB 翻译列 | 16.0 | OCU |

### 8.2 模块 `depends` 改名（manifest）

| 15 `depends` | 16 `depends` | 说明 |
|---|---|---|
| `coupon` / `sale_coupon` / `website_sale_coupon` | `loyalty` / `sale_loyalty` / `website_sale_loyalty` | 优惠券→忠诚度 |
| `fetchmail` | `mail`（或 `google_gmail`/`microsoft_outlook`） | 模块合并 |
| `pad` | `web_editor` | 模块合并 |
| `payment` 的支付字段/视图 | 部分移至 `account_payment`（自动安装） | 支付字段迁移 |

### 8.3 症状 → 修复索引

| 16 安装/运行时症状 | 可能原因 | 修复锚点 |
|---|---|---|
| `Model 'payment.acquirer' is not available` | 仍引用旧支付模型 | 第 2 章 |
| domain 报 `acquirer_id` 不存在 | 字段改名 `provider_id` | 第 2.1 章 |
| 支付回调 404 / 方法不存在 | `_handle_feedback_data`→`_handle_notification_data` | 第 2.1 章 |
| `Model 'coupon.program' is not available` | 优惠券→忠诚度 | 第 3.1 章 |
| 翻译丢失 / 自定义翻译脚本报错 | `ir_translation` 已移除 | 第 4 章 |
| `TypeError: track_visibility` / 显示名不追踪 | `track_visibility`→`tracking` | 第 5.1 章 |
| `ImportError: cannot import name 'multi' from 'odoo.api'` | `@api.multi` 删除 | 第 5.2 章 |
| 看板分组缺列 | 加 `group_expand` | 第 5.3 章 |
| 继承 `stock.production.lot` 报错 | → `stock.lot` | 第 3.2 章 |
| 发票科目类型不对 | `user_type_id`→`account_type` | 第 3.2 章 |

---

## 第 9 章 · 缓存 / SQL、字段与域

### 9.1 SQL 安全拼接 — CONFIRMED（16.0 沿用）

`SQL(...)` 包装对象在 16.0 尚未引入（17.0 才加，见 16→17 烹饪书第 7.1 章）。16.0 沿用老式 `%s` 参数化 + `cursor.execute(sql, params)`；务必参数化，绝不拼接 f-string，避免注入。

### 9.2 字段与域

- `_sql_constraints` 在 16.0 **完全正常**，无需改动。
- 非存储 related 字段搜索：16.0 沿用 15 行为（18 起改为直接抛异常），见 17→18 烹饪书。
- `ondelete='cascade'` 在 required m2o 的告警属更晚版本，15→16 无此变化。
- `Command`（来自 `odoo.fields`）在 15.0 已引入（`Command.create`/`Command.update`/`Command.link` 等），用于 `create`/`write` 的 one2many/many2many 指令式写法——15→16 已是推荐写法，**非新增**，可顺势采用但非必须。

### 9.3 缓存失效 API

`invalidate_cache` / `flush` 在 16.0 沿用；细粒度 `invalidate_recordset`/`flush_recordset`（17.0 推荐）尚未引入。15→16 无强制变更。

---

## 第 10 章 · 没有 codemod：数据库迁移 + 手动代码映射

### 10.1 现实：16.0 无 `upgrade_code`

15→16 **不存在** `odoo-bin upgrade_code` 自动化改写（16.0 分支无 `odoo/upgrade_code/` 模块，源码核实）。因此：

- **数据库结构迁移靠 OpenUpgrade（社区）或官方升级服务（Enterprise）**：它们执行 16.0 脚本，自动重命名模型/字段/模块、迁移 `ir_translation`→JSONB、合并模块、应用新约束。
- **代码级映射靠本书 + 随附扫描器**：支付/优惠券/模型改名的 `env[...]`/import/XML `ref`/`_inherit` 需在源码里手工改。
- 自定义数据迁移脚本放各模块 **`migrations/16.0/`** 目录：
  - `pre-16.0.py` / `post-16.0.py` / `end-16.0.py`（接收 `cr` 或 `env`）。
  - 例如：把自定义表里引用 `acquirer_id` 的外键列改名、把 `coupon.*` 相关自定义数据映射到 `loyalty.*`。

### 10.2 哪些必须手工（代码侧）

| 改动 | 是否 codemod | 处理 |
|---|---|---|
| `payment.acquirer`→`payment.provider` + 字段/方法改名 | 否（数据库侧 OpenUpgrade 自动；代码侧手工） | 第 2 章 |
| `coupon`→`loyalty` + 模型改名 | 否（同上） | 第 3.1 章 |
| 其他模型/模块改名（`stock.lot` 等） | 否（OpenUpgrade 自动 DB；代码侧手工） | 第 3.2 章 |
| `ir_translation` 直接读写代码 | 否（手工） | 第 4 章 |
| `track_visibility`→`tracking` | 否（手工） | 第 5.1 章 |
| `@api.multi` 删除 | 否（手工） | 第 5.2 章 |
| `website=True` 路由复核 | 否（手工 `[verify]`） | 第 5.4 章 |

### 10.3 Scanner 契约

随附的 `Odoo15to16Migration/scripts/scan_addon.py`（按 15→16 模式定制）标记发现项并打印 16.0 替换：

```bash
python3 Odoo15to16Migration/scripts/scan_addon.py /path/to/addons --addon my_module --json
# 退出码 1 = 有发现项
```

### 10.4 写自己的 `migrations/16.0/` 脚本

要新增数据迁移，在模块内 `migrations/16.0/` 下放 `pre-`/`post-`/`end-` 脚本（接收 `cr` 或 `env`）。每个脚本单一职责、幂等；提交结果 `git diff` 时附上相关 `references/*.md` 的锚点。

---

## 第 11 章 · 迁移实战清单

### 11.1 Grep 速查（pattern → 动作 → 见章节）

```
payment.acquirer                  → payment.provider（第 2 章）
acquirer_id                       → provider_id（第 2.1 章）
acquirer_reference                → provider_reference（第 2.1 章）
acquirer_ref                      → provider_ref（第 2.1 章）
_handle_feedback_data             → _handle_notification_data（第 2.1 章）
_handle_notification_data         → 已是 16（第 2.1 章）
coupon.program / coupon.reward / coupon.rule / coupon.coupon → loyalty.*（第 3.1 章）
depends: ['coupon']               → depends: ['loyalty']（第 8.2 章）
stock.production.lot              → stock.lot（第 3.2 章）
account_analytic.group            → account_analytic.plan（第 3.2 章）
mail.channel.partner              → mail.channel.member（第 3.2 章）
account.tax.report                → account.report（第 3.2 章）
user_type_id                      → account_type（第 3.2 章）
track_visibility=                → tracking=True（第 5.1 章）
@api.multi                        → 删除装饰器（第 5.2 章）
ir_translation                    → 改写（用字段翻译/JSONB）（第 4 章）
# 以下【不要】在 15→16 改（属 16→17 / 更晚版本，见 0.2 章）：
attrs="  / states="              → 15→16 仍有效，勿动（16→17 才硬拒，第 5.5 章）
<tree                            → 15→16 仍合法，勿改 <list（17→18 才改，第 5.5 章）
get_resource_path(               → 15→16 仍存在，勿动（16→17 才移除，第 5.5 章）
name_get( / user_has_groups( / check_recursion( → 15→16 仍存在，留待 17→18（第 5.5 章）
```

### 11.2 端到端工作流

1. **数据库迁移**：用 OpenUpgrade（社区）或官方升级服务（Enterprise）对 v15 库跑 16.0 迁移——自动完成模型/字段/模块改名、`ir_translation`→JSONB、模块合并、约束应用。
2. **Triage（扫描）**：`python3 Odoo15to16Migration/scripts/scan_addon.py /path/to/addons`——按文件分组列出发现项、行号、16.0 替换。
3. **人工映射**：对 scanner 标出的项，套用对应章节替换（支付 → 第 2 章；优惠券 → 第 3.1 章；模型改名 → 第 3.2 章；翻译 → 第 4 章；ORM/API → 第 5 章）。**注意红线**：不要越界改 16→17 才处理的 API（见第 5.5 章）。
4. **数据迁移脚本**：在模块 `migrations/16.0/` 放 `pre-`/`post-`/`end-` 脚本处理库内自定义数据（如外键列改名、coupon→loyalty 数据映射）。
5. **校验**：重跑 scanner（期望 0 发现）；`odoo-bin -u <module> --test-tags /<module>`；以 `--dev=all` 启动清掉每个 `DeprecationWarning`；修 `Model not available` / `ImportError` / `TypeError`。
6. **报告**：逐模块汇总——人工编辑（附所用章节锚点）、剩余 `[verify]`/`[EE-verify]` 项、测试状态。

---

## 溯源附录（Provenance）

- **OCU（Odoo Community Upgrade）《Migrate Odoo 15 to 16》**：15→16 结构差异统计（14 模型改名、23 模块合并、42 字段改名、138 约束变更）；`payment.acquirer`→`payment.provider`、`coupon`→`loyalty`、`ir_translation`→JSONB、`account.account.user_type_id`→`account_type`、`stock.production.lot`→`stock.lot`、`mail.channel.partner`→`mail.channel.member`、`account_analytic.group`→`account_analytic.plan`、`account.tax.report`→`account.report`、`fetchmail`→`mail`、`pad`→`web_editor`、`account_payment` 自动安装。
- **oejia 技术分享《Odoo 16 关键变化》**：`payment.acquirer`→`payment.provider` 字段/方法改名明细（`acquirer_id`→`provider_id`、`provider`→`code`、`acquirer_reference`→`provider_reference`、`_handle_feedback_data`→`_handle_notification_data`，GitHub 文档 PR #1981）。
- **DeployMonkey《Migrate Odoo 15 to 16》**：`track_visibility`→`tracking=True`（"deprecated in v14, removed in v16"）、`website=True` 路由复核、`group_expand` 看板分组、记录规则 `global` 行为、遗留 widget→Owl 2 持续迁移、`column_invisible` 误归（本书按 OCA 16/17 指南将 `column_invisible` 归 16→17，见 6.1 章）。
- **GitHub 16.0 源码核实**：`odoo/release.py`（`version_info=(16,0,0,FINAL,0,'')`）；`odoo/addons/base/models/ir_ui_view.py`（第 82–96 行仍处理 `attrs`/`states` 为 modifiers；第 237 行 `tree` 仍是合法视图类型）；`odoo/models.py`（`name_get` 第 1574 行、`_name_search` 第 1651 行、`user_has_groups` 第 1472 行、`check_access_rights` 第 3523 行仍存在）；`odoo/modules/module.py`（`get_resource_path` 第 280 行仍存在）；`odoo/api.py`（`api.multi` 已不存在）；`odoo/upgrade_code`（16.0 返回 404，无 codemod）；`odoo/fields.py`（15.0/16.0 均无 `track_visibility`/`tracking` 关键字——机制在 `mail` 模块，社区确认 `track_visibility` 16.0 移除）。
- **核查日期**：2026-11-01。
- **诚实标注**：`[verify]` 项（网站 `website=True` 路由、记录规则 `global`、t-raw 移除、html 精细化 sanitize、遗留 widget 清理、PG 下限、自定义翻译脚本改写）源自单一社区来源或来源间分歧，已注明待 16.0 实机/源码最终确认，未以确证语气陈述。`[EE-verify]` 项（支付 EE 连接器、优惠券/礼品卡 EE 扩展、EE 安全微调）需对照 EE 16.0 树复核。

---

*本烹饪书（单卷）覆盖 15.0 → 16.0 的支付系统重构（payment.acquirer→provider + 字段/方法改名）、优惠券→忠诚度引擎、翻译表移除（ir_translation→JSONB）、模块/模型/字段批量改名（stock.lot、account_analytic.plan、mail.channel.member 等）、以及 track_visibility→tracking / api.multi 移除的 Python API 调整。机器可读的映射表与扫描器见同目录 `Odoo15to16Migration/`。下一跳 16→17（attrs/states 硬拒、tree 仍合法）由对应技能处理。*
