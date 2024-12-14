from odoo import models,fields,api
import requests
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    location_id = fields.Char(string="Pickup Location",required=True)
    location_dest_id = fields.Char(string="Destination Location",required=True)
    location_city = fields.Char(string="City",compute="_compute_location_city")
    location_dest_city = fields.Char(string="Destination Location",compute="_compute_location_city")
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
    razorpay_order_id = fields.Char()
    razorpay_payment_id = fields.Char()

    def _compute_location_city(self):
        for rec in self:
            location_lst = rec.location_id.split(',')
            if len(location_lst) >= 3:
                rec.location_city = location_lst[-3].strip() + ', '+ location_lst[-2].strip()
            elif  len(location_lst) >= 2:
                rec.location_city = location_lst[-2].strip()
            elif len(location_lst) >= 1:
                rec.location_city = location_lst[0].strip()
            else:
                rec.location_city = False

            location_dest_lst = rec.location_dest_id.split(',')
            if len(location_dest_lst) >= 3:
                rec.location_dest_city = location_dest_lst[-3].strip() + ', '+ location_lst[-2].strip()
            elif len(location_dest_lst) >= 2:
                rec.location_dest_city = location_dest_lst[-2].strip()
            elif len(location_dest_lst) >= 1:
                rec.location_dest_city = location_dest_lst[0].strip()
            else:
                rec.location_dest_city = False

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.delivery_status = 'todo'
        return res

    def create_order_razor_pay(self):
        self.ensure_one()
        self = self.sudo()
        payment_provider_id = self.env['payment.provider'].search([('code','=','razorpay')],limit=1)
        if not payment_provider_id:
            raise ValidationError("Razorpay payment provider not found.")
        key_id = payment_provider_id.razorpay_key_id
        key_secret = payment_provider_id.razorpay_key_secret
        url = "https://api.razorpay.com/v1/orders"
        header = {"content-type": "application/json" }
        data = {
            "amount" : self.amount_total,
            "currency": "INR",
            "receipt": self.name,
        }
        res = requests.post(url,headers=header,json=data,auth=(key_id,key_secret))
        print(res.status_code)
        if res.status_code != 200:
            return {"status" : res.status_code,"error":res.text }
        else:
            status_code = res.status_code
            res = res.json()
            print(res)
            self.razorpay_order_id = res['id']
        callback_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {"status" : status_code,
                "key_id" : key_id,
                "order_id" :  res['id'],
                "amount" : self.amount_total,
                "currency": "INR",

                "name": self.company_id.name,
                "description": "",
                "image": "",
                "callback_url": callback_url,
                "prefill": {
                    "name": self.partner_id.name,
                    "email": self.partner_id.email or False,
                    "contact": self.partner_id.phone or False
                },
                "notes": {
                    "address": "Razorpay Corporate Office"
                },
                "theme": {
                    "color": "#3399cc"
                }

                }



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


    def payment_done(self,razorpay_payment_id):
        self.ensure_one()
        self = self.sudo()
        self.razorpay_payment_id = razorpay_payment_id
        move_ids = self._create_invoices()
        move_ids.action_post()
        self.register_payment(move_ids[0])

    def register_payment(self,move_id):
        bank_journal_id = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
        if not bank_journal_id:
            raise ValidationError("Bank Journal not found")
        register_payment_id = self.env['account.payment.register'].sudo().with_context({
                'active_model': 'account.move',
                'active_ids': [move_id.id],
                'active_id': move_id.id,
            }).with_company(self.company_id.id).create({
            'journal_id' : bank_journal_id.id,
            'amount' : move_id.amount_total,
            'communication' : move_id.name
        })
        register_payment_id.action_create_payments()



