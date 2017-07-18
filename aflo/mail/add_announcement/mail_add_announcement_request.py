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

from aflo import i18n

_ = i18n._

""" Subject """
SUBJECT = _("[NEC Cloud System]Request announcements registration(${status})")

""" Body """
BODY = _("""NEC Cloud System

This message is sent automatically.

Approval of the announcement Registration is required, please check.

Inquiry Overview
    Request ID: ${id}
    Request Type: Add Announcement
    Issue Date and Time: ${owner_date_time}
    Issuer: ${owner_name} ${owner_mail}

Inquiry Information
    Project ID: ${project_id}
    Project: ${project_name}
    Type: ${type}
    Title: ${title}
    Language: ${language}
    Maintext: ${field_maintext}
    Workdays: ${field_workdays}
    Target: ${field_target}
    Workcontent: ${field_workcontent}
    Acknowledgment: ${field_acknowledgements}
    Category: ${field_category}
    Scope: ${scope}
    Target Name: ${target_name}
    Announcement Date: ${field_announcementdate}
    Publish on: ${publish_on}
    Unpublish on: ${unpublish_on}

===============
Message:
${message}

===============
NEC Cloud System
URL: http://xxxx.co.jp
===============
""")
