# -*- coding: utf-8 -*-
#################################################################################


from odoo import api, fields, models, _
from datetime import datetime


# WIZARD CLASS RENT BUDGETS INFO
class RentalBudgetsInfo(models.TransientModel):
    _name = "rent.budgets.info"
    _description = 'Rental Budgets Info'

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle No')
    vehicle_no = fields.Char(string='License Plate', related='vehicle_id.license_plate')
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
    export_import_commission = fields.Float(string='Export Import Commission')

    # DRIVER EXPENSE
    beta_expense = fields.Float(string='Beta Expense')
    food_charges = fields.Float(string='Food Expense')
    spl_allowance = fields.Float(string='Special Allowance')

    # VEHICLE EXPENSE
    fuel_charges = fields.Float(string='Fuel Charges')
    toll_expense = fields.Float(string='Toll Expense')
    maintenance_and_service = fields.Float(string='Maintenance & Service')
    fright_charges_rental = fields.Float(string='Fright Charge/Rental')

    # ADMINISTRATION EXPENSE
    other_charges = fields.Float(string='Other Expense')
    loading_unloading = fields.Float(string='Loading/Unloading')
    pc_rto = fields.Float(string='Pc/Rto')
    commission = fields.Float(string='Commission')

    broker_charges = fields.Float(string='Broker Expense')
    commissions = fields.Float(string='Commissions')
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

    # def add_budget_in_rental_contract(self):
    #     if self.driver_id:
    #         existing_record = self.driver_id.contract_id
    #         existing_record.write({
    #             'beta_expense': existing_record.beta_expense + self.beta_expense,
    #             'broker_charges': existing_record.broker_charges + self.broker_charges,
    #             'commissions': existing_record.commissions + self.commissions,
    #             'other_charges': existing_record.other_charges + self.other_charges,
    #             'food_charges': existing_record.food_charges + self.food_charges,
    #             'existing_expense': existing_record.existing_expense + self.existing_expense,
    #             'srp_income': existing_record.srp_income + self.srp_income,
    #             'rental_income': existing_record.rental_income + self.rental_income,
    #             'spend_expense': existing_record.spend_expense + self.spend_expense,
    #             'expenditure_balance': existing_record.expenditure_balance + self.expenditure_balance,
    #             'total_spend_expense': existing_record.total_spend_expense + self.total_spend_expense,
    #         })

    def add_budget_in_rental_contract(self):
        if self.driver_id:
            existing_record = self.driver_id.contract_id
            existing_record.write({
                'beta_expense': existing_record.beta_expense + self.beta_expense,
                'food_charges': existing_record.food_charges + self.food_charges,
                'spl_allowance': existing_record.spl_allowance + self.spl_allowance,
                'fuel_charges': existing_record.fuel_charges + self.fuel_charges,
                'toll_expense': existing_record.toll_expense + self.toll_expense,
                'maintenance_and_service': existing_record.maintenance_and_service + self.maintenance_and_service,
                'fright_charges_rental': existing_record.fright_charges_rental + self.fright_charges_rental,
                'other_charges': existing_record.other_charges + self.other_charges,
                'loading_unloading': existing_record.loading_unloading + self.loading_unloading,
                'pc_rto': existing_record.pc_rto + self.pc_rto,
                'commission': existing_record.commission + self.commission,
            })
