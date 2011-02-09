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

# Import from itools
from itools.core import merge_dicts
from itools.csv import Property
from itools.datatypes import String
from itools.gettext import MSG
from itools.stl import set_prefix
from itools.web import STLForm

# Import from ikaaro
from ikaaro.autoform import ImageSelectorWidget
from ikaaro.views_new import NewInstance
from ikaaro.registry import get_resource_class
from ikaaro import messages



class MailingLetterNewInstance(NewInstance):

    widgets = NewInstance.widgets + [ImageSelectorWidget('banner',
              title=MSG(u'You can choose a banner'))]
    schema = merge_dicts(NewInstance.schema, banner=String)


    def action(self, resource, context, form):
        name = form['name']
        title = form['title']
        banner = form['banner']

        # Create the resource
        class_id = context.query['type']
        cls = get_resource_class(class_id)
        child = resource.make_resource(name, cls, title=title, banner=banner)

        # The metadata
        language = resource.get_edit_languages(context)[0]
        title = Property(title, lang=language)
        child.metadata.set_property('title', title)

        # Ok
        goto = './%s/' % name
        return context.come_back(messages.MSG_NEW_RESOURCE, goto=goto)



class MailingLetterView(STLForm):

    template = '/ui/mailing/MailingLetter_view.xml'
    access = 'is_allowed_to_add'
    title = MSG(u'View')

    def get_namespace(self, resource, context):

        # nb_users
        number = resource.get_property('number')
        if number:
            nb_users = MSG(u'Sent to {nb} E-Mails')
            nb_users = nb_users.gettext(nb=number)
        else:
            nb_users =  MSG(u'There are {nb} E-Mails in Database')
            nb_users = nb_users.gettext(
                                nb=resource.parent.get_subscripters_nb())

        # The data XXX handle the language
        html_resource = resource.get_resource('html_body')
        prefix = resource.get_pathto(html_resource)
        html_data = html_resource.get_html_data()
        html_data = set_prefix(html_data, '%s/' % prefix)
        txt_data = resource.get_resource('txt_body').to_text()

        return {'subject': resource.get_title(),
                'is_sent': resource.get_property('is_sent'),
                'nb_users': nb_users,
                'html_data': html_data,
                'txt_data': txt_data}


    def action(self, resource, context, form):
        # Sender OK ?
        sender = resource.parent.get_property('sender')
        if not sender:
            context.message = MSG(u'Please configure the sender !')
            return

        resource.send(context)
        msg = MSG(u'Newsletter sent !')

