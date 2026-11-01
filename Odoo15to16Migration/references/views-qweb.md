# Reference: Views & QWeb (15 → 16)

Scope: **15.0 → 16.0 only.** Unlike 16→17 (attrs/states hard-rejected) the **view XML syntax is
almost unchanged in 15→16**.

## What is UNCHANGED in 16 (verified in 16.0 source)

- `attrs="{'invisible':[...]}"` / `attrs="{'readonly':[...]}"` / `attrs="{'required':[...]}"` —
  **still processed** (ir_ui_view.py L82-96 converts them to modifiers). Do NOT rewrite in 15→16;
  that is the 16→17 skill's job.
- `states="draft,open"` — **still accepted** (same L82-96). Do NOT rewrite in 15→16.
- `<tree>` view type — **still a valid type** (ir_ui_view.py L237 `('tree','Tree')`). Do NOT rename
  to `<list>` in 15→16 (that is 17→18).
- list-column `invisible="1"` → `column_invisible="1"` belongs to **16→17 (17.0)**, not 15→16.

## `[verify]` `t-raw` removed

`t-raw` removed in 16.0 (deprecated since 14.0). Replace with `t-esc` (or `t-out` in 19.0).
`[verify]`: could not source-verify 16.0 `odoo/tools/qweb.py` (path 404 in 16.0 — directory
restructured); treat as community-consensus.

## `[verify]` `fields.Html` granular sanitize

16.0 adds `sanitize_tags` / `sanitize_attributes` / `sanitize_style` / `sanitize_formatted`
alongside `sanitize=True/False`. If a custom `html` field relies on raw HTML, set
`sanitize=False` or the granular flags. `[verify]`: not source-verified.

## Owl 2 — no version switch

15 and 16 are both **Owl 2** (Owl 2 introduced in 15.0). No component rewrite needed for 15→16.
Legacy widget registry still works but is deprecated; service injection replaces `require()`.
`[verify]`: Owl 2 legacy-widget cleanup details — confirm against 16.0 frontend (not a hard break).

## Red line

Do NOT perform attrs/states→inline-expr rewrites, tree→list, or column_invisible here. Those are
16→17 (see that skill's views-qweb.md).
