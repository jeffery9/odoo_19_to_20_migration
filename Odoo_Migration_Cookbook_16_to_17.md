# Odoo 17.0 迁移烹饪书（16.0 → 17.0）

> **适用范围**：Odoo **16.0 → 17.0** 自定义插件（CE 与 EE）升级。
> **体例说明**：本烹饪书（Cookbook）为原创，无对应外部 PDF 底本，内容基于 OCA `maintainer-tools`《Migration to version 17.0》的框架级清单（PR #104741、#106425、#122085、#135607、b4a7996、daf05d48 等）、GitHub `odoo/odoo` 17.0 分支源码核实（`odoo/addons/base/models/ir_ui_view.py` 的 `attrs`/`states` 硬拒、`odoo/tools/misc.py` 的 `get_resource_path` 移除与 `file_path` 定义、`odoo/release.py`、`odoo/requirements.txt` 的 libsass/Werkzeug 约束），以及多社区文（odoohub 版本差异、Medium《Odoo Migration Decoded》、LobeHub frontend skill、oec.sh 需求页）交叉核实。本书与同目录 `Odoo16to17Migration/` 的机器可读映射表（Skill）保持事实一致——本书可读性强，Skill 可被 agent 直接调用。
> **可信度标记**：`CONFIRMED` = 源码/官方 changelog 多源交叉核实；`[verify]` = 单一社区来源或来源间有分歧、待 17.0 实机/源码最终确认；`[EE-verify]` = Enterprise 专属、需对照 EE 17.0 树复核。
>
> **配套技能**：同目录 `Odoo16to17Migration/` 提供机器可读映射表与扫描器，含 `references/views-qweb.md`、`references/orm-api.md`、`references/http-rpc-mail.md`、`references/security.md`、`references/modules-mapping.md`、`references/upgrade-code.md` 与 `scripts/scan_addon.py`。本书为可读叙事，技能可被 agent 直接调用，两者事实一致。

---

## 第 0 章 · 导言

### 0.1 为什么是 16→17

与 17→18（"移除主导"，`name_get`/`check_access`/`user_has_groups`/`check_recursion`/`inselect` 被删、`tree`→`list`）和 18→19（"重底座"，ORM 包拆分 + Owl 3 + 安全模型重构）相比，**16→17 是一次"视图声明语法 + Python 运行时底座"双线升级**：

- **视图层语法革命（最高频、最易遗漏）**：`attrs` / `states` 这两个沿用十余年的 XML 属性被**硬拒**（17.0 在视图校验时直接抛 `ValidationError`），必须改写成内联的 `invisible` / `readonly` / `required` Python 表达式；列表字段的 `invisible="1"` 也改成 `column_invisible="1"`；`res.config.settings` 设置页结构大幅简化。
- **Python 运行时底座抬升**：Python 3.10+ 成为地板（3.8/3.9 直接不可用）；`post_init_hook` 等钩子签名从 `(cr, registry)` 改为 `env`；`get_resource_path` 被移除、改用 `file_path`；视图 context 里的 `active_id`/`active_ids`/`active_model` 被要求改写；`message_post` 的 `body` 默认改为纯文本/Markdown（HTML 需显式 `body_is_html=True`）。
- **没有任何 `upgrade_code` codemod**：17.0 分支**不含 `odoo/upgrade_code/` 模块**（源码核实：该路径在 17.0 返回 404），所以 16→17 **全部靠人工映射**，自动化程度为零——这与 17→18（1 个 codemod）、18→19（多个 codemod）形成鲜明对比。

### 0.2 版本作用域纪律（最重要的一条）

> **变更归属于它首次出现的版本。** 不要把 17→18 / 18→19 / 19→20 才引入的破坏性变更误带进 16→17。

已被显式排除在 16→17 之外、属于**更晚版本**的改动——它们由对应技能处理：

| 变更 | 真实归属版本 | 说明 |
|---|---|---|
| 视图类型 `tree` → `list`（`<tree>` 硬拒） | **17→18（18.0）** | 16→17 中 `<tree>` **仍是合法视图类型**（17.0 源码 `ir_ui_view.py` 的 `type` 选单含 `('tree','Tree')`），**不要**在 16→17 改名 |
| `name_get` / `_name_search` / `check_access_rights` / `user_has_groups` / `check_recursion` / `inselect` 运算符**移除** | **17→18（18.0）** | 16→17 中这些 API **仍存在**（仅 `name_get` 自 16.4 起弃用、17 中仍可用但告警）；移除属 17→18 |
| `mail.channel` → `discuss.channel` | **17→18（18.0）** | 16→17 中 `mail.channel` 仍有效 |
| Owl 2 → Owl 3（`setup()` 强制化） | **19.0** | 16/17 均为 Owl 2，无需重写组件 |
| `web_editor` → `html_editor` / `html_builder` | **19.0** | 16/17 中 `web_editor` 仍在 |
| `res.groups` 的 `category_id`→`privilege_id` 重构、安全文件 `ir.model.access.csv`→`ir.access.csv` | **19.0 / 20.0** | 16→17 的 `res.groups` 与安全文件格式**不变** |
| `type='json'`→`jsonrpc`、字段 `group_operator`→`aggregator` | **17.2 / 18.1（Online 小版本）** | 见 0.3：这些是在 17.x 区间内才出现的改动，对 16→17 **不适用**（16 出发落到 17.0，未包含 17.2）。若你目标锁定 17.2+，再另行处理 |
| SCSS 编译**移除**（改为只能发 CSS） | **晚于 17.0（未在 17.0 落地）** | 17.0 的 `requirements.txt` 仍含 `libsass`，SCSS **仍被编译**；"SCSS 移除"是后续版本的误传，见第 1.2 章 |

