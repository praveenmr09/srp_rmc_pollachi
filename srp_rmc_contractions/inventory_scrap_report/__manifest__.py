# -*- coding: utf-8 -*-
#############################################################################

{
    'name': 'Inventry Scrap Report',
    'version': '16.0',
    'summary': """This module will helps you to give the vehicles for Rent.""",
    'description': "This module will helps you to give the vehicles for Rent.",
    'category': "Fleet",
    'author': 'AppsComp Widgets Pvt Ltd',
    'company': 'AppsComp Widgets Pvt Ltd',
    'website': "www.appscomp.com",
    'depends': ['base', 'stock', ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/vehicle_registration_info_pdf_report.xml',
    ],
    'demo': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
