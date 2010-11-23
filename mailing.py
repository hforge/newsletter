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

# Import from ikaaro
from ikaaro.registry import register_resource_class
from ikaaro.folder import Folder
from ikaaro.folder_views import GoToSpecificDocument

# Import from itools
from itools.core import merge_dicts
from itools.gettext import MSG
from itools.web import BaseView
from itools.datatypes import Email, String

# Import from here
from users import MailingUsers
from letter import MailingLetter
from mailing_views import MailingView, Mailing_Configure
from mailing_views import Mailing_Register, Mailing_Unregister
from models import Models


class Mailing_Logo(BaseView):

    class_id = 'mailing-logo'
    access = True

    query_schema = {'id': String,
                    'mail': Email}

    def GET(self, resource, context):
        id = context.query['id']
        email = context.query['mail']
        # Inform that user exist
        users = resource.get_resource('users')
        users.set_user_exist(context, email)
        # Inform that newsletter has been open by user
        #newsletter = resource.get_resource(id)
        #newsletter.user_has_open(context, email)
        return context.uri.resolve('/ui/icons/16x16/action_home.png')


class Mailing(Folder):

    class_id = 'mailing'
    class_title = MSG(u'E-Mailing')

    class_views = [
                   #'register', 'unregister',
                   'view',
                   'configure',
                   'users',
                   'models']

    __fixed_handlers__ = ['users', 'models']


    # Views
    view = MailingView()
    configure = Mailing_Configure()
    logo = Mailing_Logo()
    users = GoToSpecificDocument(specific_document='users',
                                 title=MSG(u'Users'),
                                 access='is_admin')
    models = GoToSpecificDocument(specific_document='models',
                                  title=MSG(u'Models'),
                                 access='is_admin')

    register = Mailing_Register()
    unregister = Mailing_Unregister()

    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(Folder.get_metadata_schema(),
                           sender=Email)


    @staticmethod
    def _make_resource(cls, folder, name):
        Folder._make_resource(cls, folder, name)
        # Users
        kw = {'title': {'en': u"Registered users",
                        'fr': u'Utilisateurs enregistrés'}}
        MailingUsers._make_resource(MailingUsers, folder, '%s/users' % name, **kw)
        # Models
        kw = {'title': {'en': u'Newsletter Models',
                        'fr': u'Modéles de newsletter'}}
        Models._make_resource(Models, folder, '%s/models' % name, **kw)


    def get_document_types(self):
        return [MailingLetter]



register_resource_class(Mailing)
