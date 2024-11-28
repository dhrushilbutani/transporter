from odoo import models,fields,api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    location_id = fields.Char(string="Pickup Location",required=True)
    location_dest_id = fields.Char(string="Destination Location",required=True)
    subcategory_id = fields.Many2one("transport.subcategory",string="Vehicle Subcategory",required=1)
    category_id = fields.Many2one("transport.category",string="Vehicle Category",related="subcategory_id.category_id")
    vehicle_id = fields.Many2one("transport.vehicle")
    weight = fields.Float(string="Weight")
    schedule_date = fields.Datetime(string="Schedule_date Date",default=fields.datetime.now())
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    location_let = fields.Char(string="Location Lat")
    location_lng = fields.Char(string="Location Lng")
    location_dest_lat = fields.Char(string="Location Destination Lat")
    location_dest_lang = fields.Char(string="Location Destination Lng")
    user_id = fields.Many2one("res.users",domain=[])

