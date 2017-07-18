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

import datetime
from oslo_config import cfg
from oslo_serialization import jsonutils
import routes

from aflo.api.v1 import router
from aflo.common import wsgi
import aflo.context
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests.unit.v1.contracts\
    import utils as contract_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF

CNT_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef10001'
CNT_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef10002'
CNT_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef10003'
CNT_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef10004'
CNT_UUID5 = 'ea0a4146-fd07-414b-aa5e-dedbeef10005'

REG_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef20001'
REG_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef20002'
REG_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef20003'
REG_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef20004'
REG_UUID5 = 'ea0a4146-fd07-414b-aa5e-dedbeef20005'

PJ_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef21001'
PJ_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef21002'
PJ_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef21003'
PJ_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef21004'
PJ_UUID5 = 'ea0a4146-fd07-414b-aa5e-dedbeef21005'


class TestContractShowAPI(base.IsolatedUnitTest):
    """Do a test of 'Update ticket'"""

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
        contract_utils.create_contract_for_update(
            db_models,
            contract_id=CNT_UUID1,
            region_id=REG_UUID1,
            project_id=PJ_UUID1,
            date=datetime.date(2015, 1, 10),
            seq=1,
            deleted=0)
        contract_utils.create_contract_for_update(
            db_models,
            contract_id=CNT_UUID2,
            region_id=REG_UUID2,
            project_id=PJ_UUID2,
            date=datetime.date(2015, 1, 11),
            seq=2,
            deleted=0)
        contract_utils.create_contract_for_update(
            db_models,
            contract_id=CNT_UUID3,
            region_id=REG_UUID3,
            project_id=PJ_UUID3,
            date=datetime.date(2015, 1, 12),
            seq=3,
            deleted=1)
        contract_utils.create_contract_for_update(
            db_models,
            contract_id=CNT_UUID4,
            region_id=REG_UUID4,
            project_id=PJ_UUID4,
            date=datetime.date(2015, 1, 13),
            seq=4,
            deleted=0)

    def destroy_fixtures(self):
        # Easiest to just drop the models and re-create them...
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_show(self):
        # Create a request data
        path = '/contract/%s' % CNT_UUID1
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['contract']
        self.assertEqual(res_objs['contract_id'], CNT_UUID1)
        self.assertEqual(res_objs['region_id'], REG_UUID1)
        self.assertEqual(res_objs['expansions']['expansion_key1'], '1')

    def test_show_response_empty_irregular(self):
        # Create a request data
        path = '/contract/%s' % CNT_UUID5
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)

    def test_show_api_no_authority(self):
        # Create a request data
        path = '/contract/%s' % CNT_UUID1
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:no_authority'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_show_contract_id_length(self):
        # Create a request data
        path = '/contract/%s' % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)
