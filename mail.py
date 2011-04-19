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
from itools.datatypes import String
from itools.gettext import MSG

# import from ikaaro
from ikaaro.autoform import HTMLBody, rte_widget, timestamp_widget
from ikaaro.autoform import MultilineWidget
from ikaaro.datatypes import Multilingual
from ikaaro.file_views import File_Download
from ikaaro.webpage import WebPage, HTMLEditView



class EmailResource_Edit(HTMLEditView):

    schema = {'timestamp': HTMLEditView.schema['timestamp'],
              'data': HTMLBody(multilingual=True,
                               parameters_schema={'lang': String}),
              'email_text': Multilingual}
    widgets = [rte_widget,
               MultilineWidget('email_text', title=MSG(u'Text version')),
               timestamp_widget]

    def _get_schema(self, resource, context):
        return self.schema



class EmailResource(WebPage):

    class_id = 'email'
    class_title = MSG(u'Email')
    class_schema = merge_dicts(WebPage.class_schema,
                               email_text=Multilingual(source='metadata'))

    class_views = ['edit', 'view']

    edit = EmailResource_Edit()
    view = File_Download(title=MSG(u'View Email'))
