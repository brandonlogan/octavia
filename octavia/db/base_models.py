# Copyright 2014 Octavia
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo.db.sqlalchemy import models
import sqlalchemy as sa
from sqlalchemy.ext import declarative


class OctaviaBase(models.ModelBase):
    pass


class LookupTableMixin(object):
    """Mixin to add to classes that are lookup tables."""
    name = sa.Column(sa.String(16), primary_key=True, nullable=False)
    description = sa.Column(sa.String(255), nullable=True)


class IdMixin(object):
    """Id mixin, add to subclasses that have a tenant."""
    id = sa.Column(sa.String(36), primary_key=True)
    # TODO(brandon-logan): use uuidutils with oslo-incubator is in tree
    # default=uuidutils.generate_uuid)


class TenantMixin(object):
    """Tenant mixin, add to subclasses that have a tenant."""
    tenant_id = sa.Column(sa.String(36))


BASE = declarative.declarative_base(cls=OctaviaBase)
