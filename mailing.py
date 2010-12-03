# -*- coding: utf-8 -*-
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
from itools.core import merge_dicts
from itools.datatypes import Email, Tokens
from itools.gettext import MSG

# import from ikaaro
from ikaaro.cc import Observable
from ikaaro.folder import Folder
from ikaaro.registry import register_document_type
from ikaaro.folder_views import GoToSpecificDocument

# Import from Newsletter
from letter import MailingLetter
from mailing_views import MailingView, MailingEdit
from models import Models



class Mailing(Folder, Observable):

    class_id = 'mailing'
    class_title = MSG(u'E-Mailing')
    class_description = MSG(u'Manage Newsletters')
    class_icon16 = 'icons/16x16/mail.png'
    class_icon48 = 'icons/48x48/mail.png'
    class_schema = merge_dicts(Folder.class_schema,
                               sender=Email(source='metadata'),
                               cc_list=Tokens(source='metadata'))
    __fixed_handlers__ = ['models']

    class_views = ['view', 'edit', 'subscribe', 'models']

    view = MailingView()
    edit = MailingEdit()
    models = GoToSpecificDocument(specific_document='models',
                                  title=MSG(u'Models'),
                                  access='is_allowed_to_edit')


    def init_resource(self, **kw):
        Folder.init_resource(self, **kw)

        # Models
        kw = {'title': {'en': u'Models',
                        'fr': u'Modèles'}}
        self.make_resource('models', Models, **kw)


    def get_document_types(self):
        return [MailingLetter]



# Register
register_document_type(Mailing)
