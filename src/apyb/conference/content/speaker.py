# -*- coding:utf-8 -*-
from Acquisition import aq_inner
from apyb.conference import MessageFactory as _
from apyb.conference.content.attendee import IAttendee
from five import grok
from plone.directives import dexterity, form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.namedfile.field import NamedBlobImage
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getMultiAdapter, queryUtility
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import json


class ISpeaker(form.Schema):
    """
    A Speaker profile
    """

    form.omitted('uid')
    uid = schema.Int(
        title=_(u"uid"),
        required=False,
    )

    fullname = schema.TextLine(
        title=_(u'Fullname'),
        description=_(u'Please inform your fullname'),
        required=True,
    )

    description = schema.Text(
        title=_(u"Resumee"),
        required=True,
        description=_(u"A brief resumee"),
    )

    organization = schema.TextLine(
        title=_(u"Organization"),
        required=True,
        description=_(u"Organization you represent"),
    )

    email = schema.TextLine(
        title=_(u"Email"),
        required=True,
        description=_(u"Speaker's email"),
    )

    home_page = schema.TextLine(
        title=_(u"Site"),
        required=True,
        description=_(u"Speaker's site"),
    )

    language = schema.Choice(
        title=_(u"Language"),
        required=True,
        description=_(u"Speaker's language"),
        vocabulary='apyb.conference.languages',
    )

    image = NamedBlobImage(
        title=_(u"Portrait"),
        required=False,
        description=_(u"Upload an image to be used as speakers' portrait."),
    )

    form.fieldset(
        'registration',
        label=_(u"Registering Information"),
        fields=['registration', ],
    )
    dexterity.read_permission(registration='cmf.ReviewPortalContent')
    dexterity.write_permission(registration='cmf.ReviewPortalContent')
    registration = RelationChoice(
        title=_(u"Registration"),
        source=ObjPathSourceBinder(
            object_provides=IAttendee.__identifier__
        ),
        required=False,
    )


class Speaker(dexterity.Item):
    grok.implements(ISpeaker)

    def _get_title(self):
        return self.fullname

    def _set_title(self, value):
        pass
    title = property(_get_title, _set_title)

    def Title(self):
        return self.title

    def Description(self):
        return self.description

    def UID(self):
        return self.uid

    @property
    def uid(self):
        intids = getUtility(IIntIds)
        return intids.getId(self)


class View(grok.View):
    grok.context(ISpeaker)
    grok.require('zope2.View')

    def update(self):
        super(View, self).update()
        context = aq_inner(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.state = self._multi_adapter(u'plone_context_state')
        self.tools = self._multi_adapter(u'plone_tools')
        self.portal = self._multi_adapter(u'plone_portal_state')
        self.helper = self._multi_adapter(u'program_helper')
        voc_factory = queryUtility(IVocabularyFactory,
                                   'apyb.conference.talk.rooms')
        self.rooms = voc_factory(self.context)
        self._ct = self.tools.catalog()
        self._mt = self.tools.membership()
        self.speaker_uid = self.context.UID()
        self.member = self.portal.member()
        self.roles_context = self.member.getRolesInContext(context)
        if not self.show_border:
            self.request['disable_border'] = True

    def _multi_adapter(self, name):
        return getMultiAdapter((self.context, self.request), name=name)

    @property
    def show_border(self):
        ''' Is this user allowed to edit this content '''
        return self.state.is_editable()

    def speakers(self, speaker_uids):
        ''' Given a list os uids, we return a list of
            dicts with speakers data '''
        ct = self._ct
        brains = ct.searchResults(portal_type='apyb.conference.speaker',
                                  UID=speaker_uids)
        speakers = [{'name':b.Title,
                     'organization':b.organization,
                     'bio':b.Description,
                     'country':b.country,
                     'state':b.state,
                     'city':b.city,
                     'url':b.getURL(),
                     'json_url':'%s/json' % b.getURL(),
                     }
                    for b in brains]
        return speakers

    def track_info(self, track_uid):
        helper = self.helper
        return helper.track_info(track_uid)

    def speaker_name(self, speaker_uids):
        ''' Given a list os uids, we return a string with speakers names '''
        helper = self.helper
        speakers_dict = helper.speakers_dict
        results = [speaker for uid, speaker in speakers_dict.items()
                   if uid in speaker_uids]
        return ', '.join([b['name'] for b in results])

    def my_talks(self):
        ''' Return a list of my talks '''
        helper = self.helper
        kw = {'speakers': (self.speaker_uid, ),
              'sort_on': 'sortable_title'}
        results = helper.talks(**kw)
        return results

    def my_talks_accepted(self):
        ''' Return a list of my talks waiting for confirmation '''
        helper = self.helper
        kw = {'speakers': (self.speaker_uid, ),
              'review_state': 'accepted',
              'sort_on': 'sortable_title'}
        results = helper.talks(**kw)
        return results

    def my_talks_confirmed(self):
        ''' Return a list of my talks waiting for confirmation '''
        helper = self.helper
        kw = {'speakers': (self.speaker_uid, ),
              'review_state': 'confirmed',
              'sort_on': 'sortable_title'}
        results = helper.talks(**kw)
        return results


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
        brains = super(JSONView, self).my_talks()
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
            talk['points'] = brain.points or 0.0
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
        speaker_image = self.helper.speaker_image
        data = {'name': self.context.title,
                'organization': self.context.organization,
                'bio': self.context.description,
                'country': self.context.country,
                'state': self.context.state,
                'city': self.context.city,
                'language': self.context.language,
                'image_url': speaker_image(self.context),
                'url': self.context.absolute_url()}
        data['talks'] = talks

        self.request.response.setHeader('Content-Type',
                                        'application/json;charset=utf-8')
        return json.dumps(data, encoding='utf-8', ensure_ascii=False)
