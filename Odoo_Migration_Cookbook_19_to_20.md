# Odoo 20.0 迁移烹饪书（19.0 → 20.0）

> **适用范围**：Odoo **19.0 → 20.0** 自定义插件（CE 与 EE）升级。
> **体例说明**：本烹饪书（Cookbook）为原创单卷，内容基于 Odoo 官方 `upgrade_code` codemod 脚本库（`odoo/upgrade_code/`，含脚本名与改写契约）、`odoo/odoo` 的 **19.0 / 20.0** 两个分支源码核实（核实基准日 2026-10-11），以及社区 19→20 升级文交叉印证；并与同目录 `Odoo19to20Migration/` 的机器可读映射表（Skill，6 份 references）保持事实一致——本书可读性强，Skill 可被 agent 直接调用。姊妹卷为《Volume I（修复版）》与《Volume II · Closing the Gaps》PDF，本 `.md` 为可编辑统一卷。
> **可信度标记**：`CONFIRMED` = 多源交叉核实（含 20.0 源码/ codemod 契约）；`[verify]` = 单一社区来源、待 20.0 源码最终确认；`[EE-verify]` = Enterprise 专属、必须对照 EE 20.0 树复核，部署前不得当作已验证内容呈现。
> **红线**：绝不臆造 XML-ID 或方法名；查不到的标识符一律标 `[verify]` / `[EE-verify]`；只收录首次出现在 **[19.0, 20.0]** 的变更。

---

## 第 0 章 · 导言

### 0.1 为什么是 19→20

Odoo 20 是一次"**安全模型与 API 收口**"的版本：头号破坏性变更是访问权限文件的格式重写（`ir.model.access.csv` → `security/ir.access.csv`，`operation` 字符串 + 规则域内联），几乎每个带自定义权限的模块安装即崩（`KeyError: 'ir.rule'`）。与此同时，ORM/Python 层有一批早已 deprecated 的 API 在 20.0 被**硬移除**（`check_access_rights`、`toggle_active`、`ormcache` 工具、`group_operator`、`odoo.osv.expression`、`pytz`、`_sql_constraints`、`read_group` 旧签名等），缓存失效、SQL 报表、二进制/Excel/PDF 工具链也被重新整理。前端 Owl 3 的收尾（`t-set` 上提、`DropdownItem` 改 `attrs`）由 codemod 覆盖。

与 18→19（"重底座"：ORM 包拆分 + Owl 2→3 + `res.groups` privilege 重构 + 数据模型大改名）相比，**19→20 更接近一次"把遗留 API 清理干净"的升级**，codemod 覆盖率高，纯手工项集中在安全文件、业务模型改名与视图 xpath。建议排期：扫描 → `upgrade_code --from 19.0`（codemod 先跑）→ 人工映射收尾 → 校验 → 报告。

### 0.2 版本作用域纪律（最重要的一条）

> **变更归属于它首次出现的版本。** 19→20 只收"首次出现在 [19.0, 20.0]"的破坏性变更；更早或更晚的改动不得误带入。

已被显式排除在 19→20 之外、属于更早版本的改动（不要把它们当作 19→20 的新断裂来重复改动）：

| 变更 | 真实归属版本 | 说明 |
|---|---|---|
| ORM 包拆分（`odoo/models.py` 等 → `odoo/orm/`） | **19.0** | 19.0 已完成，20.0 只是收口 `odoo/osv/` 移除与 `odoo.tools` 导出面整理 |
| Owl 2 → Owl 3 框架迁移 | **19.0** | 19.0 已落地；19→20 仅 `t-set` 上提（`19.1-00`）、`DropdownItem` props 等收尾 |
| `<tree>` → `<list>` | **17.5**（codemod `17.5-01`） | 19.0 已硬拒绝 `<tree>`；若插件仍残留 `<tree>`，对应 legacy codemod 会收口，但非 19→20 新引入 |
| 模型级 `models.Constraint`（`_sql_constraints` 改写） | **18.1**（codemod `18.1-00`） | 同上为 legacy 收口 |
| 路由 `type='json'` → `type='jsonrpc'` | **18.1**（codemod `18.1-02`） | 同上为 legacy 收口 |
| `check_access` / `has_access` / `Domain` API（`from odoo import Domain`） | **18.0 / 18.1** | 早已存在，19→20 只是把仍写旧式的代码强制迁移 |
| `group_operator` → `aggregator` | **17.2** | 18 起已事实生效，20.0 才硬移 `group_operator=`（CONFIRMED，19 已告警 "Since Odoo 18…"） |
| `res.groups` 的 category → privilege 重构 | **19.0** | 19.0 已完成，20.0 安全文件格式重写是另一回事 |
| `account.group` 层级重构（→ `account.account` `parent_id`） | **19.3（Online）** | codemod `19.3-00-account-groups`，`--to ≥ 19.3` 才触发；纯 19→20 CE 视部署版本而定 |

### 0.3 推荐工作流（详见第 11、12 章）

1. **扫描（triage）** → 2. **跑 codemod**（`upgrade_code --from 19.0`）→ 3. **应用人工映射**（安全文件、业务模型/字段改名、视图 xpath、残留旧 API）→ 4. **校验**（`-u` + 测试 + 清 `KeyError`/`TypeError`/`Domain` 报错）→ 5. **出报告**。

---

## 第 1 章 · 框架与运行时

### 1.1 Python 底座抬升 — CONFIRMED

- 20.0 的 Python 下限从 19 的 **3.10** 抬到 **3.12**（`odoo/release.py` 的 `MIN_PY_VERSION`）；核心开始使用 PEP 695 泛型。
- 影响：旧代码里依赖 3.10/3.11 专属行为的写法需复核；CI 镜像必须上 3.12。

