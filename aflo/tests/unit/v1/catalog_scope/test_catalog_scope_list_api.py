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

from datetime import datetime
from oslo_config import cfg
from oslo_serialization import jsonutils
import routes

from aflo.api.v1 import router
from aflo.common import wsgi
from aflo import context
from aflo import db
from aflo.db.sqlalchemy import models as db_models
from aflo.db.sqlalchemy.models import CatalogScope
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF
db_api = db.get_api()

ID_101 = 'id0a4146-fd07-414b-aa5e-dedbeef00101'
ID_102 = 'id0a4146-fd07-414b-aa5e-dedbeef00102'
ID_103 = 'id0a4146-fd07-414b-aa5e-dedbeef00103'
ID_104 = 'id0a4146-fd07-414b-aa5e-dedbeef00104'
ID_105 = 'id0a4146-fd07-414b-aa5e-dedbeef00105'
ID_106 = 'id0a4146-fd07-414b-aa5e-dedbeef00106'
ID_107 = 'id0a4146-fd07-414b-aa5e-dedbeef00107'
ID_108 = 'id0a4146-fd07-414b-aa5e-dedbeef00108'
ID_109 = 'id0a4146-fd07-414b-aa5e-dedbeef00109'

CATALOG_ID_101 = 'ea0a4146-fd07-414b-aa5e-dedbeef00101'
CATALOG_ID_102 = 'ea0a4146-fd07-414b-aa5e-dedbeef00102'

