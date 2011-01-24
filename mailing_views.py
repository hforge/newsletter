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
from itools.core import merge_dicts
from itools.database import PhraseQuery, AndQuery
from itools.datatypes import Email
from itools.gettext import MSG

# import from ikaaro
from ikaaro.autoform import TextWidget
from ikaaro.cc import SubscribeForm
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.resource_views import DBResource_Edit
from ikaaro.utils import get_base_path_query
from ikaaro.views import ContextMenu



class MailingEdit(DBResource_Edit):

    access = 'is_admin'
    title = MSG(u'Configure')

    schema = merge_dicts(DBResource_Edit.schema,
                         sender=Email(source='metadata', mandatory=True))
    widgets = DBResource_Edit.widgets + [TextWidget('sender',
                                         title=MSG(u"Sender's Email"))]



class MailingMenu(ContextMenu):

    title = MSG(u'Menu')

    def get_items(self):
        path = self.context.get_link(self.resource)
        return [ {'title': MSG(u'Create a newsletter'),
                  'href': '%s/;new_resource?type=mailing-letter' % path} ]



class MailingView(Folder_BrowseContent):

    access = 'is_admin'
    title = MSG(u'View')

    template = '/ui/mailing/Mailing_view.xml'
    search_template = None
    context_menus = [MailingMenu()]


    def get_namespace(self, resource, context):
        namespace = super(MailingView, self).get_namespace(resource, context)
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



class MailingSubscribe(SubscribeForm):
    template = '/ui/mailing/Mailing_subscribe.xml'
