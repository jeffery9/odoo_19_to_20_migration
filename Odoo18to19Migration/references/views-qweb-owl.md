# Views / QWeb / Owl (18 → 19)

## 1. Owl 2.x → Owl 3.x (frontend — highest effort)

Odoo 19 upgrades the client framework to **Owl 3**. This is the largest manual work
area for 18→19. Key breaking changes for custom JS widgets:

| Odoo 18 (Owl 2) | Odoo 19 (Owl 3) | Note |
|---|---|---|
| constructor-based init | **`setup()` pattern is mandatory** | constructor init raises errors in 19 |
| older `useState` state patterns | new reactivity model (`useState` semantics refined) | review state usage |
| some lifecycle hooks | hooks renamed/consolidated | review `onWillStart`/`onMounted` usage |
| dev-only prop validation | **prop validation enforced in production** | bad props now crash in prod |
| `useEffect` (old cleanup) | `useEffect` cleanup refined | ensure cleanups run |

- Rule: rewrite custom components to use `setup()` exclusively; audit every custom
  JS widget in `static/src/**/*.js`.
- QWeb template syntax has **minor** compatibility changes for Owl 3 — re-test
  custom templates, but most carry over.

## 2. QWeb template changes — CONFIRMED

| Odoo 18 | Odoo 19 | Source |
|---|---|---|
| `t-esc` | `t-out` | Cybrosys ("replace t-esc with t-out") |
| `t-set` block consumed by a `t-call`/`t-snippet-call` | `t-set` must be **hoisted before** the call | LineScripts; corresponds to codemod `19.1-00-t-call` (19.x Online, not pure 18→19 CE) |
| Font Awesome `fa-` icon names (website snippets) | Material Symbols / `oi` + `data-icon` | (see 19→20 reference for detail — same direction) |

> `t-esc`→`t-out` is flagged by multiple 18→19 guides; treat as a required cleanup
> for 19 compatibility even where it still renders.

## 3. Kanban card template name: `kanban-box` → `card` — CONFIRMED

Community 18→19 tables (SDLC Corp, ERP Consulting 24) report the kanban card template
name changed `t-name="kanban-box"` → `t-name="card"`. This is the Owl-3 kanban
rewrite. Rename custom kanban cards accordingly (verify against the 19.0 `web` kanban
templates).

## 4. View architecture & validation (mostly backward-compatible, stricter checks)

XML view syntax is **largely backward-compatible** in 18→19, but two hard removals
apply (see §5 `<tree>`→`<list>` and §6 `target='inline'`). The following stricter
validations are reported by community write-ups; confirm against a 19.0 install
(`[verify]`):

- View `<record>` should declare `model` — source review of `ir_ui_view.py` shows `model`
  is **not** `required`, so this is **unconfirmed**. `[verify]`
- XPath expressions validated more strictly (malformed xpath raises). `[verify]`
- `groups=` on view fields validated against existing group XML-IDs at install. `[verify]`
- `oe_button_box` without a `name` attribute is no longer supported — **not found** in
  19.0 `ir_ui_view.py`; likely **not** a real 18→19 change. `[verify]`

## 5. `tree` tag → `list` — **CONFIRMED (removed in 19.0)**

In 19.0 the view `type` selection contains only `list` (no `tree`); a `<tree>` root tag
raises `Invalid view type: 'tree' ... Allowed types are: ...`. Migrate `<tree>` → `<list>`.
This is a **real 18→19 breaking change** (the legacy `tree→list` codemod is older, but
the hard rejection is what bites at 19.0).

## 6. Window actions: `target='inline'` removed — **CONFIRMED**

`ir.actions.act_window.target` in 19.0 accepts only `current`, `new`, `fullscreen`,
`main` (no `inline`). Source-verified via `odoo/addons/base/models/ir_actions.py`.
Scan XML/Python action definitions for `target='inline'` and repoint to one of the
valid values.

## 7. Module dependency: `web_editor` → `html_editor` / `html_builder` — CONFIRMED

`web_editor` is **gone** in 19 — split into `html_editor` and `html_builder`
(LineScripts, DeployMonkey, SDLC, ERP24). Any manifest `'depends': ['web_editor']`
fails to install. Repoint:

| Odoo 18 depends | Odoo 19 depends |
|---|---|
| `web_editor` | `html_editor` (rich text) and/or `html_builder` (site builder) |

(See `modules-mapping.md` §1 for the full module rename list. Note: the *website
builder* split is `html_builder`; rich-text fields use `html_editor`.)
