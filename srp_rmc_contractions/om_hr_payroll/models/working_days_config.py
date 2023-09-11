# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo.exceptions import Warning, ValidationError, UserError
from odoo import api, fields, models, _


class HrPayrollMonth(models.Model):
    _name = 'hr.payroll.month'
    _description = 'Payroll Month Master Config'

    name = fields.Char(string='Month')


class HRPayrollYears(models.Model):
    _name = 'hr.payroll.year'
    _description = 'Payroll Year Master Config'

    name = fields.Char(string='Year')
    day_and_month = fields.One2many('hr.payroll.year.line', 'name_id')
    month = fields.Char(string='month', compute='_compute_month')
    month_number = fields.Char(string='Month Number')
    date_convert = fields.Datetime(string='Date Convert')

    @api.onchange('month', 'month_number', 'name', 'day_and_month')
    def _onchange_year_and_month(self):
        import datetime
        import calendar
        try:
            year = int(self.name)
        except ValueError:
            # Handle the case when 'name' cannot be converted to an integer
            return
        for record in self.day_and_month:
            try:
                select_month = int(record.select_month)
                if select_month < 1 or select_month > 12:
                    # Handle the case when 'select_month' is not in the valid range 1-12
                    continue
            except ValueError:
                # Handle the case when 'select_month' cannot be converted to an integer
                continue
            try:
                selection_diff = datetime.datetime(year, select_month, 1)
                record.year_monthnumber_of_days = calendar.monthrange(selection_diff.year, selection_diff.month)[1]
                sundays = len(
                    [1 for i in calendar.monthcalendar(selection_diff.year, selection_diff.month) if i[6] != 0])
                record.sunday = sundays
            except (ValueError, TypeError):
                # Handle any other potential exceptions related to invalid date inputs
                continue

    @api.depends('month')
    @api.onchange('month')
    def _compute_month(self):
        import datetime
        import calendar
        date = datetime.datetime.now()
        daten = datetime.datetime(1, int(date.month), 1).strftime("%B")
        self.month = daten
        # self.month_number = date.month

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if record.name:
                domain = [('name', '=', record.name)]
                name = self.search(domain)
                if len(name) > 1:
                    for i in range(len(name)):
                        if name[i].id != record.id:
                            raise ValidationError(
                                _('Alert !!  Year - %s already exists.') % (
                                    record.name))

    # @api.onchange('day_and_month')
    # def _public_holiday(self):
    #     for record in self.day_and_month:
    #         public_leave_count = 0.00
    #         current_year = datetime.now().year
    #         employee_public_leave = record.env['hr.public.holidays.line'].sudo().search(
    #             [('month_number', '=', record.select_month),
    #              ('name', '=', current_year)])
    #
    #         for line in employee_public_leave:
    #             if record.select_month == line.month_number:
    #                 public_leave_count += 1
    #         record.public_holiday_count = public_leave_count
    #         num = ''
    #         for rec in employee_public_leave:
    #             if record.select_month == rec.month_number:
    #                 if rec.name:
    #                     num += str(rec.name) + ','
    #         record.holiday_public = num

    def find_all_sundays(self):
        import datetime
        import calendar

        today = datetime.date.today()
        current_month = today.month
        day = datetime.date(today.year, current_month, 1)
        single_day = datetime.timedelta(days=1)
        current_month_total_days = 0
        while day.month == current_month:
            current_month_total_days += 1
            day += single_day
        for line in self.day_and_month:
            if line.select_month:
                try:
                    selected_month = int(line.select_month)
                    if 1 <= selected_month <= 12:
                        selected_month_year = datetime.date(today.year, selected_month, 1)
                        days_in_selected_month = \
                            calendar.monthrange(selected_month_year.year, selected_month_year.month)[1]
                        sundays = len(
                            [1 for i in calendar.monthcalendar(selected_month_year.year, selected_month_year.month) if
                             i[6] != 0])
                        saturdays = len(
                            [1 for i in calendar.monthcalendar(selected_month_year.year, selected_month_year.month) if
                             i[5] != 0])
                        line.number_of_days = days_in_selected_month - (sundays + saturdays + line.public_holiday_count)
                        line.total_number_of_days = days_in_selected_month
                        line.sunday = sundays + saturdays
                except ValueError:
                    continue

    def get_number_of_working_days(self):
        hr_payslips = self.env['hr.payslip'].search([('date_year', '=', self.name)])
        for payslip in hr_payslips:
            for record in self.day_and_month:
                convert_select_month = datetime(1, int(record.select_month), 1).strftime("%B")
                if payslip.date_months == convert_select_month:
                    payslip.write({
                        'number_working_of_days': record.number_of_days,
                        'number_of_leave': record.public_holiday_count + record.sunday,
                        'total_days_of_month': record.total_number_of_days,

                    })


class MonthYears(models.Model):
    _name = 'hr.payroll.year.line'
    _description = 'Payroll Year  line'

    name_id = fields.Many2one('hr.payroll.year', string='Year')
    # month = fields.Char(string='Month')
    number_of_days = fields.Float(string='Number Of Days')
    week_off = fields.Selection([('weekoff', 'All Saturdays & Sundays')], default='weekoff',
                                string='Week Off')
    sunday = fields.Integer(string='Saturday & Sunday')
    boolen_leave = fields.Boolean(string='Approved')
    select_month = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ], string="Month")
    # public_holiday_id = fields.Many2many('hr.holidays.public', string='Public Holidays')
    # holiday_date = fields.Date(string='Date')
    public_holiday_count = fields.Integer(string='Public Holiday')
    holiday_public = fields.Char(string='Leave Type')
    total_number_of_days = fields.Float(string='Total Number Of Days')
    year_monthnumber_of_days = fields.Float(string='year month Number Of Days')

    def action_approve(self):
        from datetime import datetime
        currentMonth = datetime.now().month
        for rec in self:
            if rec.select_month:
                rec.write({'boolen_leave': True})
                rec.name_id.find_all_sundays()
                rec.name_id.get_number_of_working_days()

    @api.constrains('select_month')
    def _check_name(self):
        for record in self:
            if record.select_month:
                current_year = fields.Date.today().year
                domain = [
                    ('select_month', '=', record.select_month),
                    ('name_id', '=', str(current_year))
                    # Convert current_year to a string for comparison
                ]
                codes = self.search(domain)
                if len(codes) > 1:
                    for code in codes:
                        if code.id != record.id:
                            convert_select_month_val = datetime(1, int(record.select_month), 1).strftime("%B")
                            raise ValidationError(
                                _('Alert! The Selected Month and Year of %s-%s already exists.') % (
                                    convert_select_month_val, record.name_id.name))
