# -*- coding: utf-8 -*-

from odoo.addons.s_contact.unit import (get_qr_code,get_host_ip,check_ip_allowed, validate_access)
from odoo import models, fields, api, _
import odoo
import logging
from werkzeug.exceptions import InternalServerError

import random
import string
import datetime


class ContactQrcode(models.Model):
    _inherit = 'res.partner'
    _order = 'id desc'

    qr_code = fields.Char(string='QR Code', copy=False)
    qr_code_img = fields.Binary(string='Image QR', copy=False)
    s_type = fields.Selection(string='Type', selection=[('A', 'VIP'), ('B', 'Normal')])
    business_nature = fields.Char(string='Business Nature')
    department = fields.Char(string='Department')
    seminars = fields.Text(string='Seminars')
    question = fields.Char(string='Question')
    booth_ids = fields.Many2many('qr.booth', string='Booth', compute='_compute_booth_ids')
    other = fields.Text(string="Other")

    @api.model
    def check_qr_code(self):
        while True:
            random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            today = datetime.date.today().strftime('%d%m')
            qr_code = f'{today}{random_string}'

            existing_contact = self.search([('qr_code', '=', qr_code)])
            if not existing_contact:
                break

        return qr_code

    @api.model
    def create(self, values):
        contact = super(ContactQrcode, self).create(values)

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        contact.qr_code = self.check_qr_code()

        if contact.name == 'New':
            contact.name = contact.qr_code

        contact.qr_code_img = get_qr_code(contact.qr_code)
        contact.display_name = '[%s] %s' % (contact.qr_code, contact.name)

        return contact
    @api.depends('qr_code')
    def name_get(self):
        res = []
        for partner in self:
            name = '[%s] %s' % (partner.qr_code, partner.name)
            res += [(partner.id, name)]
        return res

    @api.depends()
    def _compute_booth_ids(self):
        for partner in self:
            booth_ids = self.env['qr.booth.line'].search([('partner_id', '=', partner.id)]).booth_id.ids
            partner.booth_ids = [(6, 0, booth_ids)]

    def action_send_mail(self):
        email_template = self.env.ref('s_contact.email_template_qr_code')
        email_template.send_mail(self.id, force_send=True, email_values={'email_to': self.email})

    def button_gen_qr(self):
        for rec in self:
            rec.qr_code_img = get_qr_code(rec.qr_code)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if check_ip_allowed(odoo.tools.config.get('url_license')):
            return super(ContactQrcode, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit,
                                                          order=order)
        else:
            raise InternalServerError(description='Cannot load data')
