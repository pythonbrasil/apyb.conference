# -*- coding:utf-8 -*-
from apyb.conference import MessageFactory as _

PRICES = {'apyb': 5000,
          'student': 5000,
          'individual': 10000,
          'government': 40000,
          'group': 10000,
          'speaker': 10000,
          'sponsor': 0,
          'organizer': 0,
          'training': 0}

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
                  ('supporting', _(u'Supporting')),
                  ('midia', _(u'Media Support')),
                  ('foss', _(u'Free and Open Source')),
                  ('organizers', _(u'Organization'))]
