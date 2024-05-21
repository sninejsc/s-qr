# -*- coding: utf-8 -*-


from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    hide_menu_access_ids = fields.Many2many('ir.ui.menu', 'ir_ui_hide_menu_rel', 'uid', 'menu_id',
                                            string='Hide Access Menu')

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        self.self.clear_caches()
        return res
