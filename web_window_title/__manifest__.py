# -*- coding: utf-8 -*-
{
    'name': "Web Window Title",
    'summary': "The custom web window title",
    'author': "S-Nine",
    'website': "https://snine.vn",
    'support': 'support@snine.vn',
    'category': 'Extra Tools',
    'version': '1.1',
    'license': 'LGPL-3',
    'depends': ['base_setup'],
    'demo': [
        'data/demo.xml',
    ],
    'data': [
        'views/res_config.xml',
    ],
    'images': [
        'static/description/main_screenshot.png',
    ],
    'assets': {
        'web.assets_backend': [
            'web_window_title/static/src/js/web_window_title.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
