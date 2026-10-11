# Binary, Excel, PDF, time · HTTP & mail (19 → 20)

## Binary / Excel / PDF / time

| Odoo 19 | Odoo 20 |
|---|---|
| `xlwt` | `xlsxwriter`; write into `io.BytesIO`, `{'in_memory': True}`, assign with `BinaryBytes` |
| `xlrd.open_workbook` for `.xlsx` | `openpyxl` for PK/OfficeOpenXML `.xlsx`; `xlrd` only for OLE `.xls` |
| `import PyPDF2` | `from odoo.tools.pdf import PdfFileWriter, PdfFileReader` |
| `odoo.tools.content_disposition` / old http path | `odoo.http.stream` |
| `_render_qweb_pdf(template_xmlid)` | `_render_qweb_pdf(action_xmlid)` (report **action** xmlid) |
| `request.env` inside report parsers | use `env`; `request.env` can raise `RuntimeError: request not bound` |
| binary field values bytes/base64 | `BinaryValue` objects (optional `.filename`); write with `BinaryBytes` |
| `from odoo.tools.binary import BinaryValue` (private in 19) | `from odoo.tools import BinaryValue, BinaryBytes` (public in 20) |
| `resource.calendar.leaves.time_type` | `count_as` (e.g. `count_as='absence'`) |
| `resource.calendar.tz`, attendance `name`/`day_period` | removed |

## Configuration, HTTP, mail

| Odoo 19 | Odoo 20 |
|---|---|
| `@http.route(..., type='json')` (web-client routes) | `type='jsonrpc'` (codemod `18.1-02`). External JSON-2 `/json/2/<model>/<method>` unchanged |
| server action `state="mail_post"` + `template_id` (+`mail_post_autofollow`) | `mail_post_method` |
| EE server action AI fields | `use_in_ai`, `ai_tool_name` matching `[a-zA-Z0-9_]{1,64}` |
| settings xpath `group[@name='preferences']` | `//page[@name='preferences']//group[@name='other_preferences']` |
| employee settings xpath | insert after `employees_setting_container` |
| `mail.tracking.value` in core `mail` | install Community addon `mail_tracking`; model name unchanged there |
| `request.website` in model methods | `self.env.website` (from `context['website_id']`); `request` unbound in parsers/ORM contexts |

## SQL reports

- `Model._table_query` → `Model._table_sql` property returning an `SQL` object.
- `SQL` composable: unchanged class (`odoo/tools/sql.py`), now public via `odoo.tools`;
  `cr.execute(SQL(...))` must not receive `params`.
- `Query` builder: `from odoo.orm.query import Query` (19 reached it via `odoo.tools`).
