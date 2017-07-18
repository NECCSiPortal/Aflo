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


def create_workflow_pattern(db_models, id, code):
    model = db_models.WorkflowPattern(id=id, code=code)
    model.wf_pattern_contents = {}
    model.save()
    return model


def create_ticket_template(db_models,
                           id,
                           workflow_pattern_id):
    model = db_models.TicketTemplate(id=id,
                                     workflow_pattern_id=workflow_pattern_id)
    model.ticket_type = "test"
    model.template_contents = {}
    model.save()
    return model
