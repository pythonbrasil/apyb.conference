# -*- coding:utf-8 -*
from Acquisition import aq_inner
from Acquisition import aq_parent
from apyb.conference import MessageFactory as _
from apyb.conference.behavior.allocation import IAllocation
from collective.z3cform.datagridfield import DictRow
from DateTime import DateTime
from five import grok
from plone.directives import dexterity, form
from plone.formwidget.autocomplete import widget
from plone.indexer import indexer
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.formwidget.query.interfaces import IQuerySource
from zope import schema
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import implements
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import json
import z3c.form.interfaces
import z3c.form.widget


class SpeakerWidget(widget.AutocompleteMultiSelectionWidget):
    ''' Override input template for AutocompleteMultiFieldWidget '''

    input_template = ViewPageTemplateFile('talk_templates/input.pt')

    def new_speaker_url(self):
        ''' Return an url to @@new-speaker '''
        context = aq_inner(self.context)
        while context.portal_type not in ['program', 'Plone Site']:
            context = aq_parent(context)
        if context.portal_type == 'program':
            program_url = context.absolute_url()
            return '%s/@@new-speaker' % program_url


@implementer(z3c.form.interfaces.IFieldWidget)
def SpeakerFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, SpeakerWidget(request))


class SpeakerSource(object):
    implements(IQuerySource)

    def __init__(self, context):
        self.context = aq_inner(context)

    @property
    def speakers(self):
        return self.find_speakers()

    @property
    def all_speakers(self):
        return self.find_speakers(filter=False)

    def find_speakers(self, filter=True):
        mt = getToolByName(self.context, 'portal_membership')
        ct = getToolByName(self.context, 'portal_catalog')
        member = mt.getAuthenticatedMember()
        rolesHere = member.getRolesInContext(self.context)
        dictSearch = {'portal_type': 'speaker',
                      'sort_on': 'sortable_title'}
        if filter and not [r for r in rolesHere
                           if r in ['Manager', 'Reviewer']]:
        #Only list profiles created by this user
            dictSearch['Creator'] = member.getUserName()
        return ct.searchResults(**dictSearch)

    @property
    def vocab(self):
        return SimpleVocabulary([SimpleTerm(b.UID, b.UID, b.Title)
                                for b in self.speakers if hasattr(b, 'UID')])

    @property
    def unfiltered_vocab(self):
        return SimpleVocabulary([SimpleTerm(b.UID, b.UID, b.Title)
                                 for b in self.all_speakers
                                 if hasattr(b, 'UID')])

    def __contains__(self, term):
        return self.vocab.__contains__(term)

    def __iter__(self):
        return self.vocab.__iter__()

    def __len__(self):
        return self.vocab.__len__()

    def getTerm(self, value):
        try:
            term = self.vocab.getTerm(value)
        except LookupError:
            term = self.unfiltered_vocab.getTerm(value)
        return term

    def getTermByToken(self, value):
        try:
            term = self.vocab.getTermByToken(value)
        except LookupError:
            term = self.unfiltered_vocab.getTermByToken(value)
        return term

    def normalizeString(self, value):
        context = self.context
        return normalizeString(value, context).lower()

    def search(self, query_string):
        q = self.normalizeString(query_string)
        return [self.getTerm(b.UID) for b in self.speakers
                if q in self.normalizeString(b.Title)]


class SpeakerSourceBinder(object):
    implements(IContextSourceBinder)

    def __call__(self, context):
        return SpeakerSource(context)


class ITalkReference(Interface):
    ''' A talk reference'''

    ref_type = schema.Choice(
        title=_(u'Reference type'),
        description=_(u'Type of this reference'),
        required=True,
        vocabulary='apyb.conference.talk.referencetype',
    )

    url = schema.TextLine(
        title=_(u'URL'),
        description=_(u'Please provide a link to the reference'),
        required=True,
    )

    description = schema.TextLine(
        title=_(u'Description'),
        description=_(u'Please provide a brief description of this reference'),
        required=True,
    )


