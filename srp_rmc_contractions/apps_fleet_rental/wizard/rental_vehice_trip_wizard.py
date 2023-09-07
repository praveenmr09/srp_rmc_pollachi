from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning, ValidationError


# WIZARD CLASS : RENTAL VEHICLE TRIP WIZARD
class RentalVehicleTripWizard(models.TransientModel):
    _name = "rental.vehicle.trip.wizard"
    _description = 'Rental Vehicle Trip'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    def print_rental_vehicle_trip_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            's_date': self.start_date,
            'e_date': self.end_date,
            'form': {
                'start_date': self.start_date,
                'end_date': self.end_date,
            },
        }
        return self.env.ref('apps_fleet_rental.record_vehicle_trip_history_pdf').report_action(self, data=data)


class RentalVehicleTripWizardParser(models.AbstractModel):
    _name = 'report.apps_fleet_rental.vehicle_trip_pdf_template'

    def _get_report_values(self, docids, data=None):
        start_date = data['s_date']
        end_date = data['e_date']

        # DICT TO STORE COUNTS FOR EACH VEHICLE AND MONTH
        vehicle_counts = {}
        overall_monthly_counts = {month: 0 for month in
                                  ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']}
        overall_total_count = 0

        vehicle_trip_history = self.env['car.rental.contract'].sudo().search([
            ('rental_contract_line_ids.start_date', '>=', start_date),
            ('rental_contract_line_ids.end_date', '<=', end_date),
            ('state', '=', 'done'),
        ], order='name asc')

        for j in vehicle_trip_history:
            if j.rent_end_date and j.vehicle_id and j.state == 'done':
                vehicle_name = j.vehicle_id.name
                month = j.rent_end_date.strftime('%b')  # TO GET THE MONTH

                if vehicle_name not in vehicle_counts:
                    vehicle_counts[vehicle_name] = {
                        'Jan': 0, 'Feb': 0, 'Mar': 0, 'Apr': 0, 'May': 0, 'Jun': 0,
                        'Jul': 0, 'Aug': 0, 'Sep': 0, 'Oct': 0, 'Nov': 0, 'Dec': 0,
                        'Total': 0,
                    }

                # INCREASE THE COUNT FOR SPECIFIC VEHICLE & MONTH
                vehicle_counts[vehicle_name][month] += 1

                # UPDATE OVERALL MONTHLY COUNTS AND TOTAL
                overall_monthly_counts[month] += 1
                overall_total_count += 1

        # CALCULATE TOTAL SUM FOR EACH VEHICLE
        for vehicle_name, months in vehicle_counts.items():
            total_sum = sum(months.values())
            vehicle_counts[vehicle_name]['Total'] = total_sum

        cols_heads = ['S.No', 'Vehicle', 'Jan', 'Feb', 'Mar', 'Apr',
                      'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Total']

        vehicle_list = self.env['fleet.vehicle'].sudo().search([], order='model_id asc')

        return {
            'doc_ids': docids,
            'doc_model': 'rental.vehicle.trip.wizard',
            'data': vehicle_counts,
            'vehicle': vehicle_list,
            'cols_heads': cols_heads,
            'overall_monthly_counts': overall_monthly_counts,
            'overall_total_count': overall_total_count,
        }
