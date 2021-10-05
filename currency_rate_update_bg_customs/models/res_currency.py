# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

class Currency(models.Model):
    _inherit = "res.currency"

    rate_statistics = fields.Float(compute='_compute_current_rate_statistics', string='Current Statistic Rate', digits=(12, 6),
                        help='The rate of the currency to the currency of rate 1.')

    @api.multi
    @api.depends('rate_ids.rate_statistics')
    def _compute_current_rate_statistics(self):
        date = self._context.get('date') or fields.Date.today()
        company_id = self._context.get('company_id') or self.env['res.users']._get_company().id
        # the subquery selects the last rate before 'date' for the given currency/company
        query = """SELECT c.id, (SELECT r.rate_statistics FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                               ORDER BY r.company_id, r.name DESC
                                  LIMIT 1) AS rate
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date, company_id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        for currency in self:
            currency.rate_statistics = currency_rates.get(currency.id) or 1.0


class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    rate_statistics = fields.Float(digits=(12, 6), default=1.0, help='The statistics rate of the currency to the currency of rate 1')
