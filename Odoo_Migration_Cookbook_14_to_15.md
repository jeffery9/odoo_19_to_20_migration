# Odoo 迁移烹饪书：14.0 → 15.0

> 本烹饪书是 **14→15** 迁移的事实基准（Fact Baseline）。配套技能见 `Odoo14to15Migration/`。
> 它专为**自定义模块**（CE 与 EE）从 Odoo 14 升级到 15 编写，覆盖所有破坏性（breaking）变更，
> 并明确**版本作用域**——只收 14→15 区间内真实发生的变更，更晚版本的改动一律排除（见第 1 章红线）。
>
> **可信度标记**：`CONFIRMED` = 已对**本地源码**逐条复核（Odoo CE 分支 `14.0` / `15.0`，
> 需要判定首次出现版本时追到 11.0–17.0），手法为 `git show` + 模型集 diff + 字段级 diff；
> OCA《Migration to version 15.0》与社区资料只当线索，不当依据。
> `[verify]` = 方向可信但仍需实机确认。
>
> **本轮复核推翻了 5 条长期流传的说法**（`t-raw` 被移除、`SavepointCase` 被移除、
> `Environment.manage()` 被移除、`ir.model*` 访问被移除、`subtype`→`subtype_xmlid` 属本对），
> 逐条对照见 **9.3 反例表**。凡与社区文章冲突处，以本文件为准。

---

## 目录

1. 导言与版本作用域
2. 头号断裂：QWeb `t-raw` → `t-out`（语义有陷阱）
3. `ir.model.data` 查询方法私有化
4. 邮件模板：Jinja 语法 → QWeb（正文）+ inline_template（subject 等）
5. 前端 / 资产：ES 模块 `.esm.js`、资产声明进 `__manifest__.py`
6. 测试：`SavepointCase` 与 `Environment.manage()`（弃用，非移除）
7. 安全与 `res.groups`（14→15 不变）
8. HTTP / 邮件 / 二进制（其它不变）
9. 模块 / 模型 / 字段映射
10. 测试与校验
11. `upgrade_code` codemod（14→15 无）
12. 迁移实战清单

---

## 1. 导言与版本作用域

Odoo 15.0（2021-10）是一次**QWeb 指令换代 + 资产声明入 manifest + 邮件模板 QWeb 化 + 会计支付方式行化**
的版本。与 12→13（会计重写）、13→14（`ir.actions.*` 访问 / `attrs` 约束）、16→17（`attrs`/`states` 硬拒）、
17→18（`tree`→`list`）相比，14→15 的破坏面集中在**前端模板语法与资产机制**、**`ir.model.data` 数据访问 API**、
**会计支付方式结构**，以及**测试基类的语义变化**。

**本版本对的三处头号断裂**：

1. QWeb `t-raw` 进入弃用（**16.0 才移除**），而替代品 `t-out` **默认转义**——照搬替换会把 HTML 静默转义掉；
2. `ir.model.data` 的公共查询方法（`get_object_reference` / `_get_id` / `xmlid_to_*`）私有化或移除，
   自定义代码里 `AttributeError` 高发；
3. 会计支付方式从 m2m 改为「行」模型 `account.payment.method.line`，日记账上的两个字段整体改名。

另有一条容易被忽略的横切变更：`note` / `narration` / `description` / `comment` 等字段由 `Text` 改为 `Html`，
视图 widget 与「按纯文本处理」的代码都要复核（见 9.1.10）。

### 版本作用域红线（勿套用更晚版本的改动）

| 更晚版本的改动 | 归属版本 | 在 14→15 中 |
|---|---|---|
| `ir.actions.*` 访问移除 | 13→14 | ❌ 排除（14 已处理） |
| `invisible`/`readonly` 动态表达式→`attrs` | 13→14 | ❌ 排除 |
| `_name_search` 返回 ids | 13→14 | ❌ 排除 |
| `attrs`/`states` **硬拒**（改内联表达式） | 16→17 | ❌ 排除 |
| `<tree>` → `<list>` | 17→18 | ❌ 排除 |
| `name_get` **移除** | 17→18 | ❌ 排除 |
| `get_resource_path`→`file_path` | 16→17 | ❌ 排除（14 仍用 get_resource_path） |
| `payment.acquirer`→`payment.provider`、`coupon`→`loyalty` | 15→16 | ❌ 排除 |
| `track_visibility`→`tracking` | **12→13** | ❌ 排除（常被误归 14→15） |
| `subtype`→`subtype_xmlid`（`message_post` 参数） | **13→14** | ❌ 排除（14.0 起已无 `subtype` 参数） |
| QWeb `t-raw` 指令的**彻底移除** | **15→16** | ❌ 排除（15.0 只是 deprecated，仍可渲染） |
| Python 3.10 底座抬升 | 16→17 | ❌ 排除（15.0 仍兼容 3.8+） |

> **Python 底座**：14.0 / 15.0 均要求 Python 3（15.0 支持 3.8–3.10；3.10 抬升严格化是 **16→17**）。

### 配套技能参考表（skill references）

