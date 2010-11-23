# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Sylvain Taverne <sylvain@itaapy.com>
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
from itools.datatypes import Email
from itools.gettext import MSG
from itools.web import ERROR
from itools.xapian import PhraseQuery

# Import from ikaaro
from ikaaro import messages
from ikaaro.buttons import RemoveButton
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.forms import AutoForm, TextWidget

# Import from newsletter
from letter import MailingLetter


class Mailing_Configure(AutoForm):

    access = 'is_admin'

    title = MSG(u'Configure')

    widgets = [
        TextWidget('sender', title=MSG(u'Email sender')),
        ]

    schema = {
        'sender': Email(mandatory=True),
    }


    def get_value(self, resource, context, name, datatype):
        return resource.get_property(name)


    def action(self, resource, context, form):
        # Save configuration
        for key in ['sender']:
            resource.set_property(key, form[key])
        # Come back
        return context.come_back(messages.MSG_CHANGES_SAVED, goto='./')


class MailingView(Folder_BrowseContent):

    access = 'is_admin'
    title = MSG(u'View')

    search_template = None

    # Table
    table_columns = [
        ('name', MSG(u'Name')),
        ('title', MSG(u'Title')),
        ('mtime', MSG(u'Date')),
        ('state', MSG(u'State'))]

    table_actions = [RemoveButton]

    batch_msg1 = MSG(u"There is 1 one newsletter")
    batch_msg2 = MSG(u"There are {n} newsletters")


    def get_items(self, resource, context, *args):
        args = PhraseQuery('format', MailingLetter.class_id)
        return Folder_BrowseContent.get_items(self, resource, context, args)


    def get_item_value(self, resource, context, item, column):
        item_brain, item_resource = item
        if column=='name':
            uri = '%s/;view' % resource.get_pathto(item_resource)
            return (item_resource.name, uri)
        elif column=='title':
            return item_resource.get_property('title')
        elif column=='subject':
            return item_resource.get_property('subject')
        elif column=='state':
            uri = '%s/;view' % resource.get_pathto(item_resource)
            return (MSG(u'Click to send'), uri)
        return Folder_BrowseContent.get_item_value(self, resource, context, item, column)




class Mailing_Register(AutoForm):

    access = True

    title = MSG(u'Register')

    widgets = [
        TextWidget('email', title=MSG(u'Your E-mail address')),
        ]

    schema = {
        'email': Email(mandatory=True),
    }



    def action(self, resource, context, form):
        email = form['email']
        # Check if user exist
        users = resource.get_resource('users')
        if users.get_user_exist(email):
            context.message = ERROR(u'User already exist')
            return
        # Subscribe
        users.subscribe(email)
        # Come back
        context.message =MSG(u'Inscription ok')



class Mailing_Unregister(Mailing_Register):

    access = True

    title = MSG(u'Unsubscribe')

    def action(self, resource, context, form):
        email = form['email']
        # Check if user exist
        users = resource.get_resource('users')
        # Unsubscribe
        if(users.unsubscribe(email)):
            msg = MSG(u'Unregistration ok')
        else:
            msg = ERROR(u'The E-mail address not exist')
        # Come back
        return context.come_back(msg, goto='./')
