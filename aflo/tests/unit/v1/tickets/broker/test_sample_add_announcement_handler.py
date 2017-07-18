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

import copy
import json
import requests
import six
import six.moves.urllib.parse as urlparse
import uuid

from oslo_config import cfg
from oslo_serialization import jsonutils
from requests.exceptions import ConnectionError
from requests.exceptions import SSLError

from aflo.common.exception import NotFound
from aflo.common import mail
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy import models as db_models
from aflo.mail.add_announcement import mail_add_announcement_registration
from aflo.mail.add_announcement import mail_add_announcement_request
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests.unit.utils import FakeObject
from aflo.tests.unit.v1.tickets.broker import broker_test_base as base
from aflo.tests.unit.v1.tickets.stubs import Ticket_RpcStubs as stubs
from aflo.tickets.broker.utils import utils as broker_utils

CONF = cfg.CONF

WFP_UUID1 = str(uuid.uuid4())
TT_UUID1 = str(uuid.uuid4())

DOMAIN_ID = 'default'
TICKET_DETAIL = {'type': 'maintenance',
                 'title': 'xxxxx',
                 'language': 'en',
                 'field_maintext': 'xxxxx\nxxxxx\nxxxxx',
                 'field_workdays': '2016-06-27T00:00:00.000000',
                 'field_target': 'xxxxx\nxxxxx\nxxxxx',
                 'field_workcontent': 'xxxxx\nxxxxx\nxxxxx',
                 'field_acknowledgements': 'xxxxx\nxxxxx\nxxxxx',
                 'field_category': 'xxxxx',
                 'scope': 'project',
                 'target_name': 'xxxxx',
                 'field_tenantid': 'xxxxx',
                 'field_region': 'xxxxx',
                 'field_announcementdate': '2016-06-27T00:00:00.000000',
                 'publish_on': '2999-12-30T00:00:00.000000',
                 'unpublish_on': '2999-12-31T00:00:00.000000',
                 'message': 'xxxxx\nxxxxx\nxxxxx'}
URL = {
    'LOGIN': urlparse.urljoin(
        'https://127.0.0.1', '/xxxxx/?q=rest/xxxxx/login'),
    'CREATE_CONTENTS': urlparse.urljoin(
        'https://127.0.0.1', '/xxxxx/?q=rest/node'),
    'LOGOUT': urlparse.urljoin(
        'https://127.0.0.1', '/xxxxx/?q=rest/xxxxx/logout'),
    'GET_TAXONOMY_VOCABULARY': urlparse.urljoin(
        'https://127.0.0.1', '/xxxxx/?q=rest/xxxxx/machineName'),
    'GET_TAXONOMY_TERM': urlparse.urljoin(
        'https://127.0.0.1', '/xxxxx/?q=rest/xxxxx/getTree')
}
POST_DATA = {'name': 'admin', 'pass': 'xxxx'}
HEADERS = {'Content-type': 'application/json'}
RESPONSE_DATA = {
    'LOGIN': {
        'session_name': 'xxxxx', 'sessid': 'xxxxx', 'token': 'xxxxx'},
    'CREATE_CONTENTS': {
        'nid': 'xxxxx', 'uri': 'https://127.0.0.1/xxxxx/?q=rest/node/xxxxx'},
    'LOGOUT': {
        'nid': 'xxxxx', 'hostname': 'xxxxx',
        'roles': {'1': 'xxxxx'}, 'cache': 0},
    'GET_TAXONOMY_VOCABULARY': {
        'vid': 'xxxxx', 'name': 'xxxxx', 'machine_name': 'xxxxx'},
    'GET_TAXONOMY_TERM': [{
        'tid': 'xxxxx', 'vid': 'xxxxx', 'name': 'xxxxx'}]
}
ACTION_NAME = {
    'LOGIN': '_login',
    'CREATE_CONTENTS': '_create_contents',
    'LOGOUT': '_logout',
    'GET_TAXONOMY_VOCABULARY': '_get_taxonomy_vocabulary',
    'GET_TAXONOMY_TERM': '_get_taxonomy_term'
}
ERROR_MESSAGE = {
    'IS_NOT_FUTURE_UNPUBLISH_ON': 'Unpublish on date must be in the future.',
    'IS_NOT_FUTURE_UNPUBLISH_ON_THAN_PUBLISH_ON':
        'Unpublish on date must be later than the Publish on date.',
    'STATUS_CODE': '[400]%s response info: Status code is not 200.',
    'RAISE_NOT_FOUND_GET_PROJECT_LIST': 'Unable to retrieve project data.',
    'JSON_FORMAT': '[400]%s response info: Response format is not json.',
    'RAISE_EXCEPTION': 'Unable to %s to the announcement system.',
    'RAISE_SSL_ERROR': '%s is SSLError. %s',
    'RAISE_CONNECTION_ERROR': 'Failed to connection. URL: %s',
    'NOT_EXIST': 'category of %s does not exist.'
}
EXCEPTION_MESSAGE = 'Exception message.'


