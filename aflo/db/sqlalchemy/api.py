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

"""Defines interface for DB access."""
from datetime import datetime
import json
import sys
import threading
import uuid

from oslo_config import cfg
from oslo_db import exception as db_exception
from oslo_db.sqlalchemy import session
from oslo_log import log as logging
import osprofiler.sqlalchemy
import sqlalchemy
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import false

from aflo.common import exception
from aflo.common import utils as common_utils
from aflo.db.sqlalchemy import models
from aflo.db.sqlalchemy import utils as db_api_utils
from aflo import i18n
from aflo.tickettemplates import templates

BASE = models.BASE
sa_logger = None
LOG = logging.getLogger(__name__)
_ = i18n._
_LI = i18n._LI
_LW = i18n._LW


CONF = cfg.CONF
CONF.import_group("profiler", "aflo.common.wsgi")

_FACADE = None
_LOCK = threading.Lock()

_WF_START_STARTUS_CODE = 'none'
_WF_STATUS_NON_ACTIVE = 0
_WF_STATUS_ACTIVE = 1
_WF_STATUS_END = 2

_VALID_CATALOG_SORTKEY = {
    'catalog_id': ['catalog', 'catalog_id'],
    'scope': ['catalog_scope', 'scope'],
    'catalog_name': ['catalog', 'catalog_name'],
    'price': ['price', 'price'],
    'catalog_lifetime_start': ['catalog', 'lifetime_start'],
    'catalog_lifetime_end': ['catalog', 'lifetime_end'],
    'catalog_scope_lifetime_start': ['catalog_scope', 'lifetime_start'],
    'catalog_scope_lifetime_end': ['catalog_scope', 'lifetime_end'],
    'price_lifetime_start': ['price', 'lifetime_start'],
    'price_lifetime_end': ['price', 'lifetime_end'],
    'catalog_scope_id': ['catalog_scope', 'id'],
    'price_seq_no': ['price', 'seq_no'],
    'catalog_created_at': ['catalog', 'created_at']}


def _retry_on_deadlock(exc):
    """Decorator to retry a DB API call if Deadlock was received."""

    if isinstance(exc, db_exception.DBDeadlock):
        LOG.warn(_LW("Deadlock detected. Retrying..."))
        return True
    return False


def _create_facade_lazily():
    global _LOCK, _FACADE
    if _FACADE is None:
        with _LOCK:
            if _FACADE is None:
                _FACADE = session.EngineFacade.from_config(CONF)

                if CONF.profiler.enabled and CONF.profiler.trace_sqlalchemy:
                    osprofiler.sqlalchemy.add_tracing(sqlalchemy,
                                                      _FACADE.get_engine(),
                                                      "db")
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(autocommit=True, expire_on_commit=False):
    facade = _create_facade_lazily()
    return facade.get_session(autocommit=autocommit,
                              expire_on_commit=expire_on_commit)


def clear_db_env():
    """
    Unset global configuration variables for database.
    """
    global _FACADE
    _FACADE = None


def _ticket_templates_get(context, ticket_template_id,
                          session=None, force_show_deleted=False):
    session = session or get_session()

    try:
        query = session.query(models.TicketTemplate)\
                       .filter_by(id=ticket_template_id)

        # filter out deleted if context disallows it
        if not force_show_deleted\
                or not context.can_see_deleted:
            query = query.filter_by(deleted=False)

        rtn_obj = query.one()
    except sa_orm.exc.NoResultFound:
        msg = (_("No TicketTemplate found with ID %s") % ticket_template_id)
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return rtn_obj


def _workflow_pattern_get(context,
                          workflow_pattern_id,
                          workflow_pattern_code,
                          session=None, force_show_deleted=False):
    """Get Workflow Pattern data.
    :param context: context of run process information.
    :param workflow_pattern_id: ID of Workflow Pattern.
    :param workflow_pattern_code: Code of Workflow Pattern.
    :param session: If you use this function in transaction,
        set session object.
    :param force_show_deleted: view the deleted deterministic
    """
    LOG.debug('----- _workflow_pattern_get -----')
    session = session or get_session()

    try:
        query = None
        if workflow_pattern_id:
            query = session.query(models.WorkflowPattern)\
                           .filter_by(id=workflow_pattern_id)

        if workflow_pattern_code:
            query = session.query(models.WorkflowPattern)\
                           .filter_by(code=workflow_pattern_code)

        # filter out deleted if context disallows it
        if not force_show_deleted\
                or not context.can_see_deleted:
            query = query.filter_by(deleted=False)

        result = query.one()
    except sa_orm.exc.NoResultFound:
        msg = (_("No Workflow Pattern found with ID %s") % workflow_pattern_id)
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return result


def ticket_templates_create(context, **values):
    """Create a ticket template from the values dictionary.
    :param values: Entry ticket template data.
    """
    se = get_session()

    with (se).begin():
        data = models.TicketTemplate()

        data.id = values.get('id')
        data.template_contents = values.get('template_contents')
        data.ticket_type = values.get('ticket_type')
        data.workflow_pattern_id = values.get('workflow_pattern_id')

        data.save(session=se)

    return data


def ticket_templates_list(context, marker=None, limit=None,
                          sort_key=None, sort_dir=None,
                          force_show_deleted=False,
                          ticket_type=None,
                          filters=None):
    """
    Get all objects that match zero or more filters.

    :param marker: id after which to start page
    :param limit: maximum number of images to return
    :param sort_key: image attribute by which results should be sorted
    :param sort_dir: direction in which results should be sorted (asc, desc)
    :param force_show_deleted: view the deleted deterministic
    :param ticket_type: filter tickettemplate by ticket_type.
                        When a comma is contain in a value,
                        the ticket_type condition of the SQL
                        is connected in 'OR'.
    :param filters: other filtering option.
    """
    session = get_session()

    if sort_key is not None and 0 == len(sort_key):
        sort_key = None
    if sort_key is not None and sort_key[0] is None:
        sort_key = None
    sort_key = ['created_at'] if not sort_key else sort_key
    default_sort_dir = 'desc'

    if not sort_dir or sort_dir is None or 0 == len(sort_dir) \
            or sort_dir[0] is None:
        sort_dir = [default_sort_dir] * len(sort_key)
    elif len(sort_dir) == 1:
        default_sort_dir = sort_dir[0]
        sort_dir *= len(sort_key)

    ticket_template = models.TicketTemplate
    query = session.query(ticket_template)

    marker_obj = None
    if marker is not None:
        marker_obj = \
            _ticket_templates_get(context, marker,
                                  session=session,
                                  force_show_deleted=force_show_deleted)

    for key in ['created_at', 'id']:
        if key not in sort_key:
            sort_key.append(key)
            sort_dir.append(default_sort_dir)

    # other filter option.
    if filters:
        if 'workflow_pattern_id' in filters:
            query = query.filter(ticket_template.workflow_pattern_id ==
                                 filters.get('workflow_pattern_id'))

    # filter out deleted if context disallows it
    if not force_show_deleted\
            or not context.can_see_deleted:
        query = query.filter_by(deleted=False)

    if ticket_type is not None:
        query = query.filter(
            ticket_template.ticket_type.in_(ticket_type.split(",")))

    query = db_api_utils.paginate_query(query, ticket_template,
                                        limit, sort_key,
                                        marker=marker_obj,
                                        sort_dir=None,
                                        sort_dirs=sort_dir)

    rtn_objs = query.all()

    return rtn_objs


def ticket_templates_get(context, tickettemplate_id, force_show_deleted=False):
    """
    Get a ticket template that match zero or more filters.

    :param tickettemplate_id: Get the tickete template id.
    :param force_show_deleted: View the deleted deterministic
    """
    session = get_session()
    rtn = _ticket_templates_get(context, tickettemplate_id,
                                session=session,
                                force_show_deleted=force_show_deleted)
    rtn.roles = context.roles
    # Access the "workflow_pattern" field, to get by "lazy load operation"
    rtn.workflow_pattern
    return rtn


def ticket_templates_delete(context, tickettemplate_id):
    """Destroy the ticket template or raise if it does not exist
    :param tickettemplate_id: Target ticket template id.
    """
    session = get_session()

    with session.begin():
        ticket_template = _ticket_templates_get(
            context,
            tickettemplate_id,
            session=session,
            force_show_deleted=False)

        ticket_template.delete(session=session)
    return


def workflow_patterns_list(context, force_show_deleted=False):
    """List workflow pattern.
    :param force_show_deleted: View the deleted deterministic.
    """
    session = get_session()
    query = session.query(models.WorkflowPattern)

    # filter out deleted if context disallows it
    if not force_show_deleted or not context.can_see_deleted:
        query = query.filter_by(deleted=False)

    return query.all()


