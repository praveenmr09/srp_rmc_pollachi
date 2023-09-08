# -*- coding: utf-8 -*-
#############################################################################

{
    'name': 'Fleet Rental Management',
    'version': '16.0',
    'summary': """This module will helps you to give the vehicles for Rent.""",
    'description': "This module will helps you to give the vehicles for Rent.",
    'category': "Fleet",
    'author': 'AppsComp Widgets Pvt Ltd',
    'company': 'AppsComp Widgets Pvt Ltd',
    'website': "www.appscomp.com",
    'depends': ['base', 'account', 'fleet', 'mail', 'hr', 'contacts', 'om_hr_payroll'],
    'data': [
        'data/fleet_rental_data.xml',
        'security/rental_security.xml',
        'security/ir.model.access.csv',
        'reports/rental_report.xml',
        'reports/fuel_tank_monitoring_report.xml',
        'wizard/driver_vehicle_history_view.xml',
        'wizard/apply_rent_contract_alter_charges_view.xml',
        'wizard/driver_history_vehicle_report_pdf.xml',
        # 'wizard/fleet_toll_entry_wizard.xml',
        'wizard/rental_vehicle_trip_wizard.xml',
        'wizard/rental_vehicle_trip_pdf_report.xml',
        'wizard/odometer_wizard.xml',
        'wizard/vehicle_registration_info_wizard.xml',
        'wizard/vehicle_registration_info_pdf_report.xml',
        'views/apps_fleet_rental_view.xml',
        'views/fleet_rental_checklist_view.xml',
        # 'views/fleet_rental_tools_view.xml',
        'views/account_move_view.xml',
        'views/fleet_toll_entry.xml',
        'views/hr_payslip_extended.xml',

    ],
    'demo': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