本烹饪书的事实基准由 `Odoo14to15Migration/references/` 下的六份映射表承载，二者逐条对齐、零漂移：
`references/views-qweb.md`（t-raw/t-esc→t-out 及转义陷阱、esm.js、资产 manifest）、
`references/orm-api.md`（`ir.model.data` 方法私有化、SavepointCase 语义变化、Environment.manage 变 no-op）、
`references/http-rpc-mail.md`（Jinja→QWeb 引擎、subtype 属 13→14 的反证、其它不变）、
`references/models-mapping.md`（资产 key、`qweb` 键静默失效、API/字段/核心模型映射），
`references/security.md`（res.groups 不变）、
`references/upgrade-code.md`（无 codemod + migrations/15.0 工作流）。

---

## 2. 头号断裂：QWeb `t-raw` → `t-out`（语义有陷阱）  — CONFIRMED

15.0 起 `t-raw` 进入**弃用（deprecated）**状态，**不是移除**：仍能渲染，只是每次渲染写一条
warning（`Found deprecated directive @t-raw=... Replace by @t-out`）。**真正移除是 16.0**
（16.0 的 `qweb.py` 里已无任何 `t-raw` 字样）。所以 14→15 的处置目标是「清账」而非「救火」：
趁弃用窗口改完，否则下一跳必崩。`t-esc` 在 15.0 同样被标记 deprecated。

### 关键陷阱：`t-out` 默认是**转义**的

这是最容易踩错的一点。15.0 的 `t-out` 编译为 `escape(content)`，而 `markupsafe.escape`
对 `Markup` 实例是幂等的、对普通字符串则转义。所以：

| 表达式值类型 | `t-out` 行为 |
|---|---|
| `Markup`（Html 字段、手包 `Markup(...)`） | 原样输出（等价旧 `t-raw`） |
| 普通 `str`（`Char`/`Text` 字段） | **HTML 转义**（并不等价旧 `t-raw`） |

源码里 `t-raw` 分支之所以要显式 `content = Markup(content)`，正是为了把「不转义」这个旧语义
补回来。照搬 `t-raw` → `t-out` 而不检查值的类型，会把「原本输出 HTML」静默变成「输出转义后的
HTML 文本」——页面不报错，但格式全丢。

### Before（14.0）

```xml
<div t-raw="0"/>                       <!-- 原样输出 -->
<span t-raw="record.body_html"/>       <!-- Html 字段，不受转义 -->
<span t-raw="record.my_char"/>         <!-- 若值确实是 HTML 片段 -->
```

### After（15.0）

```xml
<div t-out="0"/>                        <!-- 模板内容本身已是 Markup，原样输出 -->
<span t-out="record.body_html"/>        <!-- Html 字段值是 Markup，仍不转义 -->
<span t-out="record.my_char"/>          <!-- 普通 Char：会被转义（多数情况正是想要的） -->
<span t-out="Markup(record.my_char)"/>  <!-- 确实要输出原始 HTML 时才包 Markup -->
```

- **判断口径**：值来自 `fields.Html`（`body_html`、`description`、`narration` 等）→ 直接 `t-out`
  即可，无需包 `Markup`；值来自 `Char`/`Text` → 先想清楚是否需要渲染 HTML，需要才 `Markup`。
- 服务端拼 HTML 后回传给模板时，用 `markupsafe.Markup(html)` 包一层。
- 无脑把所有 `t-raw` 换成 `t-esc` 是**错的**：`t-esc` 在 15.0 已 deprecated，且强制转义。
- 扫描 id：`t-raw`（正则 `t-raw`）、`t-esc`（正则 `t-esc`，一并清理）。
- 校验：15.0 只 warning，须开 `--dev=all` 才会在日志里看到；不要指望加载时报错。
  清理是否彻底，用扫描器复查（应为 0 命中），而不是靠运行期报错发现。

---

## 3. `ir.model.data` 查询方法私有化  — CONFIRMED

先纠正一个流传很广的说法：**15.0 并没有「移除对 `ir.model*` 的直接访问」**。
对照 14.0 / 15.0 的 `odoo/addons/base/models/ir_model.py`，访问控制、`_fields` 读取、
`ir.model.fields` 的 search 都没有被禁——这两个版本的 `ir_model.py` 差异集中在
`ir.model.data` 的方法签名与 `@api.ondelete` 改造上。

真正的断裂发生在 **`ir.model.data` 的查询方法：一批公共方法被私有化或删除**，自定义模块里
`env['ir.model.data'].get_object_reference(...)` 这类调用会直接 `AttributeError`。

### 方法对照（源码实测）

| 14.0 | 15.0 | 状态 |
|---|---|---|
| `xmlid_lookup(xmlid)` | `_xmlid_lookup(xmlid)` | 改名（加下划线），返回 `(id, res_model, res_id)` |
| `xmlid_to_res_id(xmlid, ...)` | `_xmlid_to_res_id(xmlid, ...)` | 改名 |
| `xmlid_to_res_model_res_id(xmlid, ...)` | `_xmlid_to_res_model_res_id(xmlid, ...)` | 改名，返回 `(res_model, res_id)` |
| `xmlid_to_object(xmlid, ...)` | — | **移除**；用 `_xmlid_to_res_model_res_id` 取 model/res_id 后 `browse` |
| `_get_id(module, xml_id)` | — | **移除**；用 `_xmlid_lookup("module.xml_id")[0]` |
| `get_object_reference(module, xml_id)` | — | **移除**；用 `_xmlid_to_res_model_res_id("module.xml_id")` |
| `get_object(module, xml_id)` | — | **移除** |
| `check_object_reference(module, xml_id, ...)` | `check_object_reference(...)` | 保留（内部改用 `_xmlid_lookup`） |

