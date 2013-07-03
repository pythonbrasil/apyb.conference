# -*- coding:utf-8 -*-
from apyb.conference import MessageFactory as _
from apyb.conference.behavior.address import IAddress
from apyb.conference.behavior.contactinfo import INetContactInfo
from apyb.conference.behavior.optininformation import IOptInInformation
from apyb.conference.content.attendee import IAttendee
from apyb.conference.content.registration import IRegistration
from apyb.conference.content.registrations import IRegistrations
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from five import grok
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.directives import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import getMultiAdapter
from zope.event import notify
from zope.interface import Interface, invariant, Invalid
from zope.lifecycleevent import ObjectCreatedEvent

from apybcheck import check_apyb_membership

grok.templatedir('templates')


class IIndividualForm(IRegistration, IAttendee, IAddress,
                      INetContactInfo, IOptInInformation):
    """
    A registration in a conference
    """
    form.fieldset('default',
                  label=_(u"Personal information"),
                  fields=['fullname', 'badge_name', 'organization',
                          'gender', 't_shirt_size'])
    form.fieldset('contact',
                  label=_(u"Contact Info"),
                  fields=['email', 'twitter', 'irc_nickname', 'site'])
    form.fieldset('location',
                  label=_(u"Location"),
                  fields=['country', 'state', 'city'])
    form.fieldset('additional',
                  label=_(u"Additional packages"),
                  fields=['caipirinha', 'wall'])
    form.fieldset('opting',
                  label=_(u"Opt-In"),
                  fields=['conference', 'partners'])
    form.fieldset('extra',
                  label=_(u"Discount"),
                  fields=['discount_code'])

    email = schema.TextLine(
        title=_(u'E-mail'),
        description=_(u'Please provide an email address'),
        required=True,
    )

    state = schema.TextLine(
        title=_(u'State /Province'),
        description=_(u'Inform the state / provice you live.'),
        required=True,
    )

    form.omitted('uid')
    form.omitted('address')
    form.omitted('postcode')
    form.omitted('registration_type')


class IAPyBRegistration(IIndividualForm):

    @invariant
    def addressInvariant(data):
        check = check_apyb_membership(data.email)
        if check == 'invalid':
            raise Invalid(_(u"The email address you provided does not match any APyB merbership account."))
        elif check == 'inactive':
            raise Invalid(_(u"Your APyB merbership is inactive and needs to be renewed."))


class IAttendeeItem(Interface):

    fullname = schema.TextLine(
        title=_(u'Fullname'),
        description=_(u'Please inform your fullname'),
        required=True,
    )

    email = schema.TextLine(
        title=_(u'E-mail'),
        description=_(u'Please provide an email address'),
        required=True,
    )

    gender = schema.Choice(
        title=_(u'Gender'),
        required=True,
        vocabulary="apyb.conference.gender"
    )

    t_shirt_size = schema.Choice(
        title=_(u'T-Shirt Size'),
        required=True,
        vocabulary="apyb.conference.tshirt"
    )

    caipirinha = schema.Choice(
        title=_(u'Caipirinha Sprint'),
        vocabulary='apyb.conference.caipirinha',
        required=True,
    )

    wall = schema.Choice(
        title=_(u'Wall of supporters'),
        vocabulary='apyb.conference.wall',
        required=True,
    )


