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
from itools.gettext import MSG
from itools.core import merge_dicts
from itools.datatypes import Boolean, Integer, Email, String

# import from ikaaro
from ikaaro.folder import Folder
from ikaaro.registry import register_resource_class

# Import from Newsletter
from model import Model
from html_data import HTMLData
from txt_data import TXTData
from letter_views import MailingLetterNewInstance, MailingLetterView



class MailingLetter(Model):

    class_id = 'mailing-letter'
    class_title = MSG(u'Mailing Letter')
    class_description = MSG(u'Send a newsletter to your customers or '
                            u'visitors ...')
    class_schema = merge_dicts(Folder.class_schema,
                               model=String(source='metadata'),
                               is_sent=Boolean(source='metadata'),
                               number=Integer(source='metadata'),
                               email=Email(source='metadata'))

    #class_views = ['view', 'new_instance']
    #               'edit_html', 'edit_text',
    #               'browse_content?mode=list',
    #               'send',
    #               'view_stats']

    new_instance = MailingLetterNewInstance()
    view = MailingLetterView()


    def init_resource(self, **kw):
        Folder.init_resource(self, **kw)

        model = kw['model']
        # A model is used ?
        if model:
            model = self.parent.get_resource('models/%s' % model)
            for res in model.get_resources():
                self.copy_resource(res.get_abspath(), model.get_pathto(res))
        else:
            # HTML Version
            self.make_resource('html_body', HTMLData,
                               title={'en': u'HTML Body',
                                      'fr': u'Partie HTML'})
            # TXT Version
            self.make_resource('txt_body', TXTData,
                               title={'en': u'Text body',
                                      'fr': u'Partie texte'})


    def _make_mail_body(self, context):
        # URI to unsubscribe
        unsub_uri = context.get_link(self.parent)
        unsub_uri = str(context.uri.resolve(unsub_uri))
        unsub_uri += '/;subscribe'

        # Make the txt part
        txt_data = self.get_resource('txt_body').to_text()
        txt_data += u'\n\n'
        txt_data += u'==================================================\n'
        txt_data += MSG(u'Click there to unsubscribe\n').gettext()
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
        self.set_property('is_sent', True)

        # XXX FINISH ME
        print 'SENT !'
        print mail_body




# Register
register_resource_class(MailingLetter)
