# -*- coding:utf-8 -*-
from Acquisition import aq_inner
from five import grok
from plone.app.collection.interfaces import ICollection
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory

grok.templatedir('templates')


class CollectionTalks(grok.View):
    grok.context(ICollection)
    grok.require('zope2.View')
    grok.name('collection_talks')

    def update(self):
        super(CollectionTalks, self).update()
        context = aq_inner(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        voc_factory = queryUtility(IVocabularyFactory,
                                   'apyb.conference.rooms')
        self.rooms = voc_factory(self.context)

        portal = self.portal.portal()
        program = portal.restrictedTraverse('program')
        self.helper = getMultiAdapter((program, self.request), name=u'helper')

    def speaker_name(self, speaker_uids):
        ''' Given a list os uids, we return a string with speakers names '''
        if speaker_uids:
            helper = self.helper
            speakers_dict = helper.speakers_dict
            results = [speaker for uid, speaker in speakers_dict.items() if uid in speaker_uids]
            speakers = ', '.join([b['name'] for b in results])
        else:
            speakers = 'PythonBrasil[9]'
        return speakers

    def track_info(self, track_uid):
        if track_uid:
            helper = self.helper
            info = helper.track_info(track_uid)
        else:
            info = {'title': 'PythonBrasil[9]', }
        return info

    def show_calendar(self, item):
        location = item.location
        start = item.start
        end = item.end
        return location and start and end

    def location(self, item):
        rooms = self.rooms
        location = item.location
        term = rooms.getTerm(location)
        return term.title

    def date(self, item):
        date = item.start
        return date.strftime('%d/%m')

    def start(self, item):
        start = item.start
        return start.strftime('%H:%M')
