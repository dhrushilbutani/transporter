from odoo import models,fields,api
import requests
from odoo.exceptions import ValidationError

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
    location_dest_lng = fields.Char(string="Location Destination Lng")
    user_id = fields.Many2one("res.users",domain=[])
    transporter_user_id = fields.Many2one("res.users","Transporter User")
    delivery_status = fields.Selection([('todo','To Do'),('in_progress','In progress'),('done','Done'),('cancel','Cancel')])

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.delivery_status = 'todo'
        return res

    def get_steps(self):
        self.ensure_one()
        gmap_api_key = self.env['website'].search([]).mapped('google_places_api_key')
        if not gmap_api_key:
            raise ValidationError("Please Configure Google Map API Key")
        gmap_api_key = gmap_api_key[0]
        header = {
                'Content-Type': 'application/json'
        }
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={self.location_let},{self.location_lng}&destination={self.location_dest_lat},{self.location_dest_lng}&key={gmap_api_key}"
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            raise ValidationError("Failed to get directions")
        else:
            res = response.json()
            route = res['routes']
            legs = route[0]['legs']
            steps = legs[0]['steps']
            direction_list = [{"lat" : self.location_let,"lng": self.location_lng}]
            for step in steps:
                direction_list.append(
                    step["end_location"]
                )
            return direction_list