# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os

import falcon

from promenade import builder
from promenade.control import base
from promenade import logging


class JoinScriptsResource(base.BaseResource):
    """
    Generates join scripts
    """

    def on_get(self,
               req,
               resp,
               hostname,
               ip,
               design_ref,
               *,
               dynamic_labels=None,
               static_labels=None):
        try:
            output = os.getcwd()
            builder.Builder(design_ref, output_dir=output)
            resp.status = falcon.HTTP_204
        except Exception as e:
            msg = "Unable to generate script. Please check arguments"
            logging.error(msg)
            raise falcon.HTTP_400(title=e, description=msg)
