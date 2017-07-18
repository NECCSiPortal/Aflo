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
from aflo.tests import utils as test_utils

CONF = cfg.CONF

CT_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef00001'
CT_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef00002'
CT_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef00003'
CT_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef00004'
CT_UUID5 = 'ea0a4146-fd07-414b-aa5e-dedbeef00005'
CT_UUID6 = 'ea0a4146-fd07-414b-aa5e-dedbeef00006'
CT_UUID7 = 'ea0a4146-fd07-414b-aa5e-dedbeef00007'
CT_UUID8 = 'ea0a4146-fd07-414b-aa5e-dedbeef00008'
CT_UUID9 = 'ea0a4146-fd07-414b-aa5e-dedbeef00009'

RG_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef01001'
RG_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef01002'
RG_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef01003'
RG_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef01004'


class TestCatalogIndexAPI(base.WorkflowUnitTest):
    """Test 'Get the details of the Catalog'"""

    def setUp(self):
        """Establish a clean test environment"""
        super(TestCatalogIndexAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestCatalogIndexAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        db_models.Catalog(
            catalog_id=CT_UUID1,
            region_id=RG_UUID1,
            catalog_name='CATALOG_NAME-1',
            lifetime_start=datetime.date(2015, 1, 1),
            lifetime_end=datetime.date(2015, 12, 31),
            deleted=0).save()
        db_models.Catalog(
            catalog_id=CT_UUID2,
            region_id=RG_UUID1,
            catalog_name='CATALOG_NAME-2',
            lifetime_start=datetime.date(2016, 1, 2),
            lifetime_end=datetime.date(2016, 12, 31),
            deleted=0).save()
        db_models.Catalog(
            catalog_id=CT_UUID3,
            region_id=RG_UUID2,
            catalog_name='CATALOG_NAME-3',
            lifetime_start=datetime.date(2015, 1, 3),
            lifetime_end=datetime.date(2015, 12, 31),
            deleted=0).save()
        db_models.Catalog(
            catalog_id=CT_UUID4,
            region_id=RG_UUID2,
            catalog_name='CATALOG_NAME-4',
            lifetime_start=datetime.date(2016, 1, 4),
            lifetime_end=datetime.date(2016, 12, 31),
            deleted=0).save()
        db_models.Catalog(
            catalog_id=CT_UUID5,
            region_id=RG_UUID2,
            catalog_name='CATALOG_NAME-5',
            lifetime_start=datetime.date(2015, 1, 5),
            lifetime_end=datetime.date(2015, 12, 31),
            deleted=0).save()
        db_models.Catalog(
            catalog_id=CT_UUID6,
            region_id=RG_UUID2,
            catalog_name='CATALOG_NAME-6',
            lifetime_start=datetime.date(2016, 1, 6),
            lifetime_end=datetime.date(2016, 12, 31),
            deleted=0).save()
        db_models.Catalog(
            catalog_id=CT_UUID7,
            region_id=RG_UUID1,
            catalog_name='CATALOG_NAME-7',
            lifetime_start=datetime.date(2015, 1, 7),
            lifetime_end=datetime.datetime(2015, 12, 31, 10, 00, 00),
            deleted=0).save()
        db_models.Catalog(
            catalog_id=CT_UUID8,
            region_id=RG_UUID2,
            catalog_name='CATALOG_NAME-8',
            lifetime_start=datetime.date(2016, 1, 8),
            lifetime_end=datetime.date(2016, 12, 31),
            deleted=0).save()
        db_models.Catalog(
            catalog_id=CT_UUID9,
            region_id=RG_UUID2,
            catalog_name='CATALOG_NAME-9',
            lifetime_start=datetime.date(2016, 1, 9),
            lifetime_end=datetime.date(2016, 12, 31),
            deleted=1).save()

    def destroy_fixtures(self):
        # Easiest to just drop the models and re-create them...
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_index_api_non_params(self):
        """Test 'List Search of catalog'
        Test the operation of the parameter without.
        """

        # Create a request data
        path = '/catalog'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 8)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID8)
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID7)
        self.assertEqual(res_objs[2]['catalog_id'], CT_UUID6)
        self.assertEqual(res_objs[3]['catalog_id'], CT_UUID5)
        self.assertEqual(res_objs[4]['catalog_id'], CT_UUID4)
        self.assertEqual(res_objs[5]['catalog_id'], CT_UUID3)
        self.assertEqual(res_objs[6]['catalog_id'], CT_UUID2)
        self.assertEqual(res_objs[7]['catalog_id'], CT_UUID1)

    def test_index_api_paginate_params(self):
        """Test 'List Search of catalog'
        Test with paginate parameters.
        """

        # Create a request data
        path = '/catalog?marker=%s&limit=%d'\
            '&sort_key=%s&sort_dir=%s&force_show_deleted=%s&region_id=%s' \
            % (CT_UUID3, 2, 'catalog_id', 'asc', 'True', RG_UUID2)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID4)
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID5)

    def test_index_api_catalog_id_param(self):
        """Test 'List Search of catalog'
        Test with catalog id parameter.
        """

        # Create a request data
        path = '/catalog?catalog_id=%s' \
               % CT_UUID1
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID1)

        # Create a request data
        path = '/catalog?catalog_id=%s' \
               % "-414b-"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 0)

        # Create a request data
        path = '/catalog?catalog_id=%s' \
               % "ea0a4146"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 0)

        # Create a request data
        path = '/catalog?catalog_id=%s' \
               % "dedbeef00007"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 0)

    def test_index_api_catalog_name_param(self):
        """Test 'List Search of catalog'
        Test with catalog name parameter.
        """

        # Create a request data
        path = '/catalog?catalog_name=%s' \
               % "CATALOG_NAME-2"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID2)

        # Create a request data
        path = '/catalog?catalog_name=%s' \
               % "NAME"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 0)

        # Create a request data
        path = '/catalog?catalog_name=%s' \
               % "CATA"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 0)

        # Create a request data
        path = '/catalog?catalog_name=%s' \
               % "1"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 0)

    def test_index_api_lifetime_param(self):
        """Test 'List Search of catalog'
        Test with lifetime parameter.
        """

        # Create a request data
        path = '/catalog?lifetime=%s' \
               % "2015-1-5T00:00:00.000"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID5)
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID3)

    def test_index_api_lifetime_start_param(self):
        """Test 'List Search of catalog'
        Test with lifetime = lifetime_start parameter.
        """

        # Create a request data
        path = '/catalog?lifetime=%s' \
               % "2015-1-1T00:00:00.000"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID1)

    def test_index_api_lifetime_end_param(self):
        """Test 'List Search of catalog'
        Test with lifetime = lifetime_end parameter.
        """

        # Create a request data
        path = '/catalog?lifetime=%s' \
               % "2015-12-31T00:00:00.000"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID7)
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID5)
        self.assertEqual(res_objs[2]['catalog_id'], CT_UUID3)
        self.assertEqual(res_objs[3]['catalog_id'], CT_UUID1)

    def test_index_api_lifetime_not_datetime(self):
        """Test 'List Search of catalog'
        Test with lifetime parameter is not datetime.
        """

        # Create a request data
        path = '/catalog?lifetime=%s' \
               % "2015-1-5"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_response_empty_irregular(self):
        """Test 'List Search of catalog'
        Test if the retrieved result is of 0.
        """

        # Create a request data
        path = '/catalog?marker=%s' \
               % CT_UUID1
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 0)

    def test_index_api_many_sort_key(self):
        """Test 'List Search of catalog'
        Test of if you specify multiple 'sort_key'.
        """

        # Create a request data
        path = '/catalog?sort_key=%s&sort_key=%s' \
               '&sort_dir=%s&sort_dir=%s' \
               % ('catalog_id', 'lifetime_start', 'asc', 'desc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 8)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID1)
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID2)
        self.assertEqual(res_objs[2]['catalog_id'], CT_UUID3)
        self.assertEqual(res_objs[3]['catalog_id'], CT_UUID4)
        self.assertEqual(res_objs[4]['catalog_id'], CT_UUID5)
        self.assertEqual(res_objs[5]['catalog_id'], CT_UUID6)
        self.assertEqual(res_objs[6]['catalog_id'], CT_UUID7)
        self.assertEqual(res_objs[7]['catalog_id'], CT_UUID8)

    def test_index_api_sort_dir_not_enough_irregular(self):
        """Test 'List Search of catalog'
        Test of if you specify multiple 'sort_key'.
        Pattern the number of 'sort_dir' is not enough.
        """

        # Create a request data
        path = '/catalog?sort_key=%s&sort_key=%s&sort_key=%s'\
            '&sort_dir=%s&sort_dir=%s' \
            % ('catalog_id', 'lifetime_start', 'lifetime_end',
               'desc', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_sort_key_not_enough_irregular(self):
        """Test 'List Search of catalog'
        Test of if you specify multiple 'sort_key'.
        Pattern the number of 'sort_key' is not enough.
        """

        # Create a request data
        path = '/catalog?sort_key=%s'\
            '&sort_dir=%s&sort_dir=%s' \
            % ('catalog_id', 'asc', 'desc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_default_limit(self):
        """Test 'List Search of catalog'
        Or testing the default value of 'limit' is used.
        """

        # Create a request data
        bk_limit_param_default = CONF.limit_param_default
        self.config(limit_param_default=2)

        # Create a request data
        path = '/catalog'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        self.config(limit_param_default=bk_limit_param_default)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID8)
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID7)

    def test_index_api_max_limit(self):
        """Test 'List Search of catalog'
        Test of whether the upper limit of 'limit' is used.
        """

        # Create a request data
        bk_api_limit_max = CONF.api_limit_max
        self.config(api_limit_max=2)

        # Create a request data
        path = '/catalog'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        self.config(api_limit_max=bk_api_limit_max)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID8)
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID7)

    def test_index_api_limit_not_int(self):
        """Test 'List Search of catalog'
        Test with limit parameter is not integer.
        """

        # Create a request data
        path = '/catalog?limit=%s' \
               % "1a"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_force_show_deleted_param(self):
        """Test 'List Search of catalog'
        Test with force_show_deleted parameter.
        """

        # Create a request data
        path = '/catalog?force_show_deleted=%s' \
               % True
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 9)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID9)
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID8)
        self.assertEqual(res_objs[2]['catalog_id'], CT_UUID7)

    def test_index_api_member_authority(self):
        """Test 'List Search of catalog'
        Test when it is executed by a user other than the administrator.
        """

        # Create a request data
        path = '/catalog'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:%s:__member__' % RG_UUID1}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog']
        self.assertEqual(len(res_objs), 8)
        self.assertEqual(res_objs[0]['catalog_id'], CT_UUID8)
        self.assertEqual(res_objs[1]['catalog_id'], CT_UUID7)

    def test_index_api_no_authority_irregular(self):
        """Test 'List Search of catalog'
        Test cases run unauthorized.
        """

        # Create a request data
        path = '/catalog'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:no_authority'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_index_api_with_lifetime_not_datetime(self):
        """Test 'List Search of catalog'
        Test with lifetime parameter where is not datetime.
        """

        # Create a request data
        path = '/catalog?lifetime=%s' \
               % "2015-1-5T"
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_marker_length(self):
        """Test 'List Search of catalog'
        Test with marker parameter where is over length.
        """

        # Create a request data
        path = '/catalog?marker=%s' % 'a' * 65
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_sort_key_not_supported(self):
        """Test 'List Search of catalog'
        Test with sort kry parameter where is not supported.
        """

        # Create a request data
        path = '/catalog?sort_key=%s' % 'expansion_key1'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_sort_dir_not_supported(self):
        """Test 'List Search of catalog'
        Test with sort dir parameter where is not supported.
        """

        # Create a request data
        path = '/catalog?sort_dir=%s' % 'dasc'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)
