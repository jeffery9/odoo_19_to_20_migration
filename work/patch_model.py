#!/usr/bin/env python3
"""Merge cross-page tables and apply verified completions to clipped cells."""
import json

m = json.load(open('work/model_raw.json'))
pages = m['pages']

# ---------- 1. merge tables split across pages ----------
merged = 0
for i in range(1, len(pages)):
    prev_blocks = pages[i-1]['blocks']
    cur_blocks = pages[i]['blocks']
    if not prev_blocks or not cur_blocks:
        continue
    pb, cb = prev_blocks[-1], cur_blocks[0]
    if pb['t'] == 'table' and cb['t'] == 'table' and cb['cols'] == pb['cols']:
        ph = [''.join(r['text'] for r in c['lines'][0]) if c['lines'] else '' for c in (pb['header'] or [])]
        ch = [''.join(r['text'] for r in c['lines'][0]) if c['lines'] else '' for c in (cb['header'] or [])]
        if ph == ch:
            pb['rows'].extend(cb['rows'])
            cur_blocks.pop(0)
            merged += 1
print('merged tables:', merged)

# ---------- 2. drop fully-empty rows ----------
for pg in pages:
    for b in pg['blocks']:
        if b['t'] == 'table':
            b['rows'] = [r for r in b['rows']
                         if any(''.join(r2['text'] for ln in c['lines'] for r2 in ln).strip() for c in r)]

# ---------- 3. completions ----------
# ops: (page, row, col, line, run, expected_old, new)  ; run=None -> append run at end of line
OPS = [
 # ch2 ORM table
 (7, 0, 1, 0, 0, "_name = models.Constraint(", "_name = models.Constraint('sql', 'msg')"),
 (7, 3, 1, 0, 1, " (b", " (bool)"),
 (7, 4, 1, 0, 0, "self.env.user.has_groups('", "self.env.user.has_groups('sales_team.group_sale_manager')"),
 (7, 7, 1, 0, 4, "get_bo", "get_bool"),
 (7, 7, 1, 1, 4, "set_f", "set_float"),
 (7, 9, 1, 0, 2, "action_un", "action_unarchive"),
 # ch5 settings xpath
 (16, 3, 1, 0, 0, "//page[@name='preferences']//group[@name='other_prefe",
     "//page[@name='preferences']//group[@name='other_preferences']"),
 # ch7 views table
 (22, 0, 2, 0, 2, " w", " with workflow buttons"),
 (22, 1, 2, 0, 1, " alre", " already exists"),
 (22, 2, 2, 0, 3, "/", None),                      # drop stray wrapped slash chip
 (22, 2, 2, 1, 0, "//sheet/widget[@name='web_r", "//sheet/widget[@name='web_ribbon']"),
 (22, 3, 2, 0, 2, "//h1[hasclass('o_em", "//h1[hasclass('o_employee_form_header_info')]"),
 (22, 4, 2, 0, 3, "; form alre", "; form already uses recruiter_id"),
 (22, 7, 2, 0, 0, "//group[hasclass('oe_subtot", "//group[hasclass('oe_subtotal_footer')]"),
 (22, 13, 2, 0, 0, "product.product_variant_act", "product.product_variant_action"),
 (22, 20, 2, 0, 0, "point_of_sale.pos_order_rec", "point_of_sale.pos_order_receipt"),
 (22, 22, 2, 0, 0, "div#sale_order_sidebar_butt", "div#sale_order_sidebar_button"),
 # ch12 inventory
 (33, 10, 1, 0, 0, "//field[@name='move_ids']/list/field[@name='uom_",
     "//field[@name='move_ids']/list/field[@name='uom_id']"),
 # ch13 HR
 (36, 7, 1, 0, 0, "hr_holidays.hr_work_entry_type_view_for", "hr_holidays.hr_work_entry_type_view_form"),
 (36, 9, 1, 0, 0, "hr_work_entry.generic_work_entry_type_a", "hr_work_entry.generic_work_entry_type_attendance"),
 (36, 10, 1, 0, 0, "hr_work_entry.generic_work_entry_type_l", "hr_work_entry.generic_work_entry_type_legal_leave"),
 (36, 11, 1, 1, 5, "time_off_selectabl", "time_off_selectable"),
 (36, 13, 1, 0, 2, " on the salar", " on the salary structure"),
 (36, 14, 1, 1, 2, ", 0, [ref", ", 0, [ref(...)])]"),
 (36, 17, 1, 0, 0, "hr_payroll.hr_payrun_payslip_kanban_car", "hr_payroll.hr_payrun_payslip_kanban_card"),
 # ch16 website
 (42, 1, 1, 0, 2, "website_", "website_sale.cta_wrapper"),
 (42, 3, 1, 0, 1, "#o_wsale_product_c", "#o_wsale_product_cta_section"),
 (42, 6, 1, 0, 3, "website", "website_sale.product_compare"),
 (42, 7, 1, 0, 0, "odoo.addons.website_sale.controllers.c", "odoo.addons.website_sale.controllers.cart"),
 (42, 15, 1, 0, None, None, " rendering"),
 # ch19 mapping table
 (54, 8, 1, 0, 0, "hr_payroll.hr_payrun_payslip_kanban_car", "hr_payroll.hr_payrun_payslip_kanban_card"),
 (54, 9, 1, 0, 0, "account_budget.view_budget_analytic_for", "account_budget.view_budget_analytic_form"),
 (54, 15, 1, 0, 0, "still present (preferred external API); XML-RPC",
     "still present (preferred external API); XML-RPC /xmlrpc/2 still"),
]