### 改法

```python
# 14.0 —— 这些在 15.0 全部失效
res_id = self.env['ir.model.data']._get_id('sale', 'my_record')
model, res_id = self.env['ir.model.data'].get_object_reference('sale', 'my_record')
obj = self.env['ir.model.data'].xmlid_to_object('sale.my_record')

# 15.0 —— 优先用最高层的 env.ref（两个版本都有，行为未变）
record = self.env.ref('sale.my_record')
# 只需要 id 时
res_id = self.env['ir.model.data']._xmlid_to_res_id('sale.my_record')
# 需要 model + id 时
model, res_id = self.env['ir.model.data']._xmlid_to_res_model_res_id('sale.my_record')
```

- **首选 `self.env.ref()`**：它跨版本稳定，返回 recordset，是大多数场景的正确写法。
  只有在需要「按字符串动态拼 xml-id」或「只要 id 不想要 recordset」时才下探到 `ir.model.data`。
- `_xmlid_lookup` 是底层方法，返回三元组且找不到时**抛 `ValueError`**（不返回 False），
  批量场景注意异常处理；`_xmlid_to_res_id(..., raise_if_not_found=False)` 才是软失败版本。
- 读取模型字段信息（`ir.model.fields`）在 14→15 **不受影响**，仍可用 `search`；
  更推荐直接用 `self.env['res.partner']._fields`，避免一次 SQL 往返。
- 扫描 id：`xmlid-lookup`（正则 `xmlid_lookup|xmlid_to_res_id|xmlid_to_res_model_res_id`、
  `get_object_reference`、`get_object\(`、`_get_id\(`）。

> 与 **13→14 的 `ir.actions.*` 访问收紧**不是一回事：那是另一个对象、另一个版本对。
> 本仓曾把「ir.model* 访问移除」写入本节，源码复核后已证伪并改写（见第 9.3 节反例表）。

---

## 4. 邮件模板：Jinja 语法 → QWeb（正文）+ inline_template（subject 等）  — CONFIRMED

15.0 把 `mail.template` 的渲染从 **Jinja** 改为两种新语言：

- **正文 `body_html`**：用 **QWeb**（与视图一致，支持 `t-` 指令）。
- **subject / email_from / email_to 等字段**：用 **inline_template**——类似 Jinja，但表达式包在
  `{{ }}` 中（而非旧的 `${ }`），且仅用于单行字段。

### Before（14.0，Jinja）

```xml
<record id="email_tpl" model="mail.template">
    <field name="subject">Invoice ${object.name}</field>
    <field name="body_html"><![CDATA[<p>Hello ${object.partner_id.name}</p>]]></field>
</record>
```

### After（15.0，QWeb + inline_template）

```xml
<record id="email_tpl" model="mail.template">
    <field name="subject">Invoice {{ object.name }}</field>     <!-- inline_template：{{ }} -->
    <field name="body_html" type="html"><![CDATA[
        <p>Hello <t t-out="object.partner_id.name"/></p>          <!-- QWeb 正文 -->
    ]]></field>
</record>
```

**要点**：

- **渲染引擎改由字段参数声明**：15.0 的 `mail.template.body_html` 定义为
  `fields.Html('Body', render_engine='qweb', translate=True, sanitize=False)`——
  14.0 同一定义没有 `render_engine`。这是「正文走 QWeb、单行字段走 inline_template」的落地点。
- **XML 数据里没有 `type="qweb"` 这种写法**（15.0 全库 XML 零出现，写了会报错）。
  正文用 `type="html"`；14.0 里少数 `type="xml"` 的 body 写法在 15.0 已不存在，统一改 `type="html"`。
- **`_render_template` 的 engine 枚举变了，且是硬校验**：

  | | 14.0 | 15.0 |
  |---|---|---|
  | 默认 engine | `jinja` | `inline_template` |
  | 允许值 | `jinja`、`qweb` | `inline_template`、`qweb`、`qweb_view` |
  | 传 `engine='jinja'` | 正常 | 抛 `ValueError` |

  自定义代码里显式传 `engine='jinja'` 的地方必须改；`_render_template_jinja` /
  `_render_jinja_eval_context` 这两个方法在 15.0 已不存在（由 `_render_template` + inline_template 取代）。

- `${ ... }` 旧语法不再解析 → 正文用 `t-out`（见第 2 章的转义陷阱），单行字段用 `{{ }}`。
- 15.0 提供 `convert_inline_template_to_qweb()`（`odoo.tools.rendering_tools`），
  用于把旧 Jinja 内联模板批量转成 QWeb 写法，迁移存量模板时可用。
- 源码依据：odoo/odoo#77074。
- 扫描 id：`jinja-dollar`（正则 `\$\{` 捕捉旧 Jinja）、`engine-jinja`（正则 `engine\s*=\s*['"]jinja`）。

---

## 5. 前端 / 资产：ES 模块 `.esm.js`、资产声明进 `__manifest__.py`  — CONFIRMED

### 5.1 ES 模块需改名 `.esm.js`

以 `/** @odoo-module **/` 开头的 JS 文件（ES module）必须改名，使文件名以 **`.esm.js`** 结尾
（同时更新资产引用），以便 ESLint 兼容。