class ITalk(form.Schema):
    """
    A talk proposal
    """
    form.omitted('uid')
    uid = schema.Int(
        title=_(u"uid"),
        required=False,
    )

    form.widget(speakers=SpeakerFieldWidget)
    speakers = schema.List(
        title=_(u'Speaker'),
        description=_(u'Please fill in the name of the speaker. If no speaker '
                      u'profile was created for this name, click on '
                      u'Add new speaker'),
        default=[],
        value_type=schema.Choice(title=_(u"Speaker"),
                                 source=SpeakerSourceBinder()),
        required=True,
    )

    title = schema.TextLine(
        title=_(u'Talk Title'),
        description=_(u'Inform a talk title'),
        required=True,
    )

    form.widget(text='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
    text = schema.Text(
        title=_(u"Talk details"),
        required=True,
        description=_(u"A description of this talk"),
    )

    dexterity.read_permission(talk_type='zope2.View')
    dexterity.write_permission(talk_type='apyb.conference.AllocateTalk')
    talk_type = schema.Choice(
        title=_(u"Talk type"),
        required=True,
        description=_(u"Which type of talk best describes this one"),
        vocabulary='apyb.conference.talk.type',
    )

    language = schema.Choice(
        title=_(u"Language"),
        required=True,
        description=_(u"Speaker's language"),
        vocabulary='apyb.conference.languages',
    )

    track = schema.Choice(
        title=_(u"Track"),
        required=True,
        description=_(u"Which track this talk is"),
        vocabulary='apyb.conference.talk.tracks',
    )

    level = schema.Choice(
        title=_(u"Level"),
        required=True,
        description=_(u"Level of this talk"),
        vocabulary='apyb.conference.talk.level',
    )

    form.widget(
        references='collective.z3cform.datagridfield.DataGridFieldFactory')
    references = schema.List(
        title=_(u"References"),
        required=False,
        description=_(u"References for this talk"),
        value_type=DictRow(title=_(u'Reference'),
                           schema=ITalkReference),
    )

    iul = schema.Bool(
        title=_(u'Do you allow your image to be used in '
                u'post-conference videos?'),
        required=False,
        default=True,
    )

    form.fieldset(
        'material',
        label=_(u"Talk materials"),
        fields=['presentation', 'video', 'files'],
    )

    dexterity.read_permission(presentation='zope2.View')
    dexterity.write_permission(presentation='apyb.conference.AllocateTalk')
    presentation = schema.TextLine(
        title=_(u"Presentation file"),
        required=False,
        description=_(u"Link to the presentation file"),
    )

    dexterity.read_permission(video='zope2.View')
    dexterity.write_permission(video='apyb.conference.AllocateTalk')
    video = schema.TextLine(
        title=_(u"Presentation video"),
        required=False,
        description=_(u"Link to the presentation video"),
    )

    dexterity.read_permission(files='zope2.View')
    dexterity.write_permission(files='apyb.conference.AllocateTalk')
    files = schema.TextLine(
        title=_(u"Presentation files"),
        required=False,
        description=_(u"Link to the presentation file downloads"),
    )


class Talk(dexterity.Item):
    grok.implements(ITalk)

    def Title(self):
        return self.title


@indexer(ITalk)
def startIndexer(obj):
    if obj.startDate is None:
        return None
    #HACK: Should look into tzinfo
    return DateTime('%s-03:00' % obj.startDate.isoformat())
grok.global_adapter(startIndexer, name="start")


@indexer(ITalk)
def endIndexer(obj):
    if obj.endDate is None:
        return None
    #HACK: Should look into tzinfo
    return DateTime('%s-03:00' % obj.endDate.isoformat())
grok.global_adapter(endIndexer, name="end")


class View(dexterity.DisplayForm):
    grok.context(ITalk)
    grok.require('zope2.View')

    def update(self):
        super(View, self).update()
        context = aq_inner(self.context)
        parent = aq_parent(context)
        if parent.portal_type == 'track':
            track = parent
            program = aq_parent(track)
        else:
            program = parent
        self.context = context
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request),
                                     name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request),
                                     name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request),
                                      name=u'plone_portal_state')
        self.helper = getMultiAdapter((program, self.request),
                                      name=u'helper')
        self._ct = self.tools.catalog()
        self._mt = self.tools.membership()
        self._wt = self.tools.workflow()
        self.member = self.portal.member()
        voc_factory = queryUtility(IVocabularyFactory,
                                   'apyb.conference.rooms')
        self.rooms = voc_factory(self.context)
        self.roles_context = self.member.getRolesInContext(context)
        if not self.show_border:
            self.request['disable_border'] = True

    @property
    def show_calendar(self):
        review_state = self._wt.getInfoFor(self.context, 'review_state')
        behavior = IAllocation(self.context)
        location = behavior.location
        start = behavior.startDate
        end = behavior.endDate
        return (review_state == 'confirmed') and location and start and end

    @property
    def show_border(self):
        ''' Is this user allowed to edit this content '''
        return self.state.is_editable()

    @property
    def show_references(self):
        ''' If this talk has references, show it '''
        context = self.context
        references = context.references
        return references

    def speaker_info(self):
        ''' return information about speakers to this talk '''
        speakers = self.context.speakers
        ct = self._ct
        results = ct.searchResults(portal_type='speaker',
                                   UID=speakers)
        return results

    @property
    def location(self):
        rooms = self.rooms
        location = self.context.location
        term = rooms.getTerm(location)
        return term.title

    @property
    def date(self):
        date = self.context.startDate
        return date.strftime('%d/%m')

    @property
    def start(self):
        start = self.context.startDate
        return start.strftime('%H:%M')

    @property
    def end(self):
        end = self.context.endDate
        return end.strftime('%H:%M')


