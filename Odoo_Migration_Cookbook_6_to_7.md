# Odoo 迁移烹饪书：6.0 → 7.0（OpenERP 6.0 → OpenERP 7.0）

> 配套技能：`Odoo6to7Migration/`（SKILL + 6 份参考表 + 扫描器）
> 作用域：仅 **6.0 → 7.0** 破坏性变更。更晚改动（如 7→8 的 `@api.*` / `models.Model` / `self.env`、`openerp`→`odoo` 改名、`__openerp__.py`→`__manifest__.py`、`@api.one` 移除、`fields.Date` 对象化）一律不在本卷。

## 目录

1. 导言与版本作用域
2. 头号断裂：`osv.osv` → `osv.Model`（及 `osv.osv_memory` → `osv.TransientModel`）
3. `res.partner.address` 模型移除（合并进 `res.partner`）
4. Manifest（`__openerp__.py`）：`update_xml` → `data`
5. 视图 / QWeb / 前端：`version="7.0"` + `sheet` / `header` / `footer` + Bootstrap
6. 旧 API（`cr, uid, ids, context`）仍沿用 —— 新 API 在 7→8 才来，勿混淆
7. HTTP / 邮件 / 二进制（基本不变）
8. 安全与 `res.groups`（6→7 不变）
9. 模块 / 模型 / 字段映射
10. 测试与校验
11. `upgrade_code` codemod（6→7 无，全部手工）
12. 迁移实战清单
13. 附录 A：研究来源与溯源

---

## 1. 导言与版本作用域

OpenERP **7.0（2012-12）** 被官方称为"not just an update"——它重写了 Web 客户端（新的 Web 框架 + Bootstrap CSS），把 `res.partner.address` 合并进 `res.partner`，并把 ORM 基类从 `osv.osv` 演进为 `osv.Model`（`osv` 成为弃用别名，将在后续版本被压制）。6.0 仍使用旧的 `osv.osv` / `osv.osv_memory` 基类与 `update_xml` 清单键。

6.0 与 7.0 都还使用 **`openerp`** 包命名空间（不是 `odoo`；`openerp`→`odoo` 改名是 **9→10**），也都使用 **旧 API** 方法签名 `def meth(self, cr, uid, ids, context=None)`（新 API `@api.*` / `models.Model` / `self.env` 在 **7→8** 才引入，不在本卷）。

### 版本作用域红线（勿套用更晚版本的改动）

- `openerp` → `odoo` 改名 → **9→10**（6/7 用的就是 `openerp`，本卷不动包名）。
- `osv.Model` → `models.Model`、`@api.*` 装饰器、`self.env`、`osv.except_osv`→`UserError` → **7→8**。
- `res.partner.address` 移除 **属于本卷（6→7）**，不要误以为是更晚改动。
- `@api.one` 移除 → **11→12**；`fields.Date` 运行时对象化 → **11→12**。
- `__openerp__.py` → `__manifest__.py` 文件改名 → **9→10**（本卷的改动是 `__openerp__.py` 内部的 `update_xml`→`data`，**不是**文件改名）。

> 本卷只处理 6→7 区间；任何属于 7→8、9→10、11→12 的条目，仅在本卷"红线"处点名，不展开。

### 配套技能参考表（skill references）

- `Odoo6to7Migration/references/orm-api.md` —— `osv.osv`→`osv.Model`、旧 API 签名、ORM 基类。
- `Odoo6to7Migration/references/views-qweb.md` —— 视图 `version="7.0"`、`sheet`/`header`/`footer`、前端 Bootstrap。
- `Odoo6to7Migration/references/models-mapping.md` —— `res.partner.address` 合并、`update_xml`→`data` 等清单/模型映射。
- `Odoo6to7Migration/references/security.md` —— `res.groups` / 访问权在 6→7 不变。
- `Odoo6to7Migration/references/http-rpc-mail.md` —— 控制器 / 邮件 / 二进制（基本不变）。
- `Odoo6to7Migration/references/upgrade-code.md` —— 7.0 无 `upgrade_code` codemod，全部手工。

---

## 2. 头号断裂：`osv.osv` → `osv.Model`  — CONFIRMED

6.0 的 ORM 模型通过 `osv.osv` 基类声明；7.0 引入 `osv.Model`（以及向导用的 `osv.TransientModel`）。`osv` 作为旧别名的去留：7.0 仍兼容 `osv.osv`，但它被标记为弃用，下一版本将被压制——**迁移到 7.0 时应当直接改写为 `osv.Model` / `osv.TransientModel`**。

