# -*- coding: UTF-8 -*-
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

# Import from the standard library
from thread import start_new_thread
from datetime import datetime
from string import Template
from traceback import print_exc

# Import from ikaaro
from ikaaro.registry import register_resource_class
from ikaaro.folder import Folder
from ikaaro.file import File

# Import from itools
from itools.core import merge_dicts
from itools.stl import stl
from itools.html import xhtml_uri, XHTMLFile, HTMLParser
from itools.xml import XMLParser, START_ELEMENT
from itools.handlers import TextFile
from itools.datatypes import Boolean, Integer, Unicode, Email, DateTime
from itools.gettext import MSG

# Import from here
from letter_views import Letter_NewInstance, Letter_View


class MailingLetter(Folder):

    class_id = 'mailing-letter'
    class_title = MSG(u'Mailing Letter')
    class_description = MSG(u'Send a newsletter to your customers or visitors ...')
    class_views = ['view',
                   'edit_html', 'edit_text',
                   'browse_content?mode=list',
                   'new_resource_form',
                   'send',
                   'view_stats']

    __fixed_handlers__ = ['Stats']

    # Views
    view = Letter_View()
    new_instance = Letter_NewInstance()

    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(Folder.get_metadata_schema(),
                           is_send=Boolean,
                           number=Integer,
                           email=Email,
                           date=DateTime)


    def get_document_types(self):
        return [File]


    def get_newsletter(self, context):
        # Get the footer
        unsubscribe_uri = context.uri.resolve('../;unregister')
        logo_uri  = context.uri.resolve('../;logo?id=%s' % self.name)
        unsubscribe_msg = MSG(u'Click there to unsubscribe').gettext()
        template = ('<br/><div style="text-align:center">'
                    '<img src="%s$user"/>   '
                    '<a href="%s">%s</a></div>')
        footer = template %(logo_uri, unsubscribe_uri, unsubscribe_msg)
        footer = footer.encode('utf-8')
        footer_events = list(HTMLParser(str(footer)))
        # Main document
        index = self.get_resource('index')
        handler = index.handler
        body = handler.get_body()
        events = (handler.events[:body.end]
                  + footer_events
                  + handler.events[body.end:])
        prefix = context.uri.resolve('index/;view')
        return stl(events=events, prefix=prefix, mode='xhtml')


    def send(self, context):
        root = context.root
        parent = self.parent
        # All object must be public
        for object in self.get_resources():
            object.set_property('state', 'public')
        # Transform stream to html
        text = self.get_resource('index_txt').handler.to_str()
        text = unicode(text, "utf-8")
        subject = self.get_property('subject')
        # Get users
        users = parent.get_resource('users')
        records = users.handler.get_records()
        nb_records = users.handler.get_n_records()
        # Get HTML newsletter
        base_html = self.get_newsletter(context)
        base_html = unicode(base_html, "utf-8")
        base_html = Template(base_html)
        # Update newsletter info
        self.set_property('is_send', True)
        self.set_property('number', nb_records)
        context.commit = True
        # Send newsletter
        sender = self.get_property('sender')
        args = (context, records, sender, subject, base_html, text)
        task = start_new_thread(self._send, args)
        return True



    def _send(self, context, records, sender, subject, base_html, text):
        """Send the newsletter (method call by a thread)"""
        # XXX Big hack
        from itools.web import set_context
        set_context(context)
        # Log
        target = context.server.target
        log = open('%s/log/error' % target.path, 'a+')
        # Create spool
        try:
            root = context.root
            for record in records:
                recipient = record.get_value('mail')
                html = base_html.substitute(user='&mail=%s' % recipient)
                root.send_email(recipient, subject, sender, text=text,
                                html=html, subject_with_host=False)
        except:
            # The separator
            log.write('\n')
            log.write('%s\n' % ('*' * 78))
            # The date
            log.write('Newsletter name: %s\n' % self.name)
            log.write('DATE: %s\n' % datetime.now())
            # The traceback
            log.write('\n')
            print_exc(file=log)
            log.flush()
        # End
        log.close()


register_resource_class(MailingLetter)
