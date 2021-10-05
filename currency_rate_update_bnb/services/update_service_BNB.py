# © 2009 Camptocamp
# © 2009 Grzegorz Grzelak
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.currency_rate_update.services.currency_getter_interface \
    import CurrencyGetterInterface

from datetime import datetime
from lxml import etree

import logging
_logger = logging.getLogger(__name__)


class BNBGetter(CurrencyGetterInterface):
    """Implementation of Currency_getter_factory interface
    for BNB service
    """
    code = 'BNB'
    name = 'Bulgaria Central Bank'
    in_field = 'rate'

    supported_currency_array = [
        "AUD", "BRL", "CAD", "CHF", "CNY", "CZK", "DKK", "EUR", "GBP", "BGN",
        "HKD", "HRK", "HUF", "IDR", "ILS", "INR", "JPY", "KRW", "LTL", "MXN",
        "MYR", "NOK", "NZD", "PHP", "PLN", "RON", "RUB", "SEK", "SGD", "THB",
        "TRY", "USD", "ZAR"]

    def rate_retrieve(self, dom):
        """Parse a dom node to retrieve-
        currencies data

        """
        res = {'EUR': {'rate_currency': 1.95583, 'inverted': 1.95583, 'direct': 0.511292}}
        curr_rate = dom.xpath("//ROW/REVERSERATE")
        direct_rate = dom.xpath("//ROW/RATE")
        gold = dom.xpath("//ROW/GOLD")
        for item, curr_name in enumerate(dom.xpath("//ROW/CODE")):
            if gold[item].text == '1':
                _logger.debug("CURRENCY %s::%s::%s" % (curr_name.text, float(curr_rate[item].text), float(direct_rate[item].text)))
                res[curr_name.text] = {'rate_currency': float(curr_rate[item].text),
                                       'inverted': float(direct_rate[item].text),
                                       'direct': float(curr_rate[item].text)}
        return res

    def get_updated_currency(self, currency_array, main_currency,
                             max_delta_days):
        """implementation of abstract method of Curreny_getter_interface"""
        _logger.info("Bulgarian National Bank")
        self.validate_cur(main_currency)
        if main_currency != 'BGN':
                raise Exception('Could not update different currency %s'%(main_currency))
        url = 'https://www.bnb.bg/Statistics/StExternalSector/StExchangeRates/StERForeignCurrencies/index.htm'
        params = {'download': 'xml'}

        # We do not want to update the main currency
        if main_currency in currency_array:
            currency_array.remove(main_currency)
        _logger.info("BNB currency rate service : connecting...")
        rawfile = self.get_url_with_params(url, params)
        dom = etree.fromstring(rawfile)
        _logger.info("BNB sent a valid XML file")
        rate_date = dom.xpath("//ROW/TITLE")[0].text[-10:]
        # Don't use DEFAULT_SERVER_DATE_FORMAT here, because it's
        # the format of the XML of ECB, not the format of Odoo server !
        rate_date_datetime = datetime.strptime(rate_date, '%d.%m.%Y')
        self.check_rate_date(rate_date_datetime, max_delta_days)

        # We dynamically update supported currencies
        self.supported_currency_array = ['EUR', 'BGN']

        gold = dom.xpath("//ROW/GOLD")
        for item, curr_name in enumerate(dom.xpath("//ROW/CODE")):
            if gold[item].text == '1':
                self.supported_currency_array.append(curr_name.text)
        _logger.info("Supported currencies = %s " %
                      self.supported_currency_array)
        curr_data = self.rate_retrieve(dom)
        _logger.info("Returned currency rate %s" % curr_data)
        for curr in currency_array:
            self.validate_cur(curr)
            if curr == 'BGN':
                rate = 1.0
            else:
                rate = curr_data[curr]
            self.updated_currency[curr] = rate
            _logger.debug(
                "Rate retrieved : 1 %s = %s %s" % (main_currency, rate, curr)
            )
        return self.updated_currency, self.log_info