class IGroupForm(IRegistration, IAddress, IOptInInformation):
    """
    A registration with multiple Attendees in a conference
    """
    form.fieldset('organization',
                  label=_(u"Organization info"),
                  fields=['organization', 'email'])
    form.fieldset('attendees',
                  label=_(u"List of Attendees"),
                  fields=['attendees'])
    form.fieldset('location',
                  label=_(u"Location"),
                  fields=['country', 'state', 'city'])
    form.fieldset('opting',
                  label=_(u"Opt-In"),
                  fields=['conference', 'partners'])
    form.fieldset('extra',
                  label=_(u"Discount"),
                  fields=['discount_code'])

    organization = schema.TextLine(
        title=_(u'Organization'),
        description=_(u'''Please inform the name of the organization '''
                      u'''you will represent'''),
        required=False,
        missing_value=u'',
    )

    email = schema.TextLine(
        title=_(u'E-mail'),
        description=_(u'''Please provide an email address to be used '''
                      u'''to manage this registration.'''),
        required=True,
    )

    state = schema.TextLine(
        title=_(u'State /Province'),
        description=_(u'Inform the state / provice you live.'),
        required=True,
    )

    attendees = schema.List(
        title=_(u'Attendees'),
        description=_(u'Please inform who will attendee this conference.'),
        value_type=DictRow(title=_(u'Attendee'),
                           schema=IAttendeeItem),
        required=True)

    form.omitted('uid')
    form.omitted('address')
    form.omitted('postcode')
    form.omitted('registration_type')


class AddForm(form.SchemaAddForm):
    grok.context(IRegistrations)
    grok.require('apyb.conference.AddRegistration')

    label = (u"Register")
    description = (u"Register to this conference")

    template = ViewPageTemplateFile('templates/register.pt')

    schema = IIndividualForm

    enable_form_tabbing = False
    registration_type = u''
    member = None

    def __init__(self, context, request):
        super(AddForm, self).__init__(context, request)

    def update(self):
        super(AddForm, self).update()
        self.request['disable_plone.leftcolumn'] = 1
        self.request['disable_plone.rightcolumn'] = 1

    def create(self, data):
        ''' Create objects '''
        reg_fields = ['discount_code']
        data['registration_type'] = self.registration_type

        reg_data = dict([(k, data[k]) for k in reg_fields])
        reg_data['email'] = data['email']
        reg_data['city'] = data['city']
        reg_data['state'] = data['state']
        reg_data['country'] = data['country']
        reg_data['registration_type'] = data['registration_type']
        registration = createContent('registration',
                                     checkConstraints=True, **reg_data)

        for k in reg_fields:
            del data[k]
        # Create attendee object
        attendee = createContent('attendee',
                                 checkConstraints=True, **data)
        return [registration, attendee]

    def add(self, object):
        registration, attendee = object
        context = self.context
        regObject = addContentToContainer(context, registration)
        attObject = addContentToContainer(regObject, attendee,
                                          checkConstraints=False)
        regObject.title = attObject.title
        event = ObjectCreatedEvent(regObject)
        notify(event)
        self.immediate_view = "%s/%s" % (context.absolute_url(), regObject.id)


