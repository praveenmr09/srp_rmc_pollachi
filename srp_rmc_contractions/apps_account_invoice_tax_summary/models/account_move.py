from odoo import models, fields, api, _


class InvoiceTaxSummary(models.Model):
    _name = 'invoice.tax.summary'
    _description = 'Invoice Tax Summary'

    name = fields.Char(string='Tax Name')
    cgst_amount = fields.Float(string='CGST Amount')
    sgst_amount = fields.Float(string='SGST Amount')
    igst_amount = fields.Float(string='IGST Amount')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    tax_id = fields.Many2one('account.tax', string='Tax')


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_tax_summary_ids = fields.One2many('invoice.tax.summary', 'invoice_id', string='Invoice Tax Summary')

    @api.depends('invoice_line_ids.tax_ids')
    @api.onchange('invoice_line_ids.tax_ids')
    def _compute_invoice_tax_summary(self):
        for move in self:
            tax_summary_lines = []
            for line in move.invoice_line_ids:
                cgst_amount = 0.0
                sgst_amount = 0.0
                igst_amount = 0.0
                for tax in line.tax_ids.filtered(lambda tax: tax.type_tax_use == 'sale'):
                    if tax.tax_group_id.name == 'CGST':
                        cgst_amount += line.price_subtotal * (tax.amount / 100)
                    elif tax.tax_group_id.name == 'SGST':
                        sgst_amount += line.price_subtotal * (tax.amount / 100)
                    elif tax.tax_group_id.name == 'IGST':
                        igst_amount += line.price_subtotal * (tax.amount / 100)
                tax_summary_lines.append((0, 0, {
                    'name': line.name,
                    'cgst_amount': cgst_amount,
                    'sgst_amount': sgst_amount,
                    'igst_amount': igst_amount,
                    'invoice_id': move.id,
                    'tax_id': line.tax_ids.ids[0] if line.tax_ids else False,
                }))
            move.invoice_tax_summary_ids = tax_summary_lines
