from odoo import models, fields, api, _
from datetime import date
from datetime import datetime
from odoo.exceptions import ValidationError


# CLASS PETTY CASH EXPENSE
class PettyCashExpense(models.Model):
    _name = "petty.cash.expense"
    _description = "Petty Cash Expense"

    name = fields.Char("Reference", default='New')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    payment_journal = fields.Many2one('account.journal', string='Payment Journal')
    petty_cash_journal = fields.Many2one('account.journal', string='Petty Cash Journal')
    cash_expense_date = fields.Date(string='Date', default=fields.Date.today())
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  default=lambda self: self.env.company.currency_id)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('process', 'Process Payment'),
        ('done', 'Done'),
    ], string='State', default='draft', tracking=True)
    line_ids = fields.One2many('petty.cash.expense.lines', 'petty_cash_expense_id', string='Petty Cash Ids')

    # FUNCTION FOR CREATING SEQUENCE (REFERENCE ID)
    @api.model
    def create(self, values):
        values['name'] = self.sudo().env['ir.sequence'].get('petty.cash.expense') or '/'
        res = super(PettyCashExpense, self).create(values)
        return res

    def confirm_payment(self):
        self.write({'state': 'confirm'})

    def register_payment(self):
        self.write({'state': 'process'})

    def reconcile_payment(self):
        self.write({'state': 'done'})

    def reset_to_draft(self):
        self.write({'state': 'draft'})


# CLASS PETTY CASH EXPENSE LINES
class PettyCashExpenseLines(models.Model):
    _name = "petty.cash.expense.lines"
    _description = "Petty Cash Expense Lines"

    petty_cash_expense_id = fields.Many2one('petty.cash.expense', string='Petty Cash')
    particulars = fields.Many2one('product.template', string='Particulars')
    account = fields.Many2one('account.move', string='Account')
    analytic_account = fields.Char(string='Analytic Account')
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  default=lambda self: self.env.company.currency_id)
    request_amount = fields.Monetary("Request Amount", store=True, currency_field='currency_id', tracking=True)
