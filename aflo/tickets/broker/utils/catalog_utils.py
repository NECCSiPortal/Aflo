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
#

from aflo.common.exception import NotFound
from aflo.db.sqlalchemy import api as db_api
from aflo.tickets.broker.utils import utils as broker_utils


def is_valid_catalog(ctxt, project_id, catalog_ids):
    """Check valid catalogs lifetime
    :param ctxt request context
    :param project_id project id
    :param catalog_ids catalog id list
    """
    for catalog_id in catalog_ids:
        filters = {'catalog_id': catalog_id,
                   'scope': project_id,
                   'lifetime': broker_utils.get_now_string()}
        try:
            # get valid catalog list
            catalog = db_api.valid_catalog_list(
                ctxt, refine_flg=False, filters=filters)

            if not catalog:
                raise NotFound()
        except Exception:
            raise NotFound()
