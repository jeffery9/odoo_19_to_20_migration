# Reference: Payment restructure & Coupon→Loyalty (15 → 16)

Scope: **15.0 → 16.0 only.** Do NOT flag 16→17 concerns here (attrs/states, tree→list,
name_get, get_resource_path) — those belong to the 16→17 skill.

## Payment: `payment.acquirer` → `payment.provider`  [CONFIRMED]

Source: oejia《Odoo 16 关键变化》+ OCU 15→16 diff + GitHub docs PR #1981.

The payment provider model is renamed and several fields/methods follow. This is the
single most common blocker for custom modules on 15→16.

| 15.0 | 16.0 | note |
|---|---|---|
| `payment.acquirer` | `payment.provider` | model rename |
| `acquirer_id` | `provider_id` | field (transaction / token / business docs) |
| `acquirer_reference` | `provider_reference` | transaction field |
| `acquirer_ref` | `provider_ref` | token field |
| `payment.acquirer.provider` (field holding e.g. `'stripe'`) | `code` | the old `provider` field is renamed `code` |
| `_handle_feedback_data` | `_handle_notification_data` | connector method |
| `_process_feedback_data` | `_process_notification_data` | connector method |
| xmlid `payment.payment_acquirer_*` | `payment.payment_provider_*` | external id rename |

Fix checklist (code side — DB side handled by OpenUpgrade):

- `env['payment.acquirer']` → `env['payment.provider']`; `env.ref('payment.payment_acquirer_...')` → `...payment_provider_...`.
- domains / server actions / reports: `acquirer_id` → `provider_id`, `acquirer_reference` → `provider_reference`.
- custom connectors: `_inherit` `payment.acquirer` → `payment.provider`; rename `_handle_feedback_data`.
- manifest `depends`: payment fields/views partly move to auto-installed `account_payment` (23-module merge); update references to old payment locations.

`[EE-verify]` Enterprise payment connectors (`payment_*` EE modules) renames — verify against EE 16.0 tree.

## Coupon → Loyalty  [CONFIRMED]

Source: OCU 15→16 diff (coupon engine rebuilt as loyalty, gift cards absorbed).

| 15.0 | 16.0 |
|---|---|
| `coupon.coupon` | `loyalty.card` |
| `coupon.program` | `loyalty.program` |
| `coupon.reward` | `loyalty.reward` |
| `coupon.rule` | `loyalty.rule` |
| `coupon` / `sale_coupon` / `sale_coupon_delivery` / `website_sale_coupon` / `website_sale_coupon_delivery` / `pos_sale_gift_card` / `pos_coupon` / `pos_gift_card` | `loyalty` / `sale_loyalty` / `sale_loyalty_delivery` / `website_sale_loyalty` / `website_sale_loyalty_delivery` / `pos_sale_loyalty` / `pos_loyalty` |

Loyalty family field renames (OCU): `promo_applicability`→`applies_on`, `maximum_use_number`→`max_usage`,
`discount_percentage`→`discount`, `discount_type`→`discount_mode`.

Fix: `_inherit`/`_name` `coupon.*` → `loyalty.*`; manifest `depends` `coupon*` → `loyalty*`;
server actions / reports / domains referencing `coupon.program` etc → `loyalty.program`.

`[EE-verify]` EE coupon/gift-card extensions — verify against EE 16.0 tree.

## Red line

Do NOT touch `payment.acquirer` renames during a 16→17 pass (they are already done in 16);
do NOT import `api.multi` (removed in 16 — see orm-api.md).
