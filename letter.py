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
from itools.core import merge_dicts
from itools.datatypes import Boolean, Integer, Email, String

# import from ikaaro
from ikaaro.folder import Folder
from ikaaro.registry import register_resource_class
from ikaaro.webpage import WebPage
from ikaaro.text import Text

# Import from Newsletter
from letter_views import MailingLetterNewInstance, MailingLetterView



class MailingLetter(Folder):

    class_id = 'mailing-letter'
    class_title = MSG(u'Mailing Letter')
    class_description = MSG(u'Send a newsletter to your customers or '
                            u'visitors ...')
    class_schema = merge_dicts(Folder.class_schema,
                               model=String(source='metadata'),
                               is_send=Boolean(source='metadata'),
                               number=Integer(source='metadata'),
                               email=Email(source='metadata'))

    class_views = ['view']
    #               'edit_html', 'edit_text',
    #               'browse_content?mode=list',
    #               'send',
    #               'view_stats']

    new_instance = MailingLetterNewInstance()
    view = MailingLetterView()


    def init_resource(self, **kw):
        Folder.init_resource(self, **kw)

        model = kw['model']
        # A model is used ?
        if model:
            pass
            # XXX We have to save model
            #model = resource.get_resource('models/%s/' % form['model'])
            #for model_resource in model.get_resources():
            #    path = child.get_pathto(model_resource)
            #    child.copy_resource(path, model_resource.name)
        else:
            # HTML Version
            self.make_resource('html_body', WebPage)
            # TXT Version
            self.make_resource('txt_body', Text)



# Register
register_resource_class(MailingLetter)
