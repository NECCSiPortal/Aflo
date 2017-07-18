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

from oslo_config import cfg
from oslo_log import log as logging

from aflo.common.broker_base import BrokerBase
from aflo.common.exception import BrokerError
from aflo.common.exception import DuringContract
from aflo.common.exception import InvalidStatus
from aflo.common.exception import NotFound
from aflo.db.sqlalchemy import api as db_api
from aflo.tickets.broker.utils import catalog_utils
from aflo.tickets.broker.utils import contract_utils
from aflo.tickets.broker.utils import utils as broker_utils

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

CONTRACT_GROUP_KEYS = ['contract-pay-for-use', ]
CONTRACT_KEY = 'contract-flat-rate'


class SampleSetCatalogBroker(BrokerBase):
    """This source is a sample to learn how to create a broker.
    The following methods are provided.

    -------------------- header --------------------
    operation
        trigger
            before/after
                processing type :method name
    ------------------------------------------------
    New application
        the time of application
            before
                validation      :param_check
                broker_method   :integrity_check_for_purchase_contract
        final approval at the time
            before
                broker_method   :integrity_check_for_purchase_contract
            after
                broker_method   :
                      contract_data_registration_for_purchase_contract

    Cancellation application
        the time of application
            before
                validation      :integrity_check_for_cancellation
        final approval at the time
            before
                validation      :integrity_check_for_cancellation
            after
                broker_method   :contract_data_registration_for_cancellation
    """

    def param_check(self, ctxt, **values):
        self.general_param_check(**values)

    def integrity_check_for_purchase_contract(self, session,
                                              ctxt, **values):

        # You must write it in a handler here
        # if a check is necessary.
        pass

    def integrity_check_for_purchase_contract_pre_approval(self,
                                                           ctxt,
                                                           **values):
        self.general_param_check(**values)
        self.valid_catalog_check(ctxt, **values)
        if contract_utils.is_during_contract(
                ctxt, CONTRACT_GROUP_KEYS, values['tenant_id']):
            raise DuringContract()

    def integrity_check_for_purchase_contract_final_approval(self,
                                                             ctxt,
                                                             **values):
        self.general_param_check(**values)
        self.valid_catalog_check(ctxt, **values)
        if contract_utils.is_during_contract(
                ctxt, CONTRACT_GROUP_KEYS, values['tenant_id']):
            raise DuringContract()

    def valid_catalog_check(self, ctxt, **values):
        catalog_utils.is_valid_catalog(
            ctxt, values['tenant_id'], self.template['target_id'])

    def contract_data_registration_for_purchase_contract(self, session,
                                                         ctxt, **values):
        ticket = db_api.tickets_get(ctxt, values['id'])

        if not isinstance(ticket.ticket_detail, dict):
            ticket.ticket_detail = json.loads(ticket.ticket_detail)

        # create_contract
        contract_utils.create_contract(
            ctxt, self.template, ticket, ticket.tenant_id, ticket.tenant_name,
            ticket.owner_name, CONTRACT_KEY)

        # update quotas
        self._update_quotas_create(tenant_id=ticket.tenant_id,
                                   ticket_detail=ticket.ticket_detail)

        # send mail
        email = broker_utils.get_email_address(ticket.owner_id)
        broker_utils.sendmail_for_contract_registration(self, email, **values)

    def integrity_check_for_cancellation(self, ctxt, **values):
        contract_utils.check_canceled(ctxt, **values)

        try:
            ticket = db_api.tickets_get(ctxt, values['id'])
            tenant_id = ticket.tenant_id
            ticket_detail = ticket.ticket_detail
            self.general_param_check(**values)
        except NotFound:
            self.general_param_check(**values)
            tenant_id = values['tenant_id']
            ticket_detail = values['ticket_detail']

        if not isinstance(ticket_detail, dict):
            ticket_detail = json.loads(ticket_detail)

        contract_id = str(ticket_detail['contract_id'])

        # get contract
        catalog_data = self._get_catalog_data(ctxt, contract_id)

        nova = broker_utils.get_nova_client()
        nova_quotas = nova.quotas.get(tenant_id)
        nova_limits = nova.limits.get(tenant_id=tenant_id)

        cinder = broker_utils.get_cinder_client()
        cinder_quotas_usage = cinder.quotas.get(tenant_id, usage=True)
        cinder_limit = long(cinder_quotas_usage.gigabytes['limit'])
        cinder_in_use = long(cinder_quotas_usage.gigabytes['in_use'])

        for quota_key, info in catalog_data.iteritems():
            if quota_key not in broker_utils.NOVA_LIMIT_USED_KEYS \
                    and quota_key not in broker_utils.CINDER_LIMIT_USED_KEYS:
                continue

            cont_size = long(info['cont_num']) * long(info['goods_num'])
            if quota_key in broker_utils.UNIT_CONVERSION:
                cont_size = cont_size * \
                    broker_utils.\
                    UNIT_CONVERSION[quota_key][info['unit']]

            if quota_key in broker_utils.CINDER_QUOTAS:
                after_size = cinder_limit - cont_size
                use_size = cinder_in_use
            else:
                limit_key = broker_utils.NOVA_LIMIT_USED_KEYS[quota_key]
                after_size = \
                    long(nova_quotas.to_dict().get(quota_key)) - cont_size
                use_size = long(nova_limits.to_dict()['absolute'][limit_key])
            if after_size < use_size:
                msg = 'Value after the termination is '\
                      'the less than the value in use.'\
                      ' %s: after=%s, use=%s' % (quota_key,
                                                 after_size, use_size)
                raise InvalidStatus(msg)

    def contract_data_registration_for_cancellation(self, session,
                                                    ctxt, **values):
        ticket = db_api.tickets_get(ctxt, values['id'])
        tenant_id = ticket.tenant_id
        ticket_detail = ticket.ticket_detail
        if not isinstance(ticket_detail, dict):
            ticket_detail = json.loads(ticket_detail)
        contract_id = str(ticket_detail['contract_id'])

        catalog_data = self._get_catalog_data(ctxt, contract_id)

        # update quotas
        nova = broker_utils.get_nova_client()
        nova_quotas = nova.quotas.get(tenant_id)
        cinder = broker_utils.get_cinder_client()
        cinder_quotas = cinder.quotas.get(tenant_id)

        update_val = {}
        for quota_key, info in catalog_data.iteritems():
            cont_size = long(info['cont_num']) * long(info['goods_num'])
            if quota_key in broker_utils.UNIT_CONVERSION:
                cont_size = cont_size * \
                    broker_utils.\
                    UNIT_CONVERSION[quota_key][info['unit']]

            if quota_key in broker_utils.NOVA_QUOTAS:
                after_size = \
                    long(nova_quotas.to_dict().get(quota_key)) - cont_size

            elif quota_key in broker_utils.CINDER_QUOTAS:
                if 'gigabytes' == quota_key:
                    after_size = \
                        long(cinder_quotas.gigabytes) - cont_size
            else:
                continue

            update_val[quota_key] = after_size

        broker_utils.update_quotas(tenant_id, **update_val)

        # update contract
        if isinstance(values['confirmed_at'], datetime.datetime):
            lifetime_end = \
                values['confirmed_at'].strftime('%Y-%m-%dT%H:%M:%S.%f')
        else:
            lifetime_end = values['confirmed_at']
        contract_update_vals = {'lifetime_end': lifetime_end}
        db_api.contract_update(ctxt, contract_id, **contract_update_vals)

        # send mail
        email = broker_utils.get_email_address(ticket.owner_id)
        broker_utils.sendmail_for_contract_registration(self, email, **values)

    def _get_catalog_data(self, context, old_contract_id):
        old_contract = db_api.contract_get(context, old_contract_id)
        old_expansion_text = old_contract['expansions_text']['expansion_text']
        if not isinstance(old_expansion_text, dict):
            old_ticket_detail = json.loads(old_expansion_text). \
                get('contract_info').get('ticket_detail')
        else:
            old_ticket_detail = old_expansion_text. \
                get('contract_info').get('ticket_detail')

        catalog_id_list = self.template['target_id']
        catalog_key_list = self.template['target_key']
        catalog_data = {}
        for (catalog_id, catalog_key) in zip(catalog_id_list,
                                             catalog_key_list):
            catalog = db_api.catalog_get(context, catalog_id)
            name = catalog['catalog_name']

            catalog_content = \
                db_api.catalog_contents_list(context, catalog_id)[0]
            nova_key = catalog_content['expansions']['expansion_key2']
            goods_num = catalog_content['goods_num']
            unit = catalog_content['expansions']['expansion_key3']

            cont_num = old_ticket_detail[catalog_key]

            catalog_data[nova_key] = {'name': name,
                                      'nova_key': nova_key,
                                      'cont_num': cont_num,
                                      'goods_num': goods_num,
                                      'unit': unit}

        return catalog_data

    def _get_contract(self, ctxt, application_id, **values):

        def _send_mail():
            email = broker_utils.get_email_address(values["confirmer_id"])
            location = 'Presence check of contract'
            cause = 'Valid contract does not exist'
            broker_utils.sendmail_for_contract_error(email, location,
                                                     cause, **values)
            raise BrokerError({'location': location, 'cause': cause})

        contracts = db_api.contract_list(ctxt, application_id=application_id)
        if not contracts or 0 == len(contracts):
            _send_mail()
        contract = contracts[0]

        if 'cancellation' == contract['status']:
            _send_mail()

        if not (contract['lifetime_start'] <= values['confirmed_at'] and
                values['confirmed_at'] <= contract['lifetime_end']):
            _send_mail()

        return contract

    def _check_capacity(self, tenant_id, buy_num_new=0, buy_num_old=0):
        nova = broker_utils.get_nova_client()
        nova_quotas = nova.quotas.get(tenant_id)
        nova_limits = nova.limits.get(tenant_id=tenant_id)

        catalog_contents = broker_utils.\
            get_catalog_contents_data(self.ctxt, self.template['target_id'])

        for key, val in catalog_contents.iteritems():
            if key not in broker_utils.NOVA_LIMIT_USED_KEYS:
                continue

            limit_key = broker_utils.NOVA_LIMIT_USED_KEYS[key]
            after_size = long(nova_quotas.to_dict().get(key)) + \
                (buy_num_new * val) - (buy_num_old * val)
            use_size = long(nova_limits.to_dict()['absolute'][limit_key])
            if after_size < use_size:
                return False

        return True

    def _update_quotas_create(self, tenant_id, ticket_detail):

        nova = broker_utils.get_nova_client()
        cinder = broker_utils.get_cinder_client()

        for key, val in ticket_detail.iteritems():

            nova_quotas = nova.quotas.get(tenant_id)
            cinder_quotas = cinder.quotas.get(tenant_id)

            update_val = {}

            if key == 'vcpu':
                update_val['cores'] = \
                    (val * 10) + \
                    long(nova_quotas.to_dict().get('cores'))

                broker_utils.update_quotas(tenant_id, **update_val)

            elif key == 'ram':
                update_val['ram'] = \
                    (val * (20 * 1024)) + \
                    long(nova_quotas.to_dict().get('ram'))

                broker_utils.update_quotas(tenant_id, **update_val)

            elif key == 'volume_storage':
                update_val['gigabytes'] = \
                    (val * 50) + \
                    long(cinder_quotas.gigabytes)

                broker_utils.update_quotas(tenant_id, **update_val)
