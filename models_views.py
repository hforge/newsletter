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
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.views import ContextMenu



class ModelsMenu(ContextMenu):

    title = MSG(u'Menu')

    def get_items(self):
        path = self.context.get_link(self.resource)
        return [ {'title': MSG(u'Create a model'),
                  'href': '%s/;new_resource?type=mailing-model' % path} ]



class ModelsView(Folder_BrowseContent):

    access = 'is_admin'
    title = MSG(u'View')

    context_menus = [ModelsMenu()]
