#    Copyright 2014 Rackspace
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
from sqlalchemy import orm
from sqlalchemy.orm import validates

from octavia.common import data_models
from octavia.db import base_models


load_balancer_amphora_table = sa.Table(
    'load_balancer_amphora', base_models.BASE.metadata,
    sa.Column('amphora_id', sa.String(36), sa.ForeignKey(
        "amphora.id", name="fk_load_balancer_amphora_amphora_id")),
    sa.Column('load_balancer_id', sa.String(36), sa.ForeignKey(
        "load_balancer.id",
        name="fk_load_balancer_amphora_load_balancer_id"))
)


class ProvisioningStatus(base_models.BASE, base_models.LookupTableMixin):

    __tablename__ = "provisioning_status"


class OperatingStatus(base_models.BASE, base_models.LookupTableMixin):

    __tablename__ = "operating_status"


class Protocol(base_models.BASE, base_models.LookupTableMixin):

    __tablename__ = "protocol"


class Algorithm(base_models.BASE, base_models.LookupTableMixin):

    __tablename__ = "algorithm"


class SessionPersistenceType(base_models.BASE, base_models.LookupTableMixin):

    __tablename__ = "session_persistence_type"


class HealthMonitorType(base_models.BASE, base_models.LookupTableMixin):

    __tablename__ = "health_monitor_type"


class SessionPersistence(base_models.BASE):

    __data_model__ = data_models.SessionPersistence

    __tablename__ = "session_persistence"

    pool_id = sa.Column(
        sa.String(36),
        sa.ForeignKey("pool.id", name="fk_session_persistence_pool_id"),
        nullable=False,
        primary_key=True)
    type = sa.Column(
        sa.String(36),
        sa.ForeignKey(
            "session_persistence_type.name",
            name="fk_session_persistence_session_persistence_type_name"),
        nullable=False)
    cookie_name = sa.Column(sa.String(255), nullable=True)
    pool = orm.relationship("Pool", uselist=False,
                            backref=orm.backref("session_persistence",
                                                uselist=False))


class ListenerStatistics(base_models.BASE):

    __data_model__ = data_models.ListenerStatistics

    __tablename__ = "listener_statistics"

    listener_id = sa.Column(
        sa.String(36),
        sa.ForeignKey("listener.id",
                      name="fk_listener_statistics_listener_id"),
        primary_key=True,
        nullable=False)
    bytes_in = sa.Column(sa.BigInteger, nullable=False)
    bytes_out = sa.Column(sa.BigInteger, nullable=False)
    active_connections = sa.Column(sa.Integer, nullable=False)
    total_connections = sa.Column(sa.BigInteger, nullable=False)
    listener = orm.relationship("Listener", uselist=False,
                                backref=orm.backref("stats", uselist=False))

    @validates('bytes_in', 'bytes_out',
               'active_connections', 'total_connections')
    def validate_non_negative_int(self, key, value):
        if value < 0:
            data = {'key': key, 'value': value}
            raise ValueError(data)
            # TODO(trevor-vardeman): Repair this functionality after Openstack
            # Common is in
            # raise ValueError(_('The %(key)s field can not have '
            #                   'negative value. '
            #                   'Current value is %(value)d.') % data)
        return value


class Member(base_models.BASE, base_models.IdMixin, base_models.TenantMixin):

    __data_model__ = data_models.Member

    __tablename__ = "member"
    __table_args__ = (
        sa.UniqueConstraint('pool_id', 'address', 'protocol_port',
                            name='uq_member_pool_id_address_protocol_port'),
    )

    pool_id = sa.Column(
        sa.String(36),
        sa.ForeignKey("pool.id", name="fk_member_pool_id"),
        nullable=False)
    subnet_id = sa.Column(sa.String(36), nullable=True)
    address = sa.Column(sa.String(64), nullable=False)
    protocol_port = sa.Column(sa.Integer, nullable=False)
    weight = sa.Column(sa.Integer, nullable=True)
    operating_status = sa.Column(
        sa.String(16),
        sa.ForeignKey("operating_status.name",
                      name="fk_member_operating_status_name"),
        nullable=False)
    enabled = sa.Column(sa.Boolean(), nullable=False)
    pool = orm.relationship("Pool", backref="members")


class HealthMonitor(base_models.BASE):

    __data_model__ = data_models.HealthMonitor

    __tablename__ = "health_monitor"

    pool_id = sa.Column(
        sa.String(36),
        sa.ForeignKey("pool.id", name="fk_health_monitor_pool_id"),
        nullable=False,
        primary_key=True)
    type = sa.Column(
        sa.String(36),
        sa.ForeignKey("health_monitor_type.name",
                      name="fk_health_monitor_health_monitor_type_name"),
        nullable=False)
    delay = sa.Column(sa.Integer, nullable=False)
    timeout = sa.Column(sa.Integer, nullable=False)
    fall_threshold = sa.Column(sa.Integer, nullable=False)
    rise_threshold = sa.Column(sa.Integer, nullable=False)
    http_method = sa.Column(sa.String(16), nullable=True)
    url_path = sa.Column(sa.String(255), nullable=True)
    expected_codes = sa.Column(sa.String(64), nullable=True)
    enabled = sa.Column(sa.Boolean, nullable=False)


