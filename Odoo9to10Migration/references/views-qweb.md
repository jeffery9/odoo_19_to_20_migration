# 9→10 视图 / QWeb / 前端 映射表（源码核对版）

> 来源：OCA `Migration to version 10.0` + Odoo 10.0 源码核对（视图继承选择器收紧）。
> 作用域：仅 9→10。大规模 QWeb 重写（`t-raw` 移除、`ir.model*` 访问移除、资产进 manifest）属 14→15，不在本表。

## 1. 视图继承选择器清理  — CONFIRMED

- 旧的**字符串选择器**（`position="after"` 依赖字段文本内容、`xpath` 文本匹配）在 10.0 要求改用**属性选择器**（最常用 `name`，或 `xpath` 配 `@name` 等属性表达式）。
- 推荐写法：`<field name="target" position="after"/>` 或 `<xpath expr="//field[@name='target']" position="after"/>`。
- 不要误伤合法 `name=` 属性：本规则只捕获 `select="..."` 字符串选择器。

## 2. 根包装元素 `<openerp>`/`<data>` → `<odoo>`  — CONFIRMED

- XML 文件最外层 `<openerp>` 根元素必须删除，改用 `<odoo>`。
- `<data>` 作为根包装在 10.0 仍被接受，但 `<openerp>` 必须移除。
- 扫描 id：`xml-selector`（正则 `select\s*=\s*"|position\s*=\s*"after"|<openerp>|<data>`；`<data>` 命中需人工确认是否为根包装）。

## 3. QWeb / 前端  — CONFIRMED（基本不变）

- QWeb 模板 `t-*` 指令沿用；`t-field-options`→`t-options` 清理发生在 **11→12**，不属本卷。
- 视图结构（`<form>`/`<tree>`/`<field>`/`attrs`）9→10 无破坏性改动。

## 4. 红线

- `t-field-options`→`t-options` → 11→12；`t-raw` 移除 / `ir.model*` 移除 / 资产进 manifest → 14→15；
- `<tree>`→`<list>` → 17→18；`name_get` 移除 → 17→18。
