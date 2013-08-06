# -*- coding: utf-8 -*-
from apyb.conference import MessageFactory as _
from apyb.conference.config import SPONSOR_LEVELS
from five import grok
from plone.i18n.locales.countries import _countrylist
from Products.CMFCore.utils import getToolByName
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class PeriodsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        levels = [('morning', _(u'Morning')),
                  ('afternon', _(u'Afternon'))]
        for code, text in levels:
            term = (code, code, text)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(PeriodsVocabulary,
                    name=u"apyb.conference.periods")


class LanguagesVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        levels = [('en', _(u'English')),
                  ('pt-br', _(u'Portuguese')),
                  ('es', _(u'Spanish'))]
        for code, text in levels:
            term = (code, code, text)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(LanguagesVocabulary,
                    name=u"apyb.conference.languages")


class ThemeVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        levels = [('cloud_system_administration_networks',
                   _(u'Cloud, System Administration and Networks')),
                  ('community_education', _(u'Community and Education')),
                  ('django', _(u'Django')),
                  ('enterprise_management', _(u'Enterprise and Management')),
                  ('media_networks', _(u'Media and Networks')),
                  ('mobility_embedded_systems',
                   _(u'Mobility and Embedded Systems')),
                  ('plone', _(u'Plone')),
                  ('pyramid', _(u'Pyramid')),
                  ('scipy', _(u'Scipy')),
                  ('web_wevelopment', _(u'Web Development')),
                  ('other', _(u'Other'))]
        for code, text in levels:
            term = (code, code, text)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(ThemeVocabulary,
                    name=u"apyb.conference.theme")


class LevelsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Look for an enclosing program
            list available languages in it '''
        terms = []
        levels = [('basic', _(u'Basic')),
                  ('advanced', _(u'Advanced'))]
        for code, text in levels:
            term = (code, code, text)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(LevelsVocabulary,
                    name=u"apyb.conference.levels")


class GendersVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Genders '''
        terms = []
        genders = [('m', _(u'Male')),
                   ('f', _(u'Female'))]
        for key, value in genders:
            term = (key, key, value)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(GendersVocabulary,
                    name=u"apyb.conference.gender")


class TShirtVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' TShirt Sizes '''
        terms = []
        sizes = [('S', _(u'Small')),
                 ('M', _(u'Medium')),
                 ('L', _(u'Large')),
                 ('X', _(u'X-Large'))]
        for key, value in sizes:
            term = (key, key, value)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(TShirtVocabulary,
                    name=u"apyb.conference.tshirt")


class RegTypesVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Registration Types'''
        terms = []
        types = [('apyb', _(u'APyB Members')),
                 ('student', _(u'Student')),
                 ('individual', _(u'Individual')),
                 ('government', _(u'Government')),
                 ('group', _(u'Group/Corporate')),
                 ('speaker', _(u'Speaker')),
                 ('speaker_c', _(u'Speaker')),
                 ('sponsor', _(u'Sponsor')),
                 ('organizer', _(u'Organization'))]
        for key, value in types:
            term = (key, key, value)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(RegTypesVocabulary,
                    name=u"apyb.conference.types")


class TrainingsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        trainings = []
        for key, value in trainings:
            term = (key, key, value)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(TrainingsVocabulary,
                    name=u"apyb.conference.trainings")


class PaymentMethodsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Payment Method Options '''
        terms = []
        types = [('cash', _(u'Cash / At the conference')),
                 ('paypal', _(u'PayPal')),
                 ('pagseguro', _(u'PagSeguro'))]
        for key, value in types:
            term = (key, key, value)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(PaymentMethodsVocabulary,
                    name=u"apyb.conference.paymentservices")


class CaipirinhaSprintVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Caipirinha Sprint Options'''
        terms = []
        types = [('no', _(u'No! I will not attend.')),
                 ('yes_1', _(u'Yes! Book me a place (R$350,00)')),
                 ('yes_2', _(u'Yes! Book me 2 places (R$700,00)')),
                 ('yes_3', _(u'Yes! Book me 3 places (R$800,00)'))]
        for key, value in types:
            term = (key, key, value)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(CaipirinhaSprintVocabulary,
                    name=u"apyb.conference.caipirinha")


class WallOptionsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Wall Options '''
        terms = []
        types = [('no', _(u'No, thanks')),
                 ('100', _(u'Yes, I support with R$100,00')),
                 ('200', _(u'Yes, I support with R$200,00')),
                 ('400', _(u'Yes, I support with R$400,00'))]
        for key, value in types:
            term = (key, key, value)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(WallOptionsVocabulary,
                    name=u"apyb.conference.wall")


class SponsorLevelsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Wall Options '''
        terms = []
        types = SPONSOR_LEVELS
        for key, value in types:
            term = (key, key, value)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(SponsorLevelsVocabulary,
                    name=u"apyb.conference.sponsor_levels")


class CountriesVocabulary(object):
    """Vocabulary factory for a list of countries
    """
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        countries = [(v['name'], k) for k, v in _countrylist.items()]
        countries.sort()
        items = [SimpleTerm(k, k, v) for v, k in countries]
        return SimpleVocabulary(items)

grok.global_utility(CountriesVocabulary, name=u"contact.countries")


class TalksReferenceTypeVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Talk Reference Types Options '''
        terms = []
        types = [('article', _(u'Article / Post')),
                 ('presentation', _(u'Presentation')),
                 ('video', _(u'Video'))]
        for key, value in types:
            term = (key, key, value)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(TalksReferenceTypeVocabulary,
                    name=u"apyb.conference.talk.referencetype")


class TalksTypeVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Talk Types Options '''
        terms = []
        types = [('talk', _(u'Talk')),
                 ('panel', _(u'Panel'))]
        for key, value in types:
            term = (key, key, value)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(TalksTypeVocabulary,
                    name=u"apyb.conference.talk.type")


class TracksVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Tracks Vocabulary '''
        ct = getToolByName(context, 'portal_catalog')
        tracks = ct.searchResults(portal_type='track',
                                  sort_on='getObjPositionInParent')
        items = [SimpleTerm(b.UID, b.UID, b.Title) for b in tracks]
        return SimpleVocabulary(items)


grok.global_utility(TracksVocabulary,
                    name=u"apyb.conference.talk.tracks")


class TalksLevelVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Talk Types Options '''
        terms = []
        types = [('basic', _(u'Basic')),
                 ('intermediate', _(u'Intermediate')),
                 ('advanced', _(u'Advanced'))]
        for key, value in types:
            term = (key, key, value)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(TalksLevelVocabulary,
                    name=u"apyb.conference.talk.level")


class RoomsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Conference rooms Options '''
        terms = []
        rooms = [
            ('dorneles-tremea', _(u'Dorneles Treméa Auditorium')),
            ('cleese', _(u'John Cleese Room')),
            ('idle', _(u'Eric Idle Room')),
            ('gillian', _(u'Terry Gilliam Room')),
        ]
        for key, value in rooms:
            term = (key, key, value)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(RoomsVocabulary,
                    name=u"apyb.conference.rooms")


class SpeakersVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Speakers Vocabulary '''
        ct = getToolByName(context, 'portal_catalog')
        speakers = ct.searchResults(portal_type='speaker',
                                    sort_on='getObjPositionInParent')
        items = [SimpleTerm(b.UID, b.UID, b.Title) for b in speakers]
        return SimpleVocabulary(items)


grok.global_utility(TracksVocabulary,
                    name=u"apyb.conference.speakers")


class DurationVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        ''' Activity duration '''
        terms = []
        durations = [
            ('30 min.', _(u'30 Minutes')),
            ('45 min.', _(u'45 Minutes')),
            ('60 min.', _(u'60 Minutes')),
            ('4 hours', _(u'4 Hours')),
            ('8 hours', _(u'8 Hours')),
            ('16 hours', _(u'16 Hours')),
        ]
        for key, value in durations:
            term = (key, key, value)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(DurationVocabulary,
                    name=u"apyb.conference.duration")
