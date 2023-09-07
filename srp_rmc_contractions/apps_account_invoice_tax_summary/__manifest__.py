# -*- coding: utf-8 -*-
{
    'name': 'Account Move Tax Summary',
    'summary': 'Account Move Tax Summary',
    'description': """Show the summary of the taxes selected in the invoice order lines.""",
    'author': "AppsComp Widgets Pvt Ltd",
    'website': "https://www.appscomp.com",
    'license': 'AGPL-3',
    'category': 'Accounting',
    'version': '15.0.1.0.0',
    'depends': ['account'],
    'data': [
        "security/ir.model.access.csv",
        'views/account_move_views.xml',

    ],
    'installable': True,
    'auto_install': False,
}
