# 14→15 ORM / 模型 API / 测试映射表（源码核对版）

> 来源：Odoo CE 14.0 / 15.0 源码树复核（`ir_model.py`、`odoo/tests/common.py`、`odoo/api.py`）。
> odoo/odoo 提交号仅作查证入口，结论以源码为准。
> 作用域：仅 14→15。

## 1. `ir.model.data` 查询方法私有化  — CONFIRMED

**先纠正一个错误前提**：15.0 **没有**「移除对 `ir.model*` 的直接访问」。`ir.model` /
`ir.model.fields` 的 `search`、`_fields` 读取在 15.0 均正常，两个版本的 `ir_model.py` 差异在
`ir.model.data` 的方法签名与 `@api.ondelete` 改造上。

真正会打断代码的是 `ir.model.data` 的公共查询方法被私有化或删除：

| 14.0 | 15.0 | 状态 |
|---|---|---|
| `xmlid_lookup(xmlid)` | `_xmlid_lookup(xmlid)` | 改名 |
| `xmlid_to_res_id(xmlid, ...)` | `_xmlid_to_res_id(xmlid, ...)` | 改名 |
| `xmlid_to_res_model_res_id(xmlid, ...)` | `_xmlid_to_res_model_res_id(xmlid, ...)` | 改名 |
| `xmlid_to_object(xmlid, ...)` | — | 移除 |
| `_get_id(module, xml_id)` | — | **移除**（别把 `_get_id` 当修复手段，它本身没了） |
| `get_object_reference(module, xml_id)` | — | 移除 |
| `get_object(module, xml_id)` | — | 移除 |
| `check_object_reference(...)` | `check_object_reference(...)` | 保留 |

**改法**：

```python
# 首选（两版本都可用，行为未变）
record = self.env.ref('sale.my_record')

# 只要 id
res_id = self.env['ir.model.data']._xmlid_to_res_id('sale.my_record')

# 要 model + id
model, res_id = self.env['ir.model.data']._xmlid_to_res_model_res_id('sale.my_record')
```

- `_xmlid_lookup` 查不到时**抛 `ValueError`**（不返回 False），批量场景注意异常处理。
- 扫描 id：`xmlid-api`（正则 `xmlid_lookup|xmlid_to_res_id|xmlid_to_res_model_res_id|get_object_reference|get_object\(|_get_id\(`）。
- 注：与 13→14 的 `ir.actions.*` 访问收紧是**不同对象、不同版本对**。

## 2. 测试基类：`SavepointCase` 被合并  — CONFIRMED

- 14.0：`class SavepointCase(SingleTransactionCase)`（整类一个事务 + savepoint）。
- 15.0：`class SavepointCase(TransactionCase)`，且 `__init_subclass__` 抛
  `DeprecationWarning`（"Deprecated class SavepointCase has been merged into TransactionCase"）。
- **不是移除**，但**语义变了**：每测试方法独立事务，不再有类级共享事务。
  依赖「类级 setup 数据 + 回滚」的测试会失败或变慢。
- 同类：`HttpSavepointCase` → `HttpCase`。
- 替代：直接用 `TransactionCase` / `HttpCase`。
- 扫描 id：`savepoint-case`（正则 `SavepointCase`）。

## 3. `Environment.manage()` 变成 no-op  — CONFIRMED

- 15.0 的实现只剩 `warnings.warn("Since Odoo 15.0, Environment.manage() is useless.")` + `yield`。
- 行为无差异，删掉即可（代码卫生）。
- 扫描 id：`env-manage`（正则 `Environment\.manage`）。

## 红线（勿套用更晚版本）

- `name_get` **移除** → 17→18；`attrs`/`states` 硬拒 → 16→17；`tree`→`list` → 17→18；
- `groups_id`→`group_ids` → 18→19；`ir.model.access.csv`→`security/ir.access.csv` → 19→20；
- 「15.0 移除 `ir.model*` 访问」**不成立**，见第 1 节。
