# Reference: upgrade_code codemods (15 → 16)

## Reality: 16.0 has ZERO codemods  [CONFIRMED — source]

`odoo/upgrade_code/` **does not exist in the 16.0 branch** (GitHub directory listing returns 404;
the codemod engine first appears in 18.0, where it carries the 17.5 `tree-to-list` script).
Therefore:

- There is **no `odoo-bin upgrade_code --from 15.0`** that rewrites 15→16 code.
- All code-level changes (payment/coupon renames, model renames, `track_visibility`→`tracking`,
  `api.multi` removal, `ir_translation` rewrite) are **manual** — guided by the other reference
  files and the bundled scanner `scripts/scan_addon.py`.
- The **database-level** renames (model/field/module names, `ir_translation`→JSONB, module merges,
  new constraints) are applied by **OpenUpgrade** (community) or the **official upgrade service**
  (Enterprise) 16.0 migration scripts — not by `upgrade_code`.

## Workflow

1. Run OpenUpgrade / official DB migration on a copy of the v15 database.
2. Scan custom addons: `python3 scripts/scan_addon.py /path/to/addons` (exit 1 = findings).
3. Apply manual mappings from `references/payment-loyalty.md`, `references/models-mapping.md`,
   `references/orm-api.md`.
4. Write custom data migrations under each module's `migrations/16.0/` (`pre-`/`post-`/`end-`).
5. Validate: re-run scanner (expect 0), `odoo-bin -u <module> --test-tags /<module>`,
   start with `--dev=all` and clear every `DeprecationWarning` / `ImportError` / `Model not available`.
