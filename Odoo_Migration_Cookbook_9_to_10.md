# Odoo 迁移烹饪书：9.0 → 10.0

> 配套技能：`Odoo9to10Migration/`（SKILL + 6 份参考表 + 扫描器）
> 作用域：仅 **9.0 → 10.0** 破坏性变更。更晚改动（如 10→11 的 Python 3 强制、工作流移除、报表 API 重写，或 11→12 的 `@api.one` 移除、`fields.Date` 运行时对象化）一律不在本卷。

## 目录

1. 导言与版本作用域
2. 头号断裂：`openerp` → `odoo` 包改名（9→10 主线）
3. 清单文件：`__openerp__.py` → `__manifest__.py`
4. 字段索引：`select = True` → `index = True`
5. 视图 / XML：`position`/`xpath` 字符串选择器 → 属性选择器；`<openerp>`/`<data>` → `<odoo>`
6. 安全组：`base.group_configuration` → `base.group_system`
7. `copy` 方法装饰器：`@api.one` → `@api.multi`
8. 安全组模块化：从 `base` 迁移到各模块（group-move）
9. 视图 / QWeb 其它（基本不变）
10. HTTP / RPC / 邮件（基本不变）
11. 模块 / 模型 / 字段映射
12. 测试与校验
13. `upgrade_code` codemod（9→10 无）
14. 迁移实战清单
15. 红线（勿套用更晚版本）
16. 附录 A：研究来源与溯源

---

## 1. 导言与版本作用域

Odoo **10.0（2016-10）** 是一次"命名与结构清理"版本：框架 Python 包从 `openerp` 正式改名为 `odoo`，模块清单文件从 `__openerp__.py` 改名为 `__manifest__.py`，字段层面的 `select = True` 改为 `index = True`，视图继承的字符串 `position`/`xpath` 选择器要求改用属性（如 `name`）选择器，并顺带完成了安全组从 `base` 模块向各业务模块的模块化迁移。9.0 仍是 `openerp` 包时代，因此本卷的**头号断裂是包改名与清单改名**——任何残留的 `from openerp` 或 `__openerp__.py` 在 10.0 都会直接失败。

### 版本作用域红线（勿套用更晚版本的改动）

- `from openerp` → `from odoo` 主改名 → **本卷（9→10 主线）**；但 10→11 仅清理最后一个 `openerp` 兼容别名（10.0 已是 `odoo` 包）。
- `@api.one` 装饰器**完全移除** → **11→12**（`@api.one` 在 9.0/10.0 仍然存在，本卷只把 `copy` 方法的 `@api.one` 改成 `@api.multi`）。
- `fields.Date` / `fields.Datetime` 运行时对象化、`from_string` 移除 → **11→12**。
- `ir.actions.act_window.view` 模型移除 → **11→12**。
- `account.invoice` → `account.move` → **12→13**。
- `t-field-options` → `t-options` → **11→12**。
- Python 3 强制、工作流移除、报表 API 重写 → **10→11**。

> 本卷只处理 9→10 区间；任何属于 10→11 或 11→12 的条目，仅在本卷"红线"处点名，不展开。

### 配套技能参考表（skill references）

- `Odoo9to10Migration/references/orm-api.md` —— 包改名、`__manifest__.py`、`select`→`index`、`copy` 装饰器、`@api.one`+`@api.onchange` 警告。
- `Odoo9to10Migration/references/views-qweb.md` —— 视图 / XML 选择器清理、`<openerp>`/`<data>`→`<odoo>`。
- `Odoo9to10Migration/references/models-mapping.md` —— 模块 / 模型 / 字段映射（9→10 无大规模重命名）。
- `Odoo9to10Migration/references/security.md` —— `base.group_configuration`→`base.group_system` + 安全组模块化（group-move）。
- `Odoo9to10Migration/references/http-rpc-mail.md` —— 控制器 / 邮件 / 二进制（基本不变，`openerp.http`→`odoo.http` 随主改名）。
- `Odoo9to10Migration/references/upgrade-code.md` —— 10.0 及更早无 `upgrade_code` codemod，全部手工。

---

## 2. 头号断裂：`openerp` → `odoo` 包改名  — CONFIRMED

框架 Python 包目录 `openerp` 在 **9→10** 正式改名为 `odoo`（OCA `Migration to version 10.0` 明确要求 `from openerp` → `from odoo`）。到 10.0，`openerp` 包不再有效；任何残留的 `import openerp` 都会直接 `ImportError`。

### Before（9.0）

```python
import openerp
from openerp import models, fields, api
from openerp.osv import osv
from openerp.addons.base.ir.ir_config_parameter import ...
```

### After（10.0）

```python
import odoo
from odoo import models, fields, api
from odoo.osv import osv                 # 仍可用，建议 from odoo import models
from odoo.addons.base.models.ir_config_parameter import ...
```

