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
from persistent.dict import PersistentDict
from plone.app.uuid.utils import uuidToObject
from Products.statusmessages.interfaces import IStatusMessage

class IAttendee(form.Schema):
    """
    An attendee at a conference
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

    @property
    def confirmed_trainings(self):
        payments = getattr(self, "payments", {})
        for trainings_uid_list in payments.values():
            for uid in trainings_uid_list:
                yield uid

    @property
    def pending_trainings(self):
        all_trainings = set(getattr(self, "trainings", []))
        confirmed = set(self.confirmed_trainings)
        return [uuidToObject(uid) for uid in all_trainings.difference(confirmed)]


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

    def has_registered_trainings(self):
        return getattr(self.context, "payments", {}) or self.context.trainings

    def registered_trainings(self):
        trainings = self.trainings
        def training_with_status(uid, registration_status):
            t = trainings[uid]
            t.update(registration_status = registration_status)
            return t
        remaining = list(self.context.trainings)
        for uid in self.context.confirmed_trainings:
            remaining.remove(uid) # a confirmed trainings must be in the list of trainings
            yield training_with_status(uid, "confirmed")
        for uid in remaining:
            yield training_with_status(uid, "payment pending")

    def available_trainings(self):
        trainings = self.trainings
        confirmed = set(self.context.confirmed_trainings)
        selected = set(self.context.trainings)
        sorted_uids_trainings = sorted(trainings.items(), key=lambda (u,t): t['title'])
        seat_table = SeatTable(self.context)
        for uid, training in sorted_uids_trainings:
            state = training.get('review_state', '')
            if not (state == 'confirmed'):
                continue
            available_seats = seat_table.available_seats(uid)
            training.update(selected = uid in selected,
                            disabled = (uid in confirmed or
                                        (not available_seats and
                                         uid not in (selected - confirmed))),
                            available_seats = available_seats,)
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


class SeatTable(object):
    # ad-hoc seat table
    # XXX do this in a more standard way

    def __init__(self, context):
        register = context.register # via acquisition :P
        self.table = getattr(register, 'seat_table', PersistentDict())
        if not self.table:
            register.seat_table = self.table

    def refresh_attendee_trainings(self, attendee, training_uids):
        code = '/'.join((attendee.getParentNode().id, attendee.id))
        # remove attendee from the table
        for attendee_set in self.table.values():
            attendee_set.discard(code)
        # add to where she belongs
        for uid in training_uids:
            attendee_set = self.table.get(uid, set())
            attendee_set.add(code)
            self.table[uid] = attendee_set

    def available_seats(self, training_uid):
        training = uuidToObject(training_uid)
        total = training.seats or 0
        taken = len(self.table.get(training_uid, set()))
        # the result should be positive, but we can be cautious here
        return max(total - taken, 0)


class RegisterView(View):
    grok.context(IAttendee)
    grok.require('cmf.ReviewPortalContent')
    grok.name('register_trainings')

    template = None

    def render(self):
        this_attendee = self.context
        trainings_uid = self.request.form.get('trainings_uid', [])
        if isinstance(trainings_uid, str):
            trainings_uid = [trainings_uid, ]
        seat_table = SeatTable(this_attendee)

        # confirmed trainings are always part of the selection
        all_trainings = list(this_attendee.confirmed_trainings)
        for uid in trainings_uid:
            if uid not in all_trainings:
                # was this training already ours
                # OR are there still available seats?
                if uid in this_attendee.trainings or seat_table.available_seats(uid):
                    all_trainings.append(uid)
                else:
                    training = uuidToObject(uid)
                    messages = IStatusMessage(self.request)
                    warning = _(u'This training is already fully booked') + ': ' + training.title
                    messages.addStatusMessage(warning, type="warning")
        # reserve a seat for each training
        seat_table.refresh_attendee_trainings(this_attendee, all_trainings)
        # store the list of trainings of this attendee
        this_attendee.trainings = all_trainings
        this_attendee.reindexObject(idxs=['trainings', ])
        # set the time of this operation for use in liberation of blocked seats
        this_attendee.last_time_trainings_were_set = datetime.now()
        if self.request.get('finish_button'):
            # back to the registration
            return self.request.response.redirect(this_attendee.getParentNode().absolute_url())
        else:
            return self.request.response.redirect(this_attendee.absolute_url())

