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

import json
import os
import testtools  # noqa
import uuid

from tempest.api.aflo import base
from tempest import config_aflo as config  # noqa
from tempest.lib import exceptions

CONF = config.CONF
FOLDER_PATH = 'tempest/api/aflo/operation_definition_files/'


class WorkflowPatternAdminTest(base.BaseV1AfloAdminTest):
    """Aflo Test Class by admin."""

    @classmethod
    def resource_setup(cls):
        """Setup Resources."""
        super(WorkflowPatternAdminTest, cls).resource_setup()

    def test_workflow_pattern(self):
        """Test 'Data Between Created to Deleted'"""
        # Create workflow pattern.
        workflow_pattern_id = \
            create_workflow_pattern(
                self,
                ["workflow_pattern_contents_one_approval.json"])

        # Delete workflow pattern.
        delete_workflow_pattern(self, workflow_pattern_id)

    def test_workflow_pattern_create_no_data_irreguler(self):
        """Test 'Create a workflow pattern'.
        Test the operation of the parameter without.
        """
        field = {}

        self.assertRaises(exceptions.BadRequest,
                          self.aflo_client.create_workflowpattern,
                          field)

    def test_workflow_pattern_delete_no_data_irreguler(self):
        """Test 'Delete the workflow pattern'.
        Test the operation of the parameter without.
        """
        id = None

        self.assertRaises(exceptions.NotFound,
                          self.aflo_client.delete_workflowpattern,
                          id)


class WorkflowPatternTest(base.BaseV1AfloTest):
    """Aflo Test Class."""

    @classmethod
    def resource_setup(cls):
        """Setup Resources."""
        super(WorkflowPatternTest, cls).resource_setup()

    def test_workflow_pattern_create_no_authority_irreguler(self):
        """Test 'Create a workflow pattern'.
        Test the operation of the Delete API(Not exist authority).
        """
        self.assertRaises(exceptions.Forbidden,
                          create_workflow_pattern,
                          self,
                          ["workflow_pattern_contents_one_approval.json"])

    def test_workflow_pattern_delete_no_authority_irreguler(self):
        """Test 'Delete a workflow pattern'.
        Test the operation of the Delete API(Not exist authority).
        """
        id = str(uuid.uuid4())

        self.assertRaises(exceptions.Forbidden,
                          delete_workflow_pattern,
                          self,
                          [id])


def create_workflow_pattern(self, file_names):
    """Test 'Create a workflow pattern'.
    :param file_names: Create workflow pattern files.
    """
    id = []

    for file_name in file_names:
        obj = open(os.path.join(FOLDER_PATH, file_name)).read()
        contents = json.loads(obj)

        field = {'wf_pattern_contents': contents}

        req, body = self.aflo_client.create_workflowpattern(field)
        workflow_patten = body

        self.assertTrue(workflow_patten['id'] is not None)

        id.append(workflow_patten['id'])

    return id


def delete_workflow_pattern(self, workflow_pattern_id):
    """Test 'Delete a workflow pattern'.
    :param workflow_pattern_id: List of workflow pattern id.
    """
    for id in workflow_pattern_id:
        self.aflo_client.delete_workflowpattern(id)
