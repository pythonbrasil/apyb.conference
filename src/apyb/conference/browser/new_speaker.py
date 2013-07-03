# -*- coding:utf-8 -*-
from apyb.conference import MessageFactory as _
from apyb.conference.behavior.address import IAddress
from apyb.conference.content.program import IProgram
from apyb.conference.content.speaker import ISpeaker
from five import grok
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.directives import form
from zope.component import getMultiAdapter


class ISpeakerForm(ISpeaker, IAddress):
    form.fieldset(
        'speaker',
        label=_(u"About the speaker"),
        fields=['fullname', 'organization', 'description', 'language',
                'email', 'home_page', 'country', 'state', 'city', 'image']
    )
    form.omitted('address')
    form.omitted('postcode')


class SpeakerForm(form.SchemaAddForm):
    ''' Speaker profile '''
    grok.context(IProgram)
    grok.require('apyb.conference.AddSpeaker')
    grok.name('new-speaker')

    label = _(u"Speaker Profile")

    schema = ISpeakerForm

    enable_form_tabbing = False

    def update(self):
        super(SpeakerForm, self).update()
        # We have only one fieldset
        self.groups[0].widgets['description'].rows = 10

    def create(self, data):
        ''' Create objects '''
        speaker = createContent('speaker', checkConstraints=True, **data)
        return speaker

    def add(self, object):
        speaker = object
        context = self.context
        speakerObj = addContentToContainer(context, speaker)
        self.immediate_view = "%s/%s" % (context.absolute_url(), speakerObj.id)


@form.default_value(field=ISpeakerForm['country'], form=SpeakerForm)
def default_country(data):
    return u'br'


@form.default_value(field=ISpeakerForm['email'])
def default_email(data):
    state = getMultiAdapter((data.context, data.request),
                            name=u'plone_portal_state')
    member = state.member()
    return member.getProperty('email')


@form.default_value(field=ISpeakerForm['fullname'])
def default_fullname(data):
    state = getMultiAdapter((data.context, data.request),
                            name=u'plone_portal_state')
    member = state.member()
    return member.getProperty('fullname')


@form.default_value(field=ISpeakerForm['home_page'])
def default_home_page(data):
    state = getMultiAdapter((data.context, data.request),
                            name=u'plone_portal_state')
    member = state.member()
    return member.getProperty('home_page')
