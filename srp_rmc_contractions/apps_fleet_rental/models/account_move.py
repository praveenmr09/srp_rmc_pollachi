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
    trip_alter_charges = fields.Float(string='Halter Charges')
    trip_alter_charges_remarks = fields.Text(string='Halter Charges Remarks',
                                             placeholder='Halter Charges Remarks')
    rate_per_km = fields.Float(string='Rate/Km')
    end_date = fields.Date(string="End Date")
    name_of_goods = fields.Text(string='Name of Goods')
    # price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_price_subtotal_with_charges')
    #
    # # @api.onchange('trip_alter_charges')
    # # def _onchange_trip_alter_charges(self):
    # #     for record in self:
    # #         if record.trip_alter_charges:
    # #             # If trip_alter_charges has a value, update price_subtotal
    # #             record.price_subtotal += record.trip_alter_charges
    # #         else:
    # #             record.price_subtotal = record.price_subtotal
    #
    # @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id', 'trip_alter_charges')
    # def _compute_totals(self):
    #     for line in self:
    #         if line.display_type != 'product':
    #             line.price_total = line.price_subtotal = False
    #         # Compute 'price_subtotal'.
    #         line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))
    #         subtotal = (line.quantity * line_discount_price_unit) + line.trip_alter_charges
    #
    #         # Compute 'price_total'.
    #         if line.tax_ids:
    #             taxes_res = line.tax_ids.compute_all(
    #                 line_discount_price_unit,
    #                 quantity=line.quantity,
    #                 currency=line.currency_id,
    #                 product=line.product_id,
    #                 partner=line.partner_id,
    #                 is_refund=line.is_refund,
    #             )
    #             line.price_subtotal = taxes_res['total_excluded']
    #             line.price_total = taxes_res['total_included']
    #         else:
    #             line.price_total = line.price_subtotal = subtotal
    #
    # # @api.depends('trip_alter_charges', 'price_subtotal', 'price_unit', 'quantity',)
    # # @api.onchange('trip_alter_charges', 'price_subtotal', 'price_unit', 'quantity',)
    # # def _compute_price_subtotal_with_charges(self):
    # #     for line in self:
    # #         if line.trip_alter_charges or line.price_unit or line.quantity:
    # #             line.price_subtotal = (line.price_unit * line.quantity) + line.trip_alter_charges
    # #         else:
    # #             line.price_subtotal = line.price_subtotal
    #
    # # price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_price_subtotal_with_charges')
    # #
    # # @api.depends('price_unit', 'quantity', 'trip_alter_charges')
    # # @api.onchange('price_unit', 'quantity', 'trip_alter_charges')
    # # def _compute_price_subtotal_with_charges(self):
    # #     for line in self:
    # #         line.price_subtotal = (line.price_unit * line.quantity) + line.trip_alter_charges
