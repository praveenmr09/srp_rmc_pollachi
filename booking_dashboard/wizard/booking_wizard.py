from odoo import _, api, fields, models


class QuickBooking(models.TransientModel):
    _name = 'booking.wizard'
    _description = 'Booking Wizard'
    _inherit = ['mail.thread']

    date = fields.Date(string="Date")
    vehicle = fields.Many2one('fleet.vehicle')

    def tick_ok(self):
        pass

    @api.model
    def default_get(self, fields):
        res = super(QuickBooking, self).default_get(fields)
        keys = self._context.keys()
        if "date" in keys:
            res.update({"date": self._context["date"]})
        if "date" in keys:
            res.update({"vehicle": int(self._context["vehicle_id"])})

        return res
