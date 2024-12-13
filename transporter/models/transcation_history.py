from odoo import models,fields,api,_
from odoo.exceptions import ValidationError
import requests

class TransactionHistory(models.Model):
    _name = 'transaction.history'
    _order = "date desc"

    name = fields.Char(
        string="Name",
        required=True, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))
    partner_id = fields.Many2one("res.partner")
    amount = fields.Float("Amount")
    date = fields.Datetime(default=fields.Datetime.now())
    user_id = fields.Many2one("res.users")
    remark = fields.Char("Remark")
    account_id = fields.Many2one("res.partner.bank")
    razorpay_id = fields.Char()
    state = fields.Selection([('draft','Draft'),('approve','Approve'),('reject','Reject')],default='draft')


    def create(self,vals):
        if vals.get('name', _("New")) == _("New"):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'transcation.request') or _("New")
        return super(TransactionHistory,self).create(vals)

    def create_payout_in_razorpay(self):
        self.ensure_one()
        payment_provider_id = self.env['payment.provider'].search([('code', '=', 'razorpay')], limit=1)
        if not payment_provider_id:
            raise ValidationError("Razorpay payment provider not found.")
        key_id = payment_provider_id.razorpay_key_id
        key_secret = payment_provider_id.razorpay_key_secret
        url = "https://api.razorpay.com//v1/payouts"
        header = {"content-type": "application/json"}
        if not self.account_id.razorpay_id:
            self.account_id.create_account_in_razorpay()
        data ={
              "account_number": self.account_id.acc_number,
              "fund_account_id": self.account_id.razorpay_id,
              "amount": self.amount,
              "currency": "INR",
              "mode": "IMPS",
              "purpose": "widtharaw of vendor",
              "queue_if_low_balance": True,
              "reference_id": self.remark,
            }
        if payment_provider_id.state == 'enabled':

            res = requests.post(url, headers=header, json=data, auth=(key_id, key_secret))
            print(res.status_code)
            if res.status_code != 200:
                self.state = 'reject'
                raise ValidationError(res.text)
            else:
                res = res.json()
                print(res)
                self.state = 'approve'
                self.razorpay_id = res['id']
        else:
            self.state = 'approve'

    def action_open_multi_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Multi Payment'),
            'res_model': 'create.multi.payment',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
        }