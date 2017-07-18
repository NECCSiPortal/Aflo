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

from aflo.api.v1 import catalog
from aflo.api.v1 import catalog_contents
from aflo.api.v1 import catalog_scope
from aflo.api.v1 import contracts
from aflo.api.v1 import goods
from aflo.api.v1 import price
from aflo.api.v1 import tickets
from aflo.api.v1 import tickettemplates
from aflo.api.v1 import valid_catalog
from aflo.api.v1 import workflowpatterns
from aflo.common import wsgi


class API(wsgi.Router):

    """WSGI router for Aflo v1 API requests."""

    def __init__(self, mapper):
        tickettemplates_resource = tickettemplates.create_resource()
        workflowpatterns_resource = workflowpatterns.create_resource()
        tickets_resource = tickets.create_resource()
        contracts_resource = contracts.create_resource()
        goods_resource = goods.create_resource()
        catalog_resource = catalog.create_resource()
        catalog_contents_resource = catalog_contents.create_resource()
        catalog_scope_resource = catalog_scope.create_resource()
        price_resource = price.create_resource()
        valid_catalog_resource = valid_catalog.create_resource()

        mapper.connect("/",
                       controller=tickettemplates_resource,
                       action="index")
        mapper.connect("/tickettemplates",
                       controller=tickettemplates_resource,
                       action='index',
                       conditions={'method': ['GET']})
        mapper.connect("/tickettemplates/{tickettemplate_id}",
                       controller=tickettemplates_resource,
                       action='show',
                       conditions={'method': ['GET']})
        mapper.connect("/tickettemplates",
                       controller=tickettemplates_resource,
                       action='create',
                       conditions={'method': ['POST']})
        mapper.connect("/tickettemplates/{tickettemplate_id}",
                       controller=tickettemplates_resource,
                       action='delete',
                       conditions={'method': ['DELETE']})

        mapper.connect("/workflowpatterns",
                       controller=workflowpatterns_resource,
                       action='create',
                       conditions={'method': ['POST']})
        mapper.connect("/workflowpatterns/{workflowpattern_id}",
                       controller=workflowpatterns_resource,
                       action='delete',
                       conditions={'method': ['DELETE']})

        mapper.connect("/tickets",
                       controller=tickets_resource,
                       action='index',
                       conditions={'method': ['GET']})
        mapper.connect("/tickets/{ticket_id}",
                       controller=tickets_resource,
                       action='show',
                       conditions={'method': ['GET']})
        mapper.connect("/tickets",
                       controller=tickets_resource,
                       action='create',
                       conditions={'method': ['POST']})
        mapper.connect("/tickets/{ticket_id}",
                       controller=tickets_resource,
                       action='update',
                       conditions={'method': ['PUT']})
        mapper.connect("/tickets/{ticket_id}",
                       controller=tickets_resource,
                       action='delete',
                       conditions={'method': ['DELETE']})

        mapper.connect("/contract",
                       controller=contracts_resource,
                       action='create',
                       conditions={'method': ['POST']})
        mapper.connect("/contract/{contract_id}",
                       controller=contracts_resource,
                       action='show',
                       conditions={'method': ['GET']})
        mapper.connect("/contract/{contract_id}",
                       controller=contracts_resource,
                       action='delete',
                       conditions={'method': ['DELETE']})
        mapper.connect("/contract",
                       controller=contracts_resource,
                       action='list',
                       conditions={'method': ['GET']})
        mapper.connect("/contract/{contract_id}",
                       controller=contracts_resource,
                       action='update',
                       conditions={'method': ['PATCH']})

        mapper.connect("/goods",
                       controller=goods_resource,
                       action='create',
                       conditions={'method': ['POST']})
        mapper.connect("/goods/{goods_id}",
                       controller=goods_resource,
                       action='update',
                       conditions={'method': ['PATCH']})
        mapper.connect("/goods",
                       controller=goods_resource,
                       action='list',
                       conditions={'method': ['GET']})
        mapper.connect("/goods/{goods_id}",
                       controller=goods_resource,
                       action='show',
                       conditions={'method': ['GET']})
        mapper.connect("/goods/{goods_id}",
                       controller=goods_resource,
                       action='delete',
                       conditions={'method': ['DELETE']})

        mapper.connect("/catalog",
                       controller=catalog_resource,
                       action='create',
                       conditions={'method': ['POST']})
        mapper.connect("/catalog/{catalog_id}",
                       controller=catalog_resource,
                       action='update',
                       conditions={'method': ['PATCH']})
        mapper.connect("/catalog/{catalog_id}",
                       controller=catalog_resource,
                       action='show',
                       conditions={'method': ['GET']})
        mapper.connect("/catalog",
                       controller=catalog_resource,
                       action='index',
                       conditions={'method': ['GET']})
        mapper.connect("/catalog/{catalog_id}",
                       controller=catalog_resource,
                       action='delete',
                       conditions={'method': ['DELETE']})

        mapper.connect("/catalog/{catalog_id}/contents",
                       controller=catalog_contents_resource,
                       action='create',
                       conditions={'method': ['POST']})
        mapper.connect("/catalog/{catalog_id}/contents",
                       controller=catalog_contents_resource,
                       action='list',
                       conditions={'method': ['GET']})
        mapper.connect("/catalog/{catalog_id}/contents/{seq_no}",
                       controller=catalog_contents_resource,
                       action='show',
                       conditions={'method': ['GET']})
        mapper.connect("/catalog/{catalog_id}/contents/{seq_no}",
                       controller=catalog_contents_resource,
                       action='update',
                       conditions={'method': ['PATCH']})
        mapper.connect("/catalog/{catalog_id}/contents/{seq_no}",
                       controller=catalog_contents_resource,
                       action='delete',
                       conditions={'method': ['DELETE']})

        mapper.connect("/catalogs/{catalog_id}/scope/{scope}",
                       controller=catalog_scope_resource,
                       action='create',
                       conditions={'method': ['POST']})
        mapper.connect("/catalogs/scope",
                       controller=catalog_scope_resource,
                       action='index',
                       conditions={'method': ['GET']})
        mapper.connect("/catalogs/scope/{catalog_scope_id}",
                       controller=catalog_scope_resource,
                       action='show',
                       conditions={'method': ['GET']})
        mapper.connect("/catalogs/scope/{catalog_scope_id}",
                       controller=catalog_scope_resource,
                       action='update',
                       conditions={'method': ['PATCH']})
        mapper.connect("/catalogs/scope/{catalog_scope_id}",
                       controller=catalog_scope_resource,
                       action='delete',
                       conditions={'method': ['DELETE']})

        mapper.connect("/catalogs",
                       controller=valid_catalog_resource,
                       action='index',
                       conditions={'method': ['GET']})

        mapper.connect("/catalog/{catalog_id}/price/{scope}",
                       controller=price_resource,
                       action='create',
                       conditions={'method': ['POST']})
        mapper.connect("/catalog/{catalog_id}/price/{scope}/seq/{seq_no}",
                       controller=price_resource,
                       action='show',
                       conditions={'method': ['GET']})
        mapper.connect("/catalog/{catalog_id}/price",
                       controller=price_resource,
                       action='index',
                       conditions={'method': ['GET']})
        mapper.connect("/catalog/{catalog_id}/price/{scope}/seq/{seq_no}",
                       controller=price_resource,
                       action='update',
                       conditions={'method': ['PATCH']})
        mapper.connect("/catalog/{catalog_id}/price/{scope}/seq/{seq_no}",
                       controller=price_resource,
                       action='delete',
                       conditions={'method': ['DELETE']})

        super(API, self).__init__(mapper)
