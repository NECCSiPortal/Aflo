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

from oslo_config import cfg
from oslo_serialization import jsonutils

from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
from aflo.tests.unit import utils as unit_test_utils
from aflo.tests.unit.v1.tickettemplates import utils

CONF = cfg.CONF

WF_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef00001'
WF_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef00002'
WF_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef00003'
WF_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef00004'
WF_UUID5 = 'ea0a4146-fd07-414b-aa5e-dedbeef00005'
WF_UUID_NO_ROLE = 'ea0a4146-fd07-414b-aa5e-dedbeef00010'

TT_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef01001'
TT_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef01002'
TT_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef01003'
TT_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef01004'
TT_UUID5 = 'ea0a4146-fd07-414b-aa5e-dedbeef01005'
TT_UUID6 = 'ea0a4146-fd07-414b-aa5e-dedbeef01006'
TT_UUID7 = 'ea0a4146-fd07-414b-aa5e-dedbeef01007'
TT_UUID_NO_ROLE = 'ea0a4146-fd07-414b-aa5e-dedbeef01010'


class TestTicketTemplatesListAPI(base.WorkflowUnitTest):
    """Do a test of 'List Search of tickettemplates'"""

    def create_fixtures(self):
        target_id1 = ['catalog0-1111-2222-3333-000000000001']
        target_id2 = ['catalog0-1111-2222-3333-000000000001',
                      'catalog0-1111-2222-3333-000000000002']

        super(TestTicketTemplatesListAPI, self).create_fixtures()

        utils.create_contract_info(db_models, target_id2)

        utils.create_testdata(db_models, TT_UUID1, WF_UUID1, 1,
                              ticket_type="New Contract")
        utils.create_testdata(db_models, TT_UUID2, WF_UUID2, 2,
                              ticket_type="New Contract")
        utils.create_testdata(db_models, TT_UUID3, WF_UUID3, 3,
                              ticket_type="request")
        utils.create_testdata(db_models, TT_UUID4, WF_UUID4, 4,
                              ticket_template_delete=True,
                              ticket_type="request")
        utils.create_ticket_template(db_models, TT_UUID5, WF_UUID1, 5)
        utils.create_ticket_template(db_models, TT_UUID6, WF_UUID1, 6,
                                     ticket_type="New Contract",
                                     target_id=target_id1)
        utils.create_ticket_template(db_models, TT_UUID7, WF_UUID1, 7,
                                     ticket_type="New Contract",
                                     target_id=target_id2)

        utils.create_workflow_pattern(db_models, WF_UUID_NO_ROLE, 8, True)
        utils.create_ticket_template(db_models,
                                     TT_UUID_NO_ROLE, WF_UUID_NO_ROLE, 8,
                                     ticket_type="New Contract",
                                     target_id=target_id1)

    def test_index_api_non_params(self):
        """Do a test of 'List Search of tickettemplates'
        Test the operation of the parameter without.
        """

        # Create a request data
        path = '/tickettemplates'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickettemplates']
        self.assertEqual(len(res_objs), 7)
        self.assertEqual(res_objs[0]['id'], TT_UUID_NO_ROLE)
        self.assertEqual(res_objs[1]['id'], TT_UUID7)
        self.assertEqual(res_objs[2]['id'], TT_UUID6)
        self.assertEqual(res_objs[3]['id'], TT_UUID5)
        self.assertEqual(res_objs[4]['id'], TT_UUID3)
        self.assertEqual(res_objs[5]['id'], TT_UUID2)
        self.assertEqual(res_objs[6]['id'], TT_UUID1)

    def test_index_api_all_params(self):
        """Do a test of 'List Search of tickettemplates'
        Test with allex parameters.
        """

        # Create a request data
        path = '/tickettemplates?marker=%s&limit=%d'\
            '&sort_key=%s&sort_dir=%s'\
            '&enable_expansion_filters=%s'\
            '&force_show_deleted=%s&ticket_type=%s' \
            % (TT_UUID1, 3, 'id', 'asc',
               'True',
               'True', 'New Contract,request')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickettemplates']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['id'], TT_UUID3)
        self.assertEqual(res_objs[1]['id'], TT_UUID4)
        self.assertEqual(res_objs[2]['id'], TT_UUID6)

    def test_index_api_response_empty_irregular(self):
        """Do a test of 'List Search of tickettemplates'
        Test if the retrieved result is of 0.
        """

        # Create a request data
        path = '/tickettemplates?marker=%s' % (TT_UUID1)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickettemplates']
        self.assertEqual(len(res_objs), 0)

    def test_index_api_no_authority_irregular(self):
        """Do a test of 'List Search of tickettemplates'
        Test cases run unauthorized.
        """

        # Create a request data
        path = '/tickettemplates'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:no_auth'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_index_api_marker_missing_irregular(self):
        """Do a test of 'List Search of tickettemplates'
        Test when the specified 'marker' does not exist.
        """

        # Create a request data
        path = '/tickettemplates?marker=%s' % (TT_UUID4)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 404)

    def test_index_api_force_show_deleted_no_authority_irregular(self):
        """Do a test of 'List Search of tickettemplates'
        Be ignored 'force_show_deleted' for no authority.
        """

        # Create a request data
        path = '/tickettemplates?force_show_deleted=%s' \
            % ('True')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickettemplates']
        self.assertEqual(len(res_objs), 7)
        self.assertEqual(res_objs[0]['id'], TT_UUID_NO_ROLE)
        self.assertEqual(res_objs[1]['id'], TT_UUID7)
        self.assertEqual(res_objs[2]['id'], TT_UUID6)
        self.assertEqual(res_objs[3]['id'], TT_UUID5)
        self.assertEqual(res_objs[4]['id'], TT_UUID3)
        self.assertEqual(res_objs[5]['id'], TT_UUID2)
        self.assertEqual(res_objs[6]['id'], TT_UUID1)

    def test_index_api_ticket_template_single_type(self):
        """Test 'List Search of ticket_type single value'"""
        # Create a request data
        path = '/tickettemplates?ticket_type=%s'\
            '&enable_expansion_filters=%s'\
            % ('request', 'True')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickettemplates']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['id'], TT_UUID3)

    def test_index_api_ticket_template_not_exists_type(self):
        """Test 'List Search of not exists ticket_type value'"""
        path = '/tickettemplates?ticket_type=%s' \
            % ('aaaaa')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickettemplates']
        self.assertEqual(len(res_objs), 0)

    def test_index_api_many_sort_key(self):
        """Do a test of 'List Search of tickettemplates'
        Test of if you specify multiple 'sort_key'.
        """

        # Create a request data
        path = '/tickettemplates?sort_key=%s&sort_key=%s'\
               '&sort_dir=%s&sort_dir=%s' \
            % ('workflow_pattern_id', 'id', 'asc', 'desc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickettemplates']
        self.assertEqual(len(res_objs), 7)
        self.assertEqual(res_objs[0]['id'], TT_UUID7)
        self.assertEqual(res_objs[1]['id'], TT_UUID6)
        self.assertEqual(res_objs[2]['id'], TT_UUID5)
        self.assertEqual(res_objs[3]['id'], TT_UUID1)
        self.assertEqual(res_objs[4]['id'], TT_UUID2)
        self.assertEqual(res_objs[5]['id'], TT_UUID3)
        self.assertEqual(res_objs[6]['id'], TT_UUID_NO_ROLE)

    def test_index_api_sort_dir_not_enough_irregular(self):
        """Do a test of 'List Search of tickettemplates'
        Test of if you specify multiple 'sort_key'.
        Pattern the number of 'sort_dir' is not enough.
        """

        # Create a request data
        path = '/tickettemplates?sort_key=%s&sort_key=%s&sort_key=%s'\
            '&sort_dir=%s&sort_dir=%s' \
            % ('workflow_pattern_id', 'id', 'created_at', 'asc', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_sort_key_not_enough_irregular(self):
        """Do a test of 'List Search of tickettemplates'
        Test of if you specify multiple 'sort_key'.
        Pattern the number of 'sort_key' is not enough.
        """

        # Create a request data
        path = '/tickettemplates?sort_key=%s'\
            '&sort_dir=%s&sort_dir=%s' \
            % ('workflow_pattern_id', 'asc', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_default_limit(self):
        """Do a test of 'List Search of tickettemplates'
        Or testing the default value of 'limit' is used.
        """

        # Create a request data
        path = '/tickettemplates'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Set value to 'limit_param_default'
        bk_limit_param_default = CONF.limit_param_default
        self.config(limit_param_default=2)

        # Send request
        res = req.get_response(self.api)

        # Set default value to 'limit_param_default'
        self.config(limit_param_default=bk_limit_param_default)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickettemplates']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['id'], TT_UUID_NO_ROLE)
        self.assertEqual(res_objs[1]['id'], TT_UUID7)

    def test_index_api_max_limit(self):
        """Do a test of 'List Search of tickettemplates'
        Test of whether the upper limit of 'limit' is used.
        """

        # Create a request data
        path = '/tickettemplates?limit=%s' % ('1000')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Set value to 'bk_api_limit_max'
        bk_api_limit_max = CONF.api_limit_max
        self.config(api_limit_max=2)

        # Send request
        res = req.get_response(self.api)

        self.config(api_limit_max=bk_api_limit_max)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickettemplates']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['id'], TT_UUID_NO_ROLE)
        self.assertEqual(res_objs[1]['id'], TT_UUID7)

    def test_index_api_min_limit(self):
        """Do a test of 'List Search of tickettemplates'
        Test of less than the lower limit of 'limit'.
        """

        # Create a request data
        path = '/tickettemplates?limit=%s' % ('-1')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:developer'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_unknown_sort_key_irregular(self):
        """Do a test of 'List Search of tickettemplates'
        Testing is not defined 'sort_key'.
        Uppercase key undefined.
        """

        # Create a request data
        path = '/tickettemplates?sort_key=%s&sort_dir=%s' \
            % ('ID', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_unknown_sort_dir_irregular(self):
        """Do a test of 'List Search of tickettemplates'
        Testing is not defined 'sort_dir'.
        Uppercase key undefined.
        """

        # Create a request data
        path = '/tickettemplates?sort_key=%s&sort_dir=%s' \
            % ('id', 'ASC')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_all_get_filter(self):
        """Test 'List Search of tickettemplates'
        Test the get data by filtering, it have valid catalog only.
        """
        # Create a request data
        path = '/tickettemplates?ticket_type=%s' \
            % ('New Contract,request')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickettemplates']
        self.assertEqual(len(res_objs), 6)
        self.assertEqual(res_objs[0]['id'], TT_UUID_NO_ROLE)
        self.assertEqual(res_objs[1]['id'], TT_UUID7)
        self.assertEqual(res_objs[2]['id'], TT_UUID6)
        self.assertEqual(res_objs[3]['id'], TT_UUID3)
        self.assertEqual(res_objs[4]['id'], TT_UUID2)
        self.assertEqual(res_objs[5]['id'], TT_UUID1)

    def test_index_api_all_get_filter_argument_irregular(self):
        """Test 'List Search of tickettemplates'
        Parameter to 'enable_expansion_filters' is invalid test.
        'True', 'False' only valid.
        'False' is returned if you specify an invalid parameter.
        """
        # Create a request data
        path = '/tickettemplates?ticket_type=%s&enable_expansion_filters=%s' \
            % ('New Contract,request', 'xxxxx')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickettemplates']
        self.assertEqual(len(res_objs), 6)
        self.assertEqual(res_objs[0]['id'], TT_UUID_NO_ROLE)
        self.assertEqual(res_objs[1]['id'], TT_UUID7)
        self.assertEqual(res_objs[2]['id'], TT_UUID6)
        self.assertEqual(res_objs[3]['id'], TT_UUID3)
        self.assertEqual(res_objs[4]['id'], TT_UUID2)
        self.assertEqual(res_objs[5]['id'], TT_UUID1)

    def test_index_api_irregular_not_exists_filter_config(self):
        """Test 'List Search of tickettemplates'
        Test the config of the value without.
        """

        # Create a request data
        path = '/tickettemplates?ticket_type=%s' \
            % ('New Contract,request')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Set value to 'bk_ticket_template_expansion_filters'
        bk_ticket_template_filters = \
            CONF.ticket_template_expansion_filters
        self.config(ticket_template_expansion_filters='')

        # Send request
        res = req.get_response(self.api)

        self.config(
            ticket_template_expansion_filters=bk_ticket_template_filters)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickettemplates']
        self.assertEqual(len(res_objs), 6)
        self.assertEqual(res_objs[0]['id'], TT_UUID_NO_ROLE)
        self.assertEqual(res_objs[1]['id'], TT_UUID7)
        self.assertEqual(res_objs[2]['id'], TT_UUID6)
        self.assertEqual(res_objs[3]['id'], TT_UUID3)
        self.assertEqual(res_objs[4]['id'], TT_UUID2)
        self.assertEqual(res_objs[5]['id'], TT_UUID1)

    def test_index_api_single_filter_config(self):
        """Test 'List Search of tickettemplates'
        Test the single config of the value without.
        """

        # Create a request data
        path = '/tickettemplates?ticket_type=%s' \
            '&enable_expansion_filters=%s' \
            % ('New Contract,request', 'True')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Set value to 'bk_ticket_template_expansion_filters'
        bk_ticket_template_filters = \
            CONF.ticket_template_expansion_filters
        self.config(ticket_template_expansion_filters='aflo.tickettemplates.'
                    'expansion_filters.valid_catalog_expansion_filter.'
                    'ValidCatalogExpansionFilter')

        # Send request
        res = req.get_response(self.api)

        self.config(
            ticket_template_expansion_filters=bk_ticket_template_filters)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickettemplates']
        self.assertEqual(len(res_objs), 4)
        self.assertEqual(res_objs[0]['id'], TT_UUID_NO_ROLE)
        self.assertEqual(res_objs[1]['id'], TT_UUID7)
        self.assertEqual(res_objs[2]['id'], TT_UUID6)
        self.assertEqual(res_objs[3]['id'], TT_UUID3)

    def test_index_api_filter_config_not_admin(self):
        """Test 'List Search of tickettemplates'
        Test the config of the value without.
        'True' is returned because it is not an admin authority.
        """

        # Create a request data
        path = '/tickettemplates?ticket_type=%s' \
            '&enable_expansion_filters=%s' \
            % ('New Contract,request', 'True')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:developer'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickettemplates']
        self.assertEqual(len(res_objs), 0)

    def test_index_api_irregular_invalid_filter_config(self):
        """Test 'List Search of tickettemplates'
        Test the config of the value without.
        Parameter to 'ticket_template_expansion_filters' is invalid test.
        """

        # Create a request data
        path = '/tickettemplates?ticket_type=%s' \
            '&enable_expansion_filters=%s' \
            % ('New Contract,request', 'True')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Set value to 'bk_ticket_template_expansion_filters'
        bk_ticket_template_filters = \
            CONF.ticket_template_expansion_filters
        self.config(ticket_template_expansion_filters='aflo.tickettemplates.'
                    'expansion_filters.xxxxx')

        # Send request
        res = req.get_response(self.api)

        self.config(
            ticket_template_expansion_filters=bk_ticket_template_filters)

        # Examination of response
        self.assertEqual(res.status_int, 404)
