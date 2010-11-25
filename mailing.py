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
from itools.gettext import MSG

# import from ikaaro
from ikaaro.folder import Folder
from ikaaro.registry import register_document_type

# Import from Newsletter
from mailing_views import MailingView
from letter import MailingLetter
from models import Models



class Mailing(Folder):

    class_id = 'mailing'
    class_title = MSG(u'E-Mailing')
    class_description = MSG(u'Manage Newsletters')
    class_icon16 = 'icons/16x16/mail.png'
    class_icon48 = 'icons/48x48/mail.png'

    class_views = ['view']
    # XXX
    #               #'register', 'unregister',
    #               'view',
    #               'configure',
    #               'users',
    #               'models']
    view = MailingView()


    def init_resource(self, **kw):
        Folder.init_resource(self, **kw)

        # XXX Users
        #kw = {'title': {'en': u"Registered users",
        #                'fr': u'Utilisateurs enregistrés'}}
        #MailingUsers._make_resource(MailingUsers, folder, '%s/users' % name, **kw)
        # Models
        kw = {'title': {'en': u'Newsletter Models',
                        'fr': u'Modèles de newsletter'}}
        self.make_resource('models', Models, **kw)


    def get_document_types(self):
        return [MailingLetter]



# Register
register_document_type(Mailing)
