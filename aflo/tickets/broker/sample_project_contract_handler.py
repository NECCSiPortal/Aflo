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
from aflo.common.exception import Conflict
from aflo.common.exception import Invalid
from aflo.common.exception import NotFound
from aflo.common import mail
from aflo.db.sqlalchemy import api as db_api
from aflo import i18n
from aflo.mail.project_contract \
    import mail_cancel_project_contract_final_approval
from aflo.mail.project_contract import mail_project_contract_accept
from aflo.tickets.broker.utils import contract_utils
from aflo.tickets.broker.utils import utils as broker_utils

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

_LE = i18n._LE

INTERNAL_UTC_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
LAST_WORKFLOW_STATUS_CODE = 1
NO_LIMIT_DATE = '9999-12-31'
CONTRACT_KEY = 'contract-basic-project'


class ProjectContractHandler(BrokerBase):

    def integrity_check_for_project_contract(self, ctxt, **values):
        self.general_param_check(**values)
        self.check_unique(ctxt, **values)

    def integrity_check_for_project_contract_done(self, ctxt, **values):
        self.general_param_check(**values)
        self.check_presence(ctxt, **values)

    def check_unique(self, ctxt, **values):
        try:
            # Get ticket detail.
            ticket_detail = values['ticket_detail']
        except KeyError:
            ticket = db_api.tickets_get(ctxt, values['id'])
            if not isinstance(ticket.ticket_detail, dict):
                ticket.ticket_detail = json.loads(ticket.ticket_detail)
            ticket_detail = ticket.ticket_detail
        try:
            # Get user list.
            user_name = ticket_detail.get('user_name')
            users = broker_utils.get_user_list()
        except Exception as e:
            error_message = _LE(
                'Unable to retrieve user list. %s') % e.args[0]
            LOG.error(error_message)
            raise NotFound(error_message)

        for user in users:
            if user_name == user.name:
                # User name is conflict.
                error_message = _LE(
                    'User name %s is already used.') % user_name
                LOG.error(error_message)
                raise Conflict(error_message)

        try:
            # Get project list.
            project_name = ticket_detail.get('project_name')
            projects = broker_utils.get_project_list()
        except Exception as e:
            error_message = _LE(
                'Unable to retrieve project list. %s') % e.args[0]
            LOG.error(error_message)
            raise NotFound(error_message)

        for project in projects:
            if project_name == project.name:
                # Project name is conflict.
                error_message = _LE(
                    'Project name %s is already used.') % project_name
                LOG.error(error_message)
                raise Conflict(error_message)

    def check_presence(self, ctxt, **values):
        try:
            # Get user data.
            ticket_detail = values['additional_data']
            user_id = ticket_detail.get('user_id')
            user = broker_utils.get_user(user_id)
        except Exception as e:
            error_message = _LE(
                'Unable to retrieve user data. %s') % e.args[0]
            LOG.error(error_message)
            raise NotFound(error_message)

        if not user:
            # Update data is invalid.
            error_message = _LE(
                '%s of the user ID does not exist.') % user_id
            LOG.error(error_message)
            raise Invalid(error_message)

        try:
            # Get project data.
            project_id = ticket_detail.get('project_id')
            project = broker_utils.get_project(project_id)
        except Exception as e:
            error_message = _LE(
                'Unable to retrieve project data. %s') % e.args[0]
            LOG.error(error_message)
            raise NotFound(error_message)

        if not project:
            # Update data is invalid.
            error_message = _LE(
                '%s of the project ID does not exist.') % project_id
            LOG.error(error_message)
            raise Invalid(error_message)

    def mail_to_contract_manager(self, session, *args, **values):
        if not CONF.mail.smtp_server:
            return

        try:
            ticket_detail = values['ticket_detail']
            owner_mail = ticket_detail.get('email')
            owner_mail = '(%s)' % owner_mail if owner_mail else ''

            next_roles = broker_utils.get_next_roles(self)
            project_id = CONF.keystone_client.tenant_id
            dest_addresses = broker_utils.get_email_addresses_from_role(
                project_id, next_roles)
        except Exception as e:
            error_message = _LE(
                'Unable to retrieve email address. %s') % e.args[0]
            LOG.error(error_message)
            raise NotFound(error_message)

        if not dest_addresses:
            # No destination.
            error_message = _LE(
                'E-mail address has not been set in the contract manager.')
            LOG.error(error_message)
            raise NotFound(error_message)

        status_code = self.after_status_code
        data = {'id': values['id'],
                'project_name': ticket_detail.get('project_name'),
                'user_name': ticket_detail.get('user_name'),
                'mail': owner_mail,
                'preferred_date': ticket_detail.get('preferred_date'),
                'message': ticket_detail.get('message', ''),
                'status': broker_utils.get_status_name(self, status_code)
                }
        mail.sendmail(dest_addresses, mail_project_contract_accept, data)

    def create_project_contract(self, session, ctxt, **values):
        try:
            ticket = db_api.tickets_get(ctxt, values['id'])
            if not isinstance(ticket.ticket_detail, dict):
                ticket.ticket_detail = json.loads(ticket.ticket_detail)
            # Create contract.
            self._create_project_contract(ctxt, ticket, **values)
        except Exception as e:
            error_message = _LE(
                'Failed to register the project contract. %s') % e.args[0]
            LOG.error(error_message)
            raise NotFound(error_message)

    def _create_project_contract(self, ctxt, ticket, **values):
        join_date = values['additional_data'].get('join_date')
        project_id = values['additional_data'].get('project_id')
        project = broker_utils.get_project(project_id)
        user_id = values['additional_data'].get('user_id')
        user = broker_utils.get_user(user_id)

        contract_utils.create_contract(
            ctxt, self.template, ticket, project_id, project.name,
            user.name, CONTRACT_KEY, lifetime_start=join_date)

    def integrity_check_for_cancel_project_contract(self, ctxt, **values):
        self.general_param_check(**values)

        try:
            # Get ticket detail.
            ticket_detail = values['ticket_detail']
        except KeyError:
            ticket = db_api.tickets_get(ctxt, values['id'])
            if not isinstance(ticket.ticket_detail, dict):
                ticket.ticket_detail = json.loads(ticket.ticket_detail)
            ticket_detail = ticket.ticket_detail

        try:
            # Get contract.
            contract = db_api.contract_get(
                ctxt, ticket_detail.get('contract_id'))
        except Exception as e:
            error_message = _LE(
                'Unable to retrieve contract data. %s') % e.args[0]
            LOG.error(error_message)
            raise NotFound(error_message)

        self.check_has_child_project(ctxt, contract, **values)
        self.check_canceled(ctxt, contract, **values)

    def check_has_child_project(self, ctxt, contract, **values):
        try:
            # Get workflow list.
            workflow_list = db_api.workflow_list(
                ctxt, contract['application_id'], LAST_WORKFLOW_STATUS_CODE)
        except Exception as e:
            error_message = _LE(
                'Unable to retrieve workflow data. %s') % e.args[0]
            LOG.error(error_message)
            raise NotFound(error_message)

        if not workflow_list:
            error_message = _LE('Unable to retrieve workflow data.')
            LOG.error(error_message)
            raise NotFound(error_message)

        try:
            # Get child projects.
            projects = broker_utils.get_child_project_list(json.loads(
                workflow_list[0].additional_data).get('project_id'))
        except Exception as e:
            error_message = _LE(
                'Unable to retrieve project data. %s') % e.args[0]
            LOG.error(error_message)
            raise NotFound(error_message)

        if projects:
            # Presence child projects.
            error_message = _LE('Child project exists.')
            LOG.error(error_message)
            raise Conflict(error_message)

    def check_canceled(self, ctxt, contract, **values):
        if NO_LIMIT_DATE not in contract['lifetime_end'].strftime('%Y-%m-%d'):
            # Project contract is already canceled.
            error_message = _LE('It is canceled of contract.')
            LOG.error(error_message)
            raise Conflict(error_message)

    def create_cancel_project_contract(self, session, ctxt, **values):
        try:
            ticket = db_api.tickets_get(ctxt, values['id'])
            ticket_detail = ticket.ticket_detail
            if not isinstance(ticket_detail, dict):
                ticket_detail = json.loads(ticket_detail)
            contract_id = str(ticket_detail['contract_id'])

            date_withdrawal_date = datetime.datetime.strptime(
                values['additional_data'].get(
                    'withdrawal_date'), INTERNAL_UTC_DATETIME_FORMAT)
            date_withdrawal_date = date_withdrawal_date + datetime.timedelta(
                hours=24) - datetime.timedelta(seconds=1)
            withdrawal_date = date_withdrawal_date.strftime(
                INTERNAL_UTC_DATETIME_FORMAT)

            contract_update_values = {
                'lifetime_end': withdrawal_date}
            db_api.contract_update(ctxt, contract_id, **contract_update_values)
        except Exception as e:
            error_message = _LE(
                'Failed to register the project contract. %s') % e.args[0]
            LOG.error(error_message)
            raise NotFound(error_message)

        # Send mail.
        if not CONF.mail.smtp_server:
            return

        to_address = broker_utils.get_email_address(ticket.owner_id)
        if not to_address:
            return

        data = {'id': values['id'],
                'user': values["confirmer_name"],
                'update_date': values['confirmed_at'],
                'withdrawal_date': withdrawal_date,
                'message': values['additional_data'].get('message', ''),
                'status': broker_utils.get_status_name(
                    self, values['after_status_code'])
                }
        mail.sendmail(
            to_address, mail_cancel_project_contract_final_approval, data)
