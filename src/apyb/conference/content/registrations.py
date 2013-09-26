# -*- coding:utf-8 -*-
from Acquisition import aq_inner
from apyb.conference import MessageFactory as _
from apyb.conference.config import REVIEW_STATE
from apyb.conference.utils import fmt_price
from DateTime import DateTime
from five import grok
from plone.directives import dexterity, form
from zope.component import getMultiAdapter, queryUtility
from zope.schema.interfaces import IVocabularyFactory
from persistent.dict import PersistentDict
from plone.app.uuid.utils import uuidToObject


class IRegistrations(form.Schema):
    """
    Folderish content that contains registrations
    """
    pass


class Registrations(dexterity.Container):
    grok.implements(IRegistrations)


class View(grok.View):
    grok.context(IRegistrations)
    grok.require('zope2.View')

    def update(self):
        context = aq_inner(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request),
                                     name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request),
                                     name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request),
                                      name=u'plone_portal_state')
        self._ct = self.tools.catalog()
        self.is_anonymous = self.portal.anonymous()
        self.mt = self.tools.membership()
        if not self.show_border:
            self.request['disable_border'] = True

    @property
    def vocabs(self):
        if not hasattr(self, "_vocabs"):
            vocabs = {}
            vocabs['gender'] = queryUtility(IVocabularyFactory,
                                            'apyb.conference.gender')
            vocabs['tshirt'] = queryUtility(IVocabularyFactory,
                                            'apyb.conference.tshirt')
            vocabs['types'] = queryUtility(IVocabularyFactory,
                                           'apyb.conference.types')
            vocabs['payment'] = queryUtility(IVocabularyFactory,
                                             'apyb.conference.paymentservices')
            vocabs['country'] = queryUtility(IVocabularyFactory,
                                             'contact.countries')
            self._vocabs = dict((key, value(self))
                                for key, value in vocabs.items())
        return self._vocabs

    @property
    def login_url(self):
        return '%s/login' % self.portal.portal_url()

    @property
    def register_url(self):
        return '%s/@@register' % self.portal.portal_url()

    @property
    def registrations_enabled(self):
        mt = self.mt
        state = self.state.workflow_state()
        # If opened, its enabled
        if state == 'opened':
            return True
        return mt.checkPermission('apyb.conference: Add Registration',
                                  self.context)

    def registration_options(self):
        base = self.context.absolute_url()
        options = [
            {'type': 'apyb',
             'href': '%s/@@registration-apyb' % base,
             'text': _(u'Register as an APyB Member'), },
            {'type': 'student',
             'href': '%s/@@registration-student' % base,
             'text': _(u'Register as a student'), },
            {'type': 'individual',
             'href': '%s/@@registration-individual' % base,
             'text': _(u'Register as an Individual'), },
            {'type': 'group',
             'href': '%s/@@registration-group' % base,
             'text': _(u'Register members of a group or organization '
                       u'(Group registration)'), },
            {'type': 'government',
             'href': '%s/@@registration-gov' % base,
             'text': _(u'Register member(s) of Brazilian Government'), }, ]
        return options

    @property
    def show_border(self):
        ''' Is this user allowed to edit this content '''
        return self.state.is_editable()

    @property
    def listing_enabled(self):
        ''' Is this user allowed to view registration listings '''
        return self.show_border

    def _regs_as_dict(self, registrations):
        ''' Given a list of brains, we return proper dictionaries '''
        voc = self.vocabs
        att_by_reg = self.attendees_by_registration()
        regs = []
        for brain in registrations:
            reg = {}
            reg['id'] = brain.getId
            reg['url'] = brain.getURL()
            reg['email'] = brain.email
            reg['date'] = DateTime(brain.created).strftime('%Y-%m-%d %H:%M')
            reg['title'] = brain.Title
            reg['type'] = voc['types'].getTerm(brain.Subject[0]).title
            reg['num_attendees'] = brain.num_attendees
            reg['price_est'] = fmt_price(brain.price_est)
            reg['amount'] = fmt_price(brain.amount)
            attendees = att_by_reg.get(brain.getId, [])
            caipirinha = sum([int(att['caipirinha']) for att in attendees])
            reg['caipirinha'] = caipirinha
            wall = sum([int(att['wall'])
                        for att in attendees
                        if att['wall'].isdigit()])
            reg['wall'] = wall
            reg['state'] = REVIEW_STATE.get(brain.review_state,
                                            brain.review_state)
            regs.append(reg)
        return regs

    def _att_as_dict(self, attendees):
        ''' Given a list of brains, we return proper dictionaries '''
        voc = self.vocabs
        atts = []
        for brain in attendees:
            att = {}
            att['id'] = brain.getId
            att['reg'] = brain.getPath().split('/')[-2]
            att['reg_url'] = '/'.join(brain.getURL().split('/')[:-1])
            att['url'] = brain.getURL()
            att['date'] = DateTime(brain.created).strftime('%Y-%m-%d %H:%M')
            att['fullname'] = brain.Title
            att_type = voc['types'].getTerm(
                brain.Subject[0]).title if brain.Subject else ''
            att['type'] = att_type
            att['email'] = brain.email
            caipirinha = brain.caipirinha
            if caipirinha.startswith('yes'):
                caipirinha = int(caipirinha[-1])
            else:
                caipirinha = 0
            att['caipirinha'] = caipirinha
            att['wall'] = brain.wall
            att['badge_name'] = brain.badge_name or att['fullname']
            att['gender'] = voc['gender'].getTerm(brain.gender).title
            att['t_shirt_size'] = voc['tshirt'].getTerm(
                brain.t_shirt_size).title
            att['state'] = REVIEW_STATE.get(brain.review_state,
                                            brain.review_state)
            atts.append(att)
        return atts

    def registrations(self):
        ''' List registrations'''
        ct = self._ct
        results = ct.searchResults(portal_type='registration',
                                   sort_on='created',
                                   sort_order='reverse',
                                   path=self._path)
        return self._regs_as_dict(results)

    def registrations_by_type(self):
        ''' List registrations by type '''
        registrations = self.registrations()
        reg_by_type = {}
        for reg in registrations:
            reg_type = reg['type']
            reg_state = reg['state']
            if not reg_type in reg_by_type:
                reg_by_type[reg_type] = {}
            if not reg_state in reg_by_type[reg_type]:
                reg_by_type[reg_type][reg_state] = []
            reg_by_type[reg_type][reg_state].append(reg)
        return reg_by_type

    def member_registrations(self):
        ''' List registrations made by authenticated member'''
        user = self.context.portal_membership.getAuthenticatedMember().getUserName()
        ct = self._ct
        brains = ct.searchResults(portal_type='registration',
                                  Creator=user)
        regs = [r.getObject() for r in brains]
        return [dict(
            href=reg.absolute_url(),
            text=_('Registration for [%s] made in [%s]') % (reg.title, reg.created())) for reg in regs]

    def attendees(self):
        ''' List attenddees'''
        ct = self._ct
        results = ct.searchResults(portal_type='attendee',
                                   sort_on='created',
                                   sort_order='reverse',
                                   path=self._path)
        return self._att_as_dict(results)

    def attendees_by_registration(self):
        ''' List attendees by Registration '''
        attendees = self.attendees()
        att_by_reg = {}
        for att in attendees:
            att_reg = att['reg']
            if not att_reg in att_by_reg:
                att_by_reg[att_reg] = []
            att_by_reg[att_reg].append(att)
        return att_by_reg

    def attendees_by_type(self):
        ''' List attendees by type '''
        attendees = self.attendees()
        att_by_type = {}
        for att in attendees:
            att_type = att['type']
            if not att_type in att_by_type:
                att_by_type[att_type] = []
            att_by_type[att_type].append(att)
        return att_by_type

    def attendees_by_state(self):
        ''' List attendees by state '''
        attendees = self.attendees()
        att_by_state = {}
        for att in attendees:
            att_state = att['state']
            if not att_state in att_by_state:
                att_by_state[att_state] = []
            att_by_state[att_state].append(att)
        return att_by_state


