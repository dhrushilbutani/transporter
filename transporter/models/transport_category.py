from odoo import models,fields,api

class TransporterCategory(models.Model):
    _name = 'transport.category'

    website_image = fields.Image(string="Image")
    name = fields.Char(string='Category Name', required=True,)
    description = fields.Text(string='Description')
    subcategory_ids = fields.One2many('transport.subcategory', 'category_id', string='Subcategories')
    