# -*- coding: utf-8 -*-
from apyb.conference import MessageFactory as _
from apyb.conference.config import SPONSOR_LEVELS
from five import grok
from plone.i18n.locales.countries import _countrylist
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


class DurationVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        levels = [('half_day', _(u'Half day')),
                  ('one_day', _(u'1 day')),
                  ('two_days', _(u'2 days'))]
        for code, text in levels:
            term = (code, code, text)
            terms.append(SimpleVocabulary.createTerm(*term))

        return SimpleVocabulary(terms)


grok.global_utility(DurationVocabulary,
                    name=u"apyb.conference.duration")


class LanguagesVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        levels = [('english', _(u'English')),
                  ('portuguese', _(u'Portuguese')),
                  ('spanish', _(u'Spanish'))]
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
                 ('pagseguro', _(u'Pagseguro'))]
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
        types = [('no', _(u'No, I will not attend')),
                 ('yes_1', _(u'Yes, I will')),
                 ('yes_2', _(u'Yes and I will bring my SO')),
                 ('yes_3', _(u'Yes, plus 2 other people'))]
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
