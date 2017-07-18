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

import json

from oslo_config import cfg
from oslo_log import log as logging

from aflo.common.broker_base import BrokerBase
from aflo.common import mail
from aflo.db.sqlalchemy import api as db_api
from aflo.mail.common_request import mail_common_request_accepted
from aflo.mail.common_request import mail_common_request_completed
from aflo.mail.common_request import mail_common_request_request
from aflo.mail.user_registration import mail_user_registration_accepted
from aflo.mail.user_registration import mail_user_registration_completed
from aflo.mail.user_registration import mail_user_registration_request
from aflo.tickets.broker.utils import utils as broker_utils

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class UserEntryRequestHandler(BrokerBase):

    def param_check(self, ctxt, **values):
        """It is performed 'before' changing the status 'inquiring' """
        self.general_param_check(**values)

    def mail_to_support(self, session, *args, **values):
        owner_mail = broker_utils.get_email_address(values.get('owner_id'))
        if owner_mail is not None:
            owner_mail = '(' + owner_mail + ')'
        next_roles = broker_utils.get_next_roles(self)
        addresses = \
            broker_utils.get_email_addresses_from_role(values['tenant_id'],
                                                       next_roles)
        if not addresses or 0 == len(addresses):
            return

        ticket_detail = values['ticket_detail']
        data = {'id': values['id'],
                'date_time': values['owner_at'],
                'owner_name': values['owner_name'],
                'owner_mail': owner_mail,
                'project_id': values['tenant_id'],
                'project_name': values['tenant_name'],
                'user_name': ticket_detail.get('User Name', ''),
                'mail': ticket_detail.get('Email', ''),
                'roles': ', '.join(ticket_detail.get('Role', '')),
                'message': ticket_detail.get('Message', ''),
                'status': broker_utils.get_status_name(self,
                                                       self.after_status_code)
                }

        if CONF.mail.smtp_server:
            mail.sendmail(addresses,
                          mail_user_registration_request,
                          data)

    def mail_to_member(self, session, *args, **values):
        owner_mail = broker_utils.get_email_address(values.get('owner_id'))
        if not owner_mail:
            return

        addresses = [owner_mail]
        if owner_mail is not None:
            owner_mail = '(' + owner_mail + ')'

        ticket = db_api._ticket_get(self.ctxt, values['id'], session)
        ticket_detail = ticket.ticket_detail
        if ticket_detail and \
                not isinstance(ticket_detail, dict):
            ticket_detail = json.loads(ticket_detail)

        data = {'id': values['id'],
                'date_time': values['owner_at'],
                'owner_name': values['owner_name'],
                'owner_mail': owner_mail,
                'project_id': values['tenant_id'],
                'project_name': values['tenant_name'],
                'user_name': ticket_detail.get('User Name', ''),
                'mail': ticket_detail.get('Email', ''),
                'roles': ', '.join(ticket_detail.get('Role', '')),
                'message': ticket_detail.get('Message', ''),
                'status': broker_utils.get_status_name(self,
                                                       self.after_status_code)
                }

        if CONF.mail.smtp_server:
            if 'working' == self.after_status_code:
                mail.sendmail(addresses,
                              mail_user_registration_accepted,
                              data)

            elif 'done' == self.after_status_code:
                mail.sendmail(addresses,
                              mail_user_registration_completed,
                              data)


class CommonRequestHandler(BrokerBase):

    def __init__(self,
                 ctxt,
                 template_contents,
                 wf_pattern_contents,
                 **values):
        """Load template contents and workflow pattern contents from json string.
        :param ctxt: Request context.
        :param template_contents: Ticket template contents json string.
        :param wf_pattern_contents: Workflow Pattern contents json string.
        :param values: Input data from form.
        """
        BrokerBase.__init__(self,
                            ctxt,
                            template_contents,
                            wf_pattern_contents,
                            **values)

    def param_check(self, ctxt, **values):
        """It is performed 'before' changing the status 'inquiring' """
        self.general_param_check(**values)

    def mail_to_support(self, session, *args, **values):
        owner_mail = broker_utils.get_email_address(values.get('owner_id'))
        if owner_mail is not None:
            owner_mail = '(' + owner_mail + ')'
        next_roles = broker_utils.get_next_roles(self)
        addresses = \
            broker_utils.get_email_addresses_from_role(values['tenant_id'],
                                                       next_roles)
        if not addresses or 0 == len(addresses):
            return

        ticket_detail = values['ticket_detail']
        data = {'id': values['id'],
                'date_time': values['owner_at'],
                'owner_name': values['owner_name'],
                'owner_mail': owner_mail,
                'project_id': values['tenant_id'],
                'project_name': values['tenant_name'],
                'message': ticket_detail.get('Message', ''),
                'status': broker_utils.get_status_name(self,
                                                       self.after_status_code)
                }

        if CONF.mail.smtp_server:
            mail.sendmail(addresses,
                          mail_common_request_request,
                          data)

    def mail_to_member(self, session, *args, **values):
        owner_mail = broker_utils.get_email_address(values.get('owner_id'))
        if not owner_mail:
            return

        addresses = [owner_mail]
        if owner_mail is not None:
            owner_mail = '(' + owner_mail + ')'

        ticket = db_api._ticket_get(self.ctxt, values['id'], session)
        ticket_detail = ticket.ticket_detail
        if ticket_detail and \
                not isinstance(ticket_detail, dict):
            ticket_detail = json.loads(ticket_detail)

        data = {'id': values['id'],
                'date_time': values['owner_at'],
                'owner_name': values['owner_name'],
                'owner_mail': owner_mail,
                'project_id': values['tenant_id'],
                'project_name': values['tenant_name'],
                'message': ticket_detail.get('Message', ''),
                'status': broker_utils.get_status_name(self,
                                                       self.after_status_code)
                }

        if CONF.mail.smtp_server:
            if 'working' == self.after_status_code:
                mail.sendmail(addresses,
                              mail_common_request_accepted,
                              data)

            elif 'done' == self.after_status_code:
                mail.sendmail(addresses,
                              mail_common_request_completed,
                              data)
