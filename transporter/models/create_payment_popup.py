from odoo import models,fields,api
from odoo.exceptions import ValidationError
from odoo import Command

class CreatePaymentPopup(models.TransientModel):
    _name = 'create.payment.popup'

    partner_id = fields.Many2one("res.partner")
    max_amount = fields.Float(string="Max Amount")
    amount = fields.Float(string="Amount")
    account_id = fields.Many2one("res.partner.bank",domain=[('partner_id','=',partner_id)],required=1)
    remark = fields.Char(string="Remark")




    def process_payment(self):
        self.ensure_one()
        if self.amount > self.max_amount:
            raise ValidationError("Payment amount exceeds the maximum allowed amount.")
        return self.do_payment()

    def do_payment(self):
        self = self.sudo()
        transcation_history_id = self.env["transaction.history"].create({
            "partner_id": self.partner_id.id,
            "amount": self.amount,
            "user_id": self.env.user.id,
            "remark": self.remark,
            "account_id": self.account_id.id,
            "date": fields.Datetime.now()
        })

        return transcation_history_id



class CreateMultiPayment(models.TransientModel):
    _name = 'create.multi.payment'

    @api.model
    def default_get(self, fields_list):
        res = super(CreateMultiPayment, self).default_get(fields_list)
        if (self.env.context.get('active_ids')):
            print("----------", self.env.context)
            transactions = self.env['transaction.history'].browse(self.env.context.get('active_ids'))
            line_ids = []
            for transaction in transactions:
                if transaction.state != 'draft':
                    raise ValidationError("Selected transaction is not in draft state.")
                line_ids.append((0, 0, {
                    'transaction_id': transaction.id
                }))
            res['line_ids'] = line_ids
        return res

    line_ids = fields.One2many("create.multi.payment.line","popup_id")

    def process_multi_payment(self):
        for line_id in self.line_ids:
            line_id.transaction_id.create_payout_in_razorpay()


class CreateMultiPaymentLine(models.TransientModel):
    _name = 'create.multi.payment.line'

    popup_id = fields.Many2one("create.multi.payment")
    transaction_id = fields.Many2one("transaction.history")
    name = fields.Char(related="transaction_id.name")
    partner_id = fields.Many2one("res.partner", related="transaction_id.partner_id")
    account_id = fields.Many2one("res.partner.bank", related="transaction_id.account_id")
    amount = fields.Float(related="transaction_id.amount")