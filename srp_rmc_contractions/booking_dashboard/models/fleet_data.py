from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
from odoo.exceptions import UserError, ValidationError
from datetime import date
from datetime import datetime, timedelta
import pytz
import datetime


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    rental_reservation_line = fields.One2many('fleet.vehicle.line', 'vehicle_id',
                                              help="Reserved Rent Info", )

    def get_datas(self, dates):
        date_list = []
        dashboard_data = {}
        summary_header = []
        vehicle_state = []
        start_date = date.today()
        if dates:
            start_date = datetime.datetime.strptime(dates['start_date'], '%Y-%m-%d')
            end_date = datetime.datetime.strptime(dates['end_date'], '%Y-%m-%d')
            while start_date <= end_date:
                date_list.append(start_date.date())
                start_date += timedelta(days=1)

        else:
            for i in range(1, 15):
                d = start_date + timedelta(days=i)
                date_list.append(d)
        fleet = self.search([])
        for i in fleet:
            vehicle_list_state = []
            data = {'vehicle_name': i.name}
            for dt in date_list:
                vehicle_list_state.append({
                    "state": "Free",
                    "date": dt,
                    "box_date": str(dt),
                    "vehicle": i.id,
                })
            data['value'] = vehicle_list_state
            vehicle_state.append(data)

        for vehicle in fleet:
            for board in vehicle_state:
                if board['vehicle_name'] == vehicle.name:
                    for line in vehicle.rental_reservation_line:
                        for val in board['value']:
                            if line.start_date <= val['date'] <= line.end_date:
                                val['state'] = 'Reserved'

        rental_lines = self.env['car.rental.contract'].search([])

        for board in vehicle_state:
            for rental in rental_lines:
                if rental.rent_start_date and rental.rent_end_date:
                    for val in board['value']:
                        if rental.rent_start_date <= val['date'] <= rental.rent_end_date and val['state'] == 'Reserved':
                            print("======================",rental.rent_start_date, val['date'], rental.rent_end_date)
                            val["rental"] = rental.id

        date_list.insert(0, 'Vehicle')
        dashboard_data['summary_header'] = date_list
        dashboard_data['vehicle_data'] = vehicle_state
        return dashboard_data


class FleetVehicleLine(models.Model):
    _name = 'fleet.vehicle.line'
    _description = 'Fleet Vehicle Line'

    date = fields.Date(string="Date")
    vehicle = fields.Many2one('fleet.vehicle')
    driver_id = fields.Many2one('hr.employee', string='Driver')
    rent_start_date = fields.Date(string="Rent Start Date", required=False,
                                  default=lambda self: fields.Datetime.now(timedelta(hours=5, minutes=30)),
                                  help="Start date of contract")
    rent_end_date = fields.Date(string="Rent End Date", required=False, help="End date of contract",
                                default=lambda self: fields.Datetime.now(timedelta(hours=5, minutes=30)))
    from_date = fields.Char(string="From")
    to_date = fields.Char(string="To")
    customer_id = fields.Many2one('res.partner', required=False, string='Customer', help="Customer")
    name_of_rental_purpose = fields.Char(string='Purpose of Rental Contract')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    total_km = fields.Float(string='T.Kms')
    rate_per_km = fields.Float(string='Rate/Km')
    duration = fields.Float(string="Duration")
    rips_starts_from = fields.Char(string="From")
    update_charges = fields.Boolean(string='Select')
    trips_ends_at = fields.Char(string="To")
    rent_date = fields.Date(string="Rent Date")
    start_date = fields.Date(string="Start Date")
    trip_alter_charges = fields.Float(string='Alter Charges')
    end_date = fields.Date(string="End Date")
    trips_starts_from = fields.Char(string="From")
    name_of_goods = fields.Text(string='Name of Goods')
