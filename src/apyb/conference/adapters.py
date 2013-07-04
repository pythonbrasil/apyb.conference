# -*- coding:utf-8 -*-
from apyb.conference import MessageFactory as _
from plone.stringinterp.adapters import BaseSubstitution
from Products.CMFCore.interfaces import IContentish
from zope.component import adapts


class EmailSubstitution(BaseSubstitution):
    adapts(IContentish)

    category = _(u'All Content')
    description = _(u'Content E-mail')

    def safe_call(self):
        return self.context.email


class SpeakerEmailSubstitution(BaseSubstitution):
    adapts(IContentish)

    category = _(u'All Content')
    description = _(u'Speaker E-mail')

    def safe_call(self):
        email = ''
        if hasattr(self.context, 'speakers'):
            speakers = self.context.speakers
            ct = self.context.portal_catalog
            results = ct.searchResults(portal_type='speaker',
                                       UID=speakers)
            email = results[0].email if results else ''
        return email


class SpeakerNameSubstitution(BaseSubstitution):
    adapts(IContentish)

    category = _(u'All Content')
    description = _(u'Speaker E-mail')

    def safe_call(self):
        name = ''
        if hasattr(self.context, 'speakers'):
            speakers = self.context.speakers
            ct = self.context.portal_catalog
            results = ct.searchResults(portal_type='speaker',
                                       UID=speakers)
            name = results[0].Title if results else ''
        return name
