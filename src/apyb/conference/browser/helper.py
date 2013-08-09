# -*- coding:utf-8 -*-
from Acquisition import aq_inner
from apyb.conference.content.registrations import IRegistrations
from DateTime import DateTime
from five import grok
from plone.memoize.view import memoize
from zope.component import getMultiAdapter


class View(grok.View):
    grok.context(IRegistrations)
    grok.require('zope2.View')
    grok.name('helper')

    def __init__(self, context, request):
        super(View, self).__init__(context, request)
        self.context = aq_inner(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.cs = self._multi_adapter(u'plone_context_state')
        self.tools = self._multi_adapter(u'plone_tools')
        self.ps = self._multi_adapter(u'plone_portal_state')
        self._ct = self.tools.catalog()

    def _multi_adapter(self, name):
        return getMultiAdapter((self.context, self.request), name=name)

    def render(self):
        return ''

    @memoize
    def registrations(self, **kw):
        kw['portal_type'] = 'registration'
        kw['path'] = self._path
        brains = self._ct.searchResults(**kw)
        return brains

    @memoize
    def attendees(self, **kw):
        kw['portal_type'] = 'attendee'
        if not 'path' in kw:
            kw['path'] = self._path
        brains = self._ct.searchResults(**kw)
        return brains

    @property
    def registrations_dict(self):
        brains = self.registrations()
        regs = dict([(b.UID, {'title': b.Title,
                              'email': b.email,
                              'review_state': b.review_state,
                              'type': b.Subject and b.Subject[0],
                              'paid': b.paid,
                              'amount': b.amount,
                              'price': b.price,
                              'num_attendees':b.num_attendees,
                              'url': b.getURL(),
                              'json_url': '%s/json' % b.getURL(), })
                    for b in brains])
        return regs

    @property
    def attendees_dict(self):
        brains = self.attendees()
        attendees = dict([(b.UID,
                          {'name': b.Title,
                           'organization': b.organization,
                           'review_state': b.review_state,
                           'type': b.Subject and b.Subject[0],
                           'badge_name': b.badge_name,
                           'gender': b.gender,
                           't_shirt_size': b.t_shirt_size,
                           'country': b.country,
                           'state': b.state,
                           'city': b.city,
                           'url': b.getURL(),
                           'json_url': '%s/json' % b.getURL()})
                         for b in brains])
        return attendees

    @memoize
    def registration_info(self, uid):
        ''' Return registration info for a given uid '''
        return self.registrations_dict.get(uid, {})

    @memoize
    def attendee_info(self, uid):
        ''' Return attendee info for a given uid '''
        return self.attendees_dict.get(uid, {})

    @memoize
    def registrations_stats(self):
        stats = {}
        for state in ['pending', 'confirmed']:
            kw = {'review_state': state}
            stats[state] = {}
            stats[state]['registrations'] = len(self.registrations(**kw))
            stats[state]['attendees'] = len(self.attendees(**kw))
        return stats

    def fmt_date(self, value):
        if not value:
            return None
        if not isinstance(value, DateTime):
            value = DateTime(value)
        return value.strftime('%d/%m/%Y %H:%M')

    def registrations_username(self, username, **kw):
        registrations = self.registrations(email=username)
        return registrations

    def speaker_name(self, speaker_uids):
        ''' Given a list os uids, we return a string with speakers names '''
        portal = self.ps.portal()
        program_helper = portal.program.restrictedTraverse('@@helper')
        speakers_dict = program_helper.speakers_dict
        results = [speaker for uid, speaker in speakers_dict.items()
                   if uid in speaker_uids]
        return ', '.join([b['name'] for b in results])
