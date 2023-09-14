from odoo import _, api, fields, models
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError, Warning, ValidationError


class QuickBooking(models.TransientModel):
    _name = 'booking.wizard'
    _description = 'Booking Wizard'
    _inherit = ['mail.thread']

    date = fields.Date(string="Date")
    vehicle = fields.Many2one('fleet.vehicle')
    driver_id = fields.Many2one('hr.employee', string='Driver')
    rent_start_date = fields.Date(string="Rent Start Date", required=False,
                                  default=lambda self: fields.Datetime.now(timedelta(hours=5, minutes=30)),
                                  help="Start date of contract")
    rent_end_date = fields.Date(string="Rent End Date", required=False, help="End date of contract",
                                default=lambda self: fields.Datetime.now(timedelta(hours=5, minutes=30)))
    from_date = fields.Char(string="From")
    to_date = fields.Char(string="To")
    customer_id = fields.Many2one('res.partner', required=False, string='Customer', help="Customer")
    name_of_rental_purpose = fields.Char(string='Purpose of Rental Contract')
    customer_type = fields.Selection([
        ('walk_in', 'New Customer'),
        ('regular', 'Existing Customer')], default="regular", string="Customer Type")
    generate_new_customer = fields.Boolean(string='Generate a Customer')
    new_customer_phone_number = fields.Char(string='Mobile Number')
    new_customer_name = fields.Char(string='Customer Name')
    name_of_goods = fields.Text(string='Name of Goods')
    duration = fields.Float(string="Duration", compute='_compute_duration_travel')
    rental_duration_days = fields.Char(string='NO of Days')

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
                rec.duration = duration_hour
                rec.rental_duration_days = days
            else:
                rec.duration = 0.0

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

    @api.onchange('rent_start_date', 'rent_end_date')
    def restrict_end_date(self):
        for rec in self:
            if rec.rent_end_date and rec.rent_start_date:
                if rec.rent_end_date < rec.rent_start_date:
                    raise ValidationError("Alert, Mr. %s.\nTrip End Date should be greater than Start Date." \
                                          % self.env.user.name)

    def tick_ok(self):
        if self.vehicle and self.driver_id:
            rental = self.env['car.rental.contract'].sudo().create({
                'customer_id': self.customer_id.id,
                'rent_start_date': self.rent_start_date,
                'rent_end_date': self.rent_end_date,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'name_of_rental_purpose': self.name_of_rental_purpose,
                'name_of_goods': self.name_of_goods,
                'driver_id': self.driver_id.id,
                'vehicle_id': self.vehicle.id,
                'state': 'draft',
            })
            fleet = self.env['fleet.vehicle'].search([])
            for vehicle in fleet:
                vehicle_id = f"{vehicle.brand_id.name}/{vehicle.model_id.name}/{vehicle.license_plate}"
                if vehicle_id == self.vehicle.name:
                    rental_line_vals = {
                        'start_date': self.rent_start_date,
                        'end_date': self.rent_end_date,
                        'name_of_rental_purpose': self.name_of_rental_purpose,
                        'name_of_goods': self.name_of_goods,
                        'trips_starts_from': self.from_date,
                        'trips_ends_at': self.to_date,
                        'driver_id': self.driver_id.id,
                        'duration': self.duration,
                    }
                    rental_line = self.env['fleet.vehicle.line'].create(rental_line_vals)
                    vehicle.write({'rental_reservation_line': [(4, rental_line.id)]})

    @api.model
    def default_get(self, fields):
        res = super(QuickBooking, self).default_get(fields)
        keys = self._context.keys()
        if "date" in keys:
            res.update({"date": self._context["date"]})
        if "date" in keys:
            res.update({"vehicle": int(self._context["vehicle_id"])})

        return res


