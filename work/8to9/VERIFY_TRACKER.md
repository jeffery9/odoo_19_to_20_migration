# 8→9 待核实追踪表（VERIFY_TRACKER）

> 修订 SOP：每完成一项核实，把对应行从"待核实"移到下方"已关闭"，并在 `RESEARCH_SOURCES.md`
> 与交付物（`Odoo_Migration_Cookbook_8_to_9.md` + `Odoo8to9Migration/references/*`）同步更新，
> 最后重跑 `check_cookbook_consistency.py` 确保零漂移。

## 待核实（[verify] / [EE-verify]）

| # | 项 | 当前标注 | 核实动作 |
|---|---|---|---|
| V1 | Material Design 在 9.0 的具体落地细节（类名 / SCSS 变量） | [verify] | 在 9.0 安装查 `web` 模块资产，确认样式命名；据此收紧或移除标注 |
| V2 | 变为 Enterprise-only 的完整模块清单及 XML-ID 去向 | [EE-verify] | 对照 EE 9.0 树 module 列表，确认 Community 版结论可复用 |

## 已关闭（核实后）

（暂无）

## 一致性维护

- 每次修订后运行：`python3 work/8to9/check_cookbook_consistency.py`
- 期望：`CONSISTENCY OK`，所有 token 在 Cookbook↔references 零漂移。
- 任何新引入的 `[verify]` 项必须同时出现在 Cookbook 与至少一个 reference 中。
