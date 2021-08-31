# -*- coding: utf-8 -*-
# from odoo import http


# class RimsMaintenance(http.Controller):
#     @http.route('/rims_maintenance/rims_maintenance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rims_maintenance/rims_maintenance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rims_maintenance.listing', {
#             'root': '/rims_maintenance/rims_maintenance',
#             'objects': http.request.env['rims_maintenance.rims_maintenance'].search([]),
#         })

#     @http.route('/rims_maintenance/rims_maintenance/objects/<model("rims_maintenance.rims_maintenance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rims_maintenance.object', {
#             'object': obj
#         })
