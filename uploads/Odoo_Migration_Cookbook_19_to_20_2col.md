# Odoo Migration Cookbook: Version 19 to Version 20

Community Edition and Enterprise Edition · First Edition · September 2026

Authors: Mustufa Rangwala, Sananaz Mansuri

Publisher: Probuse Consulting Service Pvt. Ltd.

Source: `Odoo_Migration_Cookbook_19_to_20.pdf`

说明：本文档将 PDF 内容转换为扁平 Markdown，移除重复页眉、页码和目录导航文字；正文按章节顺序排列。原文中的代码片段、映射关系和技术表项尽可能保留为纯文本或 Markdown 列表。

## 1. Security

CE + EE

Odoo 20 loads ir.access.csv . It does not load ir.model.access.csv plus XML

ir.rule records. XML <record model="ir.rule"> raises KeyError: 'ir.rule' .

Odoo 19

id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink

access_lock,lock,model_my_lock,base.group_user,1,1,1,0

Odoo 20 — security/ir.access.csv

id,name,model_id,group_id/id,operation,domain

access_my_lock,my.lock,my.lock,base.group_user,cru,

Column

Odoo 20

model_id

Technical model name ( sale.order ). Not module.model_x .

group_id/id

Group XML id. Empty = global rule.

operation

crud , cru , cr , … — not rc , and not perm_read columns

domain

Record-rule domain, or empty

Further 19 → 20 rules on this file:

model_id/id from 19 is not model_id . The 20 column needs the technical

name.

Domains [(1, '=', 1)] and [('1', '=', 1)] fail validation. Use an empty

domain.

A domain on a non-stored field raises Field has no SQL representation . Use a

stored field or a stored path.

Company domain ('company_id', 'in', company_ids + [False]) fails. Use:

['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]

Custom res.groups XML must be listed in the manifest before

ir.access.csv if the CSV references those groups.

## 2. ORM and Python

CE + EE unless marked otherwise.

Odoo 19

Odoo 20

_sql_constraints = [('name', 'sql', 'msg')]

`_name = models.Constraint(`

`self.fields_view_get(...)`

`self._get_view(...)`

`self.check_access_rights('read')`

`self.check_access('read')`

`self.check_access_rights('read',`

raise_exception=False)

`self.has_access('read') (b`

`self.user_has_groups('sales_team.group_sale_manager')`

`self.env.user.has_groups('`

`self._context`

`self.env.context`

`self.env.user.company_id`

`self.env.company`

ir.config_parameter.get_param / set_param

get_int / get_str / get_bo

set_str / set_bool / set_f

pytz

datetime.UTC and zoneinfo

window action toggle_active

action_archive / action_un

write archive=True

write active=False

mail.thread.cc

mail.thread

# 19

_sql_constraints = [

('code_uniq', 'unique(code, company_id)', 'Code must be unique per company.'),

]

# 20

`_code_uniq = models.Constraint(`

'unique(code, company_id)',

'Code must be unique per company.',

)

# 19

`self.check_access_rights('read')`

# 20

`self.check_access('read')`

`self.has_access('read')`

# 20 — selection_add requires ondelete

`state = fields.Selection(selection_add=[`

('extra', 'Extra'),

], ondelete={'extra': 'set default'})

`_name listed in _inherit requires that parent model to exist in the registry.`

CE a module that _name = 'helpdesk.sla' and also _inherit = 'helpdesk.sla'

fails unless EE helpdesk is installed. CE-only graphs use _name only. EE

graphs that load Enterprise Helpdesk keep _inherit .

mail.thread.cc is removed. A model that inherits rating.mixin already

inherits mail.thread . Listing both on 20 raises an MRO error.

# 20

`_inherit = ['portal.mixin', 'mail.activity.mixin', 'rating.mixin']`

Two Many2many fields on the same model to the same comodel, without

relation= , collide on 20. Set relation= on at least one.

A 20 compute must assign every record. A 20 compute must not return a

value dict. Stored and non-stored fields cannot share one compute method.

method=True on a computed field is invalid. tracking= on a related field

requires mail.thread . Related Selection must not re-declare selection /

default / tracking . placeholder= is XML-only.

A required SQL column without default= raises NOT NULL on create.

required=True on a new Many2one cannot add NOT NULL when the table

already has rows.

`self.env['some.model'] is a recordset. _inherit is on`

`self.env.registry['some.model'] .`

COPY, WRITE ORDER, AND TRANSLATIONS

A Char field named name now defaults to copy=mark_as_copy('name') .

Duplicating a record appends “(copy)” to that value. Override copy= when

the 19 behaviour must stay a plain copy.

`from odoo.tools.translate import mark_as_copy`

name = fields.Char(copy=mark_as_copy('name'))

code = fields.Char(copy=False)

create() and write() run field inverses in (field.write_sequence, field

definition order) . Custom inverses that assumed 19 order can break. Set

write_sequence= when two inverses must run in a fixed sequence.

`partner_id = fields.Many2one('res.partner', write_sequence=10)`

Reading a One2many or Many2many returns only records the user can

access. Code that counted or mapped the full relational cache of forbidden

ids will see a shorter recordset.

Module translations are stored in that module’s PO. 20 no longer dumps

them into base . Export and import translations per module.

WEBSITE ON THE ENVIRONMENT

CE + EE when website is installed. 19 model code often used request.website .

20 Environment exposes env.website from context['website_id'] . Prefer

`self.env.website in models. request is not bound in report parsers and`

several ORM contexts (Chapter 4).

# 20

website = self.env.website

## 3. Search and domains

CE + EE

Odoo 19

Odoo 20

`_name_search`

_rec_names_search and/or

_search_display_name

`from odoo.osv import expression /`

expression.AND / expression.OR

`from odoo.fields import Domain /`

Domain.AND / Domain.OR

`from odoo.fields import Domain, AND,`

FALSE_DOMAIN

`from odoo.fields import Domain only`

( Domain.FALSE )

`_name_search(..., args=...,`

name_get_uid=...)

(self, name, domain=None,

operator='ilike', limit=None,

order=None)

_read_group_stage_ids(self, stages,

domain, order)

_read_group_stage_ids(self, stages,

domain)

view modifier in 'x' / not in 'x'

== 'x' / != 'x' (tuple in ('a', 'b') is

valid)

# 20

`class AccountAnalyticAccount(models.Model):`

`_inherit = 'account.analytic.account'`

_rec_names_search = ('name', 'code', 'custom_number', 'partner_id')

`from odoo.fields import Domain`

`def _search_display_name(self, *args, **kwargs):`

`return Domain(super()._search_display_name(*args, **kwargs))`

odoo.tools.Query is not exported from odoo.tools . Import SQL from

odoo.tools .

### DOMAIN OPERATOR ACCESS

20 adds the domain operator access . It is valid on id and on Many2one

