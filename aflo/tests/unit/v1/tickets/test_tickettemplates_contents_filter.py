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

TT_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef01001'
TT_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef01002'

T_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef03001'
T_UUID2 = 'ea0a4146-fd07-414b-aa5e-dedbeef03002'

TAR_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef04001'

TEN_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef05001'

OWN_UUID1 = 'ea0a4146-fd07-414b-aa5e-dedbeef06001'


WF_UUID1_1 = 'ea0a4146-fd07-414b-aa5e-dedbeef02011'
WF_UUID1_2 = 'ea0a4146-fd07-414b-aa5e-dedbeef02012'


class TestTicketsListAPI(base.WorkflowUnitTest):
    """Do a test of 'List Search of tickets'"""

    def create_fixtures(self):
        super(TestTicketsListAPI, self).create_fixtures()

        # Create wrokflow pattern & ticket template
        tickets_utils.create_workflow_pattern(db_models, WFP_UUID1, 1)

        tickets_utils.create_ticket_template(db_models, TT_UUID1, WFP_UUID1, 1,
                                             template_contents_data=1)
        tickets_utils.create_ticket_template(db_models, TT_UUID2, WFP_UUID1, 2,
                                             template_contents_data=2)

        # Create ticket
        tickets_utils.create_ticket(db_models, T_UUID1, TT_UUID1,
                                    TAR_UUID1, TEN_UUID1, OWN_UUID1, 1)
        tickets_utils.create_ticket(db_models, T_UUID2, TT_UUID2,
                                    TAR_UUID1, TEN_UUID1, OWN_UUID1, 2)

        # Create workflow
        tickets_utils.create_workflow(db_models, WF_UUID1_1, T_UUID1, 1,
                                      'applied', '__member__',
                                      'confirmer01',
                                      datetime.date(2015, 1, 10), 1)
        tickets_utils.create_workflow(db_models, WF_UUID1_2, T_UUID2, 1,
                                      'applied_1st', 'director',
                                      'confirmer01',
                                      datetime.date(2015, 1, 10), 1)

    def test_index_api_ticket_template_name_param(self):
        """Do a test of 'List Search of tickets'
        Test with 'ticket_template_name' parameter.
        """

        # Create a request data
        path = '/tickets?ticket_template_name=%s' % ('ticket_template_name_jp')
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
        self.assertEqual(res_objs[0]['id'], T_UUID2)

    def test_index_api_application_kinds_name_param(self):
        """Do a test of 'List Search of tickets'
        Test with 'api_application_kinds_name' parameter.
        """

        # Create a request data
        path = '/tickets?application_kinds_name=%s' \
            % ('application_kinds_name_2_jp')
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
        self.assertEqual(res_objs[0]['id'], T_UUID2)

    def test_index_api_temlate_contents_multi_param(self):
        """Do a test of 'List Search of tickets'
        Test with template contents parameters.
        """

        # Create a request data
        path = ('/tickets?ticket_template_name=%s&' +
                'api_application_kinds_name=%s') \
            % ('ticket_template_name_jp',
               'api_application_kinds_name_2_jp')
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
        self.assertEqual(res_objs[0]['id'], T_UUID2)

    def test_index_api_not_exists_ticket_template_name_param(self):
        """Do a test of 'List Search of tickets'
        Test with not exists 'ticket_template_name' parameter.
        """

        # Create a request data
        path = '/tickets?ticket_template_name=%s' % ('aaaaa')
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

    def test_index_api_not_exists_application_kinds_name_param(self):
        """Do a test of 'List Search of tickets'
        Test with not exists 'api_application_kinds_name' parameter.
        """

        # Create a request data
        path = '/tickets?application_kinds_name=%s' \
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
