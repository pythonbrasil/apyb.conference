# -*- coding: utf-8 -*-
from apyb.conference.config import SPONSOR_LEVELS
from five import grok
from plone.app.layout.viewlets.interfaces import IPortalFooter
from plone.memoize.view import memoize
from zope.component import getMultiAdapter
from zope.interface import Interface


grok.templatedir('templates')


class Sponsors(grok.Viewlet):
    """ Viewlet listing sponsors on the conference
    """

    grok.viewletmanager(IPortalFooter)
    grok.context(Interface)
    grok.order(1)

    def sponsors_by_level(self):
        sponsors = []
        all_sponsors = self.all_sponsors()
        levels = self.levels()
        for level in levels:
            level_id = level.get('id')
            if not level_id in all_sponsors:
                continue
            sponsors.append({
                'id': level_id,
                'title': level.get('title'),
                'sponsors': all_sponsors[level_id]
            })
        return sponsors

    def levels(self):
        levels = []
        for level_id, title in SPONSOR_LEVELS:
            levels.append({'id': level_id,
                           'title': title})
        return levels

    @memoize
    def all_sponsors(self):
        sponsors = {}
        context = self.context
        tools = getMultiAdapter((context, self.request),
                                name=u'plone_tools')
        ct = tools.catalog()
        # Sponsors should be published to be listed
        results = ct.searchResults(portal_type='sponsor',
                                   review_state='published',
                                   sort_on='getObjPositionInParent')
        for brain in results:
            o = brain.getObject()
            level = brain.level
            if not level in sponsors:
                sponsors[level] = []
            sponsor = {
                'id': o.getId(),
                'title': o.Title(),
                'image': o.tag(scale='thumb', css_class='sponsor_logo'),
                'description': o.Description(),
                'url': o.remoteUrl,
            }
            sponsors[level].append(sponsor)
        return sponsors

    def available(self):
        return True if self.sponsors_by_level() else False
