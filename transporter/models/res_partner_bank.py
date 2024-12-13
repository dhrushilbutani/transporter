from odoo import models,fields,api
from odoo.exceptions import ValidationError
import requests

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    ifsc_code = fields.Char("IFSC Code",required=True)
    razorpay_id = fields.Char()

    def create_account_in_razorpay(self):
        self.ensure_one()
        payment_provider_id = self.env['payment.provider'].search([('code', '=', 'razorpay')], limit=1)
        if not payment_provider_id:
            raise ValidationError("Razorpay payment provider not found.")
        key_id = payment_provider_id.razorpay_key_id
        key_secret = payment_provider_id.razorpay_key_secret
        url = "https://api.razorpay.com//v1/fund_accounts"
        header = {"content-type": "application/json"}
        if not self.partner_id.razorpay_id:
            self.partner_id.create_partner_in_razorpay()
        data = {
                  "contact_id": self.partner_id.razorpay_id,
                  "account_type":"bank_account",
                  "bank_account":{
                    "name":self.partner_id.name,
                    "ifsc":self.ifsc_code,
                    "account_number": self.acc_number
                  }
                }
        res = requests.post(url, headers=header, json=data, auth=(key_id, key_secret))
        print(res.status_code)
        if res.status_code != 200:

            raise ValidationError(res.text)
        else:
            res = res.json()
            print(res)
            self.razorpay_id = res['id']