### 1.2 `odoo/http.py` → 包、`odoo/osv/` 移除 — CONFIRMED

- `odoo/http.py` 变为 `odoo/http/` **包**，但公开导入路径不变（`from odoo import http` 仍可）。
- **`odoo/osv/` 目录在 20.0 被移除**：最重要的是 `odoo.osv.expression` 不再可用，域表达式须改用 `Domain`（见第 4 章）。
- `from odoo import models, fields, api` 仍是规范写法（`odoo.models|fields|api` 在 19/20 都是 shim 包，导入不变）。

### 1.3 `odoo.tools` 导出面整理 — CONFIRMED

`odoo.tools` 在 20.0 的公开导出面变化：

| 19（`odoo.tools`） | 20.0 | 来源 |
|---|---|---|
| `Query` | **移除** → `from odoo.orm.query import Query`（19 经 `odoo.tools` 可达，20 必须显式从 `odoo.orm.query` 导入） | `api-deltas-vol2.md` |
| `ormcache` / `ormcache_context` | **移除** → `@api.ormcache(...)`（见第 5 章） | `api-deltas-vol2.md` |
| `convert_xml_import` / `convert_csv` / `convert_sql` | 内部化，不再从 `odoo.tools` 导出 | `api-deltas-vol2.md` |
| `SQL` | **新增**（公开）| `odoo/tools/sql.py` 的 `SQL` 现在经 `odoo.tools` 公开 |
| `BinaryValue` / `BinaryBytes` | **新增**（公开，原 `odoo.tools.binary` 私有）| `from odoo.tools import BinaryValue, BinaryBytes` |
| `drop_view_if_exists` | **新增**（公开）| `api-deltas-vol2.md` |

---

## 第 2 章 · 安全与 res.groups（头号断裂）

### 2.1 访问文件：`ir.model.access.csv` → `security/ir.access.csv` — CONFIRMED

Odoo 20 **只加载** `security/ir.access.csv`。旧文件名 `ir.model.access.csv` 被忽略；而在 XML 里写 `<record model="ir.rule">` 会直接抛 **`KeyError: 'ir.rule'`**（该模型在 20 不再以 `ir.rule` 暴露）。这是 19→20 最容易"安装即崩"的改动。

