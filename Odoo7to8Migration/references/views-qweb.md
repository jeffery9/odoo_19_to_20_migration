# 7→8 视图 / QWeb / 前端映射表（源码核对版）

> 来源：Odoo 8.0 Release Notes + Odoo odoodays-2014《The New API》+ 社区迁移脚本核对。
> 作用域：仅 **7.0 → 8.0**。8.0 在视图层的最大新闻是 **QWeb 报表引擎** 与
> **Bootstrap 3 前端框架 + website builder** 的引入；但大量旧视图/报表写法仍兼容。

## 1. QWeb 报表引擎引入  — CONFIRMED（[verify] 迁移细节）

Odoo 8.0 把报表引擎重心从 RML / OpenOffice / Mako 转向 **QWeb**（HTML+QWeb 模板，
`report_type="qweb-pdf"` / `report_type="qweb-html"`）。RML / Mako 在 8.0 仍可运行
（向后兼容），但新报表应写 QWeb。

- 7.0 报表多用 RML（`report_type` 走 `rml` / `mako`，由 `ir.actions.report.xml` 定义）。
- 8.0 新增 QWeb 报表：`<report id="..." model="..." name="..." file="module.report_tpl"
  report_type="qweb-pdf" string="..."/>`。
- 自定义 RML/Mako 报表在 8.0 仍可安装；迁移到 QWeb 属 **推荐而非强制**。

扫描 id：`qweb-report`（保守正则 `report_type\s*=\s*["'](?:rml|mako)["']`——
命中即提示 deprecated 报表引擎，建议迁 QWeb）。

## 2. 前端：Bootstrap 3 + website builder  — CONFIRMED（[verify] 版本号）

Odoo 8.0 引入 **website builder** 与基于 **Bootstrap 3** 的前端框架，后端 Web 客户端的
CSS/JS 资产也随之前端化。自定义模块若依赖 7.0 时代的老 CSS 类或手写的 jQuery 版本，
需复核；但 8.0 对后端 `web` 视图（form/tree）的破坏性极小。

- 7.0：后端 Web 客户端偏自研样式，无 website builder。
- 8.0：引入 `website` 模块、Bootstrap 3 栅格与组件、QWeb 前端模板。

> `[verify]` Bootstrap 具体大版本（3.x）以 8.0 `addons/web/package.json` 实机为准；
> 无权威 8.0 前端清单，建议以 8.0 资产为准核对。

## 3. 视图语法：基本不变（保留）  — CONFIRMED

8.0 的 form / tree / kanban 视图语法与 7.0 高度兼容：`<tree>`、`<field>`、`attrs`、
`states`、`<button type="object"|"action">`、`<notebook>` 等均保留。本对**没有**
`tree`→`list`（17→18）、`t-raw` 移除（14→15）、`t-field-options`→`t-options`（11→12）
等视图破坏。Workflow 按钮（`<button type="workflow">`）在 8.0 仍存在（11.0 才移除）。

## 4. `ir.actions.act_window.view` 模型：8.0 仍存在  — CONFIRMED（红线提示）

8.0 **保留** `ir.actions.act_window.view` 视图绑定模型；它到 **11→12** 才被移除。
7→8 不要删除已有 `act_window.view` 记录（那是 11→12 的事）。

## 5. 红线（勿套用更晚版本的视图/前端改动）

- `ir.actions.act_window.view` 移除 —— **11→12**。
- `t-field-options` → `t-options` —— **11→12**。
- `t-raw` 移除 / `ir.model*` 访问移除 / 资产进 `__manifest__.py` —— **14→15**。
- `<tree>` → `<list>` —— **17→18**。
- `attrs` / `states` 动态表达式硬拒 —— **16→17** 区间。
- 前端 Bootstrap 重大跃进（OWL 前第一代重构）—— **11.0** 起，更大跃进在 **13/14**。

## 6. 相关 ORM 标记（与 views 协同）

视图中常引用 new-API 计算字段 / `@api.depends` 字段；这些字段声明见 `references/orm-api.md`
（`fields.Char` 等类属性、 `_fields` 容器）。QWeb 报表模板本身不涉及 `self.env` 旧签名。
