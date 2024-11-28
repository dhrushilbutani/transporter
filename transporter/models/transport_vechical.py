from odoo import models,fields,api,_

class TransporterVechical(models.Model):
    _name = 'transport.vehicle'

    code = fields.Char(
        string="Code",
        required=True, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))
    name = fields.Char(string='Vechical Name', required=True)
    description = fields.Text(string='Description')
    category_id = fields.Many2one('transport.category', string='Category')
    subcategory_id = fields.Many2one('transport.subcategory', string='Subcategory')
    vechical_number = fields.Char(string='Vechical Number',required=True)
    driver_name = fields.Char(string='Driver Name')
    driver_aadhar = fields.Char(string='Aadhar',required=True)
    vechicle_rc_book = fields.Image("Vechicle RC Book")
    vehicle_puc = fields.Image("Vechicle PUC")
    vechicle_image = fields.Image("Vechicle Image")
    mobile = fields.Char("Mobile")
    email = fields.Char("Email")
    active = fields.Boolean("Active",default=True)
    user_id = fields.Many2one("res.users")
    partner_id = fields.Many2one("res.partner")
    state = fields.Selection([('draft','Draft'),('approve','Approved')],default='draft')
    license_image = fields.Image("License Image")
    company_name = fields.Char("Company Name")




    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', _("New")) == _("New"):
                vals['code'] = self.env['ir.sequence'].sudo().next_by_code(
                    'vehicle.sequence') or _("New")
        return super().create(vals_list)

    def approve_vehicle(self):
        self.state = 'approve'
    def reset_to_draft(self):
        self.state = 'draft'