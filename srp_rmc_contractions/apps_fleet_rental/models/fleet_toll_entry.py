# -*- coding: utf-8 -*-
#############################################################################

# CLASS REPORT FLEET RENTAL TOLL ENTRY
from odoo import models, fields, api


class FleetTollEntry(models.Model):
    _name = "fleet.toll.entry"
    _description = "Fleet Toll Entry"

    name = fields.Char("Entry Name")
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', related='car_rental_id.vehicle_id', readonly=False,
                                 store=True)
    exit_date = fields.Date("Exit Date")
    cost_amount = fields.Float("Cost Amount")
    notes = fields.Text("Notes")
    tid = fields.Char("Transaction ID")
    vendor_id = fields.Many2one('res.partner', "Vendor")
    purchaser_id = fields.Many2one('res.partner', "Driver")
    driver_id = fields.Many2one('hr.employee', string='Driver',
                                domain="[('fleet_rental_driver', '=', True)]", related='car_rental_id.driver_id',
                                readonly=False, store=True)
    rent_contract_ref = fields.Char(string="Reference", related='car_rental_id.name', readonly=False, store=True)
    # provider = fields.Many2one('tls.toll.provider', "Module",
    #                            index=True, help="Information-providing module")
    inv_ref = fields.Many2one('account.move', "Vendor Bill",
                              help="Invoice related to this toll")
    use_booster_widget = fields.Boolean("Use Booster Widget", )
    hide_route_widget = fields.Boolean("Disable Route Widget", )
    entry_name = fields.Char("Entry station", help="Name of the entry station")
    entry_lat = fields.Float("Entry lat", digits=(3, 6), help="Geographical coordinates: Latitude")
    entry_lng = fields.Float("Entry lng", digits=(3, 6), help="Geographical coordinates: Longitude")
    entry_date = fields.Datetime("Start of journey", default=fields.Datetime.now())
    exit_name = fields.Char("Exit station", help="Name of the exit station")
    exit_lat = fields.Float("Exit lat", digits=(3, 6), help="Geographical coordinates: Latitude")
    exit_lng = fields.Float("Exit lng", digits=(3, 6), help="Geographical coordinates: Longitude")
    distance = fields.Float("Distance", digits=(4, 1), help="Journey distance, km")
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    route_image = fields.Binary("Route image", help="Image file for Route widget")
    description = fields.Char("Cost Description")
    category_ids = fields.Char()
    job_id = fields.Char()
    department_id = fields.Char()
    car_rental_id = fields.Many2one('car.rental.contract', string='Rental Contract Id')
    state = fields.Selection(
        [('draft', 'Draft'), ('generated', 'Expense Generated'), ], string="State",
        default="draft", copy=False, )
    travel_details = fields.Char(string='Description', compute='_onchange_travel_details')

    @api.depends('entry_name', 'exit_name', )
    def _onchange_travel_details(self):
        if self.entry_name and self.exit_name:
            note_text = (self.entry_name + " to " + self.exit_name + " Toll ")

            self.travel_details = note_text
        else:
            self.travel_details = False

    def generate_expense(self):
        self.write({
            'state': 'generated',
        })
        self.env['hr.expense'].create({
            'name': self.travel_details,
            'product_id': 8,
            'vehicle_id': self.vehicle_id.id,
            'driver_id': self.driver_id.id,
            'reference': self.rent_contract_ref,
        })

    # INHERITS

    @api.onchange('entry_date', 'exit_date')
    def _calculate_distance(self):
        if self.entry_date and self.exit_date:
            # Calculate distance based on your logic
            self.distance = 100  # Replace with your calculation

    @api.onchange('entry_name', 'exit_name')
    def get_description(self):
        if self.entry_name and self.exit_name:
            self.description = F"{self.entry_name} — {self.exit_name}"

    @api.constrains('entry_lat', 'entry_lng', 'exit_lat', 'exit_lng')
    def drop_map_img(self):
        for toll in self:
            if toll.route_image:
                toll.write({'route_image': False})


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    toll_entries = fields.One2many('fleet.toll.entry', 'vehicle_id', string='Toll Entries')
