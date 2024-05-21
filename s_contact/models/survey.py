from odoo import fields, models, api


class Servey(models.Model):
    _inherit = 'survey.survey'

    connect_contact = fields.Boolean(
        string='Connect Contact')
