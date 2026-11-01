# 12→13 待核实追踪表（VERIFY_TRACKER）

> 修订 SOP：每完成一项核实，把对应行从"待核实"移到下方"已关闭"，并在 `RESEARCH_SOURCES.md`
> 与交付物（`Odoo_Migration_Cookbook_12_to_13.md` + `Odoo12to13Migration/references/*`）同步更新，
> 最后重跑 `check_cookbook_consistency.py` 确保零漂移。

## 待核实（[verify]）

| # | 项 | 当前标注 | 核实动作 |
|---|---|---|---|
| V1 | 前端 FontAwesome 5 图标改名完整清单 | [verify] | 在 13.0 `web` 资产 / `fontawesome` 包查重命名映射，补全 `views-qweb.md` 清单 |
| V2 | jQuery Promise→原生 Promise 的具体文件范围 | [verify] | 在 13.0 自定义/继承前端模块 grep `$.Deferred`/`$.when`，确认替换范围 |
| V3 | EE 安全微调（企业版 13.0 group 继承） | [EE-verify] | 对照 EE 13.0 树 `res.groups` 继承链，确认社区版结论可复用 |

## 已关闭（核实后）

（暂无）

## 一致性维护

- 每次修订后运行：`python3 work/12to13/check_cookbook_consistency.py`
- 期望：`CONSISTENCY OK`，所有 token 在 Cookbook↔references 零漂移。
- 任何新引入的 `[verify]` 项必须同时出现在 Cookbook 与至少一个 reference 中。