```text
static/src/js/foo.js      ->  static/src/js/foo.esm.js
```

- 扫描 id：`odoo-module-esm`（正则 `@odoo-module` 在 `.js` 文件，且文件名非 `.esm.js`）。

### 5.2 资产声明移入 manifest（`qweb` 键静默失效）

15.0 起 JS / SCSS / QWeb 模板的声明统一进 `__manifest__.py` 的 **`assets`** 键，XML `<template>`
里的 `<link>`/`<script>` 资产节点与 manifest 的 `qweb` 键一并作废。官方模块的迁移幅度可以直接量化：

| | 14.0 | 15.0 |
|---|---|---|
| manifest 用 `assets` 键的模块数 | **0** | 179 |
| manifest 用 `qweb` 键的模块数 | 77 | 1（上游遗漏） |

```python
# __manifest__.py（15.0）
{
    'assets': {
        'web.assets_backend': ['my_module/static/src/js/foo.esm.js',
                               'my_module/static/src/scss/foo.scss'],
        'web.assets_qweb': ['my_module/static/src/xml/**/*'],
    },
}
```

- 路径相对**仓库根目录**（不是模块目录），支持 glob（`**/*`）。
- **最危险的一点：`qweb` 键不报错，只是被静默忽略**。15.0 里 `l10n_ae_pos` 仍写着
  `'qweb': [...]`（官方遗漏，至今没报错），但那些模板并不会因此加载。所以「模块能装、界面缺块」
  这种症状，第一嫌疑就是资产没声明到 `assets` 里——必须用扫描器查，不能靠启动报错发现。
- 15.0 新增 `ir.asset` 模型承接这些声明（见第 9.1 节），自定义 `assets_*.xml` 可改为 `ir.asset` 记录。
- 旧写法 `<template id="assets_backend" inherit_id="web.assets_backend">` 在 15.0 不再生效
  （`web.assets_backend` 已不是可继承的 QWeb 视图），必须整体改写成 manifest `assets`。
- 扫描 id：`qweb-key`（正则 `'qweb'` 在 `__manifest__.py`）、`xml-asset-tag`（XML 里 `<script src=...>`
  / `<link rel="stylesheet">` 出现在 `static/src/xml` 下）。

---

## 6. 测试：`SavepointCase` 与 `Environment.manage()`（弃用，非移除）  — CONFIRMED

这两条常被写成「15.0 移除」，实际都是**保留但弃用**（15.0 源码仍在，抛 `DeprecationWarning`）。
区别在于：`SavepointCase` 的**语义在 15.0 变了**，所以即便名字还能用，行为也已经不同——
这是本条比「改名」更值得注意的地方。

### 6.1 `SavepointCase`：别名被合并，事务语义随之改变

```python
# 14.0
class SavepointCase(SingleTransactionCase): ...      # 整类一个事务 + savepoint
# 15.0
class SavepointCase(TransactionCase):                 # 只是别名，且已弃用
    def __init_subclass__(cls, **kwargs):
        warnings.warn("Deprecated class SavepointCase has been merged into TransactionCase",
                      DeprecationWarning, stacklevel=2)
```

15.0 起每个测试方法各自一个事务（`TransactionCase` 语义），不再是「整类单事务 + savepoint 回滚」。
依赖「类级共享数据 + 回滚」的测试会因此失败或变慢，即使你把类名原样留着也一样。

```python
# Before（14.0）
from odoo.tests.common import SavepointCase
class MyTest(SavepointCase): ...

# After（15.0）
from odoo.tests.common import TransactionCase
class MyTest(TransactionCase): ...
```

- 同类改名：`HttpSavepointCase` → `HttpCase`（15.0 亦为弃用别名）。
- 扫描 id：`savepoint-case`（正则 `SavepointCase`）。
- **处置建议**：一次性替换到位，不要依赖弃用别名——它的行为已经变了，等于「名字没报错但测试语义悄悄换了」。

### 6.2 `Environment.manage()`：变成 no-op

```python
# 14.0
with Environment.manage():
    env = Environment(...)
# 15.0：manage() 只剩一个 yield，并告警
@classmethod
def manage(cls):
    warnings.warn("Since Odoo 15.0, Environment.manage() is useless.",
                  DeprecationWarning, stacklevel=2)
    yield
```

```python
# After（15.0）：直接创建 Environment，无需 manage()
env = Environment(...)
```

- 扫描 id：`env-manage`（正则 `Environment\.manage`）。
- **行为无差异**（本来就是空操作），删掉即可；只是清理代码卫生，不影响功能。

---

## 7. 安全与 `res.groups`（14→15 不变）  — CONFIRMED

- `ir.model.access.csv`、`ir.rule`、`res.groups` 的写法在 14→15 **不变**。
- 注意：**`ir.model.data` 的查询方法在 15.0 私有化**（见第 3 章），但这不影响 `ir.model.access` 的正常写法。
- 安全文件（CSV/XML）**无需改动**。

> **红线**：勿套用 18→19 的 `res.groups` privilege 模型或 19→20 的 `ir.access.csv` 改动——远晚于 15.0。

---

## 8. HTTP / 邮件 / 二进制（其它不变）  — CONFIRMED

