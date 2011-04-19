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
from itools.core import freeze, merge_dicts
from itools.database import PhraseQuery, AndQuery
from itools.datatypes import Email
from itools.gettext import MSG

# import from ikaaro
from ikaaro.autoform import TextWidget
from ikaaro.buttons import RemoveButton
from ikaaro.cc import SubscribeForm, ManageForm
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.resource_views import DBResource_Edit
from ikaaro.utils import get_base_path_query


class Mailing_View(Folder_BrowseContent):

    access = 'is_admin'
    title = MSG(u'View')

    search_template = None

    # Table
    batch_msg1 = MSG(u"There is 1 newsletter.")
    batch_msg2 = MSG(u"There are {n} newsletters.")
    table_columns = [
        ('checkbox', None),
        ('title', MSG(u'Title')),
        ('is_sent', MSG(u'Sent ?')),
        ('mtime', MSG(u'Last Modified')),
        ('last_author', MSG(u'Last Author'))]
    table_actions = [RemoveButton]


    def get_items(self, resource, context, *args):
        path = resource.get_canonical_path()
        query = AndQuery(get_base_path_query(str(path)),
                         PhraseQuery('format', 'mailing-letter'))
        return context.root.search(query)


    def get_item_value(self, resource, context, item, column):
        if column == 'title':
            brain, item_resource = item
            href = '%s/' % context.get_link(item_resource)
            return brain.title, href
        elif column == 'is_sent':
            brain, item_resource = item
            is_sent = item_resource.get_property('is_sent')
            if is_sent:
                nb_users = item_resource.get_property('number')
                return MSG(u'Yes (To {x} users)').gettext(x=nb_users)
            return MSG(u'No')
        proxy = super(Mailing_View, self)
        return proxy.get_item_value(resource, context, item, column)



class Mailing_Edit(DBResource_Edit):

    access = 'is_admin'
    title = MSG(u'Configure')

    schema = merge_dicts(DBResource_Edit.schema,
                         sender=Email(source='metadata', mandatory=True))
    widgets = DBResource_Edit.widgets + [TextWidget('sender',
                                         title=MSG(u"Sender's Email"))]



class Mailing_ManageForm(ManageForm):

    table_columns = freeze(ManageForm.table_columns + [
        ('grey_list', 'Unsubscribed')])


    def get_item_value(self, resource, context, item, column):
        if column == 'grey_list':
            on_grey_list = item.name in resource.get_property('grey_list')
            return MSG(u"Yes") if on_grey_list else MSG(u"No")
        proxy = super(Mailing_ManageForm, self)
        return proxy.get_item_value(resource, context, item, column)


class Mailing_SubscribeForm(SubscribeForm):

    subviews = SubscribeForm.subviews[:]
    subviews[1] = Mailing_ManageForm()