**19（`security/ir.model.access.csv`）：**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_lock,lock,model_my_lock,base.group_user,1,1,1,0
```

**20（`security/ir.access.csv`）：**

```csv
id,name,model_id,group_id/id,operation,domain
access_my_lock,my.lock,my.lock,base.group_user,cru,
```

| 列 | Odoo 20 含义 |
|---|---|
| `model_id` | 技术模型名（`sale.order`），**不再**是 `module.model_x` 形式 |
| `group_id/id` | 用户组 XML-id；空 = 全局规则 |
| `operation` | `crud` / `cru` / `cr` / `c` 等组合字符串；**绝不再用** `perm_*` 列 |
| `domain` | 记录规则域，或留空 |

**转换规则与坑：**

- 19 的 `model_id/id` → 20 的 `model_id`（技术名，去掉模块前缀）。
- 域 `[(1,'=',1)]` / `[('1','=','1')]` 校验失败 → 用**空域**（删掉该行）。
- 域落在非存储字段上会报 *Field has no SQL representation* → 改用存储字段/路径。
- 公司域 `('company_id','in',company_ids+[False])` 失败 → `['|',('company_id','=',False),('company_id','in',company_ids)]`。
- 自定义 `res.groups` 的 XML 必须在 manifest 里列在 `ir.access.csv` **之前**加载。
- **Codemod**：`odoo-bin upgrade_code --script ir-access`（`19.4-00-ir-access`）会自动完成合并（含 `ref()` 引用、true/false 域、互斥组归一化）。

> 这是 19→20 的头号手工项：即便 codemod 能转标准写法，**带自定义域的访问规则**几乎都要人工核对域语法。

### 2.2 `res.groups` 在 20 不变（确认非回归）

- 用户组（`res.groups`）模型本身在 19→20 **未重构**（privilege 重构已在 19.0 完成）；20 只是换访问文件格式。请勿把"安全文件改名"与"组模型重构"混为一谈。

---

## 第 3 章 · ORM 与模型 API

### 3.1 ORM / Python 重命名（CE+EE 除非注明）— CONFIRMED

| Odoo 19 | Odoo 20 | 来源 |
|---|---|---|
| `_sql_constraints = [('name','sql','msg')]` | `_name = models.Constraint('sql','msg')`（属性名 = 约束名） | codemod `18.1-00`；20 为 legacy 收口 |
| `self.fields_view_get(...)` | `self._get_view(...)` | `security-and-orm.md` |
| `self.check_access_rights('read')` | `self.check_access('read')`（抛异常）/ `self.has_access('read')`（布尔） | `security-and-orm.md` |
| `self.check_access_rights('read', raise_exception=False)` | `self.has_access('read')`（布尔） | `security-and-orm.md` |
| `self.user_has_groups('x.group_y')` | `self.env.user.has_groups('x.group_y')` | `security-and-orm.md` |
| `self._context` | `self.env.context` | `security-and-orm.md` |
| `self.env.user.company_id` | `self.env.company` | `security-and-orm.md` |
| `ir.config_parameter.get_param/set_param` | 类型化：`get_int/get_str/get_bool/get_float`、`set_int/set_str/set_bool/set_float` | `security-and-orm.md` |
| `pytz` | `datetime.UTC` 与 `zoneinfo` | `security-and-orm.md` |
| 窗口动作 `toggle_active` | `action_archive` / `action_unarchive` | `security-and-orm.md` |
| `write(archive=True)` | `write(active=False)` | `security-and-orm.md` |
| `mail.thread.cc` | `mail.thread`（模型移除，`mail.thread.cc` 混入了 `mail.thread`） | `security-and-orm.md` / `modules-mapping.md` |

**约束写法示例（20）：**

```python
_name = models.Constraint(
    'unique(code, company_id)',
    'Code must be unique per company.',
)
```

### 3.2 模型 API 增量 — CONFIRMED

| Odoo 19 | Odoo 20 | 来源 |
|---|---|---|
| `check_access_rule(op)` | 并入 `check_access(op)` / `has_access(op)` | `api-deltas-vol2.md` |
| `_filter_access_rules(op)` / `_filter_access_rules_python(op)` | 内部 `_access_domain(op)`；python 过滤器移除 | `api-deltas-vol2.md` |
| `check_field_access_rights(...)` | `check_field_access(field, op)` / `has_field_access(field, op)`（`Literal['read','write']`） | `api-deltas-vol2.md` |
| `toggle_active()` | **移除** → `action_archive` / `action_unarchive` | `api-deltas-vol2.md` |
| `_check_recursion()` / `_check_m2m_recursion(f)` | `_has_cycle(field_name=None)`（19 已有，提早采用） | `api-deltas-vol2.md` |
| `copy_translations(records)` | **移除**，无公开替代 | `api-deltas-vol2.md` |

---

## 第 4 章 · 搜索、域与 read_group

### 4.1 `_name_search` → `_rec_names_search` / `_search_display_name` — CONFIRMED

- `_name_search` 被 `_rec_names_search`（20 里为**元组**形式，codemod `19.5-00-tuple-rec_names_search`）与/或 `_search_display_name` 取代。
- `_search_display_name` 签名：`(self, name, domain=None, operator='ilike', limit=None, order=None)`。

### 4.2 `odoo.osv.expression` → `odoo.orm.domains.Domain` — CONFIRMED（头号 import 断裂）

- `from odoo.osv import expression` 在 20 **直接 ImportError**（`odoo/osv/` 已移除）→ 改用 `from odoo.orm.domains import Domain`。
- `expression.AND/OR` → `Domain.AND/OR`（或 `&`/`|`）；`expression.is_false(m,d)` → `Domain(d).is_false()`；`TRUE/FALSE` → `Domain.TRUE` / `Domain.FALSE`（`FALSE_DOMAIN` → `Domain.FALSE`）。

### 4.3 视图修饰符与裸 SQL 域 — CONFIRMED

- 视图修饰符 `in 'x'` / `not in 'x'` → `== 'x'` / `!= 'x'`（元组成员 `('a','b')` 仍合法）。
- 把**裸 SQL 对象**当域叶：19 仅告警，20 直接抛 `TypeError` → 改写为 `Domain.custom(to_sql=lambda table: SQL(...))`。
- `_read_group_stage_ids(self, stages, domain, order)` → 删掉 `order` 参数。

### 4.4 `read_group` 新签名 — CONFIRMED

- 19：`(domain, fields, groupby, offset, limit, orderby, lazy)`。
- 20：`(domain, groupby=(), aggregates=(), having=(), offset=0, limit=None, order=None) -> list[tuple]`；聚合用 `field:agg` 规格，外加 `__count`。

---

## 第 5 章 · 缓存 / SQL / 字段与域

### 5.1 缓存：`ormcache` → `@api.ormcache` — CONFIRMED

- `from odoo.tools import ormcache`（19）→ `@api.ormcache(...)`（20，类在 `odoo/orm/cache.py`，可选 `cache='stable'`）。
- `ormcache_context` **移除** → 把 context 折进显式参数。
- 内省：`odoo.orm.cache.get_cache_size` / `get_cache_key_counter` / `log_ormcache_stats`。
- **失效**：`registry.clear_cache()` → `self.env.transaction.invalidate_ormcache()`（codemod `19.4-00-ormcache-on-transaction`）。

### 5.2 SQL 报表：`_table_query` → `_table_sql` — CONFIRMED

- `Model._table_query` → `Model._table_sql` 属性，返回 `SQL` 对象。
- `SQL` 组合类不变（`odoo/tools/sql.py`），现经 `odoo.tools` 公开；`cr.execute(SQL(...))` **不得**再传 `params`。
- 查询构造器：`from odoo.orm.query import Query`（19 经 `odoo.tools` 可达，20 必须显式导入）。

### 5.3 字段与域：`group_operator` → `aggregator` — CONFIRMED

- `group_operator=` 在 19 已告警 "Since Odoo 18…"，20.0 **硬移除** → 改用 `aggregator=`。
- 裸 SQL 域叶的 `TypeError` 同样适用于此（见 4.3）。

---

## 第 6 章 · 视图、QWeb 与 Owl 3

### 6.1 Kanban → 卡片（cards）— CONFIRMED

| Odoo 19 | Odoo 20 |
|---|---|
| `project.view_project_kanban` 主体 | `project.view_project_card` |
| `project.view_task_kanban` 卡片/页脚 | `project.view_task_card`，xpath `//t[@t-name='card']//footer` |
| kanban 模板名 | `t-name="card"` |
| `project.view_task_kanban` 引用 | `card_ids="%(project.view_task_card)d"` |

### 6.2 徽标（ribbon）与按钮图标 — CONFIRMED

