from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import content_disposition, Controller, request, route

class MyPortal(CustomerPortal):
    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        bank_ids = request.env['res.bank'].sudo().search([])
        values['partner_id'] = partner
        values["bank_account_ids"] = partner.bank_ids
        values["transcation_history_ids"] = partner.transcation_history_ids[::-1]
        values["bank_ids"] = bank_ids

        return request.render("portal.portal_my_home", values)

    @route("/withdraw/pay", type='http', auth="user", website=True, csrf=False)
    def withdraw_pay(self, **kw):
        amount = kw.get('donation_amount')
        bank_account_id = int(kw.get('selected_bank_account_id'))
        partner_id = request.env.user.partner_id

        payment_popup_id = request.env['create.payment.popup'].create({
            "partner_id" : partner_id.id,
            "amount" : amount,
            "account_id" : bank_account_id,
            "remark" : f"Withdraw By {partner_id.name}",
            "max_amount" : partner_id.remaning,

        })
        print(payment_popup_id)
        payment_popup_id.process_payment()
        return request.redirect("/my/home")


    @route("/add_new_bank_account", type='http', auth="user", website=True, csrf=False)
    def add_new_bank_account(self, **kw):
        print(kw)
        if kw.get('bank_id') == 'other_bank':
            bank_name = kw.get("bank_name")
            bank_id = request.env["res.bank"].sudo().create({"name" : bank_name}).id
        else:
            bank_id = int(kw.get('bank_id'))
        acc_number = kw.get("acc_number")
        ifsc_code = kw.get("ifsc_code")
        partner_id = request.env.user.partner_id
        request.env["res.partner.bank"].sudo().create({
            "acc_number": acc_number,
            "bank_id" : bank_id,
            "ifsc_code" : ifsc_code,
            "partner_id" : partner_id.id
        })
        return request.redirect("/my/home")