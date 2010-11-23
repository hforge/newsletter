# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Sylvain Taverne <sylvain@itaapy.com>
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
from itools.xapian import PhraseQuery

# Import from ikaaro
from ikaaro.buttons import RemoveButton
from ikaaro.folder_views import Folder_BrowseContent



class ModelsView(Folder_BrowseContent):

    access = 'is_admin'
    title = MSG(u'View')

    search_template = None

    # Table
    table_columns = [
        ('title', MSG(u'Title'))]
    table_actions = [RemoveButton]

    batch_msg1 = MSG(u"There is 1 one model")
    batch_msg2 = MSG(u"There are {n} models")


    def get_items(self, resource, context, *args):
        from models import Model
        args = PhraseQuery('format', Model.class_id)
        return Folder_BrowseContent.get_items(self, resource, context, args)


    def get_item_value(self, resource, context, item, column):
        item_brain, item_resource = item
        if column=='title':
            uri = '%s/;view' % context.resource.get_pathto(item_resource)
            return (item_resource.get_property('title'), uri)
        return Folder_BrowseContent.get_item_value(self, resource, context,
                item, column)
