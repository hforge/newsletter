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

# Import from standard library
from datetime import datetime

# Import from itools
from itools.core import merge_dicts
from itools.datatypes import Enumerate
from itools.gettext import MSG
from itools.web import STLForm

# Import from ikaaro
from ikaaro import messages
from ikaaro.forms import SelectWidget
from ikaaro.registry import get_resource_class
from ikaaro.views_new import NewInstance


class EnumerateModels(Enumerate):

    @classmethod
    def get_options(cls):
        options = []
        for model in cls.models.get_resources():
            options.append({'name': model.name,
                            'value': model.get_property('title')})
        return options



class Letter_NewInstance(NewInstance):

    access = 'is_allowed_to_add'
    title = MSG(u'New letter')


    widgets = NewInstance.widgets + \
        [SelectWidget('model', title=MSG(u'Please choose a newsletter model'))]

    def get_schema(self, resource, context):
        models = context.resource.get_resource('models')
        schema = merge_dicts(
            NewInstance.schema,
            model=EnumerateModels(models=models))
        return schema


    def action(self, resource, context, form):
        name = form['name']
        title = form['title']

        # Create the resource
        class_id = context.query['type']
        cls = get_resource_class(class_id)
        child = cls.make_resource(cls, resource, name)

        # The metadata
        metadata = child.metadata
        language = resource.get_content_language(context)
        metadata.set_property('title', title, language=language)
        metadata.set_property('date', datetime.now())

        # We have to save model
        #model = resource.get_resource('models/%s/' % form['model'])
        #for model_resource in model.get_resources():
        #    path = child.get_pathto(model_resource)
        #    child.copy_resource(path, model_resource.name)

        # Ok
        goto = './%s/' % name
        return context.come_back(messages.MSG_NEW_RESOURCE, goto=goto)



class Letter_View(STLForm):

    template = '/ui/mailing/MailingLetter_view.xml'
    access = 'is_allowed_to_add'
    title = MSG(u'View')

    def get_namespace(self, resource, context):
        # Create namespace
        number = resource.get_property('number', None)
        if number:
            nb_users = u'Send to %s E-Mails' % number
        else:
            users = resource.parent.get_resource('users').handler
            nb_users = u'There are %s E-Mails in Database' % users.get_n_records()
        namespace = {'text': 'o', #resource.get_resource('index_txt').handler.to_str(),
                     'is_send': resource.get_property('is_send'),
                     'nb_users': MSG(nb_users),
                     'data': 'o', #resource.get_resource('index').get_html_data(),
                     'subject': resource.get_title()}
        return namespace


    def action(self, resource, context, form):
        if resource.get_property('is_send') is True:
            context.message = MSG(u'Newsletter already send !')
            return
        sender = resource.get_property('sender')
        if not sender:
            context.message = MSG(u'Please configure the sender !')
        resource.send(context)
        msg = MSG(u'Newsletter sended !')
        return context.come_back(msg, goto='../')
