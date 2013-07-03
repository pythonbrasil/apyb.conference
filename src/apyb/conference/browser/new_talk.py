# -*- coding:utf-8 -*-
from apyb.conference import MessageFactory as _
from apyb.conference.content.program import IProgram
from apyb.conference.content.talk import ITalk
from apyb.conference.content.track import ITrack
from five import grok
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.directives import form
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter


class ITalkForm(ITalk):
    ''' An interface representing a talk submission form '''

    form.fieldset(
        'speaker',
        label=_(u"About the speaker"),
        fields=['speakers', ]
    )

    form.fieldset(
        'talk',
        label=_(u"About the talk"),
        fields=['title', 'text', 'talk_type', 'track', 'language', 'level', ]
    )
    form.omitted('talk_type')
    form.omitted('location')
    form.omitted('startDate')
    form.omitted('endDate')
    form.omitted('presentation')
    form.omitted('video')
    form.omitted('files')

    form.omitted('references')
    form.fieldset(
        'metatalk',
        label=_(u"References for this talk"),
        fields=['references', ]
    )

    form.fieldset(
        'legal',
        label=_(u"Legal information"),
        fields=['iul', ]
    )


class ITrackTalkForm(ITalkForm):
    ''' An interface representing a talk submission form inside a track'''

    form.omitted('track')


class TalkForm(form.SchemaAddForm):
    ''' Talk submission form '''
    grok.context(IProgram)
    grok.require('apyb.conference.AddTalk')
    grok.name('new-talk')

    template = ViewPageTemplateFile('templates/new_talk.pt')

    label = _(u"Talk submission")
    description = _(u"")

    schema = ITalkForm

    inside_track = False
    enable_form_tabbing = False

    def track_object(self, talk):
        ''' Return Track which will host this talk '''
        if self.inside_track:
            track = self.context
        else:
            UID = talk.track
            ct = getToolByName(self.context, 'portal_catalog')
            results = ct.searchResults(portal_type='track',
                                       UID=UID)
            if not results:
                # oops
                # something wrong happened, but let's be safe
                track = self.context
            else:
                track = results[0].getObject()

        return track

    def create(self, data):
        ''' Create objects '''
        talkfields = ['speakers', 'title', 'text', 'talk_type', 'track',
                      'language', 'level', 'references', 'iul', ]
        talkinfo = dict([(k, data.get(k, '')) for k in talkfields])
        if self.inside_track:
            talkinfo['track'] = IUUID(self.context)
        talk = createContent('talk', checkConstraints=True, **talkinfo)
        return talk

    def add(self, object):
        talk = object
        # We look for the right track to add the talk
        context = self.track_object(talk)
        talkObj = addContentToContainer(context, talk)
        self.immediate_view = "%s/%s" % (context.absolute_url(), talkObj.id)


class TrackTalkForm(TalkForm):
    ''' Talk submission form '''
    grok.context(ITrack)

    schema = ITrackTalkForm

    inside_track = True


@form.default_value(field=ITalkForm['speakers'])
def default_speakers(data):
    tools = getMultiAdapter((data.context, data.request), name=u'plone_tools')
    state = getMultiAdapter((data.context, data.request),
                            name=u'plone_portal_state')
    ct = tools.catalog()
    member = state.member()
    email = member.getProperty('email')
    results = ct.searchResults(portal_type='speaker', email=email)
    if results:
        # We consider the first result as the most important one
        brain = results[0]
        UID = brain.UID
        return [UID, ]