**范围约定**：本书把"目标大版本 17"理解为 **17.0**。17.x 的 Online 小版本（17.2 的 `aggregator`、17.2 的 `jsonrpc` 等）**不纳入 16→17**——它们由"从 17 出发"的后续跳跃覆盖。每项变更都标出首次出现版本，便于核对作用域。

### 0.3 推荐工作流（详见第 10 章）

1. **扫描（triage）** → 2. **应用人工映射**（无 codemod）→ 3. **校验**（`-u` + 测试 + 清 `DeprecationWarning`）→ 4. **出报告**。

> 16→17 是三步而非五步：**没有 `upgrade_code` 这一步**。所有改动（视图 `attrs`→表达式、钩子签名、context 改写、设置页重构）都靠手工 + 本书映射表完成。

---

## 第 1 章 · 框架与运行时

### 1.1 Python 3.10+ 成为地板 — CONFIRMED

Odoo 17.0 要求 **Python 3.10 或以上**（16.0 支持 3.8/3.9/3.10）。运行 16 代码的服务器若仍是 Python 3.8/3.9，升级前必须先升 Python，否则 Odoo 17 无法启动。多源核实：17.0 `release.py`（`version_info = (17, 0, 0, FINAL, 0, '')`）+ oec.sh 需求页（"Python 3.10+"）+ odoohub 版本差异（"17.0 要求 python 版本大于 3.10"）。

- 同时 `requirements.txt` 锁定了一批依赖下限：`Werkzeug==2.0.2`（3.10）/ `2.2.2`（3.11）/ `3.0.1`（3.12）、`lxml`、`psycopg2==2.9.2`、`MarkupSafe==2.1.x`、`passlib==1.7.4` 等。升级前按目标 Python 小版本对齐依赖。

### 1.2 SCSS 在 17.0 仍被编译（纠正常见误传）— CONFIRMED

**常见误传**："Odoo 17 移除了 SCSS 编译，必须改发 CSS。" **事实**：17.0 的 `requirements.txt` 仍包含 `libsass==0.20.1`（python<3.11）/ `0.22.0`（≥3.11），表明 SCSS 编译链在 17.0 仍然存在。因此 16→17 **无需**把 `.scss` 重写为 `.css`；沿用 16 的主题 SCSS 在 17.0 照常编译。

> **作用域守卫**："SCSS 不再被 Odoo 编译"这一破坏性变更出现在**晚于 17.0** 的版本（社区报告多指向 18.0 及以后）。请勿在 16→17 阶段提前做 SCSS→CSS 重写，否则会做无用功。若你的目标实际是 18+，则在 17→18 步骤处理。
>
> **仍建议**：趁 16→17 检查主题 SCSS 是否用了已弃用的 libsass 语法（`/` 除法、`@import` 全局变量冲突），这些在后续 dart-sass 化时才会爆，提前清理可降本。

### 1.3 数据库与依赖

- **PostgreSQL 12+**：oec.sh 需求页标注 17.0 需 PostgreSQL 12+（`[verify]`：具体下限以 `odoo/sql_db.py` 的版本校验为准；社区另有报告 13/14）。升级前确认数据库版本。
- **Werkzeug 2.0.2 地板**（`[verify]`）：17.0 锁定 `Werkzeug==2.0.2`。若你的 16 代码用了 Werkzeug 1.x 专属 API（旧 `werkzeug.wrappers.Response` 行为、`werkzeug.contrib` 等），控制器可能报错——见第 5.2 章。

### 1.4 没有任何 `upgrade_code` codemod — CONFIRMED

17.0 分支**没有 `odoo/upgrade_code/` 模块**（GitHub 目录列举 + `odoo/upgrade_code/__init__.py` 在 17.0 均返回 404）。因此：

- 不存在 `odoo-bin upgrade_code --from 16.0` 这类自动化改写工具对 16→17 生效。
- 全部迁移靠本书第 2–6 章的人工映射 + 随附扫描器（`Odoo16to17Migration/scripts/scan_addon.py`）识别。
- 数据/结构升级脚本放在各模块的 `migrations/17.0/` 目录（`pre-` / `post-` / `end-` 钩子），属手动编写，见第 9 章。

---

## 第 2 章 · 视图 XML：attrs/states 移除（头号硬断裂）

### 2.1 `attrs` / `states` 属性被硬拒 — CONFIRMED（源码核实）

