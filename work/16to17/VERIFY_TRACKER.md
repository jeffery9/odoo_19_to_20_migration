# 16→17 待核实追踪表（work/16to17）

本表跟踪标注 `[verify]` / `[EE-verify]` 的未定项。修订 SOP：确认来源 → 回写
烹饪书与 `Odoo16to17Migration/references/*.md` → 跑
`work/16to17/check_cookbook_consistency.py` 复核一致性 → 在下方标记 `[CLOSED]`。

核查日期：2026-11-01。

## 仍 OPEN 的 [verify] 项

| # | 项 | 当前标注 | 待确认动作 | 风险 |
|---|---|---|---|---|
| V1 | Bootstrap 4→5 类名替换是否适用 17.0 | `[verify]` | 在 17.0 实机核对 `web.assets_frontend` 捆绑是否 Bootstrap 5 | 若误改，前端类名错乱 |
| V2 | jQuery 是否在 17.0 移除 | `[verify]` | 同上；检查 `$()`/`jQuery()` 是否仍可运行 | 若误改，JS 全崩 |
| V3 | Werkzeug 1.x 对 16→17 的影响 | `[verify]` | 确认 16 实际 werkzeug 版本；若 ≥2.0 则无影响 | 控制器 ImportError/AttributeError |
| V4 | PostgreSQL 精确下限（12 / 13） | `[verify]` | 查 17.0 `odoo/sql_db.py` 版本校验 | 升级前 DB 版本不足 |
| V5 | 缓存失效 API（`invalidate_recordset` 等）强制度 | `[verify]` | 查 17.0 是否强制新写法 | 非硬断裂，最佳实践 |
| V6 | 邮件 composer（`mail.compose.message`）结构变化 | `[verify]` | 17.0 实机核对向导内部结构 | 自定义继承可能错位 |
| V7 | `t-attf-` 弃用是否需在 16→17 主动迁移 | `[verify]` | 确认 Owl 2（16.0）起已弃用；属"早弃用"非 17 新引入 | 低（仅清理） |
| V8 | SCSS→CSS 移除的实际归属版本（18+） | `[verify]` | 在 17→18 / 18→19 步骤确认 | 本步已标注"不移除"，防越界 |

## [EE-verify] 项（Enterprise 专属）

| # | 项 | 状态 |
|---|---|---|
| E1 | Enterprise 安全/权限在 16→17 的微调 | OPEN — 需对照 EE 17.0 树复核 |

## 已 CLOSED（本次核实中确认/纠偏）

- **SCSS 在 17.0 仍编译**（libsass 在 requirements.txt）→ 非 16→17 移除项，已显式排除（C，非 verify）。
- **`mail.channel`→`discuss.channel` 不属 17.0**（归 18.0）→ 已排除出 16→17 作用域（C）。
- **`attrs`/`states` 硬拒**（17.0 源码 `ValidationError`）→ CLOSED as CONFIRMED。
- **无 `upgrade_code` codemod**（17.0 目录 404）→ CLOSED as CONFIRMED。
- **`get_resource_path` 移除 / `file_path`** 替代（17.0 `tools/misc.py`）→ CLOSED as CONFIRMED。
- **`<tree>` 在 17.0 仍合法** → CLOSED as CONFIRMED（作用域守卫：tree→list 归 17→18）。
