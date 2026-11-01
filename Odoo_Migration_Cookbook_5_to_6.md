# Odoo 迁移烹饪书：OpenERP 5.0 → 6.0

> 配套技能：`Odoo5to6Migration/`（SKILL + 6 份参考表 + 扫描器）
> 作用域：仅 **OpenERP 5.0 → 6.0** 破坏性变更。更晚改动（如 6→7 的 `osv.osv`→`osv.Model`、`res.partner.address` 移除，9→10 的 `__openerp__.py`→`__manifest__.py` / `openerp`→`odoo`，12→13 的 `account.invoice`→`account.move`）一律不在本卷。

## 目录

1. 导言与版本作用域
2. 头号断裂：清单文件改名 `__terp__.py` → `__openerp__.py`
3. 清单键 `init_xml` / `update_xml` / `demo_xml` → `data` / `demo` / `test`
4. 新默认 Web 客户端（[verify]-light 框架变更）
5. 模块结构：`report/` 与 `static/` 目录
6. 视图 / QWeb / 前端（[verify]）
7. HTTP / 邮件 / 二进制（基本不变）
8. 安全与 `res.groups`（5→6 基本不变）
9. 模块 / 模型 / 字段映射
10. 测试与校验
11. `upgrade_code` codemod（5→6 无）
12. 迁移实战清单
13. 附录 A：研究来源与溯源

---

## 1. 导言与版本作用域

OpenERP **6.0（2011）** 是一次重大 UX  overhauled + 引入了新的默认 **web client**（GTK 客户端仍可工作，但 web 客户端成为默认）。同时 6.0 对模块清单（manifest）做了规范化：清单文件名从 5.0 的 `__terp__.py` 改名为 `__openerp__.py`，并引入了更简洁的 `data` / `demo` / `test` 键替代旧的 `init_xml` / `update_xml` / `demo_xml`（旧键仍被接受但已弃用）。5.0 的 ORM 写法（`from openerp import ...`、`osv.osv` 基类、`cr, uid, ids, context` 方法签名）在 5→6 区间保持不变——这些重命名属于更晚的版本（见红线）。

> 这是一对非常古老的版本（OpenERP 5.0/6.0，2010–2011），官方文档零散且多已离线。本卷对无法钉死到扎实来源的框架级断言一律标注 **[verify]**；唯二 **CONFIRMED** 的锚点事实是：`__terp__.py`→`__openerp__.py` 与 `init_xml`/`update_xml`/`demo_xml`→`data`/`demo`/`test`。

### 版本作用域红线（勿套用更晚版本的改动）

- `__openerp__.py` → `__manifest__.py` → **9→10**（本卷只把 `__terp__.py` 改名为 `__openerp__.py`，不继续改名）。
- `osv.osv` → `osv.Model` 基类改名 → **6→7**（5→6 仍是 `osv.osv`）。
- `res.partner.address` 模型移除 → **6→7**（5→6 仍存在）。
- `openerp` → `odoo` 包改名 → **9→10**（5→6 仍是 `openerp` 包）。
- `@api.*` 新 API、`self.env`、`fields.Date` 对象、`@api.one` 移除 → **7→8 / 11→12**（5→6 仍是旧 ORM）。
- `account.invoice` → `account.move` → **12→13**。

> 本卷只处理 5→6 区间；任何属于 6→7 或 9→10 的条目，仅在本卷"红线"处点名，不展开。数据库级结构变更由 **OpenUpgrade** / 官方升级服务处理；本卷只覆盖自定义模块的**代码级**清单迁移。

### 配套技能参考表（skill references）

