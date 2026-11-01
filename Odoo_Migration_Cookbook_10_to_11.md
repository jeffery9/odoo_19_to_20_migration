# Odoo 迁移烹饪书：10.0 → 11.0

> 配套技能：`Odoo10to11Migration/`（SKILL + 6 份参考表 + 扫描器）
> 作用域：仅 **10.0 → 11.0** 破坏性变更。更晚改动（如 11→12 的 `@api.one` 移除、`fields.Date` 运行时对象化、`parent_path` 等）一律不在本卷。

## 目录

1. 导言与版本作用域
2. 头号断裂：Python 3 强制（10.0 仍 Python 2/3 双兼容，11.0 仅 Python 3）
3. 包命名空间：`openerp` → `odoo`（9→10 已完成，11.0 清理兼容别名）
4. Python 3 语法迁移清单
5. 工作流（Workflow）完全移除
6. 报表 API 重写（QWeb 报表）
7. `ir.cron`：`model` → `model_id`
8. 模块重命名与合并
9. 视图 / QWeb / 前端
10. HTTP / 邮件 / 二进制
11. 安全与 `res.groups`（10→11 微调）
12. 模块 / 模型 / 字段映射
13. 测试与校验
14. `upgrade_code` codemod（10→11 无）
15. 迁移实战清单
16. 附录 A：研究来源与溯源

---

## 1. 导言与版本作用域

Odoo **11.0（2017-10）** 是第一个 **仅支持 Python 3** 的 LTS 版本（最低 Python 3.5），同时彻底移除了工作流（Workflow）引擎、重写了 QWeb 报表调用接口、并把若干模块改名或合并进核心。10.0 仍保持 Python 2.7 / 3.5 双兼容，因此 10→11 的头号断裂是 **Python 2 → Python 3 代码迁移**，其次才是 Odoo 框架层面的 API 清理。

### 版本作用域红线（勿套用更晚版本的改动）

- `@api.one` 装饰器移除 → **11→12**（`api.one` 在 11.0 仍存在）。
- `fields.Date` / `fields.Datetime` 运行时对象化、`from_string` 移除 → **11→12**。
- `ir.actions.act_window.view` 模型移除 → **11→12**。
- `do_notify` / `do_warning` 移除 → **11→12**。
- `t-field-options` → `t-options` → **11→12**。
- `_parent_store`：`parent_left`/`parent_right` → `parent_path` → **11→12**。
- `from openerp import ...` → `from odoo import ...` 改名 → **9→10**（11.0 只是清理兼容别名，主改名在 9→10）。
- `__openerp__.py` → `__manifest__.py` → **9→10**。

> 本卷只处理 10→11 区间；任何属于 11→12 或 9→10 的条目，仅在本卷"红线"处点名，不展开。

### 配套技能参考表（skill references）

- `Odoo10to11Migration/references/orm-api.md` —— Python 3 语法、包命名空间、Workflow 移除、报表 API。
- `Odoo10to11Migration/references/views-qweb.md` —— 视图 / QWeb / 前端变更。
- `Odoo10to11Migration/references/models-mapping.md` —— 模块重命名 / 合并映射表。
- `Odoo10to11Migration/references/security.md` —— `res.groups` 微调（`base.group_configuration` → `base.group_system`）。
- `Odoo10to11Migration/references/http-rpc-mail.md` —— 控制器 / 邮件 / 二进制（基本不变）。
- `Odoo10to11Migration/references/upgrade-code.md` —— 11.0 无 `upgrade_code` codemod，全部手工。

---

## 2. 头号断裂：Python 3 强制  — CONFIRMED

10.0 仍双兼容 Python 2.7 与 3.5；**11.0 官方只支持 Python 3.5+，不再提供 Python 2 解释器路径**。所有自定义模块必须改写为 Python 3 语法才能安装。

### Before（10.0，Python 2 代码）

