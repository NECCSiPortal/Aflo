#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

"""
Test mail.py
"""
import mock
import smtplib

from aflo.common import mail
from aflo.mail import mail_template
from aflo.tests import utils as test_utils

fixtures = {'subject': 'test-subject',
            'body': 'test-body',
            'number': 'test-number',
            'description': 'test-description',
            'url': 'test-url'}


class TestEmail(test_utils.BaseTestCase):
    """
    Test email.py
    """

    def test_sendmail_to_template(self):
        """
        Test Send mail(To)
        """
        with mock.patch("smtplib.SMTP") as mock_clz:
            ins = mock_clz.return_value
            ins.sendmail.return_value = None

            mail.sendmail('to@address',
                          mail_template, fixtures,
                          encode='utf-8', from_address='from@aaa',
                          smtp_server='smtp')
            mock_clz.assert_called_once_with('smtp')

    def test_sendmail_toccbcc_template(self):
        """
        Test Send mail(To, Cc, Bcc)
        """
        with mock.patch("smtplib.SMTP") as mock_clz:
            ins = mock_clz.return_value
            ins.sendmail.return_value = None

            mail.sendmail('to@address',
                          mail_template, fixtures,
                          encode='utf-8', from_address='from@aaa',
                          smtp_server='smtp')
            mock_clz.assert_called_once_with('smtp')

    def test_sendmail_invalid_smpt(self):
        """
        Test send mail by invalid smtp server
        """
        self.assertRaises(smtplib.socket.gaierror,
                          mail.sendmail,
                          'to@address',
                          mail_template, fixtures,
                          'cc@address', 'bcc@address',
                          'utf-8',
                          'from@address',
                          'smtp')
