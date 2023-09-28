# -*- coding: utf-8 -*-
#############################################################################

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning, ValidationError
from dateutil.relativedelta import relativedelta
# ~ from dateutil import relativedelta
from odoo.tools import float_compare, float_is_zero
import num2words
from num2words import num2words


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
    date_year = fields.Char(string="Year", compute='_compute_date_year', store=True)
    leave_paid_timeoff = fields.Float(string="Paid Leave ")
    final_payslip_calcualte_amount = fields.Float(string="Final Pay")
    number_working_of_days = fields.Float(string="Number of working Days ")
    total_number_of_days = fields.Float(string="Total Number of Days ")
    number_of_leave = fields.Float(string="Saturday's and Sunday's ")
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
    total_amount = fields.Float(string='Total Amount')
    amount_words = fields.Char(string='Amount in Words', compute='_compute_num2words')

    @api.onchange('employee_present_days')
    def employee_present_days_restriction(self):
        if self.employee_present_days > self.number_working_of_days:
            raise ValidationError("Alert, Mr. %s.\nThe Employee Present Days should not be Greater "
                                  "than Number of Working Days, Kindly Check it" % self.env.user.name)

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

    def _compute_num2words(self):
        self.amount_words = 'Rupees ' + str.title(num2words(round(self.total_amount))).replace(',', '') + ' ' + 'Only'

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

    def get_payroll_year_working_days(self):
        num_of_days = self.env['hr.payroll.year'].search([('name', '=', self.date_year)])
        if num_of_days:
            num_of_days.get_number_of_working_days()

    def employee_year_month_button(self):
        num_of_days = self.env['hr.payroll.year'].search([('name', '=', self.date_year)])
        for record in self:
            if num_of_days.day_and_month:
                approved_month = False
                for line in num_of_days.day_and_month:
                    if int(line.select_month) == record.date_from.month:
                        if line.boolen_leave:
                            approved_month = True
                            break
                        else:
                            raise ValidationError(
                                _("Alert!,The selected Payslip Period - %s-%s,The Number of working days setup has "
                                  "been done, but it hasn't been approved.\n"
                                  "SO, Please, approve the configuration and generate it.") % (
                                    record.date_months, record.date_year))
                if approved_month:
                    record.get_payroll_year_working_days()
                else:
                    raise ValidationError(
                        _("Alert!,The selected Payslip Period doesn't have an approved Number of Working Days setup "
                          "for - %s-%s.\n"
                          "SO, Please create it in the configuration and generate it.") % (
                            record.date_months, record.date_year))
            else:
                raise ValidationError(
                    _("Alert!,The selected Payslip Period doesn't have any Number of Working Days setup for any month "
                      "of this year %s.\n"
                      "SO, Please configure it and generate it.") % (
                        record.date_year))

    @api.onchange('employee_id', 'date_from', 'date_to')
    def compute_days(self):
        import calendar
        import datetime
        date = datetime.datetime.now()
        month_current = calendar.monthrange(date.year, date.month)[1]
        # self.number_working_of_days = month_current - self.employee_final_present_days
        if self.date_from.month == self.date_to.month:
            date_fr = self.date_from.month and self.date_to.month
            daten = datetime.datetime(1, int(date_fr), 1).strftime("%B")
            self.date_months = daten
        if self.date_from.year == self.date_to.year:
            date_yr = self.date_from.year and self.date_to.year
            # daten = datetime.datetime(1, int(date_fr), 1).strftime("%B")
            self.date_year = date_yr

    @api.onchange('employee_id')
    def _compute_contract(self):
        if self.employee_id:
            self.contract_id = self.employee_id.contract_id.name

    def get_employee_details(self):
        employee_contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])

        # Calculation related to Gross and lop_days_amount
        for rec in self.line_ids:
            if rec.category_id.name == 'Gross':
                onedayamount = rec.amount
                total_wage_contract = self.contract_id.ctc / 30
                lop_days_amount = total_wage_contract * self.employee_loptotal_days
                self.employee_one_day_salary = round(total_wage_contract)
                total_unpaid_amount = (self.employee_balance_days + self.employee_loptotal_days) * total_wage_contract
                self.employee_loptotal_days = self.number_working_of_days - self.employee_final_present_days
                # self.employee_final_lop_total_days = self.employee_balance_days + self.employee_loptotal_days
                self.employee_final_present_days = self.employee_present_days
                # self.employee_final_present_days = self.employee_present_days + self.number_of_leave
                self.total_amount = self.employee_final_present_days * self.employee_one_day_salary
                try:
                    profitpercentday = (employee_contract.wage / 30)
                except ZeroDivisionError:
                    self.employee_one_day_salary = profitpercentday
                    self.write({'employee_one_day_salary': round(total_wage_contract),
                                'unpaid_deduction': round(total_unpaid_amount)})
                self.allowance_amount_deduction = abs(lop_days_amount)
                for line in self.line_ids:
                    if line.amount > 0.00:
                        if line.category_id.code == 'BASIC':
                            line.write({
                                'amount': employee_contract.wage
                            })
                        if line.code == 'HRA':
                            line.write({
                                'amount': employee_contract.house_rent_allowance
                            })
                        if line.code == 'SAR':
                            line.write({
                                'amount': employee_contract.advance_salary
                            })
                        if line.code == 'LO':
                            line.write({
                                'amount': employee_contract.loan_deduction
                            })
                        if line.code == 'OD':
                            line.write({
                                'amount': employee_contract.other_deduction
                            })
                        if line.code == 'BE':
                            line.write({
                                'amount': employee_contract.beta_expense
                            })
                        if line.code == 'BC':
                            line.write({
                                'amount': employee_contract.broker_charges
                            })
                        if line.code == 'CMS':
                            line.write({
                                'amount': employee_contract.commissions
                            })
                        if line.code == 'Meal':
                            line.write({
                                'amount': employee_contract.food_charges
                            })
                        if line.code == 'UPA':
                            line.write({
                                'amount': self.allowance_amount_deduction})

        import calendar
        import datetime
        date = datetime.datetime.now()
        diff = calendar.monthrange(date.year, date.month)[1]
        # Calculate profitpercentday
        try:
            profitpercentday = (employee_contract.wage / diff)
        except ZeroDivisionError:
            self.employee_one_day_salary = profitpercentday
        return True

    def _payslip_calculation(self):
        # Calculate employee_balance_days
        self.employee_balance_days = 30 - self.number_working_of_days
        # Initialize variables
        allowance = 0.00
        deduction = 0.00
        Compensations = 0.00
        Employerdeduction = 0.00
        grossamount = 0.00
        flight = 0.00
        birthday = 0.00
        loans = 0.00
        unpaid = 0.00
        adv_sal = 0.00
        total_deduct = 0.00
        net = 0.00
        basic = 0.00
        up = 0.00
        # Calculate amounts
        if self.employee_id:
            for line in self.line_ids:
                if line.category_id.name == 'Deduction':
                    if line.name != 'Unpaid':
                        deduction += line.amount
                        self.deduction_amount = deduction
                if line.category_id.name == 'Basic':
                    basic += round(line.amount)
                if line.category_id.name == 'Allowance':
                    allowance += round(line.amount)
                if line.category_id.name == 'Compensation':
                    Compensations += round(line.amount)
                if line.category_id.name == 'Gross':
                    line.write({
                        'amount': (allowance + basic + Compensations) - Employerdeduction
                    })
                    grossamount += round(line.amount)
                    self.gross_amount = round(line.amount)

                # if line.name == 'Unpaid':
                #     up = self.employee_balance_days * self.employee_one_day_salary
                #     line.write({
                #         'amount': up
                #     })
                if line.category_id.name == 'Net':
                    # net = self.total_amount if deduction > 0 else (allowance + basic)
                    net = self.total_amount
                    line.write({
                        'amount': net
                    })

    def compute_sheet(self):
        for payslip in self:
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or self.get_contract(payslip.employee_id, payslip.date_from,
                                                                        payslip.date_to)
            if not contract_ids:
                raise ValidationError(
                    _("Alert!, No running contract found for the employee: %s or no contract in the given period" % payslip.employee_id.name))
            # Filter and add only lines with amount > 0 to the payslip
            lines = [(0, 0, line) for line in self._get_payslip_lines(contract_ids, payslip.id) if
                     line.get('amount', 0) > 0]
            payslip.write({'line_ids': lines, 'number': number})
            payslip.employee_year_month_button()
            payslip.get_employee_details()
            payslip._payslip_calculation()
        return True
