# Odoo10to11Migration

Odoo **10.0 → 11.0** 自定义模块迁移技能（CE 与 EE）。配套烹饪书：`Odoo_Migration_Cookbook_10_to_11.md`。

## 这是什么

把 10.0 自定义插件（单模块或整个 addons 树）升级到 11.0，确保不留任何 10-only API。
**11.0 没有 `upgrade_code` codemod 引擎**（该引擎 18.0 才出现），所以所有代码改动都是**手工映射**；
数据库级变更由 **OpenUpgrade** / 官方升级服务处理。本技能只覆盖自定义模块的**代码级**映射。

## 头号断裂（10→11）

1. **Python 3 强制** —— 11.0 仅支持 Python ≥3.5；10.0 仍双兼容。必须改写 `print` 语句、
   `iteritems`/`has_key`/`xrange`/`unicode`/`basestring`/`StringIO`/`urllib2`/`except E, e`、整除。
   `openerp.tools.pycompat` 垫片在 11.0 移除。
2. **包命名空间 `openerp` 别名移除** —— `from openerp`/`import openerp` 残留即 `ImportError`
   （主改名在 9→10，11.0 清理别名）。
3. **工作流（Workflow）完全移除** —— `workflow` XML、`type="workflow"` 按钮、`signal_workflow()` 失效。
4. **QWeb 报表 API 重写** —— `render_html`→`get_report_values`、`get_action`→`report_action`、`get_html`→`render_qweb_html`。
5. **`ir.cron`：`model`→`model_id`**（ref 到 `ir.model`）。
6. **模块改名/合并** —— `sale`→`sale_management`、`account_accountant`→`account_invoicing`；
   `account_tax_cash_basis`→`account`、`report`→`web`。
7. **安全组微调** —— `base.group_configuration`→`base.group_system`（并补齐 9→10 的 group 模块化）。

## 目录

```
Odoo10to11Migration/
├── SKILL.md              # 技能 frontmatter + 工作流 + 硬规则
├── README.md             # 本文件
├── references/           # 6 份参考表
│   ├── orm-api.md        # Python3 语法 / 包命名空间 / Workflow / 报表 API / ir.cron
│   ├── views-qweb.md     # 视图 / QWeb / 前端
│   ├── models-mapping.md # 模块重命名 / 合并 / 模型字段映射
│   ├── security.md       # res.groups 微调 + 9→10 遗留 group 模块化
│   ├── http-rpc-mail.md  # 控制器 / 邮件 / 二进制（基本不变）
│   └── upgrade-code.md   # 11.0 无 upgrade_code codemod
└── scripts/
    ├── scan_addon.py     # 10-only API 扫描器（全部 manual，exit 1 = 有发现）
    ├── check_markdown.py # Markdown lint（0 issue 门禁）
    └── normalize_markdown.py
```

## 用法

```bash
# 1) 扫描
python3 scripts/scan_addon.py /path/to/addons
# 2) 按 references/ 手工映射
# 3) 质量门禁
python3 ../work/10to11/check_cookbook_consistency.py   # Cookbook↔references 零漂移
python3 scripts/check_markdown.py ../Odoo_Migration_Cookbook_10_to_11.md SKILL.md README.md references/*.md
```

## 质量门禁

- Cookbook（单卷）与 `references/` 核心 token 双向零漂移（`work/10to11/check_cookbook_consistency.py`）。
- `check_markdown.py` ⇒ 0 issue。
- 扫描器干净 addon ⇒ exit 0；SKILL.md frontmatter 可解析为 YAML。
