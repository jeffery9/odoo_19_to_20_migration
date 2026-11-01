# 11→12 视图 / QWeb / 前端映射表（源码核对版）

> 来源：`OCA Migration to version 12.0` + 社区（Cybrosys / Oejia）+ 12.0 源码核对。
> 作用域：仅 11→12。11→12 的 XML 视图改动极小（动作绑定 + QWeb 属性），`attrs`/`states`/`tree` 均保留。

## 1. `ir.actions.act_window.view` 模型移除  — CONFIRMED

- 11.0：用 `ir.actions.act_window.view` 记录把窗口动作绑定到特定视图。
- 12.0：该模型移除。视图绑定改为动作上的 `view_ids`（o2m）或 `views`。
- Before：

  ```xml
  <record id="action_x" model="ir.actions.act_window">
    <field name="res_model">my.model</field>
    <field name="view_mode">tree,form</field>
  </record>
  <record id="x_view" model="ir.actions.act_window.view">
    <field name="act_window_id" ref="action_x"/>
    <field name="view_id" ref="my_model_view_tree"/>
    <field name="view_mode">tree</field>
  </record>
  ```

- After：删除该记录，在 `action_x` 上加

  ```xml
  <field name="view_ids" eval="[(5,0,0),(0,0,{'view_mode':'tree','view_id':ref('my_model_view_tree')})]"/>
  ```

- 扫描 id：`act-window-view`（正则 `model\s*=\s*["']ir\.actions\.act_window\.view["']`）。

## 2. QWeb `t-field-options` → `t-options`  — CONFIRMED

- 11.0：`<span t-field="r.date" t-field-options='{"widget":"date"}'/>`。
- 12.0：`t-field-options` 重命名为 `t-options`。
- 扫描 id：`t-field-options`（正则 `t-field-options`）。

## 3. 前端依赖（轻微）  — [verify]

- 12.0 沿用 Bootstrap 4 / jQuery 3（在 12 已就位），更大的前端跃进在 13/14。
- 依赖旧 Bootstrap 3 类的自定义 widget 需复核，但 11→12 的 JS 断裂远小于后续版本。
- 来源分歧：无权威 12.0 前端清单，建议以 12.0 `web.assets_*` 实机为准。

## 红线

- `attrs`/`states` 硬拒 → 16→17；`tree`→`list` → 17→18；`t-raw` 移除 → 14→15；
- `invisible`/`readonly` 动态表达式失效 → 14→16 区间。11→12 全部保留旧写法。
