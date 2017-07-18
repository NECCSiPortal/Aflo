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


def create_contract_for_update(db_models, contract_id, region_id,
                               project_id, date, seq, deleted):
    db_models.Contract(contract_id=contract_id, region_id=region_id,
                       project_id=project_id, project_name=seq,
                       catalog_id=seq, catalog_name=seq, num=seq,
                       parent_ticket_template_id=seq, ticket_template_id=seq,
                       parent_ticket_template_name=seq,
                       parent_application_kinds_name=seq,
                       application_kinds_name=seq, cancel_application_id=seq,
                       application_id=seq, ticket_template_name=seq,
                       application_name=seq, application_date=date,
                       parent_contract_id=seq, lifetime_start=date,
                       lifetime_end=date, expansion_key1=seq,
                       expansion_key2=seq, expansion_key3=seq,
                       expansion_key4=seq, expansion_key5=seq,
                       expansion_text=seq, created_at=date,
                       updated_at=date, deleted=0).save()
