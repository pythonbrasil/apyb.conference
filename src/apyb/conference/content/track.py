# -*- coding:utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from apyb.conference import MessageFactory as _
from five import grok
from plone.directives import dexterity, form
from plone.namedfile.field import NamedBlobImage
from zope import schema
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory

import json


class ITrack(form.Schema):
    """
    A track within a conference
    """

    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Please inform title for this track'),
        required=True,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=True,
        description=_(u"A brief description of this track."),
    )

    image = NamedBlobImage(
        title=_(u"Track Logo"),
        required=False,
        description=_(u"Upload an image to be used as this track's logo."),
    )


class Track(dexterity.Container):
    grok.implements(ITrack)

    def Title(self):
        return self.title

    def Description(self):
        return self.description


class View(grok.View):
    grok.context(ITrack)
    grok.require('zope2.View')

    def update(self):
        super(View, self).update()
        context = aq_inner(self.context)
        program = aq_parent(context)
        while program.portal_type not in ('program', 'Plone Site'):
            program = aq_parent(program)
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request),
                                     name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request),
                                     name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request),
                                      name=u'plone_portal_state')
        self.helper = getMultiAdapter((program, self.request),
                                      name=u'helper')
        voc_factory = queryUtility(IVocabularyFactory,
                                   'apyb.conference.rooms')
        self.rooms = voc_factory(self.context)
        self._ct = self.tools.catalog()
        self._mt = self.tools.membership()
        self.member = self.portal.member()
        self.member_id = self.member.id
        if not self.show_border:
            self.request['disable_border'] = True

    @property
    def vocabs(self):
        if not hasattr(self, "_vocabs"):
            vocabs = {}
            vocabs['languages'] = queryUtility(IVocabularyFactory,
                                               'apyb.conference.languages')
            vocabs['level'] = queryUtility(IVocabularyFactory,
                                           'apyb.conference.talk.level')
            self._vocabs = dict((key, value(self))
                                for key, value in vocabs.items())
        return self._vocabs

    def speakers(self, speaker_uids):
        ''' Given a list os uids,
            we return a list of dicts with speakers data
        '''
        speaker_image = self.helper.speaker_image_from_brain
        ct = self._ct
        brains = ct.searchResults(portal_type='speaker',
                                  UID=speaker_uids)
        speakers = [{'name': b.Title,
                     'organization': b.organization,
                     'bio': b.Description,
                     'country': b.country,
                     'state': b.state,
                     'city': b.city,
                     'image_url': speaker_image(b),
                     'url': b.getURL(),
                     'json_url': '%s/json' % b.getURL(),
                     }
                    for b in brains]
        return speakers

    def speaker_name(self, speaker_uids):
        ''' Given a list os uids, we return a string with speakers names '''
        speakers = self.speakers(speaker_uids)
        return ', '.join([b['name'] for b in speakers])

    @property
    def can_submit(self):
        ''' This user can submit a talk in here'''
        context = self.context
        return self._mt.checkPermission('apyb.conference: Add Talk',
                                        context)

    @property
    def show_border(self):
        ''' Is this user allowed to edit this content '''
        return self.state.is_editable()

    def memberdata(self, userid=None):
        ''' Return memberdata for a userid '''
        memberdata = self._mt.getMemberById(userid)
        if memberdata:
            return memberdata.getProperty('fullname', userid) or userid
        else:
            return userid

    def pending_talks(self, **kw):
        ''' Return a list of pending in here '''
        kw['sort_on'] = 'sortable_title'
        kw['sort_order'] = 'reverse'
        kw['review_state'] = 'created'
        results = self.talks(**kw)
        return results

    def confirmed_talks(self, **kw):
        ''' Return a list of talks in here '''
        kw['sort_on'] = 'sortable_title'
        kw['sort_order'] = 'reverse'
        kw['review_state'] = 'confirmed'
        results = self.talks(**kw)
        return results

    def ordered_talks(self, **kw):
        ''' Return a list of talks in here '''
        kw['sort_on'] = 'sortable_title'
        kw['sort_order'] = 'reverse'
        results = self.talks(**kw)
        return results

    def talks(self, **kw):
        ''' Return a list of talks in here '''
        kw['portal_type'] = 'talk'
        if self.context.getId() == 'training':
            kw['portal_type'] = 'training'
        kw['path'] = self._path
        if not 'sort_on' in kw:
            kw['sort_on'] = 'sortable_title'
        results = self._ct.searchResults(**kw)
        return results


class TalksView(View):
    grok.name('talks')


class JSONView(View):
    grok.name('json')

    template = None

    def location(self, value):
        rooms = self.rooms
        location = value
        try:
            term = rooms.getTerm(location)
        except LookupError:
            return 'PythonBrasil[7]'
        return term.title

    def talks(self):
        ''' Return a list of talks in here '''
        brains = super(JSONView, self).talks()
        talks = []
        for brain in brains:
            talk = {}
            talk['id'] = brain.UID
            talk['creation_date'] = brain.CreationDate
            talk['title'] = brain.Title
            talk['description'] = brain.Description
            talk['track'] = self.context.title
            talk['speakers'] = self.speakers(brain.speakers)
            talk['language'] = brain.language
            talk['state'] = brain.review_state
            if talk['state'] == 'confirmed':
                talk['talk_location'] = self.location(brain.location)
                talk['talk_start'] = brain.start.asdatetime().isoformat()
                talk['talk_end'] = brain.end.asdatetime().isoformat()
            talk['url'] = '%s' % brain.getURL()
            talk['json_url'] = '%s/json' % brain.getURL()
            talks.append(talk)
        return talks

    def render(self):
        talks = self.talks()
        data = {'talks': talks}
        data['url'] = self.context.absolute_url()
        data['title'] = self.context.title
        data['description'] = self.context.description
        data['total_talks'] = len(talks)
        self.request.response.setHeader('Content-Type',
                                        'application/json;charset=utf-8')
        return json.dumps(data,
                          encoding='utf-8',
                          ensure_ascii=False)
