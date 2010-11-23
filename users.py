# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Taverne Sylvain <taverne.sylvain@gmail.com>
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
from itools.gettext import MSG
from itools.csv import Table as BaseTable
from itools.datatypes import Email, Boolean

# Import from ikaaro
from ikaaro.registry import register_resource_class
from ikaaro.table import Table
from ikaaro.forms import SelectWidget, TextWidget, BooleanRadio

# Import from newsletter
from datatypes import Languages_Enumerate
from utils_views import SearchTable_View


class Users(BaseTable):

    record_properties = {
      'mail': Email(mandatory=True, is_indexed=True, unique=True),
      'exist': Boolean(is_indexed=True),
      'language': Languages_Enumerate(is_indexed=True),
      }


class MailingUsersView(SearchTable_View):

    access = 'is_admin'
    search_schema = {'mail': Email,
                     'exist': Boolean,
                     'language': Languages_Enumerate}

    search_widgets = [TextWidget('mail', title=MSG(u'Email')),
                      BooleanRadio('exist', title=MSG(u'User exist ?')),
                      SelectWidget('language', title=MSG(u'Language'))]


class MailingUsers(Table):

    class_id = 'MailingUsers'
    class_title = MSG(u'Mailing Users')
    class_handler = Users
    class_views = ['view', 'add_record']


    form = [TextWidget('mail', title=MSG(u'E-Mail Address')),
            BooleanRadio('exist', title=MSG(u'User exist')),
            SelectWidget('language', title=MSG(u'Language'))]

    # Views
    view = MailingUsersView()

    ######################################
    ## API to subscribe or unsubscribe
    ######################################

    def get_user_exist(self, email):
        return len(self.handler.search(mail=email))>0


    def set_user_exist(self, context, email):
        results = self.handler.search(mail=email)
        if results:
            kw = {'exist': True}
            self.update_record(results[0].id, **kw)
            context.commit = True


    def subscribe(self, email):
        self.add_new_record({'mail': email, 'exist': False})


    def unsubscribe(self, email):
        results = self.handler.search(mail=email)
        if len(results)==0:
            return False
        self.handler.del_record(results[0].id)
        return True


register_resource_class(MailingUsers)
