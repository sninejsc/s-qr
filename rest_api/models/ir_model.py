
from odoo import models, fields


class IrModel(models.Model):
    _inherit = "ir.model"

    rest_api_used = fields.Boolean(string='Use in REST API', default=True)
