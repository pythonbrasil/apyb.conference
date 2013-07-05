# -*- coding: utf-8 -*-
from apyb.conference.config import SPONSOR_LEVELS
from five import grok
from plone.app.layout.viewlets.interfaces import IPortalFooter
from plone.folder.interfaces import IFolder
from plone.memoize.view import memoize
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import getMultiAdapter
from zope.interface import Interface


grok.templatedir('templates')


class HelperView(grok.View):
    """ Helper view to deal with sponsors and
        sponsorship listing
    """
    grok.context(IPloneSiteRoot)
    grok.require('zope2.View')
    grok.name('sponsors-helper')

    def __init__(self, context, request):
        super(HelperView, self).__init__(context, request)
        self.tools = getMultiAdapter((self.context, self.request),
                                     name=u'plone_tools')
        self.ct = self.tools.catalog()

    def render(self):
        return ''' '''

    @memoize
    def all_sponsors(self):
        sponsors = {}
        ct = self.ct
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

    @memoize
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

    @memoize
    def levels(self):
        levels = []
        for level_id, title in SPONSOR_LEVELS:
            levels.append({'id': level_id,
                           'title': title})
        return levels


class SponsorsView(grok.View):
    """ Sponsors Summary View
    """
    grok.context(IFolder)
    grok.require('zope2.View')
    grok.name('sponsors_summary_view')

    def update(self):
        ps = getMultiAdapter((self.context, self.request),
                             name=u'plone_portal_state')
        portal = ps.portal()
        self.helper = portal.restrictedTraverse('@@sponsors-helper')

    def sponsors_by_level(self):
        levels_sponsors = self.helper.sponsors_by_level()
        for level in levels_sponsors:
            for sponsor in level.get('sponsors', []):
                image = sponsor.get('image', '')
                sponsor['image'] = image.replace('sponsor_logo', 'tileImage')
        return levels_sponsors

    def levels(self):
        return self.helper.levels()


class Sponsors(grok.Viewlet):
    """ Viewlet listing sponsors on the conference
    """

    grok.viewletmanager(IPortalFooter)
    grok.context(Interface)
    grok.order(1)

    def update(self):
        ps = getMultiAdapter((self.context, self.request),
                             name=u'plone_portal_state')
        portal = ps.portal()
        self.helper = portal.restrictedTraverse('@@sponsors-helper')

    def sponsors_by_level(self):
        return self.helper.sponsors_by_level()

    def levels(self):
        return self.helper.levels()

    def available(self):
        return True if self.sponsors_by_level() else False
