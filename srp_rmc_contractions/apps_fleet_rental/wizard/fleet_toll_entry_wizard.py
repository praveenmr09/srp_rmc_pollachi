# -*- coding: utf-8 -*-
#############################################################################

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning, ValidationError


# WIZARD CLASS - FLEET TOLL ENTRY WIZARD
class FleetTollEntryWizard(models.TransientModel):
    _name = 'fleet.toll.entry.wizard'
    _description = 'Fleet Toll Entry Wizard'

    entry_date = fields.Datetime("Start of journey", default=fields.Datetime.now())
    entry_name = fields.Char("Entry station", help="Name of the entry station")
    exit_name = fields.Char("Exit station", help="Name of the exit station")
    distance = fields.Float("Distance", digits=(4, 1), help="Journey distance, km")
    cost_amount = fields.Float("Cost Amount")
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    purchaser_id = fields.Many2one('res.partner', "Driver")
    vendor_id = fields.Many2one('res.partner', "Vendor")
    inv_ref = fields.Many2one('account.move', "Vendor Bill",
                              help="Invoice related to this toll")
    rent_contract_ref = fields.Char(string="Reference")

    def update_toll_entry_details_(self):
        self.env['fleet.toll.entry'].create({
            'rent_contract_ref': self.rent_contract_ref,
            'entry_date': self.entry_date,
            'entry_name': self.entry_name,
            'exit_name': self.exit_name,
            'distance': self.distance,
            'cost_amount': self.cost_amount,
            'vehicle_id': self.vehicle_id.id,
            'purchaser_id': self.purchaser_id.id,
            'vendor_id': self.vendor_id.id,
            'inv_ref': self.inv_ref.id,
        })
