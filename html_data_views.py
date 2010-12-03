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
from itools.datatypes import String

# import from ikaaro
from ikaaro.webpage import HTMLEditView
from ikaaro.autoform import HTMLBody, rte_widget, timestamp_widget



class HTMLDataEdit(HTMLEditView):
    schema = {'timestamp': HTMLEditView.schema['timestamp'],
              'data':
              HTMLBody(multilingual=True, parameters_schema={'lang': String})}
    widgets = [rte_widget, timestamp_widget]

