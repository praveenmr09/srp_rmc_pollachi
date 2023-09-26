import pytz
from odoo import api, fields, models, _
from datetime import datetime, timedelta
import xlwt
from io import BytesIO
import base64
from base64 import b64decode, b64encode
from xlwt import easyxf


class StockScrapReport(models.TransientModel):
    _name = 'stock.scrap.report'
    _description = 'Inventory Scrap Report'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    def print_stock_scrap_report_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'form': {
                'start_date': self.start_date,
                'end_date': self.end_date,
            },
        }
        return self.env.ref('inventory_scrap_report.record_stock_scrap_pdf').report_action(self, data=data)


class RentalVehicleTripWizardParser(models.AbstractModel):
    _name = 'report.inventory_scrap_report.stock_scrap_pdf_template'

    def _get_report_values(self, docids, data=None):
        start_date = data['start_date']
        end_date = data['end_date']

        if start_date:
            inventory_scrap = self.env['stock.scrap'].search([
                ('date_done', '>=', start_date),
                ('date_done', '<=', end_date),
            ], order='date_done asc')

            scrap = []
            for i in inventory_scrap:
                scrap.append(i)

        cols_heads = ['S.No', 'Reference', 'Source Document', 'Product', 'Quantity']

        return {
            'doc_ids': docids,
            'doc_model': 'stock.scrap.report',
            'data': scrap,
            'cols_heads': cols_heads,
        }