```python
# -*- coding: utf-8 -*-
print "Hello", partner.name          # Python 2 print 语句
for k, v in ctx.iteritems():         # dict.iteritems()
    if ctx.has_key('lang'):          # dict.has_key()
        pass
u = unicode(partner.name)            # unicode 类型
for i in xrange(0, 10):              # xrange
    pass
try:
    do()
except RuntimeError, e:              # 旧式 except
    raise osv.except_osv('Err', e)
from StringIO import StringIO        # StringIO
import urllib2                       # urllib2
```

### After（11.0，Python 3）

```python
# 不再需要 -*- coding: utf-8 -*-（Python 3 源码默认 UTF-8）
print("Hello", partner.name)                       # print() 函数
for k, v in ctx.items():                           # items()
    if 'lang' in ctx:                             # in
        pass
u = str(partner.name)                              # str
for i in range(0, 10):                             # range
    pass
try:
    do()
except RuntimeError as e:                          # as
    raise UserError(_('Err: %s') % e)
from io import StringIO                            # io.StringIO
import urllib.request                              # urllib.request / werkzeug.urls
```

要点：

- `print` 语句 → `print()` 函数。
- `dict.iteritems()` / `itervalues()` / `iterkeys()` → `items()` / `values()` / `keys()`。
- `dict.has_key(k)` → `k in d`。
- `unicode` / `basestring` → `str`；`long` → `int`。
- `xrange` → `range`。
- 旧式 `except E, e:` → `except E as e:`。
- `StringIO` / `cStringIO` → `io.StringIO` / `io.BytesIO`。
- `urllib` / `urllib2` / `urlparse` → `urllib.request` / `urllib.parse`（Odoo 中通常改 `requests` 或 `werkzeug.urls`）。
- 整数除法 `/` 在 Python 3 返回浮点；需要整除用 `//`。
- Odoo 10 起提供的 `openerp.tools.pycompat` 兼容垫片（如 `izip`/`imap`/`ifilter`/`unichr`/`text_type`/`string_types`/`to_native`）在 **11.0 被移除**，不要再依赖。

---

## 3. 包命名空间：`openerp` → `odoo`  — CONFIRMED（9→10 主改名，11.0 清理别名）

包目录 `openerp` 在 **9→10** 已正式改名为 `odoo`（OCA 10.0 迁移指南明确要求 `from openerp` → `from odoo`）。到 11.0，旧的 `openerp` 兼容别名被彻底移除，残留的 `import openerp` 会直接 `ImportError`。

### Before（10.0 残留写法）

```python
import openerp
from openerp import models, fields, api
from openerp.osv import osv
from openerp.addons.base.ir.ir_config_parameter import ...
```

### After（11.0）

```python
import odoo
from odoo import models, fields, api
from odoo.osv import osv                 # 仍可用，但新代码建议 from odoo import models
from odoo.addons.base.models.ir_config_parameter import ...
```

> 注意：`from openerp import ...` 改名属于 **9→10** 主线；若模块在 10.0 已迁移干净则 10→11 无需改动。但 11.0 删除了 `openerp` 包的兼容别名，所以 **未迁移的 `openerp.*` 引用在 11.0 必然失败**，应在 10→11 顺手清理。

---

## 4. Python 3 语法迁移清单  — CONFIRMED

下面按出现频率列出 10→11 必须核对的 Python 3 语法点（对应 Odoo 官方 `python3.rst`）：

| Python 2 | Python 3 | 说明 |
|---|---|---|
| `print x` | `print(x)` | 语句→函数 |
| `d.iteritems()` | `d.items()` | 迭代视图 |
| `d.has_key(k)` | `k in d` |  |
| `unicode(x)` | `str(x)` |  |
| `basestring` | `str` | 类型判断 |
| `xrange(n)` | `range(n)` |  |
| `except E, e:` | `except E as e:` |  |
| `StringIO.StringIO` | `io.StringIO` | 文本 |
| `cStringIO.StringIO` | `io.BytesIO` | 二进制 |
| `urllib2.urlopen` | `requests.get` / `urllib.request` | Odoo 依赖 requests/werkzeug |
| `urllib.quote` | `werkzeug.urls.url_quote` |  |
| `a / b`（期望整数） | `a // b` | 整除 |
| `openerp.tools.pycompat.*` | 删除 | 11.0 移除垫片 |

