from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import logging
from urllib.parse import urlparse

_logger = logging.getLogger(__name__)


class QrBooth(models.Model):
    _name = 'qr.booth'
    _description = 'Booth'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('unique_booth_line', 'unique(booth_id, partner_id)', 'Each partner should appear only once in booth lines!'),
    ]
    _rec_name = 'code'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    user_id = fields.Many2one('res.users', string='User')
    type = fields.Selection(selection=[('event_counter', 'Event Counter'), ('check_in_counter', 'Check-in Counter')],
                            string='Type', default='check_in_counter')
    partner_ids = fields.Many2many('res.partner', string='Partners', tracking=True)
    activate = fields.Boolean(string='Activate', default=True)
    booth_line_ids = fields.One2many('qr.booth.line', 'booth_id', string='Booth Lines', tracking=True)
    note = fields.Text(string='Note')
    total_partner_count = fields.Integer(string='Total Partners', compute='_compute_total_partner_count')
    booth_line_ids_change = fields.Char(
        string='Booth Lines Change',
        compute='_compute_booth_line_ids_change',
        store=True,
        track_visibility='onchange')
    qr_contact = fields.Many2one(comodel_name='res.partner', string='QR Code', domain=[('s_type', 'in', ['A', 'B'])])
    domain_check = fields.Char(string='QR Code')

    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('qr.booth.sequence') or _('New')
        result = super(QrBooth, self).create(vals)
        return result

    @api.depends('booth_line_ids')
    def _compute_total_partner_count(self):
        for booth in self:
            booth.total_partner_count = len(booth.booth_line_ids)

    @api.depends('booth_line_ids')
    def _compute_booth_line_ids_change(self):
        for record in self:
            booth_line_names = record.booth_line_ids.mapped('partner_id.name')
            record.booth_line_ids_change = ', '.join(booth_line_names)

    def action_check_in_out(self):
        if not self.domain_check:
            raise UserError(_("Please input the QR Code !"))

        parsed_url = urlparse(self.domain_check)
        path_segments = parsed_url.path.split('/')
        qr_contact = path_segments[-1]

        qr_contact = self.env['res.partner'].search([('qr_code', '=', qr_contact)])
        BoothLine = self.env['qr.booth.line']

        contact_in = BoothLine.search([('booth_id', '=', self.id), ('partner_id', '=', qr_contact.id)])
        if not contact_in:
            booth_line = BoothLine.create({
                'booth_id': self.id,
                'partner_id': qr_contact.id})
            self.write({'booth_line_ids': [(4, booth_line.id)]})
            _logger.info(f'[IN] Check-in booth {self.display_name}, with account {qr_contact.display_name}')

            self.domain_check = False
            return {
                'type': 'ir.actions.act_url',
                'target': 'fullscreen',
                'url': '/report/pdf/s_contact.qr_code_template/%s' % booth_line.partner_id.id,
            }
        else:
            contact_in.check_out = datetime.now()
            _logger.info(f'[OUT] Check-out booth {self.display_name}, with account {qr_contact.display_name}')
            self.domain_check = False

    @api.onchange('domain_check')
    def onchange_domain_check(self):
        booth_id = self._origin.id
        if self.type != 'check_in_counter' and booth_id:
            if not self.domain_check:
                raise UserError(_("Please input the QR Code !"))

            parsed_url = urlparse(self.domain_check)
            path_segments = parsed_url.path.split('/')
            qr_contact = path_segments[-1]

            contact = self.env['res.partner'].search([('qr_code', '=', qr_contact)])

            BoothLine = self.env['qr.booth.line']

            contact_in = BoothLine.search([('booth_id', '=', booth_id), ('partner_id', '=', contact.id)])
            if not contact_in:
                booth_line = BoothLine.create({
                    'booth_id': booth_id,
                    'partner_id': contact.id})
                self.write({'booth_line_ids': [(4, booth_line.id)]})
                self.domain_check = False
                _logger.info(f'[IN] Check-in booth {self.display_name}, with account {contact.display_name}')
            else:
                self.domain_check = False
                contact_in.check_out = datetime.now()
                _logger.info(f'[OUT] Check-out booth {self.display_name}, with account {contact.display_name}')