17.0 的 `ir_ui_view.py` 在校验组合 arch 时**主动抛异常**拒绝仍使用这两个属性的视图：

```python
# odoo/addons/base/models/ir_ui_view.py （17.0）
if combined_arch.xpath('//*[@attrs]') or combined_arch.xpath('//*[@states]'):
    raise ValidationError(_('Since 17.0, the "attrs" and "states" attributes are no longer used.\nView: %(name)s in %(file)s', ...))
```

任何遗留 `attrs="{'invisible': [...]}"` / `attrs="{'required': [...]}"` / `states="draft,open"` 都会在安装/升级时直接报 `ValidationError: Since 17.0, the "attrs" and "states" attributes are no longer used.`

**改写规则**（PR #104741）：把字典式 `attrs` 翻译成对应属性的内联 Python 表达式。

```xml
<!-- 16 -->
<field name="vat" attrs="{'invisible': [('country_id', '=', False)]}"/>
<field name="credit_limit" attrs="{'readonly': [('state', '=', 'done')]}"/>
<field name="note" attrs="{'required': [('type', '=', 'contact')]}"/>
<field name="stage" states="draft,open"/>

<!-- 17 -->
<field name="vat" invisible="country_id == False"/>
<field name="credit_limit" readonly="state == 'done'"/>
<field name="note" required="type == 'contact'"/>
<field name="stage"/>  <!-- states 属性删除；改用 invisible/readonly 条件 -->
```

> **`states` 的迁移**：旧 `states="draft,open"` 表达的是"仅在这些 state 下可见/可编辑"。改用组合条件表达式，例如 `invisible="state not in ('draft','open')"` 或 `readonly="state != 'draft'"`。不要把 `states` 当字段属性遗留——它既在 XML 视图被拒，也在 Python 字段定义中被拒（odoohub："`py 文件中的 states 属性也不再支持使用`"）。

> **表达式语法**：属性值现在是**一段 Python 表达式**（布尔上下文），支持字段名直接引用、比较、`and`/`or`/`not`、`in`、圆括号。多个条件用 `and`/`or` 连接，等价于旧 `attrs` 的列表（默认 `AND`）。

### 2.2 列表字段 `invisible="1"` → `column_invisible="1"` — CONFIRMED（OCA 17 指南）

在 `tree`（列表）视图里，若某字段原本用 `invisible="1"` 仅作数据载体（不展示列），17.0 会**显示该列（空值）**。须改为 `column_invisible="1"` 才恢复"隐藏整列"语义：

```xml
<!-- 16 -->
<tree>
  <field name="partner_id"/>
  <field name="hidden_amount" invisible="1"/>
</tree>

<!-- 17 -->
<tree>
  <field name="partner_id"/>
  <field name="hidden_amount" column_invisible="1"/>
</tree>
```

> **注意**：`<tree>` 在 16→17 **仍是合法标签**（17.0 `type` 选单含 `tree`，见第 0.2 章排除表）。不要把它改成 `<list>`——那是 17→18 的事。这里只改 `invisible`→`column_invisible`。

### 2.3 `res.config.settings` 设置页简化 — CONFIRMED（PR #106425）

设置视图结构大幅简化，旧骨架需改写：

| 16（旧） | 17（新） |
|---|---|
| `<app>` 外层容器 | 改用 `<app>` 仍是入口，但内部结构变化 |
| `<block title=...>` / `<block>` | 等价为新的 `<block>`（语义更简） |
| `<div class="o_setting_right_pane">` / `o_setting_left_pane` | **删除**这两个 div，字段/标签直接放入 `<div class="...">` |
| 标题写在 `<h2>` / 单独元素 | 标题放进 `<block>` 的 `title` 属性 |
| `app_setting_block` | 改为 `<block>` |

```xml
<!-- 16 -->
<record id="res_config_settings_view_form" model="ir.ui.view">
  <field name="arch" type="xml">
    <form>
      <app string="My App">
        <block title="General">
          <div class="o_setting_left_pane"><field name="x_enabled"/></div>
          <div class="o_setting_right_pane"><label for="x_enabled"/>...</div>
        </block>
      </app>
    </form>
  </field>
</record>

<!-- 17 -->
<record id="res_config_settings_view_form" model="ir.ui.view">
  <field name="arch" type="xml">
    <form>
      <app string="My App" title="My App">
        <block title="General">
          <setting title="Enabled" help="...">
            <field name="x_enabled"/>
          </setting>
        </block>
      </app>
    </form>
  </field>
</record>
```

> OCA 指南建议用 `<setting>` 包裹字段（带 `title` / `help` / `documentation` 等属性）替代旧的双 pane div。旧 `o_setting_right_pane` / `o_setting_left_pane` 类必须删除。

### 2.4 `[verify]` 前端栈：Bootstrap 5 / jQuery（来源间有分歧，待核）

