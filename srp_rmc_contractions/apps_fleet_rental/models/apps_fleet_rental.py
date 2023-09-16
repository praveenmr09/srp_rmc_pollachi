# -*- coding: utf-8 -*-
#############################################################################

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning, ValidationError
from dateutil.relativedelta import relativedelta


# CLASS FLEET RENTAL CONTRACT
class FleetRentalContract(models.Model):
    _name = 'car.rental.contract'
    _description = 'Fleet Rental Management'
    _inherit = 'mail.thread'

    @api.onchange('rent_start_date', 'rent_end_date')
    def check_availability(self):
        self.vehicle_id = ''
        fleet_obj = self.env['fleet.vehicle'].search([])
        for i in fleet_obj:
            for each in i.rental_reserved_time:

                if str(each.date_from) <= str(self.rent_start_date) <= str(each.date_to):
                    i.write({'rental_check_availability': False})
                elif str(self.rent_start_date) < str(each.date_from):
                    if str(each.date_from) <= str(self.rent_end_date) <= str(each.date_to):
                        i.write({'rental_check_availability': False})
                    elif str(self.rent_end_date) > str(each.date_to):
                        i.write({'rental_check_availability': False})
                    else:
                        i.write({'rental_check_availability': True})
                else:
                    i.write({'rental_check_availability': True})

    image = fields.Binary(related='vehicle_id.image_128', string="Image of Vehicle")
    reserved_fleet_id = fields.Many2one('rental.fleet.reserved', invisible=True, copy=False)
    name = fields.Char(string="Name", default="Draft Contract", readonly=True, copy=False)
    customer_id = fields.Many2one('res.partner', required=False, string='Customer', help="Customer")
    model_id = fields.Many2one('fleet.vehicle.model', 'Vehicle Model',
                               tracking=True, help='Model of the vehicle',
                               domain="[('vehicle_type', '=', vehicle_category)]")
    rental_type = fields.Selection(
        [('internal', 'Internal'), ('external', 'External')], string="Rental Type",
        default="internal", copy=False, track_visibility='onchange')
    vehicle_customer = fields.Selection(
        [('srp', 'SRP'), ('vendor', 'Vendor ')], string="Vehicle for Customer",
        default="srp", copy=False, track_visibility='onchange')
    car_brand = fields.Many2one('fleet.vehicle.model.brand', string="Fleet Brand", size=50,
                                related='vehicle_id.model_id.brand_id', store=True, readonly=True)
    car_color = fields.Char(string="Fleet Color", size=50, related='vehicle_id.color', store=True, copy=False,
                            default='#FFFFFF', readonly=True)
    cost = fields.Float(string="Rent Cost", help="This fields is to determine the cost of rent", required=False)
    rent_start_date = fields.Date(string="Rent Start Date", required=False,
                                  default=lambda self: fields.Datetime.now(timedelta(hours=5, minutes=30)),
                                  help="Start date of contract",
                                  track_visibility='onchange')
    rent_end_date = fields.Date(string="Rent End Date", required=False, help="End date of contract",
                                track_visibility='onchange',
                                default=lambda self: fields.Datetime.now(timedelta(hours=5, minutes=30)))
    from_date = fields.Char(string="From")
    to_date = fields.Char(string="To")
    customer_contact = fields.Char(related='customer_id.mobile', string='Contact No')
    lr_number = fields.Char(string='LR Number')
    starting_km = fields.Float(string='S.Kms', related='vehicle_id.odometer')
    ending_km = fields.Float(string='C.Kms')
    total_km = fields.Float(string='T.Kms')
    total_rent = fields.Float(string='Total Rent')
    r_rent = fields.Float(string='Received Rent')
    mode_of_payment = fields.Many2one('account.journal', domain=[('type', 'in', ['cash', 'bank'])],
                                      string='Payment Mode')
    date_of_received = fields.Date(string='Date Of Received')
    vehicle_state = fields.Selection([('un_reserved', 'Available'), ('reserved', 'Un Available')],
                                     'Vehicle Availability', tracking=True, related='vehicle_id.vehicle_state')
    driver_id = fields.Many2one('hr.employee', string='Driver',
                                domain="[('fleet_rental_driver', '=', True),('driver_state', '=', 'un_reserved')]")
    driver_licence_registration_date = fields.Date('Licence Registration Date', tracking=True,
                                                   related='driver_id.driver_licence_registration_date')
    driver_licence_expire_date = fields.Date('Licence Expire Date', tracking=True,
                                             related='driver_id.driver_licence_expire_date')
    driver_licence_no = fields.Char('Licence No', tracking=True,
                                    related='driver_id.driver_licence_no')
    driver_state = fields.Selection([('un_reserved', 'Available'), ('reserved', 'Un Available')],
                                    'Driver State', tracking=True, related='driver_id.driver_state')
    remarks = fields.Text(string='Remarks')
    state = fields.Selection(
        [('draft', 'Draft'), ('reserved', 'Reserved'), ('running', 'Rent Scheduled'), ('cancel', 'Cancel'),
         ('checking', 'Checking'), ('invoice', 'Invoiced'), ('done', 'Done')], string="State",
        default="draft", copy=False, track_visibility='onchange')
    notes = fields.Text(string="Details & Notes")
    cost_generated = fields.Float(string='Recurring Cost',
                                  help="Costs paid at regular intervals, depending on the cost frequency")
    cost_frequency = fields.Selection([('no', 'No'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'),
                                       ('yearly', 'Yearly')], string="Recurring Cost Frequency",
                                      help='Frequency of the recurring cost', required=False)
    journal_type = fields.Many2one('account.journal', 'Journal',
                                   default=lambda self: self.env['account.journal'].search([('id', '=', 1)]))
    account_type = fields.Many2one('account.account', 'Account',
                                   default=lambda self: self.env['account.account'].search([('id', '=', 17)]))
    recurring_line = fields.One2many('fleet.rental.line', 'rental_number', readonly=False, help="Recurring Invoices",
                                     copy=False)
    goods_line_ids = fields.One2many('fleet.goods.items', 'fleet_rent_id', help="Goods Items",
                                     copy=False)
    first_payment = fields.Float(string='First Payment',
                                 help="Transaction/Office/Contract charge amount, must paid by customer side other "
                                      "than recurrent payments",
                                 track_visibility='onchange',
                                 required=False)
    first_payment_inv = fields.Many2one('account.move', copy=False)
    first_invoice_created = fields.Boolean(string="First Invoice Created", invisible=True, copy=False)
    attachment_ids = fields.Many2many('ir.attachment', 'car_rent_checklist_ir_attachments_rel',
                                      'rental_id', 'attachment_id', string="Attachments",
                                      help="Images of the vehicle before contract/any attachments")
    total = fields.Float(string="Total (Accessories/Tools)", readonly=True, copy=False)
    tools_missing_cost = fields.Float(string="Missing Cost", readonly=True, copy=False,
                                      help='This is the total amount of missing tools/accessories')
    damage_cost = fields.Float(string="Damage Cost", copy=False)
    damage_cost_sub = fields.Float(string="Damage Cost", readonly=True, copy=False)
    total_cost = fields.Float(string="Total", readonly=True, copy=False)
    # invoice_count = fields.Integer(compute='_invoice_count', string='# Invoice', copy=False)
    # check_verify = fields.Boolean(compute='check_action_verify', copy=False)
    sales_person = fields.Many2one('res.users', string='Sales Person', default=lambda self: self.env.uid,
                                   track_visibility='always')
    invoice_count = fields.Integer(string="# Invoice", copy=False,
                                   compute='_compute_invoice_count')
    update_odometer = fields.Boolean(string='Odometer Updated')
    external_driver = fields.Char(string='External Driver')
    external_vehicle = fields.Char(string='External Vehicle')
    toll_entry_count = fields.Integer(string="Toll Entry",
                                      compute='_compute_toll_entry_count')
    exact_starting_km = fields.Float(string='S.Kms')
    license_plate = fields.Char(string='Vehicle List', related='vehicle_id.license_plate')

    # OPEN FORM - ODOMETER WIZARD
    def add_odometer_details(self):
        view_id = self.env['odometer.wizard']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Odometer Update',
            'res_model': 'odometer.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('apps_fleet_rental.view_odometer_wizard_form_view', False).id,
            'target': 'new',
            'context': {
                'default_rent_contract_ref': self.name,
                'default_vehicle_id': self.vehicle_id.id,
                'default_last_odometer': self.starting_km,
            },

        }

    # COMPUTE FUNCTION FOR TOLL ENTRY COUNT
    def _compute_toll_entry_count(self):
        self.toll_entry_count = self.env['fleet.toll.entry'].sudo().search_count(
            [('rent_contract_ref', '=', self.name)])

    # FUNCTION TO PASS TOLL GATE DETAILS THROUGH SMART BUTTON
    def get_toll_entry_details_count(self):
        self.sudo().ensure_one()
        form_view = self.sudo().env.ref('apps_fleet_rental.fleet_toll_entry_form_view')
        tree_view = self.sudo().env.ref('apps_fleet_rental.fleet_toll_entry_tree_view')
        return {
            'name': _('Toll Gate History'),
            'res_model': 'fleet.toll.entry',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('rent_contract_ref', '=', self.name)],
        }

    # OPEN WIZARD FORM ADD FUEL IN RENTAL CONTRACT
    def add_fuel_history_details(self):
        view_id = self.env['add.fuel.history.wizard']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fuel History',
            'res_model': 'add.fuel.history.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('apps_fleet_rental.view_add_fuel_history_wizard_form_view', False).id,
            'target': 'new',
            'context': {
                'default_rent_contract_ref': self.name,
                'default_vehicle_id': self.vehicle_id.id,
                'default_hide_status': 'hide_in_car_rental',
                'default_last_odometer': self.starting_km,
                'default_fueled_by_driver': self.driver_id.id,
            },

        }

    # # OPEN WIZARD FORM TOLL ENTRY
    # def add_toll_entry_details(self):
    #     view_id = self.env['fleet.toll.entry.wizard']
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Toll Entry',
    #         'res_model': 'fleet.toll.entry.wizard',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_id': view_id.id,
    #         'view_id': self.env.ref('apps_fleet_rental.view_fleet_toll_entry_wizard_form_view', False).id,
    #         'target': 'new',
    #         'context': {
    #             'default_rent_contract_ref': self.name,
    #             'default_vehicle_id': self.vehicle_id.id,
    #         },
    #     }

    # COMPUTE FUNCTION FOR INVOICE COUNT
    def _compute_invoice_count(self):
        self.invoice_count = self.env['account.move'].sudo().search_count(
            [('payment_reference', '=', self.name)])

    # FUNCTION TO PASS INVOICE DETAILS THROUGH SMART BUTTON
    def get_invoice_details(self):
        self.sudo().ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        form_view = self.sudo().env.ref('account.view_move_form')
        tree_view = self.sudo().env.ref('account.view_out_invoice_tree')
        return {
            'name': _('Rental Invoice History'),
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('payment_reference', '=', self.name)],
        }

    type_of_vehicle = fields.Selection([
        ('company', 'Company Owned'),
        ('vendor', 'Vendor Owned'),
        ('rental', 'Rental'),
    ], default='company', string='Vehicle Type')
    vehicle_category = fields.Selection([
        ("car", "Car"),
        ("bus", "Bus"),
        ("jcb", "JCB"),
        ("tractor", "Tractor"),
        ("jeep", "Jeep"),
        ("tanker_lorry", "Tanker Lorry"),
        ("tipper_lorry", "Tipper Lorry"),
        ("load_vehicle", "Load Vehicle"),
        ("truck", "Truck"),
    ], string='Vehicle Category', tracking=True)
    priority_level = fields.Selection([
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High'),
        ('4', 'Very High')],
        'Priority', tracking=True)
    transport_mode = fields.Selection([
        ('roadways', 'Road'),
        ('railways', 'Railways'),
        ('airways', 'Airways'),
        ('waterways', 'Waterways')],
        'Transportation Mode', tracking=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle List",
                                 domain="[('state_id', '=', 'Downgraded'),"
                                        "('vehicle_state', '=', 'un_reserved'),]")
    rental_duration = fields.Float(string='Duration Hrs', compute='_compute_duration_travel')
    rental_duration_days = fields.Char(string='NO of Days')
    name_of_goods = fields.Text(string='Name of Goods')
    select_total_km = fields.Selection([
        ('per_km', 'Rate/km'),
        ('per_total_km', 'Rate/ Total Km')],
        'Select Km Type', )
    rate_per_km = fields.Float(string='Rate/Km')
    rate_per_total_km = fields.Float(string='Rate/ Total Km')
    name_of_rental_purpose = fields.Char(string='Purpose of Rental Contract')
    customer_type = fields.Selection([
        ('walk_in', 'New Customer'),
        ('regular', 'Existing Customer')], default="regular", string="Customer Type")
    generate_new_customer = fields.Boolean(string='Generate a Customer')
    new_customer_phone_number = fields.Char(string='Mobile Number')
    new_customer_name = fields.Char(string='Customer Name')
    create_payment_count = fields.Integer(string="Adv.Payment ", copy=False,
                                          compute='_compute_create_payment_count')
    # rental_vehicle_history_count = fields.Integer(string='Vehicle History',
    #                                               compute='rental_vehicle_history_count_record')
    rental_driver_history_count = fields.Integer(string='Driver Vehicle History',
                                                 compute='rental_driver_history_count_record')
    vehicle_image = fields.Binary(string='Vehicle Image', related='vehicle_id.image_128')
    driver_image = fields.Binary(string='Driver Image', related='driver_id.image_1920')
    delivery_status = fields.Char(string="Rent Status", compute='_delivery_statys')
    rental_contract_line_ids = fields.One2many('car.rental.contract.line', 'rent_contract_id')
    fleet_toll_entry_ids = fields.One2many('fleet.toll.entry', 'car_rental_id', string='Fleet Toll Gate')
    total_filling_fuel = fields.Integer(string='Total Filling Fuel', related='vehicle_id.total_filling_fuel')

    # RENTAL CURRENT STATUS DISPLAYED AS A WIDGETS ON THE FORM
    @api.onchange('state')
    @api.depends('state')
    def _delivery_statys(self):
        for order in self:
            if order.mapped('state'):
                status = order.mapped('state')
                res = all(ele == status[0] for ele in status)
                if res:
                    if status[0] == 'reserved':
                        order.delivery_status = '🚚 Trip Schedule Reserved'
                    elif status[0] in 'draft':
                        order.delivery_status = '🚚 Trip Schedule Waiting'
                    elif status[0] in 'checking':
                        order.delivery_status = '🚚 Trip Schedule Checking'
                    elif status[0] in 'running':
                        order.delivery_status = '🚚 Trip Scheduled'
                    elif status[0] in 'invoice':
                        order.delivery_status = '🚚 Trip Scheduled Invoiced'
                    elif status[0] in 'done':
                        order.delivery_status = '🚚 Schedule Done'
                    else:
                        order.delivery_status = '🚚 Trip Schedule Cancelled'
            else:
                order.delivery_status = '🚚No Trip Scheduled'

    # COMPUTE FUNCTION FOR RENTAL DRIVER HISTORY COUNT
    def rental_driver_history_count_record(self):
        self.rental_driver_history_count = self.env['fleet.vehicle.assignation.log'].sudo(). \
            search_count([('rental_contract_reference', '=', self.name)])

    # def rental_vehicle_history_count_record(self):
    #     self.rental_vehicle_history_count = self.env['vehicle.trip.history'].sudo().search_count(
    #         [('source_document', '=', self.name)])

    # COMPUTE FUNCTION FOR CREATE PAYMENT COUNT
    def _compute_create_payment_count(self):
        self.create_payment_count = self.env['account.payment'].sudo().search_count(
            [('ref', '=', self.name)])

    # FUNCTION TO PASS RENTAL DRIVER HISTORY COUNT THROUGH SMART BUTTON
    def rental_driver_history_record(self):
        tree_view = self.sudo().env.ref('hr_fleet.fleet_vehicle_assignation_log_view_list')
        return {
            'name': _('Rental Fleet Driver Trip History'),
            'res_model': 'fleet.vehicle.assignation.log',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'views': [(tree_view.id, 'tree')],
            'domain': [('rental_contract_reference', '=', self.name)],
        }

    # def rental_vehicle_history_record(self):
    #     form_view = self.sudo().env.ref('apps_fleet_rental.view_vehicle_trip_history_tree')
    #     tree_view = self.sudo().env.ref('apps_fleet_rental.view_vehicle_trip_history_form')
    #     return {
    #         'name': _('Rental Fleet Vehicle Trip History'),
    #         'res_model': 'vehicle.trip.history',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'tree,form',
    #         'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
    #         'domain': [('source_document', '=', self.name)],
    #     }

    # ONCHANGE FUNCTION FOR FINDING THE DURATION
    @api.onchange('rent_start_date', 'rent_end_date')
    def _compute_duration_travel(self):
        for rec in self:
            if rec.rent_start_date and rec.rent_end_date:
                # datetimeFormat = '%Y-%m-%d %H:%M:%S'
                datetimeFormat = '%Y-%m-%d'
                date1 = rec.rent_start_date.strftime(datetimeFormat)
                date2 = rec.rent_end_date.strftime(datetimeFormat)
                date11 = datetime.strptime(date1, datetimeFormat)
                date12 = datetime.strptime(date2, datetimeFormat)
                timedelta = date12 - date11
                days = timedelta.days
                seconds = timedelta.seconds
                h = int(seconds // 3600)
                m = int((seconds % 3600) // 60)
                duration_hour = days * 24 + h + m / 60
                rec.rental_duration = duration_hour
                rec.rental_duration_days = days
            else:
                rec.rental_duration = 0.0

    # BUTTON FUNCTION TO GENERATE THE RENTAL INVOICE
    # @api.constrains('select_total_km', 'rate_per_km')
    def create_invoice(self):
        # if not self.rate_per_km and self.total_km:
        #     raise ValidationError("Alert, Mr. %s.\nThe Rental Rate Per KM & Total Km is Zero. it should be Greater "
        #                           "than Zero, Kindly Check it" % self.env.user.name)
        # if self.rate_per_km or self.rate_per_total_km <= 0.00:
        #     raise ValidationError("Alert, Mr. %s.\nThe Rental Rate Per Total KM, it should be Greater "
        #                           "than Zero, Kindly Check it" % self.env.user.name)

        for record in self:
            if record.select_total_km == 'per_km':
                if record.rate_per_km <= 0.00:
                    raise ValidationError(
                        _("Alert, Mr. %s.\nThe Rental Rate Per KM "
                          "should be Greater than Zero. Kindly Check it") % self.env.user.name)

            elif record.select_total_km == 'per_total_km':
                if record.rate_per_total_km <= 0.00:
                    raise ValidationError(
                        _("Alert, Mr. %s.\nThe Rental Rate Per Total KM "
                          "should be Greater than Zero. Kindly Check it") % self.env.user.name)


        # if self.total_km <= 0.00:
        #     raise ValidationError("Alert, Mr. %s.\nThe Rental Total Km is Zero. it should be Greater "
        #                           "than Zero Or Starting KM, Kindly Check it" % self.env.user.name)

        else:
            account_move = self.env["account.move"]
            order_line = [(5, 0, 0)]
            for rent in self.rental_contract_line_ids:
                order_line.append((0, 0, {
                    'product_id': 1,
                    # 'name': f"{self.name_of_rental_purpose} ({self.name_of_goods})",
                    # 'name': f"{self.name_of_rental_purpose + self.name_of_goods}",
                    'trips_starts_from': rent.trips_starts_from,
                    'trips_ends_at': rent.trips_ends_at,
                    'duration': rent.duration,
                    'quantity': rent.rent_contract_id.total_km if rent.rent_contract_id.rate_per_km else 1,
                    'account_id': 39,
                    'tax_ids': False,
                    'price_unit': rent.rent_contract_id.rate_per_km
                    if rent.rent_contract_id.rate_per_km else rent.rent_contract_id.rate_per_total_km,
                }))
            account_move.sudo().create({
                'move_type': 'out_invoice',
                'ref': self.name,
                'partner_id': self.customer_id.id,
                'transport_mode': self.transport_mode,
                'date_of_supply': self.create_date,
                'vehicle_id': self.vehicle_id.id,
                'payment_reference': self.name,
                'journal_id': 1,
                'l10n_in_gst_treatment': 'unregistered',
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': order_line,
            })
            self.write({
                'state': 'invoice',
            })

            return True

    # BUTTON FUNCTION TO GENERATE THE RENTAL taz INVOICE
    def create_tax_invoice(self):
        for record in self:
            if record.select_total_km == 'per_km':
                if record.rate_per_km <= 0.00:
                    raise ValidationError(
                        _("Alert, Mr. %s.\nThe Rental Rate Per KM "
                          "should be Greater than Zero. Kindly Check it") % self.env.user.name)

            elif record.select_total_km == 'per_total_km':
                if record.rate_per_total_km <= 0.00:
                    raise ValidationError(
                        _("Alert, Mr. %s.\nThe Rental Rate Per Total KM "
                          "should be Greater than Zero. Kindly Check it") % self.env.user.name)

        # if self.rate_per_km and self.rate_per_total_km <= 0.00:
        #     raise ValidationError("Alert, Mr. %s.\nThe Rental Rate Per KM, it should be Greater "
        #                           "than Zero, Kindly Check it" % self.env.user.name)
        if self.total_km <= 0.00:
            raise ValidationError("Alert, Mr. %s.\nThe Rental Total Km is Zero. it should be Greater "
                                  "than Zero Or Starting KM, Kindly Check it" % self.env.user.name)

        else:
            account_move = self.env["account.move"]
            order_line = [(5, 0, 0)]
            for rent in self.rental_contract_line_ids:
                order_line.append((0, 0, {
                    'product_id': 1,
                    # 'name': f"{self.name_of_rental_purpose} ({self.name_of_goods})",
                    # 'name': f"{self.name_of_rental_purpose + self.name_of_goods}",
                    'trips_starts_from': rent.trips_starts_from,
                    'trips_ends_at': rent.trips_ends_at,
                    'duration': rent.duration,
                    'quantity': rent.rent_contract_id.total_km,
                    'account_id': 39,
                    'price_unit': rent.rent_contract_id.rate_per_km,
                }))
            account_move.sudo().create({
                'move_type': 'out_invoice',
                'ref': self.name,
                'partner_id': self.customer_id.id,
                'transport_mode': self.transport_mode,
                'date_of_supply': self.create_date,
                'vehicle_id': self.vehicle_id.id,
                'payment_reference': self.name,
                'journal_id': 9,
                'l10n_in_gst_treatment': 'unregistered',
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': order_line,
            })
            self.write({
                'state': 'invoice',
            })

            return True

    #  TO PASS RENTAL ADVANCE PAYMENT FUNCTION THROUGH SMART BUTTON
    def payment_smart_button(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        form_view = self.env.ref('account.view_account_payment_form')
        tree_view = self.env.ref('account.view_account_payment_tree')
        ctx = {
            'default_partner_id': self.customer_id.id,
            'default_ref': self.name,
        }
        return {
            'name': _('Fleet Rental Advance Payments'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'context': ctx,
            'domain': [('ref', '=', self.name)],
        }

    # UPDATE (+ BUTTON) RENTAL CONTRACT LINE FUNCTION
    @api.onchange('rent_start_date', 'rent_end_date')
    def action_validate_rental_process(self):
        cur_date = fields.Date.today()
        for rec in self:
            # if rec.rent_start_date:
            #     if rec.rent_start_date < cur_date:
            #         raise ValidationError("Alert, Mr. %s.\nTrip Start Date should be greater than Current Date." \
            #                               % self.env.user.name)
            if rec.rent_end_date and rec.rent_start_date:
                if rec.rent_end_date < rec.rent_start_date:
                    raise ValidationError("Alert, Mr. %s.\nTrip End Date should be greater than Start Date." \
                                          % self.env.user.name)

    def action_run(self):
        self.state = 'running'

    # BUTTON (APPLY Halter CHARGES) TO APPLY Halter CHARGES IN RENTAL CONTRACT LINE
    def rent_contract_alter_charges_apply(self):
        action = self.env.ref('apps_fleet_rental.open_rent_alter_charges_action')
        result = action.read()[0]
        order_line = []
        for line in self.rental_contract_line_ids:
            order_line.append({
                'start_date': line.start_date,
                'end_date': line.end_date,
                'trips_starts_from': line.trips_starts_from,
                'trips_ends_at': line.trips_ends_at,
                'name_of_goods': line.name_of_goods,
                'trip_alter_charges': line.trip_alter_charges,
                'trip_alter_charges_remarks': line.trip_alter_charges_remarks,
                'duration': line.duration,
            })
            result['context'] = {
                'default_rent_contract_ref': self.name,
                'default_order_lines': order_line,
            }
        return result

    # BUTTON (RENTAL BUDGETS)
    def rental_open_rent_budgets_info_form_action(self):
        action = self.env.ref('apps_fleet_rental.open_rent_budgets_info_form_action')
        result = action.read()[0]
        result['context'] = {
            'default_rent_contract_ref': self.name,
            'default_vehicle_id': self.vehicle_id.id,
            'default_partner_id': self.customer_id.id,
            'default_mobile': self.customer_contact,
            'default_starting_km': self.starting_km,
            'default_closing_km': self.ending_km,
            'default_total_km': self.total_km,
            'default_driver_id': self.driver_id.id,
        }
        return result

        # BUTTON (APPLY Tax Options)

    def rent_contract_tax_options_apply(self):
        action = self.env.ref('apps_fleet_rental.open_rent_invoice_options_action')
        result = action.read()[0]
        result['context'] = {
            'default_rent_contract_ref': self.name,
            'default_partner_id': self.customer_id.id,
            'default_mobile': self.customer_contact,
            'default_tax_options': 'include_tax',
        }
        return result

    # BUTTON (SET TO DONE) TO CHANGE THE STATE INTO DONE
    def set_to_done(self):
        invoice_ids = self.env['account.move'].search([('invoice_origin', '=', self.name)])
        f = 0
        for each in invoice_ids:
            if each.payment_state != 'paid':
                f = 1
                break
        if f == 0:
            self.state = 'done'
        else:
            raise UserError("Some Invoices are pending")
        self.driver_id.driver_state = 'un_reserved'
        self.vehicle_id.vehicle_state = 'un_reserved'
        self.fleet_multiple_assign_vehicle()

    # ONCHANGE FUNCTION TO GENERATE NEW CUSTOMER IN RES PARTNER THROUGH BOOLEAN
    @api.onchange('generate_new_customer')
    def create_new_customer(self):
        if self.generate_new_customer:
            customer = self.sudo().env['res.partner'].sudo().create({
                'name': self.new_customer_name,
                'mobile': self.new_customer_phone_number,
            })
            existing_customer_record = self.sudo().env['res.partner']. \
                sudo().search([('name', '=', self.new_customer_name),
                               ('mobile', '=', self.new_customer_phone_number)])
            self.write({'customer_id': existing_customer_record.id,
                        'customer_type': 'regular'})

    # COMPUTE FUNCTION TO FIND THE INVOICE COUNT
    def _invoice_count(self):
        invoice_ids = self.env['account.move'].search([('invoice_origin', '=', self.name)])
        self.invoice_count = len(invoice_ids)

    # CONSTRAINS FUNCTION FOR STATUS BAR
    @api.constrains('state')
    def state_changer(self):
        if self.state == "running":
            state_id = self.env.ref('apps_fleet_rental.vehicle_state_rent').id
            self.vehicle_id.write({'state_id': state_id})
        elif self.state == "cancel":
            state_id = self.env.ref('apps_fleet_rental.vehicle_state_active').id
            self.vehicle_id.write({'state_id': state_id})
        elif self.state == "invoice":
            self.rent_end_date = fields.Date.today()
            state_id = self.env.ref('apps_fleet_rental.vehicle_state_active').id
            self.vehicle_id.write({'state_id': state_id})

    # CONSTRAINS FUNCTION TO UPDATE TOTAL
    # @api.constrains('checklist_line', 'damage_cost')
    # def total_updater(self):
    #     total = 0.0
    #     tools_missing_cost = 0.0
    #     for records in self.checklist_line:
    #         total += records.price
    #         if not records.checklist_active:
    #             tools_missing_cost += records.price
    #     self.total = total
    #     self.tools_missing_cost = tools_missing_cost
    #     self.damage_cost_sub = self.damage_cost
    #     self.total_cost = tools_missing_cost + self.damage_cost

    # BUTTON (+) FUNCTION TO UPDATE THE VALUES INTO RENTAL CONTRACT LINES
    def get_line_items(self):
        line_vals = []
        for line in self:
            if line.from_date and line.to_date:
                vals = [0, 0, {
                    'name_of_rental_purpose': line.name_of_rental_purpose,
                    'start_date': line.rent_start_date,
                    'end_date': line.rent_end_date,
                    'trips_starts_from': line.from_date,
                    'trips_ends_at': line.to_date,
                    'name_of_goods': line.name_of_goods,
                    'duration': line.rental_duration,
                    'rate_per_km': line.rate_per_km,
                }]
                line_vals.append(vals)
        return line_vals

    # BUTTON (+) FUNCTION TO RESTRICT THE EMPTY FIELDS
    def action_update_rental_information(self):
        rental_line_items = False
        cur_date = date.today()  # Convert to datetime.date
        for rec in self:
            if not rec.rent_start_date:
                raise ValidationError(
                    "Alert!, Mr. %s. \nPlease Enter the Period." % rec.env.user.name)

            if not rec.rent_end_date:
                raise ValidationError(
                    "Alert!, Mr. %s. \nPlease Enter the Period." % rec.env.user.name)

            if not rec.name_of_rental_purpose:
                raise ValidationError(
                    "Alert!, Mr. %s. \nPlease Enter the Purpose of Rental Contract." % rec.env.user.name)

            if not rec.name_of_goods:
                raise ValidationError(
                    "Alert!, Mr. %s. \nPlease Enter the Name of Goods." % rec.env.user.name)

            if not rec.transport_mode:
                raise ValidationError(
                    "Alert!, Mr. %s. \nPlease Enter the Transportation Mode." % rec.env.user.name)

            if not rec.from_date:
                raise ValidationError(
                    "Alert!, Mr. %s. \nPlease Enter the Trip Information." % rec.env.user.name)

            if not rec.to_date:
                raise ValidationError(
                    "Alert!, Mr. %s. \nPlease Enter the Trip Information." % rec.env.user.name)

            # if rec.rent_start_date:
            #     if rec.rent_start_date < cur_date:
            #         raise ValidationError(
            #             "Alert!, Mr. %s. \n Trip Start Date should be greater than Current Date." % rec.env.user.name)
            if rec.rent_end_date:
                if rec.rent_end_date < rec.rent_start_date:
                    raise ValidationError(
                        "Alert!, Mr. %s. \n Rental Trip End Date should be "
                        "greater than Start Date." % rec.env.user.name)
            for trip in rec.rental_contract_line_ids:
                # Convert trip.start_date to datetime.date if it's a datetime.datetime object
                if isinstance(trip.start_date, datetime):
                    trip_start_date = trip.start_date.date()
                else:
                    trip_start_date = trip.start_date

                # Convert trip.end_date to datetime.date if it's a datetime.datetime object
                if isinstance(trip.end_date, datetime):
                    trip_end_date = trip.end_date.date()
                else:
                    trip_end_date = trip.end_date

                # Convert rec.rent_start_date to datetime.date if it's a datetime.datetime object
                if isinstance(rec.rent_start_date, datetime):
                    rent_start_date = rec.rent_start_date.date()
                else:
                    rent_start_date = rec.rent_start_date

                # Convert rec.rent_end_date to datetime.date if it's a datetime.datetime object
                if isinstance(rec.rent_end_date, datetime):
                    rent_end_date = rec.rent_end_date.date()
                else:
                    rent_end_date = rec.rent_end_date

                if (trip_start_date <= rent_start_date <= trip_end_date or
                        trip_start_date <= rent_end_date <= trip_end_date):
                    raise ValidationError(
                        "Alert!, Mr. %s. \n Your selected dates overlap "
                        "with an existing rental trip. Rental Trip Start & End Date should be "
                        "greater than Current Datetime." % rec.env.user.name)
                if rec.rent_start_date < trip.start_date:
                    raise ValidationError(
                        "Alert!, Mr. %s. \n Rental Trip Start Date is earlier than "
                        "the referenced trip's Start Date." % rec.env.user.name)

        for line in self:
            line.update({
                'name_of_rental_purpose': False,
                'rate_per_km': False,
                'from_date': False,
                'to_date': False,
                'name_of_goods': False,
                'rent_start_date': False,
                'rent_end_date': False,
                'rental_contract_line_ids': line.get_line_items(),
            })
            # line.update(rental_line_items)
        return True

    # BUTTON (SCHEDULE THE TRIP) TO UPDATE VALUES INTO DRIVER VEHICLE HISTORY LOG
    def fleet_multiple_assign_vehicle(self):
        driver_history = self.env['fleet.vehicle.assignation.log']
        if self.driver_id and self.vehicle_id:
            for line in self.rental_contract_line_ids:
                driver_history.create({
                    # 'driver_id': self.driver_id.id,
                    'vehicle_id': self.vehicle_id.id,
                    'driver_employee_id': self.driver_id.id,
                    'date_start': line.start_date,
                    'date_end': line.end_date,
                    'purpose_of_rental_contract': line.name_of_rental_purpose,
                    'name_of_goods': line.name_of_goods,
                    'duration': line.duration,
                    'rental_contract_reference': self.name,
                    'rental_contract_id': self.id,
                    'transport_mode': self.transport_mode,
                    'starting_km': self.starting_km,
                    'total_km': self.total_km,
                    'rate_per_km': self.rate_per_km,
                    'source_city': line.trips_starts_from,
                    'destination_city': line.trips_ends_at,
                })
            return True

    # BUTTON FUNCTION FOR UPDATE ODOMETERS
    def rental_vehicle_update_odometer(self):
        if self.ending_km <= self.starting_km:
            raise ValidationError("Alert! Please select an Ending KM Value greater than the Starting KM.")
        else:
            self.total_km = self.ending_km - self.starting_km
            self.exact_starting_km = self.ending_km - self.total_km
            self.write({'update_odometer': True})
            self.vehicle_id.write({'odometer': self.ending_km})

    # BUTTON (CONFIRM) TO CHANGE THE STATE INTO "RESERVED"
    def action_confirm(self):
        if self.rent_end_date < self.rent_start_date:
            raise ValidationError("Alert! Please select a valid end date before confirming the rental.")

        if not self.driver_id:
            raise ValidationError("Alert! Mr. %s. Please select a driver." % self.env.user.name)

        # if not self.driver_licence_registration_date:
        #     raise ValidationError(
        #         "Alert! Mr. %s. Please mention the driver's license registration date before confirming the rental." % self.env.user.name)

        # if not self.driver_state:
        #     raise ValidationError(
        #         "Alert! Mr. %s. Please mention the driver's current status (available or not) before confirming the "
        #         "rental." % self.env.user.name)

        # if not self.driver_licence_expire_date:
        #     raise ValidationError(
        #         "Alert! Mr. %s. Please mention the driver's license expiry date before confirming the rental." % self.env.user.name)

        # if not self.driver_licence_no:
        #     raise ValidationError(
        #         "Alert! Mr. %s. Please mention the driver's license number before confirming the rental." % self.env.user.name)

        if not self.type_of_vehicle:
            raise ValidationError(
                "Alert! Mr. %s. Please select a vehicle type before confirming the rental." % self.env.user.name)

        # if not self.vehicle_category:
        #     raise ValidationError(
        #         "Alert! Mr. %s. Please select a vehicle category before confirming the rental." % self.env.user.name)

        if not self.vehicle_customer:
            raise ValidationError(
                "Alert! Mr. %s. Please select the vehicle's customer (company or vendor) before confirming the rental." % self.env.user.name)

        if not self.vehicle_id:
            raise ValidationError(
                "Alert! Mr. %s. Please select a vehicle from the list before confirming the rental." % self.env.user.name)

        if not self.vehicle_state:
            raise ValidationError(
                "Alert! Mr. %s. Please mention the vehicle's current status (available or not) before confirming the "
                "rental." % self.env.user.name)
        if not self.rental_contract_line_ids:
            raise ValidationError(
                "Alert! Mr. %s. Please mention the Rental Trip Information's into Rental Contract Lines Tab before "
                "confirming the rental." % self.env.user.name)
        check_availability = 0
        # for each in self.vehicle_id.rental_reserved_time:
        # if each.date_from <= self.rent_start_date <= each.date_to:
        #     check_availability = 1
        # elif self.rent_start_date < each.date_from:
        #     if each.date_from <= self.rent_end_date <= each.date_to:
        #         check_availability = 1
        #     elif self.rent_end_date > each.date_to:
        #         check_availability = 1
        #     else:
        #         check_availability = 0
        # else:
        #     check_availability = 0
        if check_availability == 0:
            reserved_id = self.vehicle_id.rental_reserved_time.create({'customer_id': self.customer_id.id,
                                                                       'date_from': self.rent_start_date,
                                                                       'date_to': self.rent_end_date,
                                                                       'reserved_obj': self.vehicle_id.id
                                                                       })
            self.write({'reserved_fleet_id': reserved_id.id})
        else:
            raise Warning('Sorry This vehicle is already booked by another customer')
        self.state = "reserved"
        sequence_code = 'car.rental.sequence'
        order_date = self.create_date
        order_date = str(order_date)[0:10]
        self.name = self.env['ir.sequence'] \
            .with_context(ir_sequence_date=order_date).next_by_code(sequence_code)
        mail_content = _('<h3>Order Confirmed!</h3><br/>Hi %s, <br/> This is to notify that your rental contract has '
                         'been confirmed. <br/><br/>'
                         'Please find the details below:<br/><br/>'
                         '<table><tr><td>Reference Number<td/><td> %s<td/><tr/>'
                         '<tr><td>Time Range <td/><td> %s to %s <td/><tr/><tr><td>Vehicle <td/><td> %s<td/><tr/>'
                         '<tr><td>Point Of Contact<td/><td> %s , %s<td/><tr/><table/>') % \
                       (self.customer_id.name, self.name, self.rent_start_date, self.rent_end_date,
                        self.vehicle_id.name, self.sales_person.name, self.sales_person.mobile)
        main_content = {
            'subject': _('Confirmed: %s - %s') % (self.name, self.vehicle_id.name),
            'author_id': self.env.user.partner_id.id,
            'body_html': mail_content,
            'email_to': self.customer_id.email,
        }
        self.driver_id.driver_state = 'reserved'
        self.vehicle_id.vehicle_state = 'reserved'
        self.env['mail.mail'].create(main_content).send()

    # BUTTON (CANCEL) TO CHANGE THE STATE INTO "CANCEL"
    def action_cancel(self):
        self.state = "cancel"
        if self.reserved_fleet_id:
            self.reserved_fleet_id.unlink()

    #
    # def force_checking(self):
    #     self.state = "checking"


# CLASS FLEET RENTAL LINE
class FleetRentalLine(models.Model):
    _name = 'fleet.rental.line'
    _description = 'Fleet Rental Line'

    name = fields.Char('Description')
    date_today = fields.Date('Date')
    account_info = fields.Char('Account')
    recurring_amount = fields.Float('Amount')
    rental_number = fields.Many2one('car.rental.contract', string='Rental Number')
    payment_info = fields.Char(compute='paid_info', string='Payment Stage', default='draft')
    invoice_number = fields.Integer(string='Invoice ID')
    invoice_ref = fields.Many2one('account.move', string='Invoice Ref')
    date_due = fields.Date(string='Due Date', related='invoice_ref.invoice_date_due')

    # COMPUTE FUNTION FOR PAID INFO
    def paid_info(self):
        for each in self:
            if self.env['account.move'].browse(each.invoice_number):
                each.payment_info = self.env['account.move'].browse(each.invoice_number).state
            else:
                each.payment_info = 'Record Deleted'


# INHERIT RES PARTNER
class CustomPartner(models.Model):
    _inherit = 'res.partner'

    # NAME SEARCH FUNCTION WHILE SEARCH IN THE RENTAL FORM
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', ('name', operator, name),
                      ('mobile', operator, name), ('email', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)


# CLASS FLEET GOODS ITEMS
class FleetRentalGoodsItems(models.Model):
    _name = 'fleet.goods.items'
    _description = 'Fleet Rental Goods Items'

    fleet_rent_id = fields.Many2one('car.rental.contract')
    product_id = fields.Many2one('product.product', string='Goods List')
    instruction = fields.Char(string="Description")
    quantity = fields.Integer(string="Quantity")
    unit_price = fields.Float(string="Unit Price", tracking=True)
    uom_id = fields.Many2one('uom.uom', string='UoM')
    subtotal = fields.Float(string="Subtotal", tracking=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.unit_price = rec.product_id.lst_price
                rec.uom_id = rec.product_id.uom_id.id
                rec.quantity = 1
                rec.instruction = rec.product_id.name

    @api.onchange('quantity')
    def onchange_quantity(self):
        if self.quantity and self.product_id:
            if self.unit_price:
                total = self.quantity * self.unit_price
                self.write({
                    'subtotal': total
                })


# INHERIT HR EMPLOYEE
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    fleet_rental_driver = fields.Boolean(string='Is Driver')
    driver_state = fields.Selection([('un_reserved', 'Driver Available'),
                                     ('reserved', 'Driver Not Available')],
                                    'Driver Status', tracking=True)
    driver_position = fields.Selection([('out', 'Out'), ('in', 'In')],
                                       'Driver Position', tracking=True)
    driver_licence_registration_date = fields.Date('Licence Registration Date')
    driver_licence_expire_date = fields.Date('Licence Expire Date')
    driver_licence_no = fields.Char('Licence No')
    fleet_manager = fields.Many2one('res.users', string='Fleet Manager')
    emergency_contact_one = fields.Char(string="Emergency Contact")
    emergency_contact_two = fields.Char(string="Alternative Emergency Contact")
    contract_employee = fields.Boolean(string='Contract Employee', default=True)


# INHERIT FLEET VEHICLE
class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    check_availability = fields.Boolean(default=True, copy=False)
    vehicle_state = fields.Selection([('un_reserved', 'Vehicle Available'),
                                      ('reserved', 'Vehicle Not Available')],
                                     'Vehicle Status', default='un_reserved', tracking=True)
    vehicle_position = fields.Selection([('out', 'Out'), ('in', 'In')], default='in',
                                        string='Vehicle Position', tracking=True)
    vehicle_category = fields.Selection([
        ("car", "Car"),
        ("bus", "Bus"),
        ("jcb", "JCB"),
        ("tractor", "Tractor"),
        ("jeep", "Jeep"),
        ("tanker_lorry", "Tanker Lorry"),
        ("tipper_lorry", "Tipper Lorry"),
        ("load_vehicle", "Load Vehicle"),
        ("truck", "Truck"),
    ], string='Vehicle Category', tracking=True)
    title = fields.Char(string='Title', default='Fuel Tank')
    mounting_type = fields.Selection([
        ("rubber_insulators", "Rubber Insulators or Mounts"),
        ("solid_rubber_motor_mounts", "Solid Rubber Motor Mounts"),
        ("hydraulic_motor_mounts", "Hydraulic Motor Mounts"),
        ("metal_motor_mounts", "Metal Motor Mounts"),
        ("ev_motor_mounts", "Electronic (Active) Motor Mounts"),
        ("Polyurethane_motor_mounts", "Polyurethane (PU) Motor Mounts"),
    ], string='Mounting Type', )
    tank_location = fields.Char(string='Tank Location')
    fuel_tank_monitoring_date = fields.Date(string='Date')
    content = fields.Selection([
        ("petrol", "Petrol"),
        ("diesel", "Diesel"),
        ("cng", "Compressed Natural Gas (CNG)"),
        ("lpg", "Liquid Petroleum Gas (LPG)"),
        ("others", "Others"),
    ], string='Content', default="diesel")
    fuel_unit = fields.Selection([
        ("litre", "Litres"),
        ("kg", "Kg"),
    ], string='Unit', default="litre")
    vehicle_category_id = fields.Many2one('fleet.vehicle.model.category', related='model_id.vehicle_category_id',
                                          string='Vehicle Type')

    # PAGE FUEL TANK MONITORING
    tank_capacity = fields.Float(string='Tank Capacity')
    fuel = fields.Float(string='Fuel')

    fuel_cost = fields.Float(string='Fuel Cost')
    total_filling_fuel = fields.Integer(string='Total Filling Fuel', compute='_compute_total_fuel_percentage')
    fuel_history_ids = fields.One2many('fuel.history', 'fleet_vehicle_id', string='Fuel History ids')

    total_fuel_litres = fields.Float(string='Total Fuel Litres', compute='_compute_total_fuel_litres')
    total_fuel_cost = fields.Float(string='Total Fuel Cost', compute='_compute_total_fuel_cost')
    vehicle_toll_count = fields.Integer(string='Vehicle Toll Count', compute='_compute_vehicle_toll_entry_count')
    empty_trip_details_ids = fields.One2many('empty.trip.details', 'fleet_veh_id', string='Empty Trip Details ids')

    # REGISTRY INFO
    registration_date = fields.Date(string='Registration Date')
    fc_registry_date = fields.Date(string='FC Registry Date')
    permit_registry_date = fields.Date(string='Permit Registry Date')
    insurance_registry_date = fields.Date(string='Insurance Registry Date')
    national_permit_registry_date = fields.Date(string='National Permit Registry Date')
    tn_permit_registry_date = fields.Date(string='TN Permit Registry Date')
    pollution_registry_date_1 = fields.Date(string='Pollution Registry Date 1')
    pollution_registry_date_2 = fields.Date(string='Pollution Registry Date 2')

    # EXPIRY INFO
    vehicle_fc_eligible_period = fields.Integer(string='Eligible Period After', store=True, default=1)
    fc_expiry_date = fields.Date(string='FC Expiry Date')

    vehicle_permit_eligible_period = fields.Integer(string='Eligible Period After', store=True, default=1)
    permit_expiry_date = fields.Date(string='Permit Expiry Date')

    vehicle_insurance_eligible_period = fields.Integer(string='Eligible Period After', store=True, default=1)
    insurance_expiry_date = fields.Date(string='Insurance Expiry Date')

    vehicle_national_permit_eligible_period = fields.Integer(string='Eligible Period After', store=True, default=1)
    national_permit_expiry_date = fields.Date(string='National Permit Expiry Date')

    vehicle_tn_permit_eligible_period = fields.Integer(string='Eligible Period After', store=True, default=1)
    tn_permit_expiry_date = fields.Date(string='TN Permit Expiry Date')

    vehicle_pollution_1_eligible_period = fields.Integer(string='Eligible Period After', store=True, default=1)
    pollution_expiry_date_1 = fields.Date(string='Pollution Expiry Date 1')

    vehicle_pollution_2_eligible_period = fields.Integer(string='Eligible Period After', store=True, default=1)
    pollution_expiry_date_2 = fields.Date(string='Pollution Expiry Date 2')

    @api.onchange('vehicle_fc_eligible_period', 'fc_registry_date' 'fc_expiry_date')
    def find_fc_eligible_date(self):
        for rec in self:
            if rec.fc_registry_date or rec.vehicle_fc_eligible_period > 0:
                if rec.fc_registry_date:
                    months = rec.fc_registry_date + relativedelta(months=+self.vehicle_fc_eligible_period)
                    rec.fc_expiry_date = months

    @api.onchange('vehicle_permit_eligible_period', 'permit_registry_date' 'permit_expiry_date')
    def find_permit_eligible_date(self):
        for rec in self:
            if rec.permit_registry_date or rec.vehicle_permit_eligible_period > 0:
                if rec.permit_registry_date:
                    months = rec.permit_registry_date + relativedelta(months=+self.vehicle_permit_eligible_period)
                    rec.permit_expiry_date = months

    @api.onchange('vehicle_insurance_eligible_period', 'insurance_registry_date' 'insurance_expiry_date')
    def find_insurance_eligible_date(self):
        for rec in self:
            if rec.insurance_registry_date or rec.vehicle_insurance_eligible_period > 0:
                if rec.insurance_registry_date:
                    months = rec.insurance_registry_date + relativedelta(months=+self.vehicle_insurance_eligible_period)
                    rec.insurance_expiry_date = months

    @api.onchange('vehicle_national_permit_eligible_period',
                  'national_permit_registry_date' 'national_permit_expiry_date')
    def find_national_permit_eligible_date(self):
        for rec in self:
            if rec.national_permit_registry_date or rec.vehicle_national_permit_eligible_period > 0:
                if rec.national_permit_registry_date:
                    months = rec.national_permit_registry_date + relativedelta(
                        months=+self.vehicle_national_permit_eligible_period)
                    rec.national_permit_expiry_date = months

    @api.onchange('vehicle_tn_permit_eligible_period', 'tn_permit_registry_date' 'tn_permit_expiry_date')
    def find_tn_permit_eligible_date(self):
        for rec in self:
            if rec.tn_permit_registry_date or rec.vehicle_tn_permit_eligible_period > 0:
                if rec.tn_permit_registry_date:
                    months = rec.tn_permit_registry_date + relativedelta(months=+self.vehicle_tn_permit_eligible_period)
                    rec.tn_permit_expiry_date = months

    @api.onchange('vehicle_pollution_1_eligible_period', 'pollution_registry_date_1' 'pollution_expiry_date_1')
    def find_pollution_1_eligible_date(self):
        for rec in self:
            if rec.pollution_registry_date_1 or rec.vehicle_pollution_1_eligible_period > 0:
                if rec.pollution_registry_date_1:
                    months = rec.pollution_registry_date_1 + relativedelta(
                        months=+self.vehicle_pollution_1_eligible_period)
                    rec.pollution_expiry_date_1 = months

    @api.onchange('vehicle_pollution_2_eligible_period', 'pollution_registry_date_2' 'pollution_expiry_date_2')
    def find_pollution_permit_eligible_date(self):
        for rec in self:
            if rec.pollution_registry_date_2 or rec.vehicle_pollution_2_eligible_period > 0:
                if rec.pollution_registry_date_2:
                    months = rec.pollution_registry_date_2 + relativedelta(
                        months=+self.vehicle_pollution_2_eligible_period)
                    rec.pollution_expiry_date_2 = months

    # COMPUTE FUNCTION FOR VEHICLE TOLL COUNT
    def _compute_vehicle_toll_entry_count(self):
        self.vehicle_toll_count = self.env['fleet.toll.entry'].sudo().search_count(
            [('vehicle_id', '=', self.id)])

    # FUNCTION TO VIEW VEHICLE TOLL GATE DETAILS THROUGH SMART BUTTON
    def get_toll_entry_details_count(self):
        self.sudo().ensure_one()
        form_view = self.sudo().env.ref('apps_fleet_rental.fleet_toll_entry_form_view')
        tree_view = self.sudo().env.ref('apps_fleet_rental.fleet_toll_entry_tree_view')
        return {
            'name': _('Toll Gate History'),
            'res_model': 'fleet.toll.entry',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('vehicle_id', '=', self.id)],
        }

    @api.depends('fuel_history_ids.fuel')
    def _compute_total_fuel_litres(self):
        for record in self:
            total_fuel = sum(record.fuel_history_ids.mapped('fuel'))
            record.total_fuel_litres = total_fuel

    @api.depends('fuel_history_ids.fuel_cost')
    def _compute_total_fuel_cost(self):
        for record in self:
            total_fuel = sum(record.fuel_history_ids.mapped('fuel_cost'))
            record.total_fuel_cost = total_fuel

    @api.depends('fuel', 'tank_capacity', )
    def _compute_total_fuel_percentage(self):
        for record in self:
            if record.fuel and record.tank_capacity:
                total_fuel = abs(record.fuel / record.tank_capacity) * 100
                record.total_filling_fuel = total_fuel
            else:
                record.total_filling_fuel = 0.0

    # OPEN WIARD FORM ADD FUEL IN FLEET VEHICLE
    def add_fuel_history_details(self):
        view_id = self.env['add.fuel.history.wizard']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fuel History',
            'res_model': 'add.fuel.history.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('apps_fleet_rental.view_add_fuel_history_wizard_form_view', False).id,
            'target': 'new',
            'context': {
                'default_vehicle_id': self.id,
                'default_hide_status': 'hide_in_fleet_vehicle',
            },
        }


# ONE2MANY CLASS EMPTY TRIP DETAILS
class EmptyTripDetails(models.Model):
    _name = "empty.trip.details"
    _description = 'Empty Trip Details'

    fleet_veh_id = fields.Many2one('fleet.vehicle', string='Fuel Vehicle id')
    current_date = fields.Datetime(string='Date', default=lambda self: fields.Datetime.now())
    user_id = fields.Many2one('res.users', string='User Name', default=lambda self: self.env.user, readonly=True)
    last_odometer = fields.Float(string='Last Odometer')
    current_odometer = fields.Float(string='Curent Odometer')
    difference = fields.Float(string='Difference')


# CLASS FUEL HISTORY
class FuelHistory(models.Model):
    _name = "fuel.history"
    _description = 'Fuel History'

    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string='Fuel Vehicle id')
    filling_date = fields.Date(string='Filling Date')
    fueled_by = fields.Many2one('res.users', string='Fueled By')
    fueled_by_driver = fields.Many2one('hr.employee', string='Fueled By',
                                       domain="[('fleet_rental_driver', '=', True)]")
    last_odometer = fields.Float(string='Last Odometer')
    unit = fields.Selection([
        ('km', 'km'),
        ('m', 'm'),
    ], string='Unit')
    fuel = fields.Float(string='Fuel')
    fuel_cost = fields.Float(string='Fuel Cost')
    fuel_receipt = fields.Binary(string="Fuel receipt")
    reference = fields.Char(string='Reference')

    @api.onchange('model_id')
    def _onchange_fleet_category(self):
        self.sudo().write({
            'vehicle_category': self.model_id.vehicle_type,
        })


# INHERIT FLET VEHICLE MODEL
class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'

    vehicle_type = fields.Selection([
        ("car", "Car"),
        ("bus", "Bus"),
        ("jcb", "JCB"),
        ("tractor", "Tractor"),
        ("jeep", "Jeep"),
        ("tanker_lorry", "Tanker Lorry"),
        ("tipper_lorry", "Tipper Lorry"),
        ("load_vehicle", "Load Vehicle"),
        ("truck", "Truck"),
    ])
    default_fuel_type = fields.Selection(selection_add=[("petrol", "Petrol")])
    vehicle_category_id = fields.Many2one('fleet.vehicle.model.category', string='Vehicle Type')


# CLASS CAR RENTAL CONTRACT LINE
class FleetRentalContractLine(models.Model):
    _name = "car.rental.contract.line"
    _description = 'Fleet Rental Contract Line'

    trips_starts_from = fields.Char(string="From")
    update_charges = fields.Boolean(string='Select')
    trips_ends_at = fields.Char(string="To")
    duration = fields.Float(string="Duration")
    rent_date = fields.Date(string="Rent Date")
    start_date = fields.Date(string="Start Date")
    trip_alter_charges = fields.Float(string='Halter Charges')
    trip_alter_charges_remarks = fields.Text(string='Charges Remarks',
                                             placeholder='Halter Charges Remarks')
    end_date = fields.Date(string="End Date")
    rent_contract_id = fields.Many2one('car.rental.contract', string="Rental Lines")
    name_of_goods = fields.Text(string='Name of Goods')
    rate_per_km = fields.Float(string='Rate/Km')
    name_of_rental_purpose = fields.Char(string='Purpose of Rental Contract')


# CLASS FLEET VEHICLE ASSIGNATION LOG
class FleetVehicleAssignationLog(models.Model):
    _inherit = "fleet.vehicle.assignation.log"

    rental_contract_reference = fields.Char(string='Contract Ref')
    rental_contract_id = fields.Many2one('car.rental.contract', string='Contract Ref')
    vehicle_customer = fields.Selection(
        [('srp', 'SRP'), ('vendor', 'Vendor ')], string="Vehicle for Customer",
        default="srp", copy=False, track_visibility='onchange')
    transport_mode = fields.Selection([
        ('roadways', 'Road'),
        ('railways', 'Railways'),
        ('airways', 'Airways'),
        ('waterways', 'Waterways')],
        'Transportation Mode', default="roadways", tracking=True, )
    rate_per_km = fields.Float(string='Rate/Km')
    purpose_of_rental_contract = fields.Char(string='Purpose of Rental Contract')
    name_of_goods = fields.Text(string='Name of Goods')
    duration = fields.Float(string='Duration')
    starting_km = fields.Float(string='S.Kms')
    total_km = fields.Float(string='T.Kms')
    source_city = fields.Char(string="Source")
    destination_city = fields.Char(string="Destination")
    driver_id = fields.Many2one('res.partner', required=False)