class Pool(base_models.BASE, base_models.IdMixin, base_models.TenantMixin):

    __data_model__ = data_models.Pool

    __tablename__ = "pool"
    __table_args__ = (
        sa.UniqueConstraint('health_monitor_id',
                            name='uq_pool_health_monitor_id'),
    )

    name = sa.Column(sa.String(255), nullable=True)
    description = sa.Column(sa.String(255), nullable=True)
    protocol = sa.Column(
        sa.String(16),
        sa.ForeignKey("protocol.name", name="fk_pool_protocol_name"),
        nullable=False)
    lb_algorithm = sa.Column(
        sa.String(16),
        sa.ForeignKey("algorithm.name", name="fk_pool_algorithm_name"),
        nullable=False)
    health_monitor_id = sa.Column(
        sa.String(36),
        sa.ForeignKey("health_monitor.id", name="fk_pool_health_monitor_id"),
        unique=True,
        nullable=True)
    operating_status = sa.Column(
        sa.String(16),
        sa.ForeignKey("operating_status.name",
                      name="fk_pool_operating_status_name"),
        nullable=False)
    enabled = sa.Column(sa.Boolean, nullable=False)
    health_monitor = orm.relationship("HealthMonitor", uselist=False,
                                      backref=orm.backref("pool",
                                                          uselist=False))


class LoadBalancer(base_models.BASE, base_models.IdMixin,
                   base_models.TenantMixin):

    __data_model__ = data_models.LoadBalancer

    __tablename__ = "load_balancer"

    name = sa.Column(sa.String(255), nullable=True)
    description = sa.Column(sa.String(255), nullable=True)
    vip_port_id = sa.Column(sa.String(36), nullable=True)
    vip_subnet_id = sa.Column(sa.String(36), nullable=True)
    vip_floating_ip_id = sa.Column(sa.String(36), nullable=True)
    vip_floating_ip_network_id = sa.Column(sa.String(36), nullable=True)
    vip_address = sa.Column(sa.String(36), nullable=True)
    provisioning_status = sa.Column(
        sa.String(16),
        sa.ForeignKey("provisioning_status.name",
                      name="fk_load_balancer_provisioning_status_name"),
        nullable=False)
    operating_status = sa.Column(
        sa.String(16),
        sa.ForeignKey("operating_status.name",
                      name="fk_load_balancer_operating_status_name"),
        nullable=False)
    enabled = sa.Column(sa.Boolean, nullable=False)
    amphorae = orm.relationship("Amorpha", uselist=True,
                                secondary=load_balancer_amphora_table,
                                backref=orm.backref("load_balancers",
                                                    uselist=True))


class Listener(base_models.BASE, base_models.IdMixin, base_models.TenantMixin):

    __data_model__ = data_models.Listener

    __tablename__ = "listener"
    __table_args__ = (
        sa.UniqueConstraint('load_balancer_id', 'protocol_port',
                            name='uq_listener_load_balancer_id_protocol_port'),
        sa.UniqueConstraint('default_pool_id',
                            name='uq_listener_default_pool_id')
    )

    name = sa.Column(sa.String(255), nullable=True)
    description = sa.Column(sa.String(255), nullable=True)
    protocol = sa.Column(
        sa.String(16),
        sa.ForeignKey("protocol.name", name="fk_listener_protocol_name"),
        nullable=False)
    protocol_port = sa.Column(sa.Integer(), nullable=False)
    connection_limit = sa.Column(sa.Integer, nullable=True)
    load_balancer_id = sa.Column(
        sa.String(36),
        sa.ForeignKey("load_balancer.id", name="fk_listener_load_balancer_id"),
        nullable=True)
    default_tls_container_id = sa.Column(sa.String(36), nullable=True)
    default_pool_id = sa.Column(
        sa.String(36),
        sa.ForeignKey("pool.id", name="fk_listener_pool_id"),
        unique=True, nullable=True)
    provisioning_status = sa.Column(
        sa.String(16),
        sa.ForeignKey("provisioning_status.name",
                      name="fk_listener_provisioning_status_name"),
        nullable=False)
    operating_status = sa.Column(
        sa.String(16),
        sa.ForeignKey("operating_status.name",
                      name="fk_listener_operating_status_name"),
        nullable=False)
    enabled = sa.Column(sa.Boolean(), nullable=False)
    load_balancer = orm.relationship("LoadBalancer", backref="listeners")
    default_pool = orm.relationship("Pool", uselist=False,
                                    backref=orm.backref("listener",
                                                        uselist=False))


class SNI(base_models.BASE):

    __data_model__ = data_models.SNI

    __tablename__ = "sni"
    __table_args__ = (
        sa.PrimaryKeyConstraint('listener_id', 'tls_container_id'),
    )

    listener_id = sa.Column(
        sa.String(36),
        sa.ForeignKey("listener.id", name="fk_sni_listener_id"),
        nullable=False)
    tls_container_id = sa.Column(sa.String(36), nullable=False)
    position = sa.Column(sa.Integer(), nullable=True)
    listener = orm.relationship("Listener", uselist=False,
                                backref="sni_containers")


class Amphora(base_models.BASE):

    __data_model__ = data_models.Container

    __tablename__ = "amphora"

    id = sa.Column(sa.String(36), nullable=False, primary_key=True,
                   autoincrement=False)
    host_id = sa.Column(sa.String(36), nullable=False)
    status = sa.Column(
        sa.String(36),
        sa.ForeignKey("provisioning_status.name",
                      name="fk_amphora_provisioning_status_name"))