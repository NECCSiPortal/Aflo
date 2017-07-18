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

from datetime import datetime
from oslo_config import cfg
from oslo_serialization import jsonutils
import routes

from aflo.api.v1 import router
from aflo.common import wsgi
from aflo import context
from aflo import db
from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF
db_api = db.get_api()

CONTRACT_ID_101 = 'ea0a4146-fd07-414b-aa5e-dedbeef00101'
CONTRACT_ID_102 = 'ea0a4146-fd07-414b-aa5e-dedbeef00102'
CONTRACT_ID_103 = 'ea0a4146-fd07-414b-aa5e-dedbeef00103'
CONTRACT_ID_104 = 'ea0a4146-fd07-414b-aa5e-dedbeef00104'
CONTRACT_ID_105 = 'ea0a4146-fd07-414b-aa5e-dedbeef00105'
CONTRACT_ID_106 = 'ea0a4146-fd07-414b-aa5e-dedbeef00106'
CONTRACT_ID_107 = 'ea0a4146-fd07-414b-aa5e-dedbeef00107'
CONTRACT_ID_108 = 'ea0a4146-fd07-414b-aa5e-dedbeef00108'


def get_datetime(str_date):
    """Get datetime.
        :param str_date: String of date.
    """
    return datetime.strptime(str_date + 'T00:00:00.000000',
                             '%Y-%m-%dT%H:%M:%S.%f')


