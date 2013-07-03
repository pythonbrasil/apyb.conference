# -*- coding:utf-8 -*-
from apyb.conference import MessageFactory as _
from apyb.conference.utils import context_property
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.directives import form
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides


class INetContactInfo(form.Schema):
    """
       Marker/Form interface for an Internet set of contact information
    """

    email = schema.TextLine(
        title=_(u'E-mail'),
        description=_(u'Please provide an email address'),
        required=False,
    )

    twitter = schema.TextLine(
        title=_(u'Twitter'),
        description=_(u'Please provide your Twitter name, if you have one.'),
        required=False,
    )

    irc_nickname = schema.TextLine(
        title=_(u'IRC Nickname'),
        description=_(u'Please provide your IRC nickname, if you have one.'),
        required=False,
    )

    site = schema.URI(
        title=_(u'Site'),
        description=_(u'Please provide the address of your site, blog \
                        or profile'),
        required=False,
    )


alsoProvides(INetContactInfo, IFormFieldProvider)


class NetContactInfo(object):
    """ Factory to store data in attributes
    """
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    email = context_property('email')
    twitter = context_property('twitter')
    irc_nickname = context_property('irc_nickname')
    site = context_property('site')


class IPhoneContactInfo(form.Schema):
    """
       Marker/Form interface for a set of telephone contact information
    """

    phone = schema.TextLine(
        title=_(u'Phone'),
        description=_(u'Please provide a telephone number where you \
                        can be reached.'),
        required=False,
    )

    mobile = schema.TextLine(
        title=_(u'Mobile'),
        description=_(u'Please provide your mobile phone number.'),
        required=False,
    )


alsoProvides(IPhoneContactInfo, IFormFieldProvider)


class PhoneContactInfo(object):
    """ Factory to store data in attributes
    """
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    phone = context_property('phone')
    mobile = context_property('mobile')