class AttendeesView(View):
    grok.context(IRegistrations)
    grok.name('attendees_view')
    grok.require('cmf.ReviewPortalContent')

    def update(self):
        super(AttendeesView, self).update()
        self.request['disable_plone.leftcolumn'] = 1
        self.request['disable_plone.rightcolumn'] = 1


class AttendeesCSVView(View):
    grok.name('attendees-csv')

    template = None

    def update(self):
        super(AttendeesCSVView, self).update()
        self.normalizeString = self.context.plone_utils.normalizeString

    def _att_as_dict(self, attendees):
        ''' Given a list of brains, we return proper dictionaries '''
        voc = self.vocabs
        atts = []
        for brain in attendees:
            reg_type = raw_type = ''
            if brain.Subject:
                reg_type = brain.Subject[0]
                raw_type = reg_type
                if reg_type == 'speaker_c':
                    reg_type = u'Palestrante'
                elif reg_type == 'organizer':
                    reg_type = u'Organização'
                else:
                    reg_type = u'Participante'
            att = {}
            att['id'] = brain.getId
            att['uid'] = brain.UID
            att['reg'] = brain.getPath().split('/')[-2]
            att['reg_url'] = '/'.join(brain.getURL().split('/')[:-1])
            att['url'] = brain.getURL()
            att['date'] = DateTime(brain.created).strftime('%Y-%m-%d %H:%M')
            att['fullname'] = brain.Title
            att['type'] = reg_type
            att['raw_type'] = raw_type
            att['email'] = brain.email
            att['badge_name'] = brain.badge_name or att['fullname']
            att['gender'] = voc['gender'].getTerm(brain.gender).title
            att['t_shirt_size'] = voc['tshirt'].getTerm(
                brain.t_shirt_size).title
            att['rev_state'] = REVIEW_STATE.get(brain.review_state,
                                                brain.review_state)
            att['organization'] = brain.organization
            att['lat'] = brain.latitude
            att['long'] = brain.longitude
            att['city'] = brain.city
            att['state'] = brain.state
            att['country'] = brain.country
            atts.append(att)
        return atts

    def render(self):
        self.request.response.setHeader('Content-Type',
                                        'text/plain;charset=utf-8')
        data = []
        data.append('initial;cod;state;type;raw_type;fullname;'
                    'badge_name;gender;t_shirt_size;email;organization;'
                    'lat;lgn;city;state;country')
        ct = self._ct
        results = ct.searchResults(portal_type='attendee',
                                   sort_on='created',
                                   sort_order='reverse',
                                   path=self._path)
        for att in self._att_as_dict(results):
            line = []
            initial = self.normalizeString(att['fullname'][0])
            line.append('"%s"' % initial)
            line.append('"%s"' % str(att['uid']))
            line.append('"%s"' % str(att['rev_state']))
            line.append('"%s"' % str(att['type']))
            line.append('"%s"' % str(att['raw_type']))
            line.append('"%s"' % str(att['fullname']).strip())
            line.append('"%s"' % str(att['badge_name']).strip())
            line.append('"%s"' % str(att['gender']))
            line.append('"%s"' % str(att['t_shirt_size']))
            line.append('"%s"' % str(att['email']))
            line.append('"%s"' % str(att['organization']))
            line.append('"%s"' % str(att['lat']))
            line.append('"%s"' % str(att['long']))
            line.append('"%s"' % str(att['city']))
            line.append('"%s"' % str(att['state']))
            line.append('"%s"' % str(att['country']))
            data.append(';'.join(line))
        return '\n'.join(data)


