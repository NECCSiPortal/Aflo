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
from aflo.db.sqlalchemy.models import CatalogContents
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF
db_api = db.get_api()

CATALOG_ID_101 = 'ea0a4146-fd07-414b-aa5e-dedbeef00101'
CATALOG_ID_102 = 'ea0a4146-fd07-414b-aa5e-dedbeef00102'
CATALOG_ID_103 = 'ea0a4146-fd07-414b-aa5e-dedbeef00103'
CATALOG_ID_104 = 'ea0a4146-fd07-414b-aa5e-dedbeef00104'
CATALOG_ID_105 = 'ea0a4146-fd07-414b-aa5e-dedbeef00105'
CATALOG_ID_106 = 'ea0a4146-fd07-414b-aa5e-dedbeef00106'


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
        CatalogContents(catalog_id=CATALOG_ID_101,
                        seq_no='seq_no_101',
                        goods_id='goods_id_101',
                        goods_num=101,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        deleted=False,
                        expansion_key1='expansion_key1',
                        expansion_key2='expansion_key2',
                        expansion_key3='expansion_key3',
                        expansion_key4='expansion_key4',
                        expansion_key5='expansion_key5',
                        expansion_text='expansion_text'
                        ).save(db_api.get_session())

        CatalogContents(catalog_id=CATALOG_ID_101,
                        seq_no='seq_no_102',
                        goods_id='goods_id_101',
                        goods_num=102,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        deleted=False,
                        expansion_key1='expansion_key1',
                        expansion_key2='expansion_key2',
                        expansion_key3='expansion_key3',
                        expansion_key4='expansion_key4',
                        expansion_key5='expansion_key5',
                        expansion_text='expansion_text'
                        ).save(db_api.get_session())

        CatalogContents(catalog_id=CATALOG_ID_101,
                        seq_no='seq_no_103',
                        goods_id='goods_id_102',
                        goods_num=101,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        deleted=False,
                        expansion_key1='expansion_key1',
                        expansion_key2='expansion_key2',
                        expansion_key3='expansion_key3',
                        expansion_key4='expansion_key4',
                        expansion_key5='expansion_key5',
                        expansion_text='expansion_text'
                        ).save(db_api.get_session())

        CatalogContents(catalog_id=CATALOG_ID_101,
                        seq_no='seq_no_104',
                        goods_id='goods_id_102',
                        goods_num=102,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        deleted=False,
                        expansion_key1='expansion_key1',
                        expansion_key2='expansion_key2',
                        expansion_key3='expansion_key3',
                        expansion_key4='expansion_key4',
                        expansion_key5='expansion_key5',
                        expansion_text='expansion_text'
                        ).save(db_api.get_session())

        CatalogContents(catalog_id=CATALOG_ID_101,
                        seq_no='seq_no_105',
                        goods_id='goods_id_103',
                        goods_num=103,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        deleted_at=datetime.utcnow(),
                        deleted=True,
                        expansion_key1='expansion_key1',
                        expansion_key2='expansion_key2',
                        expansion_key3='expansion_key3',
                        expansion_key4='expansion_key4',
                        expansion_key5='expansion_key5',
                        expansion_text='expansion_text'
                        ).save(db_api.get_session())

        CatalogContents(catalog_id=CATALOG_ID_102,
                        seq_no='seq_no_106',
                        goods_id='goods_id_104',
                        goods_num=104,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        deleted=False,
                        expansion_key1='expansion_key1',
                        expansion_key2='expansion_key2',
                        expansion_key3='expansion_key3',
                        expansion_key4='expansion_key4',
                        expansion_key5='expansion_key5',
                        expansion_text='expansion_text'
                        ).save(db_api.get_session())

        CatalogContents(catalog_id=CATALOG_ID_104,
                        seq_no='seq_no_107',
                        goods_id='goods_id_107',
                        goods_num=107,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        deleted=False,
                        expansion_key1='!"#$%&()=~|`{+*}<>?_',
                        expansion_key2='!"#$%&()=~|`{+*}<>?_',
                        expansion_key3='!"#$%&()=~|`{+*}<>?_',
                        expansion_key4='!"#$%&()=~|`{+*}<>?_',
                        expansion_key5='!"#$%&()=~|`{+*}<>?_',
                        expansion_text=',./\;:]@[\^-'
                        ).save(db_api.get_session())

        CatalogContents(catalog_id=CATALOG_ID_105,
                        seq_no='seq_no_108',
                        goods_id='goods_id_108',
                        goods_num=108,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        deleted=False,
                        expansion_key1='expansion_key1',
                        expansion_key2=None,
                        expansion_key3=None,
                        expansion_key4=None,
                        expansion_key5=None,
                        expansion_text='expansion_text'
                        ).save(db_api.get_session())

        CatalogContents(catalog_id=CATALOG_ID_106,
                        seq_no='seq_no_109',
                        goods_id='goods_id_109',
                        goods_num=109,
                        created_at=datetime.utcnow(),
                        updated_at=None,
                        deleted_at=None,
                        deleted=False,
                        expansion_key1=None,
                        expansion_key2=None,
                        expansion_key3=None,
                        expansion_key4=None,
                        expansion_key5=None,
                        expansion_text='expansion_text'
                        ).save(db_api.get_session())

    def destroy_fixtures(self):
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_list_api_no_authority(self):
        """Test list api.
        Test cases run unauthorized.
        """
        path = '/catalog/%s/contents' % CATALOG_ID_101

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
        path = '/catalog/%s/contents' % CATALOG_ID_101
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']

        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['seq_no'], 'seq_no_104')
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[1]['seq_no'], 'seq_no_103')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[2]['seq_no'], 'seq_no_102')
        self.assertEqual(res_objs[2]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[3]['seq_no'], 'seq_no_101')
        self.assertEqual(res_objs[3]['catalog_id'], CATALOG_ID_101)

    def test_list_api_with_limit(self):
        """Test list api.
        Test with limit.
        """
        path = '/catalog/%s/contents?limit=%d' % (CATALOG_ID_101, 3)

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['seq_no'], 'seq_no_104')
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[1]['seq_no'], 'seq_no_103')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[2]['seq_no'], 'seq_no_102')
        self.assertEqual(res_objs[2]['catalog_id'], CATALOG_ID_101)

    def test_list_api_with_marker(self):
        """Test list api.
        Test with marker.
        """
        path = '/catalog/%s/contents?marker=%s' % (CATALOG_ID_101,
                                                   'seq_no_105')

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['seq_no'], 'seq_no_104')
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[1]['seq_no'], 'seq_no_103')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[2]['seq_no'], 'seq_no_102')
        self.assertEqual(res_objs[2]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[3]['seq_no'], 'seq_no_101')
        self.assertEqual(res_objs[3]['catalog_id'], CATALOG_ID_101)

    def test_list_api_with_sort_key(self):
        """Test list api.
        Test with sort key.
        """
        path = '/catalog/%s/contents?sort_key=%s' % \
            (CATALOG_ID_101, 'goods_id')

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['seq_no'], 'seq_no_104')
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[1]['seq_no'], 'seq_no_103')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[2]['seq_no'], 'seq_no_102')
        self.assertEqual(res_objs[2]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[3]['seq_no'], 'seq_no_101')
        self.assertEqual(res_objs[3]['catalog_id'], CATALOG_ID_101)

    def test_list_api_with_sort_dir(self):
        """Test list api.
        Test with sort dir.
        """
        path = '/catalog/%s/contents?sort_dir=%s' % \
            (CATALOG_ID_101, 'asc')

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['seq_no'], 'seq_no_101')
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[1]['seq_no'], 'seq_no_102')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[2]['seq_no'], 'seq_no_103')
        self.assertEqual(res_objs[2]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[3]['seq_no'], 'seq_no_104')
        self.assertEqual(res_objs[3]['catalog_id'], CATALOG_ID_101)

    def test_list_api_with_sort_key_dir(self):
        """Test list api.
        Test with sort key and sort dir.
        """
        path = '/catalog/%s/contents?sort_key=%s&sort_dir=%s' % \
            (CATALOG_ID_101,
             'goods_id,goods_num',
             'asc,desc')

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['seq_no'], 'seq_no_102')
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[1]['seq_no'], 'seq_no_101')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[2]['seq_no'], 'seq_no_104')
        self.assertEqual(res_objs[2]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[3]['seq_no'], 'seq_no_103')
        self.assertEqual(res_objs[3]['catalog_id'], CATALOG_ID_101)

    def test_list_api_with_sort_key_less_than_sort_dir(self):
        """Test list api.
        Test with sort key and sort dir, where key is less than dir.
        """
        path = '/catalog/%s/contents?sort_key=%s&sort_dir=%s' % \
            (CATALOG_ID_101,
             'goods_id',
             'asc,desc')

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['seq_no'], 'seq_no_102')
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[1]['seq_no'], 'seq_no_101')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[2]['seq_no'], 'seq_no_104')
        self.assertEqual(res_objs[2]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[3]['seq_no'], 'seq_no_103')
        self.assertEqual(res_objs[3]['catalog_id'], CATALOG_ID_101)

    def test_list_api_with_sort_key_mort_than_sort_dir(self):
        """Test list api.
        Test with sort key and sort dir, where key is more than dir.
        """
        path = '/catalog/%s/contents?sort_key=%s&sort_dir=%s' % \
            (CATALOG_ID_101,
             'goods_id,goods_num',
             'asc')

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['seq_no'], 'seq_no_102')
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[1]['seq_no'], 'seq_no_101')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[2]['seq_no'], 'seq_no_104')
        self.assertEqual(res_objs[2]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[3]['seq_no'], 'seq_no_103')
        self.assertEqual(res_objs[3]['catalog_id'], CATALOG_ID_101)

    def test_list_api_with_deleted(self):
        """Test list api.
        Test with deleted.
        """
        path = '/catalog/%s/contents?force_show_deleted=%s' % \
            (CATALOG_ID_101,
             'true')

        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(len(res_objs), 5)
        self.assertEqual(res_objs[0]['seq_no'], 'seq_no_105')
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[1]['seq_no'], 'seq_no_104')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[2]['seq_no'], 'seq_no_103')
        self.assertEqual(res_objs[2]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[3]['seq_no'], 'seq_no_102')
        self.assertEqual(res_objs[3]['catalog_id'], CATALOG_ID_101)
        self.assertEqual(res_objs[4]['seq_no'], 'seq_no_101')
        self.assertEqual(res_objs[4]['catalog_id'], CATALOG_ID_101)

    def test_list_api_all_param(self):
        """Test list api.
        Test with all parameters.
        """
        path = '/catalog/%s/contents?' \
            '&limit=%d&marker=%s' \
            '&sort_key=%s&sort_dir=%s&force_show_deleted=%s' % \
            (CATALOG_ID_101,
             1,
             'seq_no_101',
             'goods_id,goods_num',
             'asc,desc',
             'false')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['seq_no'], 'seq_no_104')
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_101)

    def test_list_api_response_empty(self):
        """Test list api.
        Test if the retrieved result is of 0.
        """
        path = '/catalog/%s/contents' % CATALOG_ID_103
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(len(res_objs), 0)

    def test_list_api_response_simbol(self):
        """Test list api.
        Test if the retrieved result is simbol.
        """
        path = '/catalog/%s/contents' % CATALOG_ID_104
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['seq_no'], 'seq_no_107')
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_104)
        self.assertEqual(res_objs[0]['expansions']['expansion_key1'],
                         '!"#$%&()=~|`{+*}<>?_')
        self.assertEqual(res_objs[0]['expansions_text']['expansion_text'],
                         ',./\;:]@[\^-')

    def test_list_api_response_expansions_all(self):
        """Test list api.
        Test if the retrieved result is all expansions.
        """
        path = '/catalog/%s/contents' % CATALOG_ID_102
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['seq_no'], 'seq_no_106')
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_102)
        self.assertEqual(res_objs[0]['expansions']['expansion_key1'],
                         'expansion_key1')
        self.assertEqual(res_objs[0]['expansions']['expansion_key2'],
                         'expansion_key2')
        self.assertEqual(res_objs[0]['expansions']['expansion_key3'],
                         'expansion_key3')
        self.assertEqual(res_objs[0]['expansions']['expansion_key4'],
                         'expansion_key4')
        self.assertEqual(res_objs[0]['expansions']['expansion_key5'],
                         'expansion_key5')

    def test_list_api_response_expansions_1(self):
        """Test list api.
        Test if the retrieved result is one expansion_key.
        """
        path = '/catalog/%s/contents' % CATALOG_ID_105
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['seq_no'], 'seq_no_108')
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_105)
        self.assertEqual(res_objs[0]['expansions']['expansion_key1'],
                         'expansion_key1')
        self.assertIsNone(res_objs[0]['expansions']['expansion_key2'])
        self.assertIsNone(res_objs[0]['expansions']['expansion_key3'])
        self.assertIsNone(res_objs[0]['expansions']['expansion_key4'])
        self.assertIsNone(res_objs[0]['expansions']['expansion_key5'])

    def test_list_api_response_expansions_0(self):
        """Test list api.
        Test if the retrieved result is no expansion_key.
        """
        path = '/catalog/%s/contents' % CATALOG_ID_106
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['catalog_contents']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['seq_no'], 'seq_no_109')
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_106)
        self.assertIsNone(res_objs[0]['expansions']['expansion_key1'])
        self.assertIsNone(res_objs[0]['expansions']['expansion_key2'])
        self.assertIsNone(res_objs[0]['expansions']['expansion_key3'])
        self.assertIsNone(res_objs[0]['expansions']['expansion_key4'])
        self.assertIsNone(res_objs[0]['expansions']['expansion_key5'])

    def test_list_api_with_catalog_id_length(self):
        """Test list api.
        Test with no params.
        """
        path = '/catalog/%s/contents' % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_sort_key_length(self):
        """Test list api.
        Test with sort_key where is over length.
        """
        path = '/catalog/%s/contents?sort_key=%s' % \
            (CATALOG_ID_101, 'expansion_key1')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_sort_dir_length(self):
        """Test list api.
        Test with sort_dir where is over length.
        """
        path = '/catalog/%s/contents?sort_dir=%s' % (CATALOG_ID_101, 'dasc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_marker_length(self):
        """Test list api.
        Test with marker where is over length.
        """
        path = '/catalog/%s/contents?marker=%s' % (CATALOG_ID_101, 'a' * 65)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_limit_length(self):
        """Test list api.
        Test with limit where is over length.
        """
        path = '/catalog/%s/contents?limit=%s' % (CATALOG_ID_101, 'a')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_list_api_with_deleted_length(self):
        """Test list api.
        Test with force_show_deleted where is over length.
        """
        path = '/catalog/%s/contents?force_show_deleted=%s' % \
            (CATALOG_ID_101, 'turue')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:__member__'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)
