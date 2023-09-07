# -*- coding: utf-8 -*-
#############################################################################

from odoo import models, fields


# CLASS RENTAL FLEET RESERVED
class FleetReservedTime(models.Model):
    _name = "rental.fleet.reserved"
    _description = "Reserved Time"

    customer_id = fields.Many2one('res.partner', string='Customer')
    date_from = fields.Date(string='Reserved Date From')
    date_to = fields.Date(string='Reserved Date To')
    reserved_obj = fields.Many2one('fleet.vehicle')


# INHERIT FLEET VEHICLE
class EmployeeFleet(models.Model):
    _inherit = 'fleet.vehicle'

    rental_check_availability = fields.Boolean(default=True, copy=False)
    color = fields.Char(string='Color', default='#FFFFFF')
    rental_reserved_time = fields.One2many('rental.fleet.reserved', 'reserved_obj', string='Reserved Time', readonly=1,
                                           ondelete='cascade')
    fuel_type = fields.Selection([('gasoline', 'Gasoline'),
                                  ('diesel', 'Diesel'),
                                  ('electric', 'Electric'),
                                  ('hybrid', 'Hybrid'),
                                  ('petrol', 'Petrol')],
                                 'Fuel Type', help='Fuel Used by the vehicle')

    _sql_constraints = [('vin_sn_unique', 'unique (vin_sn)', "Chassis Number already exists !"),
                        ('license_plate_unique', 'unique (license_plate)', "License plate already exists !")]
