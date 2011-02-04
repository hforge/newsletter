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
from itools.gettext import MSG

# import from ikaaro
from ikaaro.webpage import WebPage

# Import from Newsletter
from html_data_views import HTMLDataEdit



class HTMLData(WebPage):
    class_id = 'mailing-html-body'
    class_title = MSG(u'HTML Body')

    class_views = ['view', 'edit']

    edit = HTMLDataEdit()
