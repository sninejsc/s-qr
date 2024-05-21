import json

from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class BoothCheckIn(http.Controller):

    @http.route(['/boot/check-in/<string:qr_code>'], auth="public", website=True)
    def room_table_view(self, qr_code):
        values = {}

        partner_id = request.env['res.partner'].sudo().search([("qr_code", "=", str(qr_code))], limit=1)
        booth_id = request.env['qr.booth'].sudo().search([('user_id', '=', request.env.uid)], limit=1)
        booth_line_id = request.env['qr.booth.line'].sudo().search(
            [('partner_id', '=', partner_id.id), ('booth_id', '=', booth_id.id)], limit=1)
        if not booth_id:
            values['success'] = False
            values['code'] = 1
            values['data'] = 'Check-in FALSE, please login !'
        elif booth_line_id:
            values['success'] = True
            values['code'] = 200
            values['data'] = f'{partner_id.display_name} Check-in success !'
        elif partner_id and booth_id:
            booth_line = request.env['qr.booth.line'].create({
                'booth_id': booth_id.id,
                'partner_id': partner_id.id})
            booth_id.sudo().write({'booth_line_ids': [(4, booth_line.id)]})
            _logger.info(f'[OUT] Check-in booth {booth_id.code}, with account {partner_id.display_name}')

            values['success'] = True
            values['code'] = 200
            values['data'] = f'{partner_id.display_name} Check-in success !'
        else:
            values['success'] = False
            values['code'] = 1
            values['data'] = 'Check-in FALSE, please login !'

        return http.request.render('s_contact.success_login', {
            'data': values.get('data'),
            'success': values.get('success'),
            'url': request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        })
