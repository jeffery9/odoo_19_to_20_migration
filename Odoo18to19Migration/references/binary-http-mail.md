# Binary / HTTP / Mail / Reports (18 → 19)

## 1. HTTP controllers: `type='json'` → `type='jsonrpc'`

Introduced in 18.1 (#183636): the JSON controller `type` was renamed `json` →
`jsonrpc`. In 19 the **old alias still works but logs a `DeprecationWarning` at
import**, and the alias is scheduled for removal in a later version. Codemod
`18.1-02-route-jsonrpc` performs the rewrite.

```python
# 18
@app.route('/my/endpoint', type='json', auth='user')
def my_endpoint(self): ...

# 19
@app.route('/my/endpoint', type='jsonrpc', auth='user')
def my_endpoint(self): ...
```

- The wire protocol is **identical**, so **no JavaScript change is required** — only
  the Python `type=` value (mindscript upgrade-auditor: "the wire protocol is
  identical, so no JavaScript has to change").
- `@http.route(type='json')` is the only form flagged; `type='http'` is unaffected.
  No 18→19 change to external `JSON-2` (`/json/2/...`) or XML-RPC endpoints.

## 2. Authentication API: `authenticate()` — CONFIRMED

| Odoo 18 | Odoo 19 |
|---|---|
| `authenticate(request.session.db, creds)` | `authenticate(request.env, creds)` |

(Cybrosys / ERP Consulting 24.) Affects custom auth/controller code; normal RPC
clients are unaffected.

## 3. External RPC deprecation (awareness, not a break)

Per the Odoo external RPC API reference: as of **19.0** the XML-RPC and JSON-RPC
endpoints (`/xmlrpc`, `/xmlrpc/2`, `/jsonrpc`) are **deprecated** (db service removed
in 20.0; common/object scheduled for 22.0). For 18→19 this is a *warning only* —
integrations keep working. Plan external-integration rechecks for the 19→20 step.

## 4. Binary / Excel / PDF / time

No 18→19 breaking changes reported. `fields.Binary`, `pytz`/`zoneinfo` usage,
Excel/PDF report rendering, and server-side time helpers are stable across the jump.
(The `pytz`→`zoneinfo` guidance belongs to 19→20.) If a module renders reports via
`web_editor`, see the `web_editor` → `html_editor`/`html_builder` rename in
`modules-mapping.md` (it changes report templates' editor dependency).

## 5. Mail & server actions

Mail-thread and `mail.thread` APIs are stable in 18→19; the `mail.thread.cc` removal
is a **19→20** change, not this step. Server actions and automated actions keep their
signatures. (`mail_post` server-action `state` rework is 19→20.)

## 6. SQL reports

Reports registering controllers under `type='json'` move to `type='jsonrpc'` (§1).
SQL composition should already use the `SQL(...)` wrapper object (introduced 17.0,
#134677) — unchanged in 18→19.
