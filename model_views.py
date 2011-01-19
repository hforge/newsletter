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
from itools.web import STLView



class ModelView(STLView):

    template = '/ui/mailing/Model_view.xml'
    access = 'is_allowed_to_add'
    title = MSG(u'View')


    def get_namespace(self, resource, context):

        # The data XXX handle the language
        html_data = resource.get_resource('html_body').get_html_data()
        txt_data = resource.get_resource('txt_body').to_text()

        return {'html_data': html_data,
                'txt_data': txt_data}
