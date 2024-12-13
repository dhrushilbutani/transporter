from odoo import models,fields,api
from odoo.exceptions import ValidationError
import requests

class ResPartner(models.Model):
    _inherit = "res.partner"

    total_order = fields.Float(string="Order Amount", compute="_compute_total_history")
    order_commision = fields.Float(string="Commision Amount", compute="_compute_total_history")
    total_order_amount_with_commision = fields.Float(string="Total Amount", compute="_compute_total_history")
    total_earnings = fields.Float(string="Total Earning",compute="_compute_total_history")
    earning_commission = fields.Float(string="Earning Commission Amount", compute="_compute_total_history")
    total_withdrawal = fields.Float(string="Total Withdrawal",compute="_compute_total_history")
    remaning = fields.Float(string="Remaning",compute="_compute_total_history")
    transcation_history_ids = fields.One2many("transaction.history","partner_id")
    razorpay_id = fields.Char()

    def create_partner_in_razorpay(self):
        self.ensure_one()
        payment_provider_id = self.env['payment.provider'].search([('code', '=', 'razorpay')], limit=1)
        if not payment_provider_id:
            raise ValidationError("Razorpay payment provider not found.")
        key_id = payment_provider_id.razorpay_key_id
        key_secret = payment_provider_id.razorpay_key_secret
        url = "https://api.razorpay.com//v1/contacts"
        header = {"content-type": "application/json"}
        user_id = self.env['res.users'].search([("partner_id",'=',self.id)],limit=1)
        data = {
            "name": self.name,
            "email": self.email or "",
            "contact": self.phone or self.mobile or "",
            "type": "vendor",
            "reference_id": self.name,

        }
        res = requests.post(url, headers=header, json=data, auth=(key_id, key_secret))
        print(res.status_code)
        if res.status_code != 200:
            raise ValidationError(res.text)
        else:
            res = res.json()
            print(res)
            self.razorpay_id = res['id']


    def _compute_total_history(self):
        delivery_product_id = self.env.ref('delivery.product_product_delivery_product_template').product_variant_id
        commision_product_id = self.env.ref('transporter.product_product_commision_product_template').product_variant_id
        for rec in self:
            user_ids = self.env['res.users'].search([('partner_id','=',rec.id)])
            vechilce_ids = self.env['transport.vehicle'].search([('create_uid','in',user_ids.ids)])
            vendor_sale_order_ids = self.env['sale.order'].search([('vehicle_id','in',vechilce_ids.ids)])
            customer_sale_order_ids = self.env['sale.order'].search([('create_uid','in',user_ids.ids)])

            total_order = sum(customer_sale_order_ids.order_line.filtered(lambda x:x.product_id == delivery_product_id).mapped('price_total'))
            order_commision = sum(customer_sale_order_ids.order_line.filtered(lambda x:x.product_id == commision_product_id).mapped('price_total'))
            invoiced_sale_order_ids_vendor = vendor_sale_order_ids.filtered(lambda x:x.invoice_status == 'invoiced')

            total_earnings = sum(invoiced_sale_order_ids_vendor.order_line.filtered(lambda x:x.product_id == delivery_product_id).mapped('price_total'))
            earning_commission =  sum(invoiced_sale_order_ids_vendor.order_line.filtered(lambda x:x.product_id == commision_product_id).mapped('price_total'))
            total_withdrawal = sum(rec.transcation_history_ids.mapped('amount'))

            rec.total_order = total_order
            rec.total_earnings = total_earnings
            rec.total_withdrawal = total_withdrawal
            rec.remaning = total_earnings - total_withdrawal
            rec.order_commision = order_commision
            rec.earning_commission = earning_commission
            rec.total_order_amount_with_commision = rec.total_order + rec.order_commision

    def view_order_history(self):
        user_ids = self.env['res.users'].search([('partner_id', '=', self.id)])
        customer_sale_order_ids = self.env['sale.order'].search([('create_uid', 'in', user_ids.ids)])
        return {
            "name" : "Order",
            "type" : "ir.actions.act_window",
            "res_model" : "sale.order",
            "view_mode" : "tree,form",
            "domain" : [('id','in',customer_sale_order_ids.ids)]

        }

    def view_earning_history(self):
        user_ids = self.env['res.users'].search([('partner_id', '=', self.id)])
        vechilce_ids = self.env['transport.vehicle'].search([('create_uid', 'in', user_ids.ids)])
        vendor_sale_order_ids = self.env['sale.order'].search([('vehicle_id', 'in', vechilce_ids.ids),('invoice_status','=','invoiced')])
        return {
            "name": "Order",
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "view_mode": "tree,form",
            "domain": [('id', 'in', vendor_sale_order_ids.ids)]

        }


    def create_payment(self):
        context = self.env.context.copy()
        context['default_partner_id'] = self.id
        context['default_max_amount'] = self.remaning
        if  not self.bank_ids:
            raise ValidationError("No bank account found for this partner.")
        context['default_account_id'] = self.bank_ids[0].id

        return {
            "name" : "Payout",
            "type" : "ir.actions.act_window",
            "res_model" : "create.payment.popup",
            "view_mode" : "form",
            "context" : context,
            "target" : "new"
        }