> 模块内同目录的相对导入在 11.0 强制：`from . import submod` 而非 `import submod`（否则 ImportError）。

---

## 5. 工作流（Workflow）完全移除  — CONFIRMED

工作流在 10.0 已弃用但仍可用；**11.0 将其彻底移除**。`workflow` XML 记录、`<workflow>` 按钮、`wkf` 相关模型与 `signal_workflow()` 调用全部失效。

### Before（10.0）

```xml
<record id="test_workflow" model="workflow">
    <field name="name">test.wkf</field>
    <field name="osv">test.model</field>
</record>
<button name="signal_test" type="workflow" states="draft" />
```

```python
self.signal_workflow('invoice_open')
```

### After（11.0）

```xml
<!-- 移除 <record model="workflow"> 与 type="workflow" 按钮 -->
<button name="action_open" type="object" states="draft" />
```

```python
self.action_open()          # 用普通 @api.multi 方法 + 状态字段替代工作流
```

要点：

- 把工作流的活动（activity）/ 转换（transition）改写为模型的 **状态字段 + `@api.multi` 方法 + `<button type="object">`**。
- `signal_workflow()` / `workflow_task()` 调用删除，改为直接调用业务方法。
- 原工作流中"自动触发"的逻辑改用 `@api.model` 的 `cron` 或 `write` 覆写 / `@api.constrains` 实现。
- 扫描 id：`workflow`（正则 `\bworkflow\b|signal_workflow|type="workflow"`）。

---

## 6. 报表 API 重写  — CONFIRMED

QWeb 报表的调用接口在 11.0 重写：`render_html()` → `get_report_values()`，`get_action()` → `report_action()`，`get_html()` → `render_qweb_html()`；`ir.actions.report` 的 `_run_wkhtmltopdf` 参数顺序也变化。

### Before（10.0）

```python
class ReportJournal(models.AbstractModel):
    _name = 'report.account.report_journal'

    @api.model
    def render_html(self, docids, data=None):
        docargs = {'doc_ids': docids, 'docs': self.env['account.move'].browse(docids)}
        return self.env['report'].render('account.report_journal', docargs)

    # 调用端
    return self.env['report'].get_action(self, 'account.report_journal', data=data)
```

### After（11.0）

```python
class ReportJournal(models.AbstractModel):
    _name = 'report.account.report_journal'

    @api.model
    def get_report_values(self, docids, data=None):          # 改名 + 返回 dict
        return {'doc_ids': docids,
                'docs': self.env['account.move'].browse(docids)}

    # 调用端
    return self.env.ref('account.action_report_journal').report_action(self, data=data)
```

要点：

- `render_html(self, docids, data)` → `get_report_values(self, docids, data=None)`，且直接 `return` 渲染上下文 dict（不再调 `self.env['report'].render(...)`）。
- `self.env['report'].get_action(...)` → `self.env.ref(<action_xmlid>).report_action(self, data=...)`。
- `get_html()` → `render_qweb_html()`（如覆写底层渲染）。
- 扫描 id：`report-api`（正则 `render_html|get_action|get_html`）。

---

## 7. `ir.cron`：`model` → `model_id`  — CONFIRMED

定时任务 `ir.cron` 在 11.0 用 `model_id`（Many2one 到 `ir.model`，类似记录规则），并新增 `code` 字段直接写 Python，替代旧 `model` + `function` + `args` 组合。

### Before（10.0）

```xml
<record id="cron_test" model="ir.cron">
    <field name="name">Test</field>
    <field name="model" eval="'test.model'"/>
    <field name="function">_sync_request</field>
    <field name="args" eval="'(20,)'"/>
    <field name="interval_number">6</field>
    <field name="interval_type">hours</field>
</record>
```

### After（11.0）