| Odoo 19 | Odoo 20 |
|---|---|
| `<button icon="fa-check"/>` | `<button icon="check"/>`（名字取自 `web/icons.py`） |
| ribbon `text="Archived" bg_color="bg-info"` | `title="Archived" bg_color="text-bg-info"` + `invisible="active"` |
| 网站片段上的 Font Awesome 类（`fa fa-…`） | Material Symbols 连字；web 客户端用 `oi` + `data-icon` 渲染 |
| `iconFromString` 接受 `fa-` 名 | 不绘制 → 用 `oi` / `data-icon` |

> 网站侧 Font Awesome → Material Symbols 是 19→20 的视觉断裂：空白 FA 图标 = 未迁移。

### 6.3 表单/视图 xpath（已对 20.0 CE 视图核实）— CONFIRMED

| 表单 | 19 xpath | 20 |
|---|---|---|
| 分析账户 | `//header` | 无 header —— 插入带工作流按钮的 `<header>` |
| 工时单 | 加 `button_box` | `div[@name='button_box']` 已存在 |
| 日历事件 | `button_box` | 无 button_box —— 按钮置于 `//sheet/widget[@name='web_ribbon']` 区域 |
| 员工 | `oe_title` | `//h1` 或 `//h1[hasclass('o_employee_form_header_info')]` |
| 招聘职位 | `user_id` | 置于 `department_id` 之后；表单已用 `recruiter_id` |
| CRM | `//div[hasclass('oe_title')]/div` | `//div[hasclass('oe_title')]` |
| 维修申请 | `archive_equipment_request` / `user_id` | `//header`；指派人 `user_ids` |
| 发票合计 | `@class='oe_subtotal_footer'` | `//group[hasclass('oe_subtotal_footer')]` |
| 合作伙伴列表/搜索 | `complete_name` / `group[@name='group_by']` | `display_name` / `//search/group` |
| 用户偏好 | `group[@name='preferences']` | `//page[@name='preferences']` |
| 产品/动作 | `product.product_variant_easy_edit_view` / `product.product_normal_action` | 移除 / `product.product_variant_action` |
| 销售配置菜单 | `sale.prod_config_main` | `sale.menu_sale_config` |
| 项目表单 | `group[@name='extra_settings']` | `//page[@name='settings']` |
| 工时看板页脚 | `footer[@class='mt-0 pt-0']` | `div[@name='ts_footer']` |
| 活动弹窗 / POS 会话 | `company_id` / `move_id` | 置于 `summary` 之后 / `user_id` 之后 |
| POS 小票 | Owl `ReceiptHeader` / `pos-receipt-contact` | `point_of_sale.pos_order_receipt` |
| 销售表单 / 门户侧栏 | `show_update_fpos` / `navspy` | `fiscal_position_id` / `div#sale_order_sidebar_button` |
| 发票/销售/采购行 | `product_id`/`name` 直取 | 置于 `<column name="product_and_description">` 内；`//list/field[@name='product_id']` 不再匹配，须 xpath 直接 list 子节点（`quantity`/`product_qty`/`analytic_distribution`/`account_id`） |

**xpath 总则（已核实）：**

- 视图类型/标签自 19 起即 `<list>`（无 `<tree>`）。
- `[class='X']` 是**精确**匹配——只有当 20 父视图的 class 字符串不再等于 `X` 时才需改继承。
- `string` / `title` **不是**合法的继承选择器——用 `hasclass(...)`、`name`、`id`、`t-call`。
- xpath **不能进入** `t-call` 体——继承被调用的模板，或 xpath 那个 `t-call` 节点本身。

### 6.4 QWeb 与报表 — CONFIRMED

- `web` 内不再假定 wkhtmltopdf：模块 `base_report_wkhtmltox` / `base_report_paper_muncher` 需确认在你的部署中可用。
- `<img t-attf-src="data:image/png;base64,#{rec.img}"/>` →
  `<img t-att-src="image_data_uri(rec.img) if rec.img else '/web/static/img/placeholder.png'"/>`。
- `_render_qweb_pdf` 现在接收**报表动作**的 xmlid（见 7.4）。

### 6.5 Owl 3 收尾 — CONFIRMED（codemod `19.1-00-t-call`）

- 被 `t-call` / `t-snippet-call` 属性消费的 `t-set` 节点，须**上提**到调用之前（codemod `19.1-00-t-call`）。
- `DropdownItem` 接受 `attrs=`；`href=` 与 `dataset=` 是非法 props。
- 完整 JS 迁移助手：`odoo-bin upgrade_code --script owl3-migration`（不属于任何版本区间，须显式运行）。

---

## 第 7 章 · HTTP、邮件与二进制

### 7.1 路由：`type='json'` → `type='jsonrpc'` — CONFIRMED（legacy 收口）

- 面向 web 客户端的 `@http.route(..., type='json')` → `type='jsonrpc'`（codemod `18.1-02`）。
- **外部集成**仍用 JSON-2 `/json/2/<model>/<method>`（20 仍在）——**不要把外部客户端迁走**。

### 7.2 二进制 / Excel / PDF / 时间 — CONFIRMED

