import uuid
from odoo import api, fields, models, exceptions
import datetime
from datetime import date

import dateutil
from dateutil.relativedelta import relativedelta


class SolicitudImpresionesLine(models.Model):
    _name = 'solicitud.impresiones.lines'

    solicitud_id = fields.Many2one('solicitud.impresiones', string='Solicitud de Impresiones', required=True,
                               copy=False)

    product_id = fields.Many2one('product.product', string='Etiqueta', domain=[('es_etiqueta', '=', True)],
                                 change_default=True, ondelete='restrict')

    qty = fields.Integer(string='Cantidad',required=True, default=1)
    kg_polvo = fields.Float(string="Kg/L por unidad")

    kg_polvo_total = fields.Float("Kg/L total")

    certificado_ids = fields.Many2many('certificado.conformidad', string="Certificados", required=False)
    factura_ids = fields.Many2many('factura_comprobante', string="Facturas", required=False)

    impresion_etiqueta_id = fields.Many2one('impresion.etiquetas', required=True, string="Impresion de Etiquetas")

    @api.onchange('product_id')
    @api.depends('product_id')
    def onchangeProduct(self):
        for this in self:
            if this.product_id and this.product_id.kg_polvo:
                this.kg_polvo = this.product_id.kg_polvo


    @api.onchange('qty','kg_polvo')
    @api.depends('qty','kg_polvo')
    def calculoKgPolvo(self):
        for this in self:
            this.kg_polvo_total = this.qty * this.kg_polvo


