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

from datetime import datetime
from oslo_config import cfg
from oslo_serialization import jsonutils
import routes

from aflo.api.v1 import router
from aflo.common import wsgi
import aflo.context
from aflo import db
from aflo.db.sqlalchemy import models as db_models
from aflo.tests.unit import base
import aflo.tests.unit.utils as unit_test_utils
from aflo.tests import utils as test_utils

CONF = cfg.CONF
db_api = db.get_api()

CONTRACT_ID_101 = 'ea0a4146-fd07-414b-aa5e-dedbeef00101'
CONTRACT_ID_102 = 'ea0a4146-fd07-414b-aa5e-dedbeef00102'
CONTRACT_ID_103 = 'ea0a4146-fd07-414b-aa5e-dedbeef00103'
CONTRACT_ID_104 = 'ea0a4146-fd07-414b-aa5e-dedbeef00104'

bo01 = \
    {'contract':
        {'region_id': 'region_id_101_u',
         'project_id': 'project_id_101_u',
         'project_name': 'project_name_101_u',
         'catalog_id': 'catalog_id_101_u',
         'catalog_name': 'catalog_name_101_u',
         'num': 109,
         'parent_ticket_template_id': 'parent_ticket_template_id_101_u',
         'ticket_template_id': 'ticket_template_id_101_u',
         'parent_ticket_template_name': 'parent_ticket_template_name_101_u',
         'parent_application_kinds_name': 'par_application_kinds_name_101_u',
         'application_kinds_name': 'application_kinds_name_101_u',
         'cancel_application_id': 'cancel_application_id_101_u',
         'application_id': 'application_id_101_u',
         'ticket_template_name': 'ticket_template_name_101_u',
         'application_name': 'application_name_101_u',
         'application_date': datetime(2015, 6, 9, 0, 0, 0, 0),
         'parent_contract_id': 'parent_contract_id_101_u',
         'lifetime_start': datetime(2015, 7, 9, 0, 0, 0, 0),
         'lifetime_end': datetime(2015, 8, 9, 0, 0, 0, 0),
         'deleted': True,
         'expansions':
         {'expansion_key1': 'expansion_key1_u',
          'expansion_key2': 'expansion_key2_u',
          'expansion_key3': 'expansion_key3_u',
          'expansion_key4': 'expansion_key4_u',
          'expansion_key5': 'expansion_key5_u'},
         'expansions_text':
         {'expansion_text': 'expansion_text_u'}
         }
     }

bo02 = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

bo04 = {'contract': {}}

