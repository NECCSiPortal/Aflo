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
import routes

from aflo.api.v1 import router
from aflo.common import wsgi
import aflo.context
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF

CONTRACT_ID_101 = 'ea0a4146-fd07-414b-aa5e-dedbeef00101'
CONTRACT_ID_102 = 'ea0a4146-fd07-414b-aa5e-dedbeef00102'


def get_datetime(str_date):
    """Get datetime.
        :param str_date: String of date.
    """
    return datetime.strptime(str_date + 'T00:00:00.000000',
                             '%Y-%m-%dT%H:%M:%S.%f')


class TestContractShowAPI(base.IsolatedUnitTest):
    """Do a test of 'Delete contract'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestContractShowAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestContractShowAPI, self).tearDown()
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
               parent_ticket_template_name='par_ticket_template_name_101',
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

    def destroy_fixtures(self):
        # Easiest to just drop the models and re-create them...
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_delete(self):
        """Delete a contract"""
        path = '/contract/%s' % CONTRACT_ID_101
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 200)

        se = db_api.get_session()
        contract = se.query(db_models.Contract).get(CONTRACT_ID_101)
        self.assertIsNone(contract)

    def test_delete_api_no_authority(self):
        """Delete a contract with no authority"""
        path = '/contract/%s' % CONTRACT_ID_102
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:no_auth'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 403)

    def test_delete_api_no_exist_irregular(self):
        """Delete a contract which is not exist."""
        path = '/contract/%s' % CONTRACT_ID_102
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 404)

    def test_delete_api_error_uri(self):
        """Delete a contract which error uri."""
        path = '/contract/%s' % ''
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 404)

    def test_delete_contract_id_length(self):
        """Delete a contract"""
        path = '/contract/%s' % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)
