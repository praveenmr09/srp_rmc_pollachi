# -*- coding: utf-8 -*-
#############################################################################

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning, ValidationError
from dateutil.relativedelta import relativedelta


# CLASS HR PAYSLIP
class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    unpaid_deduction = fields.Float(string="Unpaid Amount Deduction")
    loan_deduction = fields.Boolean(string='Loan Deduction', readonly=True,
                                    states={'draft': [('readonly', False)]},
                                    help="Indicates this payslip has a loan payment deduction")
    gross_deduction_amount = fields.Float(string="Gross Deduction Amount")
    basic_deduction_amount = fields.Float(string="Basic Deduction Amount")
    house_deduction_amount = fields.Float(string="HRA Deduction Amount")
    deduction_amount = fields.Float(string="Deduction Amount")
    employee_one_day_salary = fields.Float(string="Employee One Day Amount", readonly=True,
                                           states={'draft': [('readonly', False)]},
                                           help="Employee One Day Salary Information")
    employee_loptotal_days = fields.Integer(string="Employee LOP Days")
    remarks = fields.Text(string="Loan Payment Remarks",
                          default="Gross Amount Deduction(50%),Basic Amount Deduction(40%)")
    employee_present_days = fields.Integer(string="Employee Present Days")
    employee_final_present_days = fields.Integer(string="Employee Final Present Days")
    employee_balance_days = fields.Float(string="Employee Balance Days")
    date_months = fields.Char(string="Month")
    date_year = fields.Char(string="Year")
    leave_paid_timeoff = fields.Float(string="Paid Leave ")
    final_payslip_calcualte_amount = fields.Float(string="Final Pay")
    number_working_of_days = fields.Float(string="Number of working Days ")
    total_number_of_days = fields.Float(string="Total Number of Days ")
    number_of_leave = fields.Float(string="Public Leave's and Sunday's ")
    total_days_of_month = fields.Float(string="Total Days in Month ")
    employee_final_lop_total_days = fields.Integer(string="Employee Final LOP Days")
    allowance_amount_total = fields.Float(string="Allowance Amount")
    allowance_amount_deduction = fields.Float(string="Allowance Deduction")
    weekly_incentive = fields.Float(string="Weekly Incentive")
    monthly_incentive = fields.Float(string="Monthly Incentive")
    special_incentive = fields.Float(string="Special Incentive")
    gross_amount = fields.Float(string="Gross Amount")
    select_year = fields.Many2one('hr.payroll.year', string='Year')
    select_month = fields.Selection([
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ], string="Month/Year")
    pay_date = fields.Date(string='Pay Date')
    select_year = fields.Many2one('hr.payroll.year', string='Year')
    select_month = fields.Selection([
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ], string="Month/Year")

    @api.onchange('select_year', 'select_month')
    def _onchange_select_year_month(self):
        if self.select_year and self.select_month:
            year = self.select_year.name
            month = self.select_month
            last_day_of_month = (
                    datetime(int(year), self.select_month_to_number(month), 1) + relativedelta(day=31)).date()
            self.date_from = datetime(int(year), self.select_month_to_number(month), 1).date()
            self.date_to = last_day_of_month
        else:
            self.date_from = fields.Date.to_string(datetime.today().replace(day=1))
            self.date_to = fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date())

    def select_month_to_number(self, month):
        months_dict = {
            'January': 1,
            'February': 2,
            'March': 3,
            'April': 4,
            'May': 5,
            'June': 6,
            'July': 7,
            'August': 8,
            'September': 9,
            'October': 10,
            'November': 11,
            'December': 12,
        }
        return months_dict.get(month, 1)

    @api.onchange('select_year', 'select_month')
    def _onchange_select_year_month(self):
        if self.select_year and self.select_month:
            year = self.select_year.name
            month = self.select_month
            last_day_of_month = (
                    datetime(int(year), self.select_month_to_number(month), 1) + relativedelta(day=31)).date()
            self.date_from = datetime(int(year), self.select_month_to_number(month), 1).date()
            self.date_to = last_day_of_month
        else:
            self.date_from = fields.Date.to_string(datetime.today().replace(day=1))
            self.date_to = fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date())

    def select_month_to_number(self, month):
        months_dict = {
            'January': 1,
            'February': 2,
            'March': 3,
            'April': 4,
            'May': 5,
            'June': 6,
            'July': 7,
            'August': 8,
            'September': 9,
            'October': 10,
            'November': 11,
            'December': 12,
        }
        return months_dict.get(month, 1)

    _sql_constraints = [
        ('unique_payslip', 'UNIQUE(date_from)', 'Alert!, The payslip already generated')
    ]

    @api.onchange('employee_id')
    def _compute_contract(self):
        if self.employee_id:
            self.contract_id = self.employee_id.contract_id.name