class GroupAddForm(form.SchemaAddForm):
    grok.context(IRegistrations)
    grok.require('apyb.conference.AddRegistration')

    label = _(u"Register")
    description = _(u"Register to this conference")

    template = ViewPageTemplateFile('templates/register.pt')

    schema = IGroupForm

    enable_form_tabbing = False
    registration_type = u''

    def update(self):
        super(GroupAddForm, self).update()
        self.request['disable_plone.leftcolumn'] = 1
        self.request['disable_plone.rightcolumn'] = 1
        groups = self.groups
        attendees_group = groups[1]
        attendees_group.widgets['attendees'].allow_insert = True
        attendees_group.widgets['attendees'].allow_delete = True

    def updateWidgets(self):
        groups = self.groups
        att_group = groups[1]
        att_group.fields['attendees'].widgetFactory = DataGridFieldFactory
        super(GroupAddForm, self).updateWidgets()

    def create(self, data):
        ''' Create objects '''
        reg_fields = ['discount_code']
        data['registration_type'] = self.registration_type

        reg_data = dict([(k, data[k]) for k in reg_fields])
        reg_data['email'] = data['email']
        reg_data['city'] = data['city']
        reg_data['state'] = data['state']
        reg_data['country'] = data['country']
        reg_data['registration_type'] = data['registration_type']
        registration = createContent('registration',
                                     checkConstraints=True, **reg_data)

        for k in reg_fields:
            del data[k]
        base_attendee = data.copy()
        del base_attendee['attendees']
        del base_attendee['email']
        attendees = []
        if not data['attendees']:
            form = self.request.form
            base_fname = 'form.widgets.attendees.%s.widgets.%s'
            ftype = 'AA'
            fname = base_fname % (ftype, 'fullname')
            if not fname in form:
                ftype = 'TT'
                fname = base_fname % (ftype, 'fullname')
                if not fname in form:
                    ftype = '00'
                    fname = base_fname % (ftype, 'fullname')
                    if not fname in form:
                        # Will raise an error in add..
                        return None
            line = {'fullname':
                    form[base_fname % (ftype, 'fullname')],
                    'gender':
                    form[base_fname % (ftype, 'gender')][0],
                    't_shirt_size':
                    form[base_fname % (ftype, 't_shirt_size')][0],
                    'email':
                    form[base_fname % (ftype, 'email')],
                    'caipirinha':
                    form[base_fname % (ftype, 'caipirinha')][0],
                    'wall':
                    form[base_fname % (ftype, 'wall')][0],
                    }
            data['attendees'].append(line)

        for line in data['attendees']:
            line.update(base_attendee)
            # Create attendee object
            attendee = createContent('attendee',
                                     checkConstraints=True, **line)
            attendees.append(attendee)
        return [registration, attendees]

    def add(self, object):
        registration, attendees = object
        context = self.context
        regObject = addContentToContainer(context, registration)
        regObject.title = attendees[0].organization
        for attendee in attendees:
            addContentToContainer(regObject, attendee, checkConstraints=False)
        event = ObjectCreatedEvent(regObject)
        notify(event)
        self.immediate_view = "%s/%s" % (context.absolute_url(), regObject.id)


class APyBRegistrationForm(AddForm):
    grok.name('registration-apyb')

    label = _(u"APyB Member Registration")
    registration_type = u'apyb'

    schema = IAPyBRegistration


class StudentRegistrationForm(AddForm):
    grok.name('registration-student')

    label = _(u"Student registration")
    registration_type = u'student'


class IndividualRegistrationForm(AddForm):
    grok.name('registration-individual')

    label = _(u"Individual registration")
    registration_type = u'individual'


class SpeakerRegistrationForm(AddForm):
    grok.name('registration-speaker')

    label = _(u"Speaker registration")
    registration_type = u'speaker'


class GroupRegistrationForm(GroupAddForm):
    grok.name('registration-group')

    label = _(u"Group / Corporate registration")
    registration_type = u'group'


class StudentsRegistrationForm(GroupAddForm):
    grok.name('registration-students')

    label = _(u"Group registration for students")
    registration_type = u'student'


class GovernmentRegistrationForm(GroupAddForm):
    grok.name('registration-gov')

    label = _(u"Government registration")
    registration_type = u'government'


class SponsorsRegistrationForm(GroupAddForm):
    grok.name('registration-sponsor')
    grok.require('cmf.ManagePortal')

    label = _(u"Group registration for sponsors")
    registration_type = u'sponsor'


class OrganizerRegistrationForm(GroupAddForm):
    grok.name('registration-organizer')
    grok.require('cmf.ManagePortal')

    label = _(u"Organizers registration")
    registration_type = u'organizer'


@form.default_value(field=IAddress['country'], form=AddForm)
@form.default_value(field=IAddress['country'], form=GroupAddForm)
def default_country_registration(data):
    country = u'br'
    return country


@form.default_value(field=IIndividualForm['email'])
@form.default_value(field=IGroupForm['email'])
def default_email_registration(data):
    state = getMultiAdapter((data.context, data.request),
                            name=u'plone_portal_state')
    member = state.member()
    return member.getProperty('email')


@form.default_value(field=IIndividualForm['fullname'])
@form.default_value(field=IGroupForm['organization'])
def default_fullname_registration(data):
    state = getMultiAdapter((data.context, data.request),
                            name=u'plone_portal_state')
    member = state.member()
    return member.getProperty('fullname')
