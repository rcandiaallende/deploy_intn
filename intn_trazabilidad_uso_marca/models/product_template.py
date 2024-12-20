# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions,_
from re import findall as regex_findall, split as regex_split

from psycopg2 import OperationalError, Error

from odoo.osv import expression


from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round, float_compare, float_is_zero

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    es_agente = fields.Boolean("Es un Agente")
    etiqueta_ids = fields.Many2many("product.product", string='Etiquetas')
    es_etiqueta = fields.Boolean("Es Etiqueta Uso de Marca")
    aro_id = fields.Many2one("product.product", string='Anillo de Seguridad')
    kg_polvo = fields.Float(string="Kg/L a Descontar")

    sgte_numero_control = fields.Integer("Sgte. Número de Control")

    cod_licencia = fields.Char(string="Código para Licencia")

    determinacion_ids= fields.One2many('intn_trazabilidad_uso_marca.determinacion_productos','product_id',string="Determinaciones")
    observaciones_certificado= fields.Html(string="Observaciones")