class RegistrationsView(View):
    grok.context(IRegistrations)
    grok.name('registrations_view')
    grok.require('cmf.ReviewPortalContent')

    def update(self):
        super(RegistrationsView, self).update()
        self.request['disable_plone.leftcolumn'] = 1
        self.request['disable_plone.rightcolumn'] = 1


class RegDetailedView(View):
    grok.context(IRegistrations)
    grok.name('registrations_detailed')
    grok.require('cmf.ReviewPortalContent')

    def update(self):
        super(RegDetailedView, self).update()
        self.request['disable_plone.leftcolumn'] = 1
        self.request['disable_plone.rightcolumn'] = 1

    def registrations(self, state='confirmed'):
        ''' List registrations'''
        ct = self._ct
        results = ct.searchResults(portal_type='registration',
                                   sort_on='created',
                                   sort_order='reverse',
                                   review_state=state,
                                   path=self._path)
        regs = []
        for brain in results:
            regObj = brain.getObject()
            reg = {}
            reg['id'] = brain.getId
            reg['url'] = brain.getURL()
            reg['email'] = brain.email
            reg['date'] = DateTime(brain.created).strftime('%Y/%m/%d')
            reg['title'] = brain.Title
            reg['type'] = brain.Subject[0]
            reg['num_attendees'] = brain.num_attendees
            reg['price_est'] = brain.price_est
            reg['amount'] = brain.amount or '0000'
            caipirinha = brain.caipirinha
            if caipirinha.startswith('yes'):
                caipirinha = int(caipirinha[-1])
            else:
                caipirinha = 0
            reg['caipirinha'] = caipirinha
            reg['wall'] = brain.wall
            reg['state'] = brain.review_state
            reg['paid'] = getattr(regObj, 'paid', False)
            reg['service'] = getattr(regObj, 'service', '----')
            reg['discount_code'] = regObj.discount_code
            regs.append(reg)
        return regs

    def pending(self):
        return self.registrations(state='pending')


