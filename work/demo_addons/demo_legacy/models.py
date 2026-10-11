import pytz
from odoo import models, fields, api
from odoo.osv import expression
from odoo.tools import ormcache, Query


class DemoModel(models.Model):
    _name = 'demo.legacy'
    _description = 'Legacy demo'

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code must be unique'),
    ]

    code = fields.Char()
    total = fields.Monetary(group_operator='sum')
    tz = fields.Char(default=lambda self: str(pytz.UTC))

    @ormcache('code')
    def _get_id(self, code):
        return self.env.context.get('x')

    def action_check(self):
        self.check_access_rights('read')
        if self._check_recursion():
            return False
        self.toggle_active()
        groups = self.read_group([('id', '>', 0)], ['total'], ['code'], lazy=False)
        domain = expression.AND([[('code', '=', self.code)], self._context.get('dom', [])])
        self.env.registry.clear_cache()
        return groups

    @api.route('/demo/legacy', type='json', auth='user')
    def legacy_route(self):
        return {'ok': request.env.user.has_group('base.group_user')}
