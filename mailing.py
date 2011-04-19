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
from itools.datatypes import Email, Tokens
from itools.gettext import MSG

# import from ikaaro
from ikaaro.cc import Observable
from ikaaro.folder import Folder
from ikaaro.folder_views import Folder_NewResource
from ikaaro.registry import register_document_type

# Import from Newsletter
from letter import MailingLetter
from mailing_views import Mailing_View, Mailing_Edit
from mailing_views import Mailing_SubscribeForm



class Mailing(Folder, Observable):

    class_id = 'mailing'
    class_title = MSG(u'E-Mailing')
    class_description = MSG(u'Manage Newsletters')
    class_icon16 = 'icons/16x16/mail.png'
    class_icon48 = 'icons/48x48/mail.png'
    class_schema = merge_dicts(Folder.class_schema,
                               Observable.class_schema,
                               sender=Email(source='metadata'),
                               grey_list=Tokens(source='metadata'))

    class_views = ['view', 'new_resource?type=mailing-letter',
                   'edit', 'subscribe']

    # Views
    view = Mailing_View()
    edit = Mailing_Edit()
    subscribe = Mailing_SubscribeForm()
    new_resource = Folder_NewResource(title=MSG(u'Add a newsletter'))


    def get_document_types(self):
        return [MailingLetter]


    def get_subscripters_nb(self):
        users = self.get_property('cc_list')
        return len(users)


    def after_register(self, username):
        grey_list = set(self.get_property('grey_list'))
        grey_list.discard(username)
        self.set_property('grey_list', tuple(grey_list))

        return super(Mailing, self).after_register(username)


    def after_unregister(self, username):
        grey_list = set(self.get_property('grey_list'))
        grey_list.add(username)
        self.set_property('grey_list', tuple(grey_list))

        return super(Mailing, self).after_unregister(username)


    def is_subscription_allowed(self, username):
        grey_list = self.get_property('grey_list')
        if username in grey_list:
            return False

        return super(Mailing, self).is_subscription_allowed(username)



# Register
register_document_type(Mailing)