- `Odoo5to6Migration/references/orm-api.md` —— ORM / Python 旧式写法（5→6 不变）+ 红线（osv.osv 改名属 6→7）。
- `Odoo5to6Migration/references/views-qweb.md` —— 视图 / QWeb / 前端（web client 成为默认）。
- `Odoo5to6Migration/references/models-mapping.md` —— 清单文件名 / 清单键 / 模块结构（`report/` / `static/`）映射表。
- `Odoo5to6Migration/references/security.md` —— `res.groups` / 访问权限（5→6 基本不变）。
- `Odoo5to6Migration/references/http-rpc-mail.md` —— 控制器 / 邮件 / 二进制（基本不变）。
- `Odoo5to6Migration/references/upgrade-code.md` —— 6.0 及更早**无** `upgrade_code` codemod，全部手工。

---

## 2. 头号断裂：清单文件改名 `__terp__.py` → `__openerp__.py`  — CONFIRMED

5.0 的模块清单文件名为 `__terp__.py`（源自 TurboGears 时代的 `__terp__.py` 约定）。**6.0 将其正式改名为 `__openerp__.py`**。6.0 仍兼容旧的 `__terp__.py`，但新模块与迁移后的模块应使用 `__openerp__.py`。

### Before（5.0，`__terp__.py`）

```python
# __terp__.py  (OpenERP 5.0)
{
    'name': 'My Module',
    'version': '1.0',
    'init_xml': ['mymodule_view.xml'],
    'update_xml': ['mymodule_data.xml'],
    'demo_xml': ['mymodule_demo.xml'],
    'installable': True,
    'active': True,
}
```

### After（6.0，`__openerp__.py`）

```python
# __openerp__.py  (OpenERP 6.0)
{
    'name': 'My Module',
    'version': '1.0',
    'data': ['mymodule_view.xml', 'mymodule_data.xml'],
    'demo': ['mymodule_demo.xml'],
    'installable': True,
    'active': True,
}
```

要点：

- 把模块根目录的 `__terp__.py` 重命名为 `__openerp__.py`。6.0 仍会读旧文件名，但新代码应统一。
- 扫描 id：`terp-manifest`（正则 `__terp__\.py`）；任何残留的 `__terp__.py` 文件都应改名。

---

## 3. 清单键 `init_xml` / `update_xml` / `demo_xml` → `data` / `demo` / `test`  — CONFIRMED

6.0 引入了更简洁的清单键：`init_xml`（安装时加载）与 `update_xml`（安装/更新均加载）合并为单一的 `data` 键；`demo_xml` 改名为 `demo`；并新增了 `test` 键用于测试数据。旧键在 6.0 仍被接受但已弃用。

| 5.0 键 | 6.0 键 | 说明 |
|---|---|---|
| `init_xml` | `data` | 安装时加载的视图/数据 XML |
| `update_xml` | `data` | 安装/更新均加载的 XML（并入 `data`） |
| `demo_xml` | `demo` | 演示数据 |
| （无） | `test` | 6.0 新增：测试数据键 |
| （无） | `web` | 6.0 新增：标记模块是否提供 web 客户端资源（布尔） |

要点：

- 将 `init_xml` 与 `update_xml` 两个列表合并进 `data`。
- 将 `demo_xml` 改名为 `demo`。
- 可选：将测试相关 XML 列入新的 `test` 键（[verify] 具体加载时机以 6.0 源码 `osv/__init__.py` / `modules/loading.py` 为准）。
- 6.0 还新增了一个 `web` 布尔键，用于声明模块对 web 客户端的支持——纯 GTK 模块可忽略（[verify] 细节）。
- 扫描 id：`manifest-keys`（正则 `'init_xml'|'update_xml'|'demo_xml'`）。

> 注意：本卷**只**覆盖 `__terp__.py`→`__openerp__.py` 这一步。`__openerp__.py`→`__manifest__.py`（9→10）不属本卷，切勿在 5→6 顺手继续改名。

---

## 4. 新默认 Web 客户端（[verify]-light 框架变更）

6.0 引入了新的默认 **web client**（基于 Python 的 `openerp-web` / 内置 web 模块）。GTK 客户端在 6.0 仍可工作，但 web 客户端成为默认入口。

