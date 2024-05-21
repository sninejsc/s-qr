from odoo import models, fields


class QRBoothLine(models.Model):
    _name = 'qr.booth.line'
    _description = 'Booth Line'
    _rec_name = 'booth_id'

    booth_id = fields.Many2one('qr.booth', string='Booth', required=True)
    s_type = fields.Selection(related='partner_id.s_type')
    partner_id = fields.Many2one('res.partner', string='Partners',
                                 domain=[('s_type', 'in', ['A', 'B'])], required=True)
    check_in = fields.Datetime(string='Check-In', default=lambda self: fields.Datetime.now())
    check_out = fields.Datetime(string='Check-Out')

    def action_print_qr(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'fullscreen',
            'url': '/report/pdf/s_contact.qr_code_template/%s' % self.partner_id.id,
        }
