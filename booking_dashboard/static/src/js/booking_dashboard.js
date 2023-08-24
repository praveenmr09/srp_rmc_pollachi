odoo.define('booking_dashboard.dashboard_booking', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var utils = require('web.utils');
    var QWeb = core.qweb;
    var _t = core._t;
    var framework = require('web.framework');
    var datepicker = require('web.datepicker');
    var time = require('web.time');

    window.click_num = 0;
    var BookingDashBoard = AbstractAction.extend({
    template: 'BookingGeneralTemp',
        events: {
            'click #apply_filter': 'apply_filter',
        },

        init: function(parent, action) {
            this._super(parent, action);

        },

        start: function() {
            var self = this;
            var text='None'
            var date = {}
            this._rpc({
                model: 'fleet.vehicle',
                method: 'get_datas',
                args: [[],date],
            }).then(function(data) {
            console.log("ddddd",data)
                self.load_data(data)
            })
        },


        load_data: function (data) {
            var self = this;
            self.$('.filter_view_tb').html(QWeb.render('FilterView', {}));
            self.$('.table_view_tb').html(QWeb.render('TableCon', {data:data}));

            this.$el.find(".table_free").bind("click", function () {
                self.do_action({
                    type: "ir.actions.act_window",
                    res_model: "booking.wizard",
                    views: [[false, "form"]],
                    target: "new",
                    context:{
                        vehicle_id: $(this).attr("data"),
                        date: $(this).attr("box_date"),
                    },
                });
            });
        },

        apply_filter: function() {
            var self = this;
            var date = {}
            var start_date = this.$el.find('#start_date').val()
            var end_date = this.$el.find('#end_date').val()
            date['start_date'] = start_date
            date['end_date'] = end_date
            this._rpc({
                model: 'fleet.vehicle',
                method: 'get_datas',
                args: [[],date],
            }).then(function(data) {
            console.log("ddddd",data)
                self.load_data(data)
            })
            console.log("FFFFFFFFFFFFFFFFFf",start_date, end_date)
        }








    });
    core.action_registry.add("booking_dashboard", BookingDashBoard);
    return BookingDashBoard;
});