from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning, ValidationError


# WIZARD CLASS : VEHICLE REGISTRATION INFO WIZARD
class RentalVehicleTripWizard(models.TransientModel):
    _name = "vehicle.registration.info.wizard"
    _description = 'Vehicle Registration Info Wizard'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    vehicle_type = fields.Selection([
        ("car", "Car"),
        ("bus", "Bus"),
        ("jcb", "JCB"),
        ("tractor", "Tractor"),
        ("jeep", "Jeep"),
        ("tanker_lorry", "Tanker Lorry"),
        ("tipper_lorry", "Tipper Lorry"),
        ("load_vehicle", "Load Vehicle"),
        ("truck", "Truck"),
    ])
    vehicle_category_id = fields.Many2one('fleet.vehicle.model.category', string='Vehicle Type')

    def print_vehicle_registration_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            's_date': self.start_date,
            'e_date': self.end_date,
            'vehicle_category_id': self.vehicle_category_id.name,
            'form': {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'vehicle_category_id': self.vehicle_category_id.name,
            },
        }
        return self.env.ref('apps_fleet_rental.record_vehicle_registration_pdf').report_action(self, data=data)


class VehicleRegistrationInfoWizardParser(models.AbstractModel):
    _name = 'report.apps_fleet_rental.vehicle_registration_pdf_template'

    def _get_report_values(self, docids, data=None):
        start_date = data['s_date']
        end_date = data['e_date']
        vehicle_category_id = data['vehicle_category_id']

        vehicle_list = self.env['fleet.vehicle'].sudo().search([
            ('vehicle_category_id.name', '=', vehicle_category_id),
        ], order='model_id asc')

        brand = self.env['fleet.vehicle.model'].search([])

        data = []
        for i in brand:
            if i.vehicle_category_id.name == vehicle_category_id:
                val = []
                for j in vehicle_list:
                    if i.vehicle_category_id.name == j.vehicle_category_id.name:
                        val.append(j)
                data.append({
                    str(i.name): val
                })
            #
            # else:
            #     val = []
            #     for j in vehicle_list:
            #         if i.vehicle_category_id.name == j.vehicle_category_id.name:
            #             val.append(j)
            #     data.append({
            #         str(i.name): val
            #     })

        # Header For Attendance List
        cols_heads = ['S.No', 'Vehicle No', 'Vehicle Type', 'Registration Date', 'FC Ex Date', 'Permit',
                      'Insurance Ex Date', 'Np Ex Date', 'Tn Ex Date', 'Pol Ex Date 1', 'Pol ex Date 2']

        return {
            'cols_heads': cols_heads,
            'doc_ids': docids,
            'data': data,
            'vehicle': vehicle_list,
            'doc_model': 'vehicle.registration.info.wizard',
        }