def workflow_patterns_get(context,
                          workflow_pattern_id,
                          workflow_pattern_code,
                          force_show_deleted=False):
    """Get a workflow pattern that match zero or more filters.
    :param workflow_pattern_id: Get the workflow pattern id.
    :param workflow_pattern_code: Get the workflow pattern code.
    :param force_show_deleted: View the deleted deterministic.
    """
    session = get_session()
    rtn = _workflow_pattern_get(context,
                                workflow_pattern_id,
                                workflow_pattern_code,
                                session=session,
                                force_show_deleted=force_show_deleted)

    return rtn


def workflow_patterns_create(context, **values):
    """Create a workflow pattern from the values dictionary.
    :param values: Entry workflow pattern data.
    """
    se = get_session()

    with (se).begin():
        data = models.WorkflowPattern()

        data.id = values.get('id')
        data.code = values.get('code')
        data.wf_pattern_contents = values.get('wf_pattern_contents')

        data.save(session=se)

    return data


def workflow_patterns_delete(context, workflowpattern_id):
    """Destroy the workflow pattern or raise if it does not exist
    :param workflowpattern_id: Target workflow pattern id.
    """
    session = get_session()

    with session.begin():
        workflow_pattern = _workflow_pattern_get(
            context,
            workflowpattern_id,
            None,
            session=session,
            force_show_deleted=False)

        workflow_pattern.delete(session=session)
    return


def _get_ticket_craete_data(template_contents, **values):
    """Create a new ticket data.
    :param template_contents: Used template contents.
    :param values: Entry ticket and workflow data.
    """
    ticket = models.Ticket()

    ticket.id = values.get('id')
    ticket.ticket_template_id = values.get('ticket_template_id')
    ticket.tenant_id = values.get('tenant_id')
    ticket.tenant_name = values.get('tenant_name')
    ticket.owner_id = values.get('owner_id')
    ticket.owner_name = values.get('owner_name')
    ticket.owner_at = values.get('owner_at')
    ticket.ticket_detail = values.get('ticket_detail2')

    # Set ticket template data
    ticket.ticket_type = template_contents['ticket_type']
    ticket.target_id = template_contents['target_id']
    ticket.action_detail = ""

    return ticket


def _get_workflow_craete_data(ticket_id, wf_pattern_contents, **values):
    """Create new workflow data.
    :param ticket_id: ID of a new ticket.
    :param wf_pattern_contents: Work flow pattern from ticket template.
    :param values: Entry ticket and workflow data.
    """
    workflows = []

    # For database start row, Search start status in workflow pattern contents.
    start_status = filter(lambda status:
                          status["status_code"] == _WF_START_STARTUS_CODE,
                          wf_pattern_contents['status_list'])
    status_of_start_entry_row = \
        start_status[0]['next_status'][0]['next_status_code']

    for status in wf_pattern_contents['status_list']:
        # StartStatus(none) is empty data.
        # Don't entry Database.
        if status["status_code"] == _WF_START_STARTUS_CODE:
            continue

        workflow = models.Workflow()

        workflow.id = str(uuid.uuid4())
        workflow.ticket_id = ticket_id
        workflow.status = _WF_STATUS_ACTIVE \
            if status["status_code"] == status_of_start_entry_row else \
            _WF_STATUS_NON_ACTIVE
        workflow.status_code = status["status_code"]
        workflow.status_detail = status
        workflow.target_role = "none"
        if workflow.status == _WF_STATUS_ACTIVE:
            workflow.confirmer_id = values.get('owner_id')
            workflow.confirmer_name = values.get('owner_name')
            workflow.confirmed_at = values.get('owner_at')
        else:
            workflow.confirmer_id = None
            workflow.confirmer_name = None
            workflow.confirmed_at = None
        workflow.additional_data = ""

        workflows.append(workflow)

    return workflows


def _ticket_craete(ctxt, se, template_contents, wf_pattern_contents, **values):
    """Create ticket data.
    This is between broker-before-action and broker^after-action.
    :param se: DB session.
    :param template_contents: json dumpd template contents.
    :param wf_pattern_contents: json dumpd workflow pattern contents.
    :param values: Entry ticket and workflow data.
    """
    ticket = _get_ticket_craete_data(
        template_contents,
        **values)
    workflows = _get_workflow_craete_data(
        ticket.id,
        wf_pattern_contents,
        **values)
    LOG.debug("session2==" + str(se))
    try:
        ticket.save(session=se)
        for workflow in workflows:
            workflow.save(session=se)

    except db_exception.DBDuplicateEntry:
        raise exception.Duplicate("ID %s already exists!" % id)


def tickets_create(context, **values):
    """Create a ticket from the values dictionary.
    :param values: Entry ticket and workflow data.
    """
    se = get_session()

    try:
        ticket_template = _ticket_templates_get(
            context, values.get('ticket_template_id'), se)
        wf_pattern = _workflow_pattern_get(
            context, ticket_template.workflow_pattern_id, None, se)

        template = templates.TicketTemplate.load(
            ticket_template.template_contents)

        # Load broker
        broker_name = template.get_handler_class()

        broker = common_utils.load_class(broker_name)(
            context,
            template.ticket_template_contents,
            wf_pattern.wf_pattern_contents,
            **values)

        broker.do_exec(_ticket_craete, se, **values)

    except Exception:
        def _ticket_craete_for_error(se):
            try:
                _ticket_get(context, values['id'])
            except exception.NotFound:
                _ticket_craete(context,
                               se,
                               template.ticket_template_contents,
                               wf_pattern.wf_pattern_contents,
                               **values)
        se = get_session()
        with (se).begin():
            _ticket_craete_for_error(se)
            _add_error_record(se, values.get('id'), values.get('owner_id'),
                              values.get('owner_name'), sys.exc_info(),
                              **values)
        raise


def _ticket_update(ctxt, se, template_contents, wf_pattern_contents, **values):
    """Create ticket data.
    This is between broker-before-action and broker^after-action.
    :param se: DB session.
    :param template_contents: json dumpd template contents.
    :param wf_pattern_contents: json dumpd workflow pattern contents.
    :param values: Entry ticket and workflow data.
    """
    # Close last status
    last_wf = _workflow_get(ctxt, values.get('last_workflow_id'), se)
    last_wf.status = 2
    last_wf.save(se)

    # Activated the next status
    next_wf = _workflow_get(ctxt, values.get('next_workflow_id'), se)
    next_wf.status = 1
    next_wf.confirmer_id = values.get('confirmer_id')
    next_wf.confirmer_name = values.get('confirmer_name')
    next_wf.confirmed_at = values.get('confirmed_at')
    next_wf.additional_data = values.get('additional_data2')
    next_wf.save(se)


def tickets_update(context, ticket_id, **values):
    """Create a ticket from the values dictionary.
    :param values: Entry ticket and workflow data.
    """
    se = get_session()

    try:
        LOG.debug("=====tickets_update======")

        ticket = _ticket_get(context, ticket_id, se)
        ticket_template = ticket.ticket_template
        template = templates.TicketTemplate.load(
            ticket_template.template_contents)
        wf_pattern = ticket_template.workflow_pattern

        values['id'] = ticket.id
        values['owner_id'] = ticket.owner_id
        values['owner_name'] = ticket.owner_name
        values['owner_at'] = ticket.owner_at

        # Load broker
        broker_name = template.get_handler_class()

        broker = common_utils.load_class(broker_name)(
            context,
            template.ticket_template_contents,
            wf_pattern.wf_pattern_contents,
            **values)

        broker.do_exec(_ticket_update, se, ticket_id=ticket_id, **values)
        LOG.debug("=====tickets_update======")

    except Exception:
        se = get_session()
        with (se).begin():
            _add_error_record(se,
                              values.get('id'), values.get('confirmer_id'),
                              values.get('confirmer_name'), sys.exc_info(),
                              **values)
        raise


def _add_error_record(se, ticket_id, user_id, user_name, exc_info, **values):
    query = se.query(models.Workflow).\
        filter_by(ticket_id=ticket_id).\
        filter_by(status=1)
    wf_list = query.all()
    for wf in wf_list:
        wf.status = 2
        wf.save(se)

    workflow = models.Workflow()
    workflow.id = str(uuid.uuid4())
    workflow.ticket_id = ticket_id
    workflow.status = 1
    workflow.status_code = 'error'
    workflow.status_detail = {"status_code": "error",
                              "status_name": {"Default": "Error"},
                              "next_status": [{}]}
    workflow.target_role = "none"
    workflow.confirmer_id = user_id
    workflow.confirmer_name = user_name
    workflow.confirmed_at = datetime.utcnow()
    description = 'Please contact your administrator.'
    additional_data = {"Message": description}
    workflow.additional_data = json.dumps(additional_data)
    workflow.save(se)


def _ticket_get(context, ticket_id,
                session=None, force_show_deleted=False):
    session = session or get_session()

    try:
        query = session.query(models.Ticket).filter_by(id=ticket_id)

        # filter out deleted if context disallows it
        if not force_show_deleted\
                or not context.can_see_deleted:
            query = query.filter_by(deleted=False)

        if not context.is_admin:
            query = query.filter_by(tenant_id=context.tenant)

        obj = query.one()

        wf_list = session.query(models.Workflow).\
            filter_by(ticket_id=ticket_id).all()
        obj.workflow = wf_list

    except sa_orm.exc.NoResultFound:
        msg = (_("No Ticket found with ID %s") % ticket_id)
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return obj


