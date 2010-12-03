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
from itools.web import STLForm

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
        model = form['model']

        # Create the resource
        class_id = context.query['type']
        cls = get_resource_class(class_id)
        child = resource.make_resource(name, cls, model=model)

        # The metadata
        language = resource.get_edit_languages(context)[0]
        title = Property(title, lang=language)
        child.metadata.set_property('title', title)

        # Ok
        goto = './%s/' % name
        return context.come_back(messages.MSG_NEW_RESOURCE, goto=goto)



class MailingLetterView(STLForm):

    template = '/ui/mailing/MailingLetter_view.xml'
    access = 'is_allowed_to_add'
    title = MSG(u'View')

    def get_namespace(self, resource, context):

        # nb_users
        number = resource.get_property('number')
        if number:
            nb_users = u'Send to %s E-Mails' % number
        else:
            # XXX
            #users = resource.parent.get_resource('users').handler
            #nb_users = u'There are %s E-Mails in Database' % users.get_n_records()
            nb_users =  u'There are [TODO] E-Mails in Database'

        # The data XXX handle the language
        html_data = resource.get_resource('html_body').get_html_data()
        txt_data = resource.get_resource('txt_body').to_text()

        return {'subject': resource.get_title(),
                'is_send': resource.get_property('is_send'),
                'nb_users': MSG(nb_users),
                'html_data': html_data,
                'txt_data': txt_data}


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


