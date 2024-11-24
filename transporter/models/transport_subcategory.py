from odoo import models,fields,api

class TransportSubCategory(models.Model):
    _name = 'transport.subcategory'

    name = fields.Char(string='Subcategory Name', required=True)
    category_id = fields.Many2one("transport.category")
    min_weight = fields.Float(string='Minimum Weight',required=True)
    max_weight = fields.Float(string='Maximum Weight',required=True)
    active = fields.Boolean(string='Active',default=True)