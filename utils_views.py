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

# Import from the Standard library
from copy import deepcopy

# Import from itools
from itools.core import merge_dicts
from itools.csv import CSVFile
from itools.datatypes import Boolean, Enumerate
from itools.gettext import MSG
from itools.web import ERROR, get_context
from itools.xapian import AndQuery, OrQuery, PhraseQuery
from itools.xml import XMLParser

# Import from ikaaro
from ikaaro.table_views import Table_View

# Import from project
from buttons import Button, ExportCSVButton


def get_value_for_csv(value):
    if type(value) is tuple:
        value = value[0]
    if type(value) is MSG:
        value = value.gettext()
    if type(value) is unicode:
        value = value.encode('utf-8')
    if type(value) is XMLParser:
        value = ''
    if value is None:
        value = ''
    else:
        value = str(value)
    return value


def get_search_query(search_schema, context, query):
    form = context.query
    for key, datatype in search_schema.items():
        value = form.get(key, None)
        if value in (None, '', []):
            continue
        if datatype.multiple is True:
            if len(value) == 1:
                query.append(PhraseQuery(key, value[0]))
            else:
                query.append(OrQuery(*[PhraseQuery(key, x) for x in value]))
        else:
            query.append(PhraseQuery(key, form[key]))
    if len(query) > 1:
        query = AndQuery(*query)
    elif len(query) == 1:
        query = query[0]
    return query



class SearchTable_View(Table_View):

    search_title = MSG(u'Search')
    search_template = '/ui/mailing/table_search.xml'
    search_widgets = []
    search_schema = {}
    search_export_csv = False
    search_buttons = [Button('search', title=u'Rechercher')]


    def GET(self, resource, context):
        # Fonctionnalité d'export CSV automatique d'une table
        if context.get_query_value('export_csv', type=Boolean) is True:
            csv = CSVFile()
            base_columns = self.get_table_columns(resource, context)
            if base_columns[0][0] == 'checkbox':
                base_columns = base_columns[1:]
            columns = [x[0] for x in base_columns]
            # Entete
            csv.add_row([get_value_for_csv(x[0]) for x in base_columns])
            # Lignes du CSV
            items = self.get_items(resource, context)
            for item in self.get_real_items(resource, items):
                line = []
                for column in columns:
                    value = self.get_item_value(resource, context, item, column)
                    value = get_value_for_csv(value)
                    line.append(value)
                csv.add_row(line)
            context.set_content_type('text/csv')
            context.set_content_disposition('attachment', 'export.csv')
            return csv.to_str()

        return Table_View.GET(self, resource, context)


    def get_query_schema(self):
        context = get_context()
        query_schema = merge_dicts(Table_View.get_query_schema(self),
            self.get_search_schema(context.resource, context))
        return query_schema


    def get_search_schema(self, resource, context):
        return self.search_schema


    def on_query_error(self, resource, context):
        # XXX Should be done in itools
        kw = {}
        for key in context.uri.query:
            if not (key in context.query_error.missing or
                key in context.query_error.invalid):
                kw[key] = context.uri.query[key]
        context.uri.query = kw
        msg = ERROR(u'Formulaire invalide')
        return context.come_back(msg, goto=context.uri)


    def get_search_namespace(self, resource, context):
        query = context.query
        namespace = {'title': self.search_title,
                     'submit_value': MSG(u'Rechercher'),
                     'action': '.',
                     'method': 'GET',
                     'submit_class': 'button-ok',
                     'has_required_widget': False,
                     'widgets': []}
        for widget in self.search_widgets:
            value = context.query[widget.name]
            datatype = self.search_schema[widget.name]
            if issubclass(datatype, Enumerate):
                value = datatype.get_namespace(value)
            elif datatype.multiple:
                value = value[0]
            html = widget.to_html(datatype, value)
            namespace['widgets'].append(
                {'name': widget.name,
                 'title': widget.title,
                 'multiple': getattr(datatype, 'multiple', False),
                 'tip': getattr(widget, 'tip', None),
                 'mandatory': getattr(datatype, 'mandatory', False),
                 'class': None,
                 'suffix': widget.suffix,
                 'widget': html})
        # Buttons
        buttons = deepcopy(self.search_buttons)
        if self.search_export_csv is True:
            buttons.append(ExportCSVButton('export_csv', title=MSG(u'Export CSV')))
        namespace['buttons'] = [x.to_html() for x in buttons]
        # First widget
        if namespace['widgets']:
            namespace['first_widget'] = namespace['widgets'][0]['name']
        return namespace


    def get_real_items(self, resource, items):
        return items


    def get_items(self, resource, context, query=None):
        if query is None:
            query = []
        query = get_search_query(self.search_schema, context, query)
        if not query:
            return []
        return resource.handler.search(query)
