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
from itools.datatypes import Enumerate
from itools.gettext import MSG
from itools.csv import Property

# Import from ikaaro
from ikaaro.autoform import SelectWidget
from ikaaro.views_new import NewInstance
from ikaaro.registry import get_resource_class
from ikaaro import messages



class EnumerateModels(Enumerate):

    @classmethod
    def get_options(cls):
        options = []
        for model in cls.models.get_resources():
            options.append({'name': model.name,
                            'value': model.get_property('title')})
        return options



class MailingLetterNewInstance(NewInstance):

    widgets = NewInstance.widgets + [SelectWidget('model',
              title=MSG(u'Please choose a newsletter model'))]


    def get_schema(self, resource, context):
        models = context.resource.get_resource('models')
        schema = merge_dicts(NewInstance.schema,
                             model=EnumerateModels(models=models))
        return schema


    def action(self, resource, context, form):
        name = form['name']
        title = form['title']

        # Create the resource
        class_id = context.query['type']
        cls = get_resource_class(class_id)
        child = resource.make_resource(name, cls)

        # The metadata
        language = resource.get_edit_languages(context)[0]
        title = Property(title, lang=language)
        child.metadata.set_property('title', title)

        # XXX We have to save model
        #model = resource.get_resource('models/%s/' % form['model'])
        #for model_resource in model.get_resources():
        #    path = child.get_pathto(model_resource)
        #    child.copy_resource(path, model_resource.name)

        # Ok
        goto = './%s/' % name
        return context.come_back(messages.MSG_NEW_RESOURCE, goto=goto)
