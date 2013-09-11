# -*- coding:utf-8 -*-
from Acquisition import aq_inner, aq_parent
from apyb.conference import MessageFactory as _
from apyb.conference.utils import generateId
from five import grok
from plone.directives import dexterity, form
from plone.indexer import indexer
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getMultiAdapter, queryUtility
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from persistent.dict import PersistentDict
from apyb.conference.behavior.allocation import IAllocation
from apyb.conference.content.attendee import IAttendee
from apyb.conference.config import PRICES
from plone.uuid.interfaces import IUUID


class IRegistration(form.Schema):
    """
    A registration in a conference
    """
    form.omitted('uid')
    uid = schema.Int(
        title=_(u"uid"),
        required=False,
    )

    email = schema.TextLine(
        title=_(u'E-mail'),
        description=_(u'Please provide an email address'),
        required=True,
    )

    registration_type = schema.Choice(
        title=_(u'Type'),
        description=_(u'Select the category of your registration'),
        required=True,
        vocabulary="apyb.conference.types",
    )

    discount_code = schema.TextLine(
        title=_(u'Discount code'),
        description=_(u'If you have a discount code, please inform here'),
        required=False,
        missing_value=u'',
    )


@indexer(IRegistration)
def num_attendees(obj):
    children = obj.objectValues()
    children = [c for c in children
                if c.portal_type == 'attendee']
    return len(children)
grok.global_adapter(num_attendees, name="num_attendees")


@indexer(IRegistration)
def price_est(obj):
    if not getattr(obj, 'paid', False):
        children = obj.objectValues()
        children = [c for c in children
                    if c.portal_type == 'attendee']

        view = aq_parent(obj).restrictedTraverse('@@reg-price')
        qty = len(children)
        caipirinha = '|'.join([c.caipirinha for c in children])
        wall = '|'.join([c.wall for c in children])

        registration_type = obj.registration_type
        discount_code = obj.discount_code
        price = view.price(registration_type, qty,
                           discount_code,
                           caipirinha=caipirinha,
                           wall=wall)
    else:
        price = obj.amount
    return price

grok.global_adapter(price_est, name="price_est")


@indexer(IRegistration)
def registration_type(obj):
    return [obj.registration_type, ]
grok.global_adapter(registration_type, name="Subject")


class Registration(dexterity.Container):
    grok.implements(IRegistration)

    def __init__(self, id=None, **kwargs):
        if not id:
            id = generateId()
        super(Registration, self).__init__(id=id, **kwargs)

    @property
    def uid(self):
        intids = getUtility(IIntIds)
        return intids.getId(self)

    def UID(self):
        return self.uid

    @property
    def payments(self):
        if not hasattr(self, '_payments'):
            self._payments = PersistentDict()
        return self._payments

    def has_payments(self):
        return hasattr(self, '_payments') and self._payments

    def get_payments_total(self, field):
        return sum([p[field] for p in self.payments.values()])

    @property
    def service(self):
        if self.has_payments():
            # the service of the first payment
            return self.payments[0]['service']

    # paypal properity
    # XXX maybe this should be removed, but I do not know which parts of the system rely on this
    @property
    def amount(self):
        return self.get_payments_total('amount')

    # paypal properity
    # XXX maybe this should be removed, but I do not know which parts of the system rely on this
    @property
    def net_amount(self):
        return self.get_payments_total('net_amount')

    # paypal properity
    # XXX maybe this should be removed, but I do not know which parts of the system rely on this
    @property
    def fee(self):
        return self.get_payments_total('fee')

    def confirm_payment(self, seq, service, amount, net_amount, fee):
        try:
            pending, _ = self.pending_payments_HACK
        except AttributeError:
            # TODO: remove this shameful hack and this bizarre POG exception handling
            raise Exception("""
        ################
        UMA **POG** FALHOU, PARA CORRIGIR ESSE PROBLEMA APENAS VISITE A PAGINA
        -- %s -- E DEPOIS IMPORTE O ARQUIVO NOVAMENTE. ################""" % self.absolute_url())

        total = sum([p['price'] for p in pending])
        if total != amount:
            return False
        else:
            self.payments[seq] = PersistentDict(items = self.pending_payments_HACK,
                                                service = service,
                                                amount = amount,
                                                net_amount = net_amount,
                                                fee = fee,)
            return True


