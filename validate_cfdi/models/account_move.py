# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re
from odoo.tools.misc import formatLang, format_date, get_lang
import warnings
from lxml import etree
from lxml.objectify import fromstring
import base64
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_mx_validate_uuid = fields.Char('Folio Fiscal', readonly=True)
    xml_valido = fields.Boolean(help='Verifica que la factura sea valida en base al XML adjuntos', default=False)
    xml_edi = fields.Binary('XML de Factura', attachment=True)
    file_name = fields.Char("File Name")

    def action_validar_facturas(self):
        self.ensure_one()
        # if not self.partner_id.disable_cfdi_validation:
        #     raise UserError('El usuario seleccionado no requiere validar factura')
        self.xml_valido = False

        def get_node(cfdi_node, attribute, namespaces):
            if hasattr(cfdi_node, 'Complemento'):
                node = cfdi_node.Complemento.xpath(attribute, namespaces=namespaces)
                return node[0] if node else None
            else:
                return None

        cfdi_data = base64.decodebytes(self.xml_edi)
        cfdi_node = fromstring(cfdi_data)
        tfd_node = get_node(
            cfdi_node,
            'tfd:TimbreFiscalDigital[1]',
            {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'},
        )

        uuid = tfd_node.get('UUID' , '')
        supplier_rfc = cfdi_node.Emisor.get('Rfc', cfdi_node.Emisor.get('rfc'))
        stamp_date = tfd_node.get('FechaTimbrado', '').replace('T', ' ')
        serie = cfdi_node.get('Serie', '')
        folio = cfdi_node.get('Folio', '')
        total = cfdi_node.get('Total', '')
        currency = cfdi_node.get('Moneda', '')
        folio_factura = serie + folio
        total_invoice = 53.63


        model = self.env['account.move']
        lista = model.search([('move_type','=','in_invoice'),('state','in',('draft','posted')),('l10n_mx_validate_uuid','=',uuid)])

        for item in lista:            
            raise UserError('Factura Invalida: EL Folio Fiscal ya ha sido registrado, verifique los documentos publicados o en estado borrador.')
      
        if(self.partner_id.vat != supplier_rfc):
            raise UserError('Factura Invalida, verifique el XML adjuntado: El RFC no corresponde')
        if(self.amount_total != float(total)):
            raise UserError('Factura Invalida, verifique el XML adjuntado: Los importes no corresponden')
        if(self.currency_id.name != currency):
            raise UserError('Factura Invalida, verifique el XML adjuntado: La moneda de la factura no corresponde con el XML')
        
        self.ref = folio_factura
        self.l10n_mx_validate_uuid = uuid
        self.date = stamp_date
        self.invoice_date = stamp_date
        self.xml_valido = True


    def action_post(self):
        _logger.warning("-------- Entra al post --------")
        for order in self:
            for line in order.line_ids:
                    if not line.analytic_account_id:
                        cuenta_analitica = order.line_ids[0].analytic_account_id
                        line.write({'analytic_account_id': cuenta_analitica })
                        
            if order.move_type == 'in_invoice':                
                cuenta_analitica = order.line_ids[0].analytic_account_id
                for line in order.line_ids:
                    if line.analytic_account_id != cuenta_analitica:
                        raise UserError('No se pueden ingresar cuentas analiticas diferentes')

                if not order.xml_valido:# and not order.partner_id.disable_cfdi_validation:
                    raise UserError('No se ha validado el XML, de clic en Validar XML')
                
        return self._post(soft=False)
