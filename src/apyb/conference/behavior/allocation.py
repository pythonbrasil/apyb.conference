# -*- coding:utf-8 -*-
from apyb.conference import MessageFactory as _
from apyb.conference.utils import context_property
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.directives import dexterity
from plone.directives import form
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides


class IAllocation(form.Schema):
    """Marker/Form interface for Allocation behavior
    """

    dexterity.read_permission(location='zope2.View')
    dexterity.write_permission(location='cmf.ModifyPortalContent')
    duration = schema.Choice(
        title=_(u"Duration"),
        required=False,
        description=_(u"Duration of this activity"),
        vocabulary='apyb.conference.duration',
    )

    form.fieldset(
        'allocation',
        label=_(u"Training Allocation"),
        fields=['seats', 'startDate', 'endDate', 'location'],
    )

    dexterity.read_permission(location='zope2.View')
    dexterity.write_permission(location='apyb.conference.AllocateTalk')
    location = schema.Choice(
        title=_(u"Location"),
        required=False,
        description=_(u"Room where this activity will be presented"),
        vocabulary='apyb.conference.rooms',
    )

    dexterity.read_permission(seats='zope2.View')
    dexterity.write_permission(seats='apyb.conference.AllocateTalk')
    seats = schema.Int(
        title=_(u"Seats"),
        description=_(u"Available seats to this activity."),
        default=1,
        required=False,
    )

    dexterity.read_permission(startDate='zope2.View')
    dexterity.write_permission(startDate='apyb.conference.AllocateTalk')
    startDate = schema.Datetime(
        title=_(u"Start date"),
        required=False,
        description=_(u"Activity start date"),
    )

    dexterity.read_permission(endDate='zope2.View')
    dexterity.write_permission(endDate='apyb.conference.AllocateTalk')
    endDate = schema.Datetime(
        title=_(u"End date"),
        required=False,
        description=_(u"Activity end date"),
    )


alsoProvides(IAllocation, IFormFieldProvider)


class Allocation(object):
    """ Factory to store data in attributes
    """
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    location = context_property('location')
    duration = context_property('duration')
    seats = context_property('seats')
    startDate = context_property('startDate')
    endDate = context_property('endDate')