多个社区来源把"Bootstrap 4→5 类名替换 + jQuery 移除"归到 Odoo 16→17 前端重写，但 **17.0 官方发布说明未提及 Bootstrap/jQuery/SCSS 变更**，且来源之间存在分歧（有来源称 jQuery 在 17 仍"完全可用"、Bootstrap 5.1.3 归到 18/19，也有来源称 Bootstrap 4→5 早在 16+ 完成）。

> **作用域守卫（诚实标注）**：本工作台**不将 Bootstrap 5 / jQuery 移除列为 16→17 的确证破坏性变更**。若你的模块含前端/网站代码，请在 17.0 实机核实 `web.assets_frontend` 捆绑包的实际依赖：
> - 若确认 17.0 已用 Bootstrap 5 并移除 jQuery，则应用下列**标准 BS4→5 类名映射**（仅当证实适用时）：
>   `ml-*`→`ms-*`、`mr-*`→`me-*`、`pl-*`→`ps-*`、`pr-*`→`pe-*`、`text-left`→`text-start`、`text-right`→`text-end`、`float-left`→`float-start`、`float-right`→`float-end`、`form-group`→`mb-3`、`custom-select`→`form-select`、`close`→`btn-close`、`badge-*`→`bg-*`、`font-weight-bold`→`fw-bold`、`sr-only`→`visually-hidden`、`no-gutters`→`g-0`；数据属性 `data-toggle`→`data-bs-toggle`、`data-target`→`data-bs-target`、`data-dismiss`→`data-bs-dismiss`。
> - 若确认 jQuery 已移除，则自定义 JS 中 `$(...)` / `jQuery(...)` / 依赖 jQuery 的插件须改写为原生/Owl。
>
> 标记 `[verify]`：以你 17.0 实际捆绑包为准，不要盲改。

### 2.5 `[verify]` 其它 QWeb 前端项

- **`t-attf-` 弃用**：`t-attf-` 在 Owl 2（16.0 引入）即被 `t-att="f'...'"` f-string 表达式取代。若你的 16 代码仍用 `t-attf-`，属"16 起已弃用"、非 17 新引入，但 16→17 可顺手迁移。来源：Owl 2 文档与社区；Odoo 官方 17 迁移指南未单列此项 → 标 `[verify]`。
- **`t-raw` 已移除**（16.0 即移除）、**`t-esc`→`t-out`** 属 19.0（见 18→19 技能），**不在此步**。

---

## 第 3 章 · ORM 与 Python API

### 3.1 `name_get()` 弃用（仍可用，告警）→ `_compute_display_name` — CONFIRMED（PR #122085）

`name_get` 自 16.4 起弃用，**在 17.0 仍可被调用但会告警**，18.0 正式移除（由 17→18 技能处理移除）。16→17 的推荐动作是**提前迁移**，避免 17 的弃用警告滚雪球：

```python
# 16
def name_get(self):
    return [(rec.id, f"{rec.code} - {rec.name}") for rec in self]

# 17（推荐）
display_name = fields.Char(compute='_compute_display_name', store=True)
@api.depends('code', 'name')
def _compute_display_name(self):
    for rec in self:
        rec.display_name = f"{rec.code} - {rec.name}"
```

> **版本作用域**：此处是"弃用期迁移"（17 中仍可用）；真正的 `name_get` **移除**归 17→18。两本烹饪书不冲突：16→17 让你**现在就改**，17→18 处理**没改的遗留代码**。

### 3.2 模块钩子签名 `(cr, registry)` → `env` — CONFIRMED（PR b4a7996）

`pre_init_hook` / `post_init_hook` / `uninstall_hook` 的入参从 `(cr, registry)` 改为单个 `env`：

```python
# 16
def post_init_hook(cr, registry):
    setup_provider(cr, registry, 'alipay')
def uninstall_hook(cr, registry):
    reset_payment_provider(cr, registry, 'alipay')

# 17
def post_init_hook(env):
    setup_provider(env, 'alipay')
def uninstall_hook(env):
    reset_payment_provider(env, 'alipay')
```

> 改写时把 `cr` 换成 `env.cr`（如需游标），把 `registry` 换成 `env.registry`。OCA 17 指南明确："the argument that is now passed is env, so you should convert your methods."

### 3.3 `get_resource_path()` 移除 → `file_path()` — CONFIRMED（源码核实 + PR #135607）

`get_resource_path` 在 17.0 的 `odoo/tools/misc.py` 中**已无定义**（源码核实），替代为 `file_path`（签名 `file_path(file_path, filter_ext=('',), env=None)`），且参数语法变化：

```python
# 16
path = get_resource_path('my_module', 'data', 'template.xml')

# 17
from odoo.tools import file_path
path = file_path('my_module/data/template.xml')   # 改用正斜杠拼接的路径串
```

> 注意 `file_path` 接收的是**单条以 `/` 连接的相对路径字符串**，不再是多个位置参数。`[verify]`：个别模块若用 `get_resource_from_path`（19 引入）属更晚版本，16→17 用 `file_path` 即可。

### 3.4 视图 context 的 `active_id` / `active_ids` / `active_model` — CONFIRMED（PR daf05d48）