class View(grok.View):
    grok.context(IRegistration)
    grok.require('zope2.View')

    def update(self):
        super(View, self).update()
        context = aq_inner(self.context)
        registrations = aq_parent(self.context)
        self.registration_type = context.registration_type
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request),
                                     name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request),
                                     name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request),
                                      name=u'plone_portal_state')
        self.helper = getMultiAdapter((registrations, self.request),
                                      name=u'helper')
        self._ct = self.tools.catalog()
        self._mt = self.tools.membership()
        self.member = self.portal.member()
        self.price_view = registrations.restrictedTraverse('@@reg-price')
        # Vocabs
        self.voc = self._vocab('apyb.conference.types')
        self.caipirinha = self._vocab('apyb.conference.caipirinha')
        self.wall = self._vocab('apyb.conference.wall')

        self.roles_context = self.member.getRolesInContext(context)
        url = context.absolute_url()
        self.training_form = '%s/@@registration-training' % url
        self.show_border = [r for r in self.roles_context
                            if r in ['Manager', 'Editor', 'Reviewer', ]]
        self.request['disable_border'] = self.show_border

    def _vocab(self, name):
        factory = queryUtility(IVocabularyFactory, name)
        return factory(self.context)

    def attendees(self):
        ct = self._ct
        path = self._path
        attendees = []
        results = ct.searchResults(portal_type='attendee',
                                   path=path)
        for brain in results:
            attendees.append({
                'Title': brain.Title,
                'organization': brain.organization,
                'email': brain.email,
                'caipirinha': brain.caipirinha,
                'wall': brain.wall,
                'url': brain.getURL,
            })
        return attendees

    def attendee(self, attendee_uid):
        ct = self._ct
        results = ct.searchResults(UID=attendee_uid)
        if results:
            brain = results[0]
            return brain.getObject()

    @property
    def creator(self):
        creator = self.context.Creator()
        data = []
        if isinstance(creator, str):
            creator = [creator, ]
        for member_id in creator:
            member = self._mt.getMemberById(member_id)
            if member:
                member_fullname = member.getProperty('fullname') or member_id
                member_email = member.getProperty('email') or member_id
                member = '%s <%s>' % (member_fullname, member_email)
            else:
                member = member_id
            data.append(member)
        return ', '.join(data)

    @property
    def created(self):
        created = self.context.creation_date
        return created.strftime('%d/%m/%Y %H:%M')

    @property
    def fmt_registration_type(self):
        registration_type = self.registration_type
        term = self.voc.getTerm(registration_type)
        return term.title

    def show_payments(self):
        return self.pending_payments_total()

    @property
    def paid(self):
        is_paid = getattr(self.context, 'paid', False)
        return is_paid

    def formatPrice(self, value):
        return self.price_view.fmtPrice(value)

    @property
    def price_paid(self):
        view = self.price_view
        try:
            amount = self.context.amount
        except:
            amount = 0
        fmtPrice = view.fmtPrice(amount)
        return fmtPrice

    @property
    def payment_details(self):
        view = self.price_view
        fmtPrice = view.fmtPrice
        for n, p in sorted(self.context.payments.items()):
            details = {
                'amount': fmtPrice(p['amount']),
                'net_amount': fmtPrice(p['net_amount']),
                'fee': fmtPrice(p['fee']),
                'service': p['service'],
                'items': p['items'][0],
            }
            yield details

    @property
    def payment_totals(self):
        view = self.price_view
        fmtPrice = view.fmtPrice
        details = {
            'amount': fmtPrice(self.context.get_payments_total('amount')),
            'net_amount': fmtPrice(self.context.get_payments_total('net_amount')),
            'fee': fmtPrice(self.context.get_payments_total('fee')),
        }
        return details

    @property
    def show_empenho(self):
        ''' show only if registration type == government'''
        return self.registration_type == 'government'

    @property
    def show_pagseguro(self):
        ''' show only if registration not paid and
            registration is from brazil
        '''
        #country = self.context.country
        #paid = self.paid
        #return (country == u'br' and not (paid or self.show_empenho))
        return False

    @property
    def show_paypal(self):
        ''' show only if registration not paid
        '''
        return self.pending_payments_total() and not self.show_empenho

    def _price(self):
        view = self.price_view
        attendees = self.attendees()
        qty = len(attendees)
        caipirinha = '|'.join([str(c.get('caipirinha', ''))
                              for c in attendees])
        wall = '|'.join([str(c.get('wall', '')) for c in attendees])
        registration_type = self.registration_type
        discount_code = self.context.discount_code
        price = view.price(registration_type, qty, discount_code,
                           caipirinha=caipirinha, wall=wall)
        fmtPrice = view.fmtPrice(price)
        return (price, fmtPrice)

    @property
    def base_price(self):
        attendees = self.attendees()
        qty = len(attendees) or 1
        price = self._price()[0]
        return price / qty

    @property
    def price(self):
        return self._price()[0]

    @property
    def fmtBasePrice(self):
        return self.price_view.fmtPrice(self.base_price)

    @property
    def fmtPrice(self):
        return self._price()[1]

    def available_trainings(self):
        ''' List of available trainings '''
        helper = self.helper
        return helper.trainings()

    # TODO memoize???
    def pending_payments(self):
        pending = []
        # basic conference registration
        if not self.context.has_payments():
            # if no payment was made then the conf registration is pending
            pending.append({'item': 'Conference Registration',
                            'price': self.price,
                            'fmtPrice': self.fmtPrice})
        # trainings
        def training_price(t):
            allocation = IAllocation(t)
            duration = int(allocation.duration.split()[0])
            # base price is for a 4h training, we adjust proportionally
            price = PRICES['training']*duration/4
            if self.registration_type == 'government':
                # government pays double for trainings
                price = price * 2
            elif self.registration_type in ['apyb', 'student']:
                # apyb and student pays half
                price = price / 2
            return price
        attendees = [a for a in self.context.getChildNodes()
                     if IAttendee.providedBy(a)]
        for a in attendees:
            for t in a.pending_trainings():
                duration = IAllocation(t).duration
                title = 'Training for [%s]: %s (%s)' % (a.title,
                                                        t.title,
                                                        duration)
                price = training_price(t)
                pending.append({'item': title,
                                'price': price,
                                'fmtPrice': self.formatPrice(price),
                                'attendee': a.id,
                                'training_uid': IUUID(t)})

        total = self.formatPrice(sum([p['price'] for p in pending]))

        # TODO we should move the property to Registration and call it from there (in the ManagePayPalView) (and not store this)
        self.context.pending_payments_HACK = pending, total

        return pending, total

    def pending_payments_total(self):
        pending, _ = self.pending_payments()
        return sum([p['price'] for p in pending])

    @property
    def pending_payments_item_number(self):
        # next payment item number for use by Paypal
        seq = len(self.context.payments)
        assert seq not in self.context.payments
        return "%s::%s" % (self.context.id, seq)

