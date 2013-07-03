# -*- coding:utf-8 -*-
from apyb.conference import MessageFactory as _
from apyb.conference.content.program import IProgram
from apyb.conference.content.track import ITrack
from apyb.conference.content.training import ITraining
from five import grok
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.directives import form
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter


class ITrainingForm(ITraining):
    ''' An interface representing a training submission form '''

    form.fieldset(
        'speaker',
        label=_(u"About the speaker"),
        fields=['speakers', ],
    )

    form.fieldset(
        'training',
        label=_(u"About the training"),
        fields=['title', 'text', 'track', 'language', 'level', ],
    )

    form.omitted('location')
    form.omitted('startDate')
    form.omitted('endDate')
    form.omitted('presentation')
    form.omitted('video')
    form.omitted('files')

    form.fieldset(
        'legal',
        label=_(u"Legal information"),
        fields=['iul', ],
    )


class ITrackTrainingForm(ITrainingForm):
    ''' An interface representing a training submission form inside a track'''

    form.omitted('track')


class TrainingForm(form.SchemaAddForm):
    ''' Training submission form '''
    grok.context(IProgram)
    grok.require('apyb.papers.AddTraining')
    grok.name('new-training')

    template = ViewPageTemplateFile('templates/new_training.pt')

    label = _(u"Training submission")
    description = _(u"")

    schema = ITrainingForm

    inside_track = False
    enable_form_tabbing = False

    def track_object(self, training):
        ''' Return Track which will host this training '''
        if self.inside_track:
            track = self.context
        else:
            UID = training.track
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
        trainingfields = ['speakers', 'title', 'text', 'track', 'language',
                          'level', 'iul']
        traininginfo = dict([(k, data.get(k, '')) for k in trainingfields])
        if self.inside_track:
            traininginfo['track'] = self.context.UID()
        training = createContent('training',
                                 checkConstraints=True, **traininginfo)
        return training

    def add(self, object):
        training = object
        # We look for the right track to add the training
        context = self.track_object(training)
        trainingObj = addContentToContainer(context, training)
        self.immediate_view = "%s/%s" % (context.absolute_url(),
                                         trainingObj.id)


class TrackTrainingForm(TrainingForm):
    ''' Training submission form '''
    grok.context(ITrack)

    schema = ITrackTrainingForm

    inside_track = True


@form.default_value(field=ITrainingForm['speakers'])
def default_speakers(data):
    tools = getMultiAdapter((data.context, data.request),
                            name=u'plone_tools')
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
