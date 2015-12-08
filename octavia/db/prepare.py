#    Copyright 2015 Rackspace
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

from oslo_utils import uuidutils

from octavia.common import constants


def create_load_balancer(lb_dict):
    if not lb_dict.get('id'):
        lb_dict['id'] = uuidutils.generate_uuid()
    if lb_dict.get('vip'):
        lb_dict['vip']['load_balancer_id'] = lb_dict.get('id')
    lb_dict['provisioning_status'] = constants.PENDING_CREATE
    lb_dict['operating_status'] = constants.OFFLINE
    return lb_dict


def create_listener(listener_dict, lb_id):
    if not listener_dict.get('id'):
        listener_dict['id'] = uuidutils.generate_uuid()
    listener_dict['load_balancer_id'] = lb_id
    listener_dict['provisioning_status'] = constants.PENDING_CREATE
    listener_dict['operating_status'] = constants.OFFLINE
    # NOTE(blogan): Throwing away because we should not store secure data
    # in the database nor should we send it to a handler.
    if 'tls_termination' in listener_dict:
        del listener_dict['tls_termination']
    sni_container_ids = listener_dict.pop('sni_containers', [])
    sni_containers = [{'listener_id': listener_dict.get('id'),
                       'tls_container_id': sni_container_id}
                      for sni_container_id in sni_container_ids]
    listener_dict['sni_containers'] = sni_containers
    return listener_dict


def create_pool(pool_dict):
    if not pool_dict.get('id'):
        pool_dict['id'] = uuidutils.generate_uuid()
    if pool_dict.get('session_persistence'):
        pool_dict['session_persistence']['pool_id'] = pool_dict.get('id')
    pool_dict['operating_status'] = constants.OFFLINE
    return pool_dict


def create_member(member_dict, pool_id):
    member_dict['pool_id'] = pool_id
    member_dict['operating_status'] = constants.OFFLINE
    return member_dict


def create_health_monitor(hm_dict, pool_id):
    hm_dict['pool_id'] = pool_id
    return hm_dict
