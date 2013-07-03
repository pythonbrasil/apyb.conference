# -*- coding:utf-8 -*-
from Acquisition import aq_inner
from apyb.conference.config import GROUP_DISCOUNTS
from apyb.conference.config import CAIPIRINHA
from apyb.conference.config import PRICES
from apyb.conference.config import WALL
from apyb.conference.content.registrations import IRegistrations
from five import grok
from Products.CMFCore.utils import getToolByName

import json


class PriceView(grok.View):
    grok.context(IRegistrations)
    grok.require('zope2.View')
    grok.name('reg-price')

    def _sheet(self):
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'portal_properties')
        sheet = getattr(ptool, 'site_properties')
        return sheet

    @property
    def discount_codes(self):
        ''' Retorna a lista de codigos ainda disponiveis
        '''
        def splitLines(lines):
            tmp = []
            for line in lines:
                tmp.append(line.split('|'))
            return tmp
        sheet = self._sheet()
        codes = splitLines(sheet.getProperty('discount_codes', []))
        # Ex: 42W23|0.2
        return dict([(k.upper(), v) for k, v in codes])

    def price(self, registration_type, qty, discount_code='',
              caipirinha='', wall='', ):
        base_price = PRICES[registration_type]
        grp_discount = GROUP_DISCOUNTS.get(registration_type, [])
        discount = 0.0
        if grp_discount and qty > 2:
            for line in grp_discount[::-1]:
                if qty >= line[0]:
                    discount = line[1]
                    break
        if discount_code and registration_type not in ['government',
                                                       'training']:
            discount = discount + float(
                self.discount_codes.get(discount_code, 0.0)
            )
        elif registration_type == 'training':
            # First is on the house
            discount = 1.0 / qty
        price = base_price * qty * (1 - discount)
        caipirinha = caipirinha.split('|')
        for item in caipirinha:
            price = price + CAIPIRINHA.get(item, 0.0)
        wall = wall.split('|')
        for item in wall:
            price = price + WALL.get(item, 0.0)
        # Price is **always** int
        return int(price)

    def fmtPrice(self, price):
        return ('R$%.2f' % (price / 100.0)).replace('.', ',')

    def render(self):
        return ''


class PriceJsonView(PriceView):
    grok.name('reg-price.json')

    def render(self):
        request = self.request
        registration_type = request.get('type', 'individual')
        qty = int(request.get('qty', 1))
        caipirinha = request.get('caipirinha', '')
        wall = request.get('wall', '')
        data = {'price': 0.0, 'fmtPrice': 'R$0,00'}
        data['price'] = self.price(registration_type,
                                   qty,
                                   caipirinha=caipirinha,
                                   wall=wall)
        data['fmtPrice'] = self.fmtPrice(data['price'])

        self.request.response.setHeader('Content-Type', 'application/json')

        return json.dumps(data)