| Odoo 19 | Odoo 20 |
|---|---|
| `xlwt` | `xlsxwriter`；写入 `io.BytesIO`，`{'in_memory': True}`，用 `BinaryBytes` 赋值 |
| `xlrd.open_workbook`（`.xlsx`） | `openpyxl`（PK/OfficeOpenXML `.xlsx`）；`xlrd` 仅用于 OLE `.xls` |
| `import PyPDF2` | `from odoo.tools.pdf import PdfFileWriter, PdfFileReader` |
| `odoo.tools.content_disposition` / 旧 http 路径 | `odoo.http.stream` |
| `_render_qweb_pdf(template_xmlid)` | `_render_qweb_pdf(action_xmlid)`（报表**动作** xmlid） |
| 报表解析器内的 `request.env` | 用 `env`；`request.env` 可能抛 `RuntimeError: request not bound` |
| 二进制字段值的 bytes/base64 | `BinaryValue` 对象（可选 `.filename`）；用 `BinaryBytes` 写 |
| `from odoo.tools.binary import BinaryValue`（19 私有） | `from odoo.tools import BinaryValue, BinaryBytes`（20 公开） |
| `resource.calendar.leaves.time_type` | `count_as`（如 `count_as='absence'`） |
| `resource.calendar.tz`、attendance `name`/`day_period` | 移除 |

### 7.3 配置、HTTP、邮件 — CONFIRMED

| Odoo 19 | Odoo 20 |
|---|---|
| server action `state="mail_post"` + `template_id`（+`mail_post_autofollow`） | `mail_post_method` |
| EE server action 的 AI 字段 | `use_in_ai`、`ai_tool_name` 须匹配 `[a-zA-Z0-9_]{1,64}` |
| 设置 xpath `group[@name='preferences']` | `//page[@name='preferences']//group[@name='other_preferences']` |
| 员工设置 xpath | 置于 `employees_setting_container` 之后 |
| 核心 `mail` 里的 `mail.tracking.value` | 安装社区插件 `mail_tracking`；模型名不变 |
| 模型方法内的 `request.website` | `self.env.website`（来自 `context['website_id']`）；`request` 在解析器/ORM 上下文里未绑定 |

---

## 第 8 章 · 模块 / 模型 / 字段映射

> 来源：本目录 `Odoo19to20Migration/references/modules-mapping.md`（基于 19.0/20.0 分支核实，基准日 2026-10-11）。`[EE-verify]` 须对照 EE 20.0 树复核。

### 8.1 模型改名 / 合并 / 移除（源码核实）— CONFIRMED

下表 21 条与 `Core_Models_Changelog.md` 同源，均经 19.0 / 20.0 源码模型集 diff 核实。

| 19 | 20 | 类型 | 说明 |
|---|---|---|---|
| `stock.quant.package` | *（见红线 8.3）* | — | **属 18→19**，19/20 两版都已是 `stock.package` |
| `hr.contract` | *（见红线 8.3）* | — | **属 18→19**，19/20 两版都已是 `hr.version` |
| `hr.expense.sheet` | *（见红线 8.3）* | — | **属 18→19** |
| `crossovered.budget(.lines)` | *（见红线 8.3）* | — | **属 17→18**（EE） |
| `hr.payslip.input.type` | 并入 `hr.salary.rule` | MERGE | EE；`hr.payslip.input` 改挂 `salary_rule_id`，`code`/`name`/`input_suffix`/`user_instructions` 转 related |
| `hr.leave.type` | 移除 | REMOVE | 20.0 无该模型；`hr.work.entry.type` **不是**改名目标（两者并存于 19.0） |
| `hr.version.wizard` / `hr.contract.type` | 移除 | REMOVE | 合同向导与合同类型模型移除 |
| `stock.scrap` | `stock.move`（`is_scrap=True`） | MERGE | 报废改由 `stock.move` 承载，`is_scrap` 为 20.0 **新增**字段（`stock.move`/`stock.move.line`/`stock.lot` 上都有） |
| `stock.return.picking` | `stock.picking._create_return()` | BEHAVIOR | 退货由向导改为方法 |
| `stock.picking.batch` | 仍在 `stock.picking.batch` | MERGE | 模型保留，仅 `stock_picking_batch` 模块并入 `stock`；`depends` 要改 |
| `account.group` | `account.account` 层级 | MERGE | 用 `parent_id` / 计算 `parent_ids` 表达；codemod `19.3-00-account-groups` |
| `payment.provider` | 移除 | REMOVE | 支付体系重构，非改名 |
| `res.bank` | 合并进 `res.partner.bank` | MERGE | `bank_name`/`bank_bic` 变为存储字段 |
| `mail.thread.cc` | 移除 | REMOVE | 抄送能力并入标准 `mail.thread` |
| `product.template.attribute.exclusion` | 移除 | DEP | 排除改 `product.template.attribute.value` 的 `excluded_value_ids`（m2m，限同模板值） |
| `stock_picking_batch` | → `stock` | MODULE | 模块合并，模型名不变 |
| `industry_fsm` / `helpdesk_fsm*` / `documents_fsm` | `project` / `helpdesk` / `documents` | MODULE | `[EE-verify]` |
| `account.asset`（`state='model'`） | `account.depreciation.model` | MODULE | `[EE-verify]` |
| `website_sale_wishlist` / `website_sale_comparison` | 并入 `website_sale` | MODULE | `[verify]` |
| `mail.tracking.value`（核心 `mail`） | `mail_tracking` 插件 | MODULE | `[verify]` |

### 8.2 字段改名 / 移除（源码核实）— CONFIRMED

| 模型（族） | 19 | 20 | 类型 |
|---|---|---|---|
| `stock.move` 等 | `product_uom` | `uom_id` | 改名 |
| `account.move` 报表 | `type` | `move_type` | 改名 |
| `stock.move` | `location_final_id` | `forecasted_location_id` | 改名 |
| `res.partner` | `company_registry` | 移除 → `additional_identifiers`（JSON，按本地化键存多标识） | 移除 |
| `res.partner` | `company_type` | 移除（用布尔 `is_company` 判断） | 移除 |
| `ir.attachment` | `datas` | 移除（`raw` 自 17.0 起即并存，**非改名**） | 移除 |
| `sale.order` | `state='done'` | 移除该状态 | 移除 |
| `mrp.production` | `show_produce_all` | 移除（用 `button_mark_done`） | 移除 |
| `product.template` | `is_storable`（定义在 `stock`） | 上移到 `product` 核心 | 搬迁 |