def tables_on(pno):
    return [b for b in pages[pno]['blocks'] if b['t'] == 'table']

applied = 0
for op in OPS:
    pno, ri, ci, li, ridx, old, new = op
    tbls = tables_on(pno)
    assert len(tbls) == 1, f'page {pno} has {len(tbls)} tables'
    cell = tbls[0]['rows'][ri][ci]
    line = cell['lines'][li]
    if ridx is None:
        line.append({'text': new, 'size': 9.8, 'mono': False, 'bold': False,
                     'italic': False, 'color': '#241c14', 'x1': 0})
    else:
        run = line[ridx]
        assert run['text'] == old, f'p{pno} r{ri} c{ci} l{li} r{ridx}: {run["text"]!r} != {old!r}'
        if new is None:
            line.pop(ridx)
        else:
            run['text'] = new
            run['x1'] = 0
    cell['clipped'] = False
    applied += 1
print('applied ops:', applied, '/', len(OPS))

# ---------- 4. code-block line completions (pre-wrap blocks) ----------
CODE_FIX = [
 (14, "<img t-att-src=\"image_data_uri(doc.image_1920) if doc.image_1920 else '/web/static",
      "<img t-att-src=\"image_data_uri(doc.image_1920) if doc.image_1920 else '/web/static/img/placeholder.png\"/>"),
 (20, "<widget name=\"web_ribbon\" title=\"Archived\" bg_color=\"text-bg-info\" invisible=\"acti",
      "<widget name=\"web_ribbon\" title=\"Archived\" bg_color=\"text-bg-info\" invisible=\"active\"/>"),
 (41, "<input t-att-value=\"request.env.user.partner_id.email if not request.env.user._is_",
      "<input t-att-value=\"request.env.user.partner_id.email if not request.env.user._is_public() else ''\"/>"),
]
for pno, old, new in CODE_FIX:
    done = False
    for b in pages[pno]['blocks']:
        if b['t'] == 'code':
            for line in b['lines']:
                txt = ''.join(r['text'] for r in line)
                if txt == old:
                    line[0]['text'] = new
                    for r in line[1:]:
                        r['text'] = ''
                    line[0]['x1'] = 0
                    b['clipped'] = False
                    done = True
    assert done, f'code fix not found p{pno}'
print('code fixes applied')

# ---------- 5. merge wrapped lines back where intended as one sentence ----------
MERGE = [(54, 15, 1)]
for pno, ri, ci in MERGE:
    tbl = [b for b in pages[pno]['blocks'] if b['t'] == 'table'][0]
    cell = tbl['rows'][ri][ci]
    if len(cell['lines']) > 1:
        first = cell['lines'][0]
        for ln in cell['lines'][1:]:
            first.append({'text': ' ', 'size': 9.8, 'mono': False, 'bold': False,
                          'italic': False, 'color': '#241c14', 'x1': 0})
            first.extend(ln)
        cell['lines'] = [first]

json.dump(m, open('work/model.json', 'w'), indent=1)
print('model.json written')
