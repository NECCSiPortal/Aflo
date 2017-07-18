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

"""
SQLAlchemy models for aflo data
"""

from aflo.db.sqlalchemy import base_models
from oslo_serialization import jsonutils
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.orm import backref, relationship
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator

BASE = declarative_base()


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string"""

    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = jsonutils.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = jsonutils.loads(value)
        return value


class WorkflowPattern(BASE, base_models.AfloBase):
    __tablename__ = 'workflow_pattern'
    __table_args__ = (Index('ix_workflow_pattern_code', 'code'),
                      Index('ix_workflow_pattern_deleted', 'deleted'),)

    id = Column(String(36), primary_key=True)
    code = Column(String(255), nullable=False)
    wf_pattern_contents = Column(JSONEncodedDict(), default={})


class TicketTemplate(BASE, base_models.AfloBase):
    __tablename__ = 'ticket_template'
    __table_args__ = (Index('ix_ticket_template_deleted', 'deleted'),)

    id = Column(String(36), primary_key=True)
    ticket_type = Column(String(64), nullable=False)
    template_contents = Column(JSONEncodedDict(), default={})
    workflow_pattern_id = Column(String(36),
                                 ForeignKey('workflow_pattern.id'),
                                 nullable=False)
    workflow_pattern = relationship(WorkflowPattern,
                                    backref=backref('workflow_pattern_id'))


class Ticket(BASE, base_models.AfloBase):
    __tablename__ = 'ticket'
    __table_args__ = (Index('ix_ticket_deleted', 'deleted'),)

    id = Column(String(36), primary_key=True)
    ticket_template_id = Column(String(36),
                                ForeignKey('ticket_template.id'),
                                nullable=False)
    ticket_template = relationship(TicketTemplate,
                                   backref=backref('ticket_template_id'))
    ticket_type = Column(String(64), nullable=False)
    target_id = Column(JSONEncodedDict(), default={})
    tenant_id = Column(String(36), nullable=False)
    tenant_name = Column(String(255))
    owner_id = Column(String(255))
    owner_name = Column(String(255))
    owner_at = Column(DateTime())
    ticket_detail = Column(JSONEncodedDict(), default={})
    action_detail = Column(JSONEncodedDict(), default={})


class Workflow(BASE, base_models.AfloBase):
    __tablename__ = 'workflow'
    __table_args__ = (Index('ix_workflow_deleted', 'deleted'),)

    id = Column(String(36), primary_key=True)
    ticket_id = Column(String(36), ForeignKey('ticket.id'), nullable=False)
    ticket = relationship(Ticket, backref=backref('ticket_id'))
    status = Column(Integer(), nullable=False)
    status_code = Column(String(64), nullable=False)
    status_detail = Column(JSONEncodedDict(), default={})
    target_role = Column(String(512))
    confirmer_id = Column(String(255))
    confirmer_name = Column(String(255))
    confirmed_at = Column(DateTime())
    additional_data = Column(JSONEncodedDict(), default={})


class Contract(BASE, base_models.AfloBase, base_models.ExpansionMixin):
    """Contarct model."""
    __tablename__ = 'contract'
    __table_args__ = (Index('ix_contract_deleted', 'deleted'),)

    contract_id = Column(String(64), primary_key=True)
    region_id = Column(String(255))
    project_id = Column(String(64))
    project_name = Column(String(64))
    catalog_id = Column(String(64))
    catalog_name = Column(String(128))
    num = Column(Integer())
    parent_ticket_template_id = Column(String(64))
    ticket_template_id = Column(String(64))
    parent_ticket_template_name = Column(Text())
    ticket_template_name = Column(Text())
    parent_application_kinds_name = Column(Text())
    application_kinds_name = Column(Text())
    cancel_application_id = Column(String(64))
    application_id = Column(String(64))
    application_name = Column(String(64))
    application_date = Column(DateTime())
    parent_contract_id = Column(String(64))
    lifetime_start = Column(DateTime())
    lifetime_end = Column(DateTime())

    def to_dict(self):
        """Change contract model to dict."""
        d = {}
        for key in Contract.__table__.columns._data.keys():
            d[key] = getattr(self, key, None)

        d['expansions'] = {}
        d['expansions_text'] = {}

        for i in range(5):
            key = 'expansion_key%d' % (i + 1)
            d['expansions'][key] = d.pop(key) if key in d else None

        key = 'expansion_text'
        d['expansions_text'][key] = d.pop(key) if key in d else None

        return d


class Goods(BASE, base_models.AfloBase):
    __tablename__ = 'goods'
    __table_args__ = (Index('ix_goods_deleted', 'deleted'),)

    goods_id = Column(String(64), primary_key=True)
    region_id = Column(String(255))
    goods_name = Column(String(128))
    expansion_key1 = Column(String(255))
    expansion_key2 = Column(String(255))
    expansion_key3 = Column(String(255))
    expansion_key4 = Column(String(255))
    expansion_key5 = Column(String(255))
    expansion_text = Column(Text(4000))

    def to_dict(self):
        """Change contract model to dict."""
        d = {}
        for key in Goods.__table__.columns._data.keys():
            d[key] = getattr(self, key, None)

        d['expansions'] = {}
        d['expansions_text'] = {}

        for i in range(5):
            key = 'expansion_key%d' % (i + 1)
            d['expansions'][key] = d.pop(key) if key in d else None

        key = 'expansion_text'
        d['expansions_text'][key] = d.pop(key) if key in d else None

        return d


class Catalog(BASE, base_models.AfloBase):
    __tablename__ = 'catalog'
    __table_args__ = (Index('ix_catalog_deleted', 'deleted'),)

    catalog_id = Column(String(64), primary_key=True)
    region_id = Column(String(255))
    catalog_name = Column(String(128))
    lifetime_start = Column(DateTime())
    lifetime_end = Column(DateTime())
    expansion_key1 = Column(String(255))
    expansion_key2 = Column(String(255))
    expansion_key3 = Column(String(255))
    expansion_key4 = Column(String(255))
    expansion_key5 = Column(String(255))
    expansion_text = Column(Text(4000))

    def to_dict(self):
        """Change contract model to dict."""
        d = {}
        for key in Catalog.__table__.columns._data.keys():
            d[key] = getattr(self, key, None)

        d['expansions'] = {}
        d['expansions_text'] = {}

        for i in range(5):
            key = 'expansion_key%d' % (i + 1)
            d['expansions'][key] = d.pop(key) if key in d else None

        key = 'expansion_text'
        d['expansions_text'][key] = d.pop(key) if key in d else None

        return d


class CatalogContents(BASE, base_models.AfloBase):
    __tablename__ = 'catalog_contents'
    __table_args__ = (Index('ix_catalog_contents_deleted', 'deleted'),)

    catalog_id = Column(String(64), primary_key=True)
    seq_no = Column(String(64), primary_key=True)
    goods_id = Column(String(64))
    goods_num = Column(Integer)
    expansion_key1 = Column(String(255))
    expansion_key2 = Column(String(255))
    expansion_key3 = Column(String(255))
    expansion_key4 = Column(String(255))
    expansion_key5 = Column(String(255))
    expansion_text = Column(Text(4000))

    def to_dict(self):
        """Change contract model to dict."""
        d = {}
        for key in CatalogContents.__table__.columns._data.keys():
            d[key] = getattr(self, key, None)

        d['expansions'] = {}
        d['expansions_text'] = {}

        for i in range(5):
            key = 'expansion_key%d' % (i + 1)
            d['expansions'][key] = d.pop(key) if key in d else None

        key = 'expansion_text'
        d['expansions_text'][key] = d.pop(key) if key in d else None

        return d


class CatalogScope(BASE, base_models.AfloBase):
    """Catalog scope model."""
    __tablename__ = 'catalog_scope'
    __table_args__ = (Index('ix_catalog_scope_deleted', 'deleted'),)

    id = Column(String(64), primary_key=True)
    catalog_id = Column(String(64), primary_key=True)
    scope = Column(String(64), primary_key=True)
    lifetime_start = Column(DateTime())
    lifetime_end = Column(DateTime())
    expansion_key1 = Column(String(255))
    expansion_key2 = Column(String(255))
    expansion_key3 = Column(String(255))
    expansion_key4 = Column(String(255))
    expansion_key5 = Column(String(255))
    expansion_text = Column(Text(4000))

    def to_dict(self):
        """Change catalog scope model to dict."""
        d = {}
        for key in CatalogScope.__table__.columns._data.keys():
            d[key] = getattr(self, key, None)

        d['expansions'] = {}
        d['expansions_text'] = {}

        for i in range(5):
            key = 'expansion_key%d' % (i + 1)
            d['expansions'][key] = d.pop(key) if key in d else None

        key = 'expansion_text'
        d['expansions_text'][key] = d.pop(key) if key in d else None

        return d


class Price(BASE, base_models.AfloBase):
    __tablename__ = 'price'
    __table_args__ = (Index('ix_price_deleted', 'deleted'),)

    catalog_id = Column(String(64), primary_key=True)
    scope = Column(String(64), primary_key=True)
    seq_no = Column(String(64), primary_key=True)
    price = Column(Numeric(12, 3), nullable=False)
    lifetime_start = Column(DateTime())
    lifetime_end = Column(DateTime())
    expansion_key1 = Column(String(255))
    expansion_key2 = Column(String(255))
    expansion_key3 = Column(String(255))
    expansion_key4 = Column(String(255))
    expansion_key5 = Column(String(255))
    expansion_text = Column(Text(4000))

    def to_dict(self):
        """Change contract model to dict."""
        d = {}
        for key in Price.__table__.columns._data.keys():
            d[key] = getattr(self, key, None)

        d['expansions'] = {}
        d['expansions_text'] = {}

        for i in range(5):
            key = 'expansion_key%d' % (i + 1)
            d['expansions'][key] = d.pop(key) if key in d else None

        key = 'expansion_text'
        d['expansions_text'][key] = d.pop(key) if key in d else None

        return d


def register_models(engine):
    """Create database tables for all models with the given engine."""
    BASE.metadata.create_all(engine)


def unregister_models(engine):
    """Drop database tables for all models with the given engine."""
    BASE.metadata.drop_all(engine)