class SolicitudImpresiones(models.Model):
    _name = 'solicitud.impresiones'
    _description = 'Solicitud de Impresiones'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "name desc"

    name = fields.Char(
        string='Número', track_visibility="onchange", copy=False)
    fecha_solicitud = fields.Datetime(
        string="Fecha de solicitud", track_visibility="onchange", default=fields.Datetime.now())
    partner_id = fields.Many2one(
        "res.partner", string="Empresa", required=True, track_visibility="onchange")
    user_id = fields.Many2one(
        "res.users", string="Usuario", copy=False, track_visibility="onchange")
    state = fields.Selection(string="Estado", selection=[("draft", "Nuevo"), ("asignado", "Asignado"),("verificado", "Verificado"), ("cancel", "Cancelado")], default="draft", copy=False, track_visibility="onchange")
    # order_id = fields.Many2one(
    #    'sale.order', string="Expediente", copy=False, track_visibility="onchange")

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company'])

    solicitud_impresiones_lines = fields.One2many('solicitud.impresiones.lines', 'solicitud_id', string="Etiquetas Solicitadas",
                                    track_visibility='onchange')

    etiquetas_disponibles = fields.Many2many('product.product', string="Etiquetas disponibles")

    licencia_id = fields.Many2one('licencia.servicios', string="Licencia por Uso de Marca", copy=False, track_visibility="onchange")

    active = fields.Boolean('Activo', default=True, track_visibility='onchange')



    @api.onchange('partner_id')
    @api.depends('partner_id')
    def onchangePartner(self):
        licencia_vigente = self.partner_id.mapped('licencia_servicios_ids').filtered(lambda x: x.state == 'done' and x.fecha_vencimiento >= fields.Date.today()).sorted(key=lambda r: r.name)
        if licencia_vigente:
            self.licencia_id = licencia_vigente[0]
            etiquetas_disponibles = licencia_vigente.mapped('agentes_1.etiqueta_ids')
            self.etiquetas_disponibles = [(6, 0, etiquetas_disponibles.ids)]

    def _default_access_token(self):
        return uuid.uuid4().hex

    access_url = fields.Char('URL del portal de cliente', compute="_compute_access_url")
    access_token = fields.Char('Token de seguridad', default=_default_access_token)

    @api.multi
    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % ('Solicitud de Impresión', self.name)

    def _compute_access_url(self):
        # super(SolicitudesServicio, self)._compute_access_url()
        for solicitud in self:
            solicitud.access_url = '/my/solicitud-impresion/%s' % (solicitud.id)

    def _portal_ensure_token(self):
        """ Get the current record access token """
        if not self.access_token:
            # we use a `write` to force the cache clearing otherwise `return self.access_token` will return False
            self.sudo().write({'access_token': str(uuid.uuid4())})
        return self.access_token

    @api.multi
    def get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        self.ensure_one()
        url = self.access_url + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self._portal_ensure_token(),
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        return url

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            seq = self.env['ir.sequence'].sudo().next_by_code(
                'seq_solicitud_impresiones')
            vals['name'] = seq
        res = super(SolicitudImpresiones, self).create(vals)
        for i in res:
            reg = {
                'res_id': i.id,
                'res_model': 'solicitud.impresiones',
                'partner_id': i.partner_id.id
            }
            follower_id = self.env['mail.followers'].create(reg)
        return res


    def button_draft(self):
        for i in self:
            i.write({'state': 'draft'})
        return

    def button_asignar(self):
        for i in self:
            if not i.user_id:
                raise exceptions.ValidationError(
                    "Debe asignar un usuario de impresión")

            for line in i.solicitud_impresiones_lines:
                if not line.certificado_ids and not line.factura_ids:
                    raise exceptions.ValidationError(
                        "No puede asignar la solicitud de impresión, revise que todas las lineas tengan facturas "
                        "o certificados para descontar.")
                if line.certificado_ids:
                    cant_descontar = line.kg_polvo_total
                    if sum(line.certificado_ids.mapped('tamaño_lote_restante_aproximado')) < line.kg_polvo_total:
                        raise exceptions.ValidationError(
                            "No puede asignar la solicitud de impresión, no tiene disponible la cantidad de kg/l necesaria.")
                    else:
                        for c in line.certificado_ids:
                            if cant_descontar > 0:
                                if cant_descontar > c.tamaño_lote_restante_aproximado:
                                    resto = cant_descontar - c.tamaño_lote_restante_aproximado
                                    c.tamaño_lote_restante_aproximado = c.tamaño_lote_restante_aproximado - resto
                                    cant_descontar = cant_descontar - resto
                                else:
                                    c.tamaño_lote_restante_aproximado = c.tamaño_lote_restante_aproximado - cant_descontar
                                    cant_descontar = 0
                elif line.factura_ids:
                    cant_restante = sum(line.factura_ids.mapped('line_ids.qty')) - sum(
                        line.factura_ids.mapped('line_ids.aprox_qty_usada'))
                    cant_descontar_factura = line.kg_polvo_total
                    if cant_restante < line.kg_polvo_total:
                        raise exceptions.ValidationError(
                            "No puede asignar la solicitud de impresión, no tiene disponible la cantidad de kg/l necesaria.")
                    else:
                        for l in line.mapped('factura_ids.line_ids'):
                            restante_line = l.qty - l.aprox_qty_usada
                            if cant_descontar_factura > 0:
                                if cant_descontar_factura > restante_line:
                                    resto = cant_descontar_factura - restante_line
                                    l.aprox_qty_usada = l.aprox_qty_usada + resto
                                    cant_descontar_factura = cant_descontar_factura - resto
                                else:
                                    l.aprox_qty_usada = l.aprox_qty_usada + cant_descontar_factura
                                    cant_descontar_factura = 0

            # i.crear_expediente()
            i.write({'state': 'asignado'})
            for pro in i.solicitud_impresiones_lines:
                vals = {
                    'partner_id':i.partner_id.id,
                    'solicitud_id':i.id,
                    'user_id':i.user_id.id,
                    'control_inicial':pro.product_id.sgte_numero_control,
                    'prox_control':pro.product_id.sgte_numero_control,
                    'product_id':pro.product_id.id,
                    'qty':pro.qty,
                    'control_final':pro.product_id.sgte_numero_control+pro.qty-1
                }
                pro.product_id.write({'sgte_numero_control':pro.product_id.sgte_numero_control+pro.qty-1})
                impresion = self.env['impresion.etiquetas'].create(vals)
                pro.write({'impresion_etiqueta_id':impresion.id})

        return

    # def crear_expediente(self):
    #    product_id = self.env['product.product'].browse(4660)
    #    order = {
    #        'partner_id': self.partner_id.id,
    #        'date_order': fields.Datetime.now(),
    #        'order_line': [(0, 0, {'product_id': product_id.id, 'name': product_id.name, 'product_uom_qty': 1, 'product_uom': product_id.uom_id.id, 'price_unit': product_id.list_price, 'tax_id': [(6, 0, product_id.taxes_id.ids)]})]
    #    }
    #    order_id = self.env['sale.order'].create(order)
    #    if order_id:
    #        order_id.action_confirm()
    #        self.write({'order_id': order_id.id})

    #    return

    def button_cancelar(self):
        for i in self:
            for line in i.solicitud_impresiones_lines:
                if line.certificado_ids:
                    cant_colocar = line.kg_polvo_total
                    for c in line.certificado_ids:
                        if cant_colocar > 0:
                            if cant_colocar > c.tamaño_lote_kg - c.tamaño_lote_restante_aproximado:
                                resto = cant_colocar - (c.tamaño_lote_kg - c.tamaño_lote_restante_aproximado)
                                c.tamaño_lote_restante_aproximado = c.tamaño_lote_restante_aproximado + cant_colocar - resto
                                cant_colocar = cant_colocar - resto
                            else:
                                c.tamaño_lote_restante_aproximado = c.tamaño_lote_restante_aproximado + cant_colocar
                                cant_colocar = 0
                elif line.factura_ids:
                    cant_aportar_factura = line.kg_polvo_total
                    for l in line.mapped('factura_ids.line_ids'):
                        restante_line = l.qty - l.aprox_qty_usada
                        if cant_aportar_factura > 0:
                            if cant_aportar_factura > restante_line:
                                resto = cant_aportar_factura + restante_line
                                l.aprox_qty_usada = l.aprox_qty_usada - resto
                                cant_aportar_factura = cant_aportar_factura - resto
                            else:
                                l.aprox_qty_usada = l.aprox_qty_usada - cant_aportar_factura
                                cant_aportar_factura = 0

            i.write({'state': 'cancel'})
            impresiones = self.env['impresion.etiquetas'].search([('solicitud_id','=',i.id)])
            for impre in impresiones:
                impre.button_cancelar()
        return

    def verificar(self):
        for this in self:
            impresion_etiquetas = this.mapped('solicitud_impresiones_lines.impresion_etiqueta_id')
            print('Impresion de etiquetas')
            print(impresion_etiquetas)
            if len(impresion_etiquetas) == len(impresion_etiquetas.filtered(lambda x: x.state == 'verificado')):
                ie = []
                for i in impresion_etiquetas:
                    ie.append(i.id)
                vals = {
                    'solicitud_id': this.id,
                    'impresion_etiquetas_ids': [(6,0,ie)],
                    'fecha_hora': fields.datetime.now(),
                    'partner_id': this.partner_id.id,
                }
                gestion = self.env['gestion.comprobantes'].create(vals)

                for line in impresion_etiquetas:
                    vals_line = {
                        'product_id':line.product_id.id,
                        'qty':line.qty,
                        'nro_inicial':line.control_inicial,
                        'nro_final':line.control_final,
                        'comprobante_id': gestion.id,
                        'impresion_etiqueta_id':line.id
                    }
                    gestion_line = self.env['gestion_comprobantes_lines'].create(vals_line)

    def unlink(self):
        raise exceptions.ValidationError(
            "No se pueden eliminar solicitudes, sólo cancelarlas.")


