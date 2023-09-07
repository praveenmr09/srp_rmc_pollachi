# -*- coding: utf-8 -*-
#################################################################################


from odoo import api, fields, models, _
from datetime import datetime


# WIZARD CLASS RENT ALTER CHARGES
class ApplyRentAlterCharges(models.TransientModel):
    _name = "rent.alter.charges"
    _description = 'Apply Rent Alter Charges'

    remarks = fields.Text('Remarks')
    alter_charges_amount = fields.Float(string='Alter Charges')
    is_default_remark = fields.Boolean('Enable Default Remark')
    default_remark = fields.Text('Default Remark',
                                 default='Rental Contract Alter Charges Approval '
                                         'get confirmed Without Remarks')
    rent_contract_ref = fields.Char(string="Reference")
    order_lines = fields.One2many('rent.alter.charges.line', 'line_order_id', string='Order Lines')

    @api.onchange("is_default_remark")
    def _onchange_is_default_remark(self):
        for val in self:
            if val.is_default_remark:
                val.remarks = val.default_remark
            else:
                val.remarks = ''

    @api.onchange('alter_charges_amount', 'remarks')
    def update_alter_charges(self):
        self.ensure_one()  # Make sure only one record is being updated
        if self.alter_charges_amount and self.order_lines:
            for charge in self.order_lines:
                charge.write({
                    'trip_alter_charges': self.alter_charges_amount,
                    'trip_alter_charges_remarks': self.remarks
                })

    def update_trip_alter_charges(self):
        if self.env.context.get('active_model') == 'car.rental.contract':
            active_id = self.env.context.get('active_id', False)
            rental_contract = self.env['car.rental.contract'].search([('id', '=', active_id)])
            for line in self.order_lines:
                if line:
                    rental_contract_line = (self.env['car.rental.contract.line'].
                                            search([('rent_contract_id', '=', rental_contract.id)]))
                    if rental_contract_line:
                        rental_contract_line.write({
                            'trip_alter_charges': line.trip_alter_charges,
                            'trip_alter_charges_remarks': line.trip_alter_charges_remarks,
                            # 'rental_contract_id': rental_contract.id,
                        })
            rental_contract.write({
                'state': 'checking'
            })


# WIZARD CLASS RENT ALTER CHARGES LINE
class ApplyRentAlterChargesLine(models.TransientModel):
    _name = "rent.alter.charges.line"
    _description = 'Apply Rent Alter Charges Line'

    trips_starts_from = fields.Char(string="From")
    trips_ends_at = fields.Char(string="To")
    duration = fields.Float(string="Duration")
    rent_date = fields.Date(string="Rent Date")
    start_date = fields.Date(string="Start Date")
    trip_alter_charges = fields.Float(string='Rental Alter Charges')
    trip_alter_charges_remarks = fields.Text(string='Alter Charges Remarks',
                                             placeholder='Alter Charges Remarks')
    end_date = fields.Date(string="End Date")
    name_of_goods = fields.Text(string='Name of Goods')
    line_order_id = fields.Many2one('rent.alter.charges')
