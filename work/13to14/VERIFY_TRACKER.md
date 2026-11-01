# 13→14 待核实追踪表（VERIFY_TRACKER）

> 修订 SOP：每完成一项核实，把对应行从"待核实"移到下方"已关闭"，并在 `RESEARCH_SOURCES.md`
> 与交付物（`Odoo_Migration_Cookbook_13_to_14.md` + `Odoo13to14Migration/references/*`）同步更新，
> 最后重跑 `check_cookbook_consistency.py` 确保零漂移。

## 待核实（[verify]）

| # | 项 | 当前标注 | 核实动作 |
|---|---|---|---|
| V1 | `stock.picking.move_lines`/`move_line_ids` 字段改名 | [verify] | 在 14.0 `stock.picking` 模型源码查 `move_ids_without_package` / `move_line_ids_without_package` 定义，确认改名并补全白名单 |
| V2 | EE 安全微调（企业版 14.0 group 继承） | [EE-verify] | 对照 EE 14.0 树 `res.groups` 继承链，确认社区版结论可复用 |

## 已关闭（核实后）

（暂无）

## 一致性维护

- 每次修订后运行：`python3 work/13to14/check_cookbook_consistency.py`
- 期望：`CONSISTENCY OK`，所有 token 在 Cookbook↔references 零漂移。
- 任何新引入的 `[verify]` 项必须同时出现在 Cookbook 与至少一个 reference 中。
