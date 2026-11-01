# 16→17 Views / QWeb / Frontend mapping

Source-verified against Odoo 17.0. Each row is a hard or behavior break that
landed in 17.0. Red line: do NOT apply tree→list here (that is 17→18).

## attrs / states removed (HARD break) — CONFIRMED (ir_ui_view.py 17.0)

`ir_ui_view._check_xml` raises `ValidationError: "Since 17.0, the 'attrs' and
'states' attributes are no longer used."` for any combined arch containing
`@attrs` or `@states`. Rewrite as inline Python expressions.

| 16 | 17 |
|---|---|
| `attrs="{'invisible': [('country_id','=',False)]}"` | `invisible="country_id == False"` |
| `attrs="{'readonly': [('state','=','done')]}"` | `readonly="state == 'done'"` |
| `attrs="{'required': [('type','=','contact')]}"` | `required="type == 'contact'"` |
| `states="draft,open"` (view or py field) | delete; use `invisible="state not in ('draft','open')"` etc. |

Expr is a boolean Python expression; multiple conditions via `and`/`or`/`not`/`in`.

## column_invisible (list view) — CONFIRMED (OCA 17)

`invisible="1"` on a field inside a `tree` (list) view now SHOWS the column
(empty). Use `column_invisible="1"` to hide the whole column.

```xml
<tree><field name="x" column_invisible="1"/></tree>
```

NOTE: `<tree>` itself is STILL valid in 17.0 (type selection contains
`('tree','Tree')`). Do NOT rename to `<list>` here — that is 17→18.

## res.config.settings simplified — CONFIRMED (PR #106425)

- Remove `o_setting_right_pane` / `o_setting_left_pane` divs.
- Replace `app_setting_block` with `<block>`.
- Wrap fields in `<setting title=".." help="..">`.
- Put title in `<block title="..">` / `<app title="..">`.

## active_id / active_ids / active_model in context — CONFIRMED (PR daf05d48)

- `active_id` → `id`
- `active_model` → hardcoded model name (e.g. `'res.partner'`)
- `active_ids` → no direct replacement; rewrite per intent (OCA calls it a weird case)

## t-attf- (frontend) — [verify]

`t-attf-` deprecated since Owl 2 (16.0). Prefer `t-att="f'...'"`. 17→18 cookbook
attributes t-esc→t-out to 19.0; do not conflate. Flag for cleanup, not a hard break.

## Bootstrap 5 / jQuery — [verify] (version scope disputed)

Official 17.0 release notes do NOT mention Bootstrap/jQuery/SCSS. Sources conflict:
some attribute BS4→5 + jQuery removal to 16→17, others say jQuery still available
in 17 and Bootstrap 5.1.3 is 18/19. **Verify against your 17.0 `web.assets_frontend`
bundle before acting.** If confirmed, apply standard BS4→5 class map
(`ml-*`→`ms-*`, `mr-*`→`me-*`, `text-left`→`text-start`, `float-left`→`float-start`,
`form-group`→`mb-3`, `custom-select`→`form-select`, `close`→`btn-close`,
`badge-*`→`bg-*`, `font-weight-bold`→`fw-bold`, `sr-only`→`visually-hidden`,
`no-gutters`→`g-0`; data attrs `data-toggle`→`data-bs-toggle`,
`data-dismiss`→`data-bs-dismiss`). Do NOT blindly rewrite SCSS to CSS in 17.0
(libsass still in requirements.txt — SCSS still compiles; removal is post-17.0).
