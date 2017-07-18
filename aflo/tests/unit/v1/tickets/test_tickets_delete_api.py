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

from aflo.common import exception
from aflo.db.sqlalchemy import api as db_api
from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests.unit.v1.tickets.stubs import Ticket_RpcStubs as stubs
from aflo.tests.unit.v1.tickets import utils as tickets_utils

CONF = cfg.CONF


class TestTicketsDeleteAPI(base.WorkflowUnitTest):
    """Do a test of 'Delete ticket'"""

    def create_fixtures(self):
        super(TestTicketsDeleteAPI, self).create_fixtures()

        self.tickets0, self.t0_workflows = \
            tickets_utils.create_ticket_for_update(db_models, 'tenant', 0)

        self.tickets1, self.t1_workflows = \
            tickets_utils.create_ticket_for_update(db_models, 'tenant', 1)

        self.tickets2, self.t2_workflows = \
            tickets_utils.create_ticket_for_update(db_models, 'tenant', 2)
        self.tickets2.delete()
        for wf_key in self.t2_workflows:
            self.t2_workflows[wf_key].delete()

    def test_delete_api(self):
        """Do a test of 'Delete ticket'
        Test of successful completion
        """

        # Create a request data
        path = '/tickets/%s' % self.tickets0.id
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_delete')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 200)

        # Compare the deleted data
        session = db_api.get_session()
        ticket = session.query(db_models.Ticket).\
            filter(db_models.Ticket.id == self.tickets0.id).one()
        self.assertTrue(ticket.deleted)
        workflows = session.query(db_models.Workflow).\
            filter(db_models.Workflow.ticket_id == self.tickets0.id).all()
        for wf in workflows:
            self.assertTrue(wf.deleted)

    def test_delete_api_no_authority_irregular(self):
        """Do a test of 'Delete ticket'
        Test cases run unauthorized.
        """

        # Create a request data
        path = '/tickets/%s' % self.tickets1.id
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:no_auth'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_delete')

        # Send request
        res = req.get_response(self.api)

        # Examination of response
        self.assertEqual(res.status_int, 403)

    def test_delete_api_no_exist_irregular(self):
        """Do a test of 'Delete ticket'
        Remove non-existent data.
        """

        # Create a request data
        path = '/tickets/%s' % '00000'
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_delete')

        # Send request
        self.assertRaises(exception.NotFound,
                          req.get_response,
                          self.api)

    def test_delete_api_remove_deleted_irregular(self):
        """Do a test of 'Delete ticket'
        Test to remove the deleted data.
        """

        # Create a request data
        path = '/tickets/%s' % self.tickets2.id
        req = unit_test_utils.get_fake_request(method='DELETE',
                                               path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}
        for k, v in headers.iteritems():
            req.headers[k] = v

        # set stubs
        # "stub_fake_call" is a stub in order to omit the queue transmission
        # When you use the "call_info",
        # you can confirm the call arguments of stub
        stubs.stub_fake_cast(self, 'tickets_delete')

        # Send request
        self.assertRaises(exception.NotFound,
                          req.get_response,
                          self.api)
