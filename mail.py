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
from itools.datatypes import String
from itools.gettext import MSG
from itools.xml import START_ELEMENT, END_ELEMENT, COMMENT

# import from ikaaro
from ikaaro.autoform import HTMLBody, RTEWidget, timestamp_widget
from ikaaro.autoform import MultilineWidget, TextWidget
from ikaaro.datatypes import Multilingual
from ikaaro.file_views import File_Download
from ikaaro.webpage import WebPage, HTMLEditView


def rewrite_css_to_attribute(stream):
    """
    Replace for table and td
    style="width=xxx" by width="xxx"
    style="height=xxx" by height="xxx"
    style="background-color=xxx" by bgcolor="xxx"
    style="text-align=xxx" by align="xxx"
    """
    style_map = {'width': 'width',
                 'height': 'height',
                 'background-color': 'bgcolor',
                 'text-align': 'align'}

    for event in stream:
        type, value, line = event
        if type == START_ELEMENT:
            tag_uri, tag_name, _attributes = value
            if tag_name not in ('table', 'td'):
                yield event
                continue
            # Rewrite attributes
            attributes = _attributes.copy()
            style = attributes.get((None, 'style'), None)
            if not style:
                # Do nothing
                yield event
                continue

            for item in style.split(';'):
                try:
                    key, value = item.split(':')
                except ValueError:
                    continue
                key = key.strip()
                if key in style_map:
                    attributes[(None, style_map[key])] = value.strip()
            yield type, (tag_uri, tag_name, attributes), line
        else:
            yield event


class EmailHTMLBody(HTMLBody):

    def decode(cls, data):
        events = super(EmailHTMLBody, cls).decode(data)
        return list(rewrite_css_to_attribute(events))



class EmailResource_Edit(HTMLEditView):

    schema = {'timestamp': HTMLEditView.schema['timestamp'],
              'title': Multilingual,
              'email_subject': Multilingual,
              'data': EmailHTMLBody(multilingual=True,
                               parameters_schema={'lang': String}),
              'email_text': Multilingual}
    widgets = [
        TextWidget('title', title=MSG(u'Title')),
        TextWidget('email_subject', title=MSG(u'Email subject')),
        MultilineWidget('email_text', title=MSG(u'Email body (Text Version)')),
        RTEWidget('data', title=MSG(u'Email body (HTML Version)')),
        timestamp_widget]

    def _get_schema(self, resource, context):
        return self.schema



class EmailResource_Download(File_Download):

    def get_bytes(self, resource, context):
        return resource.get_email_html(context, web_version=True)


class EmailResource(WebPage):

    class_id = 'email'
    class_title = MSG(u'Email')
    class_schema = merge_dicts(WebPage.class_schema,
                               email_subject=Multilingual(source='metadata'),
                               email_text=Multilingual(source='metadata'))

    class_views = ['edit', 'download']

    edit = EmailResource_Edit()
    download = EmailResource_Download(title=MSG(u'View Email'))


    def get_email_subject(self, context):
        subject = self.get_property('email_subject')
        return subject.encode('utf-8')


    def get_email_text(self, context):
        data = self.get_property('email_text')
        return data.encode('utf-8')


    def get_email_html(self, context, web_version=False):
        return self.handler.to_str()
