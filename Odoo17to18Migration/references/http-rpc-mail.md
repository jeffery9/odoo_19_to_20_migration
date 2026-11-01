# HTTP, RPC, mail & binary (17 → 18)

## 1. Controller `type='json'` → `type='jsonrpc'` — CONFIRMED (18.1 #183636)

> First appears in **18.1 (Online)**; included here per the 17→18 scope (new relative to 17).

```python
@app.route('/my/endpoint', type='json', auth='user')      # 17 / 18.0
def my_endpoint(self): ...
@app.route('/my/endpoint', type='jsonrpc', auth='user')   # 18.1+
def my_endpoint(self): ...
```

- **Wire protocol is identical** — no JavaScript changes needed, only the Python `type=` value.
- Only `@http.route(type='json')` is affected; `type='http'` is untouched.
- In 18.1 the old alias still works but logs `DeprecationWarning`.
- **No codemod for 17→18**: the `18.1-02-route-jsonrpc` script ships in the **19.0** tree
  (used by the 18→19 step). For 17→18, edit `type='json'` → `type='jsonrpc'` by hand.

## 2. Mail & server actions — stable

`mail.thread`, message/activity APIs are unchanged in 17→18. `mail.thread.cc` removal and
`mail_post` server-action rework are **19→20** changes — not this step.

## 3. Binary / Excel / PDF / time — stable

`fields.Binary`, `xlsxwriter`/`io.BytesIO` reports, PyTZ/`zoneinfo`, server-side time helpers
are stable across 17→18. No breaking change.

## 4. Real-time: Longpolling → WebSocket — informational

Bus / live-chat real-time push moved to WebSocket channels (infrastructure layer). Custom code
generally needs no change, but deployment must enable the WebSocket channel.
