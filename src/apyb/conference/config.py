# -*- coding:utf-8 -*-
from apyb.conference import MessageFactory as _

BASE_PRICE = 15000

PRICES = {'apyb': BASE_PRICE / 2,
          'student': BASE_PRICE / 2,
          'individual': BASE_PRICE,
          'government': 40000,
          'group': BASE_PRICE,
          'speaker': BASE_PRICE,
          'sponsor': 0,
          'organizer': 0,
          'training': 5000, # for 4h training, adjust proportionally!
          }

CAIPIRINHA = {'no': 0,
              'yes_1': 35000,
              'yes_2': 70000,
              'yes_3': 80000}

WALL = {'no': 0,
        '100': 10000,
        '200': 20000,
        '400': 40000}

GROUP_DISCOUNTS = {
    'student': [
        (7, 0.25),
        (10, 0.27),
        (15, 0.32)],
    'group': [
        (7, 0.25),
        (10, 0.27),
        (15, 0.32)]}

REVIEW_STATE = {
    'confirmed': 'Confirmado',
    'pending': 'Pendente',
}

SPONSOR_LEVELS = [('diamond', _(u'Diamond')),
                  ('platinum', _(u'Platinum')),
                  ('gold', _(u'Gold')),
                  ('silver', _(u'Silver')),
                  ('bronze', _(u'Bronze')),
                  ('a_la_carte', _(u'À la Carte')),
                  ('supporting', _(u'Supporting')),
                  ('midia', _(u'Media Support')),
                  ('foss', _(u'Free and Open Source')),
                  ('organizers', _(u'Organization'))]
