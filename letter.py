# -*- coding: utf-8 -*-
# Copyright (C) 2007 Taverne Sylvain <taverne.sylvain@gmail.com>
# Copyright (C) 2010-2011 David Versmisse <david.versmisse@itaapy.com>
# Copyright (C) 2011 Henry Obein <henry@itaapy.com>
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

# Import from the Standard Library
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email.header import Header

# Import from itools
from itools.core import merge_dicts
from itools.datatypes import Boolean, Integer, Email
from itools.gettext import MSG
from itools.html import HTMLParser
from itools.stl import set_prefix, stl
from itools.web import get_context

# Import from Newsletter
from mail import EmailResource
from letter_views import MailingLetterNewInstance, MailingLetterView



class MailingLetter(EmailResource):

    class_id = 'mailing-letter'
    class_title = MSG(u'Mailing Letter')
    class_description = MSG(u'Send a newsletter to your customers or '
                            u'visitors ...')
    class_schema = merge_dicts(EmailResource.class_schema,
                               is_sent=Boolean(source='metadata'),
                               number=Integer(source='metadata'),
                               email=Email(source='metadata'))
    __fixed_handlers__ = ['mail']

    class_views = ['view', 'edit', 'download']

    new_instance = MailingLetterNewInstance()
    view = MailingLetterView()


    def init_resource(self, **kw):
        EmailResource.init_resource(self)
        root = self.get_root()
        banner = kw['banner']

        ## HTML Version
        default_language = self.get_site_root().get_default_language()
        default_language = 'en'
        if banner:
            banner = self.parent.get_resource(banner)
            banner = get_context().get_link(banner)
        namespace = {'page_uri': './;download',
                     'banner': banner,
                     'title': kw['title']}
        template = root.get_resource('/ui/mailing/LetterTemplate.xml')
        handler = self.get_handler(language=default_language)
        handler.set_changed()
        handler.events = list(stl(template, namespace))
        # TEXT Version
        self.set_property('email_text', u'Your email', language='en')
        self.set_property('email_text', u'Votre email', language='fr')



    def _make_mail_body(self, context):
        # URI to unsubscribe
        unsub_uri = context.get_link(self.parent)
        unsub_uri = str(context.uri.resolve(unsub_uri))
        unsub_uri += '/;subscribe'

        # URI to view the page
        page_uri = str(context.uri.resolve('.')) + '/;download'

        # Make the txt part
        txt_data = MSG(
              u'To see this news in your browser, please follow this link:\n'
                       ).gettext()
        txt_data += page_uri + '\n'
        txt_data += u'======================================================\n'
        txt_data += self.get_property('email_text')
        txt_data += u'\n\n'
        txt_data += u'======================================================\n'
        txt_data += MSG(u'Click here to unsubscribe\n').gettext()
        txt_data += unsub_uri
        txt_data = txt_data.encode('utf-8')

        # Make the HTML part
        header = MSG(u'Please click <a href="{page_uri}">here</a> '
                     ).gettext(page_uri=page_uri)
        header += MSG(u'to see this news on your browser').gettext()
        header = HTMLParser(header.encode('utf-8'))
        footer = MSG(u'Click <a href="{unsub_uri}">here</a> to unsubscribe'
                     ).gettext(unsub_uri=unsub_uri)
        footer = HTMLParser(footer.encode('utf-8'))

        handler = self.handler
        body = handler.get_body()
        events = (handler.events[:body.start + 1]
                  + header
                  + handler.events[body.start + 1:body.end]
                  + footer
                  + handler.events[body.end:])

        # Rewrite link with scheme and autority
        prefix = self.get_site_root().get_pathto(self)
        html_data = set_prefix(events, prefix='%s/' % prefix, uri=context.uri)
        html_data = stl(events=html_data, mode='xhtml')

        return (txt_data, html_data)


    def _make_message(self, from_addr, to_addr, subject, text, html):
        message = MIMEMultipart('related')
        message['Subject'] = Header(subject, 'utf-8')
        message['Date'] = formatdate(localtime=True)
        message['From'] = from_addr
        message['To'] = to_addr
        message['Precedence'] = 'bulk'
        message['List-Unsubscribe'] = '<mailto:%s>' % from_addr
        message_html = MIMEText(html, 'html', _charset='utf-8')
        message_text = MIMEText(text, _charset='utf-8')
        message_alternative = MIMEMultipart('alternative')
        message.attach(message_alternative)
        message_alternative.attach(message_text)
        message_alternative.attach(message_html)
        return message


    def send(self, context):
        server = context.server

        # Users
        users = self.parent.get_subscribed_users()
        if not users:
            return

        # All object must be public
        print self.get_links()

        # Prepare the last infos
        from_addr = self.parent.get_property('sender')
        subject = self.get_title().encode('utf-8')
        text, html = self._make_mail_body(context)

        # Save the emails in the spool
        number = 0
        for username in users:
            user = context.root.get_user(username)
            if user:
                number += 1
                mail = user.get_property('email')
                message = self._make_message(from_addr, mail, subject, text,
                                             html)
                server.save_email(message)

        # And send the messages
        server.flush_spool()

        # Stats
        self.set_property('number', number)
        self.set_property('is_sent', True)