```xml
<record id="cron_test" model="ir.cron">
    <field name="name">Test</field>
    <field name="model_id" ref="model_test_model"/>      <!-- ref 指向 ir.model -->
    <field name="state">code</field>
    <field name="code">model._sync_request(20)</field>
    <field name="interval_number">6</field>
    <field name="interval_type">hours</field>
</record>
```

要点：

- `model`（字符串 eval） → `model_id`（ref 到 `ir.model` 记录）。
- `function` + `args` → `state="code"` + `code` 字段里的 Python 调用（或保留 `state="object"` 配 `model_id` + `function`/`args` 也可，但 `model` 字段本身已弃用）。
- 扫描 id：`ir-cron-model`（正则 `model\s*=\s*eval=.*ir.cron|ir\.cron` 配合 `name="model"` 在 cron 记录内，建议手工核对）。

---

## 8. 模块重命名与合并  — CONFIRMED

| 操作 | 10.0 | 11.0 | 说明 |
|---|---|---|---|
| 改名 | `sale` | `sale_management` | 销售模块改名 |
| 改名 | `account_accountant` | `account_invoicing` | 会计辅助改名 |
| 合并 | `account_tax_cash_basis` | `account` | 并入 account |
| 合并 | `report` | `web` | report 模块并入 web |

要点：

- `depends` 里的模块名需同步更新（`sale` → `sale_management`）。
- 被合并模块的 XML-ID 前缀随之变化（如 `report.*` 报表 action 可能迁移到 `web` 或对应业务模块），需逐条核对。
- 扫描 id：`module-rename`（正则 `depends[\s\S]*\bsale\b`（非 sale_management）或 `account_accountant` / `account_tax_cash_basis` / `report` 出现在 depends/import）。

---

## 9. 视图 / QWeb / 前端  — CONFIRMED（含 [verify]）

11.0 前端从 Odoo 自研 JS 框架切换到 **OWL 之前的第一代重构**，同时 Bootstrap 升级。视图层面 10→11 变化相对温和，但需注意：

- 同目录静态资源相对引入在 Python 3 下更严格；JS/CSS/SCSS 内 `import` 路径需为相对。
- 老 `t-*` QWeb 指令基本兼容（大规模 QWeb 重写在 14→15 的 `t-raw` 移除潮，不属本卷）。
- 报表模板（QWeb）的 `report` 调用接口见第 6 节。

> `[verify]` 前端 Bootstrap 具体大版本号（3→4？）属社区描述，无官方 10→11 前端清单；建议以 11.0 源码 `package.json` / `web` 资产为准，必要时收紧本标注。

---

## 10. HTTP / 邮件 / 二进制  — CONFIRMED（基本不变）

- 控制器：`from odoo import http`（10.0 已是 `odoo` 包），`http.Controller` / `route()` 接口 10→11 无破坏性变更。
- 邮件：`mail.template` 渲染仍用 QWeb（Jinja→QWeb 大改在 14→15）；10→11 邮件模板结构基本不变。
- 二进制字段：`Binary` 默认存 `ir.attachment` 的时机在 13.0，10→11 维持原状。
- `pycompat` 垫片移除会影响个别 `http` 工具函数，按第 4 节语法清单处理。

---

## 11. 安全与 `res.groups`（10→11 微调）  — CONFIRMED

- `base.group_configuration` → **`base.group_system`**（10→11 改名，OCA 10.0 指南已记，但残留于 10 代码需在 11 修正）。
- 其余 `security/ir.model.access.csv` 列结构（`perm_read`/`perm_write`/`perm_create`/`perm_unlink`）不变。
- 注意 9→10 已发生的安全组模块化迁移（`base.group_sale_salesman` → `sales_team.group_sale_salesman`、`base.group_hr_user` → `hr.group_hr` 等）若尚未做，应在升级链路中一并补齐（见 `references/security.md`）。

---

## 12. 模块 / 模型 / 字段映射

除第 8 节模块改名/合并外，10→11 模型层无大规模重命名（`account.invoice`→`account.move` 属于 12→13，不属本卷）。需要关注的：

