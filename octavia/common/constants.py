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

LB_ALGORITHM_ROUND_ROBIN = 'ROUND_ROBIN'
LB_ALGORITHM_LEAST_CONNECTIONS = 'LEAST_CONNECTIONS'
LB_ALGORITHM_SOURCE_IP = 'SOURCE_IP'
SUPPORTED_LB_ALGORITHMS = (LB_ALGORITHM_LEAST_CONNECTIONS,
                           LB_ALGORITHM_ROUND_ROBIN,
                           LB_ALGORITHM_SOURCE_IP)

SESSION_PERSISTENCE_SOURCE_IP = 'SOURCE_IP'
SESSION_PERSISTENCE_HTTP_COOKIE = 'HTTP_COOKIE'
SESSION_PERSISTENCE_APP_COOKIE = 'APP_COOKIE'
SUPPORTED_SP_TYPES = (SESSION_PERSISTENCE_SOURCE_IP,
                      SESSION_PERSISTENCE_HTTP_COOKIE,
                      SESSION_PERSISTENCE_APP_COOKIE)

HEALTH_MONITOR_PING = 'PING'
HEALTH_MONITOR_TCP = 'TCP'
HEALTH_MONITOR_HTTP = 'HTTP'
HEALTH_MONITOR_HTTPS = 'HTTPS'
SUPPORTED_HEALTH_MONITOR_TYPES = (HEALTH_MONITOR_HTTP, HEALTH_MONITOR_HTTPS,
                                  HEALTH_MONITOR_PING, HEALTH_MONITOR_TCP)

PROTOCOL_TCP = 'TCP'
PROTOCOL_HTTP = 'HTTP'
PROTOCOL_HTTPS = 'HTTPS'
PROTOCOL_TERMINATED_HTTPS = 'TERMINATED_HTTPS'
SUPPORTED_PROTOCOLS = (PROTOCOL_TCP, PROTOCOL_HTTPS, PROTOCOL_HTTP,
                       PROTOCOL_TERMINATED_HTTPS)

ACTIVE = 'ACTIVE'
PENDING_DELETE = 'PENDING_DELETE'
PENDING_UPDATE = 'PENDING_UPDATE'
PENDING_CREATE = 'PENDING_CREATE'
DELETED = 'DELETED'
SUPPORTED_PROVISIONING_STATUSES = (ACTIVE, PENDING_DELETE, PENDING_CREATE,
                                   PENDING_UPDATE, DELETED)

ONLINE = 'ONLINE'
OFFLINE = 'OFFLINE'
DEGRADED = 'DEGRADED'
SUPPORTED_OPERATING_STATUSES = (ONLINE, OFFLINE, DEGRADED)