fields. The value is 'read' , 'write' , 'create' , or 'unlink' . Use it when a

domain must keep only records (or related records) the user may operate

on. It does not work on properties.

# 20 — current user can write the partner

Domain('partner_id', 'access', 'write')

# 20 — current user can read this record

Domain('id', 'access', 'read')

This operator is useful in ir.access.csv domains (Chapter 1) when the rule

must follow comodel rights.

## 4. Binary, Excel, PDF, and time

CE + EE

### BINARY

On the record, a Binary field is BinaryValue ( odoo.tools.binary ). .content is

already raw bytes. base64.decodebytes(self.datas) double-decodes or raises

Incorrect padding .

Direction

Odoo 20

Read

value.content or bytes(value)

Filename

value.filename — optional name on BinaryValue / BinaryBytes

Write

`from odoo.tools.binary import BinaryBytes — not raw bytes , not`

base64.b64encode(...)

Image write

image_apply_opt(pil_image, 'PNG') then BinaryBytes(...) .

image_to_base64 is removed

ir.attachment

field raw , not datas ; res_id is an integer

XML binary

type="bytes"

RPC / HTTP

binary payload is BinaryValue , not a bare base64 string

BinaryBytes(data, filename=name) keeps the original file name on the value.

RPC and HTTP that still send a raw base64 string without that wrapper fail

the 20 type check.

`from odoo.tools.binary import BinaryBytes`

`from odoo.tools.image import image_apply_opt`

`record.image_1920 = BinaryBytes(image_apply_opt(pil_image, 'PNG'))`

`record.datas = BinaryBytes(stream.getvalue(), filename=name)`

`<!-- 19 -->`

`<img t-attf-src="data:image/png;base64,#{doc.image_1920}"/>`

`<!-- 20 -->`

`<img t-att-src="image_data_uri(doc.image_1920) if doc.image_1920 else '/web/static`

### EXCEL

Odoo 19

Odoo 20

xlwt

xlsxwriter (in the 20 virtualenv). Write to io.BytesIO with

{'in_memory': True} . Assign with BinaryBytes

xlrd.open_workbook on

.xlsx

xlrd 2.0.1 cannot open Office Open XML. Use openpyxl for PK

.xlsx . Use xlrd only for OLE .xls

### PDF

Odoo 19

Odoo 20

`import PyPDF2`

`from odoo.tools.pdf import`

PdfFileWriter, PdfFileReader

content_disposition in odoo.tools /

odoo.http old path

odoo.http.stream

_render_qweb_pdf(template_xmlid)

_render_qweb_pdf(action_xmlid)

request.env in a report parser

env — request.env raises RuntimeError:

request not bound

### TIME

`from datetime import UTC`

`from zoneinfo import ZoneInfo`

`local_tz = ZoneInfo(self.env.user.tz or 'UTC') # ZoneInfo('utc') fails`

`if utc_dt.tzinfo is None:`

utc_dt = utc_dt.replace(tzinfo=UTC)

local_dt = utc_dt.astimezone(local_tz)

resource._attendance_intervals_batch(

start_dt, end_dt,

resources_per_tz=resource._get_resources_per_tz(),

)

Odoo 19

Odoo 20

time_type on leave / calendar leave

count_as='absence'

resource.calendar field tz

removed

calendar attendance name / day_period

removed

## 5. Configuration, HTTP, and mail

CE + EE unless marked EE.

Odoo 19

Odoo 20

@http.route(...,

type='json')

@http.route(..., type='jsonrpc')

ir.actions.server

mail_post_method

state="mail_post" + template_id + optional

mail_post_autofollow

EE server action use_in_ai

ai_tool_name matching [a-zA-Z0-9_]{1,64}

settings inherit

group[@name='preferences']

//page[@name='preferences']//group[@name='other_prefe

employee settings xpath

after employees_setting_container

A mail template that inherits an Enterprise model must use the defining

module’s model xmlid. Example EE: account_budget.model_budget_analytic .

Inherit does not create your_module.model_budget_analytic .

### MAIL.TRACKING.VALUE

CE + EE. 19 stores mail.tracking.value in core mail . 20 moves the model to

the Community addon mail_tracking (Discuss Tracking). Core mail still

generates tracking messages; it does not keep the stored tracking rows

unless mail_tracking is installed.

Odoo 19

Odoo 20

mail.tracking.value in mail

install mail_tracking ; then _name =

'mail.tracking.value'

search mail.tracking.value with

only mail

empty / missing model unless mail_tracking is in

the graph

Depend mail_tracking when custom code reads stored old/new values.

### EXTERNAL RPC

/json/2/<model>/<method> (JSON-2, type='json2' , bearer auth) is the

documented external API on 20. The same controller already exists on 19.

XML-RPC ( /xmlrpc/2 ) is still present on both versions. New integrations

should call JSON-2. Do not treat XML-RPC as removed in 20.

`POST /json/2/res.partner/search_read`

Controller routes that the web client calls stay type='jsonrpc' (table above).

That is not the same as JSON-2.

## 6. SQL reports

CE + EE

_TABLE_QUERY → _TABLE_SQL

19 SQL views set _auto = False and define _table_query (attribute or method).

20 removes _table_query . The lint on 20 is: overwrite _table_sql . Return

odoo.tools.SQL .

# 19

`_auto = False`

`def _table_query(self):`

`return self._query()`

# 20

`from odoo.tools import SQL`

`_auto = False`

`def _table_sql(self) -> SQL:`

`return SQL("(%s)", self._query())`

sale.report on 20 is the reference: _table_sql() builds a Query and returns

`query.subselect(...) . A module that only migrated _select() / _group_by() to`

SQL still fails if it leaves _table_query in place.

### _SELECT() AND _GROUP_BY()

_select() and _group_by() return odoo.tools.SQL . A Python string cannot be

concatenated onto that value. LiteralSQL has no .code .

`from odoo.tools import SQL`

`def _select(self):`

`return SQL("%s,\n t.custom_type", super()._select())`

Report

Odoo 20 hook

report.project.task.user

_select() / _group_by() → SQL

timesheets.analysis.report

_select() → SQL

sale.report

_select_dict + _groupby_list

purchase.report

_select_list(table) + _groupby_list(table)

account.move invoice report

_select_list

report.pos.order

wrap _select only

A field added on analytic.view_account_analytic_line_filter must also be added

on timesheets.analysis.report through _select() .

Translated name in SQL:

COALESCE(project_task_type.name->>'en_US', project_task_type.name::text)

## 7. Views

CE + EE unless marked otherwise.

### KANBAN

Odoo 19 inherit

Odoo 20 inherit

project.view_project_kanban

body

project.view_project_card

project.view_task_kanban footer

project.view_task_card

//t[@t-

name='card']//footer

kanban template name

