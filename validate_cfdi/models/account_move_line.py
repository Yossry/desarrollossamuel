# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        index=True,
        compute="_compute_analytic_account",
        store=True,
        readonly=False,
        check_company=True,
        copy=True,
        required=False
    )


    

        

