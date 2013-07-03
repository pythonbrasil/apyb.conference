# -*- coding:utf-8 -*-
from apyb.conference import MessageFactory as _
from five import grok
from plone.app.textfield import RichText
from plone.directives import dexterity
from plone.directives import form
from plone.indexer.decorator import indexer
from plone.namedfile.field import NamedBlobImage
from zope import schema


def has_image(sponsor):
    image = sponsor.image
    return (image and image.getSize())


class ISponsor(form.Schema):
    """ A Sponsor
    """

    level = schema.Choice(
        title=_(u'Sponsorship Level'),
        description=_(u'Which sponsorship package this sponsor acquired.'),
        required=True,
        vocabulary="apyb.conference.sponsor_levels",
    )

    text = RichText(
        title=_(u'Text'),
        description=_(u'A detailed text about this sponsor.'),
        required=False,
    )

    remoteUrl = schema.TextLine(
        title=_(u'Site'),
        description=_(u'Sponsor site.'),
        required=False,
    )

    twitter = schema.TextLine(
        title=_(u'Twitter'),
        description=_(u'''Inform the sponsor's Twitter account.'''),
        required=False,
    )

    image = NamedBlobImage(
        title=_(u"Logo"),
        description=_(u"Sponsor logo."),
        required=False,
    )


class Sponsor(dexterity.Item):
    """ A Sponsor
    """
    grok.implements(ISponsor)

    def image_thumb(self):
        ''' Return a thumbnail '''
        if not has_image(self):
            return None
        view = self.unrestrictedTraverse('@@images')
        return view.scale(fieldname='image',
                          scale='thumb').index_html()

    def tag(self, scale='thumb', css_class='tileImage', **kw):
        ''' Return a tag to the image '''
        if not (has_image(self)):
            return ''
        view = self.unrestrictedTraverse('@@images')
        return view.tag(fieldname='image',
                        scale=scale,
                        css_class=css_class,
                        **kw)


@indexer(ISponsor)
def SearchableText(obj):
    text = obj.text.output if obj.text else ''
    return ' '.join((obj.id, obj.title,
                     obj.description, text, obj.remoteUrl))


@indexer(ISponsor)
def getRemoteUrl(obj):
    return obj.remoteUrl


class View(dexterity.DisplayForm):
    grok.context(ISponsor)
    grok.require('zope2.View')
    grok.name('view')

    def image(self):
        context = self.context
        if not (has_image(context)):
            return ''
        scale = 'preview'
        return context.tag(scale=scale)
