# -*- coding: utf-8 -*-
{
    'name': "Trazabilidad de Uso de Marca",

    'summary': """
        Trazabilidad de Uso de Marca""",

    'description': """
        Trazabilidad de Uso de Marca
    """,

    'author': "Interfaces S.A.",
    'website': "http://www.interfaces.com.py",
    'application': True,

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Others',
    'version': '0.2022.9.21.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'ciudades', 'sale', 'campos_intn', 'stock'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/views.xml',
        # 'views/licencia_conformidad.xml',
        # 'views/licencia_conformidad_dos.xml',
        'views/licencia_servicios.xml',
        'views/normas_licencia.xml',
        'views/reglamentos_licencia.xml',
        'views/licencia_conformidad_report.xml',
        'views/licencia_conformidad_online.xml',
        'views/licencia_conformidad_dos_report.xml',
        'views/licencia_conformidad_dos_online.xml',
        'views/licencia_servicios_report.xml',
        'views/licencia_servicios_online.xml',
        'views/licencia_servicios_public.xml',
        'views/marca_producto.xml',
        'views/fabricante_producto.xml',
        'views/certificado_conformidad.xml',
        'views/certificado_conformidad_report.xml',
        'views/certificado_conformidad_online.xml',
        'views/res_partner.xml',
        'views/acta_extraccion.xml',
        'views/acta_extraccion_report.xml',
        'views/informe_muestreo.xml',
        'views/informe_muestreo_report.xml',
        'views/solicitud_ensayos.xml',
        'views/solicitud_ensayos_report.xml',
        'views/determinacion_ensayos.xml',
        'views/product_template.xml',
        'views/verificar.xml',
        'views/solicitud_impresiones.xml',
        'views/solicitud_impresiones_report.xml',
        'views/impresion_etiquetas.xml',
        'views/impresora_etiquetas.xml',
        'views/imprimir_wizard_view.xml',
        'views/reimprimir_wizard.xml',
        'views/control_etiquetas.xml',
        'views/factura_comprobante.xml',
        'views/gestion_comprobantes.xml',
        'views/nota_rechazo.xml',
        'views/nota_rechazo_report.xml',
        'views/stock_location.xml',
        'views/stock_picking.xml',
        'views/stock_picking_type.xml',
        'views/color_anillos.xml',
        'portal/home.xml',
        'portal/solicitud_impresiones_portal.xml',
        'portal/control_etiquetas_portal.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