要点：

- 全仓库 `grep` `openerp`：所有 `from openerp ...` / `import openerp` 改为 `from odoo ...` / `import odoo`。
- 模块内部相对导入、`openerp.addons.*` 路径一并改为 `odoo.addons.*`。
- 控制器、报表、向导、测试文件同样适用（见 `references/http-rpc-mail.md`）。
- 扫描 id：`openerp-import`（正则 `from openerp|import openerp`）。

---

## 3. 清单文件：`__openerp__.py` → `__manifest__.py`  — CONFIRMED

模块声明文件从 `__openerp__.py` 改名为 `__manifest__.py`。9.0 的 `__openerp__.py` 在 10.0 不会被识别为模块清单，模块将无法加载。

### Before（9.0）

```python
# __openerp__.py
{
    'name': 'My Module',
    'version': '9.0.1.0.0',
    'depends': ['base'],
    'data': ['views/mymodule.xml'],
    'installable': True,
}
```

### After（10.0）

```python
# __manifest__.py
{
    'name': 'My Module',
    'version': '10.0.1.0.0',
    'depends': ['base'],
    'data': ['views/mymodule.xml'],
    'installable': True,
}
```

要点：

- 重命名文件：`git mv __openerp__.py __manifest__.py`（同时更新 `.gitignore` / 打包配置里对 `__openerp__.py` 的引用）。
- 清单内的字典键（`name`/`depends`/`data`/`version` 等）格式不变，仅文件名变化。
- 扫描 id：`manifest-rename`（正则 `__openerp__`，并检测文件名 `__openerp__.py`）。

---

## 4. 字段索引：`select = True` → `index = True`  — CONFIRMED

字段定义中的 `select = True`（为字段建数据库索引）在 10.0 改名为 `index = True`，沿用至今。残留的 `select = True` 在 10.0 不再有建索引语义（会被忽略或告警）。

### Before（9.0）

```python
name = fields.Char(string='Name', select=True)
ref = fields.Char(select=1)
```

### After（10.0）

```python
name = fields.Char(string='Name', index=True)
ref = fields.Char(index=True)
```

要点：

- 全仓库替换 `select=True` / `select=1` / `select = True` → `index=True`。
- 仅影响字段索引语义；其余字段属性（`required`/`readonly`/`store` 等）不变。
- 扫描 id：`select-index`（正则 `select\s*=\s*True|select\s*=\s*1`）。

---

## 5. 视图 / XML：`position`/`xpath` 字符串选择器 → 属性选择器；`<openerp>`/`<data>` → `<odoo>`  — CONFIRMED

视图继承中，旧的**字符串选择器**（用 `position="after"` 配合字段文本内容、或 `xpath` 用文本匹配）在 10.0 要求改用**属性选择器**（最常用 `name`，也可用 `xpath` 配合 `@name` 等属性表达式）。同时，XML 文件最外层的 `<openerp>` / `<data>` 包装元素应替换为 `<odoo>`（`<data>` 作为根包装也可继续用，但 `<openerp>` 必须移除）。

### Before（9.0）

```xml
<openerp>
  <data>
    <record id="view_form_inherit" model="ir.ui.view">
      <field name="inherit_id" ref="base.view_form"/>
      <field name="arch" type="xml">
        <field name="name" position="after">
          <field name="my_field"/>
        </field>
      </field>
    </record>
  </data>
</openerp>
```

### After（10.0）

```xml
<odoo>
  <record id="view_form_inherit" model="ir.ui.view">
    <field name="inherit_id" ref="base.view_form"/>
    <field name="arch" type="xml">
      <field name="my_field" position="after"/>
      <xpath expr="//field[@name='name']" position="after">
        <field name="my_field" position="after"/>
      </xpath>
    </field>
  </record>
</odoo>
```

要点：

- 字符串 `position` 选择器（依赖标签文本内容定位）改为基于 `name` 等属性的选择器；推荐 `<field name="target" position="after"/>` 或 `<xpath expr="//field[@name='target']" position="after"/>`。
- 最外层 `<openerp>` 根元素删除，改用 `<odoo>`（`<data>` 作为根包装在 10.0 仍被接受；但 `<openerp>` 必须移除）。
- 不要误伤合法的 `name=` 属性：本规则只捕获 `select="..."` 字符串选择器与 `<openerp>`/`<data>` 根包装，不改动普通 `name=` 属性。
- 扫描 id：`xml-selector`（正则 `select\s*=\s*"|position\s*=\s*"after"|<openerp>|<data>`；`<data>` 命中需人工确认是否为根包装）。

---

## 6. 安全组：`base.group_configuration` → `base.group_system`  — CONFIRMED

