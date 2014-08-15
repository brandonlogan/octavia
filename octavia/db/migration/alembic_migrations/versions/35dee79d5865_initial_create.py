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

"""initial_create

Revision ID: 35dee79d5865
Revises: None
Create Date: 2014-08-15 11:01:14.897223

"""

# revision identifiers, used by Alembic.
revision = '35dee79d5865'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy import sql


def upgrade():
    # Create lookup tables
    op.create_table(
        u'health_monitor_type',
        sa.Column(u'name', sa.String(30), primary_key=True),
        sa.Column(u'description', sa.String(255), nullable=True)
    )

    # Create temporary table for table data seeding
    insert_table = sql.table(
        u'health_monitor_type',
        sql.column(u'name', sa.String),
        sql.column(u'description', sa.String)
    )

    op.bulk_insert(
        insert_table,
        [
            {'name': 'HTTP'},
            {'name': 'HTTPS'},
            {'name': 'TCP'}
        ]
    )

    op.create_table(
        u'protocol',
        sa.Column(u'name', sa.String(30), primary_key=True),
        sa.Column(u'description', sa.String(255), nullable=True)
    )

    insert_table = sql.table(
        u'protocol',
        sql.column(u'name', sa.String),
        sql.column(u'description', sa.String)
    )

    op.bulk_insert(
        insert_table,
        [
            {'name': 'HTTP'},
            {'name': 'HTTPS'},
            {'name': 'TERMINATED_HTTPS'},
            {'name': 'TCP'}
        ]
    )

    op.create_table(
        u'algorithm',
        sa.Column(u'name', sa.String(30), primary_key=True),
        sa.Column(u'description', sa.String(255), nullable=True)
    )

    insert_table = sql.table(
        u'algorithm',
        sql.column(u'name', sa.String),
        sql.column(u'description', sa.String)
    )

    op.bulk_insert(
        insert_table,
        [
            {'name': 'ROUND_ROBIN'},
            {'name': 'LEAST_CONNECTIONS'},
            {'name': 'SOURCE_IP'}
        ]
    )

    op.create_table(
        u'session_persistence_type',
        sa.Column(u'name', sa.String(30), primary_key=True),
        sa.Column(u'description', sa.String(255), nullable=True)
    )

    insert_table = sql.table(
        u'session_persistence_type',
        sql.column(u'name', sa.String),
        sql.column(u'description', sa.String)
    )

    op.bulk_insert(
        insert_table,
        [
            {'name': 'SOURCE_IP'},
            {'name': 'HTTP_COOKIE'},
            {'name': 'APP_COOKIE'}
        ]
    )

    op.create_table(
        u'provisioning_status',
        sa.Column(u'name', sa.String(30), primary_key=True),
        sa.Column(u'description', sa.String(255), nullable=True)
    )

    insert_table = sql.table(
        u'provisioning_status',
        sql.column(u'name', sa.String),
        sql.column(u'description', sa.String)
    )

    op.bulk_insert(
        insert_table,
        [
            {'name': 'ACTIVE'},
            {'name': 'PENDING_CREATE'},
            {'name': 'PENDING_UPDATE'},
            {'name': 'PENDING_DELETE'},
            {'name': 'DELETED'}
        ]
    )

    op.create_table(
        u'operating_status',
        sa.Column(u'name', sa.String(30), primary_key=True),
        sa.Column(u'description', sa.String(255), nullable=True)
    )

    insert_table = sql.table(
        u'protocol',
        sql.column(u'name', sa.String),
        sql.column(u'description', sa.String)
    )

    op.bulk_insert(
        insert_table,
        [
            {'name': 'ONLINE'},
            {'name': 'OFFLINE'},
            {'name': 'DEGRADED'}
        ]
    )

    op.create_table(
        u'health_monitor',
        sa.Column(u'tenant_id', sa.String(255), nullable=True),
        sa.Column(u'id', sa.String(36), nullable=False, primary_key=True),
        sa.Column(u'type', sa.String(36), nullable=False),
        sa.Column(u'delay', sa.Integer(), nullable=False),
        sa.Column(u'timeout', sa.Integer(), nullable=False),
        sa.Column(u'max_retries', sa.Integer(), nullable=False),
        sa.Column(u'http_method', sa.String(16), nullable=True),
        sa.Column(u'url_path', sa.String(255), nullable=True),
        sa.Column(u'expected_codes', sa.String(64), nullable=True),
        sa.Column(u'enabled', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint([u'type'],
                                [u'health_monitor_type.name']),
        sa.PrimaryKeyConstraint(u'id')
    )

    op.create_table(
        u'pool',
        sa.Column(u'tenant_id', sa.String(255), nullable=True),
        sa.Column(u'id', sa.String(36), nullable=False),
        sa.Column(u'name', sa.String(255), nullable=True),
        sa.Column(u'description', sa.String(255), nullable=True),
        sa.Column(u'protocol', sa.String(16), nullable=False),
        sa.Column(u'lb_algorithm', sa.String(16), nullable=False),
        sa.Column(u'health_monitor_id', sa.String(36), nullable=True),
        sa.Column(u'operating_status', sa.String(16), nullable=False),
        sa.Column(u'enabled', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint(u'id'),
        sa.UniqueConstraint(u'health_monitor_id'),
        sa.ForeignKeyConstraint([u'protocol'],
                                [u'protocol.name']),
        sa.ForeignKeyConstraint([u'lb_algorithm'],
                                [u'algorithm.name']),
        sa.ForeignKeyConstraint([u'operating_status'],
                                [u'operating_status.name']),
        sa.ForeignKeyConstraint([u'health_monitor_id'],
                                [u'health_monitor.id'])
    )

    op.create_table(
        u'session_persistence',
        sa.Column(u'pool_id', sa.String(36), nullable=False),
        sa.Column(u'type', sa.String(16), nullable=False),
        sa.Column(u'cookie_name', sa.String(1024), nullable=True),
        sa.ForeignKeyConstraint([u'type'],
                                [u'session_persistence_type.name']),
        sa.ForeignKeyConstraint([u'pool_id'], [u'pool.id']),
        sa.PrimaryKeyConstraint(u'pool_id')
    )

    op.create_table(
        u'member',
        sa.Column(u'tenant_id', sa.String(255), nullable=True),
        sa.Column(u'id', sa.String(36), nullable=False),
        sa.Column(u'pool_id', sa.String(36), nullable=False),
        sa.Column(u'subnet_id', sa.String(36), nullable=True),
        sa.Column(u'address', sa.String(64), nullable=False),
        sa.Column(u'protocol_port', sa.Integer(), nullable=False),
        sa.Column(u'weight', sa.Integer(), nullable=True),
        sa.Column(u'operating_status', sa.String(16), nullable=False),
        sa.Column(u'enabled', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint(u'id'),
        sa.ForeignKeyConstraint([u'pool_id'], [u'pool.id']),
        sa.ForeignKeyConstraint([u'operating_status'],
                                [u'operating_status.name']),
        sa.UniqueConstraint(u'pool_id', u'address', u'protocol_port')
    )

    op.create_table(
        u'load_balancer',
        sa.Column(u'tenant_id', sa.String(255), nullable=True),
        sa.Column(u'id', sa.String(36), nullable=False),
        sa.Column(u'name', sa.String(255), nullable=True),
        sa.Column(u'description', sa.String(255), nullable=True),
        sa.Column(u'vip_port_id', sa.String(36), nullable=True),
        sa.Column(u'vip_subnet_id', sa.String(36), nullable=False),
        sa.Column(u'vip_address', sa.String(36), nullable=True),
        sa.Column(u'provisioning_status', sa.String(16), nullable=False),
        sa.ForeignKeyConstraint([u'provisioning_status'],
                                [u'provisioning_status.name']),
        sa.Column(u'enabled', sa.Boolean(), nullable=False),
        sa.Column(u'host_id', sa.String(36), nullable=True),
        sa.Column(u'colocation_hint', sa.String(36), nullable=True),
        sa.Column(u'apolocation_hint', sa.String(36), nullable=True),
        sa.PrimaryKeyConstraint(u'id')
    )

    op.create_table(
        u'listener',
        sa.Column(u'tenant_id', sa.String(255), nullable=True),
        sa.Column(u'id', sa.String(36), nullable=False),
        sa.Column(u'name', sa.String(255), nullable=True),
        sa.Column(u'description', sa.String(255), nullable=True),
        sa.Column(u'protocol', sa.String(16), nullable=False),
        sa.Column(u'protocol_port', sa.Integer(), nullable=False),
        sa.Column(u'connection_limit', sa.Integer(), nullable=True),
        sa.Column(u'load_balancer_id', sa.String(36), nullable=True),
        sa.Column(u'default_tls_container_id', sa.String(36), nullable=True),
        sa.Column(u'pool_id', sa.String(36), nullable=True),
        sa.Column(u'operating_status', sa.String(16), nullable=False),
        sa.Column(u'enabled', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint([u'load_balancer_id'], [u'load_balancer.id']),
        sa.ForeignKeyConstraint([u'pool_id'], [u'pool.id']),
        sa.ForeignKeyConstraint([u'protocol'], [u'protocol.name']),
        sa.ForeignKeyConstraint([u'operating_status'],
                                [u'operating_status.name']),
        sa.UniqueConstraint(u'pool_id'),
        sa.UniqueConstraint(u'load_balancer_id', u'protocol_port'),
        sa.PrimaryKeyConstraint(u'id')
    )

    op.create_table(
        u'sni',
        sa.Column(u'listener_id', sa.String(36), nullable=False),
        sa.Column(u'tls_container_id', sa.String(36), nullable=False),
        sa.Column(u'position', sa.Integer, nullable=True),
        sa.ForeignKeyConstraint([u'listener_id'], [u'listener.id']),
        sa.PrimaryKeyConstraint(u'listener_id', u'tls_container_id')
    )

    op.create_table(
        u'listener_statistics',
        sa.Column(u'listener_id', sa.String(36), nullable=False),
        sa.Column(u'bytes_in', sa.BigInteger(), nullable=False),
        sa.Column(u'bytes_out', sa.BigInteger(), nullable=False),
        sa.Column(u'active_connections', sa.BigInteger(), nullable=False),
        sa.Column(u'total_connections', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint(u'listener_id'),
        sa.ForeignKeyConstraint([u'listener_id'], [u'listener.id'])
    )


def downgrade():
    op.drop_table(u'listener_statistics')
    op.drop_table(u'sni')
    op.drop_table(u'listener')
    op.drop_table(u'load_balancer')
    op.drop_table(u'member')
    op.drop_table(u'session_persistence')
    op.drop_table(u'pool')
    op.drop_table(u'health_monitor')
    op.drop_table(u'provisioning_status')
    op.drop_table(u'operating_status')
    op.drop_table(u'session_persistence_type')
    op.drop_table(u'algorithm')
    op.drop_table(u'protocol')
    op.drop_table(u'health_monitor_type')