> **`is_storable` 不是新增**：18.0 起它就定义在 `addons/stock/models/product.py`，20.0 只是上移到 `product` 核心。且 20.0 的 `type` Selection 仍然存在——不要把"可库存判断"改写成删 `type`。

### 8.3 红线：本章曾收录但已被证伪的说法

19→20 是二手资料（论坛、迁移服务商博客）错误最密集的版本对。以下说法曾在早期版本的本章出现，**源码核实不成立**，请勿采用：

| 错误说法 | 真实情况 |
|---|---|
| `hr.contract`→`hr.version` 属 19→20 | 属 **18→19**；19.0 与 20.0 都已是 `hr.version` |
| `hr.expense.sheet`→`hr.expense` 属 19→20 | 属 **18→19** |
| `stock.quant.package`→`stock.package` 属 19→20 | 属 **18→19** |
| `res.users.groups_id`→`group_ids` 属 19→20 | 属 **18→19** |
| `account.analytic.account.group_id`→`plan_id` 属 19→20 | 属 **15→16** |
| `res.partner.mobile` 移除属 19→20 | 属 **18→19**；19/20 均无 `mobile` |
| `project.task.user_id`→`user_ids` 属 19→20 | **不成立**；`user_ids` 自 16.0 已存在 |
| `note.note`→`project.task` | **`note.note` 在 17/18/19/20 均不存在**，纯属虚构 |
| `crossovered.budget`→`budget.analytic` 属 19→20 | 属 **17→18**（EE 预算族整族重写） |
| `hr.payslip.input.type` 改为 `input_usage_payslip` 设计 | `input_usage_payslip` 是 `hr.salary.rule` 上的既有布尔字段（19.0 已有），非替代模型；真实变更是**并入 `hr.salary.rule`** |
| `ir.attachment.datas`→`raw` 是改名 | `raw` 自 17.0 即并存，`datas` 在 20.0 被**移除**，属 FIELD-REMOVE |
| `hr.leave.type`→`hr.work.entry.type` 是改名 | `hr.leave.type` **移除**；`hr.work.entry.type` 在 19.0 已并存，非改名目标 |
| `payment.provider.state`→`is_live`/`is_published` 是字段改名 | `payment.provider` **模型整体移除**，谈字段改名没有意义 |

#### 8.3.1 待核条目（二手资料有，源码未逐条坐实）

以下条目来自早期二手资料，**尚未**用 19.0/20.0 源码逐条核实，使用前请自行复核（`git grep` 两版对照）。列在这里是为了不丢信息，而不是推荐采用：

| 说法 | 状态 |
|---|---|
| `res.partner.bank`：`acc_number`→`account_number`、`acc_holder_name`→`holder_name` | 待核（`res.bank` 合并进 `res.partner.bank` 已证实，字段名未核） |
| `hr.leave`：`holiday_status_id`/`holiday_type`→`work_entry_type_id`/`validation_type` | 待核（`hr.leave.type` 移除已证实，`hr.leave` 侧字段未核） |
| `crm.lead`：`currency_id`→`company_currency` | 待核 |
| `resource.calendar.leaves`：`time_type`→`count_as` | 待核 |
| `account.payment`：`state` 取值 `'in_process'`/`'paid'`→`'paid'`/`'reconciled'` | 待核 |
| `sale.order.line`/`account.move.line` 的 `product_uom_id` 保持不变 | 待核（与 `uom_id` 改名同批，需确认边界） |
| `fleet.vehicle.log.services`：`date`→`date_from`/`date_to` | 待核（该条在 18→19 章也出现，版本归属存疑） |

### 8.4 XML-id 与视图

| 19 | 20 |
|---|---|
| `project.portal_my_home` | `portal.entry` |
| `industry_fsm.fsm_menu_root` | `project.menu_main_pm` **[EE-verify]** |
| `hr_work_entry.work_entry_type_attendance` | `hr_work_entry.generic_work_entry_type_attendance` |
| 法定休假默认 | `hr_work_entry.generic_work_entry_type_legal_leave` |
| 请假类型表单继承 | `hr_holidays.hr_work_entry_type_view_form`（+ 字段 `support_document`、`time_off_selectable`） |
| 工资运行看板 | `hr_payroll.hr_payrun_payslip_kanban_card` **[EE-verify]** |
| EE 预算表单 | `account_budget.view_budget_analytic_form` **[EE-verify]** |
| 报废表单 / 批量拣货表单 | `stock.view_scrap_move_form` / `stock.stock_picking_batch_form`（在 `stock` 中） |
| 心愿单/对比模板 | `website_sale.product_wishlist`、`website_sale.product_compare`、`website_sale.model_product_wishlist` |
| 加入购物车 | `a[@id='add_to_cart']`→`button[@name='add_to_cart']`；包裹：`div[@id='add_to_cart_wrap']`、模板 `website_sale.cta_wrapper`、`#o_wsale_cta_wrapper` |
| `website_sale.product_terms_and_conditions` | 移除 —— xpath 置于 `#o_wsale_product_cta_section` 之后 |
| 对比控制器 | `odoo.addons.website_sale.controllers.cart` |
| EE 工资规则 `category_id`/`struct_id` | `category_ids`/`struct_ids` / `[(6, 0, [ref(...)])]` **[EE-verify]** |