### Before（6.0）

```python
from openerp.osv import osv, fields

class my_model(osv.osv):
    _name = 'my.model'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
    }

class my_wizard(osv.osv_memory):
    _name = 'my.wizard'
    _columns = {
        'value': fields.float('Value'),
    }
```

### After（7.0）

```python
from openerp.osv import osv, fields

class my_model(osv.Model):
    _name = 'my.model'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
    }

class my_wizard(osv.TransientModel):
    _name = 'my.wizard'
    _columns = {
        'value': fields.float('Value'),
    }
```

要点：

- `class Foo(osv.osv)` → `class Foo(osv.Model)`。
- `class Foo(osv.osv_memory)` → `class Foo(osv.TransientModel)`。
- 仍保留 `from openerp.osv import osv, fields`（6/7 都是 `openerp` 包名，本卷不改包名）。
- 方法签名 **保持不变**：仍是 `def meth(self, cr, uid, ids, context=None)`（旧 API），新 API 在 7→8 才来。
- 扫描 id：`osv-base`（正则 `osv\.osv\b|osv\.osv_memory|class \w+\(osv\.osv\)|class \w+\(osv\.osv_memory\)`）。

---

## 3. `res.partner.address` 模型移除  — CONFIRMED

6.0 把"联系人/地址"拆成单独的 `res.partner.address` 模型（`res_partner_address` 表），通过 `partner_id` 关联到 `res.partner`，一个联系人可有多个地址。7.0 把地址字段**直接合并进 `res.partner`**——`res.partner.address` 模型被删除，街道、城市、邮箱、电话等字段现在都在 `res.partner` 上。

### Before（6.0）

```python
# 读取客户的默认地址
addr_ids = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['default', 'invoice'])
addr = self.pool.get('res.partner.address').browse(cr, uid, addr_ids['default'])
street = addr.street
city = addr.city
email = addr.email
phone = addr.phone
```

```xml
<record id="view_partner_address_form" model="res.partner.address">
    <field name="name">Contact</field>
    <field name="street">Main St</field>
    <field name="partner_id" ref="base.res_partner_1"/>
</record>
```

### After（7.0）

```python
# 地址字段已合并进 res.partner 本身
partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
street = partner.street
city = partner.city
email = partner.email
phone = partner.phone
```

```xml
<record id="view_partner_form" model="res.partner">
    <field name="name">Contact</field>
    <field name="street">Main St</field>
</record>
```

要点：

- 凡是引用 `res.partner.address` 模型（或 `res_partner_address` 表/外键）的代码、XML、视图、报表，全部改为使用 `res.partner` 上的字段。
- `address_get`、`address_create` 等旧辅助方法在 7.0 大多被移除或改变行为——逐条核对，不要盲目保留。
- 跨模型查询 `res.partner.address` 的代码（搜索、关联字段、`_columns` 里指向它的 `many2one`）需重写指向 `res.partner`。
- 扫描 id：`partner-address`（正则 `res\.partner\.address|res_partner_address`）。

---

## 4. Manifest（`__openerp__.py`）：`update_xml` → `data`  — CONFIRMED

6.0 的 `__openerp__.py` 把视图/安全/演示数据分别放在 `init_xml`、`update_xml`、`demo_xml` 三个键里。7.0 **统一为单一 `data` 键**，`init_xml` / `update_xml` / `demo_xml` 三个键被移除——任何残留都会让模块在 7.0 安装时找不到对应数据文件声明（事实上 7.0 的 manifest 加载只认 `data`）。

### Before（6.0）

```python
{
    'name': 'My Module',
    'version': '1.0',
    'init_xml': ['security/my_module_security.xml'],
    'update_xml': ['my_module_view.xml', 'my_module_menu.xml'],
    'demo_xml': ['my_module_demo.xml'],
}
```

### After（7.0）

```python
{
    'name': 'My Module',
    'version': '1.0',
    'data': [
        'security/my_module_security.xml',
        'my_module_view.xml',
        'my_module_menu.xml',
        'my_module_demo.xml',
    ],
}
```

要点：

- `init_xml` / `update_xml` / `demo_xml` 的内容全部合并进 `data` 列表。
- 文件顺序仍建议保持原有加载次序（安全 → 视图 → 菜单 → 演示）。
- 注意：**文件本身仍是 `__openerp__.py`**（改名成 `__manifest__.py` 是 **9→10**，不属于本卷）。本卷只改键名，不改动文件名。
- 扫描 id：`manifest-keys`（正则 `update_xml|init_xml|demo_xml`，在 `__openerp__.py` 上下文内命中即告警）。

