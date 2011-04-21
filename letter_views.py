# -*- coding: utf-8 -*-
# Copyright (C) 2007 Taverne Sylvain <taverne.sylvain@gmail.com>
# Copyright (C) 2010-2011 David Versmisse <david.versmisse@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from standard library
import re

# Import from itools
from itools.core import merge_dicts
from itools.csv import Property
from itools.datatypes import String, XMLContent
from itools.gettext import MSG
from itools.stl import stl
from itools.web import ERROR, STLForm
from itools.xml import XMLParser

# Import from ikaaro
from ikaaro.autoform import ImageSelectorWidget, TextWidget
from ikaaro.datatypes import Unicode
from ikaaro.views_new import NewInstance
from ikaaro.registry import get_resource_class
from ikaaro import messages



class MailingLetterNewInstance(NewInstance):

    schema = merge_dicts(NewInstance.schema,
        email_subject=Unicode(mandatory=True),
        banner=String)
    widgets = NewInstance.widgets + [
        TextWidget('email_subject', title=MSG(u'Email subject')),
        ImageSelectorWidget('banner', title=MSG(u'You can choose a banner'))]


    def action(self, resource, context, form):
        # Get the container
        root = resource.get_root()
        container = form['container']
        # Make the resource
        class_id = context.query['type']
        cls = get_resource_class(class_id)
        # Banner relative to here
        prefix = container.get_pathto(resource)
        banner = prefix.resolve2(form['banner'])
        child = container.make_resource(form['name'], cls)

        # Set properties
        language = container.get_edit_languages(context)[0]
        for key in ['title', 'email_subject']:
            value = Property(form[key], lang=language)
            child.metadata.set_property(key, value)

        # Build HTML template
        if banner:
            banner = resource.get_resource(banner)
            banner = context.get_link(banner)
        namespace = {'page_uri': './;download',
                     'banner': banner,
                     'title': form['email_subject']}
        template = root.get_resource('/ui/mailing/LetterTemplate.xml')
        handler = child.get_handler(language=language)
        handler.set_changed()
        handler.events = list(stl(template, namespace))
        # Build Text template
        txt = MSG(u'Type your text email here').gettext(language=language)
        value = Property(txt, lang=language)
        child.metadata.set_property('email_text', value)
        # Ok
        goto = str(resource.get_pathto(child))
        return context.come_back(messages.MSG_NEW_RESOURCE, goto=goto)



class MailingLetterView(STLForm):

    template = '/ui/mailing/MailingLetter_view.xml'
    access = 'is_allowed_to_add'
    title = MSG(u'View')

    def get_namespace(self, resource, context):
        # Render txt version as webmail
        txt_data = resource.get_email_text(context)
        txt_data = XMLContent.encode(txt_data)
        txt_data = re.sub(r'(\A|\s)(http://(\w|\.|/|:|;|\?|=|%|&|-)+)',
                          r'\1<a href="\2" target="_blank"> \2</a>', txt_data)
        txt_data = XMLParser(txt_data.replace('\n', '<br/>'))
        # Return namespace
        return {'title': resource.get_title(),
                'email_subject': resource.get_email_subject(context),
                'spool_size': context.server.get_spool_size(),
                'nb_users': resource.parent.get_subscripters_nb(),
                'is_sent': resource.get_property('is_sent'),
                'number': resource.get_property('number'),
                'txt_data': txt_data}


    def action(self, resource, context, form):
        # Sender OK ?
        sender = resource.parent.get_property('sender')
        if not sender:
            context.message = ERROR(u'Please configure the sender !')
            return
        # All object must be public
        links = []
        for link in resource.get_links():
            link_resource = context.root.get_resource(link)
            if link_resource.get_statename() != 'public':
                links.append(
                    {'href': context.get_link(link_resource),
                     'title': link_resource.get_title()})
        if links:
            context.message = ERROR(u"""
                Error, some resources used on newsletter are not public:<br/>
                <stl:block stl:repeat="link links">
                  <a href="${link/href}">${link/title}</a>
                  <stl:inline stl:if="not repeat/link/end">,</stl:inline>
                </stl:block>
                <br/>Please fix it and resend the newsletter.
                """, format='stl', links=links)
            return
        # Send the newsletter
        resource.send(context)
        context.message = MSG(u'Newsletter sent !')
