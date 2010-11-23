# -*- coding: UTF-8 -*-
# Copyright (C) 2010 Sylvain Taverne <sylvain@itaapy.com>
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

# Import from ikaaro
from ikaaro.forms import Widget

# Import from ortho
from utils import make_stl_template


################################################
# XXX That must be done in ikaaro
################################################

class Button(Widget):

    access = False
    confirm = None
    css = 'button-ok'
    name = None
    title = None
    value = None

    template = make_stl_template("""
    <button type="submit" name="${name}" class="${css}" value="${value}">${title}</button>""")


    def __init__(self, name=None, **kw):
        for key in kw:
            setattr(self, key, kw[key])
        self.name = name


    def get_namespace(self, datatype, value):
        return {'name': self.name,
                'css': self.css,
                'value': self.value,
                'title': self.title}


    def to_html(self):
        return Widget.to_html(self, None, None)


    @classmethod
    def show(cls, resource, context, items):
        if len(items) == 0:
            return False
        ac = resource.get_access_control()
        return ac.is_access_allowed(context.user, resource, cls)



class ExportCSVButton(Button):

    access = 'is_allowed_to_edit'
    css = 'button-csv'
    name = 'export_csv'
    value = '1'
    title = MSG(u'Export CSV')


