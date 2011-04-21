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

# Import from Newsletter
from mail import EmailResource
from letter_views import MailingLetterNewInstance, MailingLetterView

email_text_template = MSG("""
To see this news in your browser, please follow this link:
{newsletter_uri}
======================================================
{email_text}
======================================================
Click here to unsubscribe:
{unsubscribe_uri}
""")


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
        self.set_property('state', 'public')


    def get_newsletter_uri(self, context):
        unsub_uri = context.get_link(self)
        unsub_uri = str(context.uri.resolve(unsub_uri))
        return '%s/;download' % unsub_uri


    def get_unsubscribe_uri(self, context):
        unsub_uri = context.get_link(self.parent)
        unsub_uri = str(context.uri.resolve(unsub_uri))
        return '%s/;subscribe' % unsub_uri


    def get_email_text(self, context):
        data = email_text_template.gettext(
                   newsletter_uri=self.get_newsletter_uri(context),
                   unsubscribe_uri=self.get_unsubscribe_uri(context),
                   email_text=self.get_property('email_text'))
        return data.encode('utf-8')


    def get_email_html(self, context, web_version=False):
        header = []
        if web_version is False:
            header = MSG(u"""
                <center>
                  <span style="font-size:10px;font-weight:bold;
                    font-family:Arial,Helvetica,sans-serif;">
                    <a href="{page_uri}" target="_blank">Click here</a>
                    to see this news on you browser
                  </span>
                </center>
                """).gettext(page_uri=self.get_newsletter_uri(context))
            header = HTMLParser(header.encode('utf-8'))
        footer = MSG(u"""
            <center>
              <span style="font-size:10px;font-weight:bold;
                font-family:Arial,Helvetica,sans-serif;">
                <a href="{unsub_uri}" target="_blank">Click here</a>
                to unsubscribe
              </span>
            </center>
            """).gettext(unsub_uri=self.get_unsubscribe_uri(context))
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
        return html_data


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

        # Prepare the last infos
        from_addr = self.parent.get_property('sender')
        subject = self.get_email_subject(context)
        text = self.get_email_text(context)
        html = self.get_email_html(context)

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
