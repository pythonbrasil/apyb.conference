import json
import urllib2

from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite


def check_apyb_membership(email):
    # XXX refactor the proxy config to run only once

    # If your site is behind a proxy,
    # you must configure a 'http_proxy' property for it
    # in "portal_properties/site_properties"
    portal_properties = getToolByName(getSite(), 'portal_properties')
    site_properties = portal_properties['site_properties']
    http_proxy = site_properties.getProperty('http_proxy')
    if http_proxy:
        proxy = urllib2.ProxyHandler({'http': http_proxy})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)

    response = json.load(urllib2.urlopen("http://associados.python.org.br/members/status/?email=%s" % email))
    return response['status']