class JSONView(View):
    grok.context(ITalk)
    grok.require('zope2.View')
    grok.name('json')

    template = None

    def speakers(self):
        ''' Return a list of speakers in here '''
        speaker_image = self.helper.speaker_image_from_brain
        brains = super(JSONView, self).speaker_info()
        speakers = []
        for brain in brains:
            speaker = {'name': brain.Title,
                       'organization': brain.organization,
                       'bio': brain.Description,
                       'country': brain.country,
                       'state': brain.state,
                       'city': brain.city,
                       'language': brain.language,
                       'image_url': speaker_image(brain),
                       'url': brain.getURL(),
                       'json_url': '%s/json' % brain.getURL(),
                       }
            speakers.append(speaker)
        return speakers

    def location(self, value):
        rooms = self.rooms
        location = value
        try:
            term = rooms.getTerm(location)
        except LookupError:
            return 'PythonBrasil[7]'
        return term.title

    def render(self):
        data = {'speakers': self.speakers()}
        data['id'] = self.context.uid
        data['url'] = self.context.absolute_url()
        data['title'] = self.context.title
        data['summary'] = self.context.text
        data['creation_date'] = self.context.CreationDate()
        data['track'] = aq_parent(self.context).Title()
        data['language'] = self.context.language
        data['talk_type'] = self.context.talk_type
        data['text'] = self.context.talk_type
        data['level'] = self.context.level
        data['state'] = self._wt.getInfoFor(self.context, 'review_state')
        if data['state'] == 'confirmed':
            start = self.context.startDate
            end = self.context.endDate
            data['talk_location'] = self.location(self.context.location)
            data['talk_start'] = start.isoformat()
            data['talk_end'] = end.isoformat()
        self.request.response.setHeader('Content-Type',
                                        'application/json;charset=utf-8')
        return json.dumps(data, encoding='utf-8', ensure_ascii=False)
