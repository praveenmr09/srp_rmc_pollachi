# -*- coding: utf-8 -*-
#############################################################################

{
    'name': 'Petty Cash Management',
    'version': '16.0',
    'summary': """This module will helps you to give the Petty Cash Management.""",
    'description': "This module will helps you to give the Petty Cash Management.",
    'category': "Fleet",
    'author': 'AppsComp Widgets Pvt Ltd',
    'company': 'AppsComp Widgets Pvt Ltd',
    'website': "www.appscomp.com",
    'depends': ['base', 'account', 'fleet', 'mail', 'hr', 'contacts',],
    'data': [
        'security/ir.model.access.csv',
        'views/petty_cash_request.xml',
        'views/petty_cash_expense.xml',
    ],
    'demo': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
