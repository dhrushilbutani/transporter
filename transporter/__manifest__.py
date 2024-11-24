# -*- coding: utf-8 -*-
{
    'name': "Transporter",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'sale_management', 'stock','delivery'],

    # always loaded
    'data': [
        'data/sequence.xml',
        'data/data.xml',

        'security/ir.model.access.csv',

        'views/home.xml',
        'views/create_order.xml',
        'views/transport_vehicle.xml',
        'views/transport_category.xml',
        'views/transport_subcategory.xml',
        'views/sale_order_view.xml',
        'views/view_order.xml',
        'views/edit_order.xml',
        'views/register_vehicle.xml',
        'views/thank_you_register_vehicle.xml',
        'views/view_vechile.xml',
        'views/update_vechile.xml',

        'views/menu.xml'

    ],
    'assets': {
        'web.assets_frontend': [
            'transporter/static/src/js/transport.js'
        ],
    }
}