t-name="card"

project.view_task_kanban uses card_id="%(project.view_task_card)d" .

### RIBBONS AND BUTTON ICONS

`<!-- 19 -->`

`<button icon="fa-check"/>`

`<widget name="web_ribbon" text="Archived" bg_color="bg-info"/>`

`<!-- 20 -->`

`<button icon="check"/>`

`<widget name="web_ribbon" title="Archived" bg_color="text-bg-info" invisible="acti`

Odoo 19

Odoo 20

web_ribbon

text=

title=

bg_color="bg-info" / bg-

primary

bg_color="text-bg-info" / text-bg-primary / text-

bg-success / text-bg-warning / text-bg-danger

button icon="fa-check"

icon="check" — names from web/icons.py

ICONS

Font Awesome / GTK icon

names on ViewButton

do not draw. iconFromString renders oi + data-icon=

Font Awesome on website

snippets

Material Symbols ligature (same names as ViewButton)

Legal ViewButton names include check , save , close , history , edit_square ,

task , group , book , description , stethoscope .

Owl 3 DropdownItem takes attrs= . href= and dataset= are invalid props.

### XPATH

View inherit cannot use attribute string or title as a selector. Use

hasclass(...) , name , id , or t-call .

Xpath cannot enter the body of a t-call . Inherit the called template, or

`xpath the t-call node.`

[@class='X'] is an exact match. Convert the inherit only when the 20 parent

`class string no longer equals X . Use hasclass('X') in that case.`

Invoice, sale, and purchase order line product_id / name are inside <column

name="product_and_description"> . /list/field[@name='product_id'] does not match.

Xpath a direct list child ( quantity , product_qty , analytic_distribution ,

account_id ).

Form

Odoo 19 xpath

Odoo 20

Analytic

account

//header

no header — insert <header> w

Timesheet

add button_box

div[@name='button_box'] alre

Calendar

event

button_box

no button_box — buttons in /

//sheet/widget[@name='web_r

Employee

oe_title

//h1 or //h1[hasclass('o_em

Job

user_id

after department_id ; form alre

CRM

//div[hasclass('oe_title')]/div

//div[hasclass('oe_title')]

Maintenance

request

archive_equipment_request / user_id

//header ; assignees user_ids

Invoice

totals

@class='oe_subtotal_footer'

//group[hasclass('oe_subtot

Equipment

19 location_id

owner_user_id

Partner list

complete_name

display_name

Partner

search

group[@name='group_by']

//search/group

User

preferences

group[@name='preferences']

//page[@name='preferences']

Product

product.product_variant_easy_edit_view

removed

Product

action

product.product_normal_action

product.product_variant_act

Sale config

menu

sale.prod_config_main

sale.menu_sale_config

Project form

group[@name='extra_settings']

//page[@name='settings']

Timesheet

kanban

footer

footer[@class='mt-0 pt-0']

div[@name='ts_footer']

eLearning

channel

//field[@name='active']

no active — xpath name

Form

Odoo 19 xpath

Odoo 20

Activity

popup

company_id

after summary

POS session

move_id

user_id

POS receipt

Owl ReceiptHeader / pos-receipt-

contact

point_of_sale.pos_order_rec

Sale form

show_update_fpos

fiscal_position_id

Sale portal

sidebar

navspy

div#sale_order_sidebar_butt

product.product_variant_action context active_id is defined only on a product

form. A custom ir.actions.act_window copied from that action must not keep

active_id if it opens from another model.

## 8. QWeb and reports

CE + EE

<act_window> and <report> are not in Odoo 20 import_xml.rng . Use

ir.actions.act_window and ir.actions.report records. ir.actions.report has no

report_file .

`<record id="action_print_doc" model="ir.actions.report">`

`<field name="name">Document</field>`

`<field name="model">sale.order</field>`

`<field name="report_type">qweb-pdf</field>`

`<field name="report_name">my_module.report_document</field>`

`<field name="binding_model_id" ref="sale.model_sale_order"/>`

`<field name="binding_type">report</field>`

</record>

Odoo 19

Odoo 20

t-esc

t-out

t-raw

t-out

t-field-options / t-esc-options

t-options

t-field

still valid

invoice o.type

o.move_type

BoM overview header BoM Cost

Total Cost

`from odoo.tools import`

html2plaintext

`from odoo.tools.mail import`

html2plaintext

web_editor Python

get_video_embed_code

package removed; embed is JS html_editor

An xpath that selected @t-esc must select @t-out .

### REPORT ENGINES

CE + EE. 20 splits PDF rendering into two Community modules that 19 did

not ship as addons:

Engine

Odoo 20 module

wkhtmltopdf

base_report_wkhtmltox

Paper Muncher (in-house)

base_report_paper_muncher

A custom report that assumed “one wkhtml pipeline inside web ” must

depend on the engine actually installed. Paper Muncher is the 20 in-house

