# 14→15 待核实追踪表（VERIFY_TRACKER）

> 修订 SOP：每完成一项核实，把对应行从"待核实"移到下方"已关闭"，并在 `RESEARCH_SOURCES.md`
> 与交付物（`Odoo_Migration_Cookbook_14_to_15.md` + `Odoo14to15Migration/references/*`）同步更新，
> 最后重跑 `check_cookbook_consistency.py` 确保零漂移。

## 待核实（[verify]）

| # | 项 | 当前标注 | 核实动作 |
|---|---|---|---|
| V1 | `subtype` → `subtype_xmlid` | [verify] | 在 15.0 `mail.message`/`mail.template` 源码核实 `message_post`/`message_notify`/`notify` 参数名确为 `subtype_xmlid`，并确认目标值为 xmlid（单一社区源存在分歧） |
| V2 | EE 前端资产细节（企业版 15.0 资产分包） | [EE-verify] | 对照 EE 15.0 树 `web.assets_*` 分包，确认社区版结论可复用 |

## 已关闭（核实后）

（暂无）

## 一致性维护

- 每次修订后运行：`python3 work/14to15/check_cookbook_consistency.py`
- 期望：`CONSISTENCY OK`，所有 token 在 Cookbook↔references 零漂移。
- 任何新引入的 `[verify]` 项必须同时出现在 Cookbook 与至少一个 reference 中。
- 扫描器门禁：`python3 Odoo14to15Migration/scripts/scan_addon.py /path/to/addons` → 修复后期望退出码 0。
