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
from itools.web import STLForm

# Import from ikaaro
from ikaaro.autoform import ImageSelectorWidget
from ikaaro.views_new import NewInstance
from ikaaro.registry import get_resource_class
from ikaaro import messages



class MailingLetterNewInstance(NewInstance):

    schema = merge_dicts(NewInstance.schema, banner=String)
    widgets = NewInstance.widgets + [ImageSelectorWidget('banner',
              title=MSG(u'You can choose a banner'))]


    def action(self, resource, context, form):
        # Get the container
        container = form['container']
        # Make the resource
        class_id = context.query['type']
        cls = get_resource_class(class_id)
        # Banner relative to here
        prefix = container.get_pathto(resource)
        banner = prefix.resolve2(form['banner'])
        child = container.make_resource(form['name'], cls, banner=banner,
                title=form['title'])
        # Set properties
        language = container.get_edit_languages(context)[0]
        title = Property(form['title'], lang=language)
        child.metadata.set_property('title', title)
        # Ok
        goto = str(resource.get_pathto(child))
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
        mail = resource.get_resource('mail')
        txt_data = mail.get_property('email_text')

        return {'subject': resource.get_title(),
                'is_sent': resource.get_property('is_sent'),
                'nb_users': nb_users,
                'link_to_html': context.get_link(mail),
                'txt_data': txt_data}


    def action(self, resource, context, form):
        # Sender OK ?
        sender = resource.parent.get_property('sender')
        if not sender:
            context.message = MSG(u'Please configure the sender !')
            return

        resource.send(context)
        context.message = MSG(u'Newsletter sent !')