自定义视图 context 里硬编码 `active_id` / `active_ids` / `active_model`（如智能按钮 context）会被要求改写，否则发出警告：

- `active_id` → 直接用 `id`（记录自身的 id）。
- `active_model` → 改为**硬编码模型名**（如 `'res.partner'`）。
- `active_ids` → 无直接替换，需按实际意图重写（例如改用 `self` 的上下文或显式 id 列表）。

```xml
<!-- 16 -->
<button name="action_open" context="{'default_partner_id': active_id, 'active_model': 'res.partner'}"/>

<!-- 17 -->
<button name="action_open" context="{'default_partner_id': id, 'default_model': 'res.partner'}"/>
```

> 源码对未替换的 `active_id`/`active_ids`/`active_model` 会发 warning；`active_ids` 视具体场景处理（OCA 指南称其为"weird case"，需按意图重构）。

### 3.5 16→17 **未移除**的 ORM API（版本作用域提醒）

下列 API 在 16→17 **仍然存在**（它们的"移除"属于 17→18，勿在 16→17 提前改）：

- `check_access_rights` / `check_access_rule` / `user_has_groups` / `check_recursion` — 17 中仍可用；18 才移除。
- `_name_search` — 17 中仍可用；18 才移除（改 `_search_display_name`）。
- `inselect` 域运算符 — 17 中仍可用；17.4/18 才移除。
- 字段 `group_operator` — 17.0 中仍是 `group_operator`（17.2 才改名 `aggregator`，属 17.x 小版本，**不纳入 16→17**）。
- `@http.route(type='json')` — 17 中仍是 `type='json'`（18.1 才改 `jsonrpc`，属 17→18 的 Online 小版本面）。

> **红线**：16→17 不要动上述 API；它们的迁移由 17→18 技能统一负责，避免重复/越界修改。

---

## 第 4 章 · 安全与 res.groups（16→17 基本不变）

> **关键结论**：16→17 的**安全文件格式与 `res.groups` 模型都不变**。以下仅在"清理 16 代码"时相关，切勿套用 19→20 的 `privilege_id` / `ir.access.csv` 改动（那是 18→19 之后的事）。

- `security/ir.model.access.csv` 列格式**不变**（`perm_read/perm_write/perm_create/perm_unlink`）。
- `res.groups.category_id` / `groups_id` / `users` 字段**不变**。
- 本步唯一与安全相关的代码改动是第 3.1 章的 `name_get` 弃用迁移（它影响显示名，不影响安全模型）。
- `[EE-verify]`：Enterprise 专属安全/权限行为在 16→17 若有微调，需对照 EE 17.0 树复核；CE 层面无变化。

---

## 第 5 章 · HTTP、邮件与二进制

### 5.1 `message_post` 的 `body` 默认改为文本/Markdown — CONFIRMED（多源）

`mail.thread.message_post` 的 `body` 参数默认**不再按 HTML 解析**：

- 17.0 起 `body` 默认接收 **str 或 Markdown**；若需发送 HTML，必须显式传 `body_is_html=True`。
- 这影响任何自定义调用 `message_post(body="<p>...</p>")` 的代码——17 下会被当作纯文本/Markdown 渲染。

```python
# 16（body 默认当 HTML）
self.message_post(body="<p>Invoice %s confirmed</p>" % inv.name)

# 17（HTML 需显式标记）
from markupsafe import Markup
self.message_post(body=Markup("<p>Invoice %s confirmed</p>" % escape(inv.name)),
                  body_is_html=True)
# 或改用 Markdown（默认）
self.message_post(body=f"Invoice {inv.name} confirmed")
```

> 源码核实注：`mail/models/mail_thread.py` 在 17.0 的具体路径与 18 不同（17.0 该路径返回 404，属目录结构调整），但 `body_is_html` 行为变更由 OCA 17 指南与 odoohub 版本差异一致确认。列入 `CONFIRMED`（多社区源 + 官方迁移共识）。

### 5.2 `[verify]` 控制器与 Werkzeug 2

17.0 锁定 `Werkzeug==2.0.2`（python 3.10）。若你的 16 代码或依赖用了 Werkzeug 1.x 专属 API，自定义控制器可能报错（`[verify]`：版本归属——16 是否也用 Werkzeug 2 存疑，但 17 的地板已明确）。高风险点：

- `werkzeug.wrappers.Response` 的若干行为变化、`BaseRequest` 用法。
- `werkzeug.contrib` 已移除（若 import 会直接失败）。
- `werkzeug.urls` 的 `url_encode` / `url_quote` / `url_decode` 位置移动。

> 若升级后控制器报 `ImportError` / `AttributeError` 指向 werkzeug，按 2.x API 改写；属 `[verify]`，以你实际 16→17 的 werkzeug 版本差为据。

### 5.3 二进制 / Excel / PDF / 时间

16→17 无报告破坏性变更：`fields.Binary`、`xlsxwriter` 报表、`PyPDF2`（17.0 仍列于 requirements）、`zoneinfo`（替代 `pytz`，17 起推荐）均稳定跨版本。`zoneinfo` 用法：`from zoneinfo import ZoneInfo`（Python 3.9+ 标准库），替代 `import pytz`。

