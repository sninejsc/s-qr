# -*- coding: utf-8 -*-


{
    'name': "Contact QRCode",
    'author': 'SNine',
    'company': 'SNine',
    'maintainer': 'SNine',
    'website': "https://www.snine.vn",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'contacts', 'survey', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/qr_booth_access.xml',
        'views/contact_view.xml',
        'views/survey_view.xml',
        'views/survey_user_input_view.xml',
        'views/qr_booth_view.xml',
        'views/qr_booth_line_view.xml',
        'views/sne_survey_templates.xml',
        'views/sne_webclient_templates.xml',
        'views/login_templates.xml',
        'views/survey_question_view.xml',
        'views/success_login.xml',
        'wizard/import_contact_view.xml',
        'data/qr_booth_data.xml',
        'data/partner_category_data.xml',
        'data/survey_question_data.xml',
        'report/template_qr_code_view.xml',
        'report/email_qr_code.xml',
        'views/menuitem.xml',
    ],

    'assets': {
        'survey.survey_assets': [
            's_contact/static/src/scss/custom_survey.scss',
        ],
    }
}
