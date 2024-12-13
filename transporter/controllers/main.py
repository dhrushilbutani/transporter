from odoo import http
from odoo.http import request
from datetime import datetime
import base64



class TransportWebsite(http.Controller):

    @http.route('/',type='http',auth='public',methods=["GET","POST"], csrf=False, website=True)
    def home(self):
        transport_category_ids = request.env["transport.category"].sudo().search([])
        return request.render('transporter.homepage', {
            "transport_category_ids": transport_category_ids
        })

    @http.route('/home', type='http', auth='public',methods=["GET","POST"], csrf=False, website=True)
    def home_page(self):
        transport_category_ids = request.env["transport.category"].sudo().search([])
        return request.render('transporter.homepage',{
            "transport_category_ids" : transport_category_ids
        })

    @http.route('/create_order_view/<string:transport_category_id>', type='http', auth='user',website=True,csrf=False)
    def create_order_form(self, transport_category_id):

        transport_category_id = request.env["transport.category"].browse(int(transport_category_id))
        transport_subcategory_ids = transport_category_id.subcategory_ids
        data = {"transport_subcategory_ids" : transport_subcategory_ids}
        data.update({
            "name" : request.env.user.partner_id.name,
            "email" : request.env.user.partner_id.email,
            "phone" : request.env.user.partner_id.phone,
        })
        return request.render("transporter.create_order_form",data)

    @http.route("/transporter/create_order", methods=["POST"], type='http', auth='user', website=True, csrf=False)
    def create_order(self, **kwargs):
        print(kwargs)
        sale_order_data = {
            'partner_id' : request.env.user.partner_id.id,
            'location_id' : kwargs.get('location_id'),
            'location_dest_id' : kwargs.get("location_dest_id"),
            'subcategory_id' : kwargs.get('subcategory_id'),
            'phone' : kwargs.get('phone'),
            'email' : kwargs.get('email'),
            'schedule_date' : datetime.strptime(kwargs.get('schedule_date'),"%Y-%m-%dT%H:%M"),
            'order_line' : [(0,0,{'product_id' : request.env.ref('delivery.product_product_delivery_product_template').sudo().product_variant_id.id,
                                   'product_uom_qty' : 1})],
            'location_let' : kwargs.get('location_let'),
            'location_lng' : kwargs.get('location_lng'),
            'location_dest_lat' : kwargs.get('location_dest_lat'),
            'location_dest_lng' : kwargs.get('location_dest_lng'),
            'user_id' : request.env.user.id
        }
        request.env['sale.order'].sudo().create(sale_order_data)
        return request.redirect('/view_order')


    @http.route("/view_order",type='http', auth='user',website=True,csrf=False)
    def view_order(self):
        sale_order_ids = request.env['sale.order'].search([])
        data = {"sale_order_ids" : sale_order_ids}
        print(data)
        return request.render("transporter.view_order",data)

    @http.route("/edit_order/<string:sale_order_id>",type='http', auth='user',website=True,csrf=False)
    def edit_order(self,sale_order_id):
        sale_order = request.env['sale.order'].browse(int(sale_order_id))
        data = {"sale_order_id" : sale_order,"transport_subcategory_ids" : sale_order.category_id.subcategory_ids}
        data["object"] = sale_order
        data['assign_vechile_button'] = True if sale_order.transporter_user_id == request.env.user and not sale_order.vehicle_id else False
        if data.get('assign_vechile_button'):
            vechile_ids = request.env['transport.vehicle'].search([('create_uid','=',request.env.user.id)])
            data['vechile_ids'] = vechile_ids
        transporter_user_ids = request.env['transport.vehicle'].sudo().search(
            [('subcategory_id', '=', sale_order.subcategory_id.id)]).create_uid
        data['transporter_user_ids'] = transporter_user_ids
        if sale_order.user_id == request.env.user:
            data['update_button'] = True
            data['cancel_button'] = True
        elif sale_order.transporter_user_id == request.env.user:
            data['cancel_button'] = True
        if sale_order.state in ('draft','sent') and sale_order.user_id == request.env.user:
            data['set_amount_and_transporter'] = True
        transporter_user_ids = request.env['transport.vehicle'].sudo().search(
            [('subcategory_id', '=', sale_order.subcategory_id.id)]).create_uid
        data['transporter_user_ids'] = transporter_user_ids
        if sale_order.delivery_status == 'done' and sale_order.invoice_status == 'to invoice' and sale_order.user_id == request.env.user:
            data['create_payment'] = True
        if sale_order.delivery_status == 'done' and sale_order.invoice_status == 'to invoice' and sale_order.user_id == request.env.user:
            data['create_payment'] = True
        data['object'] = sale_order
        if sale_order.delivery_status == 'in_progress' and sale_order.transporter_user_id == request.env.user:
            data['delivered_and_invoice_button'] = True

        print(data)
        return request.render("transporter.edit_order",data)

    @http.route("/transporter/update_order", methods=["POST"], type='http', auth='user', website=True, csrf=False)
    def update_order(self, **kwargs):
        print(kwargs)
        sale_order = request.env['sale.order'].browse(int(kwargs.get('sale_order_id')))
        sale_order.sudo().write({
            'partner_id': request.env.user.partner_id.id,
            'location_id': kwargs.get('location_id'),
            'location_dest_id': kwargs.get("location_dest_id"),
            'subcategory_id': int(kwargs.get('subcategory_id')),
            'phone': kwargs.get('phone'),
            'email': kwargs.get('email'),
            'schedule_date': datetime.strptime(kwargs.get('schedule_date'), "%Y-%m-%dT%H:%M")})
        return request.redirect('/view_order')

    @http.route("/transporter/cancel_order/<string:sale_order_id>",type='http', auth='user', website=True,csrf=False)
    def delete_order(self,sale_order_id):
        sale_order = request.env['sale.order'].browse(int(sale_order_id))
        print(sale_order)
        sale_order.sudo()._action_cancel()
        return request.redirect('/view_order')

    @http.route("/transporter/register_vehicle", type='http', auth='user',  website=True, csrf=False)
    def register_vehicle(self):
        category_ids = request.env['transport.category'].sudo().search([])
        subcategory_ids = request.env['transport.subcategory'].sudo().search([])
        user_id = request.env.user
        data = {
            'user_id': user_id,
            'transport_category_ids': category_ids,
            'transport_subcategory_ids' : subcategory_ids
        }
        print(">>>>>>>>>",data)
        return request.render('transporter.register_vehicle',data)

    @http.route("/transporter/create_vehicle", methods=["POST"], type='http', auth='user', website=True, csrf=False)
    def create_vehicle(self, **kwargs):
        print(kwargs)
        vehicle_data = {
            'name' : kwargs.get('name'),
            'mobile' : kwargs.get('phone'),
            'email' : kwargs.get('email_from'),
            'category_id' : int(kwargs.get('category_id')) or False,
            'subcategory_id' : int(kwargs.get('subcategory_id')) or False,
            'user_id' : request.env.user.id,
            'description' : kwargs.get('description'),
            'vechical_number' : kwargs.get('vechical_number'),
            'driver_aadhar' : kwargs.get('aadhar_number'),
            'vechicle_rc_book' : base64.b64encode(kwargs.get('rc_image').read()),
            'vehicle_puc' : base64.b64encode(kwargs.get('puc_image').read()),
            'license_image' : base64.b64encode(kwargs.get('licence_image').read()),
            'driver_name' : kwargs.get('driver_name'),
            'vechicle_image' :  base64.b64encode(kwargs.get('vechicle_image').read()) if kwargs.get('vechicle_image') else False,
            'company_name' : kwargs.get('company_name') }


        request.env['transport.vehicle'].create(vehicle_data)
        return request.render("transporter.thank_you_register_vehicle")

    @http.route("/transporter/view_vehicle", type="http",methods=["POST","GET"],auth='user', website=True, csrf=False)
    def view_vehicle(self,**kwargs):
        transport_vehicle_ids = request.env['transport.vehicle'].search([('user_id','=',request.env.uid)])
        data = {"transport_vehicle_ids": transport_vehicle_ids}
        print(data)
        return request.render("transporter.view_vechile", data)

    @http.route("/edit_vechicle/<string:vehicle_id>", type='http', auth='user', website=True, csrf=False)
    def edit_vehicle(self, vehicle_id):
        category_ids = request.env['transport.category'].sudo().search([])
        subcategory_ids = request.env['transport.subcategory'].sudo().search([])
        transport_vehicle_id = request.env['transport.vehicle'].browse(int(vehicle_id))
        data = {"transport_vehicle_id": transport_vehicle_id,
                "transport_category_ids" : category_ids,
                "transport_subcategory_ids" : subcategory_ids
                }
        return request.render("transporter.update_vehicle",data)

    @http.route("/transporter/update_vehicle", methods=["POST"], type='http', auth='user', website=True, csrf=False)
    def update_vechile(self, **kwargs):
        print(kwargs)
        vechile_id = request.env['transport.vehicle'].browse(int(kwargs.get('vechile_id')))
        vehicle_data = {
            'name': kwargs.get('name'),
            'mobile': kwargs.get('phone'),
            'email': kwargs.get('email_from'),
            'description': kwargs.get('description'),
            'driver_name': kwargs.get('driver_name'),
            'company_name': kwargs.get('company_name')}
        if kwargs.get('category_id'):
            vehicle_data['category_id'] = int(kwargs.get('category_id')) or False
        if kwargs.get('subcategory_id'):
            vehicle_data['subcategory_id'] = int(kwargs.get('subcategory_id')) or False
        if kwargs.get('driver_aadhar'):
            vehicle_data['driver_aadhar'] = kwargs.get('driver_aadhar') or False
        vechile_id.write(vehicle_data)
        return request.redirect('/transporter/view_vehicle')

    @http.route("/transporter/view_market_place", methods=["POST","GET"], type='http', auth='user', website=True, csrf=False)
    def view_market_place(self, **kwargs):
        sale_order_ids = request.env['sale.order'].search([('state','in',('draft','sent'))])
        sale_order_ids += request.env['sale.order'].search(['&',('state','=','sale'),
                                                             '|',
                                                             ('transporter_user_id','=',request.env.user.id),
                                                            ('user_id','=',request.env.user.id)])
        row_range = len(sale_order_ids)/3
        if row_range == int(row_range):
            row_range = int(row_range)
        else:
            row_range = int(row_range)+1

        data = {"sale_order_ids": sale_order_ids, "row_range" : row_range, "total" : len(sale_order_ids)}
        print(data)
        return request.render("transporter.market_place_page", data)

    @http.route("/view_market_place_order/<string:sale_order_id>", type='http', auth='user', website=True, csrf=False)
    def view_market_place_order(self, sale_order_id):
        sale_order = request.env['sale.order'].browse(int(sale_order_id))
        data = {"sale_order_id": sale_order, "transport_subcategory_ids": sale_order.subcategory_id}
        transporter_user_ids = request.env['transport.vehicle'].sudo().search([('subcategory_id', '=',sale_order.subcategory_id.id)]).create_uid
        data['transporter_user_ids'] = transporter_user_ids

        if sale_order.state in ('draft','sent') and sale_order.create_uid == request.env.user:
            data['set_amount_and_transporter'] = True
        data['discuusion_button'] = True
        if sale_order.delivery_status == 'done' and sale_order.invoice_status == 'to invoice' and sale_order.user_id == request.env.user:
            data['create_payment'] = True
        data['object'] = sale_order
        if sale_order.delivery_status == 'in_progress' and sale_order.transporter_user_id == request.env.user:
            data['delivered_and_invoice_button'] = True

        data[
            'assign_vechile_button'] = True if sale_order.transporter_user_id == request.env.user and not sale_order.vehicle_id else False
        if data.get('assign_vechile_button'):
            vechile_ids = request.env['transport.vehicle'].search([('create_uid', '=', request.env.user.id)])
            data['vechile_ids'] = vechile_ids
        print(data)
        return request.render("transporter.view_market_place_order", data)

    @http.route("/transporter/confirm_order", type='http', auth='user', website=True, csrf=False)
    def confirm_order(self,**kwargs):

        sale_order_id = request.env['sale.order'].sudo().browse(int(kwargs.get('sale_order_id')))
        price = float(kwargs.get('customer_input'))
        transporter_user_id = int(kwargs.get('transporter_user_id'))
        sale_order_id.order_line[0].sudo().write({'price_unit' : price})
        sale_order_id.sudo().write({'transporter_user_id' : transporter_user_id})
        commision_product_id=request.env.ref("transporter.product_product_commision")
        order_line_data = {
            "product_id" :commision_product_id.id,
            "price_unit" : 50,
            "order_id" : sale_order_id.id,
            "name" : commision_product_id.name,
            "product_uom_qty" : 1.0
        }
        order_line_id = request.env['sale.order.line'].sudo().create(order_line_data)
        order_line_id.sudo()._compute_amount()
        sale_order_id.sudo().action_confirm()
        return request.render("transporter.thank_you_order_confirm")

    @http.route("/confirm_vechile/<string:sale_order_id>", type='http', auth='user', website=True, csrf=False)
    def confirm_vechile(self, **kwargs):
        sale_order_id = request.env['sale.order'].browse(int(kwargs.get('sale_order_id')))
        sale_order_id.sudo().write({'vehicle_id' : int(kwargs.get('vechile_id')) if kwargs.get('vechile_id') else False})
        sale_order_id.sudo().write({'delivery_status' : 'in_progress'})
        return request.redirect(f'/view_market_place_order/{ sale_order_id.id }')

    @http.route("/delivered_order/<string:sale_order_id>", type='http', auth='user', website=True, csrf=False)
    def delivered_order(self, sale_order_id):
        sale_order_id = request.env['sale.order'].browse(int(sale_order_id))
        sale_order_id.sudo().write({'delivery_status' : 'done'})
        return request.render('transporter.thank_you_delivered_order')

