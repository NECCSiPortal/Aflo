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

from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
from aflo.tests.unit import utils as unit_test_utils
from aflo.tests.unit.v1.tickets import utils as tickets_utils

CONF = cfg.CONF

WFP_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef00001'
WFP_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef00002'

TT_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef01001'
TT_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef01002'

WF_UUID1_1 = 'ea0a4146-fd07-414b-aa5e-dedbeef02011'
WF_UUID1_2 = 'ea0a4146-fd07-414b-aa5e-dedbeef02012'
WF_UUID1_3 = 'ea0a4146-fd07-414b-aa5e-dedbeef02013'
WF_UUID2_1 = 'ea0a4146-fd07-414b-aa5e-dedbeef02021'
WF_UUID2_2 = 'ea0a4146-fd07-414b-aa5e-dedbeef02022'
WF_UUID2_3 = 'ea0a4146-fd07-414b-aa5e-dedbeef02023'
WF_UUID3_1 = 'ea0a4146-fd07-414b-aa5e-dedbeef02031'
WF_UUID3_2 = 'ea0a4146-fd07-414b-aa5e-dedbeef02032'
WF_UUID3_3 = 'ea0a4146-fd07-414b-aa5e-dedbeef02033'
WF_UUID4_1 = 'ea0a4146-fd07-414b-aa5e-dedbeef02041'
WF_UUID4_2 = 'ea0a4146-fd07-414b-aa5e-dedbeef02042'
WF_UUID4_3 = 'ea0a4146-fd07-414b-aa5e-dedbeef02043'
WF_UUID5_1 = 'ea0a4146-fd07-414b-aa5e-dedbeef02051'
WF_UUID5_2 = 'ea0a4146-fd07-414b-aa5e-dedbeef02052'
WF_UUID5_3 = 'ea0a4146-fd07-414b-aa5e-dedbeef02053'
WF_UUID6_1 = 'ea0a4146-fd07-414b-aa5e-dedbeef02061'

T_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef03001'
T_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef03002'
T_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef03003'
T_UUID4 = 'ea0a4146-fd07-414b-aa5e-dedbeef03004'
T_UUID5 = 'ea0a4146-fd07-414b-aa5e-dedbeef03005'
T_UUID6 = 'ea0a4146-fd07-414b-aa5e-dedbeef03006'

TAR_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef04001'
TAR_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef04002'

TEN_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef05001'
TEN_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef05002'

OWN_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef06001'
OWN_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef06002'
OWN_UUID3 = 'ea0a4146-fd07-414b-aa5e-dedbeef06003'