- `http.route`、`request.env`、`http.Controller` 在 14/15 一致；`type='json'` 仍是 `json`
  （重命名为 `jsonrpc` 是 **18.1**）。
- 邮件 `message_post(body=..., message_type=...)` 行为一致；`subtype` → `subtype_xmlid` 是
  **13→14** 的变更，本对不涉及（见 8.1 的反证）。
- `get_resource_path` 在 14/15 仍使用（`file_path` 是 **16→17** 改名）。
- `Binary` 字段默认存储行为 14/15 一致（默认存 `ir.attachment` 自 **13.0** 起）。

### 8.1 `subtype` → `subtype_xmlid`：**不属本版本对**（属 13→14）

这条长期被社区资料归入 14→15，源码复核后证伪。`mail_thread.message_post` 的参数演变：

| 版本 | 签名中的 subtype 参数 |
|---|---|
| 11.0 / 12.0 | `subtype=None` |
| 13.0 | `subtype_id=False, subtype=None`（过渡期，新旧并存） |
| 14.0 | `subtype_xmlid=None, subtype_id=False` |
| 15.0 | `subtype_xmlid=None, subtype_id=False`（与 14.0 完全一致） |

也就是说：**`subtype` 参数在 13.0→14.0 就被 `subtype_xmlid` 取代了**，14→15 这一跳不需要动它。
代码里若还写着 `subtype=`，说明该模块连 14.0 都没真正迁到位，应回到 13→14 烹饪书处理。

结论：本对**不需要**做 subtype 改造，扫描器也不再报此项。

---

## 9. 模块 / 模型 / 字段映射

### 9.0 框架级映射

| 14.0 | 15.0 | 类别 | 可信度 |
|---|---|---|---|
| QWeb `t-raw`（不转义） | `t-out`（**默认转义**，`Markup` 值不转义） | 模板指令 | CONFIRMED |
| QWeb `t-esc` | `t-out`（`t-esc` 已 deprecated） | 模板指令 | CONFIRMED |
| 邮件模板 Jinja（`${ }`） | QWeb 正文（`render_engine='qweb'`）+ inline_template（`{{ }}`） | 邮件渲染 | CONFIRMED |
| `_render_template(engine='jinja')` | `engine='inline_template'`（传 `jinja` 抛 `ValueError`） | 邮件 API | CONFIRMED |
| `ir.model.data.xmlid_lookup` 等公共方法 | `_xmlid_lookup` / `_xmlid_to_res_id` | 数据 API | CONFIRMED |
| ES module `foo.js`（`@odoo-module`） | `foo.esm.js` | 前端文件 | CONFIRMED |
| 资产在 XML `<template>` / manifest `qweb` 键 | `__manifest__.py` `assets` 键（`qweb` 键静默失效） | 资产机制 | CONFIRMED |
| `SavepointCase`（继承 `SingleTransactionCase`） | `TransactionCase`（旧名为弃用别名，语义已变） | 测试基类 | CONFIRMED |
| `with Environment.manage():` | 直接 `Environment(...)`（`manage()` 成 no-op） | 测试/环境 | CONFIRMED |

**本版本对不涉及**的重大重命名（红线）：`payment.acquirer`→`payment.provider`（15→16）、
`coupon`→`loyalty`（15→16）、`stock.production.lot`→`stock.lot`（15→16）、
`ir_translation`→JSONB（15→16）、`attrs`/`states` 硬拒（16→17）、`tree`→`list`（17→18）、
`name_get` 移除（17→18）、`track_visibility`→`tracking`（12→13）、
`subtype`→`subtype_xmlid`（**13→14**）、`t-raw` 的**彻底移除**（**15→16**）。

### 9.1 核心领域模型变更（本版本对必查）— CONFIRMED

14→15 共有 **17 条**核心模型变更（14 条移除/新增/结构性调整 + 3 条专章叙述），均由 14.0 / 15.0
源码模型集 diff（CE 全库：移除 21 个模型、新增 111 个）与字段级 diff 核实，与
`Core_Models_Changelog.md` 同源。它们不属于「框架改名」，最容易被框架清单漏掉。

#### 9.1.1 库存：盘点换代（头号断裂）

`stock.inventory` 与 `stock.inventory.line` 在 15.0 **整体移除**。盘点不再是一张独立单据，
改为在 `stock.quant` 上直接录入盘点数量，并新增 `stock.inventory.adjustment.name` 给这批调整命名。

| 14.0 | 15.0 | 说明 |
|---|---|---|
| `stock.inventory`（盘点单） | 移除 | 盘点改 `stock.quant` 的盘点模式 |
| `stock.inventory.line` | 移除 | 明细即 quant 行的盘点数量 |
| — | `stock.quant.inventory_date` | 盘点日期 |
| — | `stock.quant.inventory_quantity_set` | 是否已录入盘点数（判断入口） |
| — | `stock.quant.inventory_diff_quantity` | 盘点差异（算好的差额） |
| — | `stock.quant.inventory_quantity_auto_apply` | 自动应用数量 |
| — | `stock.quant.is_outdated` | 盘点数过期标记 |
| — | `stock.inventory.adjustment.name` | 给一次盘点批次命名 |
| — | `stock.inventory.conflict` / `stock.inventory.warning` | 盘点冲突与警告 |

