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
import requests
import six
import six.moves.urllib.parse as urlparse
import sys

from oslo_config import cfg
from oslo_log import log as logging
from requests.exceptions import ConnectionError
from requests.exceptions import SSLError

from aflo.common.broker_base import BrokerBase
from aflo.common.exception import Forbidden
from aflo.common.exception import InvalidParameterValue
from aflo.common.exception import NotFound
from aflo.common import mail
from aflo.db.sqlalchemy import api as db_api
from aflo import i18n
from aflo.mail.add_announcement import mail_add_announcement_registration
from aflo.mail.add_announcement import mail_add_announcement_request
from aflo.tickets.broker.utils import utils as broker_utils

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

SSL_VERIFY = CONF.announcement.ssl_verify

_LE = i18n._LE
_LI = i18n._LI
_LW = i18n._LW

SCOPE_PROJECT = 'project'
SCOPE_REGION = 'region'
MACHINE_READABLE_NAME_CATEGORY = 'category'
MACHINE_READABLE_NAME_PROJECT = 'tenantid'
MACHINE_READABLE_NAME_REGION = 'region'


class AddAnnouncementHandler(BrokerBase):

    def param_check(self, ctxt, **values):
        self.general_param_check(**values)

    def integrity_check_for_add_announcement(self, ctxt, **values):
        self.general_param_check(**values)

        ticket_detail = values['ticket_detail']
        self._check_for_public(
            ticket_detail['publish_on'], ticket_detail['unpublish_on'])

        # Integrity check for announcement data.
        login_response = self._login()
        headers = self._get_headers(login_response)
        self._integrity_check_for_announcement_data(
            headers, ticket_detail['field_category'], ticket_detail['scope'],
            ticket_detail['target_name'])
        self._logout(headers)

    def _check_for_public(self, publish_on, unpublish_on):
        now = datetime.datetime.utcnow()
        datetime_publish_on = datetime.datetime.strptime(
            publish_on, '%Y-%m-%dT%H:%M:%S.%f')
        datetime_unpublish_on = datetime.datetime.strptime(
            unpublish_on, '%Y-%m-%dT%H:%M:%S.%f') + \
            datetime.timedelta(hours=24) - datetime.timedelta(seconds=1)

        if now >= datetime_unpublish_on:
            error_message = _LE('Unpublish on date must be in the future.')
            LOG.error(error_message)
            mes_param = {'value': datetime_unpublish_on,
                         'param': 'unpublish_on',
                         'extra_msg': error_message}
            raise InvalidParameterValue(**mes_param)

        if datetime_publish_on >= datetime_unpublish_on:
            error_message = _LE(
                'Unpublish on date must be later than the Publish on date.')
            LOG.error(error_message)
            raise Exception(error_message)
            mes_param = {'value': unpublish_on,
                         'param': 'unpublish_on',
                         'extra_msg': error_message}
            raise InvalidParameterValue(**mes_param)

    def _integrity_check_for_announcement_data(
            self, headers, category, scope, target_name):
        self._get_taxonomy_id(
            headers, MACHINE_READABLE_NAME_CATEGORY, category)
        if target_name:
            if scope == SCOPE_PROJECT:
                self._get_taxonomy_id(
                    headers, MACHINE_READABLE_NAME_PROJECT,
                    self._get_project_id(target_name))
            else:
                self._get_taxonomy_id(
                    headers, MACHINE_READABLE_NAME_REGION, target_name)

    def _get_project_id(self, project_name):
        try:
            project_list = broker_utils.get_project_list()
        except NotFound:
            raise NotFound(_LE('Unable to retrieve project data.'))
        project = [p for p in project_list
                   if p.name == project_name and
                   p.domain_id == CONF.keystone_client.project_domain_id]
        if project:
            return project[0].id

        # If the project can not get dealing with project name as project id.
        return project_name

    def _get_taxonomy_id(self, headers, machine_readable_name, target_name):
        if not target_name:
            return ''

        action_name = sys._getframe().f_code.co_name
        error_message = None
        taxonomy_id = ''
        try:
            taxonomy_vocabulary_response = self._get_taxonomy_vocabulary(
                headers, machine_readable_name).json()
            vocabulary_id = taxonomy_vocabulary_response.get('vid', '')
        except ValueError as ve:
            error_message = \
                'Response format is not json in %s.' % action_name
            LOG.error(_LE('%(error_message)s %(exception_message)s') % {
                'error_message': error_message,
                'exception_message': ve.args[0]})
            mes_param = {'value': target_name,
                         'param': machine_readable_name,
                         'extra_msg': error_message}
            raise InvalidParameterValue(**mes_param)
        if not vocabulary_id:
            error_message = _LE(
                '%s of vocabulary id does not exist.') % machine_readable_name
            LOG.error(error_message)
            mes_param = {'value': target_name,
                         'param': machine_readable_name,
                         'extra_msg': error_message}
            raise InvalidParameterValue(**mes_param)
        try:
            taxonomy_term_response = self._get_taxonomy_term(
                headers, vocabulary_id).json()
            for data in taxonomy_term_response:
                if data.get('name', '') == target_name:
                    taxonomy_id = data.get('tid', '')
                    break
        except ValueError as ve:
            error_message = \
                'Response format is not json in %s.' % action_name
            LOG.error(_LE('%(error_message)s %(exception_message)s') % {
                'error_message': error_message,
                'exception_message': ve.args[0]})
            mes_param = {'value': target_name,
                         'param': machine_readable_name,
                         'extra_msg': error_message}
            raise InvalidParameterValue(**mes_param)
        if not taxonomy_id:
            error_message = _LE(
                '%(machine_readable_name)s of taxonomy id does not exist. '
                'Value: %(value)s') % {
                'machine_readable_name': machine_readable_name,
                'value': target_name}
            LOG.error(error_message)
            mes_param = {'value': target_name,
                         'param': machine_readable_name,
                         'extra_msg': error_message}
            raise InvalidParameterValue(**mes_param)

        return taxonomy_id

    def _get_taxonomy_vocabulary(self, headers, machine_readable_name):
        url = urlparse.urljoin(CONF.announcement.announcement_url,
                               CONF.announcement.get_taxonomy_vocabulary_url)
        data = {'machine_name': machine_readable_name}

        return self._post(url, data, headers, sys._getframe().f_code.co_name)

    def _get_taxonomy_term(self, headers, vocabulary_id):
        url = urlparse.urljoin(CONF.announcement.announcement_url,
                               CONF.announcement.get_taxonomy_term_url)
        data = {'vid': vocabulary_id}

        return self._post(url, data, headers, sys._getframe().f_code.co_name)

    def mail_to_service_manager(self, session, *args, **values):
        if not CONF.mail.smtp_server:
            return

        next_roles = broker_utils.get_next_roles(self)
        dest_addresses = broker_utils.get_email_addresses_from_role(
            values['tenant_id'], next_roles)
        if not dest_addresses:
            return

        owner_mail = broker_utils.get_email_address(values.get('owner_id'))
        owner_mail = '(%s)' % owner_mail if owner_mail else ''

        ticket_detail = values['ticket_detail']
        data = {'id': values['id'],
                'owner_date_time': values['owner_at'],
                'owner_name': values['owner_name'],
                'owner_mail': owner_mail,
                'project_id': values['tenant_id'],
                'project_name': values['tenant_name'],
                'status': broker_utils.get_status_name(self,
                                                       self.after_status_code)
                }

        for (k, v) in six.iteritems(ticket_detail):
            data[k] = v

        mail.sendmail(dest_addresses, mail_add_announcement_request, data)

    def data_registration_for_add_announcement(self, session, ctxt, **values):
        ticket = db_api.tickets_get(ctxt, values['id'])

        if not isinstance(ticket.ticket_detail, dict):
            ticket.ticket_detail = json.loads(ticket.ticket_detail)

        # Create announcement.
        self._create_announcement(ticket.ticket_detail)

        # Send mail.
        self._mail_to_owner(session, **values)

    def _create_announcement(self, ticket_detail):
        login_response = self._login()

        headers = self._get_headers(login_response)

        self._create_contents(ticket_detail, headers)

        self._logout(headers)

    def _login(self):
        url = urlparse.urljoin(
            CONF.announcement.announcement_url, CONF.announcement.login_url)
        headers = {'Content-type': CONF.announcement.content_type}
        data = {'name': CONF.announcement.username,
                'pass': CONF.announcement.password}

        return self._post(url, data, headers, sys._getframe().f_code.co_name)

    def _get_headers(self, login_response):
        try:
            response = login_response.json()
            cookie = '%(session_name)s=%(sessid)s' % {
                'session_name': response['session_name'],
                'sessid': response['sessid']}
            headers = {
                'Content-type': CONF.announcement.content_type,
                'X-CSRF-Token': response['token'],
                'Cookie': cookie,
            }
        except ValueError as ve:
            error_message = 'Response format is not json.'
            LOG.error(_LE('%(error_message)s %(exception_message)s') % {
                'error_message': error_message,
                'exception_message': ve.args[0]})
            raise Exception(error_message)

        return headers

    def _create_contents(self, ticket_detail, headers):
        url = urlparse.urljoin(CONF.announcement.announcement_url,
                               CONF.announcement.create_contents_url)
        data = self._convert_announcement_data(ticket_detail, headers)

        self._post(url, data, headers, sys._getframe().f_code.co_name)

        LOG.info(_LI('Create contents is successful.'))

    def _logout(self, headers):
        logout_response = None
        try:
            url = urlparse.urljoin(CONF.announcement.announcement_url,
                                   CONF.announcement.logout_url)
            logout_response = requests.post(
                url, headers=headers, verify=SSL_VERIFY)
        except Exception as e:
            # If you fail to logout, workflow is a success.
            LOG.warning(_LW(
                'Unable to Logout to the announcement system. %s') %
                e.args[0])

        if logout_response and logout_response.status_code is not 200:
            # If you fail to logout, workflow is a success.
            LOG.warning(_LW('[%(status_code)d]'
                            'Logout response info: %(error_message)s') % {
                'status_code': logout_response.status_code,
                'error_message': logout_response.text})

    def _mail_to_owner(self, session, **values):
        if not CONF.mail.smtp_server:
            return

        owner_mail = broker_utils.get_email_address(values.get('owner_id'))
        if not owner_mail:
            return
        addresses = [owner_mail]

        ticket = db_api._ticket_get(self.ctxt, values['id'], session)
        ticket_detail = ticket.ticket_detail
        if ticket_detail and not isinstance(ticket_detail, dict):
            ticket_detail = json.loads(ticket_detail)

        data = {'id': values['id'],
                'update_date_time': values['confirmed_at'],
                'update_user': values['confirmer_name'],
                'project_id': values['tenant_id'],
                'project_name': values['tenant_name'],
                'message': values['additional_data'].get('message', ''),
                'status': broker_utils.get_status_name(self,
                                                       self.after_status_code)
                }

        for (k, v) in six.iteritems(ticket_detail):
            if k == 'message':
                continue
            data[k] = v

        mail.sendmail(addresses, mail_add_announcement_registration, data)

    def _post(self, url, data, headers, action_name):
        error_message = None
        exception_message = None
        try:
            response = requests.post(
                url, data=json.dumps(data), headers=headers, verify=SSL_VERIFY)
        except SSLError as se:
            exception_message = se.args[0]
            error_message = _LE('%(name)s is SSLError. '
                                '%(exception_message)s') % {
                'name': action_name, 'exception_message': exception_message}
            raise Forbidden(error_message)
        except ConnectionError as ce:
            error_message = _LE('Failed to connection. URL: %s') % url
            exception_message = ce.args[0]
            raise Forbidden(error_message)
        except Exception as e:
            if not error_message:
                error_message = \
                    'Unable to %s to the announcement system.' % action_name
                exception_message = e.args[0]
            LOG.error(_LE('%(error_message)s %(exception_message)s') % {
                'error_message': error_message,
                'exception_message': exception_message})
            raise Forbidden(error_message)

        if response.status_code is not 200:
            error_message = _LE('[%(status_code)d]%(name)s response info: '
                                '%(error_message)s') % {
                                    'status_code': response.status_code,
                                    'name': action_name,
                                    'error_message': response.text}
            LOG.error(error_message)
            raise Forbidden(error_message)

        return response

    def _convert_announcement_data(self, ticket_detail, headers):
        data = ['type', 'title', 'language']
        und_data = ['field_maintext', 'field_target', 'field_workcontent',
                    'field_acknowledgements']
        und_date_data = ['field_workdays', 'field_announcementdate']
        return_data = {}
        for (k, v) in six.iteritems(ticket_detail):
            if k in data:
                return_data[k] = v
            elif k in und_data:
                return_data[k] = {'und': [{'value': v}]}
            elif k in und_date_data:
                return_data[k] = {'und': [{'value': {
                    'date': self._convert_datetime_to_date(v)}}]}
            elif 'scope' == k:
                scope = v
            elif 'target_name' == k:
                target_name = v
            elif 'publish_on' == k:
                return_data[k] = self._create_publish_on(v)
            elif 'unpublish_on' == k:
                return_data[k] = self._create_unpublish_on(v)
            elif 'field_category' == k:
                return_data[k] = {'und': {'tid': self._get_taxonomy_id(
                    headers, MACHINE_READABLE_NAME_CATEGORY, v)}}
        if scope == SCOPE_PROJECT:
            taxonomy_id = self._get_taxonomy_id(
                headers, MACHINE_READABLE_NAME_PROJECT,
                self._get_project_id(target_name))
            if taxonomy_id:
                return_data['field_tenantid'] = {'und': {'tid': taxonomy_id}}
        else:
            taxonomy_id = self._get_taxonomy_id(
                headers, MACHINE_READABLE_NAME_REGION, target_name)
            if taxonomy_id:
                return_data['field_region'] = {'und': {'tid': taxonomy_id}}

        return return_data

    def _create_publish_on(self, publish_on):
        return datetime.datetime.strptime(
            publish_on, '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S')

    def _create_unpublish_on(self, unpublish_on):
        datetime_unpublish_on = datetime.datetime.strptime(
            unpublish_on, '%Y-%m-%dT%H:%M:%S.%f') + \
            datetime.timedelta(hours=24) - datetime.timedelta(seconds=1)

        return datetime_unpublish_on.strftime('%Y-%m-%d %H:%M:%S')

    def _convert_datetime_to_date(self, string_datetime):
        return datetime.datetime.strptime(
            string_datetime, '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%d')
