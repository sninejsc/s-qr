# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    contact_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact')

    def write(self, values):
        user_input = super(SurveyUserInput, self).write(values)
        if self.survey_id.connect_contact == True and values.get('state') == 'done':

            title = self.env.ref('base.res_partner_title_madam')
            if self.get_value('title') == 'Mr.':
                title = self.env.ref('base.res_partner_title_mister')

            name = 'New'
            if self.get_value('name'):
                name = self.get_value('name')

            phone = self.get_value('phone')
            email = self.get_value('email')

            partner_id = self.env['res.partner'].search(
                [('name', '=', name), ('phone', '=', phone), ('email', '=', email)])
            if not partner_id:
                value = {
                    'title': title.id,
                    'name': name,
                    'phone': phone,
                    'email': email,
                    'company_name': self.get_value('company_name'),
                    'business_nature': self.get_much_value('business_nature'),
                    'department': self.get_value('department'),
                    'function': self.get_value('function'),
                    'seminars': self.get_much_value('seminars'),
                    'question': self.get_value('question'),
                    'other': self.get_much_value('other'),
                    'category_id': [(4, self.env.ref('s_contact.category_normal').id)],
                    's_type': 'B',
                }
                partner_id = self.env['res.partner'].create(value)
            else:
                value = {
                    'title': title.id,
                    'company_name': self.get_value('company_name'),
                    'business_nature': self.get_much_value('business_nature'),
                    'department': self.get_value('department'),
                    'function': self.get_value('function'),
                    'seminars': self.get_much_value('seminars'),
                    'question': self.get_value('question'),
                    'other': self.get_much_value('other'),
                    'category_id': [(4, self.env.ref('s_contact.category_normal').id)],
                    's_type': 'B',
                }
                partner_id.write(value)
            self.contact_id = partner_id.id
            partner_id.action_send_mail()
        return user_input

    def get_value(self, fields_name):
        try:
            input_line_id = self.user_input_line_ids.filtered(lambda i: i.question_id.fields_id.name == fields_name)
            return input_line_id.display_name
        except:
            _logger.warning('[QR] Cannot question %s', fields_name)
            return False

    def get_much_value(self, fields_name):
        try:
            input_line_id = self.user_input_line_ids.filtered(lambda i: i.question_id.fields_id.name == fields_name)
            seminars = False
            if input_line_id:
                seminars = ' '.join([str(question_id.display_name) for question_id in input_line_id])
            return seminars
        except:
            _logger.warning('[QR] Cannot question %s', fields_name)
            return False
