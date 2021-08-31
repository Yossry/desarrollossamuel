# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }


    xml_edi = fields.Binary('XML de Factura', attachment=True)
    file_name = fields.Char("File Name")

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        partner_invoice_id = self.partner_id.address_get(['invoice'])['invoice']
        invoice_vals = {
            'ref': self.partner_ref or '',
            'move_type': move_type,
            'narration': self.notes,
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'journal_id': self.picking_type_id.warehouse_id.journal_id_supplier.id,
            'partner_id': partner_invoice_id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
            'payment_reference': self.partner_ref or '',
            'partner_bank_id': self.partner_id.bank_ids[:1].id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'xml_edi': self.xml_edi,
            'file_name': self.file_name,
        }
        return invoice_vals

    

    @api.constrains('xml_edi')
    def _check_file(self):
        if self.xml_edi:
            if str(self.file_name.split(".")[1]) != 'xml' :
                raise UserError("No puede adjuntar un archivo que no sea XML")

    def button_confirm(self):
        for order in self:
            current_login= self.env.user
            if self.amount_total > current_login.amount_purchase_approval_max:
                raise UserError('No puede validar esta orden: Limite de aprobacion superado')
            #Solo una cuenta análitica por pedido
            cuenta_analitica =self.order_line[0].account_analytic_id.id
            for line in self.order_line:
                if line.account_analytic_id.id != cuenta_analitica:
                    raise UserError('No se puede generar una pedido con diferentes cuentas analiticas. Verifique que la cuenta análitica sea la misma para todas las lineas del pedido')
            
            #Cuentas análiticas permitidas por almacén
            lista = []
            cuentas_perm =self.picking_type_id.warehouse_id.analytic_account_ids    
            for item in cuentas_perm:
                lista.append(item.id)

            existe = cuenta_analitica not in lista

            if existe:
                raise UserError('Seleccione el Almacen de recepción correspondiente a la cuenta cuenta analitica')

            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.company.currency_id._convert(
                            order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

    def action_create_invoice(self):
        """Create the invoice associated to the PO. """
        if not self.xml_edi:# not self.partner_id.disable_cfdi_validation and 
                raise UserError('No puede crear la factura sin adjuntar el XML')
        
        res = super(PurchaseOrder, self).action_create_invoice()
        return res