### 5.4 `[verify]` 邮件 composer / `mail.compose.message`

`mail.compose.message` 向导在 17 仍可用，但 Odoo 持续将发信 UX 收敛到 `message_post` + 对话框。若自定义继承该向导，建议在 17 实机验证其结构是否变化（`[verify]`，社区未单列明确破坏性条目）。推荐：新代码直接用 `message_post`，避免深度依赖 composer 向导内部。

---

## 第 6 章 · 模块 / 模型 / 字段映射（16→17 较轻）

> OCA 17 指南明确：**本步聚焦框架变更，不罗列数据模型变更**（后者因模块而异且极其庞大）。数据模型改名请查 OCA OpenUpgrade 的 `upgrade_analysis.txt`。以下仅列框架级、跨模块通用的重命名/行为变更。

### 6.1 通用字段/属性/API 改名（框架级）— CONFIRMED

| Odoo 16 | Odoo 17 | 版本 | 来源 |
|---|---|---|---|
| 视图 `attrs="{'invisible':[...]}"` | `invisible="expr"` | 17.0 | PR #104741（硬拒） |
| 视图 `attrs="{'required':[...]}"` | `required="expr"` | 17.0 | PR #104741 |
| 视图 `attrs="{'readonly':[...]}"` | `readonly="expr"` | 17.0 | PR #104741 |
| 视图 `states="draft,open"` | 删除 `states`，改 `invisible`/`readonly` 条件 | 17.0 | PR #104741 + odoohub |
| 列表字段 `invisible="1"` | `column_invisible="1"` | 17.0 | OCA 17 |
| `res.config.settings` 双 pane div | `<setting>` / 删 `o_setting_*_pane` | 17.0 | PR #106425 |
| `message_post(body="<p>..</p>")` | `body_is_html=True` 或 Markdown | 17.0 | OCA + odoohub |
| `post_init_hook(cr, registry)` | `post_init_hook(env)` | 17.0 | PR b4a7996 |
| `uninstall_hook(cr, registry)` | `uninstall_hook(env)` | 17.0 | PR b4a7996 |
| `get_resource_path(a,b,c)` | `file_path('a/b/c')` | 17.0 | PR #135607（源码核实） |
| 视图 context `active_id` | `id` | 17.0 | PR daf05d48 |
| 视图 context `active_model` | 硬编码模型名 | 17.0 | PR daf05d48 |
| `name_get()` | `_compute_display_name` | 16.4 弃用/17 可用 | PR #122085 |
| Python 3.8 / 3.9 | Python 3.10+ | 17.0 | release + 多源 |

### 6.2 模块改名（manifest `depends`）— 16→17 基本无

与 17→18（无核心改名）、18→19（`web_editor` 拆分）不同，**16→17 没有核心模块改名**。常见"改名"多属更早版本（如 `delivery`→`stock_delivery` 是早期）或业务模块特定，不在此框架清单内。第三方应用是主要阻塞点：每个付费/OCA 应用需有 17.0 分支（odoohub 指南）。

### 6.3 数据模型改名 — 见 OpenUpgrade

`account.*` / `stock.*` / `hr.*` 等业务模型字段改名属模块特定迁移，不在本书范围。建议直接查阅 OCA OpenUpgrade 的 `upgrade_analysis.txt`（按核心模块拆分）。

### 6.4 症状 → 修复索引

| 17 安装/运行时症状 | 可能原因 | 修复锚点 |
|---|---|---|
| `ValidationError: Since 17.0, the "attrs" and "states" attributes are no longer used.` | 视图仍用 `attrs`/`states` | 第 2.1 章 |
| 列表多出一列空字段 | `invisible="1"` 未改 `column_invisible` | 第 2.2 章 |
| 设置页渲染错位/报错 | 旧 `o_setting_*_pane` / `<app>` 结构 | 第 2.3 章 |
| 消息体显示为原始 HTML 标签 | `message_post(body=html)` 缺 `body_is_html` | 第 5.1 章 |
| 升级报 `TypeError` / 钩子签名错 | `post_init_hook(cr, registry)` 未改 `env` | 第 3.2 章 |
| `ImportError: cannot import name 'get_resource_path'` | 改用 `file_path` | 第 3.3 章 |
| 智能按钮 context 警告 | `active_id`/`active_model` 未改 | 第 3.4 章 |
| 服务起不来（Python 版本） | 仍是 Python 3.8/3.9 | 第 1.1 章 |
| 自定义组件仍 `define([...])` | 旧 Owl 1 写法（若从更老版本跳） | 第 2.5 章 `[verify]` |

---

## 第 7 章 · 缓存 / SQL、字段与域

### 7.1 SQL 安全拼接 — CONFIRMED（17.0 沿用）

`SQL(...)` 包装对象自 17.0（PR #134677）引入，16→17 **不变**。务必用 `SQL()` 组合 SQL，绝不拼接 f-string，避免注入。

