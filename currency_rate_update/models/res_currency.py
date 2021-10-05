# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

class Currency(models.Model):
    _inherit = "res.currency"

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency):
        rate_field = self._context.get('rate_field')
        if rate_field and rate_field in from_currency._fields and rate_field in to_currency._fields:
            from_currency = from_currency.with_env(self.env)
            to_currency = to_currency.with_env(self.env)
            return getattr(to_currency, rate_field) / getattr(from_currency, rate_field)
        else:
            return super(Currency, self)._get_conversion_rate(from_currency, to_currency)
