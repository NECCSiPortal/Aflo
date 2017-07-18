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

from tempest.api.aflo.fixture import sample_set_catalog_monthly as fixture
from tempest.api.aflo import test_workflowpattern

CONF = config.CONF
FOLDER_PATH = 'tempest/api/aflo/operation_definition_files/'


class TicketTemplateAdminTest(base.BaseV1AfloAdminTest):
    """Aflo Test Class by admin."""

    @classmethod
    def resource_setup(cls):
        """Setup Resources."""
        super(TicketTemplateAdminTest, cls).resource_setup()

    def test_ticket_template(self):
        """Test 'Data Between Created to Deleted'"""
        # Get contract info ids.
        goods_ids, catalog_ids, contents_ids, scope_ids, price_ids = \
            get_contract_info_ids(self)

        # Get invalid contract info ids.
        i_goods_ids, i_catalog_ids, i_cont_ids, i_scope_ids, i_price_ids = \
            get_contract_info_ids(self, False)

        # Create data.
        workflow_pattern_id = \
            test_workflowpattern.create_workflow_pattern(
                self,
                ["workflow_pattern_contents_001.json",
                 "workflow_pattern_contents_002.json",
                 "workflow_pattern_contents_003.json"])

        ticket_template_ids = []
        ticket_template_id = create_ticket_template(
            self,
            ["ticket_template_contents_001"], '20160627')
        ticket_template_ids.append(ticket_template_id[0])
        # Valid catalog data.
        ticket_template_id = create_ticket_template(
            self,
            ["ticket_template_contents_002"],
            '20160627', catalog_ids)
        ticket_template_ids.append(ticket_template_id[0])
        # Invalid catalog data.
        ticket_template_id = create_ticket_template(
            self,
            ["ticket_template_contents_003"],
            '20160627', i_catalog_ids)
        ticket_template_ids.append(ticket_template_id[0])

        # Get a ticket template.
        self._test_get_ticket_template(ticket_template_ids)

        # Delete data.
        delete_ticket_template(self, ticket_template_ids)
        test_workflowpattern.delete_workflow_pattern(
            self, workflow_pattern_id)

        delete_contract_info_data(self,
                                  None,
                                  goods_ids,
                                  catalog_ids,
                                  contents_ids,
                                  scope_ids,
                                  price_ids)
        delete_contract_info_data(self,
                                  None,
                                  i_goods_ids,
                                  i_catalog_ids,
                                  i_cont_ids,
                                  i_scope_ids,
                                  i_price_ids)

    def _test_get_ticket_template(self, ticket_template_id):
        """Test 'Get a list of ticket template'.
        :param ticket_template_id: List of ticket template id.
        """
        resp, body = self.aflo_client.list_tickettemplate()
        self._check_template(body, ticket_template_id)

        resp, body = self.aflo_client.list_tickettemplate(
            "ticket_type=New+Contract,request")
        self._check_template(body, ticket_template_id)

        resp, body = self.aflo_client.list_tickettemplate(
            "sort_key=created_at&sort_key=updated_at"
            "&sort_dir=asc&sort_dir=asc&ticket_type=New+Contract")
        self._check_template(body,
                             [ticket_template_id[1],
                              ticket_template_id[2]])

        resp, body = self.aflo_client.list_tickettemplate(
            "enable_expansion_filters=false")
        self._check_template(body, ticket_template_id)

        resp, body = self.aflo_client.list_tickettemplate(
            "enable_expansion_filters=true")
        self._check_template(body,
                             [ticket_template_id[0],
                              ticket_template_id[1]])

        # Invalid values will be the same as 'False'.
        resp, body = self.aflo_client.list_tickettemplate(
            "enable_expansion_filters=aaaaaa")
        self._check_template(body, ticket_template_id)

        resp, body = self.aflo_client.get_tickettemplate(
            ticket_template_id[0])
        self.assertEqual(body['id'], ticket_template_id[0])

    def _check_template(self, body, ticket_template_id):
        count = 0
        for template in ticket_template_id:
            for db_template in body:
                if template == db_template['id']:
                    count = count + 1
        self.assertTrue(count == len(ticket_template_id))

    def test_get_tiket_template_irregular_ticket_type(self):
        """Test 'List search of ticket template.'
        Test of if you filtering irregular ticket type.
        """
        # Create data.
        workflow_pattern_id = \
            test_workflowpattern.create_workflow_pattern(
                self, ["workflow_pattern_contents_001.json"])
        ticket_template_id = create_ticket_template(
            self, ["ticket_template_contents_001"], '20160627')

        resp, body = self.aflo_client.list_tickettemplate(
            "ticket_type=aaaaa")

        self.assertTrue(len(body) == 0)

        # Delete data.
        delete_ticket_template(self, ticket_template_id)
        test_workflowpattern.delete_workflow_pattern(
            self, workflow_pattern_id)

    def test_ticket_template_create_no_data_irreguler(self):
        """Test 'Create a ticket template'.
        Test the operation of the parameter without.
        """
        field = {}

        self.assertRaises(exceptions.BadRequest,
                          self.aflo_client.create_tickettemplate,
                          field)

    def test_ticket_template_delete_no_data_irreguler(self):
        """Test 'Delete the ticket template'.
        Test the operation of the parameter without.
        """
        id = None

        self.assertRaises(exceptions.NotFound,
                          self.aflo_client.delete_tickettemplate,
                          id)