**影响面**：所有依赖「盘点单」的业务都断——自定义盘点报表、按 `inventory_id` 聚合的统计、
盘点审批流、以及任何 `env['stock.inventory']` 的代码。

**迁移动作**：

1. 代码层：`env['stock.inventory']` 全部改为 `env['stock.quant']` + `action_apply_inventory()`；
2. 数据层：历史盘点单在 15.0 无载体，升级前导出归档（OpenUpgrade 会把在途盘点转录为 quant 调整，
   但不保留单据号语义）；
3. 自定义盘点报表改用 `inventory_quantity_set` + `inventory_date` + `stock.inventory.adjustment.name`；
4. 盘点审批流需在新模型上重建，因为没有「单据状态」可挂。

> 这不是「换了个表」，是**作业范式变化**：从「开单—录数—审核—过账」变成「直接改 quant—批量应用」。
> 相关培训与 SOP 也要改。

**同期新增的库存概念模型**（可替代自建逻辑）：`stock.storage.category` / `.capacity`（存储类别与容量约束）、
`stock.package.type`（包装类型）、`stock.replenishment.info`（补货信息：在途/待补）、
`stock.add.to.wave`（波次）、`stock.request.count`（盘点请求）。

#### 9.1.2 会计：支付方式行化（会计头号断裂）

15.0 把日记账上的支付方式从 m2m 改成「行」——新模型 `account.payment.method.line`，每行可单独
指定科目与序号。

| 14.0 | 15.0 |
|---|---|
| `account.journal.inbound_payment_method_ids`（m2m） | `inbound_payment_method_line_ids`（o2m → `account.payment.method.line`） |
| `account.journal.outbound_payment_method_ids`（m2m） | `outbound_payment_method_line_ids`（o2m） |
| `account.payment.method` 直接挂日记账 | `account.payment.method` 降为「方式目录」，配置落到行上 |

`account.payment.method.line` 的关键字段：`payment_method_id`、`payment_account_id`（该日记账下
这一支付方式用哪个科目）、`sequence`、`journal_id`。

**迁移动作**：所有读写 `inbound_payment_method_ids` / `outbound_payment_method_ids` 的代码、视图、
服务器动作改为 `*_payment_method_line_ids`；自定义支付方式若依赖「日记账级共用科目」，
现在可以（也应该）改为按行配 `payment_account_id`。

#### 9.1.3 会计：税额汇总与税基字段

| 14.0 | 15.0 | 影响 |
|---|---|---|
| `account.move.amount_by_group`（Binary） | 移除，改 `tax_totals_json`（Char） | 发票/账单模板里按税组展示金额的自定义代码会断；改读 `tax_totals` widget 或解析 JSON |
| `sale.order.amount_by_group`（Binary） | 移除，改 `tax_totals_json` | 报价单/销售单同理 |
| `account.move.line.tax_exigible` | 移除，改 `account.move.always_tax_exigible` | 行级税基判断逻辑要上移 |
| `account.move.line.tax_fiscal_country_id` | 移除，改 move 的 `tax_country_id` / `tax_country_code` | 税务国家判断从行级改单据级 |
| `account.move.tax_cash_basis_move_id` | `tax_cash_basis_origin_move_id` | 现金基础税额的溯源字段改名 |
| — | `account.move.line.group_tax_id`、`tax_tag_invert` 新增 | 税额分组与标签反向 |

#### 9.1.4 产品：类型细分与模板价格

| 14.0 | 15.0 | 说明 |
|---|---|---|
| — | `product.template.detailed_type`（新增） | `consu`/`product`/`service`，与 `type` 并存；区分「可库存产品」与「消耗品」。**18.0 又被移除** |
| `product.template.lst_price` | 移除 | 模板级公开价格没了，仅保留在 `product.product.lst_price`（15.0 标签改 "Sales Price"）；模板层经 `product_variant_id.lst_price` 取 |
| `product.template.custom_message` / `inventory_availability` / `event_ok` | 移除 | 由 `product_tooltip` / `allow_out_of_stock_order` + `show_availability` 等替代 |

> `detailed_type` 是**新增**不是改名——`type` 在 15.0 仍是主字段。若目标版本 ≥18.0，
> 直接写 `is_storable`，省一次返工（`detailed_type` 在 18.0 被移除）。

#### 9.1.5 HR：多人休假、加班抵扣与合同结构

`hr.leave` 在 15.0 从「一人一单」变成可覆盖多员工，并接入加班抵扣：

| 方向 | 字段 |
|---|---|
| 新增 | `employee_ids`(m2m)、`multi_employee`、`employee_company_id`、`employee_overtime` |
| 新增 | `overtime_id`、`overtime_deductible`（加班抵扣休假） |
| 新增 | `attachment_ids`、`supported_attachment_ids`（休假附件）、`holiday_allocation_id` |
| 移除 | `payslip_status` |

配套新模型：`hr.leave.accrual.plan` / `.level`（休假累积计划）、`hr.contract.history`、
`hr.contract.type`、`hr.departure.reason`、`hr.work.location`、`hr.attendance.overtime`。

> 自定义休假审批若写死 `holiday_status_id` 的单员工逻辑，要复核 `employee_ids` 的多员工分支；
> 自建「离职原因」「工作地点」下拉可改为标准模型。

#### 9.1.6 项目：里程碑与项目更新

