# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# Copyright 2018 Fork Sand Inc.
# Copyright 2018 Ross Golder
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.currency_rate_update.services.currency_getter_interface \
    import CurrencyGetterInterface
from datetime import datetime
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from bs4 import BeautifulSoup, Comment, NavigableString
from selenium import webdriver

import logging
_logger = logging.getLogger(__name__)

CMC_URL_PREFIX = 'https://customs.bg/wps/portal/agency/home/info-business/bank-information/customs-exchange-rates'


class BGSRGetter(CurrencyGetterInterface):
    """Implementation of Currency_getter_factory interface
    for BG Customs service
    """
    code = 'BGSR'
    name = 'BG Customs'
    in_field = 'rate_statistics'

    supported_currency_array = [
        'AUD', 'BRL', 'CAD', 'CHF', 'CNY', 'CZK', 'DKK',
        'GBP', 'HKD', 'HRK', 'HUF', 'IDR', 'ILS', 'INR',
        'ISK', 'JPY', 'KRW', 'MXN', 'MYR', 'NOK', 'NZD',
        'PHP', 'PLN', 'RON', 'RUB', 'SEK', 'SGD', 'THB',
        'TRY', 'USD', 'ZAR', 'EUR', 'BGN'
    ]

    def get_updated_currency(self, currency_array, main_currency, max_delta_days):
        """implementation of abstract method of Curreny_getter_interface"""
        self.validate_cur(main_currency)
        if main_currency != 'BGN':
                raise Exception('Could not update different currency %s'%(main_currency))
        #self.init_updated_currency()
        url = CMC_URL_PREFIX
        _logger.debug("Supported currencies = %s " % self.supported_currency_array)
        if main_currency in currency_array :
            currency_array.remove(main_currency)
        #soup = BeautifulSoup(self.get_url_by_browser(url),"html.parser")
        soup = BeautifulSoup(self.get_url(url),"html.parser")
        data_table = soup.find('div', {'id': 'content'})
        for date in data_table.find_all('p'):
             date_now = date.find(text=lambda text: text.encode('utf-8').strip().startswith('валидни за периода от'))
             if date_now != None:
                 break
        date_start = datetime.strptime(date_now.split()[4],'%d.%m.%Y')
        date_end = datetime.strptime(date_now.split()[7],'%d.%m.%Y')
        self.check_rate_date(datetime.today(), (date_end-datetime.today()).days)
        # collect currency rate from webpage
        table = data_table.find('table')
        table_body = table.find('tbody')
        data = []
        rates = []
        for j, row in enumerate(table_body.find_all('tr')):
                if j == 0: # skip first row of title in table
                        continue
                row_in = []
                for i, cell in enumerate(row.find_all('td')):
                        cell_inc = cell.find(text=True)
                        if i in {1, 3, 4}:
                                row_in.append(cell_inc)
                data.append(row_in)
                #_logger.info("Row %s" % row_in)
        #_logger.info("Array %s" % currency_array)
        #_logger.info("Currency %s" % [x[0] for x in data])
        # Check and fill currency rate
        res = [[x[0] for x in data].index(y) for y in currency_array]
        #_logger.info("Array %s" % res)
        for inx in res:
            _logger.info("Cur %s" % data[inx][0])
            self.validate_cur(data[inx][0])
            val = float(data[inx][2])/float(data[inx][1])
            rates.append([data[inx][0], 1/val])
            if val :
                self.updated_currency[data[inx][0]] = 1/val
                #_logger.info("Row %s" % 1/val)
            else :
                raise Exception('Could not update the %s'%(data[inx][0]))
        #_logger.debug("Rate retrieved : 1 %s = %s" % (main_currency, rates))
        return self.updated_currency, self.log_info
