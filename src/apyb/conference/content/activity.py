# -*- coding:utf-8 -*
from Acquisition import aq_inner
from apyb.conference import MessageFactory as _
from DateTime import DateTime
from five import grok
from plone.directives import dexterity, form
from plone.indexer import indexer
from zope import schema
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory


class IActivity(form.Schema):
    """
    An activity in a conference
    """
    title = schema.TextLine(
        title=_(u'Activity Title'),
        description=_(u'Inform a title for this activity'),
        required=True,
    )

    form.widget(text='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
    text = schema.Text(
        title=_(u"Activity details"),
        required=True,
        description=_(u"A description of this activity"),
    )

    form.fieldset(
        'allocation',
        label=_(u"Activity Allocation"),
        fields=['startDate', 'endDate', 'location'],
    )

    dexterity.read_permission(location='zope2.View')
    dexterity.write_permission(location='apyb.conference.AllocateTalk')
    location = schema.Choice(
        title=_(u"Location"),
        required=False,
        description=_(u"Room where this activity will be presented"),
        vocabulary='apyb.conference.rooms',
    )
    dexterity.read_permission(startDate='zope2.View')
    dexterity.write_permission(startDate='apyb.conference.AllocateTalk')
    startDate = schema.Datetime(
        title=_(u"Start date"),
        required=False,
        description=_(u"Activity start date"),
    )

    dexterity.read_permission(endDate='zope2.View')
    dexterity.write_permission(endDate='apyb.conference.AllocateTalk')
    endDate = schema.Datetime(
        title=_(u"End date"),
        required=False,
        description=_(u"Activity end date"),
    )


class Activity(dexterity.Item):
    grok.implements(IActivity)

    def Title(self):
        return self.title


@indexer(IActivity)
def startIndexer(obj):
    if obj.startDate is None:
        return None
    #HACK: Should look into tzinfo
    return DateTime('%s-03:00' % obj.startDate.isoformat())
grok.global_adapter(startIndexer, name="start")


@indexer(IActivity)
def endIndexer(obj):
    if obj.endDate is None:
        return None
    #HACK: Should look into tzinfo
    return DateTime('%s-03:00' % obj.endDate.isoformat())
grok.global_adapter(endIndexer, name="end")


class View(dexterity.DisplayForm):
    grok.context(IActivity)
    grok.require('zope2.View')

    def update(self):
        super(View, self).update()
        context = aq_inner(self.context)
        self.context = context
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request),
                                     name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request),
                                     name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request),
                                      name=u'plone_portal_state')
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
        location = self.context.location
        start = self.context.startDate
        end = self.context.endDate
        return (review_state == 'confirmed') and location and start and end

    @property
    def show_border(self):
        ''' Is this user allowed to edit this content '''
        return self.state.is_editable()

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
