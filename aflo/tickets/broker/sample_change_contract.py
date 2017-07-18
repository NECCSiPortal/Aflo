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
import six

from oslo_config import cfg
from oslo_log import log as logging

from aflo.common.broker_base import BrokerBase
from aflo.common.exception import DuringContract
from aflo.common.exception import InvalidStatus
from aflo.common.exception import NotFound
from aflo.db.sqlalchemy import api as db_api
from aflo import i18n
from aflo.tickets.broker.utils import catalog_utils
from aflo.tickets.broker.utils import contract_utils
from aflo.tickets.broker.utils import INTERNAL_UTC_DATETIME_FORMAT
from aflo.tickets.broker.utils import utils as broker_utils

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

CONTRACT_KEY_FLAT_RATE = 'contract-flat-rate'
CONTRACT_KEY_PAY_FOR_USE = 'contract-pay-for-use'
CONTRACT_QUOTA_VALUE = CONF.quotas.pay_for_use_contract_quota_value

CORES = broker_utils.NOVA_QUOTAS[0]
RAM = broker_utils.NOVA_QUOTAS[1]
GIGABYTES = broker_utils.CINDER_QUOTAS[0]

_LE = i18n._LE


class ChangeToFlatRateContractHandler(BrokerBase):

    def param_check(self, ctxt, **values):
        self.general_param_check(**values)

    def integrity_check_for_contract_approval(self, ctxt, **values):
        """Integrity checks of the input parameters.
        Also check whether the catalog to the contract is valid.
        """
        self.general_param_check(**values)

        project_id = values['tenant_id']
        catalog_utils.is_valid_catalog(
            ctxt, project_id, self.template['target_id'])

        _check_during_contract(
            ctxt, [CONTRACT_KEY_FLAT_RATE, CONTRACT_KEY_PAY_FOR_USE],
            project_id, 'Pay-for-use')

        self._input_contract_quotas_check(ctxt, project_id, **values)

    def _input_contract_quotas_check(self, ctxt, project_id, **values):
        """Value to the contract at the time of contract changes
        will check whether or not less than the amount used in the quota.
        """
        # Get ticket detail.
        if not self.before_status_code:
            ticket_detail = values['ticket_detail']
        else:
            ticket = db_api.tickets_get(ctxt, values['id'])
            ticket_detail = json.loads(ticket.ticket_detail)

        # Get catalog data.
        catalog_data = self._get_catalog_data(ctxt, ticket_detail)

        nova = broker_utils.get_nova_client()
        nova_limits = nova.limits.get(tenant_id=project_id)

        cinder = broker_utils.get_cinder_client()
        cinder_quotas_usage = cinder.quotas.get(project_id, usage=True)
        cinder_in_use = long(cinder_quotas_usage.gigabytes['in_use'])

        for quota_key, catalog in six.iteritems(catalog_data):
            if quota_key not in broker_utils.NOVA_LIMIT_USED_KEYS \
                    and quota_key not in broker_utils.CINDER_LIMIT_USED_KEYS:
                continue

            contract_size = long(
                catalog['contract_quota_num']) * long(catalog['goods_num'])
            if quota_key in broker_utils.UNIT_CONVERSION:
                contract_size = contract_size * broker_utils. \
                    UNIT_CONVERSION[quota_key][catalog['unit']]

            if quota_key in broker_utils.CINDER_QUOTAS:
                use_size = cinder_in_use
            else:
                limit_key = broker_utils.NOVA_LIMIT_USED_KEYS[quota_key]
                use_size = long(nova_limits.to_dict()['absolute'][limit_key])
            if contract_size < use_size:
                error_message = _LE(
                    'The value of the contract changes '
                    'have been lower than the current usage. '
                    '%(quota_key)s: '
                    'contract=%(contract_size)s, use=%(use_size)s') % {
                        'quota_key': quota_key,
                        'contract_size': contract_size,
                        'use_size': use_size}
                raise InvalidStatus(error_message)

    def _get_catalog_data(self, context, ticket_detail):
        catalog_id_list = self.template['target_id']
        catalog_key_list = self.template['target_key']
        catalog_data = {}
        for (catalog_id, catalog_key) in zip(
                catalog_id_list, catalog_key_list):
            catalog_content = db_api.catalog_contents_list(
                context, catalog_id)[0]
            quota_key = catalog_content['expansions']['expansion_key2']
            goods_num = catalog_content['goods_num']
            unit = catalog_content['expansions']['expansion_key3']

            # Get input contract quota number.
            contract_quota_num = ticket_detail[catalog_key]

            catalog_data[quota_key] = {
                'contract_quota_num': contract_quota_num,
                'goods_num': goods_num,
                'unit': unit
            }

        return catalog_data

    def contract_data_registration(self, session, ctxt, **values):
        # Terminate current contract.
        _update_contract(ctxt, CONTRACT_KEY_PAY_FOR_USE, **values)

        ticket = db_api.tickets_get(ctxt, values['id'])
        ticket.ticket_detail = json.loads(ticket.ticket_detail)

        try:
            # Create flat-rate contract.
            contract_utils.create_contract(
                ctxt, self.template, ticket, ticket.tenant_id,
                ticket.tenant_name, ticket.owner_name, CONTRACT_KEY_FLAT_RATE)
        except Exception:
            raise NotFound(_LE('Failed to register the contract.'))

        try:
            # Update quotas.
            self._update_quotas_create(
                ctxt, ticket.tenant_id, ticket.ticket_detail)
        except Exception:
            raise NotFound(_LE('Failed to update the quotas.'))

        # Send mail.
        _send_email(self, ticket.owner_id, **values)

    def _update_quotas_create(self, ctxt, tenant_id, ticket_detail):
        # Get catalog data.
        catalog_data = self._get_catalog_data(ctxt, ticket_detail)

        nova = broker_utils.get_nova_client()
        cinder = broker_utils.get_cinder_client()

        for key, val in six.iteritems(ticket_detail):
            nova_quotas = nova.quotas.get(tenant_id)
            cinder_quotas = cinder.quotas.get(tenant_id)

            update_val = {}

            if key == 'vcpu':
                update_val[CORES] = (val * long(
                    catalog_data[CORES]['goods_num'])) + long(
                        nova_quotas.to_dict().get(CORES)) - long(
                            CONTRACT_QUOTA_VALUE[CORES])

                broker_utils.update_quotas(tenant_id, **update_val)
            elif key == 'ram':
                update_val[RAM] = (val * long(
                    catalog_data[RAM]['goods_num']) * broker_utils.
                    UNIT_CONVERSION[RAM][catalog_data[RAM]['unit']]) + \
                    long(nova_quotas.to_dict().get(RAM)) - \
                    long(CONTRACT_QUOTA_VALUE[RAM])

                broker_utils.update_quotas(tenant_id, **update_val)
            elif key == 'volume_storage':
                update_val[GIGABYTES] = (val * long(
                    catalog_data[GIGABYTES]['goods_num'])) + long(
                        cinder_quotas.gigabytes) - \
                    long(CONTRACT_QUOTA_VALUE[GIGABYTES])

                broker_utils.update_quotas(tenant_id, **update_val)


