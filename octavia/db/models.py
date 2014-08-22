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

import sqlalchemy as sa
from sqlalchemy.ext import declarative
from sqlalchemy.orm import validates

from octavia.db import base_models


class SessionPersistence(base_models.BASE):

    @declarative.declared_attr
    def __tablename__(cls):
        return "session_persistence"
    pool_id = sa.Column(sa.String(36), sa.ForeignKey("pool.id"),
                        nullable=False, primary_key=True)
    type = sa.Column(sa.String(36), sa.ForeignKey("session_persistence_type"),
                     nullable=False)
    cookie_name = sa.Column(sa.String(1024), nullable=True)
    description = sa.Column(sa.String(255), nullable=True)


class ListenerStatistics(base_models.BASE):
    """Represents load balancer statistics."""

    @declarative.declared_attr
    def __tablename__(cls):
        return "listener_statistics"

    listener_id = sa.Column(sa.String(36), sa.ForeignKey("listener.id"),
                            primary_key=True, nullable=False)
    bytes_in = sa.Column(sa.BigInteger, nullable=False)
    bytes_out = sa.Column(sa.BigInteger, nullable=False)
    active_connections = sa.Column(sa.BigInteger, nullable=False)
    total_connections = sa.Column(sa.BigInteger, nullable=False)

    @validates('bytes_in', 'bytes_out',
               'active_connections', 'total_connections')
    def validate_non_negative_int(self, key, value):
        if value < 0:
            data = {'key': key, 'value': value}
            raise ValueError(data)
            #TODO: Repair this functionality after Openstack Common is in
            #raise ValueError(_('The %(key)s field can not have '
            #                   'negative value. '
            #                   'Current value is %(value)d.') % data)
        return value


class Member(base_models.BASE, base_models.IdMixin, base_models.TenantMixin):
    """Represents a  neutron load balancer member."""

    @declarative.declared_attr
    def __tablename__(cls):
        return "member"

    __table_args__ = (
        sa.UniqueConstraint('pool_id', 'address', 'protocol_port')
    )

    tenant_id = sa.Column(sa.String(255), nullable=True)
    id = sa.Column(sa.String(36), nullable=False, primary_key=True)
    pool_id = sa.Column(sa.String(36), sa.ForeignKey("pool.id"),
                        nullable=False)
    subnet_id = sa.Column(sa.String(36), nullable=True)
    address = sa.Column(sa.String(64), nullable=False)
    protocol_port = sa.Column(sa.Integer, nullable=False)
    weight = sa.Column(sa.Integer, nullable=True)
    operating_status = sa.Column(sa.String(16),
                                 sa.ForeignKey("operating_status.name"),
                                 nullable=False)
    enabled = sa.Column(sa.Boolean(), nullable=False)


class HealthMonitor(base_models.BASE, base_models.IdMixin,
                      base_models.TenantMixin):
    """Represents a  neutron load balancer healthmonitor."""

    @declarative.declared_attr
    def __tablename__(cls):
        return "health_monitor"

    tenant_id = sa.Column(sa.String(255), nullable=True)
    id = sa.Column(sa.String(36), nullable=False, primary_key=True)
    type = sa.Column(sa.String(36), sa.ForeignKey("health_monitor_type.name"),
                     nullable=False)
    delay = sa.Column(sa.Integer, nullable=False)
    timeout = sa.Column(sa.Integer, nullable=False)
    max_retries = sa.Column(sa.Integer, nullable=False)
    http_method = sa.Column(sa.String(16), nullable=True)
    url_path = sa.Column(sa.String(255), nullable=True)
    expected_codes = sa.Column(sa.String(64), nullable=True)
    enabled = sa.Column(sa.Boolean, nullable=False)


class Pool(base_models.BASE, base_models.IdMixin, base_models.TenantMixin):
    """Represents a  neutron load balancer pool."""

    @declarative.declared_attr
    def __tablename__(cls):
        return "pool"

    tenant_id = sa.Column(sa.String(255), nullable=True)
    id = sa.Column(sa.String(36), nullable=False, primary_key=True)
    name = sa.Column(sa.String(255), nullable=True)
    description = sa.Column(sa.String(255), nullable=True)
    protocol = sa.Column(sa.String(16), sa.ForeignKey("protocol.name"),
                         nullable=False)
    lb_algorithm = sa.Column(sa.String(16), sa.ForeignKey("algorithm.name"),
                             nullable=False)
    healthmonitor_id = sa.Column(sa.String(36),
                                 sa.ForeignKey("health_monitor.id"),
                                 unique=True,
                                 nullable=True)
    operating_status = sa.Column(sa.String(16),
                                 sa.ForeignKey("operating_status.name"),
                                 nullable=False)
    enabled = sa.Column(sa.Boolean, nullable=False)


class LoadBalancer(base_models.BASE, base_models.IdMixin,
                   base_models.TenantMixin):
    """Represents a  neutron load balancer."""

    @declarative.declared_attr
    def __tablename__(cls):
        return "load_balancer"

    tenant_id = sa.Column(sa.String(255), nullable=True)
    id = sa.Column(sa.String(36), nullable=True, primary_key=True)
    name = sa.Column(sa.String(255), nullable=True)
    description = sa.Column(sa.String(255), nullable=True)
    vip_port_id = sa.Column(sa.String(36), nullable=True)
    vip_subnet_id = sa.Column(sa.String(36), nullable=False)
    vip_address = sa.Column(sa.String(36), nullable=True)
    provisioning_status = sa.Column(sa.String(16),
                                    sa.ForeignKey("provisioning_status.name"),
                                    nullable=False)
    enabled = sa.Column(sa.Boolean, nullable=False)
    host_id = sa.Column(sa.String(36), nullable=True)
    colocation_hint = sa.Column(sa.String(36), nullable=True)
    apolocation_hint = sa.Column(sa.String(36), nullable=True)


class Listener(base_models.BASE, base_models.IdMixin, base_models.TenantMixin):
    """Represents a  neutron listener."""

    @declarative.declared_attr
    def __tablename__(cls):
        return "listener"

    __table_args__ = (
        sa.UniqueConstraint('load_balancer_id', 'protocol_port')
    )

    tenant_id = sa.Column(sa.String(255), nullable=True)
    id = sa.Column(sa.String(36), nullable=False, primary_key=True)
    name = sa.Column(sa.String(255), nullable=True)
    description = sa.Column(sa.String(255), nullable=True)
    protocol = sa.Column(sa.String(16), sa.ForeignKey("protocol.name"),
                         nullable=False)
    protocol_port = sa.Column(sa.Integer(), nullable=False)
    connection_limit = sa.Column(sa.Integer, nullable=True)
    load_balancer_id = sa.Column(sa.String(36),
                                 sa.ForeignKey("load_balancer.id"),
                                 nullable=True)
    default_tls_container_id = sa.Column(sa.String(36), nullable=True)
    default_pool_id = sa.Column(sa.String(36), sa.ForeignKey("pool.id"),
                                unique=True, nullable=True)
    provisioning_status = sa.Column(sa.String(16),
                                    sa.ForeignKey("provisioning_status.name"),
                                    nullable=False)
    operating_status = sa.Column(sa.String(16),
                                 sa.ForeignKey("operating_status.name"),
                                 nullable=False)
    enabled = sa.Column(sa.Boolean(), nullable=False)