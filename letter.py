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

# import from ikaaro
from ikaaro.file import File
from ikaaro.folder import Folder
from ikaaro.folder_views import GoToSpecificDocument
from ikaaro.registry import register_resource_class

# Import from Newsletter
from html_data import HTMLData
from txt_data import TXTData
from letter_views import MailingLetterNewInstance, MailingLetterView



class MailingLetter(Folder):

    class_id = 'mailing-letter'
    class_title = MSG(u'Mailing Letter')
    class_description = MSG(u'Send a newsletter to your customers or '
                            u'visitors ...')
    class_schema = merge_dicts(Folder.class_schema,
                               is_sent=Boolean(source='metadata'),
                               number=Integer(source='metadata'),
                               email=Email(source='metadata'))
    __fixed_handlers__ = ['html_body', 'txt_body']

    class_views = ['view', 'edit_html', 'edit_txt', 'browse_content']

    # XXX DELETE ME
    #class_views = ['view', 'new_instance']
    #               'edit_html', 'edit_text',
    #               'browse_content?mode=list',
    #               'send',
    #               'view_stats']

    new_instance = MailingLetterNewInstance()
    view = MailingLetterView()
    edit_html = GoToSpecificDocument(specific_document='html_body/;edit',
                                     title=MSG(u'Edit HTML'),
                                     access='is_allowed_to_edit')
    edit_txt =  GoToSpecificDocument(specific_document='txt_body',
                                     title=MSG(u'Edit Text'),
                                     access='is_allowed_to_edit')


    def init_resource(self, **kw):
        Folder.init_resource(self)
        banner = kw['banner']

        # HTML Version
        if banner:
            default_language = self.get_site_root().get_default_language()
            banner = self.parent.get_resource(banner)
            namespace = {'page_uri': './;view',
                         'banner': get_context().get_link(banner),
                         'title': kw['title']}
            template = self.get_root().get_resource(
                                       '/ui/mailing/LetterTemplate.xml')
            body = stl(template, namespace, mode='xhtml')
            self.make_resource('html_body', HTMLData, body=body,
                               language=default_language,
                               title={'en': u'HTML Body',
                                      'fr': u'Partie HTML'})
        else:
            self.make_resource('html_body', HTMLData,
                               title={'en': u'HTML Body',
                                      'fr': u'Partie HTML'})

        # TXT Version
        self.make_resource('txt_body', TXTData,
                           title={'en': u'Text body',
                                  'fr': u'Partie texte'})


    def get_document_types(self):
        return [File]


    def _make_mail_body(self, context):
        # URI to unsubscribe
        unsub_uri = context.get_link(self.parent)
        unsub_uri = str(context.uri.resolve(unsub_uri))
        unsub_uri += '/;subscribe'

        # URI to view the page
        html_body = self.get_resource('html_body')
        page_uri = context.get_link(html_body)
        page_uri = str(context.uri.resolve(page_uri)) + '/;view'

        # Make the txt part
        txt_data = MSG(
              u'To see this news in your browser, please follow this link:\n'
                       ).gettext()
        txt_data += page_uri + '\n'
        txt_data += u'======================================================\n'
        txt_data += self.get_resource('txt_body').to_text()
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

        handler = html_body.handler
        body = handler.get_body()
        events = (handler.events[:body.start + 1]
                  + header
                  + handler.events[body.start + 1:body.end]
                  + footer
                  + handler.events[body.end:])

        # Rewrite link with scheme and autority
        prefix = self.get_site_root().get_pathto(html_body)
        html_data = set_prefix(events, prefix='%s/' % prefix, uri=context.uri)
        html_data = stl(events=html_data, mode='xhtml')

        return (txt_data, html_data)


    def _make_message(self, from_addr, to_addr, subject, text, html):

        # Build the message
        message = MIMEMultipart('related')
        message['Subject'] = Header(subject, 'utf-8')
        message['Date'] = formatdate(localtime=True)
        message['From'] = from_addr
        message['To'] = to_addr

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
        users = self.parent.get_property('cc_list')
        if not users:
            return

        # All object must be public
        for object in self.get_resources():
            object.set_property('state', 'public')

        # Prepare the last infos
        from_addr = self.parent.get_property('sender')
        subject = self.get_title().encode('utf-8')
        text, html = self._make_mail_body(context)

        # Save the emails in the spool
        number = 0
        for user in users:
            user = context.root.get_user(user)
            if user and not user.get_property('user_must_confirm'):
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



# Register
register_resource_class(MailingLetter)
