from odoo import models, fields, api, _
from datetime import date
from datetime import datetime
from odoo.exceptions import ValidationError


# CLASS PETTY CASH REQUEST
class PettyCashRequest(models.Model):
    _name = "petty.cash.request"
    _description = "Petty Cash Request"

    name = fields.Char("Reference", default='New')
    petty_cash_journal = fields.Many2one('account.journal', string='Petty Cash Journal', default=10)
    cash_request_date = fields.Date(string='Date', default=fields.Date.today())
    request_amount = fields.Monetary("Request Amount", store=True, currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  default=lambda self: self.env.company.currency_id)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    payment_reference = fields.Many2one('account.payment', string='Payment Reference')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Requested'),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
    ], string='State', default='draft', tracking=True)
    line_ids = fields.One2many('petty.cash.details', 'petty_cash_request_id', string='Petty Cash Details')

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
    partner_id = fields.Many2one('res.partner', string='Partner')
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
