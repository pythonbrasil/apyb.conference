# -*- coding:utf-8 -*-
from apyb.conference.config import PROJECTNAME
from plone.app.upgrade.utils import loadMigrationProfile

import logging


def apply_profile(context):
    ''' Uodate to version 2000 '''
    logger = logging.getLogger(PROJECTNAME)
    profile = 'profile-apyb.conference.upgrades.v2000:default'
    loadMigrationProfile(context, profile)
    logger.info('Updated to version 2000')
