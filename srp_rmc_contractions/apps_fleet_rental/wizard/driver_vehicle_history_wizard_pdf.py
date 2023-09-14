import pytz
from odoo import api, fields, models, _
from datetime import datetime


class DriverVehicleHistoryWizardParser(models.AbstractModel):
    _name = 'report.apps_fleet_rental.driver_history_pdf_template'

    def _get_report_values(self, docids, data=None):
        start_date = data['s_date']
        end_date = data['e_date']
        # vehicle_name_ids = data['vehicle_ids']
        # driver_name_ids = data['driver_ids']
        vehicle_name_ids = data.get('vehicle_ids') or []
        driver_name_ids = data.get('driver_ids') or []
        currency_symbol = data.get('currency_symbol') or []

        # Initialize an empty list for domain conditions
        domain_conditions = []

        # Conditionally add the filter for 'vehicle_id' if it's present in the list
        if vehicle_name_ids:
            domain_conditions.append(('vehicle_id', 'in', vehicle_name_ids))

        # Conditionally add the filter for 'driver_id' if it's present in the list
        if driver_name_ids:
            domain_conditions.append(('driver_id', 'in', driver_name_ids))

        # Construct the final domain condition using OR operators
        if domain_conditions:
            domain = ['&'] + domain_conditions
        else:
            domain = []

        # Apply the domain filter to the search query
        vehicle_history = self.env['fleet.vehicle.assignation.log'].sudo().search(
            domain + [
                ('date_start', '>=', start_date),
                ('date_end', '<=', end_date),
            ],
            order='date_start asc'
        )

        symbol = vehicle_history.vehicle_id.company_id.currency_id.symbol

        total_subtotal = 0.00
        report_data = []
        for log in vehicle_history:
            total_cost = log.rate_per_km * log.total_km
            total_subtotal += total_cost

            data_dict = {
                'rental_date': log.date_start or '',
                'source': log.source_city or '',
                'destination': log.destination_city or '',
                'driver_name': log.driver_employee_id.name if log.driver_employee_id else '',
                'reference': log.rental_contract_reference or '',
                'purpose': log.purpose_of_rental_contract or '',
                'vehicle_no': log.vehicle_id.license_plate if log.vehicle_id else '',
                'symbol': log.vehicle_id.company_id.currency_id.symbol if log.vehicle_id else '',
                'duration': log.duration or '',
                'starting_km': log.starting_km or '',
                'total_km': log.total_km or '',
                'rate_km': log.rate_per_km or '',
                'total_cost': total_cost or '',
                'total_subtotal': total_subtotal or '',
            }
            report_data.append(data_dict)

        # total_subtotal = sum(log.rate_per_km * log.total_km for log in vehicle_history)

        cols_heads = ['S.No', 'Rental Date', 'Source', 'Destination', 'Driver Name', 'Reference',
                      'Purpose', 'Vehicle No', 'Duration', 'Starting Km', 'Total Km', 'Rate/km', 'Subtotal']

        return {
            'doc_ids': docids,
            'doc_model': 'driver.vehicle.history.wizard',
            'data': report_data,
            'cols_heads': cols_heads,
        }
