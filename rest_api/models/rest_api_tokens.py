
import time
import sys
from odoo import models, fields, api

_is_used_simple_token_store = sys.modules.get('odoo.addons.rest_api.controllers.simple_token_store')


class RestApiAccessToken(models.Model):
    _name = "rest.api.access.token"
    
    access_token = fields.Char(index=True)
    user_id = fields.Integer()
    expiry_time = fields.Float(index=True)
    
    @api.model
    def _cron_delete_expired_tokens(self):
        if _is_used_simple_token_store:
            self.delete_expired_tokens_in_table('access')
            self.delete_expired_tokens_in_table('refresh')
    
    def delete_expired_tokens_in_table(self, table):
        model_name = 'rest.api.' + table + '.token'
        current_time = time.time()
        expired_tokens = self.env[model_name].sudo().search([('expiry_time', '<', current_time)])
        if expired_tokens:
            expired_tokens.unlink()


class RestApiRefreshToken(models.Model):
    _name = "rest.api.refresh.token"
    
    refresh_token = fields.Char(index=True)
    access_token = fields.Char()
    user_id = fields.Integer()
    expiry_time = fields.Float(index=True)