配置权限组在 10.0 改名为 `base.group_system`（原 `base.group_configuration` 失效）。所有引用它的 `ir.model.access.csv`、安全 XML、`res.groups` 的 `implied_ids` 需同步修改，否则安装报 `External ID not found`。

### Before（9.0）

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model,my.model,model_my_model,base.group_configuration,1,0,0,0
```

### After（10.0）

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model,my.model,model_my_model,base.group_system,1,0,0,0
```

要点：

- `security/ir.model.access.csv`、安全 XML 中 `base.group_configuration` 全部改为 `base.group_system`。
- 扫描 id：`group-config`（正则 `base\.group_configuration`）。

---

## 7. `copy` 方法装饰器：`@api.one` → `@api.multi`  — CONFIRMED

OCA `Migration to version 10.0` 明确："Change decorator of copy method ... from `@api.one` to `@api.multi`"。`copy` 方法在 10.0 应以 `@api.multi` 定义（方法体内部遍历 `self`）。

### Before（9.0）

```python
@api.one
def copy(self, default=None):
    default = dict(default or {})
    default['name'] = self.name + ' (copy)'
    return super(MyModel, self).copy(default)
```

### After（10.0）

```python
@api.multi
def copy(self, default=None):
    self.ensure_one()
    default = dict(default or {})
    default['name'] = self.name + ' (copy)'
    return super(MyModel, self).copy(default)
```

要点：

- 仅 `copy` 方法的 `@api.one` 改为 `@api.multi`；若方法体假设单记录，加 `self.ensure_one()` 或 `for record in self:`。
- 注意：**不要**把 `@api.one` 与 `@api.onchange` 混用——在 9.0/10.0 上这会导致崩溃（不属扫描器模式，仅作提醒）。
- 扫描 id：`copy-decorator`（正则 `@api\.one[\s\S]{0,200}?def\s+copy|def\s+copy[\s\S]{0,200}?@api\.one`）。

---

## 8. 安全组模块化：从 `base` 迁移到各模块（group-move）  — CONFIRMED

OCA 10.0 将若干原本挂在 `base` 模块下的安全组 / 菜单 / 记录迁移到各自业务模块（如销售组进 `sales_team`、人事组进 `hr`）。9.0 残留的旧 ID 在 10.0 触发 `External ID not found`，必须改写下表右侧的新 ID。

| 旧 ID（≤9.0，`base` 前缀） | 新 ID（10.0+ 模块化） |
|---|---|
| `base.group_sale_salesman` | `sales_team.group_sale_salesman` |
| `base.group_sale_salesman_all_leads` | `sales_team.group_sale_salesman_all_leads` |
| `base.group_sale_manager` | `sales_team.group_sale_manager` |
| `base.group_hr_user` | `hr.group_hr_user` |
| `base.group_hr_manager` | `hr.group_hr_manager` |
| `menu_hr_configuration` | `menu_human_resources_configuration` |
| `website.salesteam_website_sales` | `sales_team.salesteam_website_sales` |
| `product.prod_config_main` | `sale.prod_config_main` |

要点：

- `security/ir.model.access.csv`、安全 XML、菜单 XML、动作 XML 中所有上表左侧旧 ID 改为右侧新 ID。
- 特别注意 `product.prod_config_main` → `sale.prod_config_main`（`product` 模块的配置菜单移至 `sale`）；以及 `website.salesteam_website_sales` → `sales_team.salesteam_website_sales`。
- 扫描 id：`group-move`（正则覆盖上述 8 个旧 ID）。

---

## 9. 视图 / QWeb 其它（基本不变）  — CONFIRMED

- 视图结构（`<form>`/`<tree>`/`<field>`/`attrs` 等）9→10 无破坏性改动。
- QWeb 模板 `t-*` 指令沿用；`t-field-options`→`t-options` 的清理发生在 **11→12**，不属本卷。
- 视图继承选择器清理见第 5 节；其余视图写法不变。

---

## 10. HTTP / RPC / 邮件（基本不变）  — CONFIRMED

- 控制器：随主改名，`from openerp import http` → `from odoo import http`；`http.Controller` / `http.route()` 接口 9→10 无破坏性变更。
- 邮件：`mail.template`、QWeb 渲染、`message_post` 接口稳定（Jinja/Python-format 语法移除发生在 14→15）。
- 二进制字段：`fields.Binary` 用法不变（`Binary` 默认存 `ir.attachment` 的时机在 13.0）。

---

## 11. 模块 / 模型 / 字段映射

9→10 **没有**大规模模型 / 模块重命名（`account.invoice`→`account.move` 属 12→13，不属本卷）。需要关注的字段层改名：