def _workflow_get(context, workflow_id, session=None):
    session = session or get_session()

    try:
        query = session.query(models.Workflow).filter_by(id=workflow_id)

        obj = query.one()
    except sa_orm.exc.NoResultFound:
        msg = (_("No Workflow found with id %s") % workflow_id)
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return obj


def workflow_list(context, ticket_id, status=None, session=None):
    session = session or get_session()

    try:
        query = session.query(models.Workflow).filter_by(ticket_id=ticket_id)
        if status:
            query = query.filter_by(status=status)

        objs = query.all()
    except sa_orm.exc.NoResultFound:
        msg = (_("No Workflow found with ticket_id %s") % ticket_id)
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return objs


def tickets_list(context, marker=None, limit=None,
                 sort_key=None, sort_dir=None,
                 force_show_deleted=False, filters=None):
    """
    Get all Ticket that match zero or more filters.

    :param marker: id after which to start page
    :param limit: maximum number of images to return
    :param sort_key: image attribute by which results should be sorted
    :param sort_dir: direction in which results should be sorted (asc, desc)
    :param force_show_deleted: view the deleted deterministic
    :param filters: other filtering option.
                ticket_type filter is when a comma is contain in a value,
                the ticket_type condition of the SQL
                is connected in 'OR'.
    """
    objs = []
    session = get_session()

    if sort_key is not None and 0 == len(sort_key):
        sort_key = None
    if sort_key is not None and sort_key[0] is None:
        sort_key = None
    sort_key = ['created_at'] if not sort_key else sort_key
    default_sort_dir = 'desc'

    if not sort_dir or sort_dir is None or 0 == len(sort_dir) \
            or sort_dir[0] is None:
        sort_dir = [default_sort_dir] * len(sort_key)
    elif len(sort_dir) == 1:
        default_sort_dir = sort_dir[0]
        sort_dir *= len(sort_key)

    # create SQL
    m_Workflow = models.Workflow
    m_Ticket = models.Ticket

    # Set workflow filter
    last_wf_sq = session.query(m_Workflow).filter(m_Workflow.status == 1)
    if 'last_status_code' in filters:
        last_wf_sq = last_wf_sq.\
            filter(m_Workflow.status_code == filters.get('last_status_code'))
    if 'last_confirmer_id' in filters:
        last_wf_sq = last_wf_sq.\
            filter(m_Workflow.confirmer_id == filters.get('last_confirmer_id'))
    if 'last_confirmer_name' in filters:
        last_wf_sq = last_wf_sq.\
            filter(m_Workflow.confirmer_name ==
                   filters.get('last_confirmer_name'))
    if 'last_confirmed_at_from' in filters:
        last_wf_sq = last_wf_sq.\
            filter(m_Workflow.confirmed_at >=
                   filters.get('last_confirmed_at_from'))
    if 'last_confirmed_at_to' in filters:
        last_wf_sq = last_wf_sq.\
            filter(m_Workflow.confirmed_at <=
                   filters.get('last_confirmed_at_to'))

    last_wf_sq = last_wf_sq.subquery()
    last_wf = aliased(m_Workflow, last_wf_sq)

    query = session.query(m_Ticket, last_wf)
    query = query.join((last_wf, m_Ticket.id == last_wf.ticket_id))

    if context.is_admin:
        if 'tenant_id' in filters:
            query = query.filter(m_Ticket.tenant_id ==
                                 filters.get('tenant_id'))
    else:
        query = query.filter(m_Ticket.tenant_id == context.tenant)

    if 'ticket_template_id' in filters:
        query = query.filter(m_Ticket.ticket_template_id ==
                             filters.get('ticket_template_id'))
    if 'ticket_type' in filters:
        ticket_types = filters.get('ticket_type') \
            if isinstance(filters.get('ticket_type'), list) \
            else [filters.get('ticket_type')]

        for ticket_type in ticket_types:
            query = query.filter(m_Ticket.ticket_type.in_(
                ticket_type.split(",")))

    if 'target_id' in filters:
        query = query.filter(m_Ticket.target_id ==
                             filters.get('target_id'))
    if 'owner_id' in filters:
        query = query.filter(m_Ticket.owner_id ==
                             filters.get('owner_id'))
    if 'owner_name' in filters:
        query = query.filter(m_Ticket.owner_name ==
                             filters.get('owner_name'))
    if 'owner_at_from' in filters:
        query = query.filter(m_Ticket.owner_at >=
                             filters.get('owner_at_from'))
    if 'owner_at_to' in filters:
        query = query.filter(m_Ticket.owner_at <=
                             filters.get('owner_at_to'))
    if 'ticket_template_id' in filters:
        query = query.filter(m_Ticket.ticket_template_id ==
                             filters.get('ticket_template_id'))

    # Set tickettemplate contents filter
    if 'ticket_template_name' in filters\
            or 'application_kinds_name' in filters:

        ticket_template_name = filters['ticket_template_name'] \
            if 'ticket_template_name' in filters else None
        application_kinds_name = filters['application_kinds_name'] \
            if 'application_kinds_name' in filters else None

        template_id = _get_template_id_from_filter(
            ticket_template_name,
            application_kinds_name)

        if 0 < len(template_id):
            query = query.filter(m_Ticket.ticket_template_id.in_(template_id))
        else:
            return objs

    marker_obj = None
    if marker is not None:
        marker_obj = \
            _ticket_get(context, marker,
                        session=session,
                        force_show_deleted=force_show_deleted)

    for key in ['created_at', 'id']:
        if key not in sort_key:
            sort_key.append(key)
            sort_dir.append(default_sort_dir)

    # filter out deleted if context disallows it
    if not force_show_deleted\
            or not context.can_see_deleted:
        query = query.filter(models.Ticket.deleted == False)

    query = db_api_utils.paginate_query(query, models.Ticket,
                                        limit, sort_key,
                                        marker=marker_obj,
                                        sort_dir=None,
                                        sort_dirs=sort_dir)

    for obj_t, obj_lw in query.all():
        obj_t.last_workflow = obj_lw
        objs.append(obj_t)

    return objs


def _get_template_id_from_filter(ticket_template_name,
                                 application_kinds_name):
    """
    Filtering ticket from ticket template contents values.
    :param ticket_template_name:
        value in 'ticket_template_name' key of contents
    :param application_kinds_name:
        value in 'application_kinds_name' key of contents
    """
    template_id = []
    templates = ticket_templates_list(None)

    for row in templates:
        exists_ticket_template_name = False
        exists_application_kinds_name = False

        contents = row["template_contents"]

        # root/ticket_template_name
        # The multi language does not consider it by filter
        if ticket_template_name and \
                "ticket_template_name" in contents:
            for key, value in contents["ticket_template_name"].items():
                if value == ticket_template_name:
                    exists_ticket_template_name = True
                    break

        else:
            exists_ticket_template_name = True

        # root/application_kinds_name
        # The multi language does not consider it by filter
        if application_kinds_name and \
                "application_kinds_name" in contents:
            for key, value in contents["application_kinds_name"].items():
                if value == application_kinds_name:
                    exists_application_kinds_name = True
                    break
        else:
            exists_application_kinds_name = True

        # Filtering
        if exists_ticket_template_name and \
                exists_application_kinds_name:

            template_id.append(row.id)

    return template_id


def tickets_get(context, ticket_id, force_show_deleted=False):
    """
    Get a ticket that match zero or more filters.

    :param ticket_id: Get the tickete id.
    :param force_show_deleted: View the deleted deterministic
    """
    ticket = _ticket_get(context, ticket_id,
                         force_show_deleted=force_show_deleted)
    ticket.roles = context.roles
    return ticket


def tickets_delete(context, ticket_id):
    """
    Destroy the ticket or raise if it does not exist

    :param ticket_id: Target ticket id.
    """
    session = get_session()
    with session.begin():
        ticket = _ticket_get(context, ticket_id, session=session,
                             force_show_deleted=False)
        workflows = workflow_list(context, ticket_id, session=session)
        ticket.delete(session=session)
        for wf in workflows:
            wf.delete(session=session)
    return


def _get_contract_create_data(**values):
    """Get contract data from values.
        :param values: Contract dict data.
        :return Contract.
    """
    contract_ref = models.Contract()

    for key in values:
        if key in ('lifetime_start', 'lifetime_end',
                   'application_date') and values[key]:
            val = datetime.strptime(values[key], '%Y-%m-%dT%H:%M:%S.%f')
        else:
            val = values[key]

        setattr(contract_ref, key, val)

    return contract_ref


def _contract_create(se, **values):
    """Create contract.
        :param se: database session.
        :param values: Contract values.
        :return Contract.
    """
    contract = _get_contract_create_data(**values)

    try:
        contract.save(session=se)

    except db_exception.DBDuplicateEntry:
        raise exception.Duplicate("Contract is already exist,contract_id=%s." %
                                  contract.contract_id)


