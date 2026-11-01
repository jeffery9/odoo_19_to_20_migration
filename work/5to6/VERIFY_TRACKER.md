# 5→6 验证追踪（VERIFY_TRACKER）

> 记录本卷所有 `[verify]` / `[EE-verify]` 项的状态、动作与进度。
> 一旦某项被确认，从 Cookbook 与 `references/` 的 `[verify]` 标记中移除，并在本表标记 `DONE`。

## 待验证项

| # | 项 | 标记 | 状态 | 动作 / 进度 |
|---|---|---|---|---|
| 1 | 6.0 新默认 web client 的架构细节（与 7.0+ `web` 模块差异） | [verify] | OPEN | 核对 6.0 源码 `addons/web` 早期形态；勿套用更晚约定 |
| 2 | `report/` 与 `static/` 子路径约定（如 `static/src/js`） | [verify] | OPEN | 以 6.0 `web` 模块目录约定为准 |
| 3 | `test` 清单键的加载时机（安装/更新均加载？） | [verify] | OPEN | 核对 6.0 源码 `openerp/modules/loading.py` |
| 4 | `web` 清单键（布尔）的确切语义 | [verify] | OPEN | 核对 6.0 源码 manifest 解析 |
| 5 | 5→6 视图 widget / 视图继承差异 | [verify] | OPEN | 核对 6.0 源码 `addons/base/` 视图定义 |

## 已确认项（CONFIRMED，无需追踪）

- `__terp__.py` → `__openerp__.py`（清单文件名改名）
- `init_xml`/`update_xml` → `data`；`demo_xml` → `demo`（清单键重映射）

## EE 验证项

- 无（本卷为 CE，无 [EE-verify] 项）。
