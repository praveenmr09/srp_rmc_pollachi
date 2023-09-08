# -*- coding: utf-8 -*-
#############################################################################

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning, ValidationError


# CLASS ACCOUNT MOVE
class AccountMove(models.Model):
    _inherit = 'account.move'
    transport_mode = fields.Selection([
        ('roadways', 'Road'),
        ('railways', 'Railways'),
        ('airways', 'Airways'),
        ('waterways', 'Waterways')],
        'Transportation Mode', tracking=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle No", )
    place_of_supply = fields.Text(string='Place of Supply')
    date_of_supply = fields.Date(string='Date of Supply')


# CLASS ACCOUNT MOVE LINE
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    trips_starts_from = fields.Char(string="From")
    update_charges = fields.Boolean(string='Select')
    trips_ends_at = fields.Char(string="To")
    duration = fields.Float(string="Duration")
    rent_date = fields.Date(string="Rent Date")
    start_date = fields.Date(string="Start Date")
    trip_alter_charges = fields.Float(string='Rental Halter Charges')
    trip_alter_charges_remarks = fields.Text(string='Halter Charges Remarks',
                                             placeholder='Halter Charges Remarks')
    rate_per_km = fields.Float(string='Rate/Km')
    end_date = fields.Date(string="End Date")
    name_of_goods = fields.Text(string='Name of Goods')
