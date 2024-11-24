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

