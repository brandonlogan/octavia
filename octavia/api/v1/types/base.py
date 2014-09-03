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

from wsme import types as wtypes


class IPAddressType(wtypes.UserType):
    basetype = str
    name = 'ipaddress'

    @staticmethod
    def validate(value):
        try:
            wtypes.IPv4AddressType.validate(value)
            return value
        except ValueError:
            try:
                wtypes.IPv6AddressType.validate(value)
                return value
            except ValueError:
                error = 'Value should be IPv4 or IPv6 format'
                raise ValueError(error)


class BaseType(wtypes.Base):
    @classmethod
    def from_data_model(cls, data_model):
        return cls(**data_model.to_dict())

    def to_dict(self, render_unsets=True):
        ret_dict = {}
        for attr in dir(self):
            if attr.startswith('_'):
                continue
            value = getattr(self, attr, None)
            if value and callable(value):
                continue
            if value and isinstance(value, BaseType):
                value = value.to_dict()
            if isinstance(value, wtypes.UnsetType):
                if render_unsets:
                    value = None
                else:
                    continue
            ret_dict[attr] = value
        return ret_dict
