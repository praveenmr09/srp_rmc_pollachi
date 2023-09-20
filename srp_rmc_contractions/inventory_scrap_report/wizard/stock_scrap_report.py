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
    _description = 'Wizard Report'

    start_date = fields.Date(string='Attendance Status', required=True)

    # def print_attendance_report_pdf(self):
    #     data = {
    #         'ids': self.ids,
    #         'model': self._name,
    #         'date': self.start_date,
    #         'depart_name_id': self.depart_name_id.name,
    #         'all_department': self.all_department
    #     }
    #     return self.env.ref('attendance_report.report_attendance_pdf').report_action(self, data=data)
