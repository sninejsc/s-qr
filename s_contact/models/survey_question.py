from odoo import fields, models, api


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    fields_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Fields')