`project.milestone`、`project.update` 在 15.0 新增。项目域从「只有任务」扩展到
「任务 + 里程碑 + 状态汇报」。同期新增 `project.collaborator`（协作人）、`project.project.stage`、
`project.task.stage.personal`（个人任务阶段）。

**迁移动作**：自建里程碑表可迁到 `project.milestone`；周期性周报可改用 `project.update`。

#### 9.1.7 邮件与协作：审核模型移除、表情回应

| 方向 | 内容 |
|---|---|
| 移除 | `mail.moderation` 模型；`mail.message` 的 `moderation_status`/`moderator_id`/`need_moderation` 一并移除 |
| 移除 | `mail.message.channel_ids`（m2m）、`no_auto_thread` |
| 新增 | `mail.message.reaction_ids`（表情回应）、`author_guest_id`（配 `mail.guest` 访客） |
| 新增 | `mail.group` 族、`mail.composer.mixin`、`mailing.contact.to.list` |

**迁移动作**：任何读 `moderation_status` 的代码删除；论坛/群组自建审核逻辑改挂标准流程；
自定义邮件编写模板可继承 `mail.composer.mixin`。

#### 9.1.8 平台侧新模型（可替代自建）

| 新模型 | 用途 |
|---|---|
| `ir.asset` | 资产 bundle 记录化，与 manifest `assets` 键配套；自定义 `assets_*.xml` 可改记录 |
| `res.users.settings` / `.volumes` | 用户偏好独立模型，替代在 `res.users` 上堆字段 |
| `crm.team.member` | 销售团队成员独立模型（`crm_team_member_ids` o2m）；`member_ids` m2m **仍保留** |
| `avatar.mixin`、`website.searchable.mixin`、`res.partner.iap` | 通用 mixin / 集成辅助 |

#### 9.1.9 移除的模型（会直接 `KeyError`）

`phone.validation.mixin`、`project.task.create.sale.order`、`calendar.contacts`、
`closing.balance.confirm.wizard`、`export.computed.binary`、`lunch.product.report`、
`website.mass_mailing.popup`、`mail.moderation`。

- **`phone.validation.mixin` 最需要注意**：它是很多自定义伙伴/员工模块的继承基类。
  15.0 改调 `phone_validation` 的工具函数（`phone_validation.phone_format`、
  `phone_validation.tools.phone_parse`），不再有 mixin 可继承。
- `calendar.contacts` 移除后，联系人日历改由 `res.partner` 侧能力承载。

#### 9.1.10 文本字段 `Text` → `Html`（横切）

以下字段在 15.0 从 `Text` 改为 `Html`：`account.move.narration`、`sale.order.note`、
`product.template.description`、`res.partner.comment`、`stock.picking.note`。

**影响**：视图 widget 从 textarea 变为 HTML 编辑器；代码里假设纯文本的地方（`strip_tags`、
按 `\n` 切行、往 QWeb 里塞未转义值）要复核——尤其在配合第 2 章的 `t-out` 转义规则时。

### 9.2 本章与其他文档的关系

| 需求 | 去处 |
|---|---|
| 某业务模块的逐字段改名 | OpenUpgrade `upgrade_analysis.txt` |
| 跨版本模型演变全局索引 | `Core_Models_Changelog.md` |
| 本对框架级改名 | 本章主表 |

---

### 9.3 反例表：被源码证伪的说法

| 流传说法 | 源码事实 |
|---|---|
| 15.0 移除了 `t-raw` | 15.0 只是 deprecated（可运行 + warning），**16.0 才移除** |
| `t-out` 等价于「不转义」的 `t-raw` | `t-out` 编译为 `escape(content)`，**默认转义**；只有 `Markup` 值才不转义 |
| 15.0 移除了 `SavepointCase` 别名 | 保留为弃用别名，但**继承关系从 `SingleTransactionCase` 变为 `TransactionCase`**，事务语义已变 |
| 15.0 移除了 `Environment.manage()` | 保留为 no-op + `DeprecationWarning` |
| 15.0 移除了对 `ir.model*` 的直接访问 | 未移除；`ir.model` / `ir.model.fields` 的 search 与 `_fields` 均正常。真正断裂是 **`ir.model.data` 查询方法私有化** |
| 修 `ir.model.data` 用 `_get_id()` | **`_get_id(module, xml_id)` 本身就在 15.0 被移除**——这条「修复建议」是把人往坑里推。用 `_xmlid_to_res_id` 或 `env.ref()` |
| `subtype` → `subtype_xmlid` 属 14→15 | 属 **13→14**；14.0 与 15.0 的 `message_post` 签名完全一致 |
| 邮件模板 XML 正文写 `type="qweb"` | 15.0 全库 XML 中 `type="qweb"` 零出现，写了会报错；引擎由字段参数 `render_engine='qweb'` 声明 |
| manifest `qweb` 键在 15.0 会报错 | 不报错，**静默忽略**（官方 `l10n_ae_pos` 至今仍留着该键） |

---

## 10. 测试与校验

- 测试基类：`TransactionCase` 在 14/15 均可用；`SavepointCase` 在 15.0 是**弃用别名且语义已变**
  （14.0 继承 `SingleTransactionCase`，15.0 继承 `TransactionCase`）。
