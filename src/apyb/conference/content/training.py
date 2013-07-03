# -*- coding:utf-8 -*-
from five import grok
from zope import schema
from apyb.conference import MessageFactory as _
from plone.directives import form
from plone.directives import dexterity


class ITraining(form.Schema):
    """
    A training in a conference
    """

    duration = schema.Choice(
        title=_(u'Duration'),
        description=_(u''),
        required=True,
        vocabulary='apyb.conference.duration',
    )

    language_talk = schema.Choice(
        title=_(u"Language"),
        required=True,
        description=_(u"Language of your training."),
        vocabulary='apyb.conference.languages',
    )

    infrastructure_requirements = schema.Text(
        title=_(u"Training requirements"),
        required=False,
        description=_(u"Which software do the student must have installed on her/his own computer?"),
    )

    global_theme = schema.Choice(
        title=_(u"Global theme"),
        required=True,
        description=_(u"What is the subject of your training?"),
        vocabulary='apyb.conference.theme',
    )

    level = schema.Choice(
        title=_(u"Level"),
        required=True,
        description=_(u"Level of your training."),
        vocabulary='apyb.conference.levels',
    )

    observations = schema.Text(
        title=_(u"Observations"),
        required=False,
        description=_(u"Do you want to give us another information?"),
    )


class Training(dexterity.Item):
    grok.implements(ITraining)
