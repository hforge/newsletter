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
from itools.web import ERROR

# import from ikaaro
from ikaaro.autoform import TextWidget
from ikaaro.buttons import RemoveButton
from ikaaro.cc import SubscribeForm
from ikaaro.folder_views import Folder_BrowseContent
from ikaaro.messages import MSG_CHANGES_SAVED
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


    def get_item_value(self, resource, context, item, column):
        if column == 'title':
            brain, item_resource = item
            href = '%s/' % context.get_link(item_resource)
            return brain.title, href
        return super(MailingView, self).get_item_value(resource, context,
                                                       item, column)



class MailingSubscribe(SubscribeForm):

    template = '/ui/mailing/Mailing_subscribe.xml'

    def action(self, resource, context, form):
        x_email = form.get('x_email')
        x_subscribe = form.get('x_subscribe')
        new_cc = form.get('cc_list')
        new_users = form.get('new_users')
        grey_list =  set(resource.get_property('grey_list'))

        # Case 1: anonymous user
        user = context.user
        if user is None:
            new_cc = set(resource.get_property('cc_list'))

            if x_subscribe:
                new_id = self._add_user(resource, context, x_email)
                new_cc.add(new_id)
                grey_list.discard(new_id)
                context.message = MSG(u'A new account has been created and '
                                u'you are now registered to this newsletter')
            else:
                # Check whether the user already exists
                user = context.root.get_user_from_login(x_email)
                if user:
                    new_cc.discard(user.name)
                    grey_list.add(user.name)
                    context.message = MSG_CHANGES_SAVED
                else:
                    context.message = ERROR(
                                    u'This user was not in our database')
            # Ok
            resource.set_property('cc_list', tuple(new_cc))
            resource.set_property('grey_list', tuple(grey_list))
            context.get_form()['cc_list'] = list(new_cc)
            context.get_form()['new_users'] = ''
            return

        # Case 2: admin
        ac = resource.get_access_control()
        is_admin = ac.is_admin(context.user, resource)
        if is_admin:
            new_id_set = set()
            for email in new_users:
                new_id_set.add(self._add_user(resource, context, email))
            new_cc = set(new_cc).union(new_id_set)
            new_cc = new_cc - grey_list

            # Ok
            context.message = MSG_CHANGES_SAVED
            self._reset_context(resource, context, new_cc)
            return

        # Case 3: someone else
        old_cc = resource.get_property('cc_list')
        if user.name in new_cc:
            new_cc = set(old_cc)
            new_cc.add(user.name)
            grey_list.discard(user.name)
        else:
            new_cc = set(old_cc)
            new_cc.discard(user.name)
            grey_list.add(user.name)

        # Ok
        context.message = MSG_CHANGES_SAVED
        resource.set_property('grey_list', tuple(grey_list))
        self._reset_context(resource, context, new_cc)
