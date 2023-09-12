# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo.exceptions import Warning, ValidationError, UserError
from odoo import api, fields, models, _


class HrContract(models.Model):
    """
    Employee contract based on the visa, work permits
    allows to configure different Salary structure
    """
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    date_start = fields.Date(string="Date From", related='employee_id.date_of_joining')
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-weekly'),
        ('bi-monthly', 'Bi-monthly'),
    ], string='Scheduled Pay', index=True, default='monthly',
        help="Defines the frequency of the wage payment.")
    resource_calendar_id = fields.Many2one(required=True, help="Employee's working schedule.")
    hra = fields.Monetary(string='HRA', help="House rent allowance.")
    travel_allowance = fields.Monetary(string="Travel Allowance", help="Travel allowance")
    da = fields.Monetary(string="DA", help="Dearness allowance")
    meal_allowance = fields.Monetary(string="Meal Allowance", help="Meal allowance")
    medical_allowance = fields.Monetary(string="Medical Allowance", help="Medical allowance")
    other_allowance = fields.Monetary(string="Other Allowance", help="Other allowances")
    type_id = fields.Many2one('hr.contract.type', string="Employee Category",
                              required=True, help="Employee category",
                              default=lambda self: self.env['hr.contract.type'].search([], limit=1))
    food_allowance = fields.Monetary(string="Food Allowance", help="Food allowance")
    beta_allowance = fields.Monetary(string="Beta Allowance", help="Beta allowance")
    grease_allowance = fields.Monetary(string="Grease Allowance", help="Grease allowance")
    ctc = fields.Monetary(string='CTC', store=True)
    amount_settlment_diff = fields.Monetary(string='CTC Difference')
    compute_contract_valdiate = fields.Boolean(string='Compute Contract')
    basic_percentage = fields.Float(string='Basic Percentage %')
    travel_incentives = fields.Monetary(string='Maintenance/ Travel Allowance')
    hra_percentage = fields.Float(string='HRA Allowance Percentage %')
    basic_allowance = fields.Monetary(string="Basic Allowance")
    house_rent_allowance = fields.Monetary(string="House Rent Allowance")
    house_allowance = fields.Monetary(string="House Allowance")
    special_allowance = fields.Monetary(string="Special Allowance")
    weekly_incentive = fields.Monetary(string="Weekly Incentive")
    monthly_incentive = fields.Monetary(string="Monthly Incentive")
    special_incentive = fields.Monetary(string="Special Incentive")
    health_insurance = fields.Monetary(string="Special Incentive")
    manual_ctc = fields.Monetary(string="CTC")
    contract_deduction_settlement = fields.Monetary(string="Contract Deduction")
    contract_amount_settlement = fields.Monetary(string="Contract Allowance")
    salary_hike_enabled = fields.Boolean(string="Hike")
    other_deduction = fields.Float(string="Other Deduction")
    advance_salary = fields.Float(string="Advance Salary")
    loan_deduction = fields.Float(string="Loan Deduction")
    amount_settlement_diff = fields.Boolean(string="")
    compute_contract_validate = fields.Boolean(string="")

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

    @api.onchange('wage', 'hra_percentage', 'basic_percentage', 'ctc', 'manual_ctc')
    def hra_allowance(self):
        for record in self:
            # Set initial values to zero
            total_basic = 0.00
            total_conveyance = 0.00

            if record.manual_ctc:
                # If manual_ctc is provided, update the ctc field
                record.ctc = record.manual_ctc

            if record.ctc > 0.00:
                if record.basic_percentage:
                    # Calculate total_basic based on basic_percentage
                    total_basic = record.ctc * (record.basic_percentage / 100.0)
                    record.write({
                        'basic_allowance': total_basic,
                        'wage': record.ctc - total_basic  # Update wage based on basic_allowance
                    })
            if record.wage > 0.00:
                if record.hra_percentage:
                    # Calculate total_conveyance based on hra_percentage
                    total_conveyance = record.wage * (record.hra_percentage / 100.0)
                    record.write({
                        'house_allowance': total_conveyance,
                        'house_rent_allowance': record.wage - total_conveyance
                        # Update house_rent_allowance based on house_allowance
                    })

    # APPLY THE EMPLOYEE CONTRACT AMOUNT TO WITH PERCENTAGE WISE
    @api.depends('amount_settlement_diff')
    @api.onchange('amount_settlement_diff', 'wage', 'house_rent_allowance',
                  'health_insurance', 'special_allowance',
                  'other_deduction')
    def _onchange_amount_settlement_diff(self):
        total_calculation = 0.00
        if self.ctc:
            self.contract_amount_settlement = self.wage + \
                                              self.house_rent_allowance + \
                                              self.special_allowance + \
                                              self.health_insurance
            self.contract_deduction_settlement = self.other_deduction
            total_calculation = self.contract_amount_settlement + self.contract_deduction_settlement
            self.amount_settlment_diff = self.ctc - total_calculation

    def employee_contract_setup_validate(self):
        if self.employee_id and self.amount_settlment_diff != 0.00:
            raise ValidationError(
                _("Alert!, Contract cannot be Validated for Mr.%s, "
                  "as The Contract Salary Allocation is Not Matching with CTC - %s. "
                  "The Payment Difference is %s.") % (
                    self.employee_id.name, self.ctc,
                    self.amount_settlment_diff))
        else:
            self.write({'compute_contract_validate': True})
            self.write({
                'state': 'open',
            })

    def employee_contract_setup_expire(self):
        self.write({
            'state': 'close',
        })

    def employee_contract_setup_cancel(self):
        self.write({
            'state': 'cancel',
        })

    # CLEAR THE EMPLOYEE CONTRACT AMOUNT TO RE-CALCULATE
    def clear_contract_amount_setup(self):
        for contract in self:
            if contract.ctc:
                contract.amount_settlment_diff = contract.ctc
                contract.wage = 0.00
                contract.basic_percentage = 0.00
                contract.house_rent_allowance = 0.00
                contract.special_allowance = 0.00
                contract.health_insurance = 0.00
                contract.other_deduction = 0.00
                contract.hra_percentage = 0.00

    def get_all_structures(self):
        """
        @return: the structures linked to the given contracts, ordered by hierachy (parent=False first,
                 then first level children and so on) and without duplicata
        """
        structures = self.mapped('struct_id')
        if not structures:
            return []
        # YTI TODO return browse records
        return list(set(structures._get_parent_structure().ids))

    def get_attribute(self, code, attribute):
        return self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1)[attribute]

    def set_attribute_value(self, code, active):
        for contract in self:
            if active:
                value = self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1).default_value
                contract[code] = value
            else:
                contract[code] = 0.0


class HrContractAdvantageTemplate(models.Model):
    _name = 'hr.contract.advantage.template'
    _description = "Employee's Advantage on Contract"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    lower_bound = fields.Float('Lower Bound', help="Lower bound authorized by the employer for this advantage")
    upper_bound = fields.Float('Upper Bound', help="Upper bound authorized by the employer for this advantage")
    default_value = fields.Float('Default value for this advantage')