class TicketTemplateTest(base.BaseV1AfloTest):
    """Aflo Test Class."""

    @classmethod
    def resource_setup(cls):
        """Setup Resources."""
        super(TicketTemplateTest, cls).resource_setup()

    def test_ticket_template_create_no_authority_irreguler(self):
        """Test 'Create a ticket template'.
        Test the operation of the Delete API(Not exist authority).
        """
        self.assertRaises(exceptions.Forbidden,
                          create_ticket_template,
                          self,
                          ["ticket_template_contents_001"], '20160627')

    def test_ticket_template_delete_no_authority_irreguler(self):
        """Test 'Delete a ticket template'.
        Test the operation of the Delete API(Not exist authority).
        """
        id = str(uuid.uuid4())

        self.assertRaises(exceptions.Forbidden,
                          self.aflo_client.delete_tickettemplate,
                          id)


def create_ticket_template(self, files_prefix, version, catalogs=None,
                           cancelling_template_id=None):
    """Test 'Create a ticket template'.
    :param files_prefix: Create ticket template files prefix.
    :param catalogs: Catalog ids.
    :param cancelling_template_id: Cancelling template id.
    """
    id = []

    for file_prefix in files_prefix:
        file_name = '%(file_prefix)s_%(version)s.json' \
            % {'file_prefix': file_prefix, 'version': version}
        obj = open(os.path.join(FOLDER_PATH, file_name)).read()
        contents = json.loads(obj)

        if catalogs:
            contents['target_id'] = catalogs

        if cancelling_template_id:
            contents['cancelling_template']['id'] = cancelling_template_id

        field = {'template_contents': contents}

        req, body = self.aflo_client.create_tickettemplate(field)
        ticket_template = body

        self.assertTrue(ticket_template['id'] is not None)

        id.append(ticket_template['id'])

    return id


def delete_ticket_template(self, ticket_template_id):
    """Test 'Delete a ticket template'.
    :param workflow_pattern_id: List of workflow pattern id.
    """
    for id in ticket_template_id:
        self.aflo_client.delete_tickettemplate(id)


