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
from ikaaro.views import ContextMenu


class Mailing_Menu(ContextMenu):
    title = MSG(u'Menu')


    def get_items(self):
        path = self.context.get_link(self.resource)
        return [ {'title': MSG(u'Create a newsletter'),
                  'href': '%s/;new_resource?type=mailing-letter' % path} ]



class Mailing_View(Folder_BrowseContent):
    access = 'is_admin'
    title = MSG(u'View')

    template = '/ui/mailing/Mailing_view.xml'
    search_template = None
    context_menus = [Mailing_Menu()]

    # Table
    batch_msg1 = MSG(u"There is 1 newsletter.") # FIXME Use plural forms
    batch_msg2 = MSG(u"There are {n} newsletters.")
    table_columns = [
        ('checkbox', None),
        ('title', MSG(u'Title')),
        ('mtime', MSG(u'Last Modified')),
        ('last_author', MSG(u'Last Author'))]
    table_actions = [ RemoveButton ]


    def get_namespace(self, resource, context):
        proxy = super(Mailing_View, self)
        namespace = proxy.get_namespace(resource, context)
        namespace['spool_size'] = context.server.get_spool_size()
        return namespace


    def get_items(self, resource, context, *args):
        # Query
        args = list(args)

        # Search in subtree
        path = resource.get_canonical_path()
        query = get_base_path_query(str(path))
        args.append(query)

        # Filter by type
        args.append(PhraseQuery('format', 'mailing-letter'))

        # Ok
        query = AndQuery(*args)

        return context.root.search(query)


    def get_item_value(self, resource, context, item, column):
        if column == 'title':
            brain, item_resource = item
            href = '%s/' % context.get_link(item_resource)
            return brain.title, href
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

    def get_items(self, resource, context):
        items = super(Mailing_ManageForm, self).get_items(resource, context)
        # Filter out unsubscribed users
        subscribed_users = list(resource.get_subscribed_users(
                skip_unconfirmed=False))
        return [user for user in items if user.name in subscribed_users]



class Mailing_SubscribeForm(SubscribeForm):
    subviews = SubscribeForm.subviews[:]
    subviews[1] = Mailing_ManageForm()