class ManagePagSeguroView(grok.View):
    grok.context(IRegistrations)
    grok.name('registrations_pagseguro')
    grok.require('cmf.ReviewPortalContent')

    def update(self):
        context = aq_inner(self.context)
        self.payment = 'pagseguro'
        self._path = '/'.join(context.getPhysicalPath())
        self.state = self._multi_adapter(u'plone_context_state')
        self.tools = self._multi_adapter(u'plone_tools')
        self.portal = self._multi_adapter(u'plone_portal_state')
        self._ct = self.tools.catalog()
        self._wt = self.tools.workflow()
        self.mt = self.tools.membership()
        self.updated = []
        pfile = self.request.get('pfile', '')
        if pfile:
            items = self.process_file(pfile)
            self.update_registrations(items)

    def _multi_adapter(self, name):
        return getMultiAdapter((self.context, self.request), name=name)

    def fix_value(self, value):
        ''' Convert string from PagSeguro to an int representing cents '''
        # If there is a thousands separator, kill it
        # Remove also negative sign
        value = value.replace('.', '').replace('-', '')
        return int(value.replace(',', '')[:-2])

    def process_file(self, pfile=None):
        ''' Try to process a txt file exported by PagSeguro '''
        if not pfile:
            return []
        data = pfile.read()
        lines = data.split('\n')
        lines = [l.split('\t') for l in lines]
        header = lines[0]
        items = [dict(zip(header, l)) for l in lines[1:] if len(l) > 1]
        return items

    def update_registrations(self, items):
        ''' Given a list of dictionaries, we transition registrations
            as needed
        '''
        context = self.context
        oIds = context.objectIds()
        for item in items:
            oId = item.get('Ref_Transacao', '')
            status = item.get('Status', '')
            if (not oId in oIds) or (not status == 'Aprovada'):
                continue
            reg = context[oId]
            if getattr(reg, 'paid', False):
                continue
            reg.amount = self.fix_value(item.get('Valor_Bruto', '00,000'))
            reg.paid = True
            reg.service = self.payment
            self._wt.doActionFor(reg, 'confirm')
            self.updated.append(reg.id)


class ManagePayPalView(grok.View):
    grok.context(IRegistrations)
    grok.name('registrations_paypal')
    grok.require('cmf.ReviewPortalContent')

    def update(self):
        context = aq_inner(self.context)
        self.payment = 'paypal'
        self._path = '/'.join(context.getPhysicalPath())
        self.state = self._multi_adapter(u'plone_context_state')
        self.tools = self._multi_adapter(u'plone_tools')
        self.portal = self._multi_adapter(u'plone_portal_state')
        self._ct = self.tools.catalog()
        self._wt = self.tools.workflow()
        self.mt = self.tools.membership()
        self.updated = []
        self.not_updated_problems = []
        pfile = self.request.get('pfile', '')
        if pfile:
            items = self.process_file(pfile)
            self.update_registrations(items)

    def _multi_adapter(self, name):
        return getMultiAdapter((self.context, self.request), name=name)

    def fix_value(self, value):
        ''' Convert string from PayPal to an int representing cents '''
        return int(value.replace(',', '').replace('.', '').replace('-', ''))

    def process_file(self, pfile=None):
        ''' Try to process a txt file exported by PagSeguro '''
        if not pfile:
            return []
        data = pfile.read()
        lines = data.replace('"', '')
        lines = lines.split('\n')
        lines = [l.split('\t') for l in lines]
        header = ['Data', 'Hora', 'TZ', 'Nome', 'Tipo', 'Status', 'Moeda',
                  'Bruto', 'Taxa', 'Liquido', 'From', 'To', 'Id_Transacao',
                  'Status_equivalente', 'Status_endereco', 'Título_item',
                  'ID_item', 'Valor_envio_manuseio', 'Valor_seguro',
                  'Imposto_vendas', 'Opcao_1_nome', 'Opcao_1_valor',
                  'Opcao_2_nome', 'Opcao_2_valor', 'Site_leilao',
                  'ID_comprador', 'URL_do_item', 'Data_termino',
                  'ID_escritura', 'ID_fatura', 'ID_txn_ref', 'Num_fatura',
                  'Num_personalizado', 'ID_recibo', 'End_lin1',
                  'End_lin2', 'Cidade', 'UF', 'CEP', 'Pais', 'Tel', ]
        items = [dict(zip(header, l)) for l in lines[1:] if len(l) > 1]
        return items

    def update_registrations(self, items):
        ''' Given a list of dictionaries, we transition registrations
            as needed
        '''
        context = self.context
        oIds = context.objectIds()
        for item in items:
            # the first payment has sequential number == 0
            # it's ID is either in the format '<oid>' (for backward compatibility) or '<oid>::0'
            oId, seq = item.get('ID_item', ''), 0
            # extra payments have ID's in the format '<oid>::<seq>', seq = 1,2,...
            if '::' in oId:
                oId, seq = oId.split('::')
                seq = int(seq)
            if (not oId in oIds):
                continue
            reg = context[oId]
            if seq in reg.payments:
                # this payment was already processed
                continue
            # this is a new payment
            service = self.payment
            amount = self.fix_value(item.get('Bruto', '0,00'))
            net_amount = self.fix_value(item.get('Liquido', '0,00'))
            fee = self.fix_value(item.get('Taxa', '0,00'))
            success = reg.confirm_payment(seq, service, amount, net_amount, fee)
            if success:
                workflow_state = getMultiAdapter((reg, self.request), name=u'plone_context_state').workflow_state()
                if workflow_state != 'confirmed':
                    self._wt.doActionFor(reg, 'confirm')
                self.updated.append(reg.id)
            else:
                self.not_updated_problems.append(reg.id)


