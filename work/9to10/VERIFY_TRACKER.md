# 9→10 待核实追踪表（VERIFY_TRACKER）

> 修订 SOP：每完成一项核实，把对应行从"待核实"移到下方"已关闭"，并在 `RESEARCH_SOURCES.md`
> 与交付物（`Odoo_Migration_Cookbook_9_to_10.md` + `Odoo9to10Migration/references/*`）同步更新，
> 最后重跑 `check_cookbook_consistency.py` 确保零漂移。

## 待核实（[verify]）

| # | 项 | 当前标注 | 核实动作 |
|---|---|---|---|
| V1 | 安全组模块化是否覆盖全部 OCA 官方列表（有无遗漏的 `base.group_*`） | [verify] | 在 OCA `Migration to version 10.0` 完整清单中核对，确认本卷 8 项是否齐全 |
| V2 | EE 专属模块在 10.0 的归属微调 | [EE-verify] | 对照 EE 10.0 树 module 列表，确认社区版结论可复用 |

## 已关闭（核实后）

（暂无）

## 一致性维护

- 每次修订后运行：`python3 work/9to10/check_cookbook_consistency.py`
- 期望：`CONSISTENCY OK`，所有 token 在 Cookbook↔references 零漂移。
- 任何新引入的 `[verify]` 项必须同时出现在 Cookbook 与至少一个 reference 中。
