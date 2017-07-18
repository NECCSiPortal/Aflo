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

from aflo.db.sqlalchemy import api as db_api


class ContractManager(object):

    def contract_create(self, ctxt, **values):
        """Create contract.
            :param ctxt: Request context.
            :param values: Contract values.
            :return Contract.
        """
        return db_api.contract_create(ctxt, **values)

    def contract_update(self, ctxt, contract_id, **values):
        """Update contract.
            :param ctxt: Request context.
            :param contract_id: Contract id.
            :param values: Contract values.
            :return Contract.
        """
        return db_api.contract_update(ctxt, contract_id, **values)

    def contract_get(self, ctxt, contract_id):
        return db_api.contract_get(ctxt, contract_id)

    def contract_delete(self, ctxt, contract_id):
        """Delete contract.
            :param ctxt: Http context.
            :param contract_id: Contract id.
        """
        db_api.contract_delete(ctxt, contract_id)

    def contract_list(self, ctxt, project_id=None, region_id=None,
                      project_name=None, catalog_name=None,
                      application_id=None, lifetime=None,
                      date_in_lifetime=None,
                      ticket_template_name=None, application_kinds_name=None,
                      application_name=None, parent_contract_id=None,
                      application_date_from=None, application_date_to=None,
                      lifetime_start_from=None, lifetime_start_to=None,
                      lifetime_end_from=None, lifetime_end_to=None,
                      limit=None, marker=None,
                      sort_key=None, sort_dir=None,
                      force_show_deleted=False):
        """Get all Contract that match zero or more filters.
        :param project_id: project_id of contract.
        :param region_id: project_id of contract.
        :param project_name: project_name of contract.
        :param catalog_name: catalog_name of contract.
        :param application_id: application_id of contract.
        :param lifetime: lifetime of contract.
        :param date_in_lifetime: date_in_lifetime of contract.
        :param ticket_template_name: ticket_template_name of contract.
        :param application_kinds_name: application_kinds_name of contract.
        :param application_name: application_name of contract.
        :param parent_contract_id: contract_id of contract.
        :param application_date_from: application_date for get one day data.
        :param application_date_to: application_date for get one day data.
        :param lifetime_start_from: lifetime_start for get one day data.
        :param lifetime_start_to: lifetime_start for get one day data.
        :param lifetime_end_from: lifetime_end for get one day data.
        :param lifetime_end_to: lifetime_end for get one day data.
        :param limit: maximum number of images to return.
        :param marker: contract_id after which to start page.
        :param sort_key: contract attribute by which results should be sorted.
        :param sort_dir: dict in which results should be sorted (asc, desc).
        :param force_show_deleted: view the deleted deterministic.
        """
        return db_api.contract_list(ctxt, project_id, region_id,
                                    project_name, catalog_name,
                                    application_id, lifetime,
                                    date_in_lifetime,
                                    ticket_template_name,
                                    application_kinds_name,
                                    application_name, parent_contract_id,
                                    application_date_from, application_date_to,
                                    lifetime_start_from, lifetime_start_to,
                                    lifetime_end_from, lifetime_end_to,
                                    limit, marker, sort_key, sort_dir,
                                    force_show_deleted)