### 7.2 字段与域

- 字段 `group_operator` 在 17.0 **仍是 `group_operator`**（改名 `aggregator` 发生在 17.2，属 17.x 小版本，**不纳入 16→17**）。
- `aggregator` / `Domain` API / `models.Constraint` 声明式约束均**不在 17.0**（它们出现在 17.2/18.1，由 17→18 技能按 Online 小版本处理）。
- `_sql_constraints` 在 17.0 **完全正常**，无需改动。
- 非存储 related 字段搜索：17.0 沿用 16 行为（18 起改为直接抛异常），见 17→18 第 2.7 章。

### 7.3 缓存失效 API

若你的 16 代码用了老式缓存失效（`self.env[...].invalidate_cache([...])` / `flush()` 套在单例上），17 推荐更细粒度写法（`records.invalidate_recordset(...)` / `records.flush_recordset(...)`，或模型级 `invalidate_model` / `flush_model`）。属最佳实践而非硬断裂；`[verify]` 是否强制以你的 17 实机为准（Medium 文章列为 17 变更，但 OCA 17 指南未单列）。

---

## 第 8 章 · 认证 / 测试与校验

- **安装时视图校验更严**：任何 `attrs`/`states` 残留会直接抛 `ValidationError`（见第 2.1 章），且畸形 XPath / 缺失字段引用会在安装时报错。加一道视图 RNG 检查。
- **以可见弃用警告启动服务**（`--dev=all` / 开 log-level），清掉**每一个** `DeprecationWarning`——`name_get` 弃用、`get_resource_path` 弃用都会在 17 告警，提前修掉可避免 17→18 的移除硬断裂。
- 在 17.0 沙箱跑 `odoo-bin -u <module> --test-tags /<module>`；视图 `ValidationError` 与 `TypeError`（context/钩子签名）最先修。
- 16→17 对外部 JSON-2 / XML-RPC 测试契约**无改动**（控制器 `type='json'` 仍有效）。

---

## 第 9 章 · 没有 codemod：手动迁移与 migrations/ 脚本

### 9.1 现实：17.0 无 `upgrade_code`

16→17 **不存在** `odoo-bin upgrade_code` 自动化改写（17.0 分支无 `odoo/upgrade_code/` 模块，源码核实）。因此：

- **没有 `--from 16.0` 的 codemod 可跑**。所有改动靠本书映射 + 随附扫描器识别。
- 数据/结构升级放模块内 **`migrations/17.0/`** 目录：
  - `pre-17.0.py`：`pre_init_hook` 风格的数据库预处理。
  - `post-17.0.py`：安装后数据迁移。
  - `end-17.0.py`：收尾。
  - `ir_model_fields` 等表的列/数据调整。
- 纯代码级映射（attrs→表达式、钩子签名、`get_resource_path`→`file_path`、`active_*` context）由开发者在源码里直接改，再 `git diff` 复核。

### 9.2 哪些必须手工（全部）

| 改动 | 是否 codemod | 处理 |
|---|---|---|
| `attrs`/`states` → 内联表达式 | 否（手工） | 第 2.1 章 |
| `invisible="1"` → `column_invisible` | 否（手工） | 第 2.2 章 |
| `res.config.settings` 结构 | 否（手工） | 第 2.3 章 |
| `message_post` body | 否（手工） | 第 5.1 章 |
| 钩子签名 `env` | 否（手工） | 第 3.2 章 |
| `get_resource_path` → `file_path` | 否（手工） | 第 3.3 章 |
| `active_*` context | 否（手工） | 第 3.4 章 |
| `name_get` → `_compute_display_name` | 否（手工，弃用期迁移） | 第 3.1 章 |
| Bootstrap/JQuery（若证实适用） | 否（手工） | 第 2.4 章 `[verify]` |

### 9.3 Scanner 契约

随附的 `Odoo16to17Migration/scripts/scan_addon.py`（按 16→17 模式定制）标记发现项并打印 17.0 替换：

```bash
python3 Odoo16to17Migration/scripts/scan_addon.py /path/to/addons --addon my_module --json
# 退出码 1 = 有发现项
```

### 9.4 写自己的 `migrations/17.0/` 脚本

要新增数据迁移，在模块内 `migrations/17.0/` 下放 `pre-`/`post-`/`end-` 脚本（接收 `cr` 或 `env`）。每个脚本单一职责、幂等；提交结果 `git diff` 时附上相关 `references/*.md` 的锚点。

---

## 第 10 章 · 迁移实战清单

### 10.1 Grep 速查（pattern → 动作 → 见章节）