class TestTicketsListAPI(base.WorkflowUnitTest):
    """Do a test of 'List Search of tickets'"""

    def create_fixtures(self):
        super(TestTicketsListAPI, self).create_fixtures()

        tickets_utils.create_workflow_pattern(db_models, WFP_UUID1, 1)
        tickets_utils.create_workflow_pattern(db_models, WFP_UUID2, 2)

        tickets_utils.create_ticket_template(db_models, TT_UUID1, WFP_UUID1, 1)
        tickets_utils.create_ticket_template(db_models, TT_UUID2, WFP_UUID2, 2)

        tickets_utils.create_ticket(db_models, T_UUID1, TT_UUID1,
                                    TAR_UUID1, TEN_UUID1, OWN_UUID1, 1,
                                    datetime.datetime(2015, 1, 1,
                                                      14, 59, 59, 999999))
        tickets_utils.create_ticket(db_models, T_UUID2, TT_UUID1,
                                    TAR_UUID1, TEN_UUID2, OWN_UUID3, 2,
                                    datetime.datetime(2015, 1, 1,
                                                      15, 0, 0, 000000))
        tickets_utils.create_ticket(db_models, T_UUID3, TT_UUID2,
                                    TAR_UUID2, TEN_UUID1, OWN_UUID2, 3,
                                    datetime.datetime(2015, 1, 1,
                                                      15, 0, 0, 1))
        ticket = tickets_utils.create_ticket(db_models, T_UUID4, TT_UUID2,
                                             TAR_UUID2, TEN_UUID1,
                                             OWN_UUID1, 4,
                                             datetime.datetime(2015, 1, 2,
                                                               14, 59, 59,
                                                               999999))
        ticket.delete()
        tickets_utils.create_ticket(db_models, T_UUID5, TT_UUID2,
                                    TAR_UUID2, TEN_UUID2, OWN_UUID3, 5,
                                    datetime.datetime(2015, 1, 2,
                                                      15, 0, 0, 999999),
                                    "request")
        tickets_utils.create_ticket(db_models, T_UUID6, TT_UUID2,
                                    TAR_UUID2, TEN_UUID2, OWN_UUID3, 6,
                                    datetime.datetime(2015, 1, 2,
                                                      15, 0, 0, 999999),
                                    "contract")

        tickets_utils.create_workflow(db_models, WF_UUID1_1, T_UUID1, 2,
                                      'applied', '__member__',
                                      'confirmer01',
                                      datetime.date(2015, 1, 10), 1)
        tickets_utils.create_workflow(db_models, WF_UUID1_2, T_UUID1, 1,
                                      'applied_1st', 'director',
                                      'confirmer02',
                                      datetime.datetime(2015, 1, 1,
                                                        14, 59, 59,
                                                        999999),
                                      2)
        tickets_utils.create_workflow(db_models, WF_UUID1_3, T_UUID1, 0,
                                      'applied_2nd', 'tenant_admin', None,
                                      None, 3)

        tickets_utils.create_workflow(db_models, WF_UUID2_1, T_UUID2, 2,
                                      'applied', '__member__',
                                      'confirmer02',
                                      datetime.date(2015, 1, 10), 1)
        tickets_utils.create_workflow(db_models, WF_UUID2_2, T_UUID2, 2,
                                      'applied_1st', 'director',
                                      'confirmer03',
                                      datetime.date(2015, 1, 13), 2)
        tickets_utils.create_workflow(db_models, WF_UUID2_3, T_UUID2, 1,
                                      'applied_2nd', 'tenant_admin',
                                      'confirmer04',
                                      datetime.datetime(2015, 1, 1,
                                                        15, 0, 0,
                                                        000000),
                                      3)

        tickets_utils.create_workflow(db_models, WF_UUID3_1, T_UUID3, 2,
                                      'applied', '__member__',
                                      'confirmer02',
                                      datetime.date(2015, 1, 10), 1)
        tickets_utils.create_workflow(db_models, WF_UUID3_2, T_UUID3, 2,
                                      'applied_1st', 'director',
                                      'confirmer03',
                                      datetime.date(2015, 1, 13), 2)
        tickets_utils.create_workflow(db_models, WF_UUID3_3, T_UUID3, 1,
                                      'applied_2nd', 'tenant_admin',
                                      'confirmer04',
                                      datetime.datetime(2015, 1, 1,
                                                        15, 0, 0, 1),
                                      3)

        tickets_utils.create_workflow(db_models, WF_UUID4_1, T_UUID4, 2,
                                      'applied', '__member__', 'confirmer01',
                                      datetime.date(2015, 1, 12), 1)
        tickets_utils.create_workflow(db_models, WF_UUID4_2, T_UUID4, 1,
                                      'applied_1st', 'director', 'confirmer02',
                                      datetime.datetime(2015, 1, 2,
                                                        14, 59, 59,
                                                        999999),
                                      2)
        tickets_utils.create_workflow(db_models, WF_UUID4_3, T_UUID4, 0,
                                      'applied_2nd', 'tenant_admin', None,
                                      None, 3)

        tickets_utils.create_workflow(db_models, WF_UUID5_1, T_UUID5, 2,
                                      'applied', '__member__', 'confirmer01',
                                      datetime.date(2015, 1, 11), 1)
        tickets_utils.create_workflow(db_models, WF_UUID5_2, T_UUID5, 1,
                                      'applied_1st', 'director', 'confirmer01',
                                      datetime.datetime(2015, 1, 2,
                                                        15, 0, 0,
                                                        999999),
                                      2)
        tickets_utils.create_workflow(db_models, WF_UUID5_3, T_UUID5, 0,
                                      'applied_2nd', 'tenant_admin', None,
                                      None, 3)

        tickets_utils.create_workflow(db_models, WF_UUID6_1, T_UUID6, 1,
                                      'applied', '__member__', 'confirmer01',
                                      datetime.date(2015, 1, 11), 1)

    def test_index_api_non_params(self):
        """Do a test of 'List Search of tickets'
        Test the operation of the parameter without.
        """

        # Create a request data
        path = '/tickets'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 5)
        self.assertEqual(res_objs[0]['id'], T_UUID6)
        self.assertEqual(res_objs[0]['last_workflow']['id'], WF_UUID6_1)
        self.assertEqual(res_objs[1]['id'], T_UUID5)
        self.assertEqual(res_objs[1]['last_workflow']['id'], WF_UUID5_2)

    def test_index_api_paginate_params(self):
        """Do a test of 'List Search of tickets'
        Test with paginate parameters.
        """

        # Create a request data
        path = '/tickets?marker=%s&limit=%d'\
            '&sort_key=%s&sort_dir=%s&force_show_deleted=%s&ticket_type=%s' \
            % (T_UUID1, 3, 'id', 'asc', 'True', 'goods')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['id'], T_UUID2)
        self.assertEqual(res_objs[1]['id'], T_UUID3)
        self.assertEqual(res_objs[2]['id'], T_UUID4)

    def test_index_api_tenant_id_param(self):
        """Do a test of 'List Search of tickets'
        Test with tenant_id parameter.
        """

        # Create a request data
        path = '/tickets?tenant_id=%s' \
            % (TEN_UUID1)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['id'], T_UUID3)
        self.assertEqual(res_objs[1]['id'], T_UUID1)

    def test_index_api_ticket_template_id_param(self):
        """Do a test of 'List Search of tickets'
        Test with ticket_template_id parameter.
        """

        # Create a request data
        path = '/tickets?ticket_template_id=%s' \
            % (TT_UUID1)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['id'], T_UUID2)
        self.assertEqual(res_objs[1]['id'], T_UUID1)

    def test_index_api_target_id_param(self):
        """Do a test of 'List Search of tickets'
        Test with target_id parameter.
        """

        # Create a request data
        path = '/tickets?target_id=%s' \
            % (TAR_UUID1)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['id'], T_UUID2)
        self.assertEqual(res_objs[1]['id'], T_UUID1)

    def test_index_api_owner_id_param(self):
        """Do a test of 'List Search of tickets'
        Test with owner_id parameter.
        """

        # Create a request data
        path = '/tickets?owner_id=%s' \
            % (OWN_UUID1)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['id'], T_UUID1)

    def test_index_api_owner_name_param(self):
        """Do a test of 'List Search of tickets'
        Test with owner_name parameter.
        """

        # Create a request data
        path = '/tickets?owner_name=%s' \
            % (OWN_UUID3 + '_name')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['id'], T_UUID6)
        self.assertEqual(res_objs[1]['id'], T_UUID5)
        self.assertEqual(res_objs[2]['id'], T_UUID2)

    def test_index_api_owner_at_param(self):
        """Do a test of 'List Search of tickets'
        Test with owner_at parameter.
        """

        # Create a request data
        path = '/tickets?owner_at_from=%s&owner_at_to=%s' \
               '&force_show_deleted=%s&sort_key=%s&sort_dir=%s' \
            % ('2015-01-01T15:00:00.000000', '2015-01-02T14:59:59.999999',
               'True', 'id', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['id'], T_UUID2)
        self.assertEqual(res_objs[1]['id'], T_UUID3)
        self.assertEqual(res_objs[2]['id'], T_UUID4)

    def test_index_api_last_status_code_param(self):
        """Do a test of 'List Search of tickets'
        Test with last_status_code parameter.
        """

        # Create a request data
        path = '/tickets?last_status_code=%s' \
            % ('applied_1st')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['id'], T_UUID5)
        self.assertEqual(res_objs[1]['id'], T_UUID1)

    def test_index_api_last_confirmer_id_param(self):
        """Do a test of 'List Search of tickets'
        Test with last_confirmer_id parameter.
        """

        # Create a request data
        path = '/tickets?last_confirmer_id=%s' \
            % ('confirmer02')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 1)
        self.assertEqual(res_objs[0]['id'], T_UUID1)

    def test_index_api_last_confirmer_name_param(self):
        """Do a test of 'List Search of tickets'
        Test with last_confirmer_name parameter.
        """

        # Create a request data
        path = '/tickets?last_confirmer_name=%s' \
            % ('confirmer04_name')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['id'], T_UUID3)
        self.assertEqual(res_objs[1]['id'], T_UUID2)

    def test_index_api_last_confirmed_at_param(self):
        """Do a test of 'List Search of tickets'
        Test with last_confirmed_at parameter.
        """

        # Create a request data
        path = '/tickets?last_confirmed_at_from=%s&last_confirmed_at_to=%s' \
               '&force_show_deleted=%s&sort_key=%s&sort_dir=%s' \
            % ('2015-01-01T15:00:00.000000', '2015-01-02T14:59:59.999999',
               'True', 'id', 'asc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v
        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 3)
        self.assertEqual(res_objs[0]['id'], T_UUID2)
        self.assertEqual(res_objs[1]['id'], T_UUID3)
        self.assertEqual(res_objs[2]['id'], T_UUID4)

    def test_index_api_response_empty_irregular(self):
        """Do a test of 'List Search of tickets'
        Test if the retrieved result is of 0.
        """

        # Create a request data
        path = '/tickets?marker=%s' % (T_UUID1)
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 0)

    def test_index_api_many_sort_key(self):
        """Do a test of 'List Search of tickets'
        Test of if you specify multiple 'sort_key'.
        """

        # Create a request data
        path = '/tickets?sort_key=%s&sort_key=%s&sort_dir=%s&sort_dir=%s' \
            % ('ticket_template_id', 'id', 'asc', 'desc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 5)
        self.assertEqual(res_objs[0]['id'], T_UUID2)
        self.assertEqual(res_objs[1]['id'], T_UUID1)
        self.assertEqual(res_objs[2]['id'], T_UUID6)
        self.assertEqual(res_objs[3]['id'], T_UUID5)
        self.assertEqual(res_objs[4]['id'], T_UUID3)

    def test_index_api_sort_dir_not_enough_irregular(self):
        """Do a test of 'List Search of tickets'
        Test of if you specify multiple 'sort_key'.
        Pattern the number of 'sort_dir' is not enough.
        """

        # Create a request data
        path = '/tickets?sort_key=%s&sort_key=%s&sort_key=%s'\
            '&sort_dir=%s&sort_dir=%s' \
            % ('ticket_template_id', 'id', 'created_at', 'asc', 'desc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_sort_key_not_enough_irregular(self):
        """Do a test of 'List Search of tickets'
        Test of if you specify multiple 'sort_key'.
        Pattern the number of 'sort_key' is not enough.
        """

        # Create a request data
        path = '/tickets?sort_key=%s'\
            '&sort_dir=%s&sort_dir=%s' \
            % ('ticket_template_id', 'asc', 'desc')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 400)

    def test_index_api_default_limit(self):
        """Do a test of 'List Search of tickets'
        Or testing the default value of 'limit' is used.
        """

        # Create a request data
        bk_limit_param_default = CONF.limit_param_default
        self.config(limit_param_default=2)

        path = '/tickets'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        self.config(limit_param_default=bk_limit_param_default)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['id'], T_UUID6)
        self.assertEqual(res_objs[1]['id'], T_UUID5)

    def test_index_api_max_limit(self):
        """Do a test of 'List Search of tickets'
        Test of whether the upper limit of 'limit' is used.
        """

        # Create a request data
        bk_api_limit_max = CONF.api_limit_max
        self.config(api_limit_max=2)

        path = '/tickets'
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        self.config(api_limit_max=bk_api_limit_max)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['id'], T_UUID6)
        self.assertEqual(res_objs[1]['id'], T_UUID5)

    def test_index_api_multi_ticket_type_or(self):
        """Test 'List Search of tickets'
        Test with multi ticket type parameter.
        """

        # Create a request data
        path = '/tickets?ticket_type=%s' \
            % ('contract,request')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 2)
        self.assertEqual(res_objs[0]['id'], T_UUID6)
        self.assertEqual(res_objs[1]['id'], T_UUID5)

    def test_index_api_multi_ticket_type_and(self):
        """Test 'List Search of tickets'
        Test with multi ticket type parameter.
        """

        # Create a request data
        path = '/tickets?ticket_type=%s&ticket_type=%s' \
            % ('contract,request', 'request')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 1)

    def test_index_api_not_exists_ticket_type(self):
        """Test 'List Search of tickets'
        Test with not exists ticket type parameter.
        """

        # Create a request data
        path = '/tickets?ticket_type=%s' \
            % ('aaaaa')
        req = unit_test_utils.get_fake_request(method='GET', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)
        res_objs = jsonutils.loads(res.body)['tickets']
        self.assertEqual(len(res_objs), 0)
