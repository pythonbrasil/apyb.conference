# -*- coding:utf-8 -*-
from apyb.conference.content.registration import IRegistration
from five import grok
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFCore.utils import getToolByName


@grok.subscribe(IRegistration, IActionSucceededEvent)
def update_attendees(folder, event):
    ''' Set correct state to attendees under this object
    '''
    wt = getToolByName(folder, 'portal_workflow')
    objects = folder.objectValues()
    # Confirm or cancel
    if event.action in ['confirm', 'cancel']:
        transition = event.action
    else:
        return None
    for obj in objects:
        wt.doActionFor(obj, transition)
