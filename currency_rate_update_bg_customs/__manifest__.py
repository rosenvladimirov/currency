# Copyright 2019 dXFactory Ltd.
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# Copyright 2018 Fork Sand Inc.
# Copyright 2018 Ross Golder
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Currency Rate Update BG Customs Static rate',
    'version': '11.0.1.0.0',
    'category': 'Accounting & Finance',
    'summary': 'Allows to download statisics currency exchange rates from '
               'BG Customs',
    'author': 'Rosen Vladimirov,'
              'dXFactory Ltd.,'
              'Eficent,'
              'Odoo Community Association (OCA),',
    'website': 'https://www.dxfactory.eu',
    'license': 'AGPL-3',
    'depends': [
        'currency_rate_update',
        ],
    'data': [
        'views/res_currency_views.xml',
    ],
    "installable": True
}
