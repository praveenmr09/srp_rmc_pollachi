# -*- coding: utf-8 -*-
#############################################################################

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning, ValidationError
import pytz


# WIZARD CLASS - FLEET TOLL ENTRY WIZARD
class FleetTollEntryWizard(models.TransientModel):
    _name = 'fleet.toll.entry.wizard'
    _description = 'Fleet Toll Entry Wizard'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    purchaser_id = fields.Many2one('res.partner', "Driver")
    driver_id = fields.Many2one('hr.employee', string='Driver',
                                domain="[('fleet_rental_driver', '=', True)]")

    def print_fleet_toll_entry(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'vehicle_id': self.vehicle_id.name,
            'driver_id': self.driver_id.name,
            'form': {
                'start_date': self.start_date,
                'end_date': self.end_date,
            },
        }
        return self.env.ref('apps_fleet_rental.view_fleet_toll_entry_report_record_menu').report_action(self, data=data)


class FleetTollEntryWizardParser(models.AbstractModel):
    _name = 'report.apps_fleet_rental.view_fleet_toll_entry_report_template'

    def _get_report_values(self, docids, data=None):
        start_date = data['start_date']
        end_date = data['end_date']
        vehicle_id = data['vehicle_id']
        driver_id = data['driver_id']

        local_timezone = pytz.timezone("Asia/Kolkata")
        # DOMAIN FOR VEHICLE WISE REPORT
        if vehicle_id:
            toll_details = self.env['fleet.toll.entry'].search([
                ('entry_date', '>=', start_date),
                ('entry_date', '<=', end_date),
                ('vehicle_id.name', '=', vehicle_id),

            ], order='entry_date asc')

            toll = []
            for i in toll_details:
                toll.append(i)

        # # DOMAIN FOR DRIVER WISE REPORT
        # if driver_id:
        #     toll_details = self.env['fleet.toll.entry'].search([
        #         ('entry_date', '>=', start_date),
        #         ('entry_date', '<=', end_date),
        #         ('driver_id.name', '=', driver_id),
        #
        #     ], order='entry_date asc')
        #
        #     toll = []
        #     for i in toll_details:
        #         toll.append(i)
        #
        # # DOMAIN FOR VEHICLE AND DRIVER WISE REPORT
        # if vehicle_id and driver_id:
        #     toll_details = self.env['fleet.toll.entry'].search([
        #         ('entry_date', '>=', start_date),
        #         ('entry_date', '<=', end_date),
        #         ('vehicle_id.name', '=', vehicle_id),
        #         ('driver_id.name', '=', driver_id),
        #
        #     ], order='entry_date asc')
        #
        #     toll = []
        #     for i in toll_details:
        #         toll.append(i)

        # DOMAIN FOR TAKING WITHOUT VEHICLE AND DRIVER REPORT
        else:
            toll_details = self.env['fleet.toll.entry'].search([
                ('entry_date', '>=', start_date),
                ('entry_date', '<=', end_date),

            ], order='entry_date asc')

            toll = []
            for i in toll_details:
                toll.append(i)

        cols_heads = ['S.No', 'Reference', 'Start journey', 'Entry station', 'Exit Station', 'Distance/km',
                      'Cost', 'Vehicle', 'Driver', 'Vendor']

        return {
            'doc_ids': docids,
            'doc_model': 'fleet.toll.entry.wizard',
            'data': toll,
            'cols_heads': cols_heads,
            'local_timezone': local_timezone,
        }
