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

from email.header import Header
from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib

from aflo import i18n
from oslo_config import cfg
from oslo_log import log as logging


CONF = cfg.CONF
LOG = logging.getLogger(__name__)

_ = i18n._
_LE = i18n._LE


def _replaceData(template, data):
    """Replace Data
        :params template : Mail text template.
        :params data : Replace data for template.
    """
    template = template.encode('utf_8')
    for key, value in data.items():
        try:
            value = str(value)
        except UnicodeEncodeError:
            value = value.encode('utf_8')
        try:
            key = str(key)
        except UnicodeEncodeError:
            key = key.encode('utf_8')

        template = template.replace("${" + key + "}", value)

    return template


def sendmail(to_address, template, data, cc_address=None, bcc_address=None,
             encode=None, from_address=None, smtp_server=None):
    """Send Mail.
        Replace '${name}' 'data' in Template Contents.
        Send Address Ex : 'aaa@bbb' or '[aaa@bbb, ccc@ddd]'.
        :params to_address : Send to address.
        :params template : Use Template Object.
        :params data : Dictionary Object.Replace KEY-VALUE in Template.
        :params cc_address : Send to address.
        :params bcc_address : Send to address.
        :params encode : Text encoding type.
        :params from_address : Send from address.
        :params smtp_server : Send SMTP server.
    """
    # Load Setting from .conf
    if encode is None:
        encode = CONF.mail.encode
    if from_address is None:
        from_address = CONF.mail.from_address
    if smtp_server is None:
        smtp_server = CONF.mail.smtp_server

    user = CONF.mail.user
    password = CONF.mail.password

    # Create Message
    message = MIMEText(_replaceData(template.BODY, data), "plain", encode)
    message["Subject"] = Header(_replaceData(template.SUBJECT, data), encode)
    message["From"] = from_address

    if isinstance(to_address, list):
        message["To"] = ', '.join(to_address)
    else:
        message["To"] = to_address

    if cc_address is not None:
        if isinstance(cc_address, list):
            message["Cc"] = ', '.join(cc_address)
        else:
            message["Cc"] = cc_address

    if bcc_address is not None:
        if isinstance(bcc_address, list):
            message["Bcc"] = ', '.join(bcc_address)
        else:
            message["Bcc"] = bcc_address

    message["Date"] = formatdate()

    LOG.debug("Send Mail Server: %s", smtp_server)
    LOG.debug("Send Mail Text: %s", message.as_string())

    # Send to Server
    try:
        smtp = smtplib.SMTP(smtp_server)
        try:
            if user:
                smtp.login(user, password)

            smtp.sendmail(from_address, to_address, message.as_string())
        finally:
            if smtp:
                smtp.close()

        LOG.debug("Send Mail Success.")

    except Exception:
        LOG.error(_LE("Send Mail Failed."))
        raise
