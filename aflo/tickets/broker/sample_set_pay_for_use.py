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

import datetime
import json
import six

from oslo_config import cfg

from aflo.common.broker_base import BrokerBase
from aflo.common.exception import CancellationNGState
from aflo.common.exception import DuringContract
from aflo.common.exception import NotFound
from aflo.db.sqlalchemy import api as db_api
from aflo.tickets.broker.utils import catalog_utils
from aflo.tickets.broker.utils import contract_utils
from aflo.tickets.broker.utils import utils as broker_utils

CONF = cfg.CONF

CONTRACT_QUOTA_VALUE = CONF.quotas.pay_for_use_contract_quota_value
CONTRACT_KEY = 'contract-pay-for-use'
CONTRACT_GROUP_KEYS = ['contract-flat-rate', CONTRACT_KEY, ]


class PayForUseHandler(BrokerBase):

    def param_check(self, ctxt, **values):
        self.general_param_check(**values)

    def integrity_check_for_contract_approval(self, ctxt, **values):
        self.general_param_check(**values)
        catalog_utils.is_valid_catalog(
            ctxt, values['tenant_id'], self.template['target_id'])
        if contract_utils.is_during_contract(
                ctxt, CONTRACT_GROUP_KEYS, values['tenant_id']):
            raise DuringContract()

    def register_new_contract(self, session, ctxt, **values):

        ticket = db_api.tickets_get(ctxt, values['id'])

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

        # update quotas
        self._update_quotas_value(ticket.tenant_id,
                                  CONTRACT_QUOTA_VALUE)

        # send mail
        if not CONF.mail.smtp_server:
            return

        email = broker_utils.get_email_address(ticket.owner_id)
        broker_utils.sendmail_for_contract_registration(self, email, **values)

    def integrity_check_for_cancellation(self, ctxt, **values):
        self.general_param_check(**values)
        contract_utils.check_canceled(ctxt, **values)
        try:
            ticket = db_api.tickets_get(ctxt, values['id'])
            project_id = ticket.tenant_id
            ticket_detail = ticket.ticket_detail
        except NotFound:
            project_id = values['tenant_id']
            ticket_detail = values['ticket_detail']

        if not isinstance(ticket_detail, dict):
            ticket_detail = json.loads(ticket_detail)

        try:
            nova = broker_utils.get_nova_client()
            nova_limits = nova.limits.get(tenant_id=project_id)
            cinder = broker_utils.get_cinder_client()
            cinder_quotas_usage = cinder.quotas.get(project_id, usage=True)
            for quota_key in six.iterkeys(CONTRACT_QUOTA_VALUE):
                if quota_key not in broker_utils.NOVA_LIMIT_USED_KEYS \
                        and quota_key not in \
                        broker_utils.CINDER_LIMIT_USED_KEYS:
                    continue

                # Describe the process of acquiring the usage here is
                # if you want to add a quota item.
                if quota_key in broker_utils.CINDER_QUOTAS:
                    use_size = long(cinder_quotas_usage.gigabytes['in_use'])
                else:
                    limit_key = broker_utils.NOVA_LIMIT_USED_KEYS[quota_key]
                    use_size = long(
                        nova_limits.to_dict()['absolute'][limit_key])
                if 0 < use_size:
                    raise CancellationNGState()
        except NotFound:
            raise NotFound()

    def register_cancel_contract(self, session, ctxt, **values):
        try:
            ticket = db_api.tickets_get(ctxt, values['id'])
            ticket_detail = ticket.ticket_detail
            if not isinstance(ticket_detail, dict):
                ticket_detail = json.loads(ticket_detail)
            contract_id = str(ticket_detail['contract_id'])

            cancellation_quota_value = {}
            for quota_key in six.iterkeys(CONTRACT_QUOTA_VALUE):
                cancellation_quota_value[quota_key] = 0
            # update quotas
            self._update_quotas_value(ticket.tenant_id,
                                      cancellation_quota_value)

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
        except NotFound:
            raise NotFound()

    def _update_quotas_value(self, tenant_id, update_val):

        broker_utils.update_quotas(tenant_id, **update_val)