def contract_create(ctxt, **values):
    """Create contract.
        :param values: Contract values.
        :return Contract.
    """
    se = get_session()

    with se.begin():
        _contract_create(se, **values)
        return _contract_get(ctxt, values['contract_id'], se).to_dict()


def _contract_update(contract, **values):
    """Update contract.
        :param contract: Contract object.
        :param values: Contract values.
        :return Contract.
    """
    for key in values:
        if key in ('lifetime_start', 'lifetime_end',
                   'application_date') and values[key]:
            val = datetime.strptime(values[key], '%Y-%m-%dT%H:%M:%S.%f')
        else:
            val = values[key]
        setattr(contract, key, val)

    return contract


def contract_update(ctxt, contract_id, **values):
    """Update contract.
        :param ctxt: http context.
        :param contract_id: Contract id.
        :param values: Contract values.
        :return Contract.
    """
    se = get_session()

    with se.begin():
        contract = _contract_get(ctxt, contract_id, se)
        return _contract_update(contract, **values).to_dict()


def _contract_get(context, contract_id, session=None):
    session = session or get_session()

    try:
        query = session.query(models.Contract)\
            .filter_by(contract_id=contract_id)

        contractobj = query.one()

    except sa_orm.exc.NoResultFound:
        msg = (_("No contractobj found with id %s") % contract_id)
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return contractobj


def contract_get(context, contract_id):
    """
    Get contract.

    :param contract_id: Get the contract id.
    :param force_show_deleted: View the deleted deterministic
    """
    contractobj = _contract_get(context, contract_id)

    contract = {}
    contract['contract_id'] = contractobj.contract_id
    contract['region_id'] = contractobj.region_id
    contract['project_id'] = contractobj.project_id
    contract['project_name'] = contractobj.project_name
    contract['catalog_id'] = contractobj.catalog_id
    contract['catalog_name'] = contractobj.catalog_name
    contract['num'] = contractobj.num
    contract['parent_ticket_template_id'] = \
        contractobj.parent_ticket_template_id
    contract['ticket_template_id'] = contractobj.ticket_template_id
    contract['parent_ticket_template_name'] = \
        contractobj.parent_ticket_template_name
    contract['ticket_template_name'] = contractobj.ticket_template_name
    contract['parent_application_kinds_name'] = \
        contractobj.parent_application_kinds_name
    contract['application_kinds_name'] = contractobj.application_kinds_name
    contract['cancel_application_id'] = contractobj.cancel_application_id
    contract['application_id'] = contractobj.application_id
    contract['application_name'] = contractobj.application_name
    contract['application_date'] = contractobj.application_date
    contract['parent_contract_id'] = contractobj.parent_contract_id
    contract['lifetime_start'] = contractobj.lifetime_start
    contract['lifetime_end'] = contractobj.lifetime_end
    contract['created_at'] = contractobj.created_at
    contract['updated_at'] = contractobj.updated_at
    contract['deleted_at'] = contractobj.deleted_at
    contract['deleted'] = contractobj.deleted
    contract['expansions'] = {}
    contract['expansions']['expansion_key1'] = contractobj.expansion_key1
    contract['expansions']['expansion_key2'] = contractobj.expansion_key2
    contract['expansions']['expansion_key3'] = contractobj.expansion_key3
    contract['expansions']['expansion_key4'] = contractobj.expansion_key4
    contract['expansions']['expansion_key5'] = contractobj.expansion_key5
    contract['expansions_text'] = {}
    contract['expansions_text']['expansion_text'] = contractobj.expansion_text

    return contract


def contract_delete(ctxt, contract_id):
    """Destroy the contract or raise if it does not exist.
        :param ctxt: Http context.
        :param contract_id: Contract id.
    """
    se = get_session()
    with se.begin():
        contract = _contract_get(ctxt, contract_id, se)
        se.delete(contract)


