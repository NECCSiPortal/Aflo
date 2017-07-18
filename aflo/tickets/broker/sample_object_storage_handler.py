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
#

import datetime
import json

from oslo_config import cfg
from oslo_log import log as logging

from aflo.common.broker_base import BrokerBase
from aflo.common.exception import DuringContract
from aflo.common.exception import NotFound
from aflo.db.sqlalchemy import api as db_api
from aflo import i18n
from aflo.tickets.broker.utils import catalog_utils
from aflo.tickets.broker.utils import contract_utils
from aflo.tickets.broker.utils import utils as broker_utils

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

_LE = i18n._LE

CONTRACT_ROLES_VALUE = CONF.ost_contract.ost_roles

CONTRACT_KEY = 'ost'
CONTRACT_GROUP_KEYS = [CONTRACT_KEY, ]


class ObjectStorageHandler(BrokerBase):

    def param_check(self, ctxt, **values):
        self.general_param_check(**values)

    def integrity_check_for_contract_approval(self, ctxt, **values):
        """Integrity checks of the input parameters.
        Also check whether the catalog to the contract is valid.
        """
        self.general_param_check(**values)
        catalog_utils.is_valid_catalog(
            ctxt, values['tenant_id'], self.template['target_id'])
        if contract_utils.is_during_contract(
                ctxt, CONTRACT_GROUP_KEYS, values['tenant_id']):
            raise DuringContract()

    def register_new_contract(self, session, ctxt, **values):

        try:
            ticket = db_api.tickets_get(ctxt, values['id'])
        except NotFound as e:
            error_message = _LE(
                'Failed to get the ticket of object storage contract. %s') % \
                e.args[0]
            LOG.error(error_message)
            raise NotFound(error_message)

        if not isinstance(ticket.ticket_detail, dict):
            ticket.ticket_detail = json.loads(ticket.ticket_detail)

        project_id = values['tenant_id']
        project = broker_utils.get_project(project_id)

        user_id = values['owner_id']
        user = broker_utils.get_user(user_id)

        # create contract
        contract_utils.create_contract(
            ctxt, self.template, ticket, project_id, project.name,
            user.name, CONTRACT_KEY)

        # add role
        broker_utils.add_roles(CONTRACT_ROLES_VALUE,
                               ticket.owner_id, ticket.tenant_id)

        # send mail
        if not CONF.mail.smtp_server:
            return
        email = broker_utils.get_email_address(ticket.owner_id)
        broker_utils.sendmail_for_contract_registration(self, email, **values)

    def integrity_check_for_cancellation(self, ctxt, **values):
        """Integrity checks of the input parameters.
        Also check whether the catalog to the contract is valid.
        """
        self.general_param_check(**values)
        contract_utils.check_canceled(ctxt, **values)

    def register_cancel_contract(self, session, ctxt, **values):
        try:
            ticket = db_api.tickets_get(ctxt, values['id'])
        except NotFound as e:
            error_message = _LE(
                'Failed to get the ticket of object storage contract. %s') % \
                e.args[0]
            LOG.error(error_message)
            raise NotFound(error_message)

        ticket_detail = ticket.ticket_detail
        if not isinstance(ticket_detail, dict):
            ticket_detail = json.loads(ticket_detail)
        contract_id = str(ticket_detail['contract_id'])

        # remove role
        broker_utils.revoke_roles(CONTRACT_ROLES_VALUE,
                                  ticket.tenant_id)

        # update contract
        if isinstance(values['confirmed_at'], datetime.datetime):
            lifetime_end = \
                values['confirmed_at'].strftime('%Y-%m-%dT%H:%M:%S.%f')
        else:
            lifetime_end = values['confirmed_at']
        contract_update_vals = {'lifetime_end': lifetime_end}
        db_api.contract_update(ctxt, contract_id, **contract_update_vals)

        # send mail
        if not CONF.mail.smtp_server:
            return
        email = broker_utils.get_email_address(ticket.owner_id)
        broker_utils.sendmail_for_contract_registration(
            self, email, **values)
