# -*- coding: utf-8 -*-
#################################################################################


from odoo import api, fields, models, _
from datetime import datetime


# WIZARD CLASS RENT INVOICE OPTIONS
class RentalInvoiceOption(models.TransientModel):
    _name = "rent.invoice.options"
    _description = 'Rental Invoice Option'

    rent_contract_ref = fields.Char(string="Reference")
    mobile = fields.Char(string="Mobile")
    partner_id = fields.Many2one('res.partner', string="Reference")
    tax_options = fields.Selection([
        ('include_tax', 'Include Tax'),
        ('exclude_tax', 'Exclude Tax'),
    ], string='Unit', default='Create Invoice with?')
    journal_id = fields.Many2one('account.journal', string='Journal')

    @api.onchange('tax_options')
    def _define_tax_options(self):
        if self.tax_options == 'include_tax':
            self.journal_id = 9
        else:
            self.journal_id = 1

    def create_regular_tax_invoice(self):
        if self.env.context.get('active_model') == 'car.rental.contract':
            active_id = self.env.context.get('active_id', False)
            rental_contract = self.env['car.rental.contract'].search([('id', '=', active_id)])
            if self.tax_options == 'exclude_tax':
                # Call the method to create an invoice (assuming it's defined on the car.rental.contract model)
                rental_contract.create_invoice()
            if self.tax_options == 'include_tax':
                # Call the method to create a tax-inclusive invoice (assuming it's defined on the car.rental.contract
                # model)
                rental_contract.create_tax_invoice()