def contract_list(ctxt, project_id=None, region_id=None,
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
        :param parent_contract_id: parent_contract_id of contract.
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
    se = get_session()

    Contract = models.Contract

    default_sort_key = 'created_at'
    default_sort_dir = 'desc'
    try:
        # init sort_key and sort_dir
        if not sort_key:
            sort_key = [default_sort_key]

        if not sort_dir:
            sort_dir = [default_sort_dir] * len(sort_key)

        if len(sort_key) < len(sort_dir):
            sort_dir = sort_dir[:len(sort_key)]
        elif len(sort_dir) < len(sort_key):
            sort_dir.extend([default_sort_dir] *
                            (len(sort_key) - len(sort_dir)))

        # init marker
        marker_obj = None
        if marker:
            marker_obj = _contract_get(ctxt, marker, se)

        # main query
        query = se.query(models.Contract)

        # non- admin is adding a condition to get
        # the price data of a common price data + own tenant in default
        if not ctxt.is_admin:
            query = query.filter(Contract.project_id == ctxt.tenant)
        else:
            if project_id:
                query = query.filter(Contract.project_id == project_id)

        # key query
        if not force_show_deleted or not ctxt.is_admin:
            query = query.filter(Contract.deleted == false())
        if region_id:
            query = query.filter(Contract.region_id == region_id)
        if project_name:
            query = query.filter(Contract.project_name == project_name)
        if catalog_name:
            query = query.filter(Contract.catalog_name == catalog_name)
        if application_id:
            query = query.filter(Contract.application_id == application_id)
        if ticket_template_name:
            query = query.filter(Contract.ticket_template_name ==
                                 ticket_template_name)
        if application_kinds_name:
            query = query.filter(Contract.application_kinds_name ==
                                 application_kinds_name)
        if application_name:
            query = query.filter(Contract.application_name ==
                                 application_name)
        if parent_contract_id:
            query = query.filter(Contract.parent_contract_id ==
                                 parent_contract_id)
        if application_date_from:
            query = query.filter(
                sqlalchemy.or_(Contract.application_date.is_(None),
                               Contract.application_date >=
                               datetime.strptime(application_date_from,
                                                 '%Y-%m-%dT%H:%M:%S.%f')))
        if application_date_to:
            query = query.filter(
                sqlalchemy.or_(Contract.application_date.is_(None),
                               Contract.application_date <=
                               datetime.strptime(application_date_to,
                                                 '%Y-%m-%dT%H:%M:%S.%f')))
        if lifetime_start_from:
            query = query.filter(
                sqlalchemy.or_(Contract.lifetime_start.is_(None),
                               Contract.lifetime_start >=
                               datetime.strptime(lifetime_start_from,
                                                 '%Y-%m-%dT%H:%M:%S.%f')))
        if lifetime_start_to:
            query = query.filter(
                sqlalchemy.or_(Contract.lifetime_start.is_(None),
                               Contract.lifetime_start <=
                               datetime.strptime(lifetime_start_to,
                                                 '%Y-%m-%dT%H:%M:%S.%f')))
        if lifetime_end_from:
            query = query.filter(
                sqlalchemy.or_(Contract.lifetime_end.is_(None),
                               Contract.lifetime_end >=
                               datetime.strptime(lifetime_end_from,
                                                 '%Y-%m-%dT%H:%M:%S.%f')))
        if lifetime_end_to:
            query = query.filter(
                sqlalchemy.or_(Contract.lifetime_end.is_(None),
                               Contract.lifetime_end <=
                               datetime.strptime(lifetime_end_to,
                                                 '%Y-%m-%dT%H:%M:%S.%f')))
        if lifetime:
            query = query.filter(Contract.lifetime_start <= lifetime)
            query = query.filter(Contract.lifetime_end >= lifetime)
        if date_in_lifetime:
            lt_s = date_in_lifetime.replace(hour=23, minute=59, second=59,
                                            microsecond=999999)
            query = query.filter(
                sqlalchemy.or_(Contract.lifetime_start.is_(None),
                               Contract.lifetime_start <= lt_s))

            lt_e = date_in_lifetime.replace(hour=0, minute=0, second=0,
                                            microsecond=0)
            query = query.filter(
                sqlalchemy.or_(Contract.lifetime_end.is_(None),
                               Contract.lifetime_end >= lt_e))

        for key in ['created_at', 'contract_id']:
            if key not in sort_key:
                sort_key.append(key)
                sort_dir.append(default_sort_dir)

        query = db_api_utils.paginate_query(query, models.Contract,
                                            limit, sort_key,
                                            marker=marker_obj,
                                            sort_dir=None,
                                            sort_dirs=sort_dir)

        contract_refs = query.all()

        contracts = []
        for contract_ref in contract_refs:
            contracts.append(contract_ref.to_dict())

    except sa_orm.exc.NoResultFound:
        msg = _("Notfound")
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return contracts


def goods_create(context, **values):
    """Create a goods from the values dictionary.
    :param values: Entry goods data.
    """
    se = get_session()

    with (se).begin():
        goods = models.Goods()

        for key in values:
            setattr(goods, key, values[key])

        try:
            goods.save(session=se)
        except db_exception.DBDuplicateEntry:
            raise exception.Duplicate(
                "Goods ID %s already exists!" % goods['goods_id'])

    return se.query(models.Goods).get(goods['goods_id']).to_dict()


def _goods_update(goods, **values):
    """Update goods.
        :param goods: Goods object.
        :param values: Goods values.
        :return Goods.
    """
    for key, val in values.items():
        setattr(goods, key, val)

    return goods


def goods_update(ctxt, goods_id, **values):
    """Update goods.
        :param ctxt: Http context.
        :param goods_id: Goods id.
        :param values: Goods values.
        :return Goods.
    """
    se = get_session()

    with se.begin():
        goods = _goods_get(ctxt, goods_id, se)
        return _goods_update(goods, **values).to_dict()


def goods_list(context, marker=None, limit=None,
               sort_key=None, sort_dir=None,
               force_show_deleted=False, region_id=None):
    """
    Get all goods that match zero or more filters.

    :param marker: id after which to start page
    :param limit: maximum number of images to return
    :param sort_key: image attribute by which results should be sorted
    :param sort_dir: direction in which results should be sorted (asc, desc)
    :param force_show_deleted: view the deleted deterministic
    :param region_id: filter
    """
    session = get_session()

    if sort_key is not None and len(sort_key) == 0:
        sort_key = None
    if sort_key is not None and sort_key[0] is None:
        sort_key = None
    sort_key = ['created_at'] if not sort_key else sort_key
    default_sort_dir = 'desc'

    if not sort_dir or len(sort_dir) == 0 \
            or sort_dir[0] is None:
        sort_dir = [default_sort_dir] * len(sort_key)
    elif len(sort_dir) == 1:
        default_sort_dir = sort_dir[0]
        sort_dir *= len(sort_key)

    query = session.query(models.Goods)

    if region_id is not None:
        query = query.filter(
            models.Goods.region_id == region_id)

    marker_obj = None
    if marker is not None:
        marker_obj = \
            _goods_get(context, marker,
                       session=session)

    for key in ['created_at', ]:
        if key not in sort_key:
            sort_key.append(key)
            sort_dir.append(default_sort_dir)

    # filter out deleted if context disallows it
    if not force_show_deleted or not context.is_admin:
        query = query.filter_by(deleted=False)

    query = db_api_utils.paginate_query(query, models.Goods,
                                        limit, sort_key,
                                        marker=marker_obj,
                                        sort_dir=None,
                                        sort_dirs=sort_dir)

    goods_refs = query.all()

    goods_list = []
    for goods_ref in goods_refs:
        goods_list.append(goods_ref.to_dict())

    return goods_list


def _goods_get(context, goods_id, session=None):
    session = session or get_session()

    try:
        query = session.query(models.Goods).filter_by(goods_id=goods_id)
        goodsobj = query.one()

    except sa_orm.exc.NoResultFound:
        msg = (_("No goodsobj found with id %s") % goods_id)
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return goodsobj


def goods_get(context, goods_id):
    """Get a goods that match zero or more filters.
    :param goods_id: Get the goods id.
    """
    goodsobj = _goods_get(context, goods_id)

    return goodsobj.to_dict()


def goods_delete(ctxt, goods_id):
    """Destroy the goods or raise if it does not exist.
        :param ctxt: Http context.
        :param goods_id: Goods id.
    """
    se = get_session()
    with se.begin():
        goods = _goods_get(ctxt, goods_id, se)
        se.delete(goods)


def catalog_create(context, **values):
    """Create a catalog from the values dictionary.
    :param values: Entry goods data.
    """
    se = get_session()

    with (se).begin():
        catalog = models.Catalog()

        for key in values:
            if key in ('lifetime_start', 'lifetime_end') and values[key]:
                val = datetime.strptime(values[key], '%Y-%m-%dT%H:%M:%S.%f')
            else:
                val = values[key]
            setattr(catalog, key, val)

        try:
            catalog.save(session=se)
        except db_exception.DBDuplicateEntry:
            raise exception.Duplicate(
                "Catalog ID %s already exists!" % catalog['catalog_id'])

    return se.query(models.Catalog).get(catalog['catalog_id']).to_dict()


def _catalog_update(catalog, **values):
    """Update catalog.
        :param catalog: Catalog object.
        :param values: Catalog values.
        :return Catalog.
    """
    for key in values:
        if key in ('lifetime_start', 'lifetime_end') and values[key]:
            val = datetime.strptime(values[key], '%Y-%m-%dT%H:%M:%S.%f')
        else:
            val = values[key]
        setattr(catalog, key, val)

    return catalog


def catalog_update(ctxt, catalog_id, **values):
    """Update catalog.
        :param ctxt: Http context.
        :param catalog_id: Catalog_id.
        :param values: Catalog values.
        :return Catalog.
    """
    se = get_session()

    with se.begin():
        catalog = _catalog_get(ctxt, catalog_id, se)
        return _catalog_update(catalog, **values).to_dict()


def _catalog_get(context, catalog_id, session=None):
    session = session or get_session()

    try:
        query = session.query(models.Catalog).filter_by(catalog_id=catalog_id)

        catalogobj = query.one()

    except sa_orm.exc.NoResultFound:
        msg = (_("No catalogobj found with id %s") % catalog_id)
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return catalogobj


def catalog_get(context, catalog_id):
    """
    Get a catalog that match zero or more filters.
    :param catalog_id: Get the catalog id.
    """
    catalogobj = _catalog_get(context, catalog_id)

    catalog = {}
    catalog['catalog_id'] = catalogobj.catalog_id
    catalog['region_id'] = catalogobj.region_id
    catalog['catalog_name'] = catalogobj.catalog_name
    catalog['lifetime_start'] = catalogobj.lifetime_start
    catalog['lifetime_end'] = catalogobj.lifetime_end
    catalog['created_at'] = catalogobj.created_at
    catalog['updated_at'] = catalogobj.updated_at
    catalog['deleted_at'] = catalogobj.deleted_at
    catalog['deleted'] = catalogobj.deleted
    catalog['expansions'] = {}
    catalog['expansions']['expansion_key1'] = catalogobj.expansion_key1
    catalog['expansions']['expansion_key2'] = catalogobj.expansion_key2
    catalog['expansions']['expansion_key3'] = catalogobj.expansion_key3
    catalog['expansions']['expansion_key4'] = catalogobj.expansion_key4
    catalog['expansions']['expansion_key5'] = catalogobj.expansion_key5
    catalog['expansions_text'] = {}
    catalog['expansions_text']['expansion_text'] = catalogobj.expansion_text

    return catalog


def _catalog_get_id(context, catalog_id,
                    session=None, force_show_deleted=None):
    session = session or get_session()

    try:
        query = session.query(models.Catalog).filter_by(catalog_id=catalog_id)

        # filter out deleted if context disallows it
        if not force_show_deleted:
            query = query.filter_by(deleted=False)

        catalogobj = query.one()

    except sa_orm.exc.NoResultFound:
        msg = (_("No catalogobj found with id %s") % catalog_id)
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return catalogobj


def catalog_list(context, marker=None, limit=None,
                 sort_key=None, sort_dir=None,
                 force_show_deleted=False, filters=None):
    """Get all catalog that match zero or more filters.

    :param marker: id after which to start page
    :param limit: maximum number of catalog to return
    :param sort_key: catalog attribute by which results should be sorted
    :param sort_dir: direction in which results should be sorted (asc, desc)
    :param force_show_deleted: view the deleted deterministic
    """
    session = get_session()

    if sort_key is not None and len(sort_key) == 0:
        sort_key = None
    if sort_key is not None and sort_key[0] is None:
        sort_key = None
    sort_key = ['created_at'] if not sort_key else sort_key
    default_sort_dir = 'desc'

    if not sort_dir or len(sort_dir) == 0 \
            or sort_dir[0] is None:
        sort_dir = [default_sort_dir] * len(sort_key)
    elif len(sort_dir) == 1:
        default_sort_dir = sort_dir[0]
        sort_dir *= len(sort_key)

    query = session.query(models.Catalog)

    if 'catalog_id' in filters:
        query = query.filter(
            models.Catalog.catalog_id == filters.get('catalog_id'))
    if 'region_id' in filters:
        query = query.filter(
            models.Catalog.region_id == filters.get('region_id'))
    if 'catalog_name' in filters:
        query = query.filter(
            models.Catalog.catalog_name == filters.get('catalog_name'))
    if 'lifetime' in filters:
        lifetime = filters.get('lifetime')
        query = query.filter(models.Catalog.lifetime_start <= lifetime)
        query = query.filter(models.Catalog.lifetime_end >= lifetime)

    marker_obj = None
    if marker is not None:
        marker_obj = \
            _catalog_get_id(context, marker,
                            session=session,
                            force_show_deleted=force_show_deleted)

    for key in ['created_at', ]:
        if key not in sort_key:
            sort_key.append(key)
            sort_dir.append(default_sort_dir)

    # filter out deleted if context disallows it
    if not force_show_deleted:
        query = query.filter_by(deleted=False)

    query = db_api_utils.paginate_query(query, models.Catalog,
                                        limit, sort_key,
                                        marker=marker_obj,
                                        sort_dir=None,
                                        sort_dirs=sort_dir)

    catalog_refs = query.all()

    catalog_list = []
    for catalog_ref in catalog_refs:
        catalog = {}
        catalog['catalog_id'] = catalog_ref.catalog_id
        catalog['region_id'] = catalog_ref.region_id
        catalog['catalog_name'] = catalog_ref.catalog_name
        catalog['lifetime_start'] = catalog_ref.lifetime_start
        catalog['lifetime_end'] = catalog_ref.lifetime_end
        catalog['created_at'] = catalog_ref.created_at
        catalog['updated_at'] = catalog_ref.updated_at
        catalog['deleted_at'] = catalog_ref.deleted_at
        catalog['deleted'] = catalog_ref.deleted
        catalog['expansions'] = {}
        catalog['expansions']['expansion_key1'] = \
            catalog_ref.expansion_key1
        catalog['expansions']['expansion_key2'] = \
            catalog_ref.expansion_key2
        catalog['expansions']['expansion_key3'] = \
            catalog_ref.expansion_key3
        catalog['expansions']['expansion_key4'] = \
            catalog_ref.expansion_key4
        catalog['expansions']['expansion_key5'] = \
            catalog_ref.expansion_key5
        catalog['expansions_text'] = {}
        catalog['expansions_text']['expansion_text'] = \
            catalog_ref.expansion_text

        catalog_list.append(catalog)

    return catalog_list


def catalog_delete(ctxt, catalog_id):
    """Destroy the catalog or raise if it does not exist.
        :param ctxt: Http context.
        :param catlaog_id: Catalog id.
    """
    se = get_session()
    with se.begin():
        catalog = _catalog_get(ctxt, catalog_id, se)
        se.delete(catalog)


def catalog_contents_create(context, **values):
    """Create a goods from the values dictionary.
    :param values: Entry catalog contents data.
    """
    se = get_session()

    with (se).begin():
        catalog_contents = models.CatalogContents()

        for key in values:
            setattr(catalog_contents, key, values[key])

        catalog_contents.save(session=se)

    repkey = (catalog_contents['catalog_id'], catalog_contents['seq_no'])
    return se.query(models.CatalogContents).get(repkey).to_dict()


def catalog_contents_list(ctxt, catalog_id,
                          limit=None, marker=None,
                          sort_key=None, sort_dir=None,
                          force_show_deleted=False):
    """Get all CatalogContents that match zero or more filters.
        :param catalog_id: catalog_id of catalog_contents.
        :param limit: maximum number of images to return.
        :param marker: id after which to start page.
        :param sort_key: catalog_contents attribute by
                which results should be sorted.
        :param sort_dir: dict in which results should be sorted (asc, desc).
        :param force_show_deleted: view the deleted deterministic.
    """
    se = get_session()

    CatalogContents = models.CatalogContents

    default_sort_key = 'created_at'
    default_sort_dir = 'desc'
    try:
        # init sort_key and sort_dir
        if not sort_key:
            sort_key = [default_sort_key]

        if not sort_dir:
            sort_dir = [default_sort_dir] * len(sort_key)

        if len(sort_key) < len(sort_dir):
            sort_dir = sort_dir[:len(sort_key)]
        elif len(sort_dir) < len(sort_key):
            sort_dir.extend([default_sort_dir] *
                            (len(sort_key) - len(sort_dir)))

        # default sort key append
        if default_sort_key not in sort_key:
            sort_key.append(default_sort_key)
            sort_dir.append(default_sort_dir)

        # init marker
        marker_obj = None
        if marker:
            marker_obj = _catalog_contents_get_by_seq_no(ctxt,
                                                         marker,
                                                         session=se)

        # main query
        query = se.query(models.CatalogContents)
        query = query.filter(CatalogContents.catalog_id == catalog_id)
        # key query
        if not force_show_deleted or not ctxt.is_admin:
            query = query.filter(CatalogContents.deleted == False)

        query = db_api_utils.paginate_query(query, models.CatalogContents,
                                            limit, sort_key,
                                            marker=marker_obj,
                                            sort_dir=None,
                                            sort_dirs=sort_dir)

        catalog_contents_refs = query.all()

        catalog_contents = []
        for catalog_contents_ref in catalog_contents_refs:
            catalog_contents.append(catalog_contents_ref.to_dict())

    except sa_orm.exc.NoResultFound:
        msg = _("Notfound")
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return catalog_contents


def _catalog_contents_get_by_seq_no(context, seq_no, session=None):
    """Get catalog contents that match zero or more filters.
        :param context: Http context.
        :param seq_no: Get the seq_no.
        :param session: Database session.
    """
    session = session or get_session()

    try:
        query = session.query(models.CatalogContents).filter_by(
            seq_no=seq_no)

        catalog_contents_obj = query.one()

    except sa_orm.exc.NoResultFound:
        msg = (_("catalog_contents not found"))
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return catalog_contents_obj


def _catalog_contents_get(context, catalog_id, seq_no, session=None):
    session = session or get_session()

    try:
        query = session.query(models.CatalogContents).filter_by(
            catalog_id=catalog_id,
            seq_no=seq_no)

        catalog_contents_obj = query.one()

    except sa_orm.exc.NoResultFound:
        msg = (_("catalog_contents not found"))
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return catalog_contents_obj


def catalog_contents_get(ctxt, catalog_id, seq_no):
    """Get catalog contents that match zero or more filters.
    :param catalog_id: Get the catalog id.
    :param seq_no: Get the seq_no.
    """
    catalog_contents = _catalog_contents_get(ctxt, catalog_id, seq_no)

    return catalog_contents.to_dict()


def catalog_contents_update(context, catalog_id, seq_no, **values):
    """Update a catalog contents from the values dictionary.
    :param catalog_id: catalog_id of catalog_contents.
    :param seq_no: seq_no of catalog_contents.
    :param values: update value for catalog contents.
    """
    se = get_session()

    with (se).begin():
        update_contents = _catalog_contents_get(context,
                                                catalog_id,
                                                seq_no,
                                                se)
        for key in values:
                update_contents[key] = values[key]
        update_contents.save(se)

    catalog_contents = _catalog_contents_get(context, catalog_id, seq_no, se)

    return catalog_contents.to_dict()


def catalog_contents_delete(ctxt, catalog_id, seq_no):
    """Destroy the catalog contents or raise if it does not exist.
        :param ctxt: Http context.
        :param catlaog_id: Catalog id.
        :param seq_no: Seq no.
    """
    se = get_session()
    with se.begin():
        catalog_contents = _catalog_contents_get(ctxt, catalog_id, seq_no, se)
        se.delete(catalog_contents)


def catalog_scope_create(ctxt, **values):
    """Create a catalog scope from the values dictionary.
    :param values: Entry catalog scope data.
    """
    se = get_session()

    with (se).begin():
        catalog_scope = models.CatalogScope()

        for key in values:
            if key in ('lifetime_start', 'lifetime_end') and values[key]:
                val = datetime.strptime(values[key], '%Y-%m-%dT%H:%M:%S.%f')
            else:
                val = values[key]
            setattr(catalog_scope, key, val)

        try:
            catalog_scope.save(session=se)
        except db_exception.DBDuplicateEntry:
            raise exception.Duplicate(
                "Catalog scope ID is already exists!" % catalog_scope['id'])

    respkey = (catalog_scope['id'],
               catalog_scope['catalog_id'],
               catalog_scope['scope'])
    return se.query(models.CatalogScope).get(respkey).to_dict()


def _catalog_scope_get(context, catalog_scope_id, session=None):
    session = session or get_session()

    try:
        query = session.query(models.CatalogScope).filter_by(
            id=catalog_scope_id)

        catalog_scope_obj = query.one()
    except sa_orm.exc.NoResultFound:
        msg = (_("catalog_scope not found with id %s") % catalog_scope_id)
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return catalog_scope_obj


def catalog_scope_get(ctxt, catalog_scope_id):
    """Get the data for the specified id from catalog scope.
    :param catalog_scope_id: Get the catalog scope id.
    """
    catalog_scope = _catalog_scope_get(ctxt, catalog_scope_id)

    return catalog_scope.to_dict()


def catalog_scope_list(ctxt, marker=None, limit=None,
                       sort_key=None, sort_dir=None,
                       force_show_deleted=None, filters=None):
    """Get a list of catalog scope that match the filter.
    :param marker: id after which to start page
    :param limit: maximum number of images to return
    :param sort_key: item name by which results should be sorted
    :param sort_dir: direction in which results should be sorted (asc, desc)
    :param force_show_deleted: view the deleted deterministic
    :param filters: option to search a list
    """
    session = get_session()

    if sort_key is not None and len(sort_key) == 0:
        sort_key = None
    if sort_key is not None and sort_key[0] is None:
        sort_key = None
    sort_key = ['created_at'] if not sort_key else sort_key
    default_sort_dir = 'desc'

    if not sort_dir or len(sort_dir) == 0 or sort_dir[0] is None:
        sort_dir = [default_sort_dir] * len(sort_key)
    elif len(sort_dir) == 1:
        default_sort_dir = sort_dir[0]
        sort_dir *= len(sort_key)

    query = session.query(models.CatalogScope)

    if not ctxt.is_admin:
        query = query.filter(models.CatalogScope.scope == ctxt.tenant)
    else:
        if 'scope' in filters:
            query = query.filter(
                models.CatalogScope.scope == filters.get('scope'))
    if 'catalog_id' in filters:
        query = query.filter(
            models.CatalogScope.catalog_id == filters.get('catalog_id'))
    if 'lifetime' in filters:
        lifetime = datetime.strptime(filters.get('lifetime'),
                                     '%Y-%m-%dT%H:%M:%S.%f')
        query = query.filter(models.CatalogScope.lifetime_start <= lifetime)
        query = query.filter(models.CatalogScope.lifetime_end >= lifetime)

    marker_obj = None
    if marker is not None:
        marker_obj = _catalog_scope_get(ctxt, marker, session)

    for key in ['created_at', 'id']:
        if key not in sort_key:
            sort_key.append(key)
            sort_dir.append(default_sort_dir)

    if not force_show_deleted or not ctxt.is_admin:
        query = query.filter_by(deleted=False)

    query = db_api_utils.paginate_query(query, models.CatalogScope,
                                        limit, sort_key, marker=marker_obj,
                                        sort_dir=None, sort_dirs=sort_dir)

    catalog_scope_refs = query.all()

    catalog_scope_list = []
    for catalog_scope_ref in catalog_scope_refs:
        catalog_scope_list.append(catalog_scope_ref.to_dict())

    return catalog_scope_list


def catalog_scope_update(ctxt, catalog_scope_id, **values):
    """Update a catalog scope from the values dictionary.
    :param catalog_scope_id: ID of catalog scope table.
    :param values: update value for catalog scope.
    """
    se = get_session()

    with (se).begin():
        update_scope = _catalog_scope_get(ctxt, catalog_scope_id, se)

        for key in values:
            if key in ('lifetime_start', 'lifetime_end') and values[key]:
                val = datetime.strptime(values[key], '%Y-%m-%dT%H:%M:%S.%f')
            else:
                val = values[key]
            setattr(update_scope, key, val)
        update_scope.save(se)

    catalog_scope = _catalog_scope_get(ctxt, catalog_scope_id, se)

    return catalog_scope.to_dict()


def catalog_scope_delete(ctxt, catalog_scope_id):
    """Destroy the catalog scope or raise if it does not exist.
    :param catalog_scope_id: The id of catalog scope table.
    """
    se = get_session()
    with se.begin():
        catalog_scope = _catalog_scope_get(ctxt, catalog_scope_id, se)
        se.delete(catalog_scope)


def _valid_sort_key_check(sort_key, sort_dir):
    # check sort_key and sort_dir
    if sort_key is not None and len(sort_key) == 0:
        sort_key = None
    if sort_key is not None and sort_key[0] is None:
        sort_key = None
    sort_key = ['catalog_created_at'] if not sort_key else sort_key
    default_sort_dir = 'desc'

    if not sort_dir or len(sort_dir) == 0 or sort_dir[0] is None:
        sort_dir = [default_sort_dir] * len(sort_key)
    elif len(sort_dir) == 1:
        default_sort_dir = sort_dir[0]
        sort_dir *= len(sort_key)

    for key in ['catalog_id', 'catalog_scope_id', 'price_seq_no']:
        if key not in sort_key:
            sort_key.append(key)
            sort_dir.append(default_sort_dir)

    return [sort_key, sort_dir]


def _valid_filters_add(query, ctxt, filters, refine_flg):
    # Add filters
    if 'catalog_id' in filters:
        query = query.filter(
            models.Catalog.catalog_id == filters.get('catalog_id'))

    if 'catalog_name' in filters:
        query = query.filter(
            models.Catalog.catalog_name == filters.get('catalog_name'))

    if 'lifetime' in filters:
        lifetime = datetime.strptime(filters.get('lifetime'),
                                     '%Y-%m-%dT%H:%M:%S.%f')
        query = query.filter(models.Catalog.lifetime_start <= lifetime)
        query = query.filter(models.Catalog.lifetime_end >= lifetime)
        query = query.filter(models.CatalogScope.lifetime_start <= lifetime)
        query = query.filter(models.CatalogScope.lifetime_end >= lifetime)
        query = query.filter(models.Price.lifetime_start <= lifetime)
        query = query.filter(models.Price.lifetime_end >= lifetime)

    query = query.filter(models.Catalog.deleted == False)
    query = query.filter(models.CatalogScope.deleted == False)
    query = query.filter(models.Price.deleted == False)

    tenant_list = []
    if ctxt.is_admin:
        scope = filters.get('scope')
    else:
        if filters.get('scope') == 'Default':
            scope = 'Default'
        else:
            scope = ctxt.tenant

    if refine_flg or scope == 'Default':
        query = query.filter(
            models.CatalogScope.scope == scope)
    else:
        tenant_list = query.filter(
            models.CatalogScope.scope == scope).all()
        query = query.filter(sqlalchemy.or_(
            models.CatalogScope.scope == scope,
            models.CatalogScope.scope == 'Default'))

    return [query, scope, tenant_list]


def _valid_catalog_sort_query(query, original_sort_key=None, sort_dirs=None):
    # Sort_keys model set
    model_list = []
    sort_keys = []
    for set_sort_key in original_sort_key:
        if _VALID_CATALOG_SORTKEY[set_sort_key][0] == 'catalog':
            model_list.append(models.Catalog)
            sort_keys.append(_VALID_CATALOG_SORTKEY[set_sort_key][1])
        elif _VALID_CATALOG_SORTKEY[set_sort_key][0] == 'catalog_scope':
            model_list.append(models.CatalogScope)
            sort_keys.append(_VALID_CATALOG_SORTKEY[set_sort_key][1])
        elif _VALID_CATALOG_SORTKEY[set_sort_key][0] == 'price':
            model_list.append(models.Price)
            sort_keys.append(_VALID_CATALOG_SORTKEY[set_sort_key][1])
        else:
            raise exception.InvalidSortKey()

    # Add sorting
    if sort_dirs and sort_keys:
        for current_sort_key, current_sort_dir, current_model \
                in zip(sort_keys, sort_dirs, model_list):
            sort_dir_func = {
                'asc': sqlalchemy.asc,
                'desc': sqlalchemy.desc
            }[current_sort_dir]

            sort_key_attr = getattr(current_model, current_sort_key)
            query = query.order_by(sort_dir_func(sort_key_attr))

    return query


def valid_catalog_list(ctxt, marker=None, limit=None,
                       sort_key=None, sort_dir=None,
                       refine_flg=None, filters=None):
    """Get all valid catalog that match zero or more filters.
    :param marker: catalog_id and catalog_scope_id and price_seq_no
                after which to start page.
    :param limit: maximum number of catalog to return
    :param sort_key: item name by which results should be sorted.
    :param sort_dir: dict in which results should be sorted (asc, desc).
    :param refine_flg: Whether the flag to merge the default data.
    :param filters: option to search a list.
    """
    session = get_session()

    # Check sort_key and sort_dir.
    sort_key, sort_dir = _valid_sort_key_check(sort_key, sort_dir)

    # Connect the catalog table, catalog_scope talbe and price table.
    query = session.query(models.Catalog, models.CatalogScope, models.Price) \
        .filter(sqlalchemy.and_(
            models.Catalog.catalog_id == models.CatalogScope.catalog_id,
            models.CatalogScope.catalog_id == models.Price.catalog_id,
            models.CatalogScope.scope == models.Price.scope))

    # Add a filter condition.
    query, scope, tenant_list = \
        _valid_filters_add(query, ctxt, filters, refine_flg)

    # Set sort_key and sort_dir.
    query = _valid_catalog_sort_query(query, sort_key, sort_dir)

    catalog_valid_list = []
    marker_exist = False

    valid_list = query.all()
    if valid_list == []:
        marker_exist = True

    for catalog_ref, catalog_scope_ref, price_ref in valid_list:

        # Pattern that does not narrowed the data.
        # To create a valid data from the both public and private data.
        if not refine_flg:

            # Pattern scope is other than 'Default' of filter conditions.
            # and scope of the current data is 'Default'.
            if scope != 'Default' and catalog_scope_ref.scope == 'Default':

                # Check whether a valid private data exists.
                skip_flg = False
                for tenant_catalog, t_scope, t_price in tenant_list:
                    if tenant_catalog.catalog_id == catalog_ref.catalog_id:
                        skip_flg = True
                        break

                # For valid private data exists, public data I skip.
                if skip_flg:
                    continue

        # Paging position determination.
        if marker_exist == False:

            # If the position is not specified,
            # the setting of the flag to True to skip the position.
            # determined from the next time.
            if marker is None:
                marker_exist = True

            # If the location specified there is,
            # it checks whether the data matches the marker.
            # If they match, following the data read is set to True flag.
            # In the case of disagreement, the next data read.
            else:
                if catalog_ref.catalog_id == marker[0] and \
                        catalog_scope_ref.id == marker[1] and \
                        price_ref.seq_no == marker[2]:
                    marker_exist = True

                continue

        # Refill the acquisition value to the return form.
        catalog_valid = {}
        catalog_valid['catalog_id'] = catalog_ref.catalog_id
        catalog_valid['scope'] = catalog_scope_ref.scope
        catalog_valid['catalog_name'] = catalog_ref.catalog_name
        catalog_valid['catalog_lifetime_start'] = catalog_ref.lifetime_start
        catalog_valid['catalog_lifetime_end'] = catalog_ref.lifetime_end
        catalog_valid['catalog_scope_id'] = catalog_scope_ref.id
        catalog_valid['catalog_scope_lifetime_start'] = \
            catalog_scope_ref.lifetime_start
        catalog_valid['catalog_scope_lifetime_end'] = \
            catalog_scope_ref.lifetime_end
        catalog_valid['price_seq_no'] = price_ref.seq_no
        catalog_valid['price'] = str(price_ref.price)
        catalog_valid['price_lifetime_start'] = price_ref.lifetime_start
        catalog_valid['price_lifetime_end'] = price_ref.lifetime_end

        catalog_valid_list.append(catalog_valid)

        # Check limit.
        if len(catalog_valid_list) >= limit:
            break

    if not marker_exist:
        msg = (_("Valid catalog not found"))
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return catalog_valid_list


def price_create(context, **values):
    """Create a price from the values dictionary.
    :param values: Entry price data.
    """
    se = get_session()

    with (se).begin():
        price = models.Price()

        for key in values:
            if key in ('lifetime_start', 'lifetime_end') and values[key]:
                val = datetime.strptime(values[key], '%Y-%m-%dT%H:%M:%S.%f')
            else:
                val = values[key]
            price[key] = val

        price.save(session=se)

    repkey = (price['catalog_id'], price['scope'], price['seq_no'])
    return se.query(models.Price).get(repkey).to_dict()


def price_list(context, catalog_id, marker=None, limit=None,
               sort_key=None, sort_dir=None,
               force_show_deleted=False, filters=None):
    """
    Get all price that match zero or more filters.

    :param marker: id after which to start page
    :param limit: maximum number of images to return
    :param sort_key: image attribute by which results should be sorted
    :param sort_dir: direction in which results should be sorted (asc, desc)
    :param force_show_deleted: view the deleted deterministic
    """
    session = get_session()

    if sort_key is not None and len(sort_key) == 0:
        sort_key = None
    if sort_key is not None and sort_key[0] is None:
        sort_key = None
    sort_key = ['created_at'] if not sort_key else sort_key
    default_sort_dir = 'desc'

    if not sort_dir or len(sort_dir) == 0 \
            or sort_dir[0] is None:
        sort_dir = [default_sort_dir] * len(sort_key)
    elif len(sort_dir) == 1:
        default_sort_dir = sort_dir[0]
        sort_dir *= len(sort_key)

    query = session.query(models.Price)

    query = query.filter(models.Price.catalog_id == catalog_id)

    # non- admin is adding a condition to get
    # the price data of a common price data + own tenant in default
    if not context.is_admin:
        query = query.filter(
            sqlalchemy.or_(models.Price.scope == context.tenant,
                           models.Price.scope == 'Default'))
    else:
        if 'scope' in filters:
            query = query.filter(
                models.Price.scope == filters.get('scope'))

    if 'lifetime' in filters:
        lifetime = filters.get('lifetime')
        query = query.filter(models.Price.lifetime_start <= lifetime)
        query = query.filter(models.Price.lifetime_end >= lifetime)

    marker_obj = None
    if marker is not None:
        marker_obj = \
            _price_get_by_seq_no(context, marker, session=session)

    for key in ['created_at', ]:
        if key not in sort_key:
            sort_key.append(key)
            sort_dir.append(default_sort_dir)

    # filter out deleted if context disallows it
    if not force_show_deleted:
        query = query.filter_by(deleted=False)

    query = db_api_utils.paginate_query(query, models.Price,
                                        limit, sort_key,
                                        marker=marker_obj,
                                        sort_dir=None,
                                        sort_dirs=sort_dir)

    price_refs = query.all()

    price_list = []
    for price_ref in price_refs:

        catalog_price = {}
        catalog_price['catalog_id'] = price_ref.catalog_id
        catalog_price['scope'] = price_ref.scope
        catalog_price['seq_no'] = price_ref.seq_no
        catalog_price['price'] = str(price_ref.price)
        catalog_price['lifetime_start'] = price_ref.lifetime_start
        catalog_price['lifetime_end'] = price_ref.lifetime_end
        catalog_price['created_at'] = price_ref.created_at
        catalog_price['updated_at'] = price_ref.updated_at
        catalog_price['deleted_at'] = price_ref.deleted_at
        catalog_price['deleted'] = price_ref.deleted
        catalog_price['expansions'] = {}
        catalog_price['expansions']['expansion_key1'] = \
            price_ref.expansion_key1
        catalog_price['expansions']['expansion_key2'] = \
            price_ref.expansion_key2
        catalog_price['expansions']['expansion_key3'] = \
            price_ref.expansion_key3
        catalog_price['expansions']['expansion_key4'] = \
            price_ref.expansion_key4
        catalog_price['expansions']['expansion_key5'] = \
            price_ref.expansion_key5
        catalog_price['expansions_text'] = {}
        catalog_price['expansions_text']['expansion_text'] = \
            price_ref.expansion_text

        price_list.append(catalog_price)

    return price_list


def _price_get_by_seq_no(context, seq_no, session=None):
    """Get a price that match zero or more filters.
        :param context: Http context
        :param seq_no: Get the seq_no.
        :param session: Database session.
    """
    session = session or get_session()
    DEFAULT_SCOPE = 'Default'

    try:
        query = session.query(models.Price).filter_by(seq_no=seq_no)

        # non- admin is adding a condition to get
        # the price data of a common price data + own tenant in default
        if not context.is_admin:
            query = query.filter(
                sqlalchemy.or_(models.Price.scope == context.tenant,
                               models.Price.scope == DEFAULT_SCOPE))

        catalog_priceobj = query.one()

    except sa_orm.exc.NoResultFound:
        msg = (_("No catalog_price found"))
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return catalog_priceobj


def _price_get(context, catalog_id, scope, seq_no, session=None):
    session = session or get_session()
    DEFAULT_SCOPE = 'Default'

    try:
        query = session.query(models.Price).filter_by(catalog_id=catalog_id,
                                                      scope=scope,
                                                      seq_no=seq_no)

        # non- admin is adding a condition to get
        # the price data of a common price data + own tenant in default
        if not context.is_admin:
            query = query.filter(
                sqlalchemy.or_(models.Price.scope == context.tenant,
                               models.Price.scope == DEFAULT_SCOPE))

        catalog_priceobj = query.one()

    except sa_orm.exc.NoResultFound:
        msg = (_("No catalog_price found"))
        LOG.debug(msg)
        raise exception.NotFound(msg)

    return catalog_priceobj


def price_get(context, catalog_id, scope, seq_no):
    """
    Get a price that match zero or more filters.
    :param catalog_id: Get the catalog id.
    :param scope: Get the scope.
    :param seq_no: Get the seq_no.
    """
    catalogobj = _price_get(context, catalog_id, scope, seq_no)

    catalogobj['price'] = str(catalogobj['price'])

    return catalogobj.to_dict()


def price_update(context, catalog_id, scope, seq_no, **values):
    """Create a price from the values dictionary.
    :param values: Entry price data.
    """
    se = get_session()

    with (se).begin():
        update_price = _price_get(context, catalog_id, scope, seq_no, se)
        for key in values:
            if key in ('lifetime_start', 'lifetime_end') and values[key]:
                val = datetime.strptime(values[key], '%Y-%m-%dT%H:%M:%S.%f')
            else:
                val = values[key]
            update_price[key] = val
        update_price.save(se)

    priceobj = _price_get(context, catalog_id, scope, seq_no, se)

    if priceobj['price'] or priceobj['price'] == 0:
        priceobj['price'] = str(priceobj['price'])

    return priceobj.to_dict()


def price_delete(ctxt, catalog_id, scope, seq_no):
    """Destroy the price or raise if it does not exist.
        :param ctxt: Http context.
        :param catalog_id: Catalog id.
        :param scope: Scope.
        :param seq_no: Seq no.
    """
    se = get_session()
    with se.begin():
        price = _price_get(ctxt, catalog_id, scope, seq_no, se)
        se.delete(price)