- 自定义模块若提供供 web 客户端使用的静态资源，应放入模块下的 `static/` 目录（见第 5 节）。
- 这是一次 [verify]-light 的框架级变更：文档零散，且 6.0 的 web 客户端与日后 7.0+ 的 `web` 模块架构差异较大；不要把更晚版本（7.0+）的 `web` 模块约定套用到 5→6。
- 视图层面（`<form>` / `<tree>` 等）在 5→6 基本兼容，但 web 客户端对视图的渲染与 GTK 略有差异（[verify]）。

---

## 5. 模块结构：`report/` 与 `static/` 目录  — CONFIRMED（结构指引）

6.0 的模块布局开始规范化，两个目录约定值得在迁移时落实：

- `report/` —— 用于放置报表（RML / 新版报表）相关文件。5.0 的报表常散落在模块根或 `report` 子目录；迁移到 6.0 时建议统一归入 `report/`。
- `static/` —— 用于放置 web 客户端所需的静态资产（JS / CSS / 图片）。这是配合第 4 节新 web 客户端的目录约定。

> 这两个目录是**结构指引**而非强制破坏性变更：5.0 模块即使不放 `report/` / `static/` 也能在 6.0 运行。但按 6.0 约定整理可减少后续升级摩擦。具体子路径（如 `static/src/js`）在 6.0 尚不成熟（[verify]，以 6.0 `web` 模块约定为准）。

---

## 6. 视图 / QWeb / 前端  — CONFIRMED（含 [verify]）

5.0 的视图仍以传统 `arch` 内嵌 XML 的形式存在（`<form>` / `<tree>` / `<field>`），5→6 视图结构基本兼容。但 6.0 的 web 客户端对视图渲染带来新行为：

- 老的 `arch` 视图 XML 在 5→6 兼容；`<tree>`（列表）、`<form>` 标签无破坏性改动。
- 6.0 起字段小组件（widget）与视图继承机制逐步演进；具体 5→6 的 widget 差异属 [verify]，建议以 6.0 源码 `addons/base/` 的视图定义为准。
- 报表的 RML / `report` 机制在 5→6 基本延续；大规模报表/视图重写不属本卷（见红线：14→15 的 `t-raw` / 资产进 manifest）。

---

## 7. HTTP / 邮件 / 二进制  — CONFIRMED（基本不变）

- 控制器：5.0 已是 `from openerp import ...` 体系下通过 `openerp-server` 暴露；6.0 的 HTTP / RPC 接口基本延续 5.0 形态（[verify] 具体的 `openerp.service` / `netrpc`/`xmlrpc` 暴露在 6.0 变化属框架细节）。
- 邮件：5.0/6.0 的 `email_template` / `mail` 雏形尚不成熟；模板与 `res.partner` 邮件字段基本延续。
- 二进制字段：`fields.binary` 用法在 5→6 不变（默认存库字段，存 `ir.attachment` 的时机远在 13.0）。

> 这些是 [verify]-light 的"基本不变"子系统；本卷仅确认它们不在 5→6 破坏性清单内，不展开。

---

## 8. 安全与 `res.groups`（5→6 基本不变）  — CONFIRMED

- 5.0/6.0 的 `security/ir.model.access.csv` 列结构（`id`/`name`/`model_id:id`/`group_id:id`/`perm_read`/`perm_write`/`perm_create`/`perm_unlink`）一致。
- `res.groups` 模型在 5→6 基本不变（重大安全组模块化与权限调整不属本卷；见红线：18→19、19→20 的权限变更）。
- 迁移时只需确认 XML-ID 仍指向存在的 `res.groups` 记录即可。

---

## 9. 模块 / 模型 / 字段映射

除第 2、3 节的清单文件名与清单键外，5→6 模型层**无大规模重命名**（`res.partner.address`→ 拆分 属 6→7；`account.invoice`→`account.move` 属 12→13，均不属本卷）。需要关注的：

