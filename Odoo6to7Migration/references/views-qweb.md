# 6→7 视图 / QWeb / 前端映射表（源码核对版）

> 来源：OpenERP 7.0 Release Notes + dbi-services 6→7 博文 + 7.0 源码 `addons/web` 资产核对。
> 作用域：仅 6→7。6→7 的 XML 视图改动重点是"Web 客户端重写 + Bootstrap"，`sheet`/`header`/`footer` 与 `version="7.0"` 是本卷新增视图特性。

## 1. 根视图加 `version="7.0"`  — CONFIRMED

- 6.0：`<form>` / `<tree>` / `<kanban>` 无 `version` 属性。
- 7.0：建议给根视图元素加 `version="7.0"`，7.0 解析器据此启用新视图特性。
- 示例：

  ```xml
  <form version="7.0">
      <header>
          <button name="action_confirm" type="object" string="Confirm" states="draft"/>
      </header>
      <sheet>
          <group>
              <field name="name"/>
          </group>
          <footer>
              <p>Footer note.</p>
          </footer>
      </sheet>
  </form>
  ```

## 2. `sheet` / `header` / `footer` 布局标签  — CONFIRMED

- 7.0 引入 `<sheet>`（表单主体容器）、`<header>`（状态栏/按钮区）、`<footer>`（页脚/HTML 区）。
- 视图内 **允许直接写 HTML**（6.0 受限）。
- 扫描 id：`view-bootstrap`（正则 `version="7.0"|<sheet>|<header>|<footer>`，保守匹配；命中即提示此处使用了 7.0 视图特性，需人工确认结构完整性）。

## 3. 前端 Bootstrap  — CONFIRMED（框架）/ [verify]（版本号）

- 7.0 新 Web 客户端全面切到 Bootstrap CSS（自研旧框架退役）。
- `[verify]` Bootstrap 具体大版本号（3.x？）无权威 6→7 前端清单；以 7.0 源码 `addons/web` 资产为准。

## 4. 红线

- `attrs`/`states` 动态表达式硬拒 → 16→17；`tree`→`list` → 17→18；`t-raw` 移除 → 14→15。
- 资产进 manifest `assets` 键 → 14→15。6→7 全部保留旧视图写法（仅新增 `version`/`sheet`/HTML 放开）。
