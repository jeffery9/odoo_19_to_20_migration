# 12→13 字段 / 模型属性 / 数据映射表（源码核对版）

> 来源：`OCA Migration to version 13.0` + shine-it + 13.0 源码核对。
> 作用域：仅 12→13。

## 1. `dp.get_precision` 去除 → 直接用 `digits`  — CONFIRMED

- 12.0：`fields.Float(digits=dp.get_precision("Product Price"))`（需 import decimal_precision）。
- 13.0：`fields.Float(digits="Product Price")`（直接字符串精度键）。
- 扫描 id：`dp-get-precision`（正则 `dp\.get_precision`）。

## 2. `track_visibility` → `tracking`  — CONFIRMED（常见误归 15→16，以 13.0 为准）

- 12.0：`fields.Char(track_visibility="onchange")`。
- 13.0：`fields.Char(tracking=True)`（或 `tracking=10` 指定优先级）。
- 扫描 id：`track-visibility`（正则 `track_visibility=`）。

## 3. `oldname` 字段属性移除  — CONFIRMED

- 12.0：`amount = fields.Monetary(oldname="price_amount")`（改名过渡）。
- 13.0：`oldname` 不再支持 → 用 openupgradelib 的 `rename_fields` 写 `migrations/13.0/` 脚本。
- 扫描 id：`oldname`（正则 `\boldname\s*=`）。

## 4. `stock.quant` `qty` → `quantity`  — CONFIRMED

- 12.0：`quant.qty`；13.0：`quant.quantity`。

## 5. `product.product` `name` 变为 related 字段  — CONFIRMED（源码核对）

- 13.0：`product.product.name` 是 `product.template.name` 的 related（store=True）。
- 不能给变体直接写 name，应改 `product_template_id.name`。

## 6. `Binary` 字段默认存附件  — CONFIRMED（确认 11→12 旧 [verify] 归属）

- 13.0 起 `Binary` 默认 `attachment=True`（存 `ir.attachment`）；需旧"入库列"行为则显式 `attachment=False`。

## 7. 清单（含可信度）

| 12.0 | 13.0 | 类别 | 可信度 |
|---|---|---|---|
| `dp.get_precision("X")` | `digits="X"` | 工具函数 | CONFIRMED |
| `track_visibility="onchange"` | `tracking=True` | 字段属性 | CONFIRMED |
| `oldname="x"` | 移除（rename_fields） | 字段属性 | CONFIRMED |
| `stock.quant.qty` | `stock.quant.quantity` | 字段改名 | CONFIRMED |
| `product.product.name`（可写） | related（写模板） | 字段语义 | CONFIRMED |
| `Binary` 默认 `attachment=True` | 存附件 | 字段存储 | CONFIRMED |

## 红线

- `payment.acquirer`→`payment.provider`、`coupon`→`loyalty`、`stock.production.lot`→`stock.lot` → 15→16；
- `ir_translation`→JSONB → 15→16；`t-raw` 移除 → 14→15。
