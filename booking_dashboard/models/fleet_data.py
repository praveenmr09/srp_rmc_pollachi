from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
from odoo.exceptions import UserError, ValidationError
from datetime import date
from datetime import datetime, timedelta
import pytz
import  datetime

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

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
        date_list.insert(0, 'Vehicle')
        dashboard_data['summary_header'] = date_list
        dashboard_data['vehicle_data'] = vehicle_state
        return dashboard_data