### 8.4 症状 → 修复速查

- 安装时 `KeyError: 'ir.rule'` → 安全文件未转换（第 2 章）。
- `Field has no SQL representation` → 规则域落在非存储字段。
- `RuntimeError: request not bound` → 模型/报表代码里的 `request.env` / `request.website`（第 7 章）。
- 网站 Font Awesome 图标空白 → Material Symbols / `oi` + `data-icon`（第 6.2 章）。
- 公开页 500（`t-attf-value="#{user.partner_id.email}"`）→ `t-att-value="request.env.user.partner_id.email if not request.env.user._is_public() else ''"`。
- JSON-2 `/json/2` 与 XML-RPC `/xmlrpc/2` 在 20 **仍在** —— 勿把外部客户端迁走。

---

## 第 9 章 · 会计、支付与 EE 专属

### 9.1 `account.group` → `account.account` 层级 — CONFIRMED

- 会计科目的分组维度从 `account.group` 改为 `account.account` 自身的层级（`parent_id` + 计算 `parent_ids`）。
- Codemod `19.3-00-account-groups` 会把 `account.group` 的 CSV/数据改写为 `account.account` 层级 + `parent_id`。
- 另：`19.3-00-account-report-foldable` 把 `foldable` 的 XML 值归一化为布尔。

### 9.2 支付状态 — CONFIRMED

- `payment.provider` 的 `state` 字段改为 `is_live` / `is_published`（第 8.2 章）。
- `account.payment` 的 `state`：`'in_process'`/`'paid'` → `'paid'`/`'reconciled'`（第 8.2 章）。

### 9.3 固定资产（EE）— [EE-verify]

- `account.asset`（`state='model'`）改为 `account.depreciation.model`（Enterprise 专属，须对照 EE 20.0 树复核）。

### 9.4 预算（EE）— [EE-verify]

- `crossovered.budget(.lines)` 改为 `budget.analytic` / `budget.line`（Enterprise 专属）。

### 9.5 AI 插件（EE）— [EE-verify]

- EE server action 的 AI 字段：`use_in_ai`、`ai_tool_name`（须匹配 `[a-zA-Z0-9_]{1,64}`）。EE AI 插件相关改动须对照 EE 20.0 树复核。

---

## 第 10 章 · 测试与校验

### 10.1 测试模式上下文 — CONFIRMED

- `registry_enter_test_mode()` / `registry_leave_test_mode()` → `with self.registry_test_mode():`。

### 10.2 查询断言 — CONFIRMED

- `assertQueriesContain` **移除**；`assertQueries` / `assertQueryCount` 保留；新增匹配器 `QueryLike`（家族：`Like`、`WhitespaceInsensitive`、`Approx`）。

### 10.3 `MockHTTPClient` 与 HttpCase — CONFIRMED

- 新增 `MockHTTPClient` 上下文管理器（patch `requests.sessions.Session.send`，可嵌套）：按 `method`/`url`/`matcher(request)` 匹配；响应用 `return_json`/`return_body`、`return_status`/`return_headers`；断言 `assert_called(n)`、`assert_called_once()`、`assert_not_called()`。
- HttpCase 增强：`self.session`、`update_session(**)`、`update_session_context(**)`、`csrf_token()`、`file_read(path) -> BinaryBytes`、`mock_datetime_and_now(dt)`、`response.raise_for_status()`（带 Odoo 载荷）。

---

## 第 11 章 · upgrade_code codemod

### 11.1 命令 — CONFIRMED

```bash
odoo-bin upgrade_code --from 19.0 --addons-path /path/to/addons        # 区间 [19.0, 当前] 内所有脚本
odoo-bin upgrade_code --script ir-access --addons-path /path/to/addons # 单个脚本（子串匹配即可）
odoo-bin upgrade_code --from 19.0 --glob '**/models/*.py' --dry-run    # 仅预览
python3 odoo/cli/upgrade_code.py --from 19.0 --addons-path ...         # 独立运行（解析路径）
```

- `--from` / `--script` 互斥，必填其一；`--to` 含上界，默认 = 运行版本。
- 每文件打印 `updated:` / `deleted:`；**任何改动都令退出码为 1（CI 门禁）**。
- codemod 只改**源码**：`.py .js .css .scss .xml .csv .po .pot`；数据库数据升级仍在模块 `pre/post` 脚本里。

### 11.2 19→20 会介入的脚本 — CONFIRMED

| 脚本 | 改写内容 |
|---|---|
| `17.5-01-tree-to-list` | 视图模式 `tree`→`list`（view_mode/binding 字段、archs）—— legacy 收口 |
| `18.1-00-sql-constraint` | `_sql_constraints = [...]` → `models.Constraint(...)` —— legacy 收口 |
| `18.1-02-route-jsonrpc` | 路由 `type='json'` → `type='jsonrpc'` —— legacy 收口 |
| `18.2 / 18.3 l10n` | 科目模板记录；财政position 税种映射（`tax_src_id`/`tax_dest_id` → 替代税种列） |
| `18.5-00-domain-dynamic-dates` | 域内联一元负号常量；`18.5-00-no-tax-tag-invert` 税种 `formula` 符号；`18.5-00-deprecated-properties` 废弃属性字段 |
| `19.1-00-t-call` | 把消费的 `t-set` 上提到 `t-call` / `t-snippet-call` 之前（Owl 3） |
| `19.3-00-account-groups` | `account.group` CSV/数据 → `account.account` 层级 + `parent_id` |
| `19.3-00-account-report-foldable` | `foldable` XML 值归一化为布尔 |
| `19.3-00-base64-in-xml` | 内联 `type="base64" … file=` 载荷 → 20 加载形式 |
| `19.4-00-ir-access` | `ir.model.access.csv` + `<record model="ir.rule">` XML → `security/ir.access.csv`（`crud` 操作、域归一化） |
| `19.4-00-ormcache-on-transaction` | `registry.clear_cache` → `transaction.invalidate_ormcache` |
| `19.5-00-tuple-rec_names_search` | `_rec_names_search = ['name']` → 元组 |
| `20.0-00-search-date-filters` | 从 `date` 搜索过滤器丢弃 `start_month` / `end_month` 式 attrs |

