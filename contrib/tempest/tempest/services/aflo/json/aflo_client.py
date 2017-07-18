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

from tempest import config_aflo as config
from tempest.lib.common import rest_client  # noqa

CONF = config.CONF


class AfloClient(rest_client.RestClient):
    """Tempest REST client for AFLO.
    It handles aflo and access to it in OpenStack.
    """

    def __init__(self, auth_provider):
        """Initilize Client.
        :param auth_provider: keystone provider.
        """
        super(AfloClient, self).__init__(
            auth_provider,
            CONF.aflo.catalog_type,
            CONF.aflo.region or CONF.identity.region,
            endpoint_type=CONF.aflo.endpoint_type)

    def get_tickettemplate(self, id):
        """Get a ticket template.
        :param id: Target UUID.
        """
        url = '/v1/tickettemplates/%s' % str(id)

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def list_tickettemplate(self, url_palams=None):
        """Get a list of ticket template.
        :param url_palams: Filtering row data<key=value>.
        """
        url = "/v1/tickettemplates"
        if url_palams:
            url = url + "?" + url_palams

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def create_tickettemplate(self, fields):
        """Create a ticket template.
        :param fields: Add row data<key=value>.
        """
        url = '/v1/tickettemplates'
        requestData = {'tickettemplate': fields}

        resp, body = self.post(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def delete_tickettemplate(self, id):
        """Delete a ticket template.
        :param id: Target UUID.
        """
        url = "/v1/tickettemplates/%s" % id

        resp, body = self.delete(url)
        self.expected_success(200, resp.status)

    def create_workflowpattern(self, fields):
        """Create a workflow pattern.
        :param fields: Add row data<key=value>.
        """
        url = '/v1/workflowpatterns'
        requestData = {'workflowpattern': fields}

        resp, body = self.post(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def delete_workflowpattern(self, id):
        """Delete a workflow pattern.
        :param id: Target UUID.
        """
        url = "/v1/workflowpatterns/%s" % id

        resp, body = self.delete(url)
        self.expected_success(200, resp.status)

    def get_ticket(self, id):
        """Get Ticket.
        :param id: Target UUID.
        """
        url = '/v1/tickets/%s' % str(id)

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def list_ticket(self, url_palams=None):
        """Get a list of ticket.
        :param url_palams: Filterling row data<key=value>.
        """
        url = "/v1/tickets"
        if url_palams:
            url = url + "?" + url_palams

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def create_ticket(self, fields):
        """Create a Tciket
        :param fields: Add row data<key=value>.
        """
        url = '/v1/tickets'
        requestData = {'ticket': fields}

        resp, body = self.post(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def update_ticket(self, id, fields):
        """Update tickete data.
        :param id: Target UUID.
        :param fields: Update row data<key=value>.
        """
        url = "/v1/tickets/%s" % id
        requestData = {'ticket': fields}

        resp, body = self.put(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, body

    def delete_ticket(self, id):
        """Delete a ticket.
        :param id: Target UUID.
        """
        url = "/v1/tickets/%s" % id

        resp, body = self.delete(url)
        self.expected_success(200, resp.status)

    def get_contract(self, contract_id):
        """Get contract.
        :param contract_id: Contract id.
        """
        url = '/v1/contract/%s' % contract_id

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def list_contract(self, url_palams=None):
        """Get a list of contract.
        :param url_palams: Filterling row data<key=value>.
        """
        url = "/v1/contract"
        if url_palams:
            url = url + "?" + url_palams

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def create_contract(self, fields):
        """Create a contract
        :param fields: Add row data<key=value>.
        """
        url = '/v1/contract'
        requestData = {'contract': fields}

        resp, body = self.post(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def update_contract(self, contract_id, fields):
        """Update contract data.
        :param contract_id: Contract id.
        :param fields: Update row data<key=value>.
        """
        url = "/v1/contract/%s" % contract_id
        requestData = {'contract': fields}

        resp, body = self.patch(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def delete_contract(self, contract_id):
        """Delete a contract.
        :param contract_id: Contract id.
        """
        url = "/v1/contract/%s" % contract_id

        resp, body = self.delete(url)
        self.expected_success(200, resp.status)

    def get_catalog(self, catalog_id):
        """Get catalog.
        :param catalog_id: Catalog id.
        """
        url = '/v1/catalog/%s' % catalog_id

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def list_catalog(self, url_palams=None):
        """Get a list of catalog.
        :param url_palams: Filterling row data<key=value>.
        """
        url = "/v1/catalog"
        if url_palams:
            url = url + "?" + url_palams

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def create_catalog(self, fields):
        """Create a catalog
        :param fields: Add row data<key=value>.
        """
        url = '/v1/catalog'
        requestData = {'catalog': fields}

        resp, body = self.post(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def update_catalog(self, catalog_id, fields):
        """Update cataloge data.
        :param catalog_id: Catalog id.
        :param fields: Update row data<key=value>.
        """
        url = "/v1/catalog/%s" % catalog_id
        requestData = {'catalog': fields}

        resp, body = self.patch(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def delete_catalog(self, catalog_id):
        """Delete a catalog.
        :param catalog_id: Catalog id.
        """
        url = "/v1/catalog/%s" % catalog_id

        resp, body = self.delete(url)
        self.expected_success(200, resp.status)

    def get_catalog_contents(self, catalog_id, seq_no):
        """Get catalog_contents.
        :param catalog_id: Catalog id.
        :param seq_no: Seq no.
        """
        url = '/v1/catalog/%s/contents/%s' % (catalog_id, seq_no)

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def list_catalog_contents(self, catalog_id, url_palams=None):
        """Get a list of catalog_contents.
        :param catalog_id: Catalog id.
        :param url_palams: Filterling row data<key=value>.
        """
        url = "/v1/catalog/%s/contents" % catalog_id
        if url_palams:
            url = url + "?" + url_palams

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def create_catalog_contents(self, catalog_id, fields):
        """Create a catalog_contents
        :param catalog_id: Catalog id.
        :param fields: Add row data<key=value>.
        """
        url = '/v1/catalog/%s/contents' % catalog_id
        requestData = {'catalog_contents': fields}

        resp, body = self.post(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def update_catalog_contents(self, catalog_id, seq_no, fields):
        """Update catalog_contentse data.
        :param catalog_id: Catalog id.
        :param seq_no: Seq no.
        :param fields: Update row data<key=value>.
        """
        url = "/v1/catalog/%s/contents/%s" % (catalog_id, seq_no)
        requestData = {'catalog_contents': fields}

        resp, body = self.patch(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def delete_catalog_contents(self, catalog_id, seq_no):
        """Delete a catalog_contents.
        :param catalog_id: Catalog id.
        :param seq_no: Seq no.
        """
        url = "/v1/catalog/%s/contents/%s" % (catalog_id, seq_no)

        resp, body = self.delete(url)
        self.expected_success(200, resp.status)

    def get_goods(self, goods_id):
        """Get goods.
        :param goods_id: Goods id.
        """
        url = '/v1/goods/%s' % goods_id

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def list_goods(self, url_palams=None):
        """Get a list of goods.
        :param url_palams: Filterling row data<key=value>.
        """
        url = "/v1/goods"
        if url_palams:
            url = url + "?" + url_palams

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def create_goods(self, fields):
        """Create a goods
        :param fields: Add row data<key=value>.
        """
        url = '/v1/goods'
        requestData = {'goods': fields}

        resp, body = self.post(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def update_goods(self, goods_id, fields):
        """Update goodse data.
        :param goods_id: Goods id.
        :param fields: Update row data<key=value>.
        """
        url = "/v1/goods/%s" % goods_id
        requestData = {'goods': fields}

        resp, body = self.patch(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def delete_goods(self, goods_id):
        """Delete a goods.
        :param goods_id: Goods id.
        """
        url = "/v1/goods/%s" % goods_id

        resp, body = self.delete(url)
        self.expected_success(200, resp.status)

    def get_catalog_scope(self, catalog_scope_id):
        """Get catalog scope.
        :param catalog_scope_id: Catalog scope id.
        """
        url = '/v1/catalogs/scope/%s/' % (catalog_scope_id)

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def list_catalog_scope(self, url_palams=None):
        """Get a list of catalog scope.
        :param url_palams: Filtering row data<key=value>.
        """
        url = "/v1/catalogs/scope"
        if url_palams:
            url = url + "?" + url_palams

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def create_catalog_scope(self, catalog_id, scope, fields):
        """Create a catalog scope data.
        :param catalog_id: Catalog id.
        :param scope: project id.
        :param fields: Add row data<key=value>.
        """
        url = '/v1/catalogs/%s/scope/%s' % (catalog_id, scope)
        requestData = {'catalog_scope': fields}

        resp, body = self.post(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def update_catalog_scope(self, catalog_scope_id, fields):
        """Update a catalog scope data.
        :param catalog_scope_id: Catalog scope id.
        :param fields: Update row data<key=value>.
        """
        url = "/v1/catalogs/scope/%s" % catalog_scope_id
        requestData = {'catalog_scope': fields}

        resp, body = self.patch(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def delete_catalog_scope(self, catalog_scope_id):
        """Delete a catalog scope data.
        :param catalog_scope_id: Catalog scope id.
        """
        url = "/v1/catalogs/scope/%s" % (catalog_scope_id)

        resp, body = self.delete(url)
        self.expected_success(200, resp.status)

    def list_valid_catalog(self, url_palams=None):
        """Get a list of valid catalog.
        :param url_palams: Filtering row data<key=value>.
        """
        url = "/v1/catalogs"
        if url_palams:
            url = url + "?" + url_palams

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def get_price(self, catalog_id, scope, seq_no):
        """Get price.
        :param catalog_id: Catalog id.
        :param scope: Scope.
        :param seq_no: Seq no.
        """
        url = '/v1/catalog/%s/price/%s/seq/%s' % (catalog_id, scope, seq_no)

        resp, body = self.get(url)
        self.expected_success(200, resp.status)
        return resp, self._parse_resp(body)

    def list_price(self, catalog_id, url_palams=None):
        """Get a list of price.
        :param catalog_id: Catalog id.
        :param url_palams: Filterling row data<key=value>.
        """
        url = "/v1/catalog/%s/price" % catalog_id
        if url_palams:
            url = url + "?" + url_palams

        resp, body = self.get(url)
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def create_price(self, catalog_id, scope, fields):
        """Create a price
        :param catalog_id: Catalog id.
        :param scope: Scope.
        :param fields: Add row data<key=value>.
        """
        url = '/v1/catalog/%s/price/%s' % (catalog_id, scope)
        requestData = {'catalog_price': fields}

        resp, body = self.post(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def update_price(self, catalog_id, scope, seq_no, fields):
        """Update pricee data.
        :param catalog_id: Catalog id.
        :param scope: Scope.
        :param seq_no: Seq no.
        :param fields: Update row data<key=value>.
        """
        url = '/v1/catalog/%s/price/%s/seq/%s' % (catalog_id, scope, seq_no)
        requestData = {'catalog_price': fields}

        resp, body = self.patch(url, json.dumps(requestData))
        self.expected_success(200, resp.status)

        return resp, self._parse_resp(body)

    def delete_price(self, catalog_id, scope, seq_no):
        """Delete a price.
        :param catalog_id: Catalog id.
        :param scope: Scope.
        :param seq_no: Seq no.
        """
        url = '/v1/catalog/%s/price/%s/seq/%s' % (catalog_id, scope, seq_no)

        resp, body = self.delete(url)
        self.expected_success(200, resp.status)
