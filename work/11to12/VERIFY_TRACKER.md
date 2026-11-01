# 11→12 待核实追踪表（VERIFY_TRACKER）

> 修订 SOP：每完成一项核实，把对应行从"待核实"移到下方"已关闭"，并在 `RESEARCH_SOURCES.md`
> 与交付物（`Odoo_Migration_Cookbook_11_to_12.md` + `Odoo11to12Migration/references/*`）同步更新，
> 最后重跑 `check_cookbook_consistency.py` 确保零漂移。

## 待核实（[verify]）

| # | 项 | 当前标注 | 核实动作 |
|---|---|---|---|
| V1 | 前端 Bootstrap 4 / jQuery 3 在 12.0 的版本归属 | [verify] | 在 12.0 安装查 `package.json` / `web` 资产，确认 Bootstrap 版本；据此收紧或移除标注 |
| V2 | `Binary` 字段默认存 `ir.attachment` 时机 | [verify] | 在 12.0 `odoo/fields.py` 查 `Binary` 类 `attachment` 默认值（是否仍为 False） |
| V3 | EE 安全微调（企业版 12.0 group 继承） | [EE-verify] | 对照 EE 12.0 树 `res.groups` 继承链，确认社区版结论可复用 |

## 已关闭（核实后）

（暂无）

## 一致性维护

- 每次修订后运行：`python3 work/11to12/check_cookbook_consistency.py`
- 期望：`CONSISTENCY OK`，所有 token 在 Cookbook↔references 零漂移。
- 任何新引入的 `[verify]` 项必须同时出现在 Cookbook 与至少一个 reference 中。