---

## 5. 视图 / QWeb / 前端  — CONFIRMED（含 [verify]）

7.0 带来全新 Web 客户端：基于 **Bootstrap** 的 CSS、支持在视图里直接写 HTML、引入 `<sheet>` / `<header>` / `<footer>` 等布局标签，并要求根视图元素带上 `version="7.0"` 属性。

### 新视图写法（7.0）

```xml
<form version="7.0">
    <header>
        <button name="action_confirm" type="object" string="Confirm" states="draft"/>
    </header>
    <sheet>
        <group>
            <field name="name"/>
            <field name="street"/>
        </group>
        <footer>
            <p>Custom footer note.</p>
        </footer>
    </sheet>
</form>
```

要点：

- 根 `<form>` / `<tree>` / `<kanban>` 等应加 `version="7.0"` 属性（老 6.0 视图没有该属性，7.0 解析器对无 version 的视图行为不同）。
- 用 `<sheet>` 包裹表单主体，用 `<header>` 放状态栏按钮、`<footer>` 放页脚说明/HTML 内容。
- 视图内 **允许直接写 HTML**（6.0 受限）。
- 前端样式全面切到 Bootstrap——依赖老版自定义 CSS 的 widget 需复核。
- 扫描 id：`view-bootstrap`（正则 `version="7.0"|<sheet>|<header>|<footer>`，保守匹配；命中说明此处已（或将）使用 7.0 视图特性，需人工确认是否补齐 `version` / `sheet` 结构）。

> `[verify]` Bootstrap 的具体大版本号（3.x？）无权威 6→7 前端清单；建议以 7.0 源码 `addons/web` 资产为准，必要时收紧本标注。

---

## 6. 旧 API（`cr, uid, ids, context`）仍沿用  — CONFIRMED（文档性条目）

6→7 **继续使用旧 API**。方法签名形如：

```python
def action_confirm(self, cr, uid, ids, context=None):
    for obj in self.browse(cr, uid, ids, context=context):
        self.write(cr, uid, [obj.id], {'state': 'confirmed'}, context=context)
    return True
```

要点：

- 7.0 仍用 `@api` 之前的写法：`cr`（游标）、`uid`、`ids`、`context` 显式传递；方法通过 `self.pool.get('model')` 取模型、用 `browse` / `write` / `create` 等显式传 `cr, uid, ids` 的调用。
- **新 API（`@api.model` / `@api.multi` / `@api.one` / `models.Model` / `self.env`）在 7→8 才引入**——本卷不出现，也不要在 6→7 迁移里"提前现代化"成新 API（那属于 7→8 工作，且会改变方法语义）。
- `osv.except_osv` 异常类在 6/7 仍可用（它被 `UserError` 取代是 **7→8** 的事），本卷保留旧写法即可。
- 文档此条的目的：明确 6→7 的 API 边界，避免把 7→8 的 API 现代化误列为 6→7 任务。

---

## 7. HTTP / 邮件 / 二进制（基本不变）  — CONFIRMED

- 控制器：6.0 已是 Web 控制器（`openerp.addons.web.http` 一脉），6→7 的 `controller` / `route` 接口无破坏性变更。
- 邮件：`mail` 模块在 7.0 重构前（大规模邮件重写是更晚版本），`message_post` / `mail.template` 基本结构不变。
- 二进制字段：`Binary` 字段存储行为 6→7 一致。
- `<act_window>` / `<menuitem>` / `<record>` 等数据声明语法 6→7 一致（清单键改动见第 4 节）。

---

## 8. 安全与 `res.groups`（6→7 不变）  — CONFIRMED

- `security/ir.model.access.csv`：访问权 CSV 格式在 6/7 完全一致（`id`, `name`, `model_id:id`, `group_id:id`, `perm_read/perm_write/perm_create/perm_unlink`），无需改动。
- `ir.rule`：记录规则写法一致（`domain_force`、全局 `global` 语义同 6.0）。
- `res.groups`：`groups` 字段、`implied_ids` 继承链、`category_id` 机制一致。
- 安全 XML（`<record model="ir.model.access"/>`、`<record model="res.groups"/>`）无需改动。

> 本卷对不需要改安全文件；更晚版本的安全改动（如 9→10 的 group 模块化、18→19 的 privilege 模型、19→20 的 `ir.access.csv` 拆分）不在 6→7。

---

## 9. 模块 / 模型 / 字段映射

