# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import io
import xlrd
import logging
import tempfile
import binascii
from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning, UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class ImportContacts(models.TransientModel):
    _name = 'import.contact'
    _description = 'Import Contact'

    file_type = fields.Selection([('CSV', 'CSV File'), ('XLS', 'XLS File')], string='File Type', default='XLS')
    file = fields.Binary(string="Upload File")
    file_name = fields.Char(string="File Name")

    def process_imported_data(self, values):
        existing_contact = self.env['res.partner'].search([
            ('name', '=', values['name']),
            ('phone', '=', values['phone']),
            ('email', '=', values['email'])
        ])
        if not existing_contact:
            res = self.create_contact(values)
        else:
            self.update_contact(existing_contact, values)

    def import_contact(self):
        if not self.file:
            raise ValidationError(_("Please Upload File to Import Contact !"))

        if self.file_type == 'CSV':
            try:
                csv_data = base64.b64decode(self.file)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                file_reader = []
                csv_reader = csv.reader(data_file, delimiter=',')
                file_reader.extend(csv_reader)
            except Exception:
                raise ValidationError(_("Please Select Valid File Format !"))

            keys = ['title', 'name', 'phone', 'email', 'company_name', 'business_nature', 'department',
                    'function', 'country_id', 'seminars', 'question', 's_type']

            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                if values and i != 0:
                    self.process_imported_data(values)

        else:
            try:
                file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                file.write(binascii.a2b_base64(self.file))
                file.seek(0)
                values = {}
                workbook = xlrd.open_workbook(file.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise ValidationError(_("Please Select Valid File Format !"))

            for row_no in range(1,sheet.nrows):
                val = {}
                line = list(
                    map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value),
                        sheet.row(row_no)))

                values.update({
                    'title': line[0],
                    'name': line[1],
                    'phone': line[2],
                    'email': line[3],
                    'company_name': line[4],
                    'business_nature': line[5],
                    'department': line[6],
                    'function': line[7],
                    'country_id': line[8],
                    'seminars': line[9],
                    'question': line[10],
                })

                self.process_imported_data(values)

    def process_contact_data(self, values):
        title = self.env.ref('base.res_partner_title_madam')
        if values.get('title') == 'Mr.':
            title = self.env.ref('base.res_partner_title_mister')

        country = self.env.ref('base.vn')
        if values.get('country_id') == 'Chinese':
            country = self.env.ref('base.cn')

        vals = {
            'title': title.id,
            'name': values.get('name'),
            'phone': values.get('phone'),
            'email': values.get('email'),
            'company_name': values.get('company_name'),
            'business_nature': values.get('business_nature'),
            'department': values.get('department'),
            'function': values.get('function'),
            'country_id': country.id,
            'seminars': values.get('seminars'),
            'question': values.get('question'),
            'category_id': [(4, self.env.ref('s_contact.category_vip').id)],
            's_type': 'A',
        }

        if not values.get('name'):
            raise UserError(_('Contact Name is Required !'))

        return vals

    def create_contact(self, values):
        contact = self.env['res.partner']
        vals = self.process_contact_data(values)
        res = contact.create(vals)
        return res

    def update_contact(self, existing_contact, values):
        vals = self.process_contact_data(values)
        existing_contact.write(vals)

    def get_address(self, name):
        address = self.env['res.partner'].search([('name', '=', name)], limit=1)
        if not address:
            raise UserError(_('"%s" Address is not found in system !') % name)
        return address

    def get_contract_template(self):
        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': '/s_contact/static/src/template_import/Template_import.xlsx',
        }