```
attrs="                      → 内联 invisible/readonly/required 表达式（第 2.1 章）
states="  (视图或 py 字段)    → 删除 states，改条件表达式（第 2.1 章）
invisible="1"  (在 tree 内)   → column_invisible="1"（第 2.2 章）
o_setting_right_pane          → 删除，改用 <setting>（第 2.3 章）
o_setting_left_pane           → 删除，改用 <setting>（第 2.3 章）
app_setting_block             → <block>（第 2.3 章）
message_post(body="<         → 加 body_is_html=True 或改 Markdown（第 5.1 章）
def post_init_hook(cr,        → def post_init_hook(env):（第 3.2 章）
def uninstall_hook(cr,        → def uninstall_hook(env):（第 3.2 章）
get_resource_path(           → file_path('a/b/c')（第 3.3 章）
active_id / active_ids / active_model → id / 硬编码模型（第 3.4 章）
def name_get(                → _compute_display_name（第 3.1 章）
from odoo.tools import get_resource_path → file_path（第 3.3 章）
# 以下【不要】在 16→17 改（属 17→18 / 更晚版本）：
<tree                        → 16→17 仍合法，勿改 <list（见 0.2 / 第 2.2 章）
check_access_rights( / user_has_groups( / check_recursion( → 17 仍可用，留待 17→18（第 3.5 章）
group_operator=              → 17.0 仍有效，勿改 aggregator（第 7.2 章）
type='json' 路由             → 17 仍 type='json'，勿改 jsonrpc（第 3.5 章）
depends: ['web_editor']      → 17 仍可用，勿动（第 4 章）
```

### 10.2 端到端工作流

1. **Triage（扫描）**：`python3 Odoo16to17Migration/scripts/scan_addon.py /path/to/addons`——按文件分组列出发现项、行号、17.0 替换。
2. **人工映射**：对 scanner 标出的项，套用对应章节替换（视图 → 第 2 章；ORM/API → 第 3 章；HTTP → 第 5.1 章；钩子/context → 第 3.2–3.4 章；设置页 → 第 2.3 章）。**注意红线**：不要越界改 17→18 才处理的 API（见第 3.5 章）。
3. **数据迁移脚本**：在模块 `migrations/17.0/` 放 `pre-`/`post-`/`end-` 脚本处理库内数据。
4. **校验**：重跑 scanner（期望 0 发现）；`odoo-bin -u <module> --test-tags /<module>`；用 `--dev=all` 启动清掉每个 `DeprecationWarning`（`name_get`/`get_resource_path` 弃用警告是 17→18 的前兆）；最后修视图 `ValidationError` 与 `TypeError`。
5. **报告**：逐模块汇总——人工编辑（附所用章节锚点）、剩余 `[verify]`/`[EE-verify]` 项、测试状态。

---

## 溯源附录（Provenance）

- **OCA `maintainer-tools`《Migration to version 17.0》**（框架级清单，PR #104741、#106425、#122085、#135607、b4a7996、daf05d48）：`attrs`/`states` 移除、`res.config.settings` 简化、`name_get`→`_compute_display_name`、钩子 `env`、视图 context `active_*`、`get_resource_path`→`file_path`、列表 `invisible`→`column_invisible`、Python 3.10。
- **GitHub 17.0 源码核实**：`odoo/addons/base/models/ir_ui_view.py`（`_check_xml` 抛 `ValidationError: "Since 17.0, the 'attrs' and 'states' attributes are no longer used."`；`type` 选单含 `('tree','Tree')`）；`odoo/tools/misc.py`（`get_resource_path` 已无定义，`file_path(file_path, filter_ext=('',), env=None)` 已定义）；`odoo/release.py`（`version_info = (17,0,0,FINAL,0,'')`）；`odoo/requirements.txt`（`libsass==0.20.1/0.22.0`、`Werkzeug==2.0.2/2.2.2/3.0.1`）；`odoo/upgrade_code/` 与 `odoo/upgrade_code/__init__.py` 在 17.0 返回 404（无 codemod）。
- **社区交叉核实**：odoohub《第二章 odoo 版本差异》（message_post body、states、Python 3.10、mail.channel 归属更正）；Medium《Odoo Migration Decoded 16→17→18→19》（message_post/Markup、t-raw/t-esc、SCSS/libsass→dart-sass 说法——后者与 requirements 冲突，已以源码为准纠偏）；LobeHub frontend skill（Bootstrap/jQuery 类名映射，来源对版本归属有分歧，已标 `[verify]`）；oec.sh 需求页（PostgreSQL 12+、Python 3.10+）。
- **核查日期**：2026-11-01。
- **诚实标注**：`[verify]` 项（Bootstrap 5/jQuery 版本归属、Werkzeug 1.x 影响、zoneinfo 迁移、缓存失效 API 强制度、邮件 composer 结构、PG 下限、SCSS 后续移除归属）源自单一社区来源或来源间分歧，已注明待 17.0 实机/源码最终确认，未以确证语气陈述。

---

*本烹饪书（单卷）覆盖 16.0 → 17.0 的视图声明语法革命（attrs/states 硬拒、column_invisible、设置页简化）、Python 运行时底座抬升（Python 3.10、钩子 env、get_resource_path→file_path、active_* context、message_post body）、以及"零 codemod、纯手工"的迁移现实。机器可读的映射表与扫描器见同目录 `Odoo16to17Migration/`。下一跳 17→18（tree→list、name_get 等移除）由对应技能处理。*
