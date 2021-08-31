# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MaintenenceRims(models.Model):
    _name = 'maintenance.rims'

    date = fields.Date('Fecha de Revisión')
    equipment_id = fields.Many2one('maintenance.equipment',string='Equipo')
    marca = fields.Char('Marca')
    name = fields.Char()
    modelo = fields.Char('Modelo')
    no_serie = fields.Char('No Serie')
    medida = fields.Char('Medida')
    tipo_renovado = fields.Char('Tipo Renovado')
    mil_orig = fields.Char('Milimetros Orig')
    mil_act = fields.Char('Milimetros Act')
    presion = fields.Char('Presion')
    km_acum = fields.Float('Kms Acumulados')
    user_id = fields.Many2one('res.users', string='Responsable',tracking=True, default=lambda self: self.env.uid)
    current_state = fields.Selection([('n', 'Nueva'),('r', 'Renovada')], string='Estado actual')
    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)
    

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'


    maintenance_rims_count = fields.Integer(compute='_compute_maintenance_rims_count', string="Maintenance Count Rims", store=True)
    maintenance_rims_ids = fields.One2many('maintenance.rims','equipment_id', copy=False)
    
    @api.depends('maintenance_rims_ids')
    def _compute_maintenance_rims_count(self):
        lista = []
        for item in self.maintenance_rims_ids:
            lista.append(item)
        self.maintenance_rims_count = len(lista)
