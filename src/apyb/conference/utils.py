# -*- coding:utf-8 -*-
from random import choice

VALIDCHARS = 'abcdefghijklmnopqrstuvwxyz0123456789'
SIZE = 8


def fmt_price(price):
    ''' Format a value as price'''
    price = str(price).strip()
    if price:
        if price == '0':
            price = '0000'
        return 'R$ %s,%s' % (price[:-2], price[-2:])
    else:
        return '-'


def generateId():
    ''' Generate an id '''
    uid = [choice(VALIDCHARS) for i in range(0, SIZE + 1)]
    return ''.join(uid)


def context_property(name):

    def getter(self):
        return getattr(self.context, name, None)

    def setter(self, value):
        setattr(self.context, name, value)

    def deleter(self):
        delattr(self.context, name)

    return property(getter, setter, deleter)