body_region_id_error = \
    {'contract':
        {'region_id': 'a' * 256,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_project_id_error = \
    {'contract':
        {'region_id': None,
         'project_id': 'a' * 65,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_project_name_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': 'a' * 65,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_catalog_id_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': 'a' * 65,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_catalog_name_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': 'a' * 129,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_num_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': 'a',
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_parent_ticket_template_id_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': 'a' * 65,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'deleted': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_ticket_template_id_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': 'a' * 65,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'deleted': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_parent_ticket_template_name_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': 'a' * 65536,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'deleted': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_parent_application_kinds_name_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': 'a' * 65536,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'deleted': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_application_kinds_name_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': 'a' * 65536,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'deleted': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_cancel_application_id_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': 'a' * 65,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'deleted': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_application_id_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': 'a' * 65,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_ticket_template_name_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': 'a' * 65536,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'deleted': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_application_name_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': 'a' * 65,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'deleted': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_application_date_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': 'a',
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'deleted': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_parent_contract_id_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': 'a' * 65,
         'lifetime_start': None,
         'lifetime_end': None,
         'deleted': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_lifetime_start_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': 'a',
         'lifetime_end': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_lifetime_end_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': 'a',
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_expansion_key1_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'expansions':
         {'expansion_key1': 'a' * 256,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_expansion_key2_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': 'a' * 256,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_expansion_key3_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': 'a' * 256,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_expansion_key4_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': 'a' * 256,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_expansion_key5_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': 'a' * 256},
         'expansions_text':
         {'expansion_text': None}
         }
     }

body_expansion_text_error = \
    {'contract':
        {'region_id': None,
         'project_id': None,
         'project_name': None,
         'catalog_id': None,
         'catalog_name': None,
         'num': None,
         'parent_ticket_template_id': None,
         'ticket_template_id': None,
         'parent_ticket_template_name': None,
         'parent_application_kinds_name': None,
         'application_kinds_name': None,
         'cancel_application_id': None,
         'application_id': None,
         'ticket_template_name': None,
         'application_name': None,
         'application_date': None,
         'parent_contract_id': None,
         'lifetime_start': None,
         'lifetime_end': None,
         'expansions':
         {'expansion_key1': None,
          'expansion_key2': None,
          'expansion_key3': None,
          'expansion_key4': None,
          'expansion_key5': None},
         'expansions_text':
         {'expansion_text': 'a' * 65536}
         }
     }


def get_datetime(str_date):
    """Get datetime.
        :param str_date: String of date.
    """
    return datetime.strptime(str_date + 'T00:00:00.000000',
                             '%Y-%m-%dT%H:%M:%S.%f')


class TestContractUpdateAPI(base.WorkflowUnitTest):
    def setUp(self):
        """Establish a clean test environment"""
        super(TestContractUpdateAPI, self).setUp()
        self.mapper = routes.Mapper()
        self.api = test_utils.FakeAuthMiddleware(router.API(self.mapper))

        self.context = aflo.context.RequestContext(is_admin=True)
        db_api.get_engine()
        self.destroy_fixtures()
        self.create_fixtures()
        self.serializer = wsgi.JSONResponseSerializer()

    def tearDown(self):
        """Clear the test environment"""
        super(TestContractUpdateAPI, self).tearDown()
        self.destroy_fixtures()

    def create_fixtures(self):
        super(TestContractUpdateAPI, self).create_fixtures()
        db_cre = db_models.Contract
        db_cre(contract_id=CONTRACT_ID_101,
               region_id='region_id_101',
               project_id='project_id_101',
               project_name='project_name_101',
               catalog_id='catalog_id_101',
               catalog_name='catalog_name_101',
               num=101,
               parent_ticket_template_id='parent_ticket_template_id_101',
               ticket_template_id='ticket_template_id_101',
               parent_ticket_template_name='parent_ticket_template_name_101',
               parent_application_kinds_name='par_application_kinds_name_101',
               application_kinds_name='application_kinds_name_101',
               cancel_application_id='cancel_application_id_101',
               application_id='application_id_101',
               ticket_template_name='ticket_template_name_101',
               application_name='application_name_101',
               application_date=get_datetime('2015-05-01'),
               parent_contract_id='parent_contract_id_101',
               lifetime_start=get_datetime('2015-07-01'),
               lifetime_end=get_datetime('2015-08-01'),
               created_at=datetime.utcnow(),
               expansion_key1='expansion_key1',
               expansion_key2='expansion_key2',
               expansion_key3='expansion_key3',
               expansion_key4='expansion_key4',
               expansion_key5='expansion_key5',
               expansion_text='expansion_text'
               ).save(db_api.get_session())

        db_cre(contract_id=CONTRACT_ID_102,
               region_id='region_id_101',
               project_id='project_id_101',
               project_name='project_name_101',
               catalog_id='catalog_id_102',
               catalog_name='catalog_name_102',
               num=102,
               parent_ticket_template_id='parent_ticket_template_id_102',
               ticket_template_id='ticket_template_id_102',
               parent_ticket_template_name='parent_ticket_template_name_102',
               parent_application_kinds_name='par_application_kinds_name_102',
               application_kinds_name='application_kinds_name_102',
               cancel_application_id='cancel_application_id_102',
               application_id='application_id_102',
               ticket_template_name='ticket_template_name_102',
               application_name='application_name_102',
               application_date=get_datetime('2015-05-02'),
               parent_contract_id='parent_contract_id_102',
               lifetime_start=get_datetime('2015-07-02'),
               lifetime_end=get_datetime('2015-08-02'),
               created_at=datetime.utcnow(),
               expansion_key1='expansion_key1',
               expansion_key2='expansion_key2',
               expansion_key3='expansion_key3',
               expansion_key4='expansion_key4',
               expansion_key5='expansion_key5',
               expansion_text='expansion_text'
               ).save(db_api.get_session())

        db_cre(contract_id=CONTRACT_ID_103,
               region_id='region_id_101',
               project_id='project_id_101',
               project_name='project_name_101',
               catalog_id='catalog_id_103',
               catalog_name='catalog_name_103',
               num=103,
               parent_ticket_template_id='parent_ticket_template_id_103',
               ticket_template_id='ticket_template_id_103',
               parent_ticket_template_name='parent_ticket_template_name_103',
               parent_application_kinds_name='par_application_kinds_name_103',
               application_kinds_name='application_kinds_name_103',
               cancel_application_id='cancel_application_id_103',
               application_id='application_id_103',
               ticket_template_name='ticket_template_name_103',
               application_name='application_name_103',
               application_date=get_datetime('2015-05-03'),
               parent_contract_id='parent_contract_id_103',
               lifetime_start=get_datetime('2015-07-03'),
               lifetime_end=get_datetime('2015-08-03'),
               created_at=datetime.utcnow(),
               deleted=False,
               expansion_key1='expansion_key1',
               expansion_key2='expansion_key2',
               expansion_key3='expansion_key3',
               expansion_key4='expansion_key4',
               expansion_key5='expansion_key5',
               expansion_text='expansion_text'
               ).save(db_api.get_session())

        db_cre(contract_id=CONTRACT_ID_104,
               region_id='region_id_104',
               project_id='project_id_104',
               project_name='project_name_104',
               catalog_id='catalog_id_104',
               catalog_name='catalog_name_104',
               num=104,
               parent_ticket_template_id='parent_ticket_template_id_104',
               ticket_template_id='ticket_template_id_104',
               parent_ticket_template_name='parent_ticket_template_name_104',
               parent_application_kinds_name='par_application_kinds_name_104',
               application_kinds_name='application_kinds_name_104',
               cancel_application_id='cancel_application_id_104',
               application_id='application_id_104',
               ticket_template_name='ticket_template_name_104',
               application_name='application_name_104',
               application_date=get_datetime('2015-06-04'),
               parent_contract_id='parent_contract_id_104',
               lifetime_start=get_datetime('2015-07-04'),
               lifetime_end=get_datetime('2015-08-04'),
               created_at=datetime.utcnow(),
               deleted=False,
               expansion_key1='expansion_key1',
               expansion_key2='expansion_key2',
               expansion_key3='expansion_key3',
               expansion_key4='expansion_key4',
               expansion_key5='expansion_key5',
               expansion_text='expansion_text'
               ).save(db_api.get_session())

    def destroy_fixtures(self):
        # Easiest to just drop the models and re-create them...
        db_models.unregister_models(db_api.get_engine())
        db_models.register_models(db_api.get_engine())

    def test_contract_update_with_no_auth(self):
        path = '/contract/%s' % CONTRACT_ID_101
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:no_auth'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo01)

        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 403)

    def test_contract_update(self):
        path = '/contract/%s' % CONTRACT_ID_101
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo01)

        res = req.get_response(self.api)
        contract = jsonutils.loads(res.body)['contract']

        self.assertEqual(res.status_int, 200)
        self.assertIsNotNone(contract['contract_id'])
        self.assertEqual(contract['region_id'], 'region_id_101_u')
        self.assertEqual(contract['project_id'], 'project_id_101_u')
        self.assertEqual(contract['project_name'], 'project_name_101_u')
        self.assertEqual(contract['catalog_id'], 'catalog_id_101_u')
        self.assertEqual(contract['catalog_name'], 'catalog_name_101_u')
        self.assertEqual(contract['num'], 109)
        self.assertEqual(contract['parent_ticket_template_id'],
                         'parent_ticket_template_id_101_u')
        self.assertEqual(contract['ticket_template_id'],
                         'ticket_template_id_101_u')
        self.assertEqual(contract['parent_ticket_template_name'],
                         'parent_ticket_template_name_101_u')
        self.assertEqual(contract['parent_application_kinds_name'],
                         'par_application_kinds_name_101_u')
        self.assertEqual(contract['application_kinds_name'],
                         'application_kinds_name_101_u')
        self.assertEqual(contract['cancel_application_id'],
                         'cancel_application_id_101_u')
        self.assertEqual(contract['application_id'], 'application_id_101_u')
        self.assertEqual(contract['ticket_template_name'],
                         'ticket_template_name_101_u')
        self.assertEqual(contract['application_name'],
                         'application_name_101_u')
        application_date = datetime.strptime(contract['application_date'],
                                             '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(application_date, datetime(2015, 6, 9, 0, 0, 0, 0))
        self.assertEqual(contract['parent_contract_id'],
                         'parent_contract_id_101_u')
        lifetime_start = datetime.strptime(contract['lifetime_start'],
                                           '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(lifetime_start, datetime(2015, 7, 9, 0, 0, 0, 0))
        lifetime_end = datetime.strptime(contract['lifetime_end'],
                                         '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(lifetime_end, datetime(2015, 8, 9, 0, 0, 0, 0))
        self.assertEqual(contract['expansions']['expansion_key1'],
                         'expansion_key1_u')
        self.assertEqual(contract['expansions']['expansion_key2'],
                         'expansion_key2_u')
        self.assertEqual(contract['expansions']['expansion_key3'],
                         'expansion_key3_u')
        self.assertEqual(contract['expansions']['expansion_key4'],
                         'expansion_key4_u')
        self.assertEqual(contract['expansions']['expansion_key5'],
                         'expansion_key5_u')
        self.assertEqual(contract['expansions_text']['expansion_text'],
                         'expansion_text_u')
        self.assertIsNotNone(contract['created_at'])
        self.assertIsNotNone(contract['updated_at'])
        self.assertIsNone(contract['deleted_at'])
        self.assertEqual(contract['deleted'], False)

    def test_contract_update_no_keyword(self):
        path = '/contract/%s' % CONTRACT_ID_104
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo04)

        res = req.get_response(self.api)
        contract = jsonutils.loads(res.body)['contract']

        self.assertEqual(res.status_int, 200)
        self.assertIsNotNone(contract['contract_id'])
        self.assertEqual(contract['region_id'], 'region_id_104')
        self.assertEqual(contract['project_id'], 'project_id_104')
        self.assertEqual(contract['project_name'], 'project_name_104')
        self.assertEqual(contract['catalog_id'], 'catalog_id_104')
        self.assertEqual(contract['catalog_name'], 'catalog_name_104')
        self.assertEqual(contract['num'], 104)
        self.assertEqual(contract['parent_ticket_template_id'],
                         'parent_ticket_template_id_104')
        self.assertEqual(contract['ticket_template_id'],
                         'ticket_template_id_104')
        self.assertEqual(contract['parent_ticket_template_name'],
                         'parent_ticket_template_name_104')
        self.assertEqual(contract['parent_application_kinds_name'],
                         'par_application_kinds_name_104')
        self.assertEqual(contract['application_kinds_name'],
                         'application_kinds_name_104')
        self.assertEqual(contract['cancel_application_id'],
                         'cancel_application_id_104')
        self.assertEqual(contract['application_id'], 'application_id_104')
        self.assertEqual(contract['ticket_template_name'],
                         'ticket_template_name_104')
        self.assertEqual(contract['application_name'],
                         'application_name_104')
        application_date = datetime.strptime(contract['application_date'],
                                             '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(application_date, datetime(2015, 6, 4, 0, 0, 0, 0))
        self.assertEqual(contract['parent_contract_id'],
                         'parent_contract_id_104')
        lifetime_start = datetime.strptime(contract['lifetime_start'],
                                           '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(lifetime_start, datetime(2015, 7, 4, 0, 0, 0, 0))
        lifetime_end = datetime.strptime(contract['lifetime_end'],
                                         '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(lifetime_end, datetime(2015, 8, 4, 0, 0, 0, 0))
        self.assertEqual(contract['expansions']['expansion_key1'],
                         'expansion_key1')
        self.assertEqual(contract['expansions']['expansion_key2'],
                         'expansion_key2')
        self.assertEqual(contract['expansions']['expansion_key3'],
                         'expansion_key3')
        self.assertEqual(contract['expansions']['expansion_key4'],
                         'expansion_key4')
        self.assertEqual(contract['expansions']['expansion_key5'],
                         'expansion_key5')
        self.assertEqual(contract['expansions_text']['expansion_text'],
                         'expansion_text')
        self.assertIsNotNone(contract['created_at'])
        self.assertIsNotNone(contract['updated_at'])
        self.assertIsNone(contract['deleted_at'])
        self.assertEqual(contract['deleted'], False)

    def test_contract_update_with_none_value(self):
        path = '/contract/%s' % CONTRACT_ID_102
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo02)

        res = req.get_response(self.api)
        contract = jsonutils.loads(res.body)['contract']

        self.assertEqual(res.status_int, 200)
        self.assertIsNotNone(contract['contract_id'])
        self.assertIsNone(contract['region_id'])
        self.assertIsNone(contract['project_id'])
        self.assertIsNone(contract['project_name'])
        self.assertIsNone(contract['catalog_id'])
        self.assertIsNone(contract['catalog_name'])
        self.assertIsNone(contract['num'])
        self.assertIsNone(contract['parent_ticket_template_id'])
        self.assertIsNone(contract['ticket_template_id'])
        self.assertIsNone(contract['parent_ticket_template_name'])
        self.assertIsNone(contract['parent_application_kinds_name'])
        self.assertIsNone(contract['application_kinds_name'])
        self.assertIsNone(contract['cancel_application_id'])
        self.assertIsNone(contract['application_id'])
        self.assertIsNone(contract['lifetime_start'])
        self.assertIsNone(contract['lifetime_end'])
        self.assertIsNotNone(contract['expansions'])
        self.assertIsNone(contract['expansions']['expansion_key1'])
        self.assertIsNone(contract['expansions']['expansion_key2'])
        self.assertIsNone(contract['expansions']['expansion_key3'])
        self.assertIsNone(contract['expansions']['expansion_key4'])
        self.assertIsNone(contract['expansions']['expansion_key5'])
        self.assertIsNotNone(contract['expansions_text'])
        self.assertIsNone(contract['expansions_text']['expansion_text'])
        self.assertIsNotNone(contract['created_at'])
        self.assertIsNotNone(contract['updated_at'])
        self.assertIsNone(contract['deleted_at'])
        self.assertEqual(contract['deleted'], False)

    def test_contract_update_region_id_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_region_id_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_project_id_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_project_id_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_project_name_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_project_name_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_catalog_id_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_catalog_id_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_catalog_name_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_catalog_name_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_num_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_num_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_parent_ticket_template_id_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_parent_ticket_template_id_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_ticket_template_id_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_ticket_template_id_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_parent_ticket_template_name_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_parent_ticket_template_name_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_parent_application_kinds_name_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_parent_application_kinds_name_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_application_kinds_name_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_application_kinds_name_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_cancel_application_id_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_cancel_application_id_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_application_id_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_application_id_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_ticket_template_name_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_ticket_template_name_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_application_name_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_application_name_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_application_date_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_application_date_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_parent_contract_id_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_parent_contract_id_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_lifetime_start_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_lifetime_start_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_lifetime_end_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_lifetime_end_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_expansion_key1_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key1_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_expansion_key2_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key2_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_expansion_key3_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key3_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_expansion_key4_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key4_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_expansion_key5_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_key5_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_expansion_text_error(self):
        path = '/contract/%s' % CONTRACT_ID_103
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(body_expansion_text_error)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 400)

    def test_contract_update_no_contract_id(self):
        path = '/contract/%s' % ''
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo01)

        res = req.get_response(self.api)
        self.assertEqual(res.status_int, 404)

    def test_contract_update_contract_id_length(self):
        path = '/contract/%s' % ('a' * 65)
        req = unit_test_utils.get_fake_request(method='PATCH', path=path)
        headers = {'x-auth-token': 'user:tenant:admin'}

        for k, v in headers.iteritems():
            req.headers[k] = v

        req.body = jsonutils.dumps(bo01)

        res = req.get_response(self.api)

        self.assertEqual(res.status_int, 400)
