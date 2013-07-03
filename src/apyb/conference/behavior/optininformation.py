# -*- coding:utf-8 -*-
from apyb.conference import MessageFactory as _
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides


class IOptInInformation(form.Schema):
    """
      Marker/Form interface for OptIn information
    """
    conference = schema.Bool(
        title=_(u'Accept to be contacted by conference organizers'),
        default=True,
        required=False,
    )

    partners = schema.Bool(
        title=_(u'Accept to be contacted by conference partners'),
        default=True,
        required=False,
    )

alsoProvides(IOptInInformation, IFormFieldProvider)