| 项目 | 10.0 | 11.0 | 备注 |
|---|---|---|---|
| `ir.cron.model` | 字符串 eval | `model_id` ref | 第 7 节 |
| `workflow` 模型/XML | 存在 | 移除 | 第 5 节 |
| `base.group_configuration` | 存在 | `base.group_system` | 第 11 节 |
| 报表 `render_html` | 存在 | `get_report_values` | 第 6 节 |

---

## 13. 测试与校验

1. 用 **Python 3.5+** 解释器启动 11.0 实例；`python2 odoo-bin` 直接失败。
2. `python3 Odoo10to11Migration/scripts/scan_addon.py /path/to/addons` 跑扫描，逐条处理 `workflow` / `report-api` / `ir-cron-model` / `module-rename` / `openerp-import` / `py2-syntax` 发现项（全部 `manual`，无 codemod）。
3. 安装模块：先清 `ImportError`（`openerp` 包、`print` 语句、`iteritems` 等）；再清 `AttributeError`（`signal_workflow`、`render_html`）。
4. `python3 -m py_compile **/*.py` 全量编译，确保无 Python 3 语法错误。
5. `odoo-bin -u <module> --test-tags /<module>` 跑测试；`--dev=all` 下清除 `DeprecationWarning`。

---

## 14. `upgrade_code` codemod（10→11 无）  — CONFIRMED

`odoo/upgrade_code/` 引擎自 **18.0** 才出现。10→11 **没有任何 `upgrade_code` 脚本**——所有代码改名、Python 3 改写、Workflow→方法、报表 API 重写均为**手工**。数据库级变更（字段/模型结构）由 **OpenUpgrade** 或官方升级服务处理；本卷只覆盖自定义模块的**代码级**映射。

---

## 15. 迁移实战清单

- [ ] 解释器切到 Python 3.5+；`py_compile` 全量通过。
- [ ] `from openerp` / `import openerp` 全部改为 `odoo`（清理 9→10 残留别名）。
- [ ] `print` 语句→函数，`iteritems`/`has_key`/`xrange`/`unicode`/`basestring`/`StringIO`/`urllib2` 全部改写。
- [ ] `except E, e:` → `except E as e:`；整除用 `//`。
- [ ] 删除所有 `workflow` XML 与 `signal_workflow()`，改用状态字段 + 对象方法按钮。
- [ ] 报表 `render_html`→`get_report_values`、`get_action`→`report_action`。
- [ ] `ir.cron`：`model`→`model_id`（ref 到 `ir.model`），必要时改用 `code` 字段。
- [ ] `depends` 中 `sale`→`sale_management`、`account_accountant`→`account_invoicing`；合并模块 `account_tax_cash_basis`/`report` 引用迁移。
- [ ] `base.group_configuration`→`base.group_system`。
- [ ] 重扫扫描器期望 0 发现；跑测试通过。

---

## 附录 A：研究来源与溯源

- Odoo 官方 Python 3 兼容文档（`documentation/11.0/python3.html`）：11.0 首个仅 Python 3 LTS、弃用 pycompat 垫片。
- OCA `Migration to version 10.0` / `9.0` 指南：openerp→odoo 改名、`__openerp__.py`→`__manifest__.py`、group 模块化、`base.group_configuration`→`base.group_system`。
- Odoo 论坛 v10→v11 经验帖（Anil Kesariya / Niyas Raphy）：Python3 语法、Workflow 移除、报表 `render_html`→`get_report_values`/`get_action`→`report_action`、`sale`→`sale_management`、`account_accountant`→`account_invoicing`、`account_tax_cash_basis`/`report` 合并、`ir.cron` model→model_id。
- Odoo 11 Release Notes：Enterprise/Community 划分、Python 3 强制。
- 11.0 源码核对：`odoo/__init__.py` 无 `openerp` 别名；`openerp.tools.pycompat` 已移除 izip/imap/ifilter/unichr/text_type/string_types/to_native。
