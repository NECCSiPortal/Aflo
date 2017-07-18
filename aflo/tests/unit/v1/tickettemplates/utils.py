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

WORKFLOW_PATTERN_DIR = 'aflo/tests/unit/v1/workflow_patterns/' \
    'operation_definition_files'
TICKET_TEMPLATE_DIR = 'aflo/tests/unit/v1/tickettemplates/' \
    'operation_definition_files'


def create_ticket(db_models,
                  id, ticket_template_id,
                  ticket_type="test"):
    model = db_models.Ticket(id=id)
    model.ticket_template_id = ticket_template_id
    model.ticket_type = ticket_type
    model.tenant_id = "xxxx-xxxx-xxxx-xxxx-xxxx"
    model.tenant_name = "tenant_name"
    model.owner_id = "owner_id"
    model.owner_name = "owner_name"
    model.owner_at = datetime.datetime.now()
    model.save()
    return model


def create_workflow(db_models, id, ticket_id):
    model = db_models.Workflow(id=id)
    model.ticket_id = ticket_id
    model.status = 1
    model.status_code = 'status_code'
    model.status_detail = {}
    model.target_role = 'role'
    model.confirmer_id = 'confirmer_id'
    model.confirmer_name = 'confirmer_name'
    model.confirmed_at = datetime.datetime.now()
    model.save()
    return model


def create_workflow_pattern(db_models, id, seq, invalid_role=False):
    model = db_models.WorkflowPattern(id=id, code='wf_test%s' % seq)

    contents = get_dict_contents(WORKFLOW_PATTERN_DIR,
                                 'workflow_pattern_contents')
    contents['wf_pattern_code'] = 'wfp%s' % seq
    if invalid_role:
        for status in contents['status_list'][0]['next_status']:
            status['grant_role'] = 'xxxx'

    model.wf_pattern_contents = contents
    model.save()
    return model


def create_ticket_template(db_models, id, workflow_pattern_id, seq,
                           ticket_type="test", target_id=[]):
    model = db_models.TicketTemplate(id=id,
                                     workflow_pattern_id=workflow_pattern_id)
    model.ticket_type = ticket_type
    model.template_contents = {'ticket_template_name': 'ticket%s' % seq,
                               'target_id': target_id}
    model.save()
    return model


def create_testdata(db_models, ticket_template_id,
                    workflow_pattern_id, seq, ticket_template_delete=False,
                    ticket_type="test", target_id=[]):
    create_workflow_pattern(db_models, workflow_pattern_id, seq)
    t_tmp = create_ticket_template(db_models, ticket_template_id,
                                   workflow_pattern_id, seq,
                                   ticket_type, target_id)
    if ticket_template_delete:
        t_tmp.delete()


def create_contract_info(db_models, target_id):
    """Register a valid catalog information necessary to contract"""
    lifetime_start = datetime.datetime.strptime(
        '2015/01/01 00:00:00', "%Y/%m/%d %H:%M:%S")
    lifetime_end = datetime.datetime.strptime(
        '2999/12/31 23:59:59', "%Y/%m/%d %H:%M:%S")

    # Create goods data
    count = 1
    goods_ids = []
    for catalog_id in target_id:
        goods_id = 'goods000-1111-2222-3333-00000000000%s' % count
        goods_ids.append(goods_id)
        goods_model = db_models.Goods(
            goods_id=goods_id,
            goods_name='goods_name_%s' % goods_id)
        goods_model.save()
        count = count + 1

    # Create catalog data
    for catalog_id in target_id:
        catalog_model = db_models.Catalog(
            catalog_id=catalog_id,
            catalog_name='catalog_name_%s' % catalog_id,
            lifetime_start=lifetime_start,
            lifetime_end=lifetime_end)
        catalog_model.save()

    # Create catalog contents data
    count = 1
    for catalog_id in target_id:
        catalog_contents_model = db_models.CatalogContents(
            seq_no=count,
            catalog_id=catalog_id,
            goods_id=goods_ids[count - 1],
            goods_num=100,
            expansion_key2='cores',
            expansion_key3='')
        catalog_contents_model.save()
        count = count + 1

    # Create catalog scope data
    count = 1
    for catalog_id in target_id:
        scope_id = 'scope000-1111-2222-3333-00000000000%s' % count
        catalog_scope_model = db_models.CatalogScope(
            id=scope_id,
            catalog_id=catalog_id,
            scope='Default',
            lifetime_start=lifetime_start,
            lifetime_end=lifetime_end)
        catalog_scope_model.save()
        count = count + 1

    # Create price data
    count = 1
    for catalog_id in target_id:
        price_model = db_models.Price(
            seq_no=count,
            catalog_id=catalog_id,
            scope='Default',
            price=count,
            lifetime_start=lifetime_start,
            lifetime_end=lifetime_end)
        price_model.save()
        count = count + 1


def get_dict_contents(folder, file_prefix, version=None):
    file_name = None
    if version:
        file_name = '%(file_prefix)s_%(version)s.json' % {
            'file_prefix': file_prefix, 'version': version}
    else:
        file_name = '%(file_prefix)s.json' % {'file_prefix': file_prefix}

    obj = open(os.path.join(folder, file_name)).read()
    return json.loads(obj)
