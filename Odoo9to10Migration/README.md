# Odoo9to10Migration

Odoo **9.0 → 10.0** 自定义模块迁移技能（CE 与 EE）。配套烹饪书：`Odoo_Migration_Cookbook_9_to_10.md`。

## 这是什么

把 9.0 自定义插件（单模块或整个 addons 树）升级到 10.0，确保不留任何 9-only API。
**10.0 及更早没有 `upgrade_code` codemod 引擎**（该引擎 18.0 才出现），所以所有代码改动都是**手工映射**；
数据库级变更由 **OpenUpgrade** / 官方升级服务处理。本技能只覆盖自定义模块的**代码级**映射。

## 头号断裂（9→10）

1. **包改名 `openerp` → `odoo`** —— 10.0 无 `openerp` 包；`from openerp import ...` / `import openerp` 残留即 `ImportError`（本卷主线）。
2. **清单文件改名 `__openerp__.py` → `__manifest__.py`** —— 9.0 的 `__openerp__.py` 在 10.0 不被识别。
3. **字段索引 `select = True` → `index = True`** —— 旧写法不再建索引。
4. **视图 / XML 选择器收紧** —— 字符串 `position`/文本 `xpath` 选择器改属性选择器；`<openerp>`/`<data>` 根包装改 `<odoo>`。
5. **安全组微调** —— `base.group_configuration` → `base.group_system`。
6. **`copy` 方法装饰器** —— `@api.one` → `@api.multi`（勿与 `@api.onchange` 混用）。
7. **安全组模块化** —— `base.group_sale_*` → `sales_team.*`、`base.group_hr_*` → `hr.*`、`menu_hr_configuration` → `menu_human_resources_configuration`、`website.salesteam_website_sales` → `sales_team.salesteam_website_sales`、`product.prod_config_main` → `sale.prod_config_main`。

## 目录

```
Odoo9to10Migration/
├── SKILL.md              # 技能 frontmatter + 工作流 + 硬规则
├── README.md             # 本文件
├── references/           # 6 份参考表
│   ├── orm-api.md        # 包改名 / 清单改名 / select→index / copy 装饰器
│   ├── views-qweb.md     # 视图 / XML 选择器清理 / <openerp>/<data>→<odoo>
│   ├── models-mapping.md # 模块 / 模型 / 字段映射（9→10 无大规模重命名）
│   ├── security.md       # res.groups 微调 + 安全组模块化（group-move）
│   ├── http-rpc-mail.md  # 控制器 / 邮件 / 二进制（基本不变）
│   └── upgrade-code.md   # 10.0 无 upgrade_code codemod
└── scripts/
    ├── scan_addon.py     # 9-only API 扫描器（全部 manual，exit 1 = 有发现）
    ├── check_markdown.py # Markdown lint（0 issue 门禁）
    └── normalize_markdown.py
```

## 用法

```bash
# 1) 扫描
python3 scripts/scan_addon.py /path/to/addons
# 2) 按 references/ 手工映射
# 3) 质量门禁
python3 ../work/9to10/check_cookbook_consistency.py   # Cookbook↔references 零漂移
python3 scripts/check_markdown.py ../Odoo_Migration_Cookbook_9_to_10.md SKILL.md README.md references/*.md
```

## 质量门禁

- Cookbook（单卷）与 `references/` 核心 token 双向零漂移（`work/9to10/check_cookbook_consistency.py`）。
- `check_markdown.py` ⇒ 0 issue。
- 扫描器干净 addon ⇒ exit 0；SKILL.md frontmatter 可解析为 YAML。
