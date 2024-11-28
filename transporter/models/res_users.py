from odoo import models,fields,api

class ResUser(models.Model):
    _inherit = 'res.users'

    have_vechile = fields.Boolean(compute="_compute_have_vechile")
    vechile_ids = fields.One2many("transport.vehicle","create_uid")

    def _compute_have_vechile(self):
        for rec in self:
            vechile_id = self.env['transport.vehicle'].search([('create_uid','=',rec.id),
                                                               ('state','=','approve')])
            if vechile_id:
                rec.have_vechile = True
            else:
                rec.have_vechile = False
