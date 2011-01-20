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
from itools.datatypes import Boolean, Integer, Email
from itools.gettext import MSG
from itools.stl import stl
from itools.uri import get_reference

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

    # XXX DELETE ME ?
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
            namespace = {'page_uri': './html_body/;view',
                         'banner': get_reference(banner.get_abspath()),
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
        page_uri = context.get_link(self.get_resource('html_body'))
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

        return txt_data


    def send(self, context):
        # Make the mail
        mail_body = self._make_mail_body(context)

        # All object must be public
        for object in self.get_resources():
            object.set_property('state', 'public')

        # Stats
        number = self.parent.get_subscripters_nb()
        self.set_property('number', number)
        #self.set_property('is_sent', True)

        # XXX FINISH ME
        print 'SENT !'
        print mail_body



# Register
register_resource_class(MailingLetter)
