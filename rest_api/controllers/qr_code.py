# -*- coding: utf-8 -*-
from odoo.addons.rest_api.controllers.main import *
from werkzeug.wrappers import Response
from datetime import datetime
import pytz

vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')


class ControllerREST(http.Controller):

    @http.route('/api/res.users', methods=['POST'], type='http', auth='none', cors=rest_cors_value, csrf=False)
    @check_permissions
    def api_model_res_users_POST(self, **kw):
        data = json.loads(request.httprequest.data)
        register_token = data.get("register_token")
        if not register_token:
            return error_response(400, 'Error', 'Register token is required!')
        company_id = http.request.env.ref('base.main_company')
        token = company_id.token_register_account
        if not token or token != register_token:
            return error_response(400, 'Error', 'Token is invalid!')

        name, email, password = data.get('name'), data.get(
            'email'), data.get('password')
        if not name or not email or not password:
            return error_response(400, 'Error', 'All fields must be filled out!')
        user_obj = request.env['res.users'].with_user(SUPERUSER_ID)

        already_email = user_obj.search([("login", "=", email)])

        if already_email:
            return error_response(400, 'Error', 'Account already exists!')

        access_token = user_obj.create_by_api(
            name, email, password, company_id)
        return successful_response(201, {'success': True, 'access_token': access_token})

    @http.route('/api/booth/', methods=['GET'], type='http', auth='none', cors=rest_cors_value)
    @check_permissions
    def api_booth_GET(self, **kw):
        uid = request.context.get('uid')
        booths = request.env['qr.booth'].search([('user_id', '=', uid)])
        response_data = {
            'booths': [{'booth_id': booth.id, 'name': booth.name, 'code': booth.code} for booth in booths]
        }

        return Response(json.dumps(response_data), content_type='application/json')

    @http.route('/api/checkin_out', methods=['POST'], type='http', auth='none', cors=rest_cors_value, csrf=False)
    @check_permissions
    def api_booth_checkin(self, **kw):
        uid = request.context.get('uid')
        if not uid:
            return self._error_response("User not exit")

        try:
            data = json.loads(request.httprequest.data)
            if 'qr_code' not in data or 'booth_id' not in data:
                return Response(json.dumps({'error': 'Error value in body'}), status=400,
                                content_type='application/json')
            booth = request.env['qr.booth'].sudo().search(
                [('user_id', '=', uid), ('id', '=', data.get('booth_id'))])
            if not booth:
                return self._error_response("User isn't allowed to be in this booth")

            partner_id = request.env['res.partner'].sudo().search(
                [('qr_code', '=', data.get('qr_code'))], limit=1)

            booth_line = request.env['qr.booth.line'].sudo().search([
                ('booth_id', '=', int(data.get('booth_id'))),
                ('partner_id', '=', partner_id.id)
            ])
            date_time = datetime.now(vn_tz).strftime('%Y-%m-%d %H:%M:%S')
            if booth_line:
                booth_line.check_out = date_time
                return self._success_response(partner_id.name, str(date_time), 'checkout')
            request.env['qr.booth.line'].sudo().create({
                'booth_id': int(data.get('booth_id')),
                'partner_id': partner_id.id,
                'check_in': date_time
            })

            return self._success_response(partner_id.name, str(date_time), 'checkin')

        except Exception as e:
            return self._error_response(f"err: {str(e)}")

    def _success_response(self, message, date_time, status):
        response_data = {
            'success': True,
            'message': message,
            'status': status,
            'date_time': date_time
        }
        return Response(json.dumps(response_data, indent=4), status=200, content_type='application/json')

    def _error_response(self, error):
        response_data = {
            'success': False,
            'error': error,
            'status': False,
            'date_time': False
        }
        return json.dumps(response_data, indent=4)

    @http.route('/api/contact_booth/<int:booth_id>', methods=['GET', 'POST'], type='http', auth='none', cors=rest_cors_value)
    @check_permissions
    def partner_of_booth(self, booth_id, **kw):
        try:
            booth_id = request.env['qr.booth'].sudo().search(
                [('id', '=', booth_id)])
            contact_list = [
                {
                    'code': line.partner_id.qr_code,
                    'name': line.partner_id.name,
                    'check_in': str(line.check_in),
                    'check_out': str(line.check_out)
                }
                for line in booth_id.booth_line_ids
            ]
            response_data = {
                'booth_id': booth_id.id,
                'contact_list': contact_list
            }

            return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            return error_response(400, 'Error', e)