def get_contract_info_ids(self, valid_flag=True):
    """Get contract info ids.
    :param valid_flag: It will determine whether valid or.
    """
    count = 0
    goods_ids = []
    catalog_ids = []
    contents_ids = []
    catalog_scope_ids = []
    price_ids = []

    goods_data_list = fixture.GOODS_DATA_LIST
    for goods_data in goods_data_list:
        # Create goods data.
        req, goods = self.aflo_client.create_goods(goods_data)
        goods_id = goods['goods_id']
        goods_ids.append(goods_id)

        # Create catalog data.
        if valid_flag:
            catalog_data = fixture.CATALOG_DATA_LIST[count]
        else:
            catalog_data = fixture.INVALID_CATALOG_DATA_LIST[count]
        catalog_field = {'catalog_name': catalog_data.get('catalog_name'),
                         'lifetime_start': catalog_data.get('lifetime_start'),
                         'lifetime_end': catalog_data.get('lifetime_end')}
        req, catalog = self.aflo_client.create_catalog(catalog_field)
        catalog_id = catalog['catalog_id']
        catalog_ids.append(catalog_id)

        # Create catalog contents data.
        cont_data = fixture.CATALOG_CONTENTS_DATA_LIST[count]
        contents_field = {'goods_id': goods_id,
                          'goods_num': cont_data.get('goods_num'),
                          'expansion_key2': cont_data.get('expansion_key2'),
                          'expansion_key3': cont_data.get('expansion_key3')}
        req, contents = self.aflo_client.create_catalog_contents(
            catalog_id,
            contents_field)
        contents_ids.append(contents['seq_no'])

        # Create catalog scope data.
        if valid_flag:
            scope_data = fixture.CATALOG_SCOPE_DATA_LIST[count]
        else:
            scope_data = fixture.INVALID_CATALOG_SCOPE_DATA_LIST[count]
        scope_field = {'lifetime_start': scope_data.get('lifetime_start'),
                       'lifetime_end': scope_data.get('lifetime_end')}
        req, catalog_scope = self.aflo_client.create_catalog_scope(
            catalog_id,
            scope_data.get('scope'),
            scope_field)
        catalog_scope_ids.append(catalog_scope['id'])

        # Create price data.
        if valid_flag:
            price_data = fixture.PRICE_DATA_LIST[count]
        else:
            price_data = fixture.INVALID_PRICE_DATA_LIST[count]
        price_field = {'price': price_data.get('price'),
                       'lifetime_start': price_data.get('lifetime_start'),
                       'lifetime_end': price_data.get('lifetime_end')}
        req, price = self.aflo_client.create_price(
            catalog_id,
            price_data.get('scope'),
            price_field)
        price_ids.append(price['seq_no'])

        count = count + 1

    return goods_ids, catalog_ids, contents_ids, catalog_scope_ids, price_ids


def delete_contract_info_data(self,
                              contract_id,
                              goods_ids,
                              catalog_ids,
                              contents_ids,
                              catalog_scope_ids,
                              price_ids):
    """Delete contract info data.
    :param contract_id: contract id.
    :param goods_ids: goods ids.
    :param catalog_ids: catalog ids.
    :param contents_ids: catalog contents ids.
    :param catalog_scope_ids: catalog scope ids.
    :param price_ids: price ids.
    """
    # Delete contract data.
    if contract_id:
        self.aflo_client.delete_contract(contract_id)
    # Delete goods data.
    for goods_id in goods_ids:
        print(goods_id)
        self.aflo_client.delete_goods(goods_id)
    # Delete catalog data.
    for catalog_id in catalog_ids:
        self.aflo_client.delete_catalog(catalog_id)
    # Delete catalog contents data.
    count = 0
    for contents_id in contents_ids:
        self.aflo_client.delete_catalog_contents(
            catalog_ids[count],
            contents_id)
        count = count + 1
    # Delete catalog scope data.
    for catalog_scope_id in catalog_scope_ids:
        self.aflo_client.delete_catalog_scope(catalog_scope_id)
    # Delete price data.
    count = 0
    price_data_list = fixture.PRICE_DATA_LIST
    for price_id in price_ids:
        self.aflo_client.delete_price(
            catalog_ids[count],
            price_data_list[count].get('scope'),
            price_id)
        count = count + 1