SCOPE_101 = 'bdb8f50f82da4370813e6ea797b1fb101'
SCOPE_102 = 'bdb8f50f82da4370813e6ea797b1fb102'
SCOPE_DEF = 'Default'


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
        CatalogScope(id=ID_101,
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_101,
                     lifetime_start=datetime(2015, 1, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(9999, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1='expansion_key1',
                     expansion_key2='expansion_key2',
                     expansion_key3='expansion_key3',
                     expansion_key4='expansion_key4',
                     expansion_key5='expansion_key5',
                     expansion_text='expansion_text'
                     ).save(db_api.get_session())

        CatalogScope(id=ID_102,
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_101,
                     lifetime_start=datetime(2010, 1, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2010, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1='expansion_key1',
                     expansion_key2=None,
                     expansion_key3=None,
                     expansion_key4=None,
                     expansion_key5=None,
                     expansion_text='expansion_text'
                     ).save(db_api.get_session())

        CatalogScope(id=ID_103,
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_102,
                     lifetime_start=datetime(2015, 1, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(9999, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1=None,
                     expansion_key2=None,
                     expansion_key3=None,
                     expansion_key4=None,
                     expansion_key5=None,
                     expansion_text=None
                     ).save(db_api.get_session())

        CatalogScope(id=ID_104,
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_102,
                     lifetime_start=datetime(2011, 1, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2011, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1='!"#$%&()=~|`{+*}<>?_',
                     expansion_key2='!"#$%&()=~|`{+*}<>?_',
                     expansion_key3='!"#$%&()=~|`{+*}<>?_',
                     expansion_key4='!"#$%&()=~|`{+*}<>?_',
                     expansion_key5='!"#$%&()=~|`{+*}<>?_',
                     expansion_text=',./\;:]@[\^-'
                     ).save(db_api.get_session())

        CatalogScope(id=ID_105,
                     catalog_id=CATALOG_ID_102,
                     scope=SCOPE_101,
                     lifetime_start=datetime(2015, 1, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(9999, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1='expansion_key1',
                     expansion_key2='expansion_key2',
                     expansion_key3='expansion_key3',
                     expansion_key4='expansion_key4',
                     expansion_key5='expansion_key5',
                     expansion_text='expansion_text'
                     ).save(db_api.get_session())

        CatalogScope(id=ID_106,
                     catalog_id=CATALOG_ID_102,
                     scope=SCOPE_101,
                     lifetime_start=datetime(2012, 1, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2012, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1='expansion_key1',
                     expansion_key2='expansion_key2',
                     expansion_key3='expansion_key3',
                     expansion_key4='expansion_key4',
                     expansion_key5='expansion_key5',
                     expansion_text='expansion_text'
                     ).save(db_api.get_session())

        CatalogScope(id=ID_107,
                     catalog_id=CATALOG_ID_102,
                     scope=SCOPE_102,
                     lifetime_start=datetime(2015, 1, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(9999, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1='expansion_key1',
                     expansion_key2='expansion_key2',
                     expansion_key3='expansion_key3',
                     expansion_key4='expansion_key4',
                     expansion_key5='expansion_key5',
                     expansion_text='expansion_text'
                     ).save(db_api.get_session())

        CatalogScope(id=ID_108,
                     catalog_id=CATALOG_ID_102,
                     scope=SCOPE_102,
                     lifetime_start=datetime(2013, 1, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2013, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=False,
                     expansion_key1='expansion_key1',
                     expansion_key2='expansion_key2',
                     expansion_key3='expansion_key3',
                     expansion_key4='expansion_key4',
                     expansion_key5='expansion_key5',
                     expansion_text='expansion_text'
                     ).save(db_api.get_session())

        CatalogScope(id=ID_109,
                     catalog_id=CATALOG_ID_102,
                     scope=SCOPE_102,
                     lifetime_start=datetime(2014, 1, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2014, 12, 31, 23, 59, 59, 999999),
                     created_at=datetime.utcnow(),
                     updated_at=datetime.utcnow(),
                     deleted_at=None,
                     deleted=True,
                     expansion_key1='expansion_key1',
                     expansion_key2='expansion_key2',
                     expansion_key3='expansion_key3',
                     expansion_key4='expansion_key4',
                     expansion_key5='expansion_key5',
                     expansion_text='expansion_text'
                     ).save(db_api.get_session())

    def destroy_fixtures(self):
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_index_api_non_params(self):
        """Test 'List Search of catalog scope'
        Test the operation of the parameter without.
        """

        # Create a request data
        path = '/catalogs/scope'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(len(res_objs), 8)
        self.assertEqual(res_objs[0]['id'], ID_108)
        self.assertEqual(res_objs[1]['id'], ID_107)
        self.assertEqual(res_objs[2]['id'], ID_106)
        self.assertEqual(res_objs[3]['id'], ID_105)
        self.assertEqual(res_objs[4]['id'], ID_104)
        self.assertEqual(res_objs[5]['id'], ID_103)
        self.assertEqual(res_objs[6]['id'], ID_102)
        self.assertEqual(res_objs[7]['id'], ID_101)

    def test_index_api_paginate_params(self):
        """Test 'List Search of catalog scope'
        Test with paginate parameters.
        """

        # Create a request data
        path = '/catalogs/scope?' \
            'marker=%s&limit=%d&sort_key=%s&sort_dir=%s' \
            % (ID_104, 3, 'id', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['id'], ID_105)
        self.assertEqual(res_objs[1]['id'], ID_106)
        self.assertEqual(res_objs[2]['id'], ID_107)

    def test_index_api_catalog_id_param(self):
        """Test 'List Search of catalog scope'
        Test with catalog id parameter.
        """

        # Create a request data
        path = '/catalogs/scope?catalog_id=%s' % (CATALOG_ID_101)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['id'], ID_104)
        self.assertEqual(res_objs[1]['id'], ID_103)
        self.assertEqual(res_objs[2]['id'], ID_102)
        self.assertEqual(res_objs[3]['id'], ID_101)

    def test_index_api_scope_param(self):
        """Test 'List Search of catalog scope'
        Test with scope parameter.
        """

        # Create a request data
        path = '/catalogs/scope?scope=%s' % (SCOPE_101)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['id'], ID_106)
        self.assertEqual(res_objs[1]['id'], ID_105)
        self.assertEqual(res_objs[2]['id'], ID_102)
        self.assertEqual(res_objs[3]['id'], ID_101)

    def test_index_api_lifetime_param(self):
        """Test 'List Search of catalog scope'
        Test with lifetime parameter.
        """

        # Create a request data
        path = '/catalogs/scope?lifetime=%s' % '2016-12-31T23:59:59.999999'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['id'], ID_107)
        self.assertEqual(res_objs[1]['id'], ID_105)
        self.assertEqual(res_objs[2]['id'], ID_103)
        self.assertEqual(res_objs[3]['id'], ID_101)

    def test_index_api_lifetime_start_param(self):
        """Test 'List Search of catalog scope'
        Test with lifetime = lifetime_start parameter.
        """

        # Create a request data
        path = '/catalogs/scope?lifetime=%s' % '2011-01-01T00:00:00.000000'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['id'], ID_104)

    def test_index_api_lifetime_end_param(self):
        """Test 'List Search of catalog scope'
        Test with lifetime = lifetime_end parameter.
        """

        # Create a request data
        path = '/catalogs/scope?lifetime=%s' % '2011-12-31T23:59:59.999999'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['id'], ID_104)

    def test_index_api_lifetime_not_datetime_irregular(self):
        """Test 'List Search of catalog scope'
        Test with lifetime parameter is not datetime.
        """

        # Create a request data
        path = '/catalogs/scope?lifetime=%s' % '2017-01-01T00:00:00'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_response_empty(self):
        """Test 'List Search of catalog scope'
        Test if the retrieved result is empty.
        """

        # Create a request data
        path = '/catalogs/scope?marker=%s' % ID_101
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(len(res_objs), 0)

    def test_index_api_many_sort_key(self):
        """Test 'List Search of catalog scope'
        Test of if you specify multiple 'sort_key'.
        """

        # Create a request data
        path = '/catalogs/scope?' \
               'sort_key=%s&sort_key=%s&sort_dir=%s&sort_dir=%s' \
               % ('scope', 'id', 'desc', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(len(res_objs), 8)
        self.assertEqual(res_objs[0]['id'], ID_103)
        self.assertEqual(res_objs[1]['id'], ID_104)
        self.assertEqual(res_objs[2]['id'], ID_107)
        self.assertEqual(res_objs[3]['id'], ID_108)
        self.assertEqual(res_objs[4]['id'], ID_101)
        self.assertEqual(res_objs[5]['id'], ID_102)
        self.assertEqual(res_objs[6]['id'], ID_105)
        self.assertEqual(res_objs[7]['id'], ID_106)

    def test_index_api_sort_dir_not_enough_irregular(self):
        """Test 'List Search of catalog scope'
        Test of if you specify multiple 'sort_key'.
        Pattern the number of 'sort_dir' is not enough.
        """

        # Create a request data
        path = '/catalogs/scope?' \
               'sort_key=%s&sort_key=%s&sort_key=%s&sort_dir=%s&sort_dir=%s' \
            % ('catalog_id', 'scope', 'id', 'desc', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_sort_key_not_enough_irregular(self):
        """Test 'List Search of catalog scope'
        Test of if you specify multiple 'sort_dir'.
        Pattern the number of 'sort_key' is not enough.
        """

        # Create a request data
        path = '/catalogs/scope?' \
               'sort_key=%s&sort_key=%s&sort_dir=%s&sort_dir=%s&sort_dir=%s' \
            % ('catalog_id', 'scope', 'asc', 'desc', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_default_limit(self):
        """Test 'List Search of catalog scope'
        Or testing the default value of 'limit' is used.
        """

        bk_limit_param_default = CONF.limit_param_default
        self.config(limit_param_default=2)

        # Create a request data
        path = '/catalogs/scope'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        self.config(limit_param_default=bk_limit_param_default)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['id'], ID_108)
        self.assertEqual(res_objs[1]['id'], ID_107)

    def test_index_api_max_limit(self):
        """Test 'List Search of catalog scope'
        Or testing the default value of 'limit' is used.
        """

        bk_api_limit_max = CONF.api_limit_max
        self.config(api_limit_max=2)

        # Create a request data
        path = '/catalogs/scope'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        self.config(api_limit_max=bk_api_limit_max)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['id'], ID_108)
        self.assertEqual(res_objs[1]['id'], ID_107)

    def test_index_api_limit_not_int_irregular(self):
        """Test 'List Search of catalog scope'
        Test with limit parameter is not integer.
        """

        # Create a request data
        path = '/catalogs/scope?limit=%s' % '1a'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_force_show_deleted_param(self):
        """Test 'List Search of catalog scope'
        Test with force_show_deleted parameter.
        """

        # Create a request data
        path = '/catalogs/scope?force_show_deleted=%s' % True
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(len(res_objs), 9)
        self.assertEqual(res_objs[0]['id'], ID_109)

    def test_index_api_member_authority(self):
        """Test 'List Search of catalog scope'
        Test when it is executed by a user other than the administrator.
        """

        # Create a request data
        path = '/catalogs/scope'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:%s:__member__' % SCOPE_102}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_scope']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['id'], ID_108)
        self.assertEqual(res_objs[1]['id'], ID_107)
        self.assertEqual(res_objs[2]['id'], ID_104)
        self.assertEqual(res_objs[3]['id'], ID_103)

    def test_index_api_no_authority_irregular(self):
        """Test 'List Search of catalog scope'
        Test cases run unauthorized.
        """

        # Create a request data
        path = '/catalogs/scope'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:no_authority'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_index_api_with_marker_length_irregular(self):
        """Test 'List Search of catalog scope'
        Test with marker parameter where is over length.
        """

        # Create a request data
        path = '/catalogs/scope?marker=%s' % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_sort_key_not_supported_irregular(self):
        """Test 'List Search of catalog scope'
        Test with sort key parameter where is not supported.
        """

        # Create a request data
        path = '/catalogs/scope?sort_key=%s&sort_dir=%s' \
               % ('updated_at', 'desc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_sort_dir_not_supported_irregular(self):
        """Test 'List Search of catalog scope'
        Test with sort dir parameter where is not supported.
        """

        # Create a request data
        path = '/catalogs/scope?sort_key=%s&sort_dir=%s' \
               % ('catalog_id', 'dasc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)
