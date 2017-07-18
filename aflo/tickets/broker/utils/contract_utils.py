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
import uuid

from oslo_log import log as logging

from aflo.common.exception import Conflict
from aflo.common.exception import NotFound
from aflo.db.sqlalchemy import api as db_api
from aflo import i18n
from aflo.tickets.broker.utils import utils as broker_utils

LIFETIME_END = '9999-12-31T23:59:59.999999'

LOG = logging.getLogger(__name__)

_LE = i18n._LE


def create_contract(ctxt, template, ticket, project_id, project_name,
                    application_name, contract_key, lifetime_start=None):
    """Create a new contract data
    :param ctxt: request context
    :param template: ticket template data
    :param ticket: the ticket data makes contract
    :param project_id: project id
    :param project_name: project name
    :param application_name: application_name of ticket template
    :param contract_key: contrct key which a handler has
    :param lifetime_start: optional param, set a contract lifetime end
    """
    if not lifetime_start:
        lifetime_start = broker_utils.get_now_string()

    application_date = broker_utils.get_now_string()
    template_name = broker_utils.get_display_name(
        template['ticket_template_name'])
    application_kinds_name = broker_utils.get_display_name(
        template['application_kinds_name'])

    expansion_txt = {
        'contract_info': {
            'ticket_detail': ticket.ticket_detail,
        },
        'ticket_info': {
            'cancelling_template': template.get('cancelling_template', '{}'),
            'change_template': template.get('change_template', '{}'),
        },
    }

    contract_id = str(uuid.uuid4())
    contract = {
        'contract_id': contract_id,
        'project_id': project_id,
        'project_name': project_name,
        'parent_ticket_template_id': ticket.ticket_template_id,
        'ticket_template_id': ticket.ticket_template_id,
        'parent_ticket_template_name': template_name,
        'ticket_template_name': template_name,
        'parent_application_kinds_name': application_kinds_name,
        'application_kinds_name': application_kinds_name,
        'application_id': ticket.id,
        'application_name': application_name,
        'application_date': application_date,
        'parent_contract_id': contract_id,
        'lifetime_start': lifetime_start,
        'lifetime_end': LIFETIME_END,
        'expansion_text': json.dumps(expansion_txt),
        'expansion_key1': contract_key,
    }

    db_api.contract_create(ctxt, **contract)


def is_during_contract(ctxt, contract_keys, project_id):
    """A contract to register check
    a registered contract data at the same time contract.
    :param ctxt: request context
    :param contract_keys: same type contract keys.
    :param project_id: project id
    :return True is resisterd.
    """
    contracts = db_api.contract_list(ctxt, project_id)
    utcnow = datetime.datetime.utcnow()
    for contract in contracts:
        contract_type = contract['expansions']['expansion_key1']
        lifetime_end = contract['lifetime_end']

        if contract_type in contract_keys and utcnow < lifetime_end:
            return True

    return False


def check_canceled(ctxt, **values):
    """Check a target contract cancelled.
    :param ctxt: request context
    :param values: contarct data
    """
    try:
        ticket_detail = values['ticket_detail']
    except KeyError:
        ticket = db_api.tickets_get(ctxt, values['id'])
        if not isinstance(ticket.ticket_detail, dict):
            ticket.ticket_detail = json.loads(ticket.ticket_detail)
        ticket_detail = ticket.ticket_detail

    # Get contract.
    try:
        contract = db_api.contract_get(
            ctxt, ticket_detail.get('contract_id'))
        lifetime_end = contract['lifetime_end']
    except Exception as e:
        error_message = _LE(
            'Unable to retrieve contract data. %s') % e.args[0]
        LOG.error(error_message)
        raise NotFound(error_message)

    # Project contract is already canceled.
    if lifetime_end < datetime.datetime.utcnow():
        error_message = _LE('This contract has already terminated.')
        LOG.error(error_message)
        raise Conflict(error_message)
