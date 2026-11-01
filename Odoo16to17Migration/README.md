# Odoo 16 → 17 Migration Skill

This is the **16→17** member of the multi-version migration workspace
(see the root README.md). The 17→18 member lives in
`../Odoo17to18Migration/` and the 18→19 member in `../Odoo18to19Migration/`.

## What changed between 16.0 and 17.0

16→17 is a **view-declaration-syntax + Python-runtime-base** double upgrade,
and uniquely has **zero `upgrade_code` codemods** (the codemod tooling ships in
18.0). Headline breaks:

- **Views**: `attrs`/`states` attributes **hard-rejected** (ValidationError
  "Since 17.0...") → inline `invisible`/`readonly`/`required` expressions;
  list-field `invisible="1"` → `column_invisible="1"`; `res.config.settings`
  simplified (`<setting>`, drop `o_setting_*_pane`); `active_id`/`active_model`
  context rewritten.
- **Python/ORM**: `name_get` deprecated (→ `_compute_display_name`); hook
  signatures `(cr, registry)` → `env`; `get_resource_path` removed →
  `file_path`; `message_post` body defaults to text/Markdown (HTML needs
  `body_is_html=True`); Python 3.10+ floor.
- **NOT changed in 16→17** (red lines): `tree`→`list` (17→18), name_get
  *removal* (17→18), SCSS removal (post-17.0), Bootstrap5/jQuery (disputed,
  [verify]), `res.groups`/`ir.model.access.csv` (19→20).

See `SKILL.md` for the full workflow and hard rules, and the companion
`Odoo_Migration_Cookbook_16_to_17.md` (same directory as the root README) for
the human-readable, source-verified narrative.

## Layout

```
Odoo16to17Migration/
├── SKILL.md              # frontmatter + workflow + hard rules
├── README.md             # this file
├── references/           # source-verified mapping tables
│   ├── views-qweb.md      # attrs/states, column_invisible, settings, [verify] BS5/jQuery
│   ├── orm-api.md         # name_get deprecation, hooks env, get_resource_path->file_path
│   ├── http-rpc-mail.md   # message_post body, [verify] Werkzeug 2
│   ├── security.md        # 16→17 unchanged (res.groups / access.csv red lines)
│   ├── modules-mapping.md # framework-level rename table + symptom index
│   └── upgrade-code.md    # 17.0 has NO codemod; migrations/17.0/ pattern
└── scripts/
    ├── scan_addon.py      # 16→17 tailored scanner (stdlib only)
    ├── check_markdown.py  # markdown lint gate (must exit 0)
    └── normalize_markdown.py
```

## Quick start

```bash
# 1. scan
python3 Odoo16to17Migration/scripts/scan_addon.py /path/to/addons --addon my_module
# 2. apply manual mappings from references/* (no codemod exists for 16->17)
# 3. write data migrations in my_module/migrations/17.0/
# 4. validate
odoo-bin -u my_module --test-tags /my_module
# 5. clear every DeprecationWarning with --dev=all
```
