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

from aflo.db.sqlalchemy import api as db_api


class ValidCatalogManager(object):

    def valid_catalog_list(self, ctxt, marker=None, limit=None,
                           sort_key=None, sort_dir=None,
                           refine_flg=None, filters=None):
        return db_api.valid_catalog_list(ctxt, marker, limit,
                                         sort_key, sort_dir,
                                         refine_flg, filters)