| 项目 | 5.0 | 6.0 | 备注 |
|---|---|---|---|
| 清单文件名 | `__terp__.py` | `__openerp__.py` | 第 2 节 |
| `init_xml` / `update_xml` | 两个键 | 合并为 `data` | 第 3 节 |
| `demo_xml` | 键 | `demo` | 第 3 节 |
| `test` 键 | 无 | 新增 | 第 3 节 |
| `web` 键 | 无 | 新增（布尔） | 第 3 节 |
| `report/` / `static/` 目录 | 可选 | 推荐 | 第 5 节 |
| ORM 基类 | `osv.osv` | `osv.osv`（不变） | 6→7 才改 `osv.Model` |

---

## 10. 测试与校验

1. 用 6.0 源码（`openerp-server`）启动；确认模块能被发现。`__terp__.py` 残留虽被兼容，但建议改名。
2. `python3 Odoo5to6Migration/scripts/scan_addon.py /path/to/addons` 跑扫描，逐条处理 `terp-manifest` / `manifest-keys` 发现项（全部 `manual`，无 codemod）。
3. 安装/更新模块：先清 `ImportError` / 清单加载错误（文件名与键）；再确认视图、数据、演示 XML 被正确加载。
4. 在 6.0 沙箱中 `-u <module>` 更新模块，确认无 `__terp__.py` 弃用告警、无 `init_xml`/`update_xml`/`demo_xml` 弃用告警。

---

## 11. `upgrade_code` codemod（5→6 无）  — CONFIRMED

`odoo/upgrade_code/` 引擎自 **18.0** 才出现。6.0 及更早版本（5.0/6.0）**没有任何 `upgrade_code` 脚本**——所有清单改名、键重映射均为**手工**。数据库级结构变更（字段/模型结构）由 **OpenUpgrade** / 官方升级服务处理；本卷只覆盖自定义模块的**代码级**清单迁移。

---

## 12. 迁移实战清单

- [ ] 模块根目录 `__terp__.py` → 重命名为 `__openerp__.py`。
- [ ] 清单中 `init_xml` 与 `update_xml` 合并为 `data`。
- [ ] `demo_xml` → 改名为 `demo`。
- [ ] （可选）测试 XML 列入新增 `test` 键；web 资源标记 `web` 键（[verify]）。
- [ ] 报表文件归入 `report/` 目录；web 静态资产归入 `static/` 目录（结构指引）。
- [ ] 确认 `osv.osv` / `from openerp import ...` 在 5→6 仍有效（**不要**顺手改成 6→7 / 9→10 的写法）。
- [ ] 重扫扫描器期望 0 发现。

---

## 附录 A：研究来源与溯源

- OpenERP 5.0 官方文档（doc.odoo.com/5.0）展示的 `__terp__.py` 结构含 `init_xml` / `demo_xml` / `update_xml` 键——确认 5.0 清单形态。
- 社区文档（odoo.net.cn 等）关于 `__openerp__.py` 的演进说明：6.0 引入 `__openerp__.py` 替代 `__terp__.py`，并引入 `data` / `demo` / `test` / `web` 等简化键。
- OpenERP 6.0 发布说明：引入新的默认 web 客户端、模块结构（`report/` / `static/`）规范化。
- [verify] 标注项（6.0 web 客户端架构细节、`test`/`web` 键加载时机、`report/`/`static/` 子路径约定）因 5.0/6.0 文档多已离线，建议以 6.0 源码树（`openerp/modules/loading.py`、`addons/web` 早期形态）为最终核对基准。
- 红线来源：OCA 迁移指南与 Odoo 版本变更史确认 `osv.osv`→`osv.Model`、`res.partner.address` 移除属 6→7；`__openerp__.py`→`__manifest__.py`、`openerp`→`odoo` 属 9→10；`account.invoice`→`account.move` 属 12→13。