renderer ( https://odoo.github.io/paper-muncher/ ).

EE If the report bound to hr.work.entry rows: those document records are

gone. Bind to hr.payslip and iterate worked_days_line_ids .

## 9. Owl 3

CE + EE

Odoo 20 web is Owl 3.

Odoo 19

Odoo 20

`import { useState } from`

"@odoo/owl"

`import { proxy } from "@odoo/owl" then`

this.state = proxy({ ... })

template state.foo / kpis.foo /

dashboardData.foo

this.state.foo / this.kpis.foo /

this.dashboardData.foo / this.props.foo

t-esc

t-out

t-model on a proxy() field

t-model accepts a signal only. proxy() fields use

t-att-value + t-on-input

t-set inside t-call as a sub-

template variable

slot body — pass parameters as attributes on <t t-

call="..."/>

standardActionServiceProps

`from action_service`

@web/webclient/actions/action_plugin

Chart.js v2 options

Chart.js v4 ( cutout , plugins.legend ,

plugins.title , scales.y.beginAtZero ) at

web/static/lib/Chart/Chart.js

_attachment_format

_store_attachment_fields

mail.AttachmentList props

attachments

attachmentGroups ; container o-mail-

AttachmentContainer

mail.assets_messaging

empty — put JS/XML in web.assets_backend

window.alert in systray

notifications; company is user.activeCompany

`import { proxy } from "@odoo/owl";`

this.state = proxy({ total: 0 });

`<t t-out="this.state.total"/>`

`<t t-out="this.kpis.open"/>`

t-as loop locals stay unprefixed. A static CSS class is not a template

identifier ( ud-widget stays ud-widget ).

static props = { "*": true };

`import { signal } from "@odoo/owl";`

this.searchTerm = signal("");

Mail store CE + EE:

Store().add(channel, "_store_channel_fields")._build_result()

this.store["mail.thread"].getOrFetch({ model: "discuss.channel", id })

A Python method called from Owl as [[], payload] must be @api.model .

Owl 3 also drops or relocates several 19 hooks. Replace them when the 20

component fails to compile or never re-renders.

Odoo 19

Odoo 20

this.render()

the proxy / signal update re-renders; do not call

render

t-portal

removed — render into the target node, or a 20 portal

helper if the standard component still exposes one

onWillUpdateProps /

onWillRender / onRendered

removed from Owl 3. Use onWillStart , onMounted ,

onWillUnmount , and onPatched

## 10. Accounting and payments

CE + EE unless marked EE.

Odoo 19

Odoo 20

invoice lines journal_line_ids

line_ids

invoice salesperson group

sale_info_group (customer invoices)

vendor bill extra fields

accounting_info_group

journal entry other info

other_tab_entry

header dates / flags

header_right_group

res.partner.bank.acc_number

account_number

res.partner.bank.acc_holder_name

holder_name

res.partner.bank.bank_id.name /

bank_id.bic

bank_name / bank_bic

account.journal.bank_id

bank_name

res.bank

removed — Char, or res.partner.bank

account.analytic.account.group_id

plan_id

payment.provider.state

is_live / is_published

payment.controllers.post_processing

removed

payment transaction group

//group//group

//group[@name='transaction_details']

invoice report o.type

o.move_type

account.group

removed

account.account.group_id

parent_id / parent_ids on

account.account

account code required

code is computed / optional ( code_store ,

placeholder_code )

account.payment state in_process

paid

account.payment state paid

reconciled

### ACCOUNT GROUPS → PARENT ACCOUNTS

19 has account.group and account.account.group_id . 20 deletes account.group .

Hierarchy lives on account.account :

# 20

parent_id = fields.Many2one('account.account', string="Parent Account")

parent_ids = fields.Many2many('account.account', compute='_compute_parent_ids')

Replace searches on account.group and writes to group_id with parent

accounts. Account codes are no longer a required stored Char; 20 computes

code ( compute_sql ). Reports that JOIN a mandatory account_account.code must

tolerate empty codes and use placeholder_code when displaying.

### PAYMENT STATES

Odoo 19

Odoo 20

draft

draft

in_process

paid

paid

reconciled

canceled

canceled

Filters, automations, and domains that still use in_process match nothing. A

payment that 19 called “Paid” is Reconciled on 20. A payment that 19 called

“In Process” is Paid on 20.

### FIXED ASSETS — EE

19 Enterprise treats a depreciation template as account.asset with state ==

'model' . 20 Enterprise adds account.depreciation.model . Bind templates,

default depreciation methods, and CoA-generated models to that model.

account.asset remains the asset document.

payment.method.provider_id is required. Create the provider first. There is no

payment.payment_method_card xmlid in payment .

Custom fields copied from payment to the journal entry go in

_generate_move_vals / _synchronize_to_moves .

Invoice line _compute_account_id assigns line.account_id . It does not return .

## 11. Sales, purchase, and products

CE + EE

Odoo 19

Odoo 20

sale.order state done

removed. Valid: draft / sent /

sale / cancel

purchase.order.line UoM product_uom_id

uom_id

sale.order.line / account.move.line UoM

still product_uom_id

product.type == 'product'

is_storable

product.pricelist.item._compute_price(...,

date) positional

date= keyword

( _compute_base_price the same)

sale.prod_config_main

sale.menu_sale_config

product.product_normal_action

product.product_variant_action

product.product_variant_easy_edit_view

removed

sale.order.line still has product_uom_qty and product_uom_id .

## 12. Inventory, MRP, and repair

CE + EE

Odoo 19

Odoo 20

stock.scrap

stock.move with is_scrap=True

scrap name

reference

scrap / move UoM product_uom /

product_uom_id

uom_id

scrap dest scrap_location

company.scrap_location_id

scrap validate

action_scrap()

scrap form / action

stock.view_scrap_move_form /

stock.stock_scrapped_moves_action

stock.return.picking

stock.picking._create_return()

stock.quant.package

stock.package

stock_picking_batch

merged into stock ; inherit

stock.stock_picking_batch_form

mrp.bom / mrp.bom.line /

repair.order UoM

uom_id

picking move list UoM

//field[@name='move_ids']/list/field[@name='uom_

mrp.production.show_produce_all

removed

MO button “Produce All” (separate

`from Produce)`

one button_mark_done

19 manufacturing orders expose show_produce_all and two header buttons

(Produce vs Produce All). 20 removes that field. Close the order with

button_mark_done only. Xpaths and automations that test show_produce_all fail.

## 13. HR, time off, and payroll

CE + EE for employee / time off. EE for Payroll.

Odoo 19

Odoo 20

hr.contract

hr.version

SQL join hr_contract

hr_version

hr.version.wizard

employee.contract_template_id +

_onchange_contract_template_id()

hr.leave.type

hr.work.entry.type

hr.leave.holiday_status_id

work_entry_type_id

hr.leave.action_confirm

removed; action_approve remains

hr.leave.holiday_type

validation_type

inherit time-off type form

hr_holidays.hr_work_entry_type_view_for

support_document

hr.expense.sheet

hr.expense

hr_work_entry.work_entry_type_attendance

hr_work_entry.generic_work_entry_type_a

legal leave default

hr_work_entry.generic_work_entry_type_l

leave XML on hr.leave.type

merge onto hr.work.entry.type

( count_as='absence' , time_off_selectabl

depend hr_work_entry_holidays only

hr_holidays

EE hr.payslip.input.type

removed; input_usage_payslip on the salar

EE salary rule category_id / struct_id

category_ids / struct_ids

[(6, 0, [ref

EE payslip.paid_amount

payslip._get_basic_salary()

Odoo 19

Odoo 20

EE payment wizard export_format

selection_add

_get_export_format_selection()

EE pay-run kanban

hr_payroll.hr_payrun_payslip_kanban_car

EE hr.work.entry list documents

removed; print from hr.payslip

worked_days_line_ids

Search filter approve on time off is nested. //search/filter[@name='approve']

does not match. Use //filter[@name='approve'] .

Several 20 workflows use state canceled , not cancel .

## 14. Project, timesheets, and portal

CE + EE unless marked EE.

Odoo 19

Odoo 20

project.task.user_id

user_ids

access domain task_id.user_id

('task_id.user_ids', 'in', [user.id])

note.note

project.task ( project_todo )

todo default_memo

default_name ( project.task has no memo )

project.portal_my_home

portal.entry ( project.portal_projects ,

project.portal_tasks )

portal card active

show_in_portal

portal_client_category /

portal_service_category

removed

portal.portal_sidebar

//t[@t-

set='entries']

//div[hasclass('col-lg-3')]

invoice portal download

//div[hasclass('o_download_pdf')]

portal docs wrap

div.o_portal_docs

get_records_pager

removed

_prepare_home_portal_values counters are merged in counters() . Group-

restricted cards use is_config_card and _filter_visible_portal_cards .

### PROJECT PROFITABILITY — CE

19 Community project.project implements _get_profitability_items ,

_get_profitability_values , _get_profitability_labels , and related helpers. Those

methods are not on Community 20 project . Overrides and tests that call

them raise AttributeError . Enterprise 20 reports margin and budget through

the budget apps (Chapter 17), not through those 19 CE hooks.

EE Field Service: industry_fsm is not in Enterprise 20. Depend project (and

sign if signatures are used).

Odoo 19 EE

Odoo 20

industry_fsm

project

industry_fsm.fsm_menu_root

project.menu_main_pm

industry_fsm.group_fsm_user

project.group_project_user

is_fsm is not a standard 20 field. Custom domains that still use it need a

local Boolean on project.project / project.task . Enterprise Planning

( planning.slot ) is a different model.

## 15. CRM, calendar, and mail

CE + EE

Odoo 19

Odoo 20

CRM

//div[hasclass('oe_title')]/div

//div[hasclass('oe_title')]

lead currency_id (standard)

company_currency

notebook page[@name='lead']

internal_notes / extra

Extra Info company_id in

categorization

//page[@name='extra']//field[@name='company_id']

( group[@name='Misc'] )

graph amount

type="measure"

calendar button_box

removed — see Chapter 7

calendar page_invitations

notes / options

mail.tracking.value in mail

Community addon mail_tracking (Chapter 5)

## 16. Website and eCommerce

CE + EE

`<!-- 19 — 500 on 20 public pages -->`

<input t-attf-value="#{user_id.partner_id.email}"/>

`<!-- 20 -->`

<input t-att-value="request.env.user.partner_id.email if not request.env.user._is_

Odoo 19

Odoo 20

a[@id='add_to_cart']

button[@name='add_to_cart']

add-to-cart wrap

div[@id='add_to_cart_wrap'] / website_

#o_wsale_cta_wrapper

product._is_add_to_cart_possible() form

removed

website_sale.product_terms_and_conditions

removed — xpath after #o_wsale_product_c

#wrap.js_sale

removed

website_sale_wishlist /

website_sale_comparison

merged into website_sale

wishlist / compare xmlids

website_sale.product_wishlist , website

website_sale.model_product_wishlist

comparison controller

odoo.addons.website_sale.controllers.c

hide price

combination_info['hide_price']

category form sequence

list only — xpath parent_id

res.partner.company_type

removed — is_company

res.partner.mobile

removed — phone

res.users.groups_id

group_ids

action context default_company_type

default_is_company

ir.ui.view.groups_id

unchanged (view access, not the user field)

Font Awesome class on website snippets ( fa

fa-... )

Material Symbols ligature / oi + data-icon

request.website in a model method

`self.env.website (Chapter 2)`

Website and snippet markup that still ships Font Awesome class names will

not draw on 20. Use the same ViewButton / Material Symbols names as

Chapter 7 ( check , close , …). Public pages that read request from a model or

report parser hit request not bound ; use env.website .

# 19

`vals['company_type'] = 'person'`

`vals['mobile'] = '...'`

`user_vals['groups_id'] = [(6, 0, ids)]`

# 20

`vals['is_company'] = False`

`vals['phone'] = '...'`

`user_vals['group_ids'] = [(6, 0, ids)]`

## 17. Enterprise budget, Field Service,

Helpdesk, and Fleet

### BUDGET — EE

Odoo 19 Enterprise

Odoo 20 Enterprise

crossovered.budget

budget.analytic

crossovered.budget.lines

budget.line

lines field

budget_line_ids

amount field

budget_amount

states

draft / confirmed / revised / done / canceled

form

account_budget.view_budget_analytic_form

action

account_budget.act_budget_analytic_view

report binding

account_budget.model_budget_analytic

committed_amount

on account_budget_purchase

CE Community 20 has no budget.analytic . A Community budget module

that still uses its own model is not the Enterprise model and is not

retargeted to account_budget .

### HELPDESK

EE Enterprise helpdesk remains. CE a custom helpdesk.sla

`_name must not`

`_inherit = 'helpdesk.sla' unless Enterprise Helpdesk is in the registry`

(Chapter 2).

These 19 Enterprise addons have no 20 folder. Depend project / helpdesk /

documents instead of the FSM bridges:

Odoo 19 Enterprise

Odoo 20

industry_fsm*

project (Chapter 14)

helpdesk_fsm / helpdesk_fsm_report / helpdesk_fsm_sale

helpdesk

documents_fsm

documents

### FIXED ASSETS — EE

See Chapter 10. 20 adds account.depreciation.model . 19 templates were

account.asset with state == 'model' .

### AI ADDONS — EE

Enterprise 20 ships a set of ai_* modules. They are new optional apps, not

a rename of a 19 module. Do not add them to a 19 graph unless the 20

database actually uses that stack.

### FLEET — CE + EE

Odoo 19

Odoo 20

fleet.vehicle.log.services.date

date_from / date_to

## 18. Symptom index

Exception or result

Chapter

KeyError: 'ir.rule'

Field has no SQL representation

use BinaryValue instead of bytes

Incorrect padding / invalid .xlsx

No module named xlwt / pytz

stock.scrap missing

hr.leave.type / hr.contract missing

hr.expense.sheet missing

industry_fsm missing

14, 17

crossovered.budget missing

Invalid field 'company_type' / 'groups_id' / 'mobile'

mail.thread.cc / MRO error

useState is not a function

Cannot read properties of undefined in Owl

LiteralSQL / _select concatenate

`xpath parse / does not match`

<act_window> / <report> RNG

sale done never matches

portal /my cards missing

get_param / set_param missing

2, 5

check_access_rights / _name_search missing

2, 3

request not bound

type='json' deprecation

ViewButton icon blank

Exception or result

Chapter

_table_query / overwrite _table_sql

mail.tracking.value missing

5, 15

account.group missing

payment in_process never matches

show_produce_all missing

_get_profitability_items missing

helpdesk_fsm / documents_fsm missing

account.depreciation.model missing on 19 code

10, 17

Font Awesome icon blank on website

7, 16

request.website / env.website

2, 16

## 19. Mapping tables

> **Recovery method:** The PDF's rightmost table cells are clipped on pages 51–55. The tables below preserve the visible entries and recover truncated values where they can be checked against the Odoo 20.0 Community source or the visible remainder of the PDF. Enterprise-only XML IDs still require validation against the matching Enterprise 20.0 source tree. “Removed” means no direct replacement is asserted.

### Models

| Odoo 19 | Odoo 20 |
|---|---|
| `hr.contract` | `hr.version` — **Edition:** CE + EE; **Notes:** Employee contract data is represented through employee versions. |
| `hr.leave.type` | `hr.work.entry.type` — **Edition:** CE + EE; **Notes:** Validate the business relation and time-off configuration during migration. |
| `hr.expense.sheet` | `hr.expense` — **Edition:** CE + EE; **Notes:** Expense model/workflow consolidation; validate workflow changes. |
| `hr.payslip.input.type` | Removed; use the Odoo 20 payroll input design (`input_usage_payslip` is visible in the PDF) — **Edition:** EE; **Notes:** Exact Enterprise replacement requires target-source verification. |
| `stock.scrap` | `stock.move` with `is_scrap=True` — **Edition:** CE + EE; **Notes:** Scrap is represented as a stock move. |
| `stock.return.picking` | `stock.picking._create_return()` — **Edition:** CE + EE; **Notes:** The PDF's mapping table explicitly shows `_create_return()`; verify its signature in the deployed target branch. |
| `stock.quant.package` | `stock.package` — **Edition:** CE + EE; **Notes:** Package model renamed/reworked. |
| `note.note` | `project.task` (`project_todo`) — **Edition:** CE + EE; **Notes:** The PDF associates notes with project tasks; note-specific fields and access rules need migration. |
| `mail.thread.cc` | `mail.thread` — **Edition:** CE + EE; **Notes:** `mail.thread.cc` is removed; do not inherit it separately. |
| `res.bank` | Char field or `res.partner.bank`, depending on use — **Edition:** CE + EE; **Notes:** No universal one-to-one replacement. |
| `industry_fsm` | `project` — **Edition:** EE; **Notes:** Field Service functionality is reorganized under Project. |
| `stock_picking_batch` | `stock` — **Edition:** CE + EE; **Notes:** Batch picking functionality is reorganized under Stock. |
| `website_sale_wishlist` | `website_sale` — **Edition:** CE + EE; **Notes:** Wishlist functionality is merged into `website_sale`. |
| `website_sale_comparison` | `website_sale` — **Edition:** CE + EE; **Notes:** Product comparison functionality is merged into `website_sale`. |
| `crossovered.budget` | `budget.analytic` — **Edition:** EE; **Notes:** Analytic budgets model replacement. Not part of Community 20. |
| `crossovered.budget.lines` | `budget.line` — **Edition:** EE; **Notes:** Analytic budget line model replacement. |
| `hr.version.wizard` | Removed — **Edition:** CE + EE; **Notes:** Confirm the employee-version workflow used by the deployed database. |
| `account.group` | `account.account` hierarchy (`parent_id`, computed `parent_ids`) — **Edition:** CE + EE; **Notes:** `account.group` is removed; hierarchy is represented on accounts. |
| `account.asset` where `state='model'` | `account.depreciation.model` — **Edition:** EE; **Notes:** Depreciation templates are represented by a separate model; asset documents remain distinct. |
| `mail.tracking.value` (provided by `mail`) | `mail.tracking.value` in `mail_tracking` — **Edition:** CE + EE; **Notes:** Add `mail_tracking` when stored tracking rows are required. |
| `helpdesk_fsm`, `helpdesk_fsm_report`, `helpdesk_fsm_sale` | `helpdesk` — **Edition:** EE; **Notes:** FSM bridge modules are consolidated/reorganized; validate Enterprise module graph. |
| `documents_fsm` | `documents` — **Edition:** EE; **Notes:** Field Service document integration is reorganized under Documents. |

### Fields

| Odoo 19 | Odoo 20 |
|---|---|
| `sale.order` | `state = 'done'` — **Odoo 20 field / value:** Removed; **Edition:** CE + EE; **Migration note:** Remove filters/domains relying on `done`; map to target workflow behavior. |
| `stock.move.line`, `stock.move`, `purchase.order.line`, `mrp.bom`, `repair.order` | `product_uom_id` / `product_uom` — **Odoo 20 field / value:** `uom_id`; **Edition:** CE + EE; **Migration note:** Update field references, domains, views and custom code. |
| `sale.order.line`, `account.move.line` | `product_uom_id` — **Odoo 20 field / value:** Unchanged; **Edition:** CE + EE; **Migration note:** Keep the existing field on these models. |
| `res.partner.bank` | `acc_number`, `acc_holder_name` — **Odoo 20 field / value:** `account_number`, `holder_name`; **Edition:** CE + EE; **Migration note:** Update Python, XML, domains, exports and integrations. |
| `res.partner` | `company_type`, `mobile` — **Odoo 20 field / value:** `is_company`, `phone`; **Edition:** CE + EE; **Migration note:** `company_type` maps to `is_company`; `mobile` is shown as removed in favor of `phone`. Validate semantics before bulk migration. |
| `res.users` | `groups_id` — **Odoo 20 field / value:** `group_ids`; **Edition:** CE + EE; **Migration note:** Update group assignment code. |
| `ir.attachment` | `datas` — **Odoo 20 field / value:** `raw`; **Edition:** CE + EE; **Migration note:** Binary payload API changed; inspect code expecting base64 strings. |
| `project.task` | `user_id` — **Odoo 20 field / value:** `user_ids`; **Edition:** CE + EE; **Migration note:** Assignment becomes plural; update searches, writes, views and access domains. |
| `product.template` | `type == 'product'` — **Odoo 20 field / value:** `is_storable`; **Edition:** CE + EE; **Migration note:** Replace product-type checks with the storable flag. |
| `hr.leave` | `holiday_status_id` — **Odoo 20 field / value:** `work_entry_type_id`; **Edition:** CE + EE; **Migration note:** Update time-off type references. |
| `hr.leave` | `holiday_type` — **Odoo 20 field / value:** `validation_type`; **Edition:** CE + EE; **Migration note:** Update approval/validation logic. |
| `account.analytic.account` | `group_id` — **Odoo 20 field / value:** `plan_id`; **Edition:** CE + EE; **Migration note:** Analytic account grouping is replaced by analytic plans. |
| `crm.lead` | `currency_id` — **Odoo 20 field / value:** `company_currency`; **Edition:** CE + EE; **Migration note:** Verify exact field type and semantics in target source. |
| `fleet.vehicle.log.services` | `date` — **Odoo 20 field / value:** `date_from`, `date_to`; **Edition:** CE + EE; **Migration note:** Update service date filters and forms. |
| `payment.provider` | `state` — **Odoo 20 field / value:** `is_live`, `is_published`; **Edition:** CE + EE; **Migration note:** Update provider activation/publication logic. |
| `resource.calendar.leaves` | `time_type` — **Odoo 20 field / value:** `count_as` (for example, `count_as='absence'`); **Edition:** CE + EE; **Migration note:** Update calendar-leave classification logic. |
| `account.move` report | `type` — **Odoo 20 field / value:** `move_type`; **Edition:** CE + EE; **Migration note:** Update report expressions and domains. |
| `account.account` | `group_id` — **Odoo 20 field / value:** `parent_id`, `parent_ids`; **Edition:** CE + EE; **Migration note:** Account hierarchy moves to account records; `parent_ids` is computed. |
| `account.payment` | `state = 'in_process'` — **Odoo 20 field / value:** `state = 'paid'`; **Edition:** CE + EE; **Migration note:** State mapping shown by the cookbook. Verify workflow semantics against the target source. |
| `account.payment` | `state = 'paid'` — **Odoo 20 field / value:** `state = 'reconciled'`; **Edition:** CE + EE; **Migration note:** State mapping shown by the cookbook. Verify workflow semantics against the target source. |
| `mrp.production` | `show_produce_all` — **Odoo 20 field / value:** Removed; use the `button_mark_done` workflow; **Edition:** CE + EE; **Migration note:** Remove references to the old field/button. |
| Binary field values | bytes/base64 — **Odoo 20 field / value:** `BinaryValue` and optional `.filename`; **Edition:** CE + EE; **Migration note:** The PDF describes binary values as `BinaryValue`; use `BinaryBytes` for writes. |

### XML IDs, Views, and API / Runtime Changes

| Odoo 19 | Odoo 20 |
|---|---|
| `sale.prod_config_main` | `sale.menu_sale_config` — **Edition:** CE + EE; **Recovery notes:** Full right-hand value recovered from the clipped cell. |
| `product.product_normal_action` | `product.product_variant_action` — **Edition:** CE + EE; **Recovery notes:** Full right-hand value recovered from the clipped cell. |
| `product.product_variant_easy_edit_view` | Removed — **Edition:** CE + EE; **Recovery notes:** Replace custom view inheritance with an available Odoo 20 view. |
| `project.view_project_kanban_body` | `project.view_project_card` — **Edition:** CE + EE; **Recovery notes:** PDF page 55 shows `project.view_project_card`; Kanban card template changes are documented in Chapter 7. |
| `project.view_task_kanban_card` | `project.view_task_card` — **Edition:** CE + EE; **Recovery notes:** Full right-hand value recovered from the clipped cell. |
| `project.portal_my_home` | `portal.entry` — **Edition:** CE + EE; **Recovery notes:** Portal entry-point structure changes; confirm whether the replacement is a template-level or XML-ID-level dependency in the deployed source. |
| `industry_fsm.fsm_menu_root` | `project.menu_main_pm` — **Edition:** EE; **Recovery notes:** Field Service menu moved under Project. |
| `hr_work_entry.work_entry_type_attendance` | `generic_work_entry_type_attendance` — **Edition:** CE + EE; **Recovery notes:** PDF page 55 shows the right-hand identifier without a visible module prefix. Do not assume a prefixed external ID without checking the target data XML. |
| Pay-run kanban | `hr_payroll.hr_payrun_payslip_kanban_card` — **Edition:** EE; **Recovery notes:** The visible right-hand text is clipped after `...kanban_ca`; `..._card` is reconstructed from the table text and naming pattern and must be verified against Enterprise 20. |
| Enterprise budget form | `account_budget.view_budget_analytic_form` — **Edition:** EE; **Recovery notes:** Right-hand cell clipped after `...analytic_for`; suffix `m` is restored from the same form XML ID shown on page 45. |
| Scrap form | `stock.view_scrap_move_form` — **Edition:** CE + EE; **Recovery notes:** Full right-hand value is visible. |
| Batch picking form | `stock.stock_picking_batch_form` in `stock` — **Edition:** CE + EE; **Recovery notes:** The trailing words “in stock” are visible; they indicate the defining module. |
| `Model._table_query` | `Model._table_sql` property returning an `SQL` object — **Edition:** CE + EE; **Recovery notes:** PDF pages 20 and 55 show the replacement. |
| `request.website` in model methods | `self.env.website` — **Edition:** CE + EE; **Recovery notes:** Use the environment; `request` may not be bound in model/report contexts. |
| wkhtmltopdf assumed inside `web` | `base_report_wkhtmltox` / `base_report_paper_muncher` — **Edition:** CE + EE; **Recovery notes:** Module split/reorganization shown in the PDF. Verify module availability in target deployment. |
| JSON-2 `/json/2/<model>/<method>` | Still present and preferred for new external integrations; XML-RPC `/xmlrpc/2` still present in Odoo 20 — **Edition:** CE + EE; **Recovery notes:** The PDF explicitly warns not to describe XML-RPC as already removed in 20. |

### Other clipped or malformed tables recovered from the chapter pages

The following are table-cell recoveries from the main chapters, not new migration claims. The source PDF text extraction had split or truncated these cells across columns.

#### ORM and Python

| Odoo 19 | Odoo 20 |
|---|---|
| `_sql_constraints = [('name', 'sql', 'msg')]` | `_name = models.Constraint(...)` — **Recovery status:** Full pattern is shown in Chapter 2's code example. |
| `self.fields_view_get(...)` | `self._get_view(...)` — **Recovery status:** Visible in Chapter 2's mapping table. |
| `self.check_access_rights('read')` | `self.check_access('read')` — **Recovery status:** Visible in Chapter 2's mapping table. |
| `self.check_access_rights('read', raise_exception=False)` | `self.has_access('read')` — **Recovery status:** Visible mapping; check exact target method signature before using. |
| `self.user_has_groups('sales_team.group_sale_manager')` | `self.env.user.has_groups(...)` — **Recovery status:** Right-hand argument is clipped in the PDF; preserve the group XML ID from the left-hand expression. |
| `self._context` | `self.env.context` — **Recovery status:** Visible in Chapter 2. |
| `self.env.user.company_id` | `self.env.company` — **Recovery status:** Visible in Chapter 2. |
| `ir.config_parameter.get_param` / `set_param` | Typed getters/setters such as `get_int`, `get_str`, `get_bool`, `set_str`, `set_bool`, `set_float` — **Recovery status:** PDF cell is clipped; exact supported typed methods should be checked in the target source. |
| `pytz` | `datetime.UTC` and `zoneinfo` — **Recovery status:** Visible in Chapter 2 / Chapter 4 examples. |
| window action `toggle_active` | `action_archive` / `action_unarchive` — **Recovery status:** The PDF's right edge truncates `action_unarchive`; recovered from Chapter 2 context and Odoo 20 migration notes. |
| `write({'archive': True})` | `write({'active': False})` — **Recovery status:** The PDF's table uses “write archive=True” / “write active=False”; normalized to Python mapping syntax here for clarity. |

#### Search and domains

| Odoo 19 | Odoo 20 |
|---|---|
| `_name_search` | `_rec_names_search` and/or `_search_display_name` — **Recovery status:** Both target patterns are shown in Chapter 3; select based on the customization being migrated. |
| `from odoo.osv import expression`; `expression.AND` / `expression.OR` | `from odoo.fields import Domain`; `Domain.AND` / `Domain.OR` — **Recovery status:** Full mapping visible in Chapter 3. |
| `from odoo.fields import Domain, AND, FALSE_DOMAIN` | `from odoo.fields import Domain` and `Domain.FALSE` — **Recovery status:** The right-hand cell is split over lines in the PDF; the replacement is reconstructed from visible text. |
| `_name_search(..., args=..., name_get_uid=...)` | `_search_display_name` signature: `(self, name, domain=None, operator='ilike', limit=None, order=None)` — **Recovery status:** The PDF displays the new signature in the right-hand column. |
| `_read_group_stage_ids(self, stages, domain, order)` | `_read_group_stage_ids(self, stages, domain)` — **Recovery status:** The `order` argument is removed in the visible mapping. |
| View modifier `in 'x'` / `not in 'x'` | `== 'x'` / `!= 'x'` — **Recovery status:** PDF notes tuple membership such as `('a', 'b')` is valid. |

#### Binary, Excel, PDF and time

| Odoo 19 | Odoo 20 |
|---|---|
| `xlwt` | `xlsxwriter`; write to `io.BytesIO` with `{'in_memory': True}` and assign with `BinaryBytes` — **Recovery status:** Right-hand cell restored from the wrapped lines on PDF page 15. |
| `xlrd.open_workbook` for `.xlsx` | `openpyxl` for PK/Office Open XML `.xlsx`; `xlrd` only for OLE `.xls` — **Recovery status:** Full visible statement restored from page 15. |
| `import PyPDF2` | `from odoo.tools.pdf import PdfFileWriter, PdfFileReader` — **Recovery status:** Wrapped right-hand cell restored from page 15. |
| `content_disposition` in `odoo.tools` / old `odoo.http` path | `odoo.http.stream` — **Recovery status:** Right-hand mapping visible on page 15. |
| `_render_qweb_pdf(template_xmlid)` | `_render_qweb_pdf(action_xmlid)` — **Recovery status:** Visible in the PDF; pass the report action XML ID. |
| `request.env` in a report parser | Use `env`; `request.env` can raise `RuntimeError: request not bound` — **Recovery status:** Right-hand cell was split across the page text; restored from page 15. |
| `resource.calendar.leaves.time_type` | `count_as='absence'` — **Recovery status:** Visible on page 16. |
| `resource.calendar` field `tz` | Removed — **Recovery status:** Visible on page 16. |
| Calendar attendance `name` / `day_period` | Removed — **Recovery status:** Visible on page 16. |

#### Configuration, HTTP and mail

| Odoo 19 | Odoo 20 |
|---|---|
| `@http.route(..., type='json')` | `@http.route(..., type='jsonrpc')` for web-client routes — **Recovery status:** Visible on page 17. This is distinct from the external JSON-2 API. |
| Server action state `mail_post` plus `template_id` and optional `mail_post_autofollow` | `mail_post_method` — **Recovery status:** The table cell is split across lines on page 17; reconstructed from visible fragments. |
| Enterprise server action | `use_in_ai`, `ai_tool_name` matching `[a-zA-Z0-9_]{1,64}` — **Recovery status:** Visible on page 17. |
| Settings XPath `group[@name='preferences']` | `//page[@name='preferences']//group[@name='other_preferences']` — **Recovery status:** Right-hand XPath is clipped at the page edge; restored from the visible wrapped text. |
| Employee settings XPath | Insert after `employees_setting_container` — **Recovery status:** Visible on page 17. |
| `mail.tracking.value` in core `mail` | Install `mail_tracking`; model remains `mail.tracking.value` in that addon — **Recovery status:** Visible across pages 17–18. |

#### Views

| Odoo 19 | Odoo 20 |
|---|---|
| `project.view_project_kanban_body` | `project.view_project_card` — **Recovery status:** Visible on pages 7 and 55; the kanban card is separated into a `card` view. |
| `project.view_task_kanban_footer` | `project.view_task_card`, XPath `//t[@t-name='card']//footer` — **Recovery status:** The right-hand XPath was wrapped and clipped; restored from page 7. |
| Kanban template name | `t-name="card"` — **Recovery status:** Visible in Chapter 7. |
| `<button icon="fa-check"/>` | `<button icon="check"/>` — **Recovery status:** Visible in Chapter 7. |
| Ribbon `text="Archived"`, `bg_color="bg-info"` | `title="Archived"`, `bg_color="text-bg-info"`, with `invisible="active"` — **Recovery status:** The final `invisible` expression is clipped in the PDF; verify exact view logic in target source. |
| Font Awesome icon names in web client | `web/icons.py` icon names / `oi` and `data-icon` rendering — **Recovery status:** Visible in Chapter 7. |
| Font Awesome ligatures in website snippets | Material Symbols ligatures — **Recovery status:** Visible in Chapter 7 and Chapter 16. |
| Form view `//header` on Analytic Account | No header in the inherited view; insert a `<header>` — **Recovery status:** Visible in Chapter 7. |
| Timesheet button box | `div[@name='button_box']` already exists — **Recovery status:** Visible in Chapter 7. |
| Calendar Event button box | Removed; buttons are in the header / ribbon structure — **Recovery status:** PDF cell is split; verify exact parent XPath before applying. |
| Partner list `complete_name` | `display_name` — **Recovery status:** Visible in Chapter 7. |
| Partner search `group[@name='group_by']` | `//search/group` — **Recovery status:** Visible in Chapter 7. |
| User preferences `group[@name='preferences']` | `//page[@name='preferences']` — **Recovery status:** Visible in Chapter 7. |
| Product action `product.product_normal_action` | `product.product_variant_action` — **Recovery status:** Visible in Chapter 7 / page 55. |
| Sale config menu `sale.prod_config_main` | `sale.menu_sale_config` — **Recovery status:** Visible in Chapter 7 / page 55. |

### Source verification boundaries

- Community source branch: [odoo/odoo 20.0](https://github.com/odoo/odoo/tree/20.0).
- Odoo 20 migration code changes documented by another source include `ir.model.access` / `ir.rule` replacement by `ir.access`, `mail.tracking.value` moving to `mail_tracking`, JSON-2 at `/json/2/<model>/<method>`, removal of `toggle_active`, typed `ir.config_parameter` methods, `_table_query` → `_table_sql`, and binary fields represented by `BinaryValue`. See [Odoo 20 migration roadmap](https://github.com/infovpcs/odoo-agent-pro-kit/blob/main/docs/odoo-20-migration-roadmap.md).
- The PDF itself does not expose the full right-hand values for every Enterprise-only cell. Those are not presented as source-verified merely because a plausible identifier can be inferred. Check the corresponding Enterprise 20.0 source tree before deploying migrations.
