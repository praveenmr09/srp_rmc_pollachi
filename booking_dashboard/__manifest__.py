
{
    "name": "Vehicle Booking DashBoard",
    "version": "16.0.0.0.1",
    "author": "Appscomp",
    "category": "Vehicle Booking",
    "website": "",
    "depends": ['fleet'],
    "license": "LGPL-3",
    "summary": "Vehicle Booking to Manage Reservation Details",
    "demo": [],
    "data": [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'wizard/booking_wizard.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'booking_dashboard/static/src/css/style.css',
            'booking_dashboard/static/src/js/booking_dashboard.js',
            'booking_dashboard/static/src/xml/booking_dashboard.xml',
        ],
    },
    "application": True,
}
