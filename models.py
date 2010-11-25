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
from ikaaro.file import File
from ikaaro.folder import Folder
from ikaaro.registry import register_resource_class



class Models(Folder):

    class_id = 'mailing-models'
    class_title = MSG(u'Mailing Models')

    # XXX
    #class_views = ['view', 'new_resource']
    __fixed_handlers__ = ['default_model']

    # XXX Views
    #view = ModelsView()

    def get_document_types(self):
        return [Model]




class Model(Folder):

    class_id = 'mailing-model'
    class_title = MSG(u'Mailing Model')

    class_views = ['view', 'new_resource', 'browse_content']


    def get_document_types(self):
        return [File]



# Register
register_resource_class(Model)
register_resource_class(Models)