class FakeResponse(object):
    json_data = {}

    def __init__(self, **kwargs):
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    def json(self):
        return self.json_data


class Stubs(object):
    @classmethod
    def utils_stubout(cls, target, method):
        """method which method to stub out of 'aflo.tickets.broker.utils'.
        :param target: Target process.
        :param method: Called function.
        """
        call_info = {}

        def fake_get_email_address(user_id):
            call_info['user_id'] = user_id
            return user_id + '@example.com'

        def fake_error_get_email_address(user_id):
            call_info['user_id'] = user_id
            return None

        def fake_get_email_addresses_from_role(tenant, roles):
            call_info['tenant'] = tenant
            call_info['roles'] = roles
            rtn = []
            for role in roles:
                rtn.append(role + '@example.com')
            return list(set(rtn))

        def fake_get_project_list():
            project = FakeObject()
            project.setattr('id', 'xxxxx')
            project.setattr('name', 'xxxxx')
            project.setattr('domain_id', DOMAIN_ID)
            return [project]

        def fake_error_get_project_list_raise_not_found():
            raise NotFound(EXCEPTION_MESSAGE)

        fake_managers = {
            'get_email_address': {
                'method': 'get_email_address',
                'stub': fake_get_email_address},
            'error_get_email_address': {
                'method': 'get_email_address',
                'stub': fake_error_get_email_address},
            'get_email_addresses_from_role': {
                'method': 'get_email_addresses_from_role',
                'stub': fake_get_email_addresses_from_role},
            'get_project_list': {
                'method': 'get_project_list',
                'stub': fake_get_project_list},
            'error_get_project_list_raise_not_found': {
                'method': 'get_project_list',
                'stub': fake_error_get_project_list_raise_not_found},
        }
        target.stubs.Set(broker_utils, fake_managers[method]['method'],
                         fake_managers[method]['stub'])

        return call_info

    @classmethod
    def mail_stubout(cls, target, method):
        """method which method to stub out of 'aflo.tickets.broker.utils'.
        :param target: Target process.
        :param method: Called function.
        """
        call_info = {}

        def fake_sendmail(
            to_address, template, data, cc_address=None, bcc_address=None,
                encode=None, from_address=None, smtp_server=None):
            call_info['to_address'] = to_address
            call_info['template'] = template
            call_info['data'] = data

        fake_managers = {'sendmail': fake_sendmail}
        target.stubs.Set(mail, method, fake_managers[method])

        return call_info

    @classmethod
    def announcement_stubout(cls, target, method):
        """method which method to stub out of
           'aflo.tickets.broker.add_announcement_handler'.
        :param target: Target process.
        :param method: Called function.
        """
        call_info = {}

        def fake_post(url, data=None, headers=None, verify=None):
            if 'login' in url:
                return _get_login_fake_response()
            if 'node' in url:
                return _get_create_contents_fake_response()
            if 'logout' in url:
                return _get_logout_fake_response()
            if 'machineName' in url:
                return _get_taxonomy_vocabulary_fake_response()
            if 'getTree' in url:
                return _get_taxonomy_term_fake_response()

        def _get_login_fake_response():
            url = URL['LOGIN']
            headers = HEADERS
            call_info['url'] = url
            call_info['headers'] = headers
            call_info['data'] = json.dumps(POST_DATA)
            call_info['verify'] = False

            return FakeResponse(
                text='Login success.', status_code=200, headers=headers,
                json_data=RESPONSE_DATA['LOGIN'])

        def _get_create_contents_fake_response():
            url = URL['CREATE_CONTENTS']
            headers = HEADERS
            data = {}
            for key, val in TICKET_DETAIL.iteritems():
                data[key] = val
            call_info['url'] = url
            call_info['headers'] = headers
            call_info['data'] = json.dumps(data)
            call_info['verify'] = False

            return FakeResponse(
                text='Content creation success.', status_code=200,
                headers=headers, json_data=RESPONSE_DATA['CREATE_CONTENTS'])

        def _get_logout_fake_response():
            headers = HEADERS
            call_info['url'] = URL['LOGOUT']
            call_info['headers'] = headers
            call_info['verify'] = False

            return FakeResponse(
                text='Logout success.', status_code=200, headers=headers,
                json_data=RESPONSE_DATA['LOGOUT'])

        def fake_error_status_code_login_post(
                url, data=None, headers=None, verify=None):
            headers = HEADERS
            call_info['url'] = URL['LOGIN']
            call_info['headers'] = headers
            call_info['data'] = json.dumps(POST_DATA)
            call_info['verify'] = False

            return FakeResponse(
                text='Status code is not 200.', status_code=400,
                headers=headers, json_data=RESPONSE_DATA['LOGIN'])

        def _get_taxonomy_vocabulary_fake_response():
            url = URL['GET_TAXONOMY_VOCABULARY']
            headers = HEADERS
            data = {'machine_name': 'xxxxx'}
            call_info['url'] = url
            call_info['headers'] = headers
            call_info['data'] = json.dumps(data)
            call_info['verify'] = False

            return FakeResponse(
                text='Get taxonomy success.', status_code=200, headers=headers,
                json_data=RESPONSE_DATA['GET_TAXONOMY_VOCABULARY'])

        def _get_taxonomy_term_fake_response():
            url = URL['GET_TAXONOMY_TERM']
            headers = HEADERS
            data = {'vid': 'xxxxx'}
            call_info['url'] = url
            call_info['headers'] = headers
            call_info['data'] = json.dumps(data)
            call_info['verify'] = False

            return FakeResponse(
                text='Get taxonomy term success.', status_code=200,
                headers=headers, json_data=RESPONSE_DATA['GET_TAXONOMY_TERM'])

        def fake_error_response_format_is_not_json_login_post(
                url, data=None, headers=None, verify=None):
            headers = HEADERS
            call_info['url'] = URL['LOGIN']
            call_info['headers'] = headers
            call_info['data'] = json.dumps(POST_DATA)
            call_info['verify'] = False

            return FakeResponse(
                text='Response format is not json.', status_code=400,
                headers=headers, json_data='')

        def fake_error_raise_exception_login_post(
                url, data=None, headers=None, verify=None):
            raise Exception(EXCEPTION_MESSAGE)

        def fake_error_raise_ssl_error_login_post(
                url, data=None, headers=None, verify=None):
            raise SSLError(EXCEPTION_MESSAGE)

        def fake_error_raise_connection_error_login_post(
                url, data=None, headers=None, verify=None):
            raise ConnectionError(EXCEPTION_MESSAGE)

        def fake_error_vid_not_exist_get_taxonomy_vocabulary_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            else:
                url = URL['GET_TAXONOMY_VOCABULARY']
                headers = HEADERS
                data = {}
                for key, val in TICKET_DETAIL.iteritems():
                    data[key] = val
                call_info['url'] = url
                call_info['headers'] = headers
                call_info['data'] = json.dumps(data)
                call_info['verify'] = False

                return FakeResponse(
                    text='Vocabulary id does not exist.', status_code=200,
                    headers=headers, json_data={'vid': ''})

        def fake_error_status_code_get_taxonomy_vocabulary_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            else:
                url = URL['GET_TAXONOMY_VOCABULARY']
                headers = HEADERS
                data = {}
                for key, val in TICKET_DETAIL.iteritems():
                    data[key] = val
                call_info['url'] = url
                call_info['headers'] = headers
                call_info['data'] = json.dumps(data)
                call_info['verify'] = False

                return FakeResponse(
                    text='Status code is not 200.', status_code=400,
                    headers=headers,
                    json_data=RESPONSE_DATA['GET_TAXONOMY_VOCABULARY'])

        def fake_error_raise_exception_get_taxonomy_vocabulary_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            else:
                raise Exception(EXCEPTION_MESSAGE)

        def fake_error_raise_ssl_error_get_taxonomy_vocabulary_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            else:
                raise SSLError(EXCEPTION_MESSAGE)

        def fake_error_raise_connection_error_get_taxonomy_vocabulary_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            else:
                raise ConnectionError(EXCEPTION_MESSAGE)

        def fake_error_tid_not_exist_get_taxonomy_term_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            elif 0 <= url.find('machineName'):
                return _get_taxonomy_vocabulary_fake_response()
            else:
                url = URL['GET_TAXONOMY_TERM']
                headers = HEADERS
                data = {}
                for key, val in TICKET_DETAIL.iteritems():
                    data[key] = val
                call_info['url'] = url
                call_info['headers'] = headers
                call_info['data'] = json.dumps(data)
                call_info['verify'] = False

                return FakeResponse(
                    text='Taxonomy id does not exist.', status_code=200,
                    headers=headers,
                    json_data=[{'tid': '', 'name': 'category'}])

        def fake_error_status_code_get_taxonomy_term_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            elif 0 <= url.find('machineName'):
                return _get_taxonomy_vocabulary_fake_response()
            else:
                url = URL['GET_TAXONOMY_TERM']
                headers = HEADERS
                data = {}
                for key, val in TICKET_DETAIL.iteritems():
                    data[key] = val
                call_info['url'] = url
                call_info['headers'] = headers
                call_info['data'] = json.dumps(data)
                call_info['verify'] = False

                return FakeResponse(
                    text='Status code is not 200.', status_code=400,
                    headers=headers,
                    json_data=RESPONSE_DATA['GET_TAXONOMY_TERM'])

        def fake_error_raise_exception_get_taxonomy_term_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            elif 0 <= url.find('machineName'):
                return _get_taxonomy_vocabulary_fake_response()
            else:
                raise Exception(EXCEPTION_MESSAGE)

        def fake_error_raise_ssl_error_get_taxonomy_term_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            elif 0 <= url.find('machineName'):
                return _get_taxonomy_vocabulary_fake_response()
            else:
                raise SSLError(EXCEPTION_MESSAGE)

        def fake_error_raise_connection_error_get_taxonomy_term_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            elif 0 <= url.find('machineName'):
                return _get_taxonomy_vocabulary_fake_response()
            else:
                raise ConnectionError(EXCEPTION_MESSAGE)

        def fake_error_status_code_create_contents_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            elif 0 <= url.find('machineName'):
                return _get_taxonomy_vocabulary_fake_response()
            elif 0 <= url.find('getTree'):
                return _get_taxonomy_term_fake_response()
            else:
                url = URL['CREATE_CONTENTS']
                headers = HEADERS
                data = {}
                for key, val in TICKET_DETAIL.iteritems():
                    data[key] = val
                call_info['url'] = url
                call_info['headers'] = headers
                call_info['data'] = json.dumps(data)
                call_info['verify'] = False

                return FakeResponse(
                    text='Status code is not 200.', status_code=400,
                    headers=headers,
                    json_data=RESPONSE_DATA['CREATE_CONTENTS'])

        def fake_error_raise_exception_create_contents_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            elif 0 <= url.find('machineName'):
                return _get_taxonomy_vocabulary_fake_response()
            elif 0 <= url.find('getTree'):
                return _get_taxonomy_term_fake_response()
            else:
                raise Exception(EXCEPTION_MESSAGE)

        def fake_error_raise_ssl_error_create_contents_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            elif 0 <= url.find('machineName'):
                return _get_taxonomy_vocabulary_fake_response()
            elif 0 <= url.find('getTree'):
                return _get_taxonomy_term_fake_response()
            else:
                raise SSLError(EXCEPTION_MESSAGE)

        def fake_error_raise_connection_error_create_contents_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            elif 0 <= url.find('machineName'):
                return _get_taxonomy_vocabulary_fake_response()
            elif 0 <= url.find('getTree'):
                return _get_taxonomy_term_fake_response()
            else:
                raise ConnectionError(EXCEPTION_MESSAGE)

        def fake_not_error_status_code_logout_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            elif 0 <= url.find('machineName'):
                return _get_taxonomy_vocabulary_fake_response()
            elif 0 <= url.find('getTree'):
                return _get_taxonomy_term_fake_response()
            elif 0 <= url.find('node'):
                return _get_create_contents_fake_response()
            else:
                url = URL['LOGOUT']
                headers = HEADERS
                call_info['url'] = url
                call_info['headers'] = headers
                call_info['verify'] = False

                return FakeResponse(
                    text='Status code is not 200.', status_code=400,
                    headers=headers, json_data=RESPONSE_DATA['LOGOUT'])

        def fake_not_error_raise_exception_logout_post(
                url, data=None, headers=None, verify=None):
            if 0 <= url.find('login'):
                return _get_login_fake_response()
            elif 0 <= url.find('machineName'):
                return _get_taxonomy_vocabulary_fake_response()
            elif 0 <= url.find('getTree'):
                return _get_taxonomy_term_fake_response()
            elif 0 <= url.find('node'):
                return _get_create_contents_fake_response()
            else:
                raise Exception(EXCEPTION_MESSAGE)

        fake_managers = {
            'post': {'method': 'post', 'stub': fake_post},
            'error_status_code_login_post': {
                'method': 'post', 'stub': fake_error_status_code_login_post},
            'error_response_format_is_not_json_login_post': {
                'method': 'post',
                'stub': fake_error_response_format_is_not_json_login_post},
            'error_raise_exception_login_post': {
                'method': 'post',
                'stub': fake_error_raise_exception_login_post},
            'error_raise_ssl_error_login_post': {
                'method': 'post',
                'stub': fake_error_raise_ssl_error_login_post},
            'error_raise_connection_error_login_post': {
                'method': 'post',
                'stub': fake_error_raise_connection_error_login_post},
            'error_vid_not_exist_get_taxonomy_vocabulary_post': {
                'method': 'post',
                'stub': fake_error_vid_not_exist_get_taxonomy_vocabulary_post},
            'error_status_code_get_taxonomy_vocabulary_post': {
                'method': 'post',
                'stub': fake_error_status_code_get_taxonomy_vocabulary_post},
            'error_raise_exception_get_taxonomy_vocabulary_post': {
                'method': 'post',
                'stub':
                    fake_error_raise_exception_get_taxonomy_vocabulary_post},
            'error_raise_ssl_error_get_taxonomy_vocabulary_post': {
                'method': 'post',
                'stub':
                    fake_error_raise_ssl_error_get_taxonomy_vocabulary_post},
            'error_raise_connection_error_get_taxonomy_vocabulary_post': {
                'method': 'post',
                'stub':
                    fake_error_raise_connection_error_get_taxonomy_vocabulary_post},  # noqa
            'error_tid_not_exist_get_taxonomy_term_post': {
                'method': 'post',
                'stub': fake_error_tid_not_exist_get_taxonomy_term_post},
            'error_status_code_get_taxonomy_term_post': {
                'method': 'post',
                'stub': fake_error_status_code_get_taxonomy_term_post},
            'error_raise_exception_get_taxonomy_term_post': {
                'method': 'post',
                'stub': fake_error_raise_exception_get_taxonomy_term_post},
            'error_raise_ssl_error_get_taxonomy_term_post': {
                'method': 'post',
                'stub': fake_error_raise_ssl_error_get_taxonomy_term_post},
            'error_raise_connection_error_get_taxonomy_term_post': {
                'method': 'post', 'stub':
                    fake_error_raise_connection_error_get_taxonomy_term_post},
            'error_status_code_create_contents_post': {
                'method': 'post',
                'stub': fake_error_status_code_create_contents_post},
            'error_raise_exception_create_contents_post': {
                'method': 'post',
                'stub': fake_error_raise_exception_create_contents_post},
            'error_raise_ssl_error_create_contents_post': {
                'method': 'post',
                'stub': fake_error_raise_ssl_error_create_contents_post},
            'error_raise_connection_error_create_contents_post': {
                'method': 'post', 'stub':
                    fake_error_raise_connection_error_create_contents_post},
            'not_error_status_code_logout_post': {
                'method': 'post',
                'stub': fake_not_error_status_code_logout_post},
            'not_error_raise_exception_logout_post': {
                'method': 'post',
                'stub': fake_not_error_raise_exception_logout_post}}
        target.stubs.Set(requests, fake_managers[method]['method'],
                         fake_managers[method]['stub'])

        return call_info


