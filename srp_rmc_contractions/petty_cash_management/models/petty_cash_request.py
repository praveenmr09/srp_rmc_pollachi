from odoo import models, fields, api, _
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


# CLASS PETTY CASH REQUEST
class PettyCashRequest(models.Model):
    _name = "petty.cash.request"
    _description = "Petty Cash Request"

    name = fields.Char("Reference", default='New')
    petty_cash_journal = fields.Many2one('account.journal', string='Petty Cash Journal', default=10)
    request_amount = fields.Monetary("Request Amount", store=True, currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  default=lambda self: self.env.company.currency_id)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
    ], string='State', default='draft', tracking=True)
    line_ids = fields.One2many('petty.cash.details', 'petty_cash_request_id', string='Petty Cash Details')
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
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')

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

    # FUNCTION FOR CREATING SEQUENCE (REFERENCE ID)
    @api.model
    def create(self, values):
        values['name'] = self.sudo().env['ir.sequence'].get('petty.cash.request') or '/'
        res = super(PettyCashRequest, self).create(values)
        return res

    def request_cash(self):
        if self.request_amount <= 0.00:
            raise ValidationError("Alert, Mr. %s.\nThe Request Amount "
                                  "Should not be Zero, Kindly Check it" % self.env.user.name)
        self.write({'state': 'request'})

    def approve_request(self):
        self.write({'state': 'approved'})

    def reject_request(self):
        self.write({'state': 'reject'})

    def reset_to_draft(self):
        self.write({'state': 'draft'})

    def default_get(self, fields_list):
        defaults = super(PettyCashRequest, self).default_get(fields_list)
        supplier_name = self.env['hr.employee'].search([])
        partner_id = []
        serial_number = 1
        for partner_name in supplier_name:
            new_rate_vals = {
                'employee_id': partner_name.id,
                's_no': str(serial_number),
            }
            partner_id.append((0, 0, new_rate_vals))
            serial_number += 1
        defaults['line_ids'] = partner_id
        return defaults


# ONE2MANY CLASS PETTY CASH DETAILS
class PettyCashDetails(models.Model):
    _name = "petty.cash.details"
    _description = "Petty Cash details"

    petty_cash_request_id = fields.Many2one('petty.cash.request', string='Petty Cash')
    s_no = fields.Integer(string='S.No', compute='_compute_serial_number')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    amount = fields.Monetary("Requested Amount", store=True, currency_field='currency_id', tracking=True)
    given_amount = fields.Monetary("Approved Amount", store=True, currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  default=lambda self: self.env.company.currency_id)
    status = fields.Selection([
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ], string='Status', default='unpaid', tracking=True)
    payment_date = fields.Date(string='Payment Date')
    payment_reference = fields.Char(string='Payment Reference')

    @api.model
    def create_account_payment(self, amount):
        partner = self.env['res.partner'].sudo().search([('name', '=', self.employee_id.name)])

        payment_vals = {
            'payment_type': 'outbound',
            'partner_id': partner.id,
            'journal_id': self.petty_cash_request_id.petty_cash_journal.id,
            'amount': self.given_amount,
            'currency_id': self.currency_id.id,
            'ref': self.petty_cash_request_id.name,
        }

        payment = self.env['account.payment'].create(payment_vals)
        payment.action_post()
        return payment

    def generate_petty_cash(self):
        if self.given_amount <= 0.00:
            raise ValidationError("Alert, Mr. %s.\nThe Amount "
                                  "Should not be Zero, Kindly Check it" % self.env.user.name)
        # RETURN PROCESS
        payment = self.create_account_payment(self.amount)
        self.payment_reference = payment.name
        self.payment_date = payment.date
        self.given_amount = payment.amount
        self.status = 'paid'
        self.employee_id.contract_id.on_hand += self.given_amount

    # FUNCTION FOR GENERATING SERIAL NUMBER
    @api.depends('petty_cash_request_id.line_ids')
    def _compute_serial_number(self):
        for record in self:
            record.s_no = 0
        for i in self.mapped('petty_cash_request_id'):
            serial_number = 1
            for line in i.line_ids:
                line.s_no = serial_number
                serial_number += 1
