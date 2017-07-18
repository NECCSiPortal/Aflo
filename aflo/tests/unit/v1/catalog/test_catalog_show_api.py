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
from aflo.tests.unit.v1.catalog\
    import utils as catalog_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF

CT_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef00001'
CT_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef00002'
CT_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef00003'
CT_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef00004'
CT_UUID5 = 'ea0a4146-fd07-414b-aa5e-dedbeef00005'

RG_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef01001'
RG_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef01002'
RG_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef01003'
RG_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef01004'
RG_UUID5 = 'ea0a4146-fd07-414b-aa5e-dedbeef01005'


class TestCatalogShowAPI(base.WorkflowUnitTest):
    """Do a test of 'Get the details of the Catalog'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestCatalogShowAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestCatalogShowAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        catalog_utils.create_testdata(
            db_models,
            catalog_id=CT_UUID1,
            region_id=RG_UUID1,
            catalog_name='1',
            date=datetime.date(2015, 1, 11),
            seq=1,
            deleted=0)
        catalog_utils.create_testdata(
            db_models,
            catalog_id=CT_UUID2,
            region_id=RG_UUID2,
            catalog_name='2',
            date=datetime.date(2015, 1, 12),
            seq=2,
            deleted=0)
        catalog_utils.create_testdata(
            db_models,
            catalog_id=CT_UUID3,
            region_id=RG_UUID3,
            catalog_name='3',
            date=datetime.date(2015, 1, 13),
            seq=3,
            deleted=1)
        catalog_utils.create_testdata(
            db_models,
            catalog_id=CT_UUID4,
            region_id=RG_UUID4,
            catalog_name='!"#$%&()=~|{+*}<>?_',
            date=datetime.date(2015, 1, 14),
            seq=',./\;:]@[\^-',
            deleted=0)

    def destroy_fixtures(self):
        # Easiest to just drop the models and re-create them...
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_show_api(self):
        """Test 'Search of catalog'
        Test of normal processing.
        """
        path = '/catalog/%s' % CT_UUID1
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(res_objs['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs['region_id'], RG_UUID1)
        self.assertEqual(res_objs['expansions']['expansion_key1'], '1')

    def test_show_api_response_empty_irregular(self):
        """Test 'Search of catalog'
        Test if the retrieved result is of 0.
        """
        path = '/catalog/%s' % CT_UUID5
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
        """Test 'Search of catalog'
        Test cases run unauthorized.
        """
        path = '/catalog/%s' % CT_UUID1
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:no_authority'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_show_api_symbol(self):
        """Test 'Search of catalog'
        Test cases get data is symbol.
        """
        path = '/catalog/%s' % CT_UUID4
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(res_objs['catalog_id'], CT_UUID4)
        self.assertEqual(res_objs['catalog_name'], '!"#$%&()=~|{+*}<>?_')
        self.assertEqual(res_objs['expansions']['expansion_key1'],
                         ',./\;:]@[\^-')
        self.assertEqual(res_objs['expansions']['expansion_key2'],
                         ',./\;:]@[\^-')
        self.assertEqual(res_objs['expansions']['expansion_key3'],
                         ',./\;:]@[\^-')
        self.assertEqual(res_objs['expansions']['expansion_key4'],
                         ',./\;:]@[\^-')
        self.assertEqual(res_objs['expansions']['expansion_key5'],
                         ',./\;:]@[\^-')
        self.assertEqual(res_objs['expansions_text']['expansion_text'],
                         ',./\;:]@[\^-')

    def test_show_api_catalog_id_length(self):
        """Test 'Search of catalog'
        Test of catalog_id is over length.
        """
        path = '/catalog/%s' % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='GET',
                                               path=path)

        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)
