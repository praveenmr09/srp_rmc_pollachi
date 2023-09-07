from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning, ValidationError


# WIZARD CLASS : ODOMETER WIZARD
class RentalVehicleTripWizard(models.TransientModel):
    _name = "odometer.wizard"
    _description = 'Odometer Wizard'

    rent_contract_ref = fields.Char(string="Reference Id")
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    last_odometer = fields.Float(string='Last Odometer')
    difference = fields.Float(string='Difference', compute='_compute_difference')
    is_default_remark = fields.Boolean('Enable Default Remark')
    remarks = fields.Text('Remarks')
    default_remark = fields.Text('Default Remark',
                                 default='Rental Contract Alter Charges Approval '
                                         'get confirmed Without Remarks')
    exact_odometer = fields.Float(string='Exact Odometer')

    @api.onchange('last_odometer', 'exact_odometer')
    def _compute_difference(self):
        if self.last_odometer and self.exact_odometer:
            self.difference = self.exact_odometer - self.last_odometer

        if self.difference < 0.00:
            self.difference = 0.00

    def update_current_odometer(self):
        if self.exact_odometer:
            if self.exact_odometer <= self.last_odometer:
                raise ValidationError("Alert, Mr. %s.\nThe Exact Odometer should be Greater "
                                      "than Last Odometer, Kindly Check it" % self.env.user.name)
        if self.vehicle_id:
            existing_odometer = self.env['fleet.vehicle.odometer'].search([
                ('vehicle_id', '=', self.vehicle_id.id),
                ('value', '=', self.last_odometer),
            ],
                order='write_date desc', limit=1)

            if existing_odometer:
                existing_odometer.write({
                    'value': self.exact_odometer,
                })

        for update_odometer in self.env['fleet.vehicle'].search([]):
            odometer_details_line_vals = {
                'last_odometer': self.last_odometer,
                'current_odometer': self.exact_odometer,
                'difference': self.difference,
            }

            if update_odometer.license_plate == self.vehicle_id.license_plate:
                empty_trip_line = self.env['empty.trip.details'].create(odometer_details_line_vals)
                update_odometer.write({'empty_trip_details_ids': [(4, empty_trip_line.id)]})


    @api.onchange("is_default_remark")
    def _onchange_is_default_remark(self):
        for val in self:
            if val.is_default_remark:
                val.remarks = val.default_remark
            else:
                val.remarks = ''
