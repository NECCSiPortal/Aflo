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
import json
import os
import uuid


FILES_DIR = 'aflo/tests/unit/v1/tickets/operation_definition_files'


def get_dict_contents(file_prefix, version=None):
    file_name = None
    if version:
        file_name = '%(file_prefix)s_%(version)s.json' % {
            'file_prefix': file_prefix, 'version': version}
    else:
        file_name = '%(file_prefix)s.json' % {
            'file_prefix': file_prefix}

    obj = open(os.path.join(FILES_DIR, file_name)).read()
    return json.loads(obj)


def create_workflow_pattern(db_models, id, seq, for_broker=False):
    model = db_models.WorkflowPattern(id=id, code='wf_test%s' % seq)
    if for_broker:
        model.wf_pattern_contents = get_dict_contents(
            'wf_pattern_contents_001')
    else:
        model.wf_pattern_contents = get_dict_contents(
            'wf_pattern_contents_002')
    model.save()
    return model


def create_ticket_template(db_models, id, workflow_pattern_id, seq,
                           for_broker=False, template_contents_data=1,
                           ticket_type="test"):
    model = db_models.TicketTemplate(id=id,
                                     workflow_pattern_id=workflow_pattern_id)
    model.ticket_type = ticket_type
    if for_broker:
        model.template_contents = get_dict_contents(
            'template_contents_001', '20160627')
    elif template_contents_data == 1:
        model.template_contents = get_dict_contents(
            'template_contents_002', '20160627')
    else:
        model.template_contents = get_dict_contents(
            'template_contents_003', '20160627')
    model.save()
    return model


def create_testdata(db_models, ticket_template_id,
                    workflow_pattern_id, seq, ticket_template_delete=False):
    create_workflow_pattern(db_models, workflow_pattern_id, seq)
    t_tmp = create_ticket_template(db_models, ticket_template_id,
                                   workflow_pattern_id, seq)
    if ticket_template_delete:
        t_tmp.delete()


def create_workflow(db_models, id, ticket_id, status, status_code,
                    target_role, confirmer_id, confirmed_at, seq):
    model = db_models.Workflow(id=id, ticket_id=ticket_id,
                               status=status,
                               status_code=status_code,
                               status_detail={'test': 'test%s' % seq},
                               target_role=target_role,
                               confirmer_id=confirmer_id,
                               confirmer_name='%s_name' % confirmer_id,
                               confirmed_at=confirmed_at,
                               additional_data={'description': 'test%s' % seq})
    model.save()
    return model


def create_ticket(db_models, id, ticket_template_id, target_id,
                  tenant_id, owner_id, seq,
                  owner_at=datetime.date(2015, 1, 1),
                  ticket_type="goods"):
    model = db_models.Ticket(id=id, ticket_template_id=ticket_template_id,
                             target_id=target_id,
                             ticket_type=ticket_type,
                             tenant_id=tenant_id,
                             owner_id=owner_id,
                             owner_name='%s_name' % owner_id,
                             owner_at=owner_at,
                             ticket_detail={'description': 'ticket%s' % seq},
                             action_detail={'status': 'applied'})
    model.save()
    return model


def create_ticket_for_update(db_models, tenant_id, seq):
    tt_uuid = str(uuid.uuid4())
    t_uuid = str(uuid.uuid4())

    create_testdata(db_models, tt_uuid, str(uuid.uuid4()), seq)

    template_contents = get_dict_contents(
        'template_contents_002', '20160627')
    ticket = db_models.Ticket(id=t_uuid, ticket_template_id=tt_uuid,
                              target_id='dummy',
                              ticket_type='goods',
                              tenant_id=tenant_id,
                              owner_id='dummy_owner_id',
                              owner_name='dummy_owner_name',
                              owner_at=datetime.date(2015, 1, 1),
                              ticket_detail={'description': 'ticket'},
                              action_detail=template_contents['action'])
    ticket.save()
    wf_pattern_contents = get_dict_contents('wf_pattern_contents_002')
    workflows = {}
    for status_detail in wf_pattern_contents['status_list']:
        if 'none' == status_detail['status_code']:
            status = 2
            confirmer_id = 'dummy_confirmer_id'
            confirmer_name = 'dummy_confirmer_name'
            confirmed_at = datetime.date(2015, 1, 1)
        elif 'applied_1st' == status_detail['status_code']:
            status = 1
            confirmer_id = 'dummy_confirmer_id'
            confirmer_name = 'dummy_confirmer_name'
            confirmed_at = datetime.date(2015, 1, 1)
        else:
            status = 0
            confirmer_id = None
            confirmer_name = None
            confirmed_at = None

        workflow = db_models.Workflow(id=str(uuid.uuid4()), ticket_id=t_uuid,
                                      status=status,
                                      status_code=status_detail['status_code'],
                                      status_detail=status_detail,
                                      target_role='admin',
                                      confirmer_id=confirmer_id,
                                      confirmer_name=confirmer_name,
                                      confirmed_at=confirmed_at,
                                      additional_data={})
        workflow.save()
        workflows[status_detail['status_code']] = workflow

    return ticket, workflows


def _create_testdata_for_broker_test(db_models, ticket_template_id,
                                     workflow_pattern_id, seq):
    wfp = create_workflow_pattern(db_models, workflow_pattern_id, seq, True)
    t_tmp = create_ticket_template(db_models, ticket_template_id,
                                   workflow_pattern_id, seq, True)
    return t_tmp, wfp


def create_ticket_for_broker_test(db_models, tenant_id, seq):
    tt_uuid = str(uuid.uuid4())
    t_uuid = str(uuid.uuid4())

    ticket_teamplate, wfp = _create_testdata_for_broker_test(
        db_models, tt_uuid, str(uuid.uuid4()), seq)

    template_contents_for_broker_test = get_dict_contents(
        'template_contents_001', '20160627')
    wf_pattern_contents = get_dict_contents('wf_pattern_contents_001')

    action_detail = template_contents_for_broker_test['action']
    ticket = db_models.Ticket(id=t_uuid, ticket_template_id=tt_uuid,
                              target_id='dummy',
                              ticket_type='goods',
                              tenant_id=tenant_id,
                              owner_id='dummy_owner_id',
                              owner_name='dummy_owner_name',
                              owner_at=datetime.date(2015, 1, 1),
                              ticket_detail={'description': 'ticket'},
                              action_detail=action_detail)
    ticket.save()

    workflows = {}
    for status_detail in wf_pattern_contents['status_list']:
        if 'none' == status_detail['status_code']:
            status = 2
            confirmer_id = 'dummy_confirmer_id'
            confirmer_name = 'dummy_confirmer_name'
            confirmed_at = datetime.date(2015, 1, 1)
        elif 'applied_1st' == status_detail['status_code']:
            status = 1
            confirmer_id = 'dummy_confirmer_id'
            confirmer_name = 'dummy_confirmer_name'
            confirmed_at = datetime.date(2015, 1, 1)
        else:
            status = 0
            confirmer_id = None
            confirmer_name = None
            confirmed_at = None

        workflow = db_models.Workflow(id=str(uuid.uuid4()), ticket_id=t_uuid,
                                      status=status,
                                      status_code=status_detail['status_code'],
                                      status_detail=status_detail,
                                      target_role='admin',
                                      confirmer_id=confirmer_id,
                                      confirmer_name=confirmer_name,
                                      confirmed_at=confirmed_at,
                                      additional_data={})
        workflow.save()
        workflows[status_detail['status_code']] = workflow

    return ticket, workflows, ticket_teamplate
