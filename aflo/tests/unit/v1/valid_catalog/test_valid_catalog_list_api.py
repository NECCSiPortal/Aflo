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
from aflo.db.sqlalchemy.models import Catalog
from aflo.db.sqlalchemy.models import CatalogScope
from aflo.db.sqlalchemy.models import Price
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
ID_110 = 'id0a4146-fd07-414b-aa5e-dedbeef00110'
ID_111 = 'id0a4146-fd07-414b-aa5e-dedbeef00111'
ID_112 = 'id0a4146-fd07-414b-aa5e-dedbeef00112'
ID_113 = 'id0a4146-fd07-414b-aa5e-dedbeef00113'
ID_114 = 'id0a4146-fd07-414b-aa5e-dedbeef00114'
ID_115 = 'id0a4146-fd07-414b-aa5e-dedbeef00115'

CATALOG_ID_101 = 'ea0a4146-fd07-414b-aa5e-dedbeef00101'
CATALOG_ID_102 = 'ea0a4146-fd07-414b-aa5e-dedbeef00102'
CATALOG_ID_103 = 'ea0a4146-fd07-414b-aa5e-dedbeef00103'
CATALOG_ID_104 = 'ea0a4146-fd07-414b-aa5e-dedbeef00104'

SCOPE_101 = 'bdb8f50f82da4370813e6ea797b1fb101'
SCOPE_102 = 'a0d58ee41a364026a1031aca2548fd102'
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
        Catalog(catalog_id=CATALOG_ID_101,
                region_id='region-000-111-222-333-1',
                catalog_name='CATALOG_NAME-1',
                lifetime_start=datetime(2016, 1, 1, 0, 0, 0, 000000),
                lifetime_end=datetime(2016, 9, 30, 23, 59, 59, 999999),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                deleted_at=None,
                deleted=False
                ).save(db_api.get_session())
        Catalog(catalog_id=CATALOG_ID_102,
                region_id='region-000-111-222-333-2',
                catalog_name='CATALOG_NAME-2',
                lifetime_start=datetime(2015, 1, 1, 0, 0, 0, 000000),
                lifetime_end=datetime(2017, 12, 31, 23, 59, 59, 999999),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                deleted_at=None,
                deleted=False
                ).save(db_api.get_session())
        Catalog(catalog_id=CATALOG_ID_103,
                region_id='region-000-111-222-333-3',
                catalog_name='CATALOG_NAME-3',
                lifetime_start=datetime(2015, 1, 1, 0, 0, 0, 000000),
                lifetime_end=datetime(2017, 12, 31, 23, 59, 59, 999999),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                deleted_at=None,
                deleted=False
                ).save(db_api.get_session())
        Catalog(catalog_id=CATALOG_ID_104,
                region_id='region-000-111-222-333-4',
                catalog_name='CATALOG_NAME-4',
                lifetime_start=datetime(2015, 1, 1, 0, 0, 0, 000000),
                lifetime_end=datetime(2017, 12, 31, 23, 59, 59, 999999),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                deleted_at=None,
                deleted=False
                ).save(db_api.get_session())

        CatalogScope(id=ID_101,
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_DEF,
                     lifetime_start=datetime(2016, 1, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2016, 2, 28, 23, 59, 59, 999999),
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
                     scope=SCOPE_DEF,
                     lifetime_start=datetime(2016, 4, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2016, 5, 31, 23, 59, 59, 999999),
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
                     scope=SCOPE_DEF,
                     lifetime_start=datetime(2016, 7, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2016, 7, 31, 23, 59, 59, 999999),
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
                     scope=SCOPE_DEF,
                     lifetime_start=datetime(2016, 8, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2016, 8, 31, 23, 59, 59, 999999),
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
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_DEF,
                     lifetime_start=datetime(2016, 10, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2016, 10, 31, 23, 59, 59, 999999),
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
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_101,
                     lifetime_start=datetime(2016, 2, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2016, 3, 31, 23, 59, 59, 999999),
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
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_101,
                     lifetime_start=datetime(2016, 5, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2016, 5, 31, 23, 59, 59, 999999),
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
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_101,
                     lifetime_start=datetime(2016, 6, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2016, 7, 31, 23, 59, 59, 999999),
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
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_101,
                     lifetime_start=datetime(2016, 8, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2016, 8, 31, 23, 59, 59, 999999),
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
        CatalogScope(id=ID_110,
                     catalog_id=CATALOG_ID_101,
                     scope=SCOPE_101,
                     lifetime_start=datetime(2016, 10, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2016, 10, 31, 23, 59, 59, 999999),
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
        CatalogScope(id=ID_111,
                     catalog_id=CATALOG_ID_102,
                     scope=SCOPE_102,
                     lifetime_start=datetime(2015, 1, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2015, 12, 31, 23, 59, 59, 999999),
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
        CatalogScope(id=ID_112,
                     catalog_id=CATALOG_ID_102,
                     scope=SCOPE_102,
                     lifetime_start=datetime(2015, 1, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2016, 12, 31, 23, 59, 59, 999999),
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
        CatalogScope(id=ID_113,
                     catalog_id=CATALOG_ID_102,
                     scope=SCOPE_DEF,
                     lifetime_start=datetime(2015, 1, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2017, 12, 31, 23, 59, 59, 999999),
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
        CatalogScope(id=ID_114,
                     catalog_id=CATALOG_ID_103,
                     scope=SCOPE_102,
                     lifetime_start=datetime(2015, 1, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2017, 12, 31, 23, 59, 59, 999999),
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
        CatalogScope(id=ID_115,
                     catalog_id=CATALOG_ID_104,
                     scope=SCOPE_102,
                     lifetime_start=datetime(2015, 1, 1, 0, 0, 0, 000000),
                     lifetime_end=datetime(2017, 12, 31, 23, 59, 59, 999999),
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

        Price(catalog_id=CATALOG_ID_101,
              scope=SCOPE_DEF,
              seq_no='1',
              price=100,
              lifetime_start=datetime(2016, 1, 1, 0, 0, 0, 000000),
              lifetime_end=datetime(2016, 2, 28, 23, 59, 59, 999999),
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              deleted_at=None,
              deleted=False
              ).save(db_api.get_session())
        Price(catalog_id=CATALOG_ID_101,
              scope=SCOPE_DEF,
              seq_no='2',
              price=110,
              lifetime_start=datetime(2016, 4, 1, 0, 0, 0, 000000),
              lifetime_end=datetime(2016, 5, 31, 23, 59, 59, 999999),
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              deleted_at=None,
              deleted=False
              ).save(db_api.get_session())
        Price(catalog_id=CATALOG_ID_101,
              scope=SCOPE_DEF,
              seq_no='3',
              price=120,
              lifetime_start=datetime(2016, 6, 1, 0, 0, 0, 000000),
              lifetime_end=datetime(2016, 6, 30, 23, 59, 59, 999999),
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              deleted_at=None,
              deleted=False
              ).save(db_api.get_session())
        Price(catalog_id=CATALOG_ID_101,
              scope=SCOPE_DEF,
              seq_no='4',
              price=130,
              lifetime_start=datetime(2016, 9, 1, 0, 0, 0, 000000),
              lifetime_end=datetime(2016, 9, 30, 23, 59, 59, 999999),
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              deleted_at=None,
              deleted=False
              ).save(db_api.get_session())
        Price(catalog_id=CATALOG_ID_101,
              scope=SCOPE_DEF,
              seq_no='5',
              price=140,
              lifetime_start=datetime(2016, 10, 1, 0, 0, 0, 000000),
              lifetime_end=datetime(2016, 10, 31, 23, 59, 59, 999999),
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              deleted_at=None,
              deleted=False
              ).save(db_api.get_session())
        Price(catalog_id=CATALOG_ID_101,
              scope=SCOPE_101,
              seq_no='6',
              price=200,
              lifetime_start=datetime(2016, 2, 1, 0, 0, 0, 000000),
              lifetime_end=datetime(2016, 3, 31, 23, 59, 59, 999999),
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              deleted_at=None,
              deleted=False
              ).save(db_api.get_session())
        Price(catalog_id=CATALOG_ID_101,
              scope=SCOPE_101,
              seq_no='7',
              price=210,
              lifetime_start=datetime(2016, 4, 1, 0, 0, 0, 000000),
              lifetime_end=datetime(2016, 4, 30, 23, 59, 59, 999999),
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              deleted_at=None,
              deleted=False
              ).save(db_api.get_session())
        Price(catalog_id=CATALOG_ID_101,
              scope=SCOPE_101,
              seq_no='8',
              price=220,
              lifetime_start=datetime(2016, 6, 1, 0, 0, 0, 000000),
              lifetime_end=datetime(2016, 7, 31, 23, 59, 59, 999999),
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              deleted_at=None,
              deleted=False
              ).save(db_api.get_session())
        Price(catalog_id=CATALOG_ID_101,
              scope=SCOPE_101,
              seq_no='9',
              price=230,
              lifetime_start=datetime(2016, 9, 1, 0, 0, 0, 000000),
              lifetime_end=datetime(2016, 9, 30, 23, 59, 59, 999999),
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              deleted_at=None,
              deleted=False
              ).save(db_api.get_session())
        Price(catalog_id=CATALOG_ID_101,
              scope=SCOPE_101,
              seq_no='10',
              price=240,
              lifetime_start=datetime(2016, 10, 1, 0, 0, 0, 000000),
              lifetime_end=datetime(2016, 10, 31, 23, 59, 59, 999999),
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              deleted_at=None,
              deleted=False
              ).save(db_api.get_session())
        Price(catalog_id=CATALOG_ID_102,
              scope=SCOPE_102,
              seq_no='11',
              price=1100,
              lifetime_start=datetime(2015, 1, 1, 0, 0, 0, 000000),
              lifetime_end=datetime(2017, 12, 31, 23, 59, 57, 999999),
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              deleted_at=None,
              deleted=False
              ).save(db_api.get_session())
        Price(catalog_id=CATALOG_ID_102,
              scope=SCOPE_DEF,
              seq_no='12',
              price=1200.55,
              lifetime_start=datetime(2017, 1, 1, 0, 0, 0, 000000),
              lifetime_end=datetime(2017, 12, 31, 23, 59, 56, 999999),
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              deleted_at=None,
              deleted=False
              ).save(db_api.get_session())
        Price(catalog_id=CATALOG_ID_102,
              scope=SCOPE_DEF,
              seq_no='13',
              price=1300,
              lifetime_start=datetime(2016, 1, 1, 0, 0, 0, 000000),
              lifetime_end=datetime(2017, 12, 31, 23, 59, 58, 999999),
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              deleted_at=None,
              deleted=False
              ).save(db_api.get_session())
        Price(catalog_id=CATALOG_ID_103,
              scope=SCOPE_102,
              seq_no='14',
              price=1400.144,
              lifetime_start=datetime(2015, 1, 1, 0, 0, 0, 000000),
              lifetime_end=datetime(2017, 12, 31, 23, 59, 55, 999999),
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              deleted_at=None,
              deleted=False
              ).save(db_api.get_session())
        Price(catalog_id=CATALOG_ID_104,
              scope=SCOPE_102,
              seq_no='15',
              price=999,
              lifetime_start=datetime(2015, 1, 1, 0, 0, 0, 000000),
              lifetime_end=datetime(2017, 12, 31, 23, 59, 59, 999999),
              created_at=datetime.utcnow(),
              updated_at=datetime.utcnow(),
              deleted_at=None,
              deleted=False
              ).save(db_api.get_session())

    def destroy_fixtures(self):
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_index_api_january_data(self):
        """Test 'List Search of validity catalog'
        Test pattern that are defined only in the public catalog.
        """

        # Create a request data
        path = '/catalogs?catalog_id=%s&scope=%s&lifetime=%s' % \
               (CATALOG_ID_101, SCOPE_101, '2016-01-10T23:59:59.999999')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['price'], '100.000')

    def test_index_api_february_data(self):
        """Test 'List Search of validity catalog'
        Test pattern in which all of the data are aligned.
        """

        # Create a request data
        path = '/catalogs?catalog_id=%s&scope=%s&lifetime=%s' % \
               (CATALOG_ID_101, SCOPE_101, '2016-02-10T23:59:59.999999')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['price'], '200.000')

    def test_index_api_march_data(self):
        """Test 'List Search of validity catalog'
        Test pattern that is only defined in the private catalogs.
        """

        # Create a request data
        path = '/catalogs?catalog_id=%s&scope=%s&lifetime=%s' % \
               (CATALOG_ID_101, SCOPE_101, '2016-03-10T23:59:59.999999')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['price'], '200.000')

    def test_index_api_april_data(self):
        """Test 'List Search of validity catalog'
        Test pattern there are public definition and
        private tenant scope are not aligned.
        """

        # Create a request data
        path = '/catalogs?catalog_id=%s&scope=%s&lifetime=%s' % \
               (CATALOG_ID_101, SCOPE_101, '2016-04-10T23:59:59.999999')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['price'], '110.000')

    def test_index_api_may_data(self):
        """Test 'List Search of validity catalog'
        Test pattern there are public definition and
        private price are not aligned.
        """

        # Create a request data
        path = '/catalogs?catalog_id=%s&scope=%s&lifetime=%s' % \
               (CATALOG_ID_101, SCOPE_101, '2016-05-10T23:59:59.999999')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['price'], '110.000')

    def test_index_api_june_data(self):
        """Test 'List Search of validity catalog'
        Test pattern there are private definition and
        public tenant scope are not aligned.
        """

        # Create a request data
        path = '/catalogs?catalog_id=%s&scope=%s&lifetime=%s' % \
               (CATALOG_ID_101, SCOPE_101, '2016-06-10T23:59:59.999999')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['price'], '220.000')

    def test_index_api_july_data(self):
        """Test 'List Search of validity catalog'
        Test pattern there are private definition and
        public price are not aligned.
        """

        # Create a request data
        path = '/catalogs?catalog_id=%s&scope=%s&lifetime=%s' % \
               (CATALOG_ID_101, SCOPE_101, '2016-07-10T23:59:59.999999')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['price'], '220.000')

    def test_index_api_august_data(self):
        """Test 'List Search of validity catalog'
        Test pattern there is no price information.
        """

        # Create a request data
        path = '/catalogs?catalog_id=%s&scope=%s&lifetime=%s' % \
               (CATALOG_ID_101, SCOPE_101, '2016-08-10T23:59:59.999999')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 0)

    def test_index_api_september_data(self):
        """Test 'List Search of validity catalog'
        Test pattern there is no catalog tenant information.
        """

        # Create a request data
        path = '/catalogs?catalog_id=%s&scope=%s&lifetime=%s' % \
               (CATALOG_ID_101, SCOPE_101, '2016-09-10T23:59:59.999999')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 0)

    def test_index_api_october_data(self):
        """Test 'List Search of validity catalog'
        Test pattern there is no catalog information.
        """

        # Create a request data
        path = '/catalogs?catalog_id=%s&scope=%s&lifetime=%s' % \
               (CATALOG_ID_101, SCOPE_101, '2016-10-10T23:59:59.999999')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 0)

    def test_index_api_lifetime_and_scope_only(self):
        """Test 'List Search of validity catalog'
        Test with lifetime and scope parameter.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s' % \
               ('2016-12-30T23:59:59.999999', SCOPE_102)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_104)
        self.assertEqual(res_objs[0]['catalog_scope_id'], ID_115)
        self.assertEqual(res_objs[0]['price_seq_no'], '15')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_103)
        self.assertEqual(res_objs[1]['catalog_scope_id'], ID_114)
        self.assertEqual(res_objs[1]['price_seq_no'], '14')
        self.assertEqual(res_objs[2]['catalog_id'], CATALOG_ID_102)
        self.assertEqual(res_objs[2]['catalog_scope_id'], ID_112)
        self.assertEqual(res_objs[2]['price_seq_no'], '11')

    def test_index_api_filter_catalog_id(self):
        """Test 'List Search of validity catalog'
        Test with catalog_id parameter.
        """

        # Create a request data
        path = '/catalogs?catalog_id=%s&lifetime=%s&scope=%s' % \
               (CATALOG_ID_103, '2016-10-10T23:59:59.999999', SCOPE_102)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_103)
        self.assertEqual(res_objs[0]['catalog_scope_id'], ID_114)
        self.assertEqual(res_objs[0]['price_seq_no'], '14')

    def test_index_api_filter_catalog_name(self):
        """Test 'List Search of validity catalog'
        Test with catalog_name parameter.
        """

        # Create a request data
        path = '/catalogs?catalog_name=%s&lifetime=%s&scope=%s' % \
               ('CATALOG_NAME-3', '2016-10-10T23:59:59.999999', SCOPE_102)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_103)
        self.assertEqual(res_objs[0]['catalog_scope_id'], ID_114)
        self.assertEqual(res_objs[0]['price_seq_no'], '14')

    def test_index_api_paginate_params(self):
        """Test 'List Search of catalog'
        Test with paginate parameters.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s&catalog_marker=%s' \
            '&catalog_scope_marker=%s&price_marker=%s&limit=%d' \
            '&sort_key=%s&sort_dir=%s' \
            % ('2016-12-10T23:59:59.999999', SCOPE_102, CATALOG_ID_104,
               ID_115, '15', 1, 'catalog_id', 'desc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_103)
        self.assertEqual(res_objs[0]['catalog_scope_id'], ID_114)
        self.assertEqual(res_objs[0]['price_seq_no'], '14')

    def test_index_api_refine_flg_param(self):
        """Test 'List Search of validity catalog'
        Test with refine_flg parameter.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s&refine_flg=%s' % \
               ('2017-12-10T23:59:59.999999', SCOPE_102, True)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_104)
        self.assertEqual(res_objs[0]['catalog_scope_id'], ID_115)
        self.assertEqual(res_objs[0]['price_seq_no'], '15')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_103)
        self.assertEqual(res_objs[1]['catalog_scope_id'], ID_114)
        self.assertEqual(res_objs[1]['price_seq_no'], '14')

    def test_index_api_non_lifetime_irregular(self):
        """Test 'List Search of validity catalog'
        Test the operation of the lifetime is none.
        """

        # Create a request data
        path = '/catalogs?scope=%s' % SCOPE_102
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_non_scope_irregular(self):
        """Test 'List Search of validity catalog'
        Test the operation of the scope is none.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s' % '2016-12-10T23:59:59.999999'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_lifetime_not_datetime_irregular(self):
        """Test 'List Search of validity catalog'
        Test with lifetime parameter where is not datetime.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s' % \
               ('2016-12-10T23:59:59', SCOPE_102)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_two_sort_key(self):
        """Test 'List Search of validity catalog'
        Test with two sort key.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s' \
               '&sort_key=%s&sort_dir=%s&sort_key=%s&sort_dir=%s' \
               % ('2017-12-10T23:59:59.999999', SCOPE_102,
                  'scope', 'asc', 'catalog_id', 'desc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_102)
        self.assertEqual(res_objs[0]['catalog_scope_id'], ID_113)
        self.assertEqual(res_objs[0]['price_seq_no'], '13')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_102)
        self.assertEqual(res_objs[1]['catalog_scope_id'], ID_113)
        self.assertEqual(res_objs[1]['price_seq_no'], '12')
        self.assertEqual(res_objs[2]['catalog_id'], CATALOG_ID_104)
        self.assertEqual(res_objs[2]['catalog_scope_id'], ID_115)
        self.assertEqual(res_objs[2]['price_seq_no'], '15')
        self.assertEqual(res_objs[3]['catalog_id'], CATALOG_ID_103)
        self.assertEqual(res_objs[3]['catalog_scope_id'], ID_114)
        self.assertEqual(res_objs[3]['price_seq_no'], '14')

    def test_index_api_sort_dir_not_enough_irregular(self):
        """Test 'List Search of validity catalog'
        Test of if you specify multiple 'sort_key'.
        Pattern the number of 'sort_dir' is not enough.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s&sort_key=%s' \
               '&sort_key=%s&sort_dir=%s&sort_key=%s&sort_dir=%s' \
               % ('2016-01-10T23:59:59.999999', SCOPE_102,
                  'catalog_lifetime_start',
                  'scope', 'asc', 'catalog_id', 'desc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_sort_key_not_enough_irregular(self):
        """Test 'List Search of validity catalog'
        Test of if you specify multiple 'sort_key'.
        Pattern the number of 'sort_dir' is not enough.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s&sort_dir=%s' \
               '&sort_key=%s&sort_dir=%s&sort_key=%s&sort_dir=%s' \
               % ('2016-01-10T23:59:59.999999', SCOPE_102, 'desc',
                  'scope', 'asc', 'catalog_id', 'desc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_default_limit(self):
        """Test 'List Search of validity catalog'
        Or testing the default value of 'limit' is used.
        """

        bk_limit_param_default = CONF.limit_param_default
        self.config(limit_param_default=2)

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s' % \
               ('2016-12-30T23:59:59.999999', SCOPE_102)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        self.config(limit_param_default=bk_limit_param_default)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_104)
        self.assertEqual(res_objs[0]['catalog_scope_id'], ID_115)
        self.assertEqual(res_objs[0]['price_seq_no'], '15')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_103)
        self.assertEqual(res_objs[1]['catalog_scope_id'], ID_114)
        self.assertEqual(res_objs[1]['price_seq_no'], '14')

    def test_index_api_max_limit(self):
        """Test 'List Search of validity catalog'
        Test of whether the upper limit of 'limit' is used.
        """

        bk_api_limit_max = CONF.api_limit_max
        self.config(api_limit_max=2)

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s' % \
               ('2016-12-30T23:59:59.999999', SCOPE_102)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        self.config(api_limit_max=bk_api_limit_max)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_104)
        self.assertEqual(res_objs[0]['catalog_scope_id'], ID_115)
        self.assertEqual(res_objs[0]['price_seq_no'], '15')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_103)
        self.assertEqual(res_objs[1]['catalog_scope_id'], ID_114)
        self.assertEqual(res_objs[1]['price_seq_no'], '14')

    def test_index_api_limit_not_int(self):
        """Test 'List Search of validity catalog'
        Test with limit parameter is not integer.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s&limit=%s' % \
               ('2016-12-10T23:59:59.999999', SCOPE_102, '2a')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_limit_not_plus(self):
        """Test 'List Search of validity catalog'
        Test with limit parameter is not natural number.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s&limit=%s' % \
               ('2016-12-10T23:59:59.999999', SCOPE_102, '-1')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_member_authority(self):
        """Test 'List Search of validity catalog'
        Test when it is executed by a user other than the administrator.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s' % '2017-12-30T23:59:59.999999'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:%s:__member__' % SCOPE_102}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_104)
        self.assertEqual(res_objs[0]['catalog_scope_id'], ID_115)
        self.assertEqual(res_objs[0]['price_seq_no'], '15')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_103)
        self.assertEqual(res_objs[1]['catalog_scope_id'], ID_114)
        self.assertEqual(res_objs[1]['price_seq_no'], '14')
        self.assertEqual(res_objs[2]['catalog_id'], CATALOG_ID_102)
        self.assertEqual(res_objs[2]['catalog_scope_id'], ID_113)
        self.assertEqual(res_objs[2]['price_seq_no'], '13')
        self.assertEqual(res_objs[3]['catalog_id'], CATALOG_ID_102)
        self.assertEqual(res_objs[3]['catalog_scope_id'], ID_113)
        self.assertEqual(res_objs[3]['price_seq_no'], '12')

    def test_index_api_member_authority_refine(self):
        """Test 'List Search of validity catalog'
        Test when it is executed by a user other than the administrator.
        And set refine_flg.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&refine_flg=%s' % \
               ('2017-12-30T23:59:59.999999', True)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:%s:__member__' % SCOPE_102}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_104)
        self.assertEqual(res_objs[0]['catalog_scope_id'], ID_115)
        self.assertEqual(res_objs[0]['price_seq_no'], '15')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_103)
        self.assertEqual(res_objs[1]['catalog_scope_id'], ID_114)
        self.assertEqual(res_objs[1]['price_seq_no'], '14')

    def test_index_api_member_authority_default(self):
        """Test 'List Search of validity catalog'
        Test when it is executed by a user other than the administrator.
        And set default to scope.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s' % \
               ('2017-12-30T23:59:59.999999', 'Default')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:%s:__member__' % SCOPE_102}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_102)
        self.assertEqual(res_objs[0]['catalog_scope_id'], ID_113)
        self.assertEqual(res_objs[0]['price_seq_no'], '13')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_102)
        self.assertEqual(res_objs[1]['catalog_scope_id'], ID_113)
        self.assertEqual(res_objs[1]['price_seq_no'], '12')

    def test_index_api_no_authority_irregular(self):
        """Test 'List Search of validity catalog'
        Test cases run unauthorized.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s' % \
               ('2016-12-30T23:59:59.999999', SCOPE_102)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:no_authority'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_index_api_with_catalog_marker_length(self):
        """Test 'List Search of validity catalog'
        Test with catalog marker parameter where is over length.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s&catalog_marker=%s' \
               '&catalog_scope_marker=%s&price_marker=%s' % \
               ('2016-12-30T23:59:59.999999', SCOPE_102, 'a' * 65,
                ID_113, '13')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_catalog_scope_marker_length(self):
        """Test 'List Search of validity catalog'
        Test with catalog scope marker parameter where is over length.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s&catalog_marker=%s' \
               '&catalog_scope_marker=%s&price_marker=%s' % \
               ('2016-12-30T23:59:59.999999', SCOPE_102, CATALOG_ID_102,
                'a' * 65, '13')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_price_marker_length(self):
        """Test 'List Search of validity catalog'
        Test with price marker parameter where is over length.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s&catalog_marker=%s' \
               '&catalog_scope_marker=%s&price_marker=%s' % \
               ('2016-12-30T23:59:59.999999', SCOPE_102, CATALOG_ID_102,
                ID_113, 'a' * 65)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_marker_empty_irregular(self):
        """Test 'List Search of validity catalog'
        Test with maker not found.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s&catalog_marker=%s' \
               '&catalog_scope_marker=%s&price_marker=%s' % \
               ('2016-12-30T23:59:59.999999', SCOPE_102, CATALOG_ID_102,
                ID_113, '10')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)

    def test_index_api_with_sort_key_not_supported(self):
        """Test 'List Search of validity catalog'
        Test with sort key parameter where is not supported.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s' \
               '&sort_key=%s&sort_dir=%s' % \
               ('2016-12-10T23:59:59.999999', SCOPE_102, 'seq_no', 'desc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_sort_dir_not_supported(self):
        """Test 'List Search of validity catalog'
        Test with sort dir parameter where is not supported.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s' \
               '&sort_key=%s&sort_dir=%s' % \
               ('2016-12-10T23:59:59.999999', SCOPE_102, 'scope', 'dasc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_with_sort_price(self):
        """Test 'List Search of validity catalog'
        Test with sort key is price.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s' \
               '&sort_key=%s&sort_dir=%s' % \
               ('2017-12-10T23:59:59.999999', SCOPE_102, 'price', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_104)
        self.assertEqual(res_objs[0]['catalog_scope_id'], ID_115)
        self.assertEqual(res_objs[0]['price_seq_no'], '15')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_102)
        self.assertEqual(res_objs[1]['catalog_scope_id'], ID_113)
        self.assertEqual(res_objs[1]['price_seq_no'], '12')
        self.assertEqual(res_objs[2]['catalog_id'], CATALOG_ID_102)
        self.assertEqual(res_objs[2]['catalog_scope_id'], ID_113)
        self.assertEqual(res_objs[2]['price_seq_no'], '13')
        self.assertEqual(res_objs[3]['catalog_id'], CATALOG_ID_103)
        self.assertEqual(res_objs[3]['catalog_scope_id'], ID_114)
        self.assertEqual(res_objs[3]['price_seq_no'], '14')

    def test_index_api_with_sort_lifetime(self):
        """Test 'List Search of validity catalog'
        Test with sort key is lifetime.
        """

        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s' \
               '&sort_key=%s&sort_dir=%s' % \
               ('2017-12-10T23:59:59.999999', SCOPE_102,
                'price_lifetime_end', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_103)
        self.assertEqual(res_objs[0]['catalog_scope_id'], ID_114)
        self.assertEqual(res_objs[0]['price_seq_no'], '14')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_102)
        self.assertEqual(res_objs[1]['catalog_scope_id'], ID_113)
        self.assertEqual(res_objs[1]['price_seq_no'], '12')
        self.assertEqual(res_objs[2]['catalog_id'], CATALOG_ID_102)
        self.assertEqual(res_objs[2]['catalog_scope_id'], ID_113)
        self.assertEqual(res_objs[2]['price_seq_no'], '13')
        self.assertEqual(res_objs[3]['catalog_id'], CATALOG_ID_104)
        self.assertEqual(res_objs[3]['catalog_scope_id'], ID_115)
        self.assertEqual(res_objs[3]['price_seq_no'], '15')

    def test_index_api_with_all_sort_key(self):
        """Test 'List Search of validity catalog'
        Test with all sort key.
        """
        # Create a request data
        path = '/catalogs?lifetime=%s&scope=%s' \
               '&sort_key=%s&sort_key=%s&sort_key=%s&sort_key=%s' \
               '&sort_key=%s&sort_key=%s&sort_key=%s&sort_key=%s' \
               '&sort_key=%s&sort_key=%s' % \
               ('2017-12-10T23:59:59.999999', SCOPE_102,
                'catalog_id', 'scope', 'catalog_name', 'price',
                'catalog_lifetime_start', 'catalog_lifetime_end',
                'catalog_scope_lifetime_start', 'catalog_scope_lifetime_end',
                'price_lifetime_start', 'price_lifetime_end')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['valid_catalog']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['catalog_id'], CATALOG_ID_104)
        self.assertEqual(res_objs[0]['catalog_scope_id'], ID_115)
        self.assertEqual(res_objs[0]['price_seq_no'], '15')
        self.assertEqual(res_objs[1]['catalog_id'], CATALOG_ID_103)
        self.assertEqual(res_objs[1]['catalog_scope_id'], ID_114)
        self.assertEqual(res_objs[1]['price_seq_no'], '14')
        self.assertEqual(res_objs[2]['catalog_id'], CATALOG_ID_102)
        self.assertEqual(res_objs[2]['catalog_scope_id'], ID_113)
        self.assertEqual(res_objs[2]['price_seq_no'], '13')
        self.assertEqual(res_objs[3]['catalog_id'], CATALOG_ID_102)
        self.assertEqual(res_objs[3]['catalog_scope_id'], ID_113)
        self.assertEqual(res_objs[3]['price_seq_no'], '12')
