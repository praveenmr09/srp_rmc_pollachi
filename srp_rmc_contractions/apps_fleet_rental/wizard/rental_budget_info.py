# -*- coding: utf-8 -*-
#################################################################################


from odoo import api, fields, models, _
from datetime import datetime


# WIZARD CLASS RENT BUDGETS INFO
class RentalBudgetsInfo(models.TransientModel):
    _name = "rent.budgets.info"
    _description = 'Rental Budgets Info'

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle No')
    vehicle_no = fields.Char(string='Vehicle No', related='vehicle_id.license_plate')
    vehicle_departure = fields.Char(string='Vehicle Departure')
    vehicle_destination = fields.Char(string='Vehicle Destination')
    starting_km = fields.Float(string='Starting KM')
    closing_km = fields.Float(string='Closing KM')
    total_km = fields.Float(string='Closing KM')
    date = fields.Datetime(string='Date', default=lambda self: fields.Datetime.now())
    expense_detail = fields.Float(string='Expense Detail')
    content = fields.Selection([
        ("petrol", "Petrol"),
        ("diesel", "Diesel"),
        ("cng", "Compressed Natural Gas (CNG)"),
        ("lpg", "Liquid Petroleum Gas (LPG)"),
        ("others", "Others"),
    ], string='Content', default="diesel")
    toll_expense = fields.Float(string='Toll Expense')
    export_import_commission = fields.Float(string='Export Import Commission')
    beta_expense = fields.Float(string='Beta Expense')
    broker_charges = fields.Float(string='Broker Expense')
    commissions = fields.Float(string='Commissions')
    other_charges = fields.Float(string='Other Expense')
    food_charges = fields.Float(string='Food Expense')
    existing_expense = fields.Float(string='Existing Expense')
    srp_income = fields.Float(string='SRP Expense')
    rental_income = fields.Float(string='Rental Expense')
    spend_expense = fields.Float(string='Spend Expense')
    expenditure_balance = fields.Float(string='Expenditure Balance')
    total_spend_expense = fields.Float(string='Total Expense Spent')
    partner_id = fields.Many2one('res.partner', string='Customer')
    partner_mobile = fields.Char(string='Mobile', related='partner_id.mobile')
    driver_id = fields.Many2one('hr.employee', string='Driver')
    rent_contract_ref = fields.Char(string='Reference')
    vehicle_image = fields.Binary(string='Vehicle Image', related='vehicle_id.image_128')
    driver_image = fields.Binary(string='Driver Image', related='driver_id.image_1920')