class APyBView(grok.View):
    grok.context(IRegistrations)
    grok.name('apyb-member')
    grok.require('zope2.View')


class SeatTableView(View):
    "Makes a registration FREE. Use with caution"
    # TODO: improve the output of this, with a template or turn this into a csv view

    grok.name('seat-table')
    grok.context(IRegistrations)
    grok.require('cmf.ManagePortal')

    template = None

    def render(self):
        self.request.response.setHeader('Content-Type',
                                        'text/plain;charset=utf-8')
        out = "TRAINING NAME\tTRAINING TITLE\tPERSON\tPAID?\n"
        register = self.context
        for training_uid, people in register.seat_table.iteritems():
            training = uuidToObject(training_uid)
            for p in people:
                reg_uid, attendee_id = p.split('/')
                reg = register[reg_uid]
                paid = False
                for payment in reg.payments.values():
                    items, _ = payment['items']
                    for item in items:
                        if 'training_uid' in item:
                            if (attendee_id, training_uid) == (item['attendee'], item['training_uid']):
                                paid = True
                out += "%s\t%s\t%s\t%s\n" % (training.absolute_url(),
                                             training.title,
                                             register.absolute_url() + '/' +p,
                                             paid)
        return out


class HackConfirmPayedView(View):
    # XXX HACK: REMOVE ME SOMEDAY

    grok.name('hack-confirm')
    grok.context(IRegistrations)
    grok.require('cmf.ManagePortal')

    template = None

    def update(self):
        from zope.component import getMultiAdapter

        tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')
        _wt = tools.workflow()

        self.out = ''
        register = self.context
        for reg in register.getChildNodes():
            state = getMultiAdapter((reg, self.request), name=u'plone_context_state').workflow_state()
            if reg.has_payments() and state != 'confirmed':
                _wt.doActionFor(reg, 'confirm')
                self.out += '%s >>>> inscricao confirmada\n' % reg

    def render(self):
        return '################################################################\n' + self.out


class PaymentsView(View):
    "Show all payments made"

    grok.name('payments')
    grok.context(IRegistrations)
    grok.require('cmf.ManagePortal')

    template = None

    def render(self):
        self.request.response.setHeader('Content-Type', 'text/csv;charset=utf-8')
        self.request.response.setHeader('Content-disposition', 'attachment; filename=payments.csv')

        self.out = ''
        def printline(*args):
            self.out += '\t'.join(map(str, args)) + '\n'

        printline('NAME', 'EMAIL', 'LINK', 'ITEM', 'VALUE')

        register = self.context
        for reg in register.getChildNodes():
            if reg.payments:
                name = reg.title
                email = reg.email
                # atts = ', '.join(['%s <%s>' % (a.title, a.email) for a in reg.getChildNodes()])
                link = reg.absolute_url()
                for n, pay in reg.payments.iteritems():
                    items, total = pay['items']
                    for item in items:
                        # note that we remove "R$" from the start of fmtPrice
                        item_name, fmt_frice = item['item'], item['fmtPrice'][2:]
                        printline(name, email, link, item_name, fmt_frice)

        return self.out

