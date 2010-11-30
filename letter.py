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
from itools.core import merge_dicts
from itools.datatypes import Boolean, Integer, Email

# import from ikaaro
from ikaaro.folder import Folder
from ikaaro.registry import register_resource_class

# Import from Newsletter
from letter_views import MailingLetterNewInstance, MailingLetterView



class MailingLetter(Folder):

    class_id = 'mailing-letter'
    class_title = MSG(u'Mailing Letter')
    class_description = MSG(u'Send a newsletter to your customers or '
                            u'visitors ...')
    class_schema = merge_dicts(Folder.class_schema,
                               is_send=Boolean(source='metadata'),
                               number=Integer(source='metadata'),
                               email=Email(source='metadata'))

    class_views = [ 'view' ]
    #               'edit_html', 'edit_text',
    #               'browse_content?mode=list',
    #               'send',
    #               'view_stats']

    new_instance = MailingLetterNewInstance()
    view = MailingLetterView()



# Register
register_resource_class(MailingLetter)
