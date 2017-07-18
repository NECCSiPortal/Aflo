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
#

from oslo_log import log as logging

from aflo.common.broker_base import BrokerBase
from aflo.common import mail
from aflo.mail import mail_template

LOG = logging.getLogger(__name__)

ACTION_CRAETE = 'create'
ACTION_UPDATE = 'update'


class SampleBroker(BrokerBase):

    def param_check(self, ctxt, **values):
        self.general_param_check(**values)

    def sendmail(self, session, *args, **values):  # noap
        LOG.debug("sendmail Begin")

        to_address = "to.address@sample.com"
        url = 'http://localhost/'

        if not self.before_status_code or self.before_status_code == "none":
            data = {'subject': 'Create application [%s] from %s' %
                    (self.after_status_code, values["owner_name"]),
                    'user': values["owner_name"],
                    'update_date': values['owner_at'],
                    'body': 'Change status to [%s]' % self.after_status_code,
                    'url': url}
        else:
            data = {'subject': 'Change status [%s] from %s' %
                    (self.after_status_code, values["confirmer_name"]),
                    'user': values["confirmer_name"],
                    'update_date': values['confirmed_at'],
                    'body': 'Change status to [%s]' % self.after_status_code,
                    'url': url}

        mail.sendmail(to_address, mail_template, data)

        LOG.debug("sendmail End")
