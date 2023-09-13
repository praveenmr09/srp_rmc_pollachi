from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning, ValidationError
import xlwt
from io import BytesIO
import base64
import itertools
from operator import itemgetter
from odoo.exceptions import Warning
from odoo import tools
from xlwt import easyxf
import datetime
from odoo.exceptions import UserError
from datetime import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pdb

cell = easyxf('pattern: pattern solid, fore_colour yellow')
ADDONS_PATH = tools.config['addons_path'].split(",")[-1]

MONTH_LIST = [('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'),
              ('4', 'Apr'), ('5', 'May'), ('6', 'Jun'),
              ('7', 'Jul'), ('8', 'Aug'), ('9', 'Sep'),
              ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec')]


# WIZARD CLASS - ADD FUEL HISTORY WIZARD
class AddFuelHistoryWizard(models.TransientModel):
    _name = 'add.fuel.history.wizard'
    _description = 'Add Fuel History Wizard'

    last_odometer = fields.Float(string='Last Odometer')
    unit = fields.Selection([
        ('km', 'km'),
        ('m', 'm'),
    ], string='Unit', default='km')
    filling_date = fields.Date(string='Filling Date', default=fields.Date.today())
    fuel = fields.Float(string='Fuel')
    fuel_receipt = fields.Binary(string="Fuel receipt")
    fuel_cost = fields.Float(string='Fuel Cost')
    fueled_by = fields.Many2one('res.users', string='Fueled By')
    fuel_history = fields.Many2one('fuel.history', string='Fuel History')
    fleet_vehicle_add_id = fields.Many2one('fleet.vehicle', string='Fuel History')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle List')
    rent_contract_ref = fields.Char(string="Reference")
    hide_status = fields.Selection([
        ('hide_in_car_rental', 'Hide CR'),
        ('hide_in_fleet_vehicle', 'Hide FV'),
    ], string='Hide Status')

    def add_fuel(self):
        if self.last_odometer <= 0.00:
            raise ValidationError("Alert, Mr. %s.\nThe Last Odometer should "
                                  "not be Zero, Kindly Check it" % self.env.user.name)
        if self.fuel <= 0.00:
            raise ValidationError("Alert, Mr. %s.\nThe Fuel should "
                                  "not be Zero, Kindly Check it" % self.env.user.name)
        if self.fuel_cost <= 0.00:
            raise ValidationError("Alert, Mr. %s.\nThe Fuel Cost should "
                                  "not be Zero, Kindly Check it" % self.env.user.name)

        for update_fuel in self.env['fleet.vehicle'].search([]):
            fuel_history_line_vals = {
                'fuel': self.fuel,
                'fuel_cost': self.fuel_cost,
                'fueled_by': self.fueled_by.id,
                'last_odometer': self.last_odometer,
                'unit': self.unit,
                'fuel_receipt': self.fuel_receipt,
                'filling_date': self.filling_date,
            }

            if update_fuel.license_plate == self.vehicle_id.license_plate:
                fuel_history = self.env['fuel.history'].create(fuel_history_line_vals)
                update_fuel.write({'fuel_history_ids': [(4, fuel_history.id)]})

    def add_fuel_in_rental_contract(self):
        self.vehicle_id.write({
            'fuel': self.fuel,
            'fuel_cost': self.fuel_cost,
        })
        for update_fuel in self.env['fleet.vehicle'].search([]):
            fuel_history_line_vals = {
                'fuel': self.fuel,
                'fuel_cost': self.fuel_cost,
                'fueled_by': self.fueled_by.id,
                'last_odometer': self.last_odometer,
                'unit': self.unit,
                'fuel_receipt': self.fuel_receipt,
                'filling_date': self.filling_date,
                'reference': self.rent_contract_ref,
            }

            if update_fuel.license_plate == self.vehicle_id.license_plate:
                rental_line = self.env['fuel.history'].create(fuel_history_line_vals)
                update_fuel.write({'fuel_history_ids': [(4, rental_line.id)]})


# WIZARD CLASS DRIVER VEHICLE HISTORY WIZARD
class DriverVehicleHistoryWizard(models.TransientModel):
    _name = 'driver.vehicle.history.wizard'
    _description = 'Driver Vehicle History Wizard'

    start_date = fields.Date('Start date', required=True)
    end_date = fields.Date('End date', required=True)
    attachment = fields.Binary('File')
    attach_name = fields.Char('Attachment Name')
    summary_file = fields.Binary('Fleet Vehicle  Usage Report')
    file_name = fields.Char('File Name')
    report_printed = fields.Boolean('Fleet Vehicle  Usage Report')
    current_time = fields.Date('Current Time', default=lambda self: fields.Datetime.now())
    ams_time = datetime.now() + timedelta(hours=5, minutes=30)
    date = ams_time.strftime('%d-%m-%Y %H:%M:%S')
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    vehicle_list = fields.Many2many('fleet.vehicle', string="Vehicle")
    driver_name = fields.Many2many('hr.employee', string='Driver Name')
    requested = fields.Boolean('Request ?')

    vehicle_category = fields.Selection([
        ('car', 'Car'),
        ('bike', 'Bike'),
        ('truck', 'Truck'),
    ], string='Vehicle Category')

    type_of_vehicle = fields.Selection([
        ('company', 'Company Owned'),
        ('employee', 'Employee Owned'),
        ('rental', 'Rental'),
    ], string='Vehicle Type')

    def print_driver_history_wizard_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            's_date': self.start_date,
            'e_date': self.end_date,
            'vehicle_ids': self.vehicle_list.ids,
            'driver_ids': self.driver_name.ids,
            'form': {
                'start_date': self.start_date,
                'end_date': self.end_date,
            },
        }
        return self.env.ref('apps_fleet_rental.record_driver_history_pdf').report_action(self, data=data)

    def action_get_driver_vehicle_history_report(self):
        workbook = xlwt.Workbook()
        worksheet1 = workbook.add_sheet('Fleet Vehicle  Usage Report')

        design_6 = easyxf('align: horiz left;font: bold 1;')
        design_7 = easyxf('align: horiz center;font: bold 1;')
        design_8 = easyxf('align: horiz left;')
        design_9 = easyxf('align: horiz right;')
        design_10 = easyxf('align: horiz right; pattern: pattern solid, fore_colour red;')
        design_11 = easyxf('align: horiz right; pattern: pattern solid, fore_colour green;')
        design_12 = easyxf('align: horiz right; pattern: pattern solid, fore_colour gray25;')
        design_13 = easyxf('align: horiz center;font: bold 1;pattern: pattern solid, fore_colour gray25;')
        design_14 = easyxf('align: horiz left;font: bold 1;pattern: pattern solid, fore_colour gray25;')
        design_15 = easyxf('align: horiz right;font: bold 1;')
        design_16 = easyxf('align: horiz right;font: bold 1;pattern: pattern solid, fore_colour gray25;')

        worksheet1.col(0).width = 1800
        worksheet1.col(1).width = 4300
        worksheet1.col(2).width = 6000
        worksheet1.col(3).width = 4000
        worksheet1.col(4).width = 5000
        worksheet1.col(5).width = 4800
        worksheet1.col(6).width = 4800
        worksheet1.col(7).width = 4300
        worksheet1.col(8).width = 4800
        worksheet1.col(9).width = 3500
        worksheet1.col(10).width = 3500
        worksheet1.col(11).width = 3500
        worksheet1.col(12).width = 3500
        worksheet1.col(13).width = 5000
        worksheet1.col(14).width = 5000
        worksheet1.col(15).width = 5000

        rows = 0
        cols = 0
        row_pq = 5

        worksheet1.set_panes_frozen(True)
        worksheet1.set_horz_split_pos(rows + 1)
        worksheet1.set_remove_splits(True)

        col_1 = 0
        worksheet1.write_merge(rows, rows, 2, 6, 'Vehicle Driver History Report', design_13)
        rows += 1
        worksheet1.write(rows, 3, 'START DATE', design_14)
        worksheet1.write(rows, 4, self.start_date.strftime('%d-%m-%Y'), design_7)
        rows += 1
        worksheet1.write(rows, 3, 'END DATE', design_14)
        worksheet1.write(rows, 4, self.end_date.strftime('%d-%m-%Y'), design_7)
        rows += 1
        if self.type_of_vehicle:
            worksheet1.write(rows, 3, 'TYPE OF VEHICLE', design_14)
            worksheet1.write(rows, 4, self.type_of_vehicle, design_7)
            rows += 1
        # worksheet1.write(rows, 3, 'VEHICLE CATEGORY', design_14)
        # worksheet1.write(rows, 4, self.vehicle_category, design_7)
        # rows += 1
        worksheet1.write(rows, 3, 'GENERATED BY', design_14)
        worksheet1.write(rows, 4, self.user_id.name, design_7)
        if self.vehicle_category:
            worksheet1.write(rows, 6, 'VEHICLE CATEGORY', design_14)
            worksheet1.write(rows, 7, self.vehicle_category, design_7)
        rows += 1
        worksheet1.write(rows, col_1, _('Sl.No'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Rental Date'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('SOURCE'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('DESTINATION'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('DRIVER NAME'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('REFERENCE'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('PURPOSE'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('VEHICLE NO'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('DURATION'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('STARTING KM'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('TOTAL KM'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Rate/KM'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Subtotal'), design_13)
        col_1 += 1

        sl_no = 1
        row_pq = row_pq + 1
        mr_num = []
        res = []
        for record in self:
            domain = [
                ('start_date', '>=', record.start_date),
                ('end_date', '<=', record.end_date),
                ('vehicle_id', '=', record.vehicle_list.ids),
                ('driver_employee_id', '=', record.driver_name.ids),
            ]
            total_subtotal = 0.00
            total_km = 0.00
            import datetime
            domain = [
                ('date_start', '>=', record.start_date),
                ('date_end', '<=', record.end_date),
            ]
            domain1 = [
                ('date_start', '>=', record.start_date),
                ('date_end', '<=', record.end_date),
                ('vehicle_id', '=', record.vehicle_list.ids)]
            domain2 = [
                ('date_start', '>=', record.start_date),
                ('date_end', '<=', record.end_date),
                ('driver_id', '=', record.driver_name.ids)]
            domain3 = [
                ('date_start', '>=', record.start_date),
                ('date_end', '<=', record.end_date),
                ('driver_id', '=', record.driver_name.ids),
                ('vehicle_id', '=', record.vehicle_list.ids)]

            # DRIVER VEHICLE HISTORY REPORT WILL GENERATE AS PER DOMAIN

            if (record.start_date and record.end_date
                    and not record.vehicle_list and not record.driver_name):
                vehicle_history = record.env['fleet.vehicle.assignation.log'].sudo().search(
                    domain, order='date_start asc')
                for log in vehicle_history:
                    start_date = record.start_date
                    end_date = record.end_date
                    import datetime
                    d11 = str(start_date)
                    dt21 = datetime.datetime.strptime(d11, '%Y-%m-%d')
                    fleet_start_date = dt21.strftime("%d/%m/%Y")
                    d22 = str(end_date)
                    dt22 = datetime.datetime.strptime(d22, '%Y-%m-%d')
                    fleet_end_date = dt22.strftime("%d/%m/%Y")
                    worksheet1.write(row_pq, 0, sl_no, design_7)
                    worksheet1.write(row_pq, 1, fleet_start_date, design_8)
                    if log.source_city:
                        worksheet1.write(row_pq, 2, log.source_city, design_8)
                    else:
                        worksheet1.write(row_pq, 2, '-', design_7)

                    if log.destination_city:
                        worksheet1.write(row_pq, 3, log.destination_city, design_8)
                    else:
                        worksheet1.write(row_pq, 3, '-', design_7)
                    if log.driver_employee_id:
                        worksheet1.write(row_pq, 4, log.driver_employee_id.name, design_8)
                    else:
                        worksheet1.write(row_pq, 4, '-', design_7)

                    if log.rental_contract_reference:
                        worksheet1.write(row_pq, 5, log.rental_contract_reference, design_8)
                    else:
                        worksheet1.write(row_pq, 5, '-', design_7)

                    if log.purpose_of_rental_contract:
                        worksheet1.write(row_pq, 6, log.purpose_of_rental_contract, design_8)
                    else:
                        worksheet1.write(row_pq, 6, '-', design_7)
                    if log.vehicle_id:
                        worksheet1.write(row_pq, 7, log.vehicle_id.license_plate, design_8)
                    else:
                        worksheet1.write(row_pq, 7, '-', design_7)
                    if log.duration:
                        worksheet1.write(row_pq, 8, log.duration, design_9)
                    else:
                        worksheet1.write(row_pq, 8, '-', design_7)
                    if log.starting_km:
                        starting_km = log.total_km - log.vehicle_id.odometer
                        worksheet1.write(row_pq, 9, starting_km, design_9)
                    else:
                        worksheet1.write(row_pq, 9, '-', design_7)
                    if log.total_km:
                        total_km += log.total_km
                        worksheet1.write(row_pq, 10, log.total_km, design_9)
                    else:
                        worksheet1.write(row_pq, 10, '-', design_7)
                    if log.rate_per_km:
                        worksheet1.write(row_pq, 11, log.rate_per_km, design_15)
                    else:
                        worksheet1.write(row_pq, 11, '-', design_7)
                    if log.rate_per_km:
                        total_cost = log.rate_per_km * log.total_km
                        total_subtotal += total_cost
                        worksheet1.write(row_pq, 12, '%.2f' % total_cost, design_15)
                    else:
                        worksheet1.write(row_pq, 12, '-', design_7)
                    sl_no += 1
                    row_pq += 1
                worksheet1.write(row_pq + 1, 9, 'TOTAL', design_16)
                worksheet1.write(row_pq + 1, 10, '%.2f' % total_km, design_16)
                worksheet1.write(row_pq + 1, 12, '%.2f' % total_subtotal, design_16)
                # DRIVER VEHICLE HISTORY REPORT WILL GENERATE AS PER DOMAIN1
            if (record.start_date and record.end_date
                    and record.vehicle_list and not record.driver_name):
                vehicle_history = record.env['fleet.vehicle.assignation.log'].sudo().search(
                    domain1, order='date_start asc')
                for log in vehicle_history:
                    start_date = record.start_date
                    end_date = record.end_date
                    import datetime
                    d11 = str(start_date)
                    dt21 = datetime.datetime.strptime(d11, '%Y-%m-%d')
                    fleet_start_date = dt21.strftime("%d/%m/%Y")
                    d22 = str(end_date)
                    dt22 = datetime.datetime.strptime(d22, '%Y-%m-%d')
                    fleet_end_date = dt22.strftime("%d/%m/%Y")
                    worksheet1.write(row_pq, 0, sl_no, design_7)
                    worksheet1.write(row_pq, 1, fleet_start_date, design_8)
                    if log.source_city:
                        worksheet1.write(row_pq, 2, log.source_city, design_8)
                    else:
                        worksheet1.write(row_pq, 2, '-', design_7)

                    if log.destination_city:
                        worksheet1.write(row_pq, 3, log.destination_city, design_8)
                    else:
                        worksheet1.write(row_pq, 3, '-', design_7)
                    if log.driver_employee_id:
                        worksheet1.write(row_pq, 4, log.driver_employee_id.name, design_8)
                    else:
                        worksheet1.write(row_pq, 4, '-', design_7)

                    if log.rental_contract_reference:
                        worksheet1.write(row_pq, 5, log.rental_contract_reference, design_8)
                    else:
                        worksheet1.write(row_pq, 5, '-', design_7)

                    if log.purpose_of_rental_contract:
                        worksheet1.write(row_pq, 6, log.purpose_of_rental_contract, design_8)
                    else:
                        worksheet1.write(row_pq, 6, '-', design_7)
                    if log.vehicle_id:
                        worksheet1.write(row_pq, 7, log.vehicle_id.license_plate, design_8)
                    else:
                        worksheet1.write(row_pq, 7, '-', design_7)
                    if log.duration:
                        worksheet1.write(row_pq, 8, log.duration, design_9)
                    else:
                        worksheet1.write(row_pq, 8, '-', design_7)
                    if log.starting_km:
                        starting_km = log.total_km - log.vehicle_id.odometer
                        worksheet1.write(row_pq, 9, starting_km, design_9)
                    else:
                        worksheet1.write(row_pq, 9, '-', design_7)
                    if log.total_km:
                        total_km += log.total_km
                        worksheet1.write(row_pq, 10, log.total_km, design_9)
                    else:
                        worksheet1.write(row_pq, 10, '-', design_7)
                    if log.rate_per_km:
                        worksheet1.write(row_pq, 11, log.rate_per_km, design_15)
                    else:
                        worksheet1.write(row_pq, 11, '-', design_7)
                    if log.rate_per_km:
                        total_cost = log.rate_per_km * log.total_km
                        total_subtotal += total_cost
                        worksheet1.write(row_pq, 12, '%.2f' % total_cost, design_15)
                    else:
                        worksheet1.write(row_pq, 12, '-', design_7)
                    sl_no += 1
                    row_pq += 1
                worksheet1.write(row_pq + 1, 9, 'TOTAL', design_16)
                worksheet1.write(row_pq + 1, 10, '%.2f' % total_km, design_16)
                worksheet1.write(row_pq + 1, 12, '%.2f' % total_subtotal, design_16)
                # DRIVER VEHICLE HISTORY REPORT WILL GENERATE AS PER DOMAIN2
            if (record.start_date and record.end_date
                    and record.driver_name and not record.vehicle_list):
                vehicle_history = record.env['fleet.vehicle.assignation.log'].sudo().search(
                    domain2, order='date_start asc')
                for log in vehicle_history:
                    start_date = record.start_date
                    end_date = record.end_date
                    import datetime
                    d11 = str(start_date)
                    dt21 = datetime.datetime.strptime(d11, '%Y-%m-%d')
                    fleet_start_date = dt21.strftime("%d/%m/%Y")
                    d22 = str(end_date)
                    dt22 = datetime.datetime.strptime(d22, '%Y-%m-%d')
                    fleet_end_date = dt22.strftime("%d/%m/%Y")
                    worksheet1.write(row_pq, 0, sl_no, design_7)
                    worksheet1.write(row_pq, 1, fleet_start_date, design_8)
                    if log.source_city:
                        worksheet1.write(row_pq, 2, log.source_city, design_8)
                    else:
                        worksheet1.write(row_pq, 2, '-', design_7)

                    if log.destination_city:
                        worksheet1.write(row_pq, 3, log.destination_city, design_8)
                    else:
                        worksheet1.write(row_pq, 3, '-', design_7)
                    if log.driver_employee_id:
                        worksheet1.write(row_pq, 4, log.driver_employee_id.name, design_8)
                    else:
                        worksheet1.write(row_pq, 4, '-', design_7)

                    if log.rental_contract_reference:
                        worksheet1.write(row_pq, 5, log.rental_contract_reference, design_8)
                    else:
                        worksheet1.write(row_pq, 5, '-', design_7)

                    if log.purpose_of_rental_contract:
                        worksheet1.write(row_pq, 6, log.purpose_of_rental_contract, design_8)
                    else:
                        worksheet1.write(row_pq, 6, '-', design_7)
                    if log.vehicle_id:
                        worksheet1.write(row_pq, 7, log.vehicle_id.license_plate, design_8)
                    else:
                        worksheet1.write(row_pq, 7, '-', design_7)
                    if log.duration:
                        worksheet1.write(row_pq, 8, log.duration, design_9)
                    else:
                        worksheet1.write(row_pq, 8, '-', design_7)
                    if log.starting_km:
                        starting_km = log.total_km - log.vehicle_id.odometer
                        worksheet1.write(row_pq, 9, starting_km, design_9)
                    else:
                        worksheet1.write(row_pq, 9, '-', design_7)
                    if log.total_km:
                        total_km += log.total_km
                        worksheet1.write(row_pq, 10, log.total_km, design_9)
                    else:
                        worksheet1.write(row_pq, 10, '-', design_7)
                    if log.rate_per_km:
                        worksheet1.write(row_pq, 11, log.rate_per_km, design_15)
                    else:
                        worksheet1.write(row_pq, 11, '-', design_7)
                    if log.rate_per_km:
                        total_cost = log.rate_per_km * log.total_km
                        total_subtotal += total_cost
                        worksheet1.write(row_pq, 12, '%.2f' % total_cost, design_15)
                    else:
                        worksheet1.write(row_pq, 12, '-', design_7)
                    sl_no += 1
                    row_pq += 1
                worksheet1.write(row_pq + 1, 9, 'TOTAL', design_16)
                worksheet1.write(row_pq + 1, 10, '%.2f' % total_km, design_16)
                worksheet1.write(row_pq + 1, 12, '%.2f' % total_subtotal, design_16)
                # DRIVER VEHICLE HISTORY REPORT WILL GENERATE AS PER DOMAIN3
            if (record.start_date and record.end_date
                    and record.driver_name and record.vehicle_list):
                vehicle_history = record.env['fleet.vehicle.assignation.log'].sudo().search(
                    domain3, order='date_start asc')
                for log in vehicle_history:
                    start_date = record.start_date
                    end_date = record.end_date
                    import datetime
                    d11 = str(start_date)
                    dt21 = datetime.datetime.strptime(d11, '%Y-%m-%d')
                    fleet_start_date = dt21.strftime("%d/%m/%Y")
                    d22 = str(end_date)
                    dt22 = datetime.datetime.strptime(d22, '%Y-%m-%d')
                    fleet_end_date = dt22.strftime("%d/%m/%Y")
                    worksheet1.write(row_pq, 0, sl_no, design_7)
                    worksheet1.write(row_pq, 1, fleet_start_date, design_8)
                    if log.source_city:
                        worksheet1.write(row_pq, 2, log.source_city, design_8)
                    else:
                        worksheet1.write(row_pq, 2, '-', design_7)

                    if log.destination_city:
                        worksheet1.write(row_pq, 3, log.destination_city, design_8)
                    else:
                        worksheet1.write(row_pq, 3, '-', design_7)
                    if log.driver_employee_id:
                        worksheet1.write(row_pq, 4, log.driver_employee_id.name, design_8)
                    else:
                        worksheet1.write(row_pq, 4, '-', design_7)

                    if log.rental_contract_reference:
                        worksheet1.write(row_pq, 5, log.rental_contract_reference, design_8)
                    else:
                        worksheet1.write(row_pq, 5, '-', design_7)

                    if log.purpose_of_rental_contract:
                        worksheet1.write(row_pq, 6, log.purpose_of_rental_contract, design_8)
                    else:
                        worksheet1.write(row_pq, 6, '-', design_7)
                    if log.vehicle_id:
                        worksheet1.write(row_pq, 7, log.vehicle_id.license_plate, design_8)
                    else:
                        worksheet1.write(row_pq, 7, '-', design_7)
                    if log.duration:
                        worksheet1.write(row_pq, 8, log.duration, design_9)
                    else:
                        worksheet1.write(row_pq, 8, '-', design_7)
                    if log.starting_km:
                        starting_km = log.total_km - log.vehicle_id.odometer
                        worksheet1.write(row_pq, 9, starting_km, design_9)
                    else:
                        worksheet1.write(row_pq, 9, '-', design_7)
                    if log.total_km:
                        total_km += log.total_km
                        worksheet1.write(row_pq, 10, log.total_km, design_9)
                    else:
                        worksheet1.write(row_pq, 10, '-', design_7)
                    if log.rate_per_km:
                        worksheet1.write(row_pq, 11, log.rate_per_km, design_15)
                    else:
                        worksheet1.write(row_pq, 11, '-', design_7)
                    if log.rate_per_km:
                        total_cost = log.rate_per_km * log.total_km
                        total_subtotal += total_cost
                        worksheet1.write(row_pq, 12, '%.2f' % total_cost, design_15)
                    else:
                        worksheet1.write(row_pq, 12, '-', design_7)
                    sl_no += 1
                    row_pq += 1
                worksheet1.write(row_pq + 1, 9, 'TOTAL', design_16)
                worksheet1.write(row_pq + 1, 10, '%.2f' % total_km, design_16)
                worksheet1.write(row_pq + 1, 12, '%.2f' % total_subtotal, design_16)
        fp = BytesIO()
        o = workbook.save(fp)
        fp.read()
        excel_file = base64.b64encode(fp.getvalue())
        self.write({'summary_file': excel_file, 'file_name': 'Rental Fleet History Report - [ %s ].xls' % self.date,
                    'report_printed': True})
        fp.close()
        return {
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'driver.vehicle.history.wizard',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new',
        }
