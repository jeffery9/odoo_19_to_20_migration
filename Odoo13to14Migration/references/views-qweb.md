# 13→14 视图 / QWeb / 前端映射表（源码核对版）

> 来源：`OCA Migration to version 14.0` 官方指南 + odoo/odoo#53335。
> 作用域：仅 13→14。13→14 的 XML 视图改动集中在 `invisible`/`readonly` 约束与动作访问。

## 1. `invisible` / `readonly` 动态表达式 → `attrs`  — CONFIRMED

- 14.0：`invisible="state=='draft'"` / `readonly="x>0"` 这类**动态表达式被拒**（视图加载报错）。
- 必须改用 `attrs` domain：`attrs="{'invisible': [('state','=','draft')]}"`。
- **唯一例外**：直接 context 查询 `invisible="context.get('invisible')"` 仍合法。
- `attrs` 在 14.0 **完全保留且推荐**；其"硬拒"发生在 **16→17**（改为内联表达式）。
- 扫描 id：`invisible-expr`（正则 `(invisible|readonly)="[^"]*(==|!=|<=|>=|<|>|\{)`）。

## 2. `ir.actions.*` 对象访问移除  — CONFIRMED

- 14.0 移除对 `ir.actions.act_window` / `.server` / `.client` / `.report` 的直接访问。
- 读取动作字典用 `self.env['ir.actions.act_window']._for_xml_id('module.action_id')`。
- 操作记录用 `sudo()`；前端/HTTP 走 `/web/action/load`。
- 注：与 **15.0 的 `ir.model*` 访问移除** 是**不同对象**；13→14 只限 `ir.actions.*`。

## 3. 前端

- 14.0 **仍使用 SCSS**（SCSS 编译移除的误传属 17.0，见 16→17 烹饪书纠错）；`t-raw` 移除在 **14→15**。
- 更大前端跃进（Owl 框架全面铺开）在 **15→16 / 17→18**。

## 红线

- `attrs`/`states` 硬拒 → 16→17；`tree`→`list` → 17→18；`t-raw` 移除 → 14→15；
- `ir.model*` 访问移除 → 14→15（与本表 `ir.actions.*` 移除是不同对象）。
