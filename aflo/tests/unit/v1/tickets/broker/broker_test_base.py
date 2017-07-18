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

from aflo.tests.unit import base

FILES_DIR = 'aflo/tests/unit/v1/tickets/broker/operation_definition_files'


class BrokerTestBase(base.WorkflowUnitTest):

    def _get_dict_contents(self, file_prefix, version=None):
        file_name = None
        if version:
            file_name = '%(file_prefix)s_%(version)s.json' % {
                'file_prefix': file_prefix, 'version': version}
        else:
            file_name = '%(file_prefix)s.json' % {
                'file_prefix': file_prefix}

        obj = open(os.path.join(FILES_DIR, file_name)).read()
        return json.loads(obj)

    def _create_workflow_pattern(self, db_models, id, **contents):
        model = db_models.WorkflowPattern(id=id,
                                          code=contents['wf_pattern_code'])
        model.wf_pattern_contents = contents
        model.save()
        return model

    def _create_ticket_template(self, db_models, id, wf_pattern_id,
                                **contents):
        model = db_models.TicketTemplate(id=id,
                                         workflow_pattern_id=wf_pattern_id)
        model.ticket_type = contents['ticket_type']
        model.template_contents = contents
        model.save()
        return model
