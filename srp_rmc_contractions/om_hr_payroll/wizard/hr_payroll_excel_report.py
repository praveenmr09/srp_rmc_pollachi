import io

from odoo import models, fields, api, _
import xlwt
from io import BytesIO
import base64
import itertools
from operator import itemgetter
from odoo.exceptions import Warning
from odoo import tools
from xlwt import easyxf
import datetime
from odoo.exceptions import UserError
from datetime import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning, ValidationError, UserError
import pdb
import calendar
import xlsxwriter
from xlsxwriter import worksheet

cell = easyxf('pattern: pattern solid, fore_colour yellow')
ADDONS_PATH = tools.config['addons_path'].split(",")[-1]

MONTH_LIST = [('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'),
              ('4', 'Apr'), ('5', 'May'), ('6', 'Jun'),
              ('7', 'Jul'), ('8', 'Aug'), ('9', 'Sep'),
              ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec')]


class HrPayRollExcelReport(models.TransientModel):
    _name = 'hr.payroll.excel.report.wizard'
    _description = 'Hr PayRoll Excel Report'

    start_date = fields.Datetime('Start date')
    end_date = fields.Datetime('End date')
    attachment = fields.Binary('File')
    attach_name = fields.Char('Attachment Name')
    summary_file = fields.Binary('Fleet Vehicle  Usage Report')
    file_name = fields.Char('File Name')
    report_printed = fields.Boolean('Fleet Vehicle  Usage Report')
    current_time = fields.Date('Current Time', default=lambda self: fields.Datetime.now())
    ams_time = datetime.now() + timedelta(hours=5, minutes=30)
    date = ams_time.strftime('%d-%m-%Y %H:%M:%S')
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    employee_id = fields.Many2many('hr.employee', string='Employee')
    person_count = fields.Integer(string="Person Count", default=0)
    department_id = fields.Many2many('hr.department', string='Department')
    employee_boolean = fields.Boolean('All Employee')
    salary_strut_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')

    by_month_year = fields.Boolean('By Month Year')
    by_date_range = fields.Boolean('By Date Range ')
    by_date_range_year_month = fields.Selection([
        ('by_month_year', 'By Month/Year'),
    ], string="Select Period Type", default='by_month_year')
    selct_month = fields.Selection([
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

    # month_master = fields.Many2one('hr.payroll.month', string='Month/Year')
    year_master = fields.Many2one('hr.payroll.year', string='Year')

    @api.onchange('employee_id')
    def count_employees(self):
        for employee in self:
            employee.person_count = len(self.employee_id)

    # def add_company_header(self, row, sheet, company, bold):
    #     company_name = company.name
    #     if company.logo:
    #         image_data = io.BytesIO(base64.b64decode(company.logo))
    #         sheet.insert_image(row, 1, 'logo.png', {'image_data': image_data})

    def action_get_hr_payroll_excel_report(self):
        workbook = xlwt.Workbook()
        worksheet1 = workbook.add_sheet('Attendance Sheet')
        design_2 = easyxf('align: horiz center;pattern: pattern solid, fore_colour 0x33; font: color black;')
        design_3 = easyxf('align: horiz right;font: italic on')
        design_4 = easyxf('align: horiz right;')
        design_5 = easyxf('align: horiz left;')
        design_6 = easyxf('align: horiz center;')
        design_7 = easyxf('align: horiz center;font: bold 1;')
        design_8 = easyxf('align: horiz left;')
        design_9 = easyxf('align: horiz right;')
        design_12 = easyxf('align: horiz right; pattern: pattern solid, fore_colour gray25;font: bold 1;')
        design_13 = easyxf('align: horiz center;font: bold 1;pattern: pattern solid, fore_colour grey25;')
        design_14 = easyxf('align: horiz left;font: bold 1;pattern: pattern solid, fore_colour gray25;')
        design_15 = easyxf('align: horiz left;font: bold 1;pattern: pattern solid, fore_colour grey25;')
        design_16 = easyxf('align: horiz center;')
        design_17 = easyxf('align: horiz left;font: bold 1;pattern: pattern solid, fore_colour grey25;')
        design_18 = easyxf('align: horiz right;font: bold 1;pattern: pattern solid, fore_colour grey25;')

        worksheet1.col(0).width = 2000
        worksheet1.col(1).width = 6000
        worksheet1.col(2).width = 4500
        worksheet1.col(3).width = 4500
        worksheet1.col(4).width = 6000
        worksheet1.col(5).width = 4500
        worksheet1.col(6).width = 4000
        worksheet1.col(7).width = 5000
        worksheet1.col(8).width = 5000
        worksheet1.col(9).width = 4500
        worksheet1.col(10).width = 4500
        worksheet1.col(11).width = 4500
        worksheet1.col(12).width = 4500
        worksheet1.col(13).width = 4500
        worksheet1.col(14).width = 4500
        worksheet1.col(15).width = 4500
        worksheet1.col(16).width = 4500
        worksheet1.col(17).width = 4500
        worksheet1.col(18).width = 4500
        worksheet1.col(19).width = 4500
        rows = 0
        cols = 0
        serial_no = 1
        row_pq = 8
        col_pq = 5

        worksheet1.set_panes_frozen(True)
        worksheet1.set_horz_split_pos(rows + 1)

        domain1 = [
            ('employee_id', '=', self.employee_id.ids),
            ('date_months', '=', self.selct_month),
            ('date_year', '=', self.year_master.name)
        ]

        domain3 = [
            ('date_months', '=', self.selct_month),
            ('date_year', '=', self.year_master.name)
        ]

        # FUNCTION FOR DOMAIN 1
        if self.employee_id and self.selct_month and self.year_master:
            rows += 1
            worksheet1.write_merge(rows, rows, 1, 4, 'SRP RMC AND CONSTRUCTIONS', design_13)
            total_basic_salary = 0.00
            total_benefits = 0.00
            adv_loan = 0.00
            total_net_salary = 0.00
            benefit_codes = ['HRA', 'DA', 'Travel', 'Meal', 'Medical', 'Other', 'SA', 'BE', 'BC']
            adv_loan_codes = ['SAR', 'LO', ]
            payroll = self.env['hr.payslip'].sudo().sudo().search(domain1, order='date_from asc')
            if payroll:
                for val in payroll:
                    for data in val.line_ids:
                        if data.code == 'BASIC':
                            total_basic_salary += data.amount
                        elif data.code in benefit_codes:
                            total_benefits += data.amount
                        elif data.code in adv_loan_codes:
                            adv_loan += data.amount
                        elif data.code == 'NET':
                            total_net_salary += data.amount

            worksheet1.write(rows, 5, 'ACTUAL SALARY', design_17)
            worksheet1.write(rows, 6, payroll.company_id.currency_id.symbol + ' ' + str('%.2f' % total_basic_salary),
                             design_18)
            rows += 1

            worksheet1.write(rows, 5, 'BENEFITS', design_17)
            worksheet1.write(rows, 6, payroll.company_id.currency_id.symbol + ' ' + str('%.2f' % total_benefits),
                             design_18)
            rows += 1

            worksheet1.write(rows, 5, 'ADV & LOAN', design_17)
            worksheet1.write(rows, 6, payroll.company_id.currency_id.symbol + ' ' + str('%.2f' % adv_loan), design_18)
            rows += 1

            worksheet1.write(rows, 5, 'FINAL SALARY', design_17)
            worksheet1.write(rows, 6, payroll.company_id.currency_id.symbol + ' ' + str('%.2f' % total_net_salary),
                             design_18)
            rows += 2

            worksheet1.write_merge(rows, rows, 1, 6, 'EMPLOYEE PAYROLL MONTHLY SUMMARY - %s - %s ' % (
                self.selct_month, self.year_master.name), design_13)
            rows += 1

            col_1 = 0
            rows += 1

            worksheet1.write(rows, col_1, _('Sl.No'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('EMPLOYEE'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DESIGNATION'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DATE OF JOINING'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('HAND CASH'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('WORKING DAYS'), design_13)
            col_1 += 1

            salary_struc = self.env['hr.salary.rule'].sudo().search(
                [('active', '=', True)])

            # WORKING 1
            # Initialize a dictionary to store values grouped by value names
            value_data_dict = {}
            # Loop through salary_struc to populate the dictionary
            for value in salary_struc:
                value_data_dict[value.name] = []
            # Loop through payroll records to match and store values in the dictionary
            for record in payroll:
                for data in record.line_ids:
                    for value in salary_struc:
                        if data.code == value.code and data.amount > 0:
                            value_data_dict[value.name].append(data.amount)
            # Get a list of unique value names with values greater than 0
            unique_value_names = [value_name for value_name, values in value_data_dict.items() if
                                  any(v > 0 for v in values)]
            # Write the unique value names to the worksheet
            col_1 = 6  # Adjust the starting column for writing unique_value_names
            for value_name in unique_value_names:
                worksheet1.write(rows, col_1, value_name, design_13)
                col_1 += 1

            sl_no = 1
            row_pq = row_pq + 1
            col_pq = col_pq + 1
            mr_num = []
            res = []
            payroll = self.env['hr.payslip'].sudo().sudo().search(domain1, order='date_from asc')
            if payroll:
                for record in payroll:
                    if self.by_date_range_year_month == 'by_month_year':
                        if self.selct_month == record.date_months:
                            worksheet1.write(row_pq, 0, sl_no, design_7)
                            if record.employee_id.name:
                                worksheet1.write(row_pq, 1, record.employee_id.name, design_8)
                            else:
                                worksheet1.write(row_pq, 1, '-', design_7)
                            if record.employee_id.job_title:
                                worksheet1.write(row_pq, 2, record.employee_id.job_title, design_8)
                            else:
                                worksheet1.write(row_pq, 2, '-', design_7)
                            if record.employee_id.date_of_joining:
                                worksheet1.write(row_pq, 3, str(record.employee_id.date_of_joining), design_16)
                            else:
                                worksheet1.write(row_pq, 3, '-', design_7)
                            if record.employee_id.contract_id.on_hand:
                                worksheet1.write(row_pq, 4, record.employee_id.contract_id.on_hand, design_8)
                            else:
                                worksheet1.write(row_pq, 4, '-', design_7)
                            if record.employee_final_present_days:
                                worksheet1.write(row_pq, 5, record.employee_final_present_days, design_8)
                            else:
                                worksheet1.write(row_pq, 5, '-', design_7)

                            select_date_from = record.date_from
                            select_date_to = record.date_to
                            select_month_from = select_date_from.strftime("%B")
                            select_month_to = select_date_to.strftime("%B")
                            salary_struct = self.env['hr.salary.rule'].sudo().search(
                                [('active', '=', True)])

                            # Initialize a dictionary to store values grouped by value names
                            value_data_dict_employee = {}
                            # Loop through salary_struc to populate the dictionary
                            for value in salary_struc:
                                value_data_dict_employee[value.name] = []

                            # Loop through payslip line items to match and store values in the dictionary
                            for data in record.line_ids:
                                for value in salary_struc:
                                    if data.code == value.code and data.amount > 0:
                                        value_data_dict_employee[value.name].append(data.amount)

                            # Write the corresponding values to the worksheet
                            col_pq = 6  # Starting column for writing values
                            for value_name in unique_value_names:
                                values_for_name = value_data_dict_employee[value_name]
                                if values_for_name:
                                    for value in values_for_name:
                                        worksheet1.write(row_pq, col_pq,
                                                         record.company_id.currency_id.symbol + ' ' + str(
                                                             '%.2f' % value), design_9)
                                        col_pq += 1
                                else:
                                    worksheet1.write(row_pq, col_pq, '-',
                                                     design_7)  # If no values, write an empty cell
                                    col_pq += 1
                            row_pq += 1
                        sl_no += 1


            else:
                raise ValidationError(_("Alert! The Selected Month & Year contains No Records."))

        # FUNCTION FOR DOMAIN 3 (ALL EMPLOYEES)
        elif self.employee_boolean:
            rows += 1
            worksheet1.write_merge(rows, rows, 1, 4, 'SRP RMC AND CONSTRUCTIONS', design_13)
            total_basic_salary = 0.00
            total_benefits = 0.00
            adv_loan = 0.00
            total_net_salary = 0.00
            benefit_codes = ['HRA', 'DA', 'Travel', 'Meal', 'Medical', 'Other', 'SA', 'BE', 'BC']
            adv_loan_codes = ['SAR', 'LO', ]
            payroll = self.env['hr.payslip'].sudo().sudo().search(domain3, order='date_from asc')
            if payroll:
                for val in payroll:
                    for data in val.line_ids:
                        if data.code == 'BASIC':
                            total_basic_salary += data.amount
                        elif data.code in benefit_codes:
                            total_benefits += data.amount
                        elif data.code in adv_loan_codes:
                            adv_loan += data.amount
                        elif data.code == 'NET':
                            total_net_salary += data.amount

            worksheet1.write(rows, 5, 'ACTUAL SALARY', design_17)
            worksheet1.write(rows, 6,
                             payroll.company_id.currency_id.symbol + ' ' + str('%.2f' % total_basic_salary),
                             design_18)
            rows += 1

            worksheet1.write(rows, 5, 'BENEFITS', design_17)
            worksheet1.write(rows, 6, payroll.company_id.currency_id.symbol + ' ' + str('%.2f' % total_benefits),
                             design_18)
            rows += 1

            worksheet1.write(rows, 5, 'ADV & LOAN', design_17)
            worksheet1.write(rows, 6, payroll.company_id.currency_id.symbol + ' ' + str('%.2f' % adv_loan),
                             design_18)
            rows += 1

            worksheet1.write(rows, 5, 'FINAL SALARY', design_17)
            worksheet1.write(rows, 6, payroll.company_id.currency_id.symbol + ' ' + str('%.2f' % total_net_salary),
                             design_18)
            rows += 2

            worksheet1.write_merge(rows, rows, 1, 6, 'EMPLOYEE PAYROLL MONTHLY SUMMARY - %s - %s ' % (
                self.selct_month, self.year_master.name), design_13)
            rows += 1

            col_1 = 0
            rows += 1

            worksheet1.write(rows, col_1, _('Sl.No'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('EMPLOYEE'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DESIGNATION'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DATE OF JOINING'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('HAND CASH'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('WORKING DAYS'), design_13)
            col_1 += 1

            salary_struc = self.env['hr.salary.rule'].sudo().search(
                [('active', '=', True)])

            # WORKING 1
            # Initialize a dictionary to store values grouped by value names
            value_data_dict = {}
            # Loop through salary_struc to populate the dictionary
            for value in salary_struc:
                value_data_dict[value.name] = []
            # Loop through payroll records to match and store values in the dictionary
            for record in payroll:
                for data in record.line_ids:
                    for value in salary_struc:
                        if data.code == value.code and data.amount > 0:
                            value_data_dict[value.name].append(data.amount)
            # Get a list of unique value names with values greater than 0
            unique_value_names = [value_name for value_name, values in value_data_dict.items() if
                                  any(v > 0 for v in values)]
            # Write the unique value names to the worksheet
            col_1 = 6  # Adjust the starting column for writing unique_value_names
            for value_name in unique_value_names:
                worksheet1.write(rows, col_1, value_name, design_13)
                col_1 += 1

            sl_no = 1
            row_pq = row_pq + 1
            col_pq = col_pq + 1
            mr_num = []
            res = []
            payroll = self.env['hr.payslip'].sudo().sudo().search(domain3, order='date_from asc')
            if payroll:
                for record in payroll:
                    if self.by_date_range_year_month == 'by_month_year':
                        if self.selct_month == record.date_months:
                            worksheet1.write(row_pq, 0, sl_no, design_7)
                            if record.employee_id.name:
                                worksheet1.write(row_pq, 1, record.employee_id.name, design_8)
                            else:
                                worksheet1.write(row_pq, 1, '-', design_7)
                            if record.employee_id.job_title:
                                worksheet1.write(row_pq, 2, record.employee_id.job_title, design_8)
                            else:
                                worksheet1.write(row_pq, 2, '-', design_7)
                            if record.employee_id.date_of_joining:
                                worksheet1.write(row_pq, 3, str(record.employee_id.date_of_joining), design_16)
                            else:
                                worksheet1.write(row_pq, 3, '-', design_7)
                            if record.employee_id.contract_id.on_hand:
                                worksheet1.write(row_pq, 4, record.employee_id.contract_id.on_hand, design_8)
                            else:
                                worksheet1.write(row_pq, 4, '-', design_7)
                            if record.employee_final_present_days:
                                worksheet1.write(row_pq, 5, record.employee_final_present_days, design_8)
                            else:
                                worksheet1.write(row_pq, 5, '-', design_7)

                            select_date_from = record.date_from
                            select_date_to = record.date_to
                            select_month_from = select_date_from.strftime("%B")
                            select_month_to = select_date_to.strftime("%B")
                            salary_struct = self.env['hr.salary.rule'].sudo().search(
                                [('active', '=', True)])

                            # Initialize a dictionary to store values grouped by value names
                            value_data_dict_employee = {}
                            # Loop through salary_struc to populate the dictionary
                            for value in salary_struc:
                                value_data_dict_employee[value.name] = []

                            # Loop through payslip line items to match and store values in the dictionary
                            for data in record.line_ids:
                                for value in salary_struc:
                                    if data.code == value.code and data.amount > 0:
                                        value_data_dict_employee[value.name].append(data.amount)

                            # Write the corresponding values to the worksheet
                            col_pq = 6  # Starting column for writing values
                            for value_name in unique_value_names:
                                values_for_name = value_data_dict_employee[value_name]
                                if values_for_name:
                                    for value in values_for_name:
                                        worksheet1.write(row_pq, col_pq,
                                                         record.company_id.currency_id.symbol + ' ' + str(
                                                             '%.2f' % value), design_9)
                                        col_pq += 1
                                else:
                                    worksheet1.write(row_pq, col_pq, '-',
                                                     design_7)  # If no values, write an empty cell
                                    col_pq += 1
                            row_pq += 1
                        sl_no += 1


            else:
                raise ValidationError(_("Alert! The Selected Month & Year contains No Records."))

        fp = BytesIO()
        o = workbook.save(fp)
        fp.read()
        excel_file = base64.b64encode(fp.getvalue())
        self.write({'summary_file': excel_file, 'file_name': 'HR Payroll Excel Report - [ %s ].xls' % self.date,
                    'report_printed': True})
        fp.close()
        return {
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'hr.payroll.excel.report.wizard',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new',
        }
