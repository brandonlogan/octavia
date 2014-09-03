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

import oslo.db.exception as oslo_exc
from wsme import types as wtypes
from wsmeext import pecan as wsme_pecan

from octavia.api.v1.controllers import base
from octavia.api.v1 import handler
from octavia.api.v1.types import member as member_types
from octavia.common import constants
from octavia.common import data_models
from octavia.common import exceptions
from octavia.db import api as db_api
from octavia.openstack.common import excutils


class MembersController(base.BaseController):

    def __init__(self, load_balancer_id, listener_id, pool_id):
        super(MembersController, self).__init__()
        self.load_balancer_id = load_balancer_id
        self.listener_id = listener_id
        self.pool_id = pool_id

    @wsme_pecan.wsexpose(member_types.MemberResponse, wtypes.text)
    def get(self, id):
        session = db_api.get_session()
        db_member = self.repositories.member.get(session, id=id)
        if not db_member:
            raise exceptions.NotFound(
                resource=data_models.Member._name(), id=id)
        return self._convert_db_to_type(db_member, member_types.MemberResponse)

    @wsme_pecan.wsexpose([member_types.MemberResponse])
    def get_all(self):
        session = db_api.get_session()
        db_members = self.repositories.member.get_all(
            session, pool_id=self.pool_id)
        return self._convert_db_to_type(db_members,
                                        [member_types.MemberResponse])

    @wsme_pecan.wsexpose(member_types.MemberResponse,
                         body=member_types.MemberPOST, status_code=202)
    def post(self, member):
        session = db_api.get_session()
        member_dict = member.to_dict()
        member_dict['pool_id'] = self.pool_id
        member_dict['operating_status'] = constants.OFFLINE
        self.repositories.listener.update(
            session, self.listener_id,
            provisioning_status=constants.PENDING_UPDATE)
        try:
            db_member = self.repositories.member.create(session, **member_dict)
        except oslo_exc.DBDuplicateEntry:
            raise exceptions.DuplicateMemberEntry(
                ip_address=member_dict.get('ip_address'),
                port=member_dict.get('protocol_port'))
        try:
            self.handler.handle(db_member, handler.HandlerChangeTypes.CREATE)
        except Exception:
            with excutils.save_and_reraise_exception(reraise=False):
                self.repositories.listener.update(
                    session, self.listener_id,
                    operating_status=constants.ERROR)
        db_member = self.repositories.member.get(session, id=db_member.id)
        return self._convert_db_to_type(db_member, member_types.MemberResponse)

    @wsme_pecan.wsexpose(member_types.MemberResponse,
                         wtypes.text, body=member_types.MemberPUT,
                         status_code=202)
    def put(self, id, member):
        session = db_api.get_session()
        old_db_member = self.repositories.member.get(session, id=id)
        if not old_db_member:
            raise exceptions.NotFound(
                resource=data_models.Member._name(), id=id)
        member_dict = member.to_dict(render_unsets=False)
        member_dict['operating_status'] = old_db_member.operating_status
        self.repositories.listener.update(
            session, self.listener_id,
            provisioning_status=constants.PENDING_UPDATE)
        try:
            self.repositories.member.update(session, id, **member_dict)
        except oslo_exc.DBDuplicateEntry:
            raise exceptions.DuplicateMemberEntry(
                ip_address=member_dict.get('ip_address'),
                port=member_dict.get('protocol_port'))
        db_member = self.repositories.member.get(session, id=id)
        try:
            self.handler.handle(db_member, handler.HandlerChangeTypes.UPDATE)
        except Exception:
            with excutils.save_and_reraise_exception(reraise=False):
                self.repositories.listener.update(
                    session, self.listener_id,
                    operating_status=constants.ERROR)
        db_member = self.repositories.member.get(session, id=db_member.id)
        return self._convert_db_to_type(db_member, member_types.MemberResponse)

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=202)
    def delete(self, id):
        session = db_api.get_session()
        db_member = self.repositories.member.get(session, id=id)
        if not db_member:
            raise exceptions.NotFound(
                resource=data_models.Member._name(), id=id)
        self.repositories.listener.update(
            session, self.listener_id,
            provisioning_status=constants.PENDING_UPDATE)
        db_member = self.repositories.member.get(session, id=id)
        try:
            self.handler.handle(db_member, handler.HandlerChangeTypes.UPDATE)
        except Exception:
            with excutils.save_and_reraise_exception(reraise=False):
                self.repositories.listener.update(
                    session, self.listener_id,
                    operating_status=constants.ERROR)
        db_member = self.repositories.member.get(session, id=id)
        return self._convert_db_to_type(db_member, member_types.MemberResponse)