class TestAPI(base.IsolatedUnitTest):
    def setUp(self):
        """Establish a clean test environment"""
        super(TestAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        db_cre = db_models.Contract
        db_cre(contract_id=CONTRACT_ID_101,
               region_id='region_id_101',
               project_id='project_id_101',
               project_name='project_name_101',
               catalog_id='catalog_id_101',
               catalog_name='catalog_name_101',
               num=101,
               parent_ticket_template_id='parent_ticket_template_id_101',
               ticket_template_id='ticket_template_id_101',
               parent_ticket_template_name='parent_ticket_template_name_101',
               parent_application_kinds_name='par_application_kinds_name_101',
               application_kinds_name='application_kinds_name_101',
               cancel_application_id='cancel_application_id_101',
               application_id='application_id_101',
               ticket_template_name='ticket_template_name_101',
               application_name='application_name_101',
               application_date=get_datetime('2015-05-01'),
               parent_contract_id='parent_contract_id_101',
               lifetime_start=get_datetime('2015-07-01'),
               lifetime_end=get_datetime('2015-08-01'),
               deleted=False
               ).save(db_api.get_session())

        db_cre(contract_id=CONTRACT_ID_102,
               region_id='region_id_101',
               project_id='project_id_101',
               project_name='project_name_101',
               catalog_id='catalog_id_102',
               catalog_name='catalog_name_102',
               num=102,
               parent_ticket_template_id='parent_ticket_template_id_102',
               ticket_template_id='ticket_template_id_102',
               parent_ticket_template_name='parent_ticket_template_name_102',
               parent_application_kinds_name='par_application_kinds_name_102',
               application_kinds_name='application_kinds_name_102',
               cancel_application_id='cancel_application_id_102',
               application_id='application_id_102',
               ticket_template_name='ticket_template_name_101',
               application_name='application_name_102',
               application_date=get_datetime('2015-05-02'),
               parent_contract_id='parent_contract_id_102',
               lifetime_start=get_datetime('2015-07-02'),
               lifetime_end=get_datetime('2015-08-02'),
               deleted=False
               ).save(db_api.get_session())

        db_cre(contract_id=CONTRACT_ID_103,
               region_id='region_id_101',
               project_id='project_id_101',
               project_name='project_name_101',
               catalog_id='catalog_id_103',
               catalog_name='catalog_name_103',
               num=103,
               parent_ticket_template_id='parent_ticket_template_id_103',
               ticket_template_id='ticket_template_id_103',
               parent_ticket_template_name='parent_ticket_template_name_103',
               parent_application_kinds_name='par_application_kinds_name_103',
               application_kinds_name='application_kinds_name_103',
               cancel_application_id='cancel_application_id_103',
               application_id='application_id_103',
               ticket_template_name='ticket_template_name_101',
               application_name='application_name_101',
               application_date=get_datetime('2015-05-02'),
               parent_contract_id='parent_contract_id_103',
               lifetime_start=get_datetime('2015-07-03'),
               lifetime_end=get_datetime('2015-08-03'),
               deleted=False
               ).save(db_api.get_session())

        db_cre(contract_id=CONTRACT_ID_104,
               region_id='region_id_101',
               project_id='project_id_101',
               project_name='project_name_101',
               catalog_id='catalog_id_104',
               catalog_name='catalog_name_104',
               num=104,
               parent_ticket_template_id='parent_ticket_template_id_104',
               ticket_template_id='ticket_template_id_104',
               parent_ticket_template_name='parent_ticket_template_name_104',
               parent_application_kinds_name='par_application_kinds_name_104',
               application_kinds_name='application_kinds_name_104',
               cancel_application_id='cancel_application_id_104',
               application_id='application_id_104',
               ticket_template_name='ticket_template_name_102',
               application_name='application_name_101',
               application_date=get_datetime('2015-05-01'),
               parent_contract_id='parent_contract_id_104',
               lifetime_start=get_datetime('2015-07-04'),
               lifetime_end=get_datetime('2015-08-04'),
               deleted=False
               ).save(db_api.get_session())

        db_cre(contract_id=CONTRACT_ID_105,
               region_id='region_id_102',
               project_id='project_id_102',
               project_name='project_name_102',
               catalog_id='catalog_id_105',
               catalog_name='catalog_name_105',
               num=105,
               parent_ticket_template_id='parent_ticket_template_id_105',
               ticket_template_id='ticket_template_id_105',
               parent_ticket_template_name='parent_ticket_template_name_105',
               parent_application_kinds_name='par_application_kinds_name_105',
               application_kinds_name='application_kinds_name_105',
               cancel_application_id='cancel_application_id_105',
               application_id='application_id_105',
               ticket_template_name='ticket_template_name_102',
               application_name='application_name_101',
               application_date=get_datetime('2015-05-07'),
               parent_contract_id='parent_contract_id_105',
               lifetime_start=get_datetime('2015-07-05'),
               lifetime_end=get_datetime('2015-08-05'),
               deleted=False
               ).save(db_api.get_session())

        db_cre(contract_id=CONTRACT_ID_106,
               region_id='region_id_102',
               project_id='project_id_102',
               project_name='project_name_102',
               catalog_id='catalog_id_106',
               catalog_name='catalog_name_106',
               num=106,
               parent_ticket_template_id='parent_ticket_template_id_106',
               ticket_template_id='ticket_template_id_106',
               parent_ticket_template_name='parent_ticket_template_name_106',
               parent_application_kinds_name='par_application_kinds_name_106',
               application_kinds_name='application_kinds_name_106',
               cancel_application_id='cancel_application_id_106',
               application_id='application_id_106',
               ticket_template_name='ticket_template_name_101',
               application_name='application_name_102',
               application_date=get_datetime('2015-05-08'),
               parent_contract_id='parent_contract_id_106',
               lifetime_start=get_datetime('2015-07-06'),
               lifetime_end=get_datetime('2015-08-06'),
               deleted=False
               ).save(db_api.get_session())

        db_cre(contract_id=CONTRACT_ID_107,
               region_id='region_id_102',
               project_id='project_id_102',
               project_name='project_name_102',
               catalog_id='catalog_id_107',
               catalog_name='catalog_name_107',
               num=107,
               parent_ticket_template_id='parent_ticket_template_id_107',
               ticket_template_id='ticket_template_id_107',
               parent_ticket_template_name='parent_ticket_template_name_107',
               parent_application_kinds_name='par_application_kinds_name_107',
               application_kinds_name='application_kinds_name_107',
               cancel_application_id='cancel_application_id_107',
               application_id='application_id_107',
               ticket_template_name='ticket_template_name_107',
               application_name='application_name_107',
               application_date=get_datetime('2015-05-07'),
               parent_contract_id='parent_contract_id_107',
               lifetime_start=None,
               lifetime_end=None,
               deleted=False
               ).save(db_api.get_session())

        db_cre(contract_id=CONTRACT_ID_108,
               region_id='region_id_102',
               project_id='project_id_102',
               project_name='project_name_102',
               catalog_id='catalog_id_108',
               catalog_name='catalog_name_108',
               num=108,
               parent_ticket_template_id='parent_ticket_template_id_108',
               ticket_template_id='ticket_template_id_108',
               parent_ticket_template_name='parent_ticket_template_name_108',
               parent_application_kinds_name='par_application_kinds_name_108',
               application_kinds_name='application_kinds_name_108',
               cancel_application_id='cancel_application_id_108',
               application_id='application_id_108',
               ticket_template_name='ticket_template_name_102',
               application_name='application_name_102',
               application_date=get_datetime('2015-05-08'),
               parent_contract_id='parent_contract_id_108',
               lifetime_start=get_datetime('2015-07-08'),
               lifetime_end=get_datetime('2015-08-08'),
               deleted=True
               ).save(db_api.get_session())

    def destroy_fixtures(self):
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_list_api_no_authority(self):
        """Test list api.
        Test cases run unauthorized.
        """
        path = '/contract'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:no_auth'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 403)

    def test_list_api_with_no_params(self):
        """Test list api.
        Test with no params.
        """
        path = '/contract'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']

        self.assertEqual(len(res_objs), 7)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_106)
        self.assertEqual(res_objs[2]['contract_id'], CONTRACT_ID_105)
        self.assertEqual(res_objs[3]['contract_id'], CONTRACT_ID_104)
        self.assertEqual(res_objs[4]['contract_id'], CONTRACT_ID_103)
        self.assertEqual(res_objs[5]['contract_id'], CONTRACT_ID_102)
        self.assertEqual(res_objs[6]['contract_id'], CONTRACT_ID_101)

    def test_list_api__no_project_id_with_member_role(self):
        """Test list api.
        Test no project_id with __member__ role.
        """
        path = '/contract'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:project_id_102:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_project_id(self):
        """Test list api.
        Test with project id.
        """
        path = '/contract?project_id=%s' % 'project_id_102'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:project_id_102:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_106)
        self.assertEqual(res_objs[2]['contract_id'], CONTRACT_ID_105)

    def test_list_api_with_region_id(self):
        """Test list api.
        Test with region id.
        """
        path = '/contract?region_id=%s' % 'region_id_101'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_104)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_103)
        self.assertEqual(res_objs[2]['contract_id'], CONTRACT_ID_102)
        self.assertEqual(res_objs[3]['contract_id'], CONTRACT_ID_101)

    def test_list_api_with_project_name(self):
        """Test list api.
        Test with project name.
        """
        path = '/contract?project_name=%s' % 'project_name_102'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_106)
        self.assertEqual(res_objs[2]['contract_id'], CONTRACT_ID_105)

    def test_list_api_with_catalog_name(self):
        """Test list api.
        Test with catalog name.
        """
        path = '/contract?catalog_name=%s' % 'catalog_name_107'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)

    def test_list_api_with_application_id(self):
        """Test list api.
        Test with application id.
        """
        path = '/contract?application_id=%s' % 'application_id_107'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)

    def test_list_api_with_lifetime(self):
        """Test list api.
        Test with lifetime.
        """
        path = '/contract?lifetime=%s' % '2015-07-02T20:59:59.999999'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_102)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_101)

    def test_list_api_with_date_in_lifetime(self):
        """Test list api.
        Test with date_in_lifetime.
        """
        path = '/contract?date_in_lifetime=%s' % '2015-08-05'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_106)
        self.assertEqual(res_objs[2]['contract_id'], CONTRACT_ID_105)

    def test_list_api_with_ticket_template_name(self):
        """Test list api.
        Test filter with application_name.
        """
        path = '/contract?ticket_template_name=%s' % 'ticket_template_name_107'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)

    def test_list_api_with_application_name(self):
        """Test list api.
        Test filter with application_name.
        """
        path = '/contract?application_name=%s' % 'application_name_107'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)

    def test_list_api_with_parent_contract_id(self):
        """Test list api.
        Test filter with parent_contract_id.
        """
        path = '/contract?parent_contract_id=%s' % 'parent_contract_id_107'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)

    def test_list_api_with_application_kinds_name(self):
        """Test list api.
        Test filter with application_kinds_name.
        """
        path = '/contract?application_kinds_name=%s' % \
            'application_kinds_name_107'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)

    def test_list_api_with_application_date_from(self):
        """Test list api.
        Test filter with application_date_from.
        """
        path = '/contract?application_date_from=%s' \
               % '2015-05-07T00:00:00.000000'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_106)
        self.assertEqual(res_objs[2]['contract_id'], CONTRACT_ID_105)

    def test_list_api_with_application_date_to(self):
        """Test list api.
        Test filter with application_date_to.
        """
        path = '/contract?application_date_to=%s' \
               % '2015-05-01T23:59:59.999999'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_104)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_101)

    def test_list_api_with_lifetime_start_from(self):
        """Test list api.
        Test filter with lifetime_start_from.
        """
        path = '/contract?lifetime_start_from=%s' \
               % '2015-07-07T00:00:00.000000'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)

    def test_list_api_with_lifetime_start_to(self):
        """Test list api.
        Test filter with lifetime_start_to.
        """
        path = '/contract?lifetime_start_to=%s' \
               % '2015-07-01T23:59:59.999999'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_101)

    def test_list_api_with_lifetime_end_from(self):
        """Test list api.
        Test with lifetime_end_from.
        """
        path = '/contract?lifetime_end_from=%s' \
               % '2015-08-07T00:00:00.000000'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)

    def test_list_api_with_lifetime_end_to(self):
        """Test list api.
        Test with lifetime_end_to.
        """
        path = '/contract?lifetime_end_to=%s' \
               % '2015-08-01T23:59:59.999999'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_101)

    def test_list_api_with_lifetime_start_today(self):
        """Test list api.
        Test filter with date_in_lifetime if include the data of the start day.
        """
        path = '/contract?date_in_lifetime=%s' \
               % '2015-07-01'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_101)

    def test_list_api_with_lifetime_end_today(self):
        """Test list api.
        Test filter with date_in_lifetime if include the data of the end day.
        """
        path = '/contract?date_in_lifetime=%s' \
               % '2015-08-06'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_106)

    def test_list_api_with_limit(self):
        """Test list api.
        Test with limit.
        """
        path = '/contract?limit=%d' % 6

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 6)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_107)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_106)
        self.assertEqual(res_objs[2]['contract_id'], CONTRACT_ID_105)
        self.assertEqual(res_objs[3]['contract_id'], CONTRACT_ID_104)
        self.assertEqual(res_objs[4]['contract_id'], CONTRACT_ID_103)
        self.assertEqual(res_objs[5]['contract_id'], CONTRACT_ID_102)

    def test_list_api_with_marker(self):
        """Test list api.
        Test with marker.
        """
        path = '/contract?marker=%s' % CONTRACT_ID_104

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_103)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_102)
        self.assertEqual(res_objs[2]['contract_id'], CONTRACT_ID_101)

    def test_list_api_with_sort_key(self):
        """Test list api.
        Test with sort key.
        """
        path = '/contract?sort_key=%s' % 'lifetime_start'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 7)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_106)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_105)
        self.assertEqual(res_objs[2]['contract_id'], CONTRACT_ID_104)
        self.assertEqual(res_objs[3]['contract_id'], CONTRACT_ID_103)
        self.assertEqual(res_objs[4]['contract_id'], CONTRACT_ID_102)
        self.assertEqual(res_objs[5]['contract_id'], CONTRACT_ID_101)
        self.assertEqual(res_objs[6]['contract_id'], CONTRACT_ID_107)

    def test_list_api_with_sort_dir(self):
        """Test list api.
        Test with sort dir.
        """
        path = '/contract?sort_dir=%s' % 'asc'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 7)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_101)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_102)
        self.assertEqual(res_objs[2]['contract_id'], CONTRACT_ID_103)
        self.assertEqual(res_objs[3]['contract_id'], CONTRACT_ID_104)
        self.assertEqual(res_objs[4]['contract_id'], CONTRACT_ID_105)
        self.assertEqual(res_objs[5]['contract_id'], CONTRACT_ID_106)
        self.assertEqual(res_objs[6]['contract_id'], CONTRACT_ID_107)

    def test_list_api_with_sort_key_dir(self):
        """Test list api.
        Test with sort key and sort dir.
        """
        path = '/contract?sort_key=%s&sort_dir=%s' % \
            ('project_name,catalog_name',
             'asc,desc')

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 7)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_104)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_103)
        self.assertEqual(res_objs[2]['contract_id'], CONTRACT_ID_102)
        self.assertEqual(res_objs[3]['contract_id'], CONTRACT_ID_101)
        self.assertEqual(res_objs[4]['contract_id'], CONTRACT_ID_107)
        self.assertEqual(res_objs[5]['contract_id'], CONTRACT_ID_106)
        self.assertEqual(res_objs[6]['contract_id'], CONTRACT_ID_105)

    def test_list_api_with_sort_key_less_than_sort_dir(self):
        """Test list api.
        Test with sort key and sort dir, where key is less than dir.
        """
        path = '/contract?sort_key=%s&sort_dir=%s' % \
            ('catalog_name',
             'asc,desc')

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 7)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_101)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_102)
        self.assertEqual(res_objs[2]['contract_id'], CONTRACT_ID_103)
        self.assertEqual(res_objs[3]['contract_id'], CONTRACT_ID_104)
        self.assertEqual(res_objs[4]['contract_id'], CONTRACT_ID_105)
        self.assertEqual(res_objs[5]['contract_id'], CONTRACT_ID_106)
        self.assertEqual(res_objs[6]['contract_id'], CONTRACT_ID_107)

    def test_list_api_with_sort_key_mort_than_sort_dir(self):
        """Test list api.
        Test with sort key and sort dir, where key is more than dir.
        """
        path = '/contract?sort_key=%s&sort_dir=%s' % \
            ('project_name,catalog_name',
             'asc')

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 7)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_104)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_103)
        self.assertEqual(res_objs[2]['contract_id'], CONTRACT_ID_102)
        self.assertEqual(res_objs[3]['contract_id'], CONTRACT_ID_101)
        self.assertEqual(res_objs[4]['contract_id'], CONTRACT_ID_107)
        self.assertEqual(res_objs[5]['contract_id'], CONTRACT_ID_106)
        self.assertEqual(res_objs[6]['contract_id'], CONTRACT_ID_105)

    def test_list_api_with_deleted(self):
        """Test list api.
        Test with deleted.
        """
        path = '/contract?force_show_deleted=%s' % 'true'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 8)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_108)
        self.assertEqual(res_objs[1]['contract_id'], CONTRACT_ID_107)
        self.assertEqual(res_objs[2]['contract_id'], CONTRACT_ID_106)
        self.assertEqual(res_objs[3]['contract_id'], CONTRACT_ID_105)
        self.assertEqual(res_objs[4]['contract_id'], CONTRACT_ID_104)
        self.assertEqual(res_objs[5]['contract_id'], CONTRACT_ID_103)
        self.assertEqual(res_objs[6]['contract_id'], CONTRACT_ID_102)
        self.assertEqual(res_objs[7]['contract_id'], CONTRACT_ID_101)

    def test_list_api_all_param(self):
        """Test list api.
        Test with all parameters.
        """
        path = '/contract?project_id=%s&region_id=%s' \
            '&project_name=%s&catalog_name=%s' \
            '&application_id=%s&lifetime=%s&date_in_lifetime=%s' \
            '&ticket_template_name=%s&application_kinds_name=%s' \
            '&application_name=%s&parent_contract_id=%s' \
            '&application_date_from=%s&application_date_to=%s' \
            '&lifetime_start_from=%s&lifetime_start_to=%s' \
            '&lifetime_end_from=%s&lifetime_end_to=%s' \
            '&limit=%d&marker=%s' \
            '&sort_key=%s&sort_dir=%s&force_show_deleted=%s' % \
            ('project_id_102',
             'region_id_102',
             'project_name_102',
             'catalog_name_105',
             'application_id_105',
             '2015-08-04T23:59:59.999999',
             '2015-08-05',
             'ticket_template_name_102',
             'application_kinds_name_105',
             'application_name_101',
             'parent_contract_id_105',
             '2015-05-07T00:00:00.000000',
             '2015-05-07T23:59:59.999999',
             '2015-07-05T00:00:00.000000',
             '2015-07-05T23:59:59.999999',
             '2015-08-05T00:00:00.000000',
             '2015-08-05T23:59:59.999999',
             1,
             CONTRACT_ID_101,
             'catalog_name,lifetime_start',
             'asc,desc',
             'false')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:project_id_102:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['contract_id'], CONTRACT_ID_105)

    def test_list_api_response_empty(self):
        """Test list api.
        Test if the retrieved result is of 0.
        """
        path = '/contract?project_id=%s' % 'project_id_110'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 0)

    def test_list_api_member_authority_false(self):
        """Test list api.
        Test when it is executed by a user other than the administrator.
        """
        path = '/contract?project_id=%s' % 'project_id_101'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:project_id_112:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(len(res_objs), 0)

    def test_list_api_with_lifetime_not_datetime(self):
        """Test list api.
        Test with date_in_lifetime where is not datetime.
        """
        path = '/contract?date_in_lifetime=%s' % '2015-08-05T20:50:12'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_date_in_lifetime_not_date(self):
        """Test list api.
        Test with date_in_lifetime where is not datetime.
        """
        path = '/contract?date_in_lifetime=%s' % '2015-08'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_application_date_from_not_datetime(self):
        """Test list api.
        Test filter with application_date_from where is over length.
        """
        path = '/contract?application_date_from=%s' \
               % '2015-05'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_application_date_to_not_datetime(self):
        """Test list api.
        Test filter with application_date_to where is not datetime.
        """
        path = '/contract?application_date_to=%s' \
               % '2015-05-01T23:59:59'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_lifetime_start_from_not_datetime(self):
        """Test list api.
        Test filter with lifetime_start_from.
        """
        path = '/contract?lifetime_start_from=%s' \
               % '2015-07-07T00:00:00'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_lifetime_start_to_not_datetime(self):
        """Test list api.
        Test filter with lifetime_start_to.
        """
        path = '/contract?lifetime_start_to=%s' \
               % '2015-07-01T23:59.999999'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_lifetime_end_from_not_datetime(self):
        """Test list api.
        Test with lifetime_end_from.
        """
        path = '/contract?lifetime_end_from=%s' \
               % '2015-08-07T00:00:00'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_lifetime_end_to_not_datetime(self):
        """Test list api.
        Test with lifetime_end_to.
        """
        path = '/contract?lifetime_end_to=%s' \
               % '2015-08-01T23:999999'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_limit_not_int(self):
        """Test list api.
        Test with limit where is not int.
        """
        path = '/contract?limit=%s' % 'a'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_marker_lenghe(self):
        """Test list api.
        Test with marker where is over length.
        """
        path = '/contract?marker=%s' % 'a' * 65

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_sort_key_not_supported(self):
        """Test list api.
        Test with sort key where is not supported.
        """
        path = '/contract?sort_key=%s' % 'parent_application_kinds_name'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_sort_dir_not_supported(self):
        """Test list api.
        Test with sort dir where is not supported.
        """
        path = '/contract?sort_dir=%s' % 'dasc'

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)