> 无版本前缀、永不自动选中的脚本：`owl3-migration.py`（用 `--script owl3-migration` 显式跑）；辅助 `tools_etree.py`、`tools_js_expressions.py`（可作 `odoo.upgrade_code.tools_etree` 等导入）。

**版本作用域提示**：上表中 `17.5` / `18.1` / `18.2` / `18.3` / `18.5` 前缀的脚本是**更早版本 codemod 的遗留收口**——只有当插件源码仍残留对应遗留语法时才会改写；它们不是 19→20 新引入的破坏性变更。真正的 19→20 增量集中在 `19.1` / `19.3` / `19.4` / `19.5` / `20.0` 这几组（t-call 上提、account 层级、ir.access 安全文件、ormcache 失效、rec_names_search 元组化、日期过滤器）。

### 11.3 自写脚本 — CONFIRMED

```python
def upgrade(file_manager):
    files = [f for f in file_manager if f.path.suffix == '.py']
    for fileno, file in enumerate(files, start=1):
        content = file.content                      # 惰性读取
        file.content = content.replace('old_api(', 'new_api(')
        file_manager.print_progress(fileno, len(files))
```

- 文件对象：`path`（pathlib）、`addon`、惰性 `content`（赋值不变 = 无操作；赋值 `None` = 保存时删除）。
- 管理器：迭代、`len`、`get_modules()`、`get_file(module, name)`、`add_to_summary(msg)`（结尾打印）、`print_progress(cur, total, file_name)`。
- 自定义脚本必须位于 `odoo/upgrade_code/` 内（`--script` 拒绝该目录外的路径）；或直接从 Python 调 `odoo.cli.upgrade_code.migrate(...)`。

---

## 第 12 章 · 迁移实战清单

1. **环境**：Python ≥ 3.12；拉 20.0 源码与插件树；建干净 git 分支。
2. **扫描**：`python3 Odoo19to20Migration/scripts/scan_addon.py /path/to/addons`（exit 1 = 有发现），按报告分组处理。
3. **codemod 先跑**：`odoo-bin upgrade_code --from 19.0 --addons-path /path/to/addons --dry-run` → 真实运行 → 逐文件 review `git diff` 并提交。重点确认 `19.4-00-ir-access`（安全文件）与 `19.3-00-account-groups`（会计层级）的改写结果。
4. **人工映射**（scanner 标 `manual` 的项）：
   - 安全文件剩余自定义域（第 2 章）；
   - 业务模型/字段改名（`res.users.groups_id`→`group_ids`、`res.partner.company_type`→`is_company`、`project.task.user_id`→`user_ids`、`ir.attachment.datas`→`raw` 等，第 8 章）；
   - 视图 xpath（kanban→card、表单 header/button_box 变化，第 6.3 章）；
   - 残留旧 API（`pytz`、`check_access_rights`、`toggle_active`、`ormcache` 工具、`group_operator`、`odoo.osv.expression`、`read_group` 旧签名，第 1–5 章）；
   - 二进制/Excel/PDF 工具链（`xlwt`→`xlsxwriter`、`PyPDF2`→`odoo.tools.pdf`、`content_disposition`→`http.stream`，第 7.2 章）。
5. **校验**：重扫期望 0；20.0 沙箱 `odoo-bin -u <module> --test-tags /<module>`；先修 `KeyError: 'ir.rule'`（安全文件）、再修 `ImportError`（`odoo.osv.expression` / `ormcache` / `Query`）、再修 `TypeError`（`Domain` 裸 SQL 叶 / `read_group` 签名）、最后修视图 RNG 校验与域 `TypeError`。
6. **报告**：逐插件汇总 codemod 改动、人工编辑（附所用 references 锚点）、剩余 `[EE-verify]` 项、测试状态。

---

## 附录 · 版本作用域红线与来源

- **核实基准**：条目对照 `github.com/odoo/odoo` 的 **19.0 / 20.0** 分支，基准日 2026-10-11；codemod 契约取自 `odoo/upgrade_code/`（脚本名见第 11 章）。Enterprise 专属项标 `[EE-verify]`，须对照 EE 20.0 树复核。
- **头号断裂**：`security/ir.access.csv` 安全文件格式重写（`KeyError: 'ir.rule'`）。
- **已排除（非 19→20）**：`<tree>`→`<list>`（17.5）、`_sql_constraints`→`models.Constraint`（18.1）、`type='json'`→`jsonrpc`（18.1）、`check_access`/`Domain` 引入（18.0/18.1）、`group_operator`→`aggregator`（17.2）、ORM 包拆分与 Owl 3 框架（19.0）、`res.groups` privilege 重构（19.0）。
- **绝不臆造标识符**：查不到的 xml-id / 方法名一律标 `[verify]` / `[EE-verify]`；不静默"补全"。
- 配套机器可读映射见 `Odoo19to20Migration/references/`（security-and-orm / binary-http-mail / views-qweb-owl / modules-mapping / api-deltas-vol2 / upgrade-code）。