class ChangeToPayForUseContractHandler(BrokerBase):

    def param_check(self, ctxt, **values):
        self.general_param_check(**values)

    def integrity_check_for_contract_approval(self, ctxt, **values):
        """Integrity checks of the input parameters.
        Also check whether the catalog to the contract is valid.
        """
        self.general_param_check(**values)

        project_id = values['tenant_id']
        catalog_utils.is_valid_catalog(
            ctxt, project_id, self.template['target_id'])

        _check_during_contract(
            ctxt, [CONTRACT_KEY_PAY_FOR_USE, CONTRACT_KEY_FLAT_RATE],
            project_id, 'Flat-rate')

    def contract_data_registration(self, session, ctxt, **values):
        # Terminate current contract.
        _update_contract(ctxt, CONTRACT_KEY_FLAT_RATE, **values)

        ticket = db_api.tickets_get(ctxt, values['id'])
        ticket.ticket_detail = json.loads(ticket.ticket_detail)

        project_id = values['tenant_id']
        project = broker_utils.get_project(project_id)

        user_id = values['owner_id']
        user = broker_utils.get_user(user_id)

        try:
            # Create pay-for-use contract.
            contract_utils.create_contract(
                ctxt, self.template, ticket, project_id, project.name,
                user.name, CONTRACT_KEY_PAY_FOR_USE)
        except Exception:
            raise NotFound(_LE('Failed to register the contract.'))

        try:
            # Update quotas.
            self._update_quotas_value(ticket.tenant_id, CONTRACT_QUOTA_VALUE)
        except Exception:
            raise NotFound(_LE('Failed to update the quotas.'))

        # Send mail.
        _send_email(self, ticket.owner_id, **values)

    def _update_quotas_value(self, tenant_id, update_val):
        broker_utils.update_quotas(tenant_id, **update_val)


def _update_contract(ctxt, contract_key, **values):
    # Update contract.
    project_id = values['tenant_id']
    contracts = db_api.contract_list(ctxt, project_id)

    if not contracts:
        raise NotFound(_LE(
            "Contract of the project id '%s' does not exist.")) % project_id

    utcnow = datetime.datetime.utcnow()
    for contract in contracts:
        contract_type = contract['expansions']['expansion_key1']
        lifetime_end = contract['lifetime_end']
        if contract_type in contract_key and utcnow < lifetime_end:
            # Update contract.
            if isinstance(values['confirmed_at'], datetime.datetime):
                lifetime_end = values['confirmed_at'].strftime(
                    INTERNAL_UTC_DATETIME_FORMAT)
            else:
                lifetime_end = values['confirmed_at']
            contract_update_values = {'lifetime_end': lifetime_end}
            try:
                db_api.contract_update(
                    ctxt, contract['contract_id'], **contract_update_values)
            except Exception:
                raise NotFound(_LE('Failed to update the contract.'))


def _check_during_contract(
        ctxt, contract_keys, project_id, contract_name):
    if contract_utils.is_during_contract(
            ctxt, [contract_keys[0]], project_id):
        raise DuringContract()

    if not contract_utils.is_during_contract(
            ctxt, [contract_keys[1]], project_id):
        raise NotFound(
            _LE('%s contract does not exist.') % contract_name)


def _send_email(self, user_id, **values):
    if not CONF.mail.smtp_server:
        return

    email = broker_utils.get_email_address(user_id)
    broker_utils.sendmail_for_contract_registration(self, email, **values)