- `Environment.manage()`：15.0 为 no-op + 弃用警告，删掉即可。
- 校验：`odoo-bin -u <module> --test-tags /<module>`，**必须开 `--dev=all` 才能看到弃用警告**
  （重点：`t-raw`、`t-esc`、`SavepointCase`、`Environment.manage`）。
- 前端：`t-raw` 在 15.0 只 warning、**不会在加载时报错**，清理是否彻底只能靠扫描器复查；
  资产是否生效也没有报错可依（`qweb` 键静默失效），需在浏览器里确认 bundle 里出现了目标文件。


---

## 11. `upgrade_code` codemod（14→15 无）  — CONFIRMED

`odoo-bin upgrade_code` 的 codemod 引擎**从 18.0 才存在**（17.0 及更早均无 `odoo/upgrade_code/` 模块）。
因此 **14→15 零 codemod**，全部为手工改动 + 数据库级 `migrations/15.0/` 脚本（由 OpenUpgrade 处理）。

> ⚠️ **勿让用户跑 `upgrade_code --from 14.0`**——15.0 安装中该命令不存在，会报命令未找到。

---

## 12. 迁移实战清单

1. **扫描**：`scan_addon.py` 找出 `t-raw`/`t-esc`、`xmlid_lookup`/`get_object_reference`/`_get_id`、
   `engine='jinja'`、`${ }`、`@odoo-module` 的 `.js`、`SavepointCase`、`Environment.manage`、
   manifest `qweb` 键、`inbound/outbound_payment_method_ids`、`amount_by_group`、`tax_exigible`、
   `stock.inventory`、`phone.validation.mixin`。
2. **QWeb**：`t-raw`/`t-esc` → `t-out`，按第 2 章判断值类型——**只有 `Markup` 值才不转义**。
3. **ir.model.data**：`_get_id`/`get_object_reference`/`xmlid_to_*` → `env.ref()` 或
   `_xmlid_to_res_id`（注意 `_get_id` 本身已被移除，别照抄旧教程）。
4. **邮件模板**：`${ }` → `{{ }}`；正文引擎由字段参数 `render_engine='qweb'` 声明，XML 用
   `type="html"`（没有 `type="qweb"` 这种写法）；代码里 `engine='jinja'` → `engine='inline_template'`。
5. **前端**：`@odoo-module` 文件改 `.esm.js`；资产从 XML/`qweb` 键移入 manifest `assets`。
6. **测试**：`SavepointCase` → `TransactionCase`（事务语义已变，复核依赖类级共享数据的测试）；
   删 `Environment.manage()`。
7. **会计**：`journal.*_payment_method_ids` → `*_payment_method_line_ids`；
   `amount_by_group` → `tax_totals_json`；`tax_exigible` → `always_tax_exigible`。
8. **库存**：`stock.inventory` → `stock.quant` + `action_apply_inventory()`，历史盘点先导出归档。
9. **产品 / 文本字段**：`product.template.lst_price` → `product_variant_id.lst_price`；
   `note`/`narration`/`description`/`comment` 改 Html 后复核 widget 与纯文本假设。
10. **DB 迁移**：模块 `migrations/15.0/` 写数据脚本（如需）。
11. **校验**：`-u` + 测试 + `--dev=all` 看弃用警告；资产加载要人工确认（`qweb` 键静默失效）。
12. **出报告**：列出每处改动与人工确认项（t-raw 清理数、资产 bundle 生效情况、盘点历史归档）。


---

## 附录 A：研究来源与溯源

**事实基准**：Odoo CE 源码树 `14.0` / `15.0`（判定「首次出现版本」时追到 11.0–17.0）。
核对手法：

- **模型集 diff**：全库提取 `_name = '...'` 定义做集合比较——14.0 有 927 个、15.0 有 1017 个，
  区间内**移除 21 个、新增 111 个**；
- **字段级 diff**：`scripts/diff_core_models.py --repo <CE> --ref-a 14.0 --ref-b 15.0 --model <model>`；
- **定点核验**：`git grep` 必须单双引号都查（`_name = "..."` 与 `_name = '...'` 在 Odoo 源码里并存），
  模型"消失"时再查一次目标版本的其他模块目录，排除模块搬迁。

**线索来源**（仅作线索；与源码冲突处已订正）：

- OCA《Migration to version 15.0》——`t-raw`→`t-out`、Jinja→QWeb/inline_template、`.esm.js`
  改名、资产进 manifest `assets`、`SavepointCase`→`TransactionCase` 等条目**方向正确**；
  但其「移除」措辞在 15.0 多实为「弃用」（`t-raw`、`t-esc`、`SavepointCase`、`Environment.manage()`）。
- 社区汇总帖（Odoo 论坛 / Cybrosys / apps.odoo）——`subtype`→`subtype_xmlid` 归入 14→15 即由这类
  资料误传，源码比对后确认为 **13→14**。
- PR 引用（#69120 / #77074 / #62031 / 01875541b1a8）保留作为**查证入口**，但结论一律以本地源码为准：
  其中「#69120 = ir.model* 访问移除」在本轮复核中未能从源码得到支持，已改写为
  `ir.model.data` 方法私有化（见第 3 章）。

**结论对照**：被推翻的说法见 **9.3 反例表**；跨版本模型索引见 `Core_Models_Changelog.md`
（14→15 共 17 条，与本文件第 9 章逐条对应）。
