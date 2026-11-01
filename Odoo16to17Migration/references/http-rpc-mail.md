# 16→17 HTTP / RPC / Mail / Binary mapping

## message_post body format — CONFIRMED (OCA 17 + odoohub)

`mail.thread.message_post` `body` now defaults to **text / Markdown**. HTML
must be flagged with `body_is_html=True` (and wrapped in `markupsafe.Markup`).

```python
# 16 (body treated as HTML)
self.message_post(body="<p>Invoice %s confirmed</p>" % inv.name)
# 17
from markupsafe import Markup
self.message_post(body=Markup("<p>Invoice %s confirmed</p>" % escape(inv.name)),
                  body_is_html=True)
# or Markdown (default)
self.message_post(body=f"Invoice {inv.name} confirmed")
```

Note: `mail/models/mail_thread.py` lives at a different path in 17.0 than in
18.0 (verified 18-style path 404s in 17.0), but the `body_is_html` behavior
change is confirmed by OCA 17 guide + odoohub version diff.

## Werkzeug 2.0.2 floor — [verify]

17.0 requirements pin `Werkzeug==2.0.2` (py3.10) / `2.2.2` (3.11) / `3.0.1`
(3.12). If your 16 code used Werkzeug 1.x-only APIs (`werkzeug.contrib`, old
`Response`/`BaseRequest` behaviors, `werkzeug.urls` relocation), controllers
may break. `werkzeug.contrib` removal → ImportError. Rewrite against Werkzeug 2.x.
Version attribution (whether 16 already used Werkzeug 2) is disputed → [verify].

## Binary / Excel / PDF / time — stable

`fields.Binary`, `xlsxwriter`, `PyPDF2` (still in 17.0 requirements),
`zoneinfo` (recommended over `pytz` since 3.9) — no 16→17 break.

## Mail composer — [verify]

`mail.compose.message` wizard still present in 17.0; Odoo steers toward
`message_post` + dialog. If you subclass the composer, verify its structure on
your 17.0 instance before relying on internals.