除第 3 节（地址合并）与第 4 节（清单键）外，6→7 模型层无大规模重命名。需要重点关注的：

| 项目 | 6.0 | 7.0 | 备注 |
|---|---|---|---|
| ORM 基类 | `osv.osv` / `osv.osv_memory` | `osv.Model` / `osv.TransientModel` | 第 2 节 |
| `res.partner.address` 模型 | 存在（独立模型） | 移除；字段并入 `res.partner` | 第 3 节 |
| `__openerp__.py` 清单键 | `init_xml` / `update_xml` / `demo_xml` | 统一为 `data` | 第 4 节 |
| 视图根属性 | 无 `version` | `version="7.0"` + `sheet`/`header`/`footer` | 第 5 节 |
| 方法签名 | `cr, uid, ids, context` | 同（旧 API 保留） | 第 6 节 |

数据库级结构变更（如 `res_partner_address` 表并入 `res_partner`）由 **OpenUpgrade** 或官方升级服务处理；本卷只覆盖自定义模块的**代码级**映射。

---

## 10. 测试与校验

1. 在 7.0 实例上启动；6.0 模块先清 `ImportError`（`osv.osv` 基类已可用但仍建议改写，残留 `res.partner.address` 模型会报模型不存在）。
2. `python3 Odoo6to7Migration/scripts/scan_addon.py /path/to/addons` 跑扫描，逐条处理 `osv-base` / `partner-address` / `manifest-keys` / `view-bootstrap` 发现项（全部 `manual`，无 codemod）。
3. 安装模块：清 `ImportError`（`res.partner.address` 模型缺失）/ 清单键告警；再清 `AttributeError`（旧 `address_*` 方法）。
4. `python3 -m py_compile **/*.py` 全量编译，确保 Python 语法无误（6/7 仍是 Python 2.x）。
5. `openerp-server -u <module> --test-enable` 在 7.0 沙箱跑测试；逐步清 `DeprecationWarning`（`osv.osv` 弃用）。

---

## 11. `upgrade_code` codemod（6→7 无）  — CONFIRMED

`odoo/upgrade_code/` 引擎自 **18.0** 才出现。6→7 **没有任何 `upgrade_code` 脚本**——所有代码改名（`osv.osv`→`osv.Model`、地址合并、`update_xml`→`data`、视图 `version="7.0"`）均为**手工**。数据库级变更（字段/模型结构，如 `res_partner_address` 并入 `res.partner`）由 **OpenUpgrade** 或官方升级服务处理；本卷只覆盖自定义模块的**代码级**映射。

---

## 12. 迁移实战清单

- [ ] 所有 `class Foo(osv.osv)` → `osv.Model`，`class Foo(osv.osv_memory)` → `osv.TransientModel`（保留 `from openerp.osv`）。
- [ ] 删除全部 `res.partner.address` 引用（模型、`res_partner_address` 表、视图、XML），改用 `res.partner` 字段。
- [ ] `__openerp__.py`：`init_xml` / `update_xml` / `demo_xml` 全部并入 `data` 列表（文件名不动）。
- [ ] 视图加 `version="7.0"`；套 `<sheet>` / `<header>` / `<footer>`，移除 6.0 受限 HTML 写法约束。
- [ ] 确认方法签名仍是 `cr, uid, ids, context` 旧 API——**不要**提前升级到 `@api.*`（那是 7→8）。
- [ ] 重扫扫描器，预期 0 发现；`py_compile` 通过；7.0 沙箱测试通过。

---

## 附录 A：研究来源与溯源

- Odoo 官方 Release Notes（OpenERP 7.0，2012-12）："not just an update"、新 Web 客户端、Bootstrap、地址合并进 `res.partner`。
- Odoo 论坛 v6→v7 迁移讨论帖：社区证实 `osv.osv`→`osv.Model`、`res.partner.address` 合并、`update_xml`→`data`。
- dbi-services 博客 OpenERP 6→7 迁移博文：`version="7.0"` 视图、`sheet`/`header`/`footer` 标签、HTML 视图放开。
- 7.0 源码核对：`openerp.osv.osv` 仍可用但标记弃用；`osv.Model` / `osv.TransientModel` 为推荐基类；`res.partner` 已含地址字段；`__openerp__.py` 仅识别 `data` 键。
- 版本边界核对：`openerp`→`odoo`（9→10）、`models.Model`/`@api.*`/`self.env`（7→8）、`__openerp__.py`→`__manifest__.py`（9→10）、`@api.one` 移除（11→12）、`fields.Date` 对象化（11→12）——均不属于 6→7。