| 项目 | 9.0 | 10.0 | 备注 |
|---|---|---|---|
| `from openerp` / `import openerp` | 有效 | 失效 | 第 2 节 |
| 清单文件 `__openerp__.py` | 有效 | 失效 | 第 3 节 |
| 字段 `select = True` | 有效 | `index = True` | 第 4 节 |
| `copy` 方法 `@api.one` | 有效 | `@api.multi` | 第 7 节 |
| `base.group_configuration` | 存在 | `base.group_system` | 第 6 节 |
| 安全组 `base.group_sale_*` / `base.group_hr_*` 等 | 存在 | `sales_team.*` / `hr.*` | 第 8 节 |

---

## 12. 测试与校验

1. 用 **10.0** 源码（已是 `odoo` 包）启动实例；9.0 的 `openerp` 包不存在。
2. `python3 Odoo9to10Migration/scripts/scan_addon.py /path/to/addons` 跑扫描，逐条处理 `openerp-import` / `manifest-rename` / `select-index` / `xml-selector` / `group-config` / `copy-decorator` / `group-move` 发现项（全部 `manual`，无 codemod）。
3. 安装模块：先清 `ImportError`（`openerp` 包、`__openerp__.py` 缺失）；再清 `External ID not found`（`base.group_configuration`、旧 `base.group_*` ID）。
4. `python3 -m py_compile **/*.py` 全量编译，确保无语法错误。
5. `odoo-bin -u <module> --test-tags /<module>` 跑测试；`--dev=all` 下清除 `DeprecationWarning`。

---

## 13. `upgrade_code` codemod（9→10 无）  — CONFIRMED

`odoo/upgrade_code/` 引擎自 **18.0** 才随官方发布。9.0/10.0 源码树中**不存在** `odoo/upgrade_code/` 模块。因此 9→10 的全部代码迁移（包改名、清单改名、`select`→`index`、`copy` 装饰器、安全组模块化）均为**手工映射**，无自动重写脚本。数据库级变更（字段/模型结构）由 **OpenUpgrade** 或官方升级服务处理；本卷只覆盖自定义模块的**代码级**映射。

---

## 14. 迁移实战清单

- [ ] 全仓库 `from openerp` / `import openerp` 改为 `odoo`（`openerp-import`）。
- [ ] 每个模块 `__openerp__.py` → `__manifest__.py`（`manifest-rename`）。
- [ ] 字段 `select = True` / `select=1` → `index = True`（`select-index`）。
- [ ] 视图继承字符串 `position`/文本 `xpath` 选择器改为 `name` 属性选择器；`<openerp>`/`<data>` 根包装改为 `<odoo>`（`xml-selector`）。
- [ ] `base.group_configuration` → `base.group_system`（`group-config`）。
- [ ] `copy` 方法 `@api.one` → `@api.multi`（`copy-decorator`）。
- [ ] 安全组 / 菜单 / 记录 ID 模块化迁移（`group-move`）：`base.group_sale_*`→`sales_team.*`、`base.group_hr_*`→`hr.*`、`menu_hr_configuration`→`menu_human_resources_configuration`、`website.salesteam_website_sales`→`sales_team.salesteam_website_sales`、`product.prod_config_main`→`sale.prod_config_main`。
- [ ] 重扫扫描器期望 0 发现；跑测试通过。

---

## 15. 红线（勿套用更晚版本）

- `from openerp`→`from odoo` 主改名 → **本卷（9→10）**；10→11 仅清理最后一个 `openerp` 兼容别名。
- `@api.one` 装饰器**完全移除** → **11→12**（`@api.one` 在 9.0/10.0 仍存在；本卷只改 `copy` 方法）。
- `fields.Date` / `fields.Datetime` 运行时对象化、`from_string` 移除 → **11→12**。
- `ir.actions.act_window.view` 模型移除 → **11→12**。
- `t-field-options` → `t-options` → **11→12**。
- `account.invoice` → `account.move` → **12→13**。
- Python 3 强制、工作流完全移除、QWeb 报表 `render_html`→`get_report_values` → **10→11**。

---

## 附录 A：研究来源与溯源

- OCA `Migration to version 10.0`（权威）：`openerp`→`odoo` 包改名、`__openerp__.py`→`__manifest__.py`、`select`→`index`、`base.group_configuration`→`base.group_system`、`copy` 方法 `@api.one`→`@api.multi`、安全组模块化迁移。
- OCA `Migration to version 9.0`：9.0 仍为 `openerp` 包时代的基线。
- Odoo 10.0 源码核对：`odoo/__init__.py` 无 `openerp` 包；清单加载器只识别 `__manifest__.py`。
- 10.0 Release Notes：模块结构清理、视图继承选择器收紧。
- 红线对照：10→11（Python 3、工作流、报表 API）、11→12（`@api.one` 移除、`fields.Date` 对象化、`ir.actions.act_window.view` 移除、`t-field-options`）、12→13（`account.invoice`→`account.move`）。