class TestAddAnnouncementHandler(base.BrokerTestBase):
    """Do a test of 'Add Announcement'"""

    def setUp(self):
        """Establish a clean test environment."""
        super(TestAddAnnouncementHandler, self).setUp()

        self.config(announcement_url='https://127.0.0.1', group='announcement')
        self.config(
            login_url='/xxxxx/?q=rest/xxxxx/login', group='announcement')
        self.config(create_contents_url='/xxxxx/?q=rest/node',
                    group='announcement')
        self.config(
            logout_url='/xxxxx/?q=rest/xxxxx/logout', group='announcement')
        self.config(
            get_taxonomy_vocabulary_url='/xxxxx/?q=rest/xxxxx/machineName',
            group='announcement')
        self.config(get_taxonomy_term_url='/xxxxx/?q=rest/xxxxx/getTree',
                    group='announcement')
        self.config(username='admin', group='announcement')
        self.config(password='xxxx', group='announcement')
        self.config(content_type='application/json', group='announcement')
        self.config(ssl_verify=False, group='announcement')

        self.config(smtp_server='mail.example.com', group='mail')

        self.config(username='admin', group='keystone_client')
        self.config(password='xxxx', group='keystone_client')
        self.config(tenant_name='admin', group='keystone_client')
        self.config(region_name='RegionOne', group='keystone_client')
        self.config(
            auth_url='http://127.0.0.1:5000/v3', group='keystone_client')
        self.config(auth_version='3', group='keystone_client')
        self.config(user_domain_id=DOMAIN_ID, group='keystone_client')
        self.config(project_domain_id=DOMAIN_ID, group='keystone_client')

    def create_fixtures(self):
        super(TestAddAnnouncementHandler, self).create_fixtures()

        self.wf_pattern_contents = self._get_dict_contents(
            'wf_pattern_AddAnnouncement')
        self._create_workflow_pattern(
            db_models, WFP_UUID1, **self.wf_pattern_contents)

        self.template_contents = self._get_dict_contents(
            'template_contents_AddAnnouncement', '20160627')
        self._create_ticket_template(
            db_models, TT_UUID1, WFP_UUID1, **self.template_contents)

    def _make_pre_approval(self):
        """Testing of the new application"""
        # Create a request data.
        req = self._create_request_headers()
        req.body = self._create_request_body(TICKET_DETAIL)

        self._set_stubs('tickets_create')
        Stubs.announcement_stubout(self, 'post')
        Stubs.utils_stubout(self, 'get_project_list')
        Stubs.utils_stubout(self, 'get_email_address')
        Stubs.utils_stubout(self, 'get_email_addresses_from_role')
        call_info = Stubs.mail_stubout(self, 'sendmail')

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 200)
        ticket = jsonutils.loads(res.body)['ticket']

        to_address = call_info['to_address']

        self.assertTrue('O__DC1__ServiceManager@example.com' in to_address)
        self.assertEqual(call_info['template'].SUBJECT,
                         mail_add_announcement_request.SUBJECT)

        return ticket

    def _create_request_headers(self):
        path = '/tickets'
        req = unit_test_utils.get_fake_request(
            method='POST', path=path)
        headers = {'x-auth-token': 'user:tenant:_member_',
                   'x-user-name': 'user-name',
                   'x-tenant-name': 'tenant-name'}
        for (k, v) in six.iteritems(headers):
            req.headers[k] = v
        return req

    def _create_request_body(self, ticket_detail):
        body = {'ticket': {
            'ticket_template_id': TT_UUID1,
            'ticket_detail': self.serializer.to_json(ticket_detail),
            'status_code': self.template_contents['first_status_code']}}
        return self.serializer.to_json(body)

    def _update_to_final_approval(self, ticket_id):
        """Test to be approved to 'final approval'"""
        # Create a request data.
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method='PUT', path=path)
        req.body = self._create_request_data(ticket_id, req)

        self._set_stubs('tickets_update')
        Stubs.announcement_stubout(self, 'post')
        Stubs.utils_stubout(self, 'get_project_list')
        Stubs.utils_stubout(self, 'get_email_address')
        call_info = Stubs.mail_stubout(self, 'sendmail')

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 200)
        self.assertEqual(
            ', '.join(call_info['to_address']), 'user@example.com')
        self.assertEqual(call_info['template'].SUBJECT,
                         mail_add_announcement_registration.SUBJECT)

    def _create_request_data(self, ticket_id, req):
        headers = {'x-auth-token': 'admin:admin:O__DC1__ServiceManager,admin',
                   'x-user-name': 'admin-name',
                   'x-tenant-name': 'admin-tenant-name'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        session = db_api.get_session()
        last_wf = session.query(
            db_models.Workflow).filter_by(ticket_id=ticket_id).filter_by(
                status_code='pre-approval').one().id
        next_wf = session.query(db_models.Workflow).filter_by(
            ticket_id=ticket_id).filter_by(
                status_code='final approval').one().id
        additional_data = {'message': 'xxxxx\nxxxxx\nxxxxx'}
        body = {'ticket': {
            'additional_data': self.serializer.to_json(additional_data),
            'last_status_code': 'pre-approval',
            'last_workflow_id': last_wf,
            'next_status_code': 'final approval',
            'next_workflow_id': next_wf}}
        return self.serializer.to_json(body)

    def test_pre_approval_to_final_approval(self):
        """Test from a new application (pre-approval)
        until final approval.
        """
        ticket = self._make_pre_approval()
        ticket_id = ticket['id']

        self._update_to_final_approval(ticket_id)

    def test_error_unpublish_on_is_not_future(self):
        """Test unpublish on is not future"""
        self._tickets_create_error(
            '2000-01-01T00:00:00.000000', '2000-01-01T00:00:00.000000',
            ERROR_MESSAGE['IS_NOT_FUTURE_UNPUBLISH_ON'])

    def test_error_unpublish_on_is_not_future_than_publish_on(self):
        """Test unpublish on is not future than publish on"""
        self._tickets_create_error(
            '2200-01-01T00:00:00.000000', '2100-01-01T00:00:00.000000',
            ERROR_MESSAGE['IS_NOT_FUTURE_UNPUBLISH_ON_THAN_PUBLISH_ON'])

    def test_error_raise_not_found_by_get_project_list(self):
        """Test of not found"""
        self._tickets_create_error(
            '2100-01-01T00:00:00.000000', '2100-01-01T00:00:00.000000',
            ERROR_MESSAGE['RAISE_NOT_FOUND_GET_PROJECT_LIST'], True)

    def test_error_response_status_code_by_login(self):
        """Test status code of the response is not a '200'"""
        self._tickets_update_error(
            'PUT', 'error_status_code_login_post',
            ERROR_MESSAGE['STATUS_CODE'] % ACTION_NAME['LOGIN'])

    def test_error_response_format_is_not_json_by_login(self):
        """Test Response format is not a json format"""
        self._tickets_update_error(
            'PUT',
            'error_response_format_is_not_json_login_post',
            ERROR_MESSAGE['JSON_FORMAT'] % ACTION_NAME['LOGIN'])

    def test_error_raise_exception_by_login(self):
        """Test of exception"""
        self._tickets_update_error(
            'PUT', 'error_raise_exception_login_post',
            ERROR_MESSAGE['RAISE_EXCEPTION'] % ACTION_NAME['LOGIN'])

    def test_error_raise_ssl_error_by_login(self):
        """Test of ssl error"""
        self._tickets_update_error(
            'PUT', 'error_raise_ssl_error_login_post',
            ERROR_MESSAGE['RAISE_SSL_ERROR'] %
            (ACTION_NAME['LOGIN'], EXCEPTION_MESSAGE))

    def test_error_raise_connection_error_by_login(self):
        """Test of connection error"""
        self._tickets_update_error(
            'PUT', 'error_raise_connection_error_login_post',
            ERROR_MESSAGE['RAISE_CONNECTION_ERROR'] % URL['LOGIN'])

    def test_error_vid_not_exist_by_get_taxonomy_vocabulary(self):
        """Test vocabulary id dose not exist"""
        self._tickets_update_error(
            'POST', 'error_vid_not_exist_get_taxonomy_vocabulary_post',
            ERROR_MESSAGE['NOT_EXIST'] % 'vocabulary id')

    def test_error_response_status_code_by_get_taxonomy_vocabulary(self):
        """Test status code of the response is not a '200'"""
        self._tickets_update_error(
            'PUT', 'error_status_code_get_taxonomy_vocabulary_post',
            ERROR_MESSAGE['STATUS_CODE'] %
            ACTION_NAME['GET_TAXONOMY_VOCABULARY'])

    def test_error_raise_exception_by_get_taxonomy_vocabulary(self):
        """Test of exception"""
        self._tickets_update_error(
            'PUT',
            'error_raise_exception_get_taxonomy_vocabulary_post',
            ERROR_MESSAGE['RAISE_EXCEPTION'] %
            ACTION_NAME['GET_TAXONOMY_VOCABULARY'])

    def test_error_raise_ssl_error_by_get_taxonomy_vocabulary(self):
        """Test of ssl error"""
        self._tickets_update_error(
            'PUT',
            'error_raise_ssl_error_get_taxonomy_vocabulary_post',
            ERROR_MESSAGE['RAISE_SSL_ERROR'] %
            (ACTION_NAME['GET_TAXONOMY_VOCABULARY'], EXCEPTION_MESSAGE))

    def test_error_raise_connection_error_by_get_taxonomy(self):
        """Test of connection error"""
        self._tickets_update_error(
            'PUT',
            'error_raise_connection_error_get_taxonomy_vocabulary_post',
            ERROR_MESSAGE['RAISE_CONNECTION_ERROR'] %
            URL['GET_TAXONOMY_VOCABULARY'])

    def test_error_tid_not_exist_by_get_taxonomy_term(self):
        """Test taxonomy id dose not exist"""
        self._tickets_update_error(
            'POST', 'error_tid_not_exist_get_taxonomy_term_post',
            ERROR_MESSAGE['NOT_EXIST'] % 'taxonomy id')

    def test_error_response_status_code_by_get_taxonomy_term(self):
        """Test status code of the response is not a '200'"""
        self._tickets_update_error(
            'PUT', 'error_status_code_get_taxonomy_term_post',
            ERROR_MESSAGE['STATUS_CODE'] % ACTION_NAME['GET_TAXONOMY_TERM'])

    def test_error_raise_exception_by_get_taxonomy_term(self):
        """Test of exception"""
        self._tickets_update_error(
            'PUT', 'error_raise_exception_get_taxonomy_term_post',
            ERROR_MESSAGE['RAISE_EXCEPTION'] %
            ACTION_NAME['GET_TAXONOMY_TERM'])

    def test_error_raise_ssl_error_by_get_taxonomy_term(self):
        """Test of ssl error"""
        self._tickets_update_error(
            'PUT', 'error_raise_ssl_error_get_taxonomy_term_post',
            ERROR_MESSAGE['RAISE_SSL_ERROR'] %
            (ACTION_NAME['GET_TAXONOMY_TERM'], EXCEPTION_MESSAGE))

    def test_error_raise_connection_error_by_get_taxonomy_term(self):
        """Test of connection error"""
        self._tickets_update_error(
            'PUT',
            'error_raise_connection_error_get_taxonomy_term_post',
            ERROR_MESSAGE['RAISE_CONNECTION_ERROR'] % URL['GET_TAXONOMY_TERM'])

    def test_error_response_status_code_by_create_contents(self):
        """Test status code of the response is not a '200'"""
        self._tickets_update_error(
            'PUT',
            'error_status_code_create_contents_post',
            ERROR_MESSAGE['STATUS_CODE'] % ACTION_NAME['CREATE_CONTENTS'])

    def test_error_raise_exception_by_create_contents(self):
        """Test of exception"""
        self._tickets_update_error(
            'PUT',
            'error_raise_exception_create_contents_post',
            ERROR_MESSAGE['RAISE_EXCEPTION'] % ACTION_NAME['CREATE_CONTENTS'])

    def test_error_raise_ssl_error_by_create_contents(self):
        """Test of ssl error"""
        self._tickets_update_error(
            'PUT', 'error_raise_ssl_error_create_contents_post',
            ERROR_MESSAGE['RAISE_SSL_ERROR'] %
            (ACTION_NAME['CREATE_CONTENTS'], EXCEPTION_MESSAGE))

    def test_error_raise_connection_error_by_create_contents(self):
        """Test of connection error"""
        self._tickets_update_error(
            'PUT', 'error_raise_connection_error_create_contents_post',
            ERROR_MESSAGE['RAISE_CONNECTION_ERROR'] % URL['CREATE_CONTENTS'])

    def test_not_error_response_status_code_by_logout(self):
        """Test status code of the response is not a '200'
        If the logout is to continue the process.
        """
        self._tickets_update_success(
            'PUT', 'not_error_status_code_logout_post')

    def test_not_error_raise_exception_by_logout(self):
        """Test of exception
        If the logout is to continue the process.
        """
        self._tickets_update_success(
            'PUT', 'not_error_raise_exception_logout_post')

    def _tickets_update_success(self, method, fake_stub_name):
        req, req.body = self._get_make_pre_approval_request(method)

        self._set_stubs('tickets_update')
        Stubs.utils_stubout(self, 'get_project_list')
        Stubs.announcement_stubout(self, fake_stub_name)
        Stubs.utils_stubout(self, 'get_email_address')
        call_info = Stubs.mail_stubout(self, 'sendmail')

        # Send request.
        res = req.get_response(self.api)

        # Examination of response.
        self.assertEqual(res.status_int, 200)
        self.assertEqual(
            ', '.join(call_info['to_address']), 'user@example.com')
        self.assertEqual(call_info['template'].SUBJECT,
                         mail_add_announcement_registration.SUBJECT)

    def _tickets_update_error(self, method, fake_stub_name, error_message):
        req, req.body = self._get_make_pre_approval_request(method)

        self._set_stubs('tickets_update')
        Stubs.utils_stubout(self, 'get_project_list')
        Stubs.announcement_stubout(self, fake_stub_name)

        try:
            # Send request.
            req.get_response(self.api)
        except Exception as e:
            # Examination of response.
            self.assertEqual(
                e.args[0], error_message)

    def _tickets_create_error(
            self, publish_on, unpublish_on, error_message,
            get_project_list_raise_not_found_flag=False):
        # Create a request data.
        req = self._create_request_headers()

        ticket_detail = copy.deepcopy(TICKET_DETAIL)
        ticket_detail['publish_on'] = publish_on
        ticket_detail['unpublish_on'] = unpublish_on

        req.body = self._create_request_body(ticket_detail)

        self._set_stubs('tickets_create')
        if get_project_list_raise_not_found_flag:
            Stubs.announcement_stubout(self, 'post')
            Stubs.utils_stubout(self, 'error_get_project_list_raise_not_found')

        try:
            # Send request.
            req.get_response(self.api)
        except Exception as e:
            # Examination of response.
            self.assertEqual(e.args[0], error_message)

    def _get_make_pre_approval_request(self, method):
        ticket = self._make_pre_approval()
        ticket_id = ticket['id']

        # Create a request data.
        path = '/tickets/%s' % ticket_id
        req = unit_test_utils.get_fake_request(method=method, path=path)
        return req, self._create_request_data(ticket_id, req)

    def _set_stubs(self, action_name):
        # Set stubs.
        # "stub_fake_call" is a stub in order to omit the queue transmission.
        # When you use the "call_info",
        # you can confirm the call arguments of stub.
        self.stubs.UnsetAll()
        stubs.stub_fake_cast(self, action_name)
