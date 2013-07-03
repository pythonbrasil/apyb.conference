# -*- coding:utf-8 -*-
from five import grok
from zope import schema
from apyb.conference import MessageFactory as _
from plone.directives import form
from plone.directives import dexterity


class ITalk(form.Schema):
    """
    A talk in a conference
    """

    language_talk = schema.Choice(
        title=_(u"Language"),
        required=True,
        description=_(u"Language of your talk."),
        vocabulary='apyb.conference.languages',
    )

    global_theme = schema.Choice(
        title=_(u"Global theme"),
        required=True,
        description=_(u"What is the subject of your talk?"),
        vocabulary='apyb.conference.theme',
    )

    level = schema.Choice(
        title=_(u"Level"),
        required=True,
        description=_(u"Level of your talk."),
        vocabulary='apyb.conference.levels',
    )

    observations = schema.Text(
        title=_(u"Observations"),
        required=False,
        description=_(u"Do you want to give us another information?"),
    )


class Talk(dexterity.Item):
    grok.implements(ITalk)
