# -*- coding:utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from apyb.conference import MessageFactory as _
from five import grok
from plone.directives import dexterity
from plone.directives import form
from plone.indexer import indexer
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from datetime import datetime

class IAttendee(form.Schema):
    """
    An attenddee at a conference
    """
    form.omitted('uid')
    uid = schema.Int(
        title=_(u"uid"),
        required=False,
    )

    registration_type = schema.Choice(
        title=_(u'Type'),
        description=_(u'Select the category of your registration'),
        required=False,
        vocabulary="apyb.conference.types",
    )

    fullname = schema.TextLine(
        title=_(u'Fullname'),
        description=_(u'Please inform your fullname'),
        required=True,
    )

    badge_name = schema.TextLine(
        title=_(u'Badge name'),
        description=_(u'Please inform the name that will appear on your badge'
                      u' -- Leave it blank to use your fullname in the badge'),
        required=False,
        missing_value=u'',
    )

    organization = schema.TextLine(
        title=_(u'Organization'),
        description=_(u'Please inform the name of the organization you'
                      u'will represent.'),
        required=False,
        missing_value=u'',
    )

    gender = schema.Choice(
        title=_(u'Gender'),
        required=True,
        vocabulary="apyb.conference.gender",
    )

    t_shirt_size = schema.Choice(
        title=_(u'T-Shirt Size'),
        required=True,
        vocabulary="apyb.conference.tshirt",
    )

    caipirinha = schema.Choice(
        title=_(u'Caipirinha Sprint'),
        description=_(u'Will you attend Caipirinha Sprint in Joao Pessoa/PB? '
                      u'Please select if you are attending and how many '
                      u'people you will pay for the hotel accomodation. '
                      u'Payment in here will cover your stay from October 7th '
                      u'to October 11th.'),
        required=True,
        vocabulary="apyb.conference.caipirinha",
    )

    wall = schema.Choice(
        title=_(u'Name on the wall'),
        description=_(u'Support our conference and have your name displayed '
                      u'on a (huge) wall in the entrance of the convention '
                      u'center.'),
        required=True,
        vocabulary="apyb.conference.wall",
    )

    form.omitted('trainings')
    trainings = schema.List(
        title=_(u'Trainings'),
        description=_(u'Select trainings you plan to attendee.'),
        default=[],
        value_type=schema.Choice(title=_(u"Training"),
                                 vocabulary='apyb.conference.trainings'),
        required=False,
    )


class Attendee(dexterity.Item):
    grok.implements(IAttendee)

    def _get_title(self):
        return self.fullname

    def _set_title(self, value):
        pass

    title = property(_get_title, _set_title)

    def Title(self):
        return self.title

    @property
    def uid(self):
        intids = getUtility(IIntIds)
        return intids.getId(self)

    def UID(self):
        return self.uid


@indexer(IAttendee)
def registration_type(obj):
    return [obj.registration_type, ]
grok.global_adapter(registration_type, name="Subject")


class View(grok.View):
    grok.context(IAttendee)
    grok.require('zope2.View')

    def update(self):
        super(View, self).update()
        context = aq_inner(self.context)
        registration = aq_parent(context)
        registrations = aq_parent(registration)
        self.registration_type = self.context.registration_type
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request),
                                     name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request),
                                     name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request),
                                      name=u'plone_portal_state')
        self.helper = getMultiAdapter((registrations, self.request),
                                      name=u'helper')
        portal = self.portal.portal()
        program = portal.program
        self.program_helper = getMultiAdapter((program, self.request),
                                              name=u'helper')
        self._ct = self.tools.catalog()
        self.member = self.portal.member()
        self.voc = self._vocab('apyb.conference.types')
        self.caipirinha = self._vocab('apyb.conference.caipirinha')
        self.wall = self._vocab('apyb.conference.wall')

        self.roles_context = self.member.getRolesInContext(context)
        if not [r for r in self.roles_context
                if r in ['Manager', 'Editor', 'Reviewer', ]]:
            self.request['disable_border'] = True

    def _vocab(self, name):
        factory = queryUtility(IVocabularyFactory, name)
        return factory(self.context)

    @property
    def trainings(self):
        program_helper = self.program_helper
        trainings_dict = program_helper.trainings_dict
        return trainings_dict

    @property
    def confirmed_trainings(self):
        payments = getattr(self.context, "payments", {})
        for trainings_uid_list in payments.values():
            for uid in trainings_uid_list:
                yield uid

    def has_registered_trainings(self):
        return getattr(self.context, "payments", {}) or self.context.trainings

    def registered_trainings(self):
        trainings = self.trainings
        def training_with_status(uid, registration_status):
            t = trainings[uid]
            t.update(registration_status = registration_status)
            return t
        remaining = list(self.context.trainings)
        for uid in self.confirmed_trainings:
            remaining.remove(uid) # a confirmed trainings must be in the list of trainings
            yield training_with_status(uid, "confirmed")
        for uid in remaining:
            yield training_with_status(uid, "payment pending")

    def available_trainings(self):
        trainings = self.trainings
        confirmed_trainings_set = set(self.confirmed_trainings)
        selected_set = set(self.context.trainings)
        sorted_uids_trainings = sorted(trainings.items(), key=lambda (u,t): t['title'])
        for uid, training in sorted_uids_trainings:
            state = training.get('review_state', '')
            seats = training.get('seats', 0)
            if not (state == 'confirmed' and seats):
                continue
            training.update(confirmed = uid in confirmed_trainings_set,
                            selected = uid in selected_set)
            yield training

    def caipirinha_sprint(self):
        context = self.context
        caipirinha = context.caipirinha
        term = self.caipirinha.getTerm(caipirinha)
        return term.title

    def wall_status(self):
        context = self.context
        wall = context.wall
        term = self.wall.getTerm(wall)
        return term.title

    @property
    def confirmed(self):
        # TODO: remove if not used anymore ################################################################
        state = self.state
        review_state = state.workflow_state()
        return review_state == 'confirmed'

    @property
    def attended(self):
        state = self.state
        review_state = state.workflow_state()
        return review_state == 'attended'

    @property
    def allow_training_registering(self):
        if not 'Manager' in self.roles_context:
            return False
        # TODO: remove if not used anymore ################################################################
        # return self.confirmed

        # everyone can register for a training and pay everything at once
        return True

    @property
    def fmt_registration_type(self):
        registration_type = self.registration_type
        if registration_type:
            term = self.voc.getTerm(registration_type)
            return term.title


class RegisterView(View):
    grok.context(IAttendee)
    grok.require('cmf.ReviewPortalContent')
    grok.name('register_trainings')

    template = None

    def render(self):
        trainings_uid = self.request.form.get('trainings_uid', [])
        if isinstance(trainings_uid, str):
            trainings_uid = [trainings_uid, ]
        all_trainings = list(self.confirmed_trainings)
        for uid in trainings_uid:
            if uid not in all_trainings:
                all_trainings.append(uid)
        self.context.trainings = all_trainings
        # sets the time of this operation for use in liberation of blocked seats
        self.context.last_time_trainings_were_set = datetime.now()
        self.context.reindexObject(idxs=['trainings', ])
        return self.request.response.redirect(self.context.absolute_url())
