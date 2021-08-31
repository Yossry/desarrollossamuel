# -*- coding: utf-8 -*-
from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        store=True,
        string='Analytic Account',
        compute='_compute_analytic_id_and_tag_ids',
        readonly=False,
        required=True
    )
