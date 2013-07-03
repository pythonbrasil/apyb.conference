# -*- coding:utf-8 -*-
from apyb.conference import MessageFactory as _
from apyb.conference.utils import context_property
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.directives import form
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides


class IAddress(form.Schema):
    """Marker/Form interface for Address behavior
    """
    address = schema.TextLine(
        title=_(u'Address'),
        required=False,
    )

    city = schema.TextLine(
        title=_(u'City'),
        required=True,
    )

    state = schema.TextLine(
        title=_(u'State'),
        required=False,
    )

    postcode = schema.TextLine(
        title=_(u'Post Code / Zip Code'),
        required=False,
    )

    country = schema.Choice(
        title=_(u'Country'),
        required=True,
        vocabulary='contact.countries',
    )


alsoProvides(IAddress, IFormFieldProvider)


class Address(object):
    """ Factory to store data in attributes
    """
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    address = context_property('address')
    city = context_property('city')
    state = context_property('state')
    postcode = context_property('postcode')
    country = context_property('country')
