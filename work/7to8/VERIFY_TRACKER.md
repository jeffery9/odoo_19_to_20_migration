# 7→8 待核实追踪表（VERIFY_TRACKER）

> 修订 SOP：每完成一项核实，把对应行从"待核实"移到下方"已关闭"，并在 `RESEARCH_SOURCES.md`
> 与交付物（`Odoo_Migration_Cookbook_7_to_8.md` + `Odoo7to8Migration/references/*`）同步更新，
> 最后重跑 `check_cookbook_consistency.py` 确保零漂移。

## 待核实（[verify]）

| # | 项 | 当前标注 | 核实动作 |
|---|---|---|---|
| V1 | QWeb 报表迁移细节（RML/Mako 在 8.0 是否仍安装） | [verify] | 在 8.0 安装查 `ir.actions.report.xml` 是否仍接受 `report_type="rml"`/`"mako"`，确认向后兼容 |
| V2 | Bootstrap 具体大版本（3.x） | [verify] | 在 8.0 安装查 `addons/web/package.json` 确认 Bootstrap 版本号 |
| V3 | EE 安全微调（企业版 8.0 group 继承） | [EE-verify] | 对照 EE 8.0 树 `res.groups` 继承链，确认社区版结论可复用 |

## 已关闭（核实后）

（暂无）

## 一致性维护

- 每次修订后运行：`python3 work/7to8/check_cookbook_consistency.py`
- 期望：`CONSISTENCY OK`，所有 token 在 Cookbook↔references 零漂移。
- 任何新引入的 `[verify]` 项必须同时出现在 Cookbook 与至少一个 reference 中。
