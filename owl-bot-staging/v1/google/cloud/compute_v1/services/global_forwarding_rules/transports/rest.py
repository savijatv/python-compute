# -*- coding: utf-8 -*-
# Copyright 2020 Google LLC
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
#

from google.auth.transport.requests import AuthorizedSession  # type: ignore
import json  # type: ignore
import grpc  # type: ignore
from google.auth.transport.grpc import SslCredentials  # type: ignore
from google.auth import credentials as ga_credentials  # type: ignore
from google.api_core import exceptions as core_exceptions
from google.api_core import retry as retries
from google.api_core import rest_helpers
from google.api_core import path_template
from google.api_core import gapic_v1
from requests import __version__ as requests_version
import dataclasses
import re
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union
import warnings

try:
    OptionalRetry = Union[retries.Retry, gapic_v1.method._MethodDefault]
except AttributeError:  # pragma: NO COVER
    OptionalRetry = Union[retries.Retry, object]  # type: ignore


from google.cloud.compute_v1.types import compute

from .base import GlobalForwardingRulesTransport, DEFAULT_CLIENT_INFO as BASE_DEFAULT_CLIENT_INFO


DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
    gapic_version=BASE_DEFAULT_CLIENT_INFO.gapic_version,
    grpc_version=None,
    rest_version=requests_version,
)


class GlobalForwardingRulesRestInterceptor:
    """Interceptor for GlobalForwardingRules.

    Interceptors are used to manipulate requests, request metadata, and responses
    in arbitrary ways.
    Example use cases include:
    * Logging
    * Verifying requests according to service or custom semantics
    * Stripping extraneous information from responses

    These use cases and more can be enabled by injecting an
    instance of a custom subclass when constructing the GlobalForwardingRulesRestTransport.

    .. code-block:
        class MyCustomGlobalForwardingRulesInterceptor(GlobalForwardingRulesRestInterceptor):
            def pre_delete(request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_delete(response):
                logging.log(f"Received response: {response}")

            def pre_get(request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_get(response):
                logging.log(f"Received response: {response}")

            def pre_insert(request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_insert(response):
                logging.log(f"Received response: {response}")

            def pre_list(request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_list(response):
                logging.log(f"Received response: {response}")

            def pre_patch(request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_patch(response):
                logging.log(f"Received response: {response}")

            def pre_set_labels(request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_set_labels(response):
                logging.log(f"Received response: {response}")

            def pre_set_target(request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_set_target(response):
                logging.log(f"Received response: {response}")

        transport = GlobalForwardingRulesRestTransport(interceptor=MyCustomGlobalForwardingRulesInterceptor())
        client = GlobalForwardingRulesClient(transport=transport)


    """
    def pre_delete(self, request: compute.DeleteGlobalForwardingRuleRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[compute.DeleteGlobalForwardingRuleRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for delete

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GlobalForwardingRules server.
        """
        return request, metadata

    def post_delete(self, response: compute.Operation) -> compute.Operation:
        """Post-rpc interceptor for delete

        Override in a subclass to manipulate the response
        after it is returned by the GlobalForwardingRules server but before
        it is returned to user code.
        """
        return response

    def pre_get(self, request: compute.GetGlobalForwardingRuleRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[compute.GetGlobalForwardingRuleRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GlobalForwardingRules server.
        """
        return request, metadata

    def post_get(self, response: compute.ForwardingRule) -> compute.ForwardingRule:
        """Post-rpc interceptor for get

        Override in a subclass to manipulate the response
        after it is returned by the GlobalForwardingRules server but before
        it is returned to user code.
        """
        return response

    def pre_insert(self, request: compute.InsertGlobalForwardingRuleRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[compute.InsertGlobalForwardingRuleRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for insert

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GlobalForwardingRules server.
        """
        return request, metadata

    def post_insert(self, response: compute.Operation) -> compute.Operation:
        """Post-rpc interceptor for insert

        Override in a subclass to manipulate the response
        after it is returned by the GlobalForwardingRules server but before
        it is returned to user code.
        """
        return response

    def pre_list(self, request: compute.ListGlobalForwardingRulesRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[compute.ListGlobalForwardingRulesRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GlobalForwardingRules server.
        """
        return request, metadata

    def post_list(self, response: compute.ForwardingRuleList) -> compute.ForwardingRuleList:
        """Post-rpc interceptor for list

        Override in a subclass to manipulate the response
        after it is returned by the GlobalForwardingRules server but before
        it is returned to user code.
        """
        return response

    def pre_patch(self, request: compute.PatchGlobalForwardingRuleRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[compute.PatchGlobalForwardingRuleRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for patch

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GlobalForwardingRules server.
        """
        return request, metadata

    def post_patch(self, response: compute.Operation) -> compute.Operation:
        """Post-rpc interceptor for patch

        Override in a subclass to manipulate the response
        after it is returned by the GlobalForwardingRules server but before
        it is returned to user code.
        """
        return response

    def pre_set_labels(self, request: compute.SetLabelsGlobalForwardingRuleRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[compute.SetLabelsGlobalForwardingRuleRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for set_labels

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GlobalForwardingRules server.
        """
        return request, metadata

    def post_set_labels(self, response: compute.Operation) -> compute.Operation:
        """Post-rpc interceptor for set_labels

        Override in a subclass to manipulate the response
        after it is returned by the GlobalForwardingRules server but before
        it is returned to user code.
        """
        return response

    def pre_set_target(self, request: compute.SetTargetGlobalForwardingRuleRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[compute.SetTargetGlobalForwardingRuleRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for set_target

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GlobalForwardingRules server.
        """
        return request, metadata

    def post_set_target(self, response: compute.Operation) -> compute.Operation:
        """Post-rpc interceptor for set_target

        Override in a subclass to manipulate the response
        after it is returned by the GlobalForwardingRules server but before
        it is returned to user code.
        """
        return response


@dataclasses.dataclass
class GlobalForwardingRulesRestStub:
    _session: AuthorizedSession
    _host: str
    _interceptor: GlobalForwardingRulesRestInterceptor


class GlobalForwardingRulesRestTransport(GlobalForwardingRulesTransport):
    """REST backend transport for GlobalForwardingRules.

    The GlobalForwardingRules API.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends JSON representations of protocol buffers over HTTP/1.1
    """
    _STUBS: Dict[str, GlobalForwardingRulesRestStub] = {}

    def __init__(self, *,
            host: str = 'compute.googleapis.com',
            credentials: ga_credentials.Credentials=None,
            credentials_file: str=None,
            scopes: Sequence[str]=None,
            client_cert_source_for_mtls: Callable[[
                ], Tuple[bytes, bytes]]=None,
            quota_project_id: Optional[str]=None,
            client_info: gapic_v1.client_info.ClientInfo=DEFAULT_CLIENT_INFO,
            always_use_jwt_access: Optional[bool]=False,
            url_scheme: str='https',
            interceptor: Optional[GlobalForwardingRulesRestInterceptor] = None,
            ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]):
                 The hostname to connect to.
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.

            credentials_file (Optional[str]): A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is ignored if ``channel`` is provided.
            scopes (Optional(Sequence[str])): A list of scopes. This argument is
                ignored if ``channel`` is provided.
            client_cert_source_for_mtls (Callable[[], Tuple[bytes, bytes]]): Client
                certificate to configure mutual TLS HTTP channel. It is ignored
                if ``channel`` is provided.
            quota_project_id (Optional[str]): An optional project to use for billing
                and quota.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you are developing
                your own client library.
            always_use_jwt_access (Optional[bool]): Whether self signed JWT should
                be used for service account credentials.
            url_scheme: the protocol scheme for the API endpoint.  Normally
                "https", but for testing or local servers,
                "http" can be specified.
        """
        # Run the base constructor
        # TODO(yon-mg): resolve other ctor params i.e. scopes, quota, etc.
        # TODO: When custom host (api_endpoint) is set, `scopes` must *also* be set on the
        # credentials object
        maybe_url_match = re.match("^(?P<scheme>http(?:s)?://)?(?P<host>.*)$", host)
        if maybe_url_match is None:
            raise ValueError(f"Unexpected hostname structure: {host}")  # pragma: NO COVER

        url_match_items = maybe_url_match.groupdict()

        host = f"{url_scheme}://{host}" if not url_match_items["scheme"] else host

        super().__init__(
            host=host,
            credentials=credentials,
            client_info=client_info,
            always_use_jwt_access=always_use_jwt_access,
        )
        self._session = AuthorizedSession(
            self._credentials, default_host=self.DEFAULT_HOST)
        if client_cert_source_for_mtls:
            self._session.configure_mtls_channel(client_cert_source_for_mtls)
        self._interceptor = interceptor or GlobalForwardingRulesRestInterceptor()
        self._prep_wrapped_messages(client_info)

    class _Delete(GlobalForwardingRulesRestStub):
        def __hash__(self):
            return hash("Delete")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, str] =  {
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {k: v for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items() if k not in message_dict}

        def __call__(self,
                request: compute.DeleteGlobalForwardingRuleRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: float=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> compute.Operation:
            r"""Call the delete method over HTTP.

            Args:
                request (~.compute.DeleteGlobalForwardingRuleRequest):
                    The request object. A request message for
                GlobalForwardingRules.Delete. See the
                method description for details.

                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.compute.Operation:
                    Represents an Operation resource. Google Compute Engine
                has three Operation resources: \*
                `Global </compute/docs/reference/rest/v1/globalOperations>`__
                \*
                `Regional </compute/docs/reference/rest/v1/regionOperations>`__
                \*
                `Zonal </compute/docs/reference/rest/v1/zoneOperations>`__
                You can use an operation resource to manage asynchronous
                API requests. For more information, read Handling API
                responses. Operations can be global, regional or zonal.
                - For global operations, use the ``globalOperations``
                resource. - For regional operations, use the
                ``regionOperations`` resource. - For zonal operations,
                use the ``zonalOperations`` resource. For more
                information, read Global, Regional, and Zonal Resources.

            """

            http_options: List[Dict[str, str]] = [{
                'method': 'delete',
                'uri': '/compute/v1/projects/{project}/global/forwardingRules/{forwarding_rule}',
            },
            ]
            request, metadata = self._interceptor.pre_delete(request, metadata)
            request_kwargs = compute.DeleteGlobalForwardingRuleRequest.to_dict(request)
            transcoded_request = path_template.transcode(
                http_options, **request_kwargs)

            uri = transcoded_request['uri']
            method = transcoded_request['method']

            # Jsonify the query params
            query_params = json.loads(compute.DeleteGlobalForwardingRuleRequest.to_json(
                compute.DeleteGlobalForwardingRuleRequest(transcoded_request['query_params']),
                including_default_value_fields=False,
                use_integers_for_enums=False
            ))

            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
                )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = compute.Operation.from_json(
                response.content,
                ignore_unknown_fields=True
            )
            resp = self._interceptor.post_delete(resp)
            return resp

    class _Get(GlobalForwardingRulesRestStub):
        def __hash__(self):
            return hash("Get")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, str] =  {
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {k: v for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items() if k not in message_dict}

        def __call__(self,
                request: compute.GetGlobalForwardingRuleRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: float=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> compute.ForwardingRule:
            r"""Call the get method over HTTP.

            Args:
                request (~.compute.GetGlobalForwardingRuleRequest):
                    The request object. A request message for
                GlobalForwardingRules.Get. See the
                method description for details.

                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.compute.ForwardingRule:
                    Represents a Forwarding Rule resource. Forwarding rule
                resources in Google Cloud can be either regional or
                global in scope: \*
                `Global <https://cloud.google.com/compute/docs/reference/rest/v1/globalForwardingRules>`__
                \*
                `Regional <https://cloud.google.com/compute/docs/reference/rest/v1/forwardingRules>`__
                A forwarding rule and its corresponding IP address
                represent the frontend configuration of a Google Cloud
                Platform load balancer. Forwarding rules can also
                reference target instances and Cloud VPN Classic
                gateways (targetVpnGateway). For more information, read
                Forwarding rule concepts and Using protocol forwarding.

            """

            http_options: List[Dict[str, str]] = [{
                'method': 'get',
                'uri': '/compute/v1/projects/{project}/global/forwardingRules/{forwarding_rule}',
            },
            ]
            request, metadata = self._interceptor.pre_get(request, metadata)
            request_kwargs = compute.GetGlobalForwardingRuleRequest.to_dict(request)
            transcoded_request = path_template.transcode(
                http_options, **request_kwargs)

            uri = transcoded_request['uri']
            method = transcoded_request['method']

            # Jsonify the query params
            query_params = json.loads(compute.GetGlobalForwardingRuleRequest.to_json(
                compute.GetGlobalForwardingRuleRequest(transcoded_request['query_params']),
                including_default_value_fields=False,
                use_integers_for_enums=False
            ))

            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
                )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = compute.ForwardingRule.from_json(
                response.content,
                ignore_unknown_fields=True
            )
            resp = self._interceptor.post_get(resp)
            return resp

    class _Insert(GlobalForwardingRulesRestStub):
        def __hash__(self):
            return hash("Insert")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, str] =  {
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {k: v for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items() if k not in message_dict}

        def __call__(self,
                request: compute.InsertGlobalForwardingRuleRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: float=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> compute.Operation:
            r"""Call the insert method over HTTP.

            Args:
                request (~.compute.InsertGlobalForwardingRuleRequest):
                    The request object. A request message for
                GlobalForwardingRules.Insert. See the
                method description for details.

                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.compute.Operation:
                    Represents an Operation resource. Google Compute Engine
                has three Operation resources: \*
                `Global </compute/docs/reference/rest/v1/globalOperations>`__
                \*
                `Regional </compute/docs/reference/rest/v1/regionOperations>`__
                \*
                `Zonal </compute/docs/reference/rest/v1/zoneOperations>`__
                You can use an operation resource to manage asynchronous
                API requests. For more information, read Handling API
                responses. Operations can be global, regional or zonal.
                - For global operations, use the ``globalOperations``
                resource. - For regional operations, use the
                ``regionOperations`` resource. - For zonal operations,
                use the ``zonalOperations`` resource. For more
                information, read Global, Regional, and Zonal Resources.

            """

            http_options: List[Dict[str, str]] = [{
                'method': 'post',
                'uri': '/compute/v1/projects/{project}/global/forwardingRules',
                'body': 'forwarding_rule_resource',
            },
            ]
            request, metadata = self._interceptor.pre_insert(request, metadata)
            request_kwargs = compute.InsertGlobalForwardingRuleRequest.to_dict(request)
            transcoded_request = path_template.transcode(
                http_options, **request_kwargs)

            # Jsonify the request body
            body = compute.ForwardingRule.to_json(
                compute.ForwardingRule(transcoded_request['body']),                including_default_value_fields=False,
                use_integers_for_enums=False
            )
            uri = transcoded_request['uri']
            method = transcoded_request['method']

            # Jsonify the query params
            query_params = json.loads(compute.InsertGlobalForwardingRuleRequest.to_json(
                compute.InsertGlobalForwardingRuleRequest(transcoded_request['query_params']),
                including_default_value_fields=False,
                use_integers_for_enums=False
            ))

            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
                data=body,
                )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = compute.Operation.from_json(
                response.content,
                ignore_unknown_fields=True
            )
            resp = self._interceptor.post_insert(resp)
            return resp

    class _List(GlobalForwardingRulesRestStub):
        def __hash__(self):
            return hash("List")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, str] =  {
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {k: v for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items() if k not in message_dict}

        def __call__(self,
                request: compute.ListGlobalForwardingRulesRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: float=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> compute.ForwardingRuleList:
            r"""Call the list method over HTTP.

            Args:
                request (~.compute.ListGlobalForwardingRulesRequest):
                    The request object. A request message for
                GlobalForwardingRules.List. See the
                method description for details.

                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.compute.ForwardingRuleList:
                    Contains a list of ForwardingRule
                resources.

            """

            http_options: List[Dict[str, str]] = [{
                'method': 'get',
                'uri': '/compute/v1/projects/{project}/global/forwardingRules',
            },
            ]
            request, metadata = self._interceptor.pre_list(request, metadata)
            request_kwargs = compute.ListGlobalForwardingRulesRequest.to_dict(request)
            transcoded_request = path_template.transcode(
                http_options, **request_kwargs)

            uri = transcoded_request['uri']
            method = transcoded_request['method']

            # Jsonify the query params
            query_params = json.loads(compute.ListGlobalForwardingRulesRequest.to_json(
                compute.ListGlobalForwardingRulesRequest(transcoded_request['query_params']),
                including_default_value_fields=False,
                use_integers_for_enums=False
            ))

            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
                )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = compute.ForwardingRuleList.from_json(
                response.content,
                ignore_unknown_fields=True
            )
            resp = self._interceptor.post_list(resp)
            return resp

    class _Patch(GlobalForwardingRulesRestStub):
        def __hash__(self):
            return hash("Patch")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, str] =  {
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {k: v for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items() if k not in message_dict}

        def __call__(self,
                request: compute.PatchGlobalForwardingRuleRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: float=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> compute.Operation:
            r"""Call the patch method over HTTP.

            Args:
                request (~.compute.PatchGlobalForwardingRuleRequest):
                    The request object. A request message for
                GlobalForwardingRules.Patch. See the
                method description for details.

                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.compute.Operation:
                    Represents an Operation resource. Google Compute Engine
                has three Operation resources: \*
                `Global </compute/docs/reference/rest/v1/globalOperations>`__
                \*
                `Regional </compute/docs/reference/rest/v1/regionOperations>`__
                \*
                `Zonal </compute/docs/reference/rest/v1/zoneOperations>`__
                You can use an operation resource to manage asynchronous
                API requests. For more information, read Handling API
                responses. Operations can be global, regional or zonal.
                - For global operations, use the ``globalOperations``
                resource. - For regional operations, use the
                ``regionOperations`` resource. - For zonal operations,
                use the ``zonalOperations`` resource. For more
                information, read Global, Regional, and Zonal Resources.

            """

            http_options: List[Dict[str, str]] = [{
                'method': 'patch',
                'uri': '/compute/v1/projects/{project}/global/forwardingRules/{forwarding_rule}',
                'body': 'forwarding_rule_resource',
            },
            ]
            request, metadata = self._interceptor.pre_patch(request, metadata)
            request_kwargs = compute.PatchGlobalForwardingRuleRequest.to_dict(request)
            transcoded_request = path_template.transcode(
                http_options, **request_kwargs)

            # Jsonify the request body
            body = compute.ForwardingRule.to_json(
                compute.ForwardingRule(transcoded_request['body']),                including_default_value_fields=False,
                use_integers_for_enums=False
            )
            uri = transcoded_request['uri']
            method = transcoded_request['method']

            # Jsonify the query params
            query_params = json.loads(compute.PatchGlobalForwardingRuleRequest.to_json(
                compute.PatchGlobalForwardingRuleRequest(transcoded_request['query_params']),
                including_default_value_fields=False,
                use_integers_for_enums=False
            ))

            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
                data=body,
                )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = compute.Operation.from_json(
                response.content,
                ignore_unknown_fields=True
            )
            resp = self._interceptor.post_patch(resp)
            return resp

    class _SetLabels(GlobalForwardingRulesRestStub):
        def __hash__(self):
            return hash("SetLabels")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, str] =  {
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {k: v for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items() if k not in message_dict}

        def __call__(self,
                request: compute.SetLabelsGlobalForwardingRuleRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: float=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> compute.Operation:
            r"""Call the set labels method over HTTP.

            Args:
                request (~.compute.SetLabelsGlobalForwardingRuleRequest):
                    The request object. A request message for
                GlobalForwardingRules.SetLabels. See the
                method description for details.

                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.compute.Operation:
                    Represents an Operation resource. Google Compute Engine
                has three Operation resources: \*
                `Global </compute/docs/reference/rest/v1/globalOperations>`__
                \*
                `Regional </compute/docs/reference/rest/v1/regionOperations>`__
                \*
                `Zonal </compute/docs/reference/rest/v1/zoneOperations>`__
                You can use an operation resource to manage asynchronous
                API requests. For more information, read Handling API
                responses. Operations can be global, regional or zonal.
                - For global operations, use the ``globalOperations``
                resource. - For regional operations, use the
                ``regionOperations`` resource. - For zonal operations,
                use the ``zonalOperations`` resource. For more
                information, read Global, Regional, and Zonal Resources.

            """

            http_options: List[Dict[str, str]] = [{
                'method': 'post',
                'uri': '/compute/v1/projects/{project}/global/forwardingRules/{resource}/setLabels',
                'body': 'global_set_labels_request_resource',
            },
            ]
            request, metadata = self._interceptor.pre_set_labels(request, metadata)
            request_kwargs = compute.SetLabelsGlobalForwardingRuleRequest.to_dict(request)
            transcoded_request = path_template.transcode(
                http_options, **request_kwargs)

            # Jsonify the request body
            body = compute.GlobalSetLabelsRequest.to_json(
                compute.GlobalSetLabelsRequest(transcoded_request['body']),                including_default_value_fields=False,
                use_integers_for_enums=False
            )
            uri = transcoded_request['uri']
            method = transcoded_request['method']

            # Jsonify the query params
            query_params = json.loads(compute.SetLabelsGlobalForwardingRuleRequest.to_json(
                compute.SetLabelsGlobalForwardingRuleRequest(transcoded_request['query_params']),
                including_default_value_fields=False,
                use_integers_for_enums=False
            ))

            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
                data=body,
                )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = compute.Operation.from_json(
                response.content,
                ignore_unknown_fields=True
            )
            resp = self._interceptor.post_set_labels(resp)
            return resp

    class _SetTarget(GlobalForwardingRulesRestStub):
        def __hash__(self):
            return hash("SetTarget")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, str] =  {
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {k: v for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items() if k not in message_dict}

        def __call__(self,
                request: compute.SetTargetGlobalForwardingRuleRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: float=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> compute.Operation:
            r"""Call the set target method over HTTP.

            Args:
                request (~.compute.SetTargetGlobalForwardingRuleRequest):
                    The request object. A request message for
                GlobalForwardingRules.SetTarget. See the
                method description for details.

                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.compute.Operation:
                    Represents an Operation resource. Google Compute Engine
                has three Operation resources: \*
                `Global </compute/docs/reference/rest/v1/globalOperations>`__
                \*
                `Regional </compute/docs/reference/rest/v1/regionOperations>`__
                \*
                `Zonal </compute/docs/reference/rest/v1/zoneOperations>`__
                You can use an operation resource to manage asynchronous
                API requests. For more information, read Handling API
                responses. Operations can be global, regional or zonal.
                - For global operations, use the ``globalOperations``
                resource. - For regional operations, use the
                ``regionOperations`` resource. - For zonal operations,
                use the ``zonalOperations`` resource. For more
                information, read Global, Regional, and Zonal Resources.

            """

            http_options: List[Dict[str, str]] = [{
                'method': 'post',
                'uri': '/compute/v1/projects/{project}/global/forwardingRules/{forwarding_rule}/setTarget',
                'body': 'target_reference_resource',
            },
            ]
            request, metadata = self._interceptor.pre_set_target(request, metadata)
            request_kwargs = compute.SetTargetGlobalForwardingRuleRequest.to_dict(request)
            transcoded_request = path_template.transcode(
                http_options, **request_kwargs)

            # Jsonify the request body
            body = compute.TargetReference.to_json(
                compute.TargetReference(transcoded_request['body']),                including_default_value_fields=False,
                use_integers_for_enums=False
            )
            uri = transcoded_request['uri']
            method = transcoded_request['method']

            # Jsonify the query params
            query_params = json.loads(compute.SetTargetGlobalForwardingRuleRequest.to_json(
                compute.SetTargetGlobalForwardingRuleRequest(transcoded_request['query_params']),
                including_default_value_fields=False,
                use_integers_for_enums=False
            ))

            query_params.update(self._get_unset_required_fields(query_params))

            # Send the request
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(self._session, method)(
                "{host}{uri}".format(host=self._host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params),
                data=body,
                )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = compute.Operation.from_json(
                response.content,
                ignore_unknown_fields=True
            )
            resp = self._interceptor.post_set_target(resp)
            return resp

    @property
    def delete(self) -> Callable[
            [compute.DeleteGlobalForwardingRuleRequest],
            compute.Operation]:
        stub = self._STUBS.get("delete")
        if not stub:
            stub = self._STUBS["delete"] = self._Delete(self._session, self._host, self._interceptor)

        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return stub # type: ignore

    @property
    def get(self) -> Callable[
            [compute.GetGlobalForwardingRuleRequest],
            compute.ForwardingRule]:
        stub = self._STUBS.get("get")
        if not stub:
            stub = self._STUBS["get"] = self._Get(self._session, self._host, self._interceptor)

        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return stub # type: ignore

    @property
    def insert(self) -> Callable[
            [compute.InsertGlobalForwardingRuleRequest],
            compute.Operation]:
        stub = self._STUBS.get("insert")
        if not stub:
            stub = self._STUBS["insert"] = self._Insert(self._session, self._host, self._interceptor)

        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return stub # type: ignore

    @property
    def list(self) -> Callable[
            [compute.ListGlobalForwardingRulesRequest],
            compute.ForwardingRuleList]:
        stub = self._STUBS.get("list")
        if not stub:
            stub = self._STUBS["list"] = self._List(self._session, self._host, self._interceptor)

        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return stub # type: ignore

    @property
    def patch(self) -> Callable[
            [compute.PatchGlobalForwardingRuleRequest],
            compute.Operation]:
        stub = self._STUBS.get("patch")
        if not stub:
            stub = self._STUBS["patch"] = self._Patch(self._session, self._host, self._interceptor)

        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return stub # type: ignore

    @property
    def set_labels(self) -> Callable[
            [compute.SetLabelsGlobalForwardingRuleRequest],
            compute.Operation]:
        stub = self._STUBS.get("set_labels")
        if not stub:
            stub = self._STUBS["set_labels"] = self._SetLabels(self._session, self._host, self._interceptor)

        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return stub # type: ignore

    @property
    def set_target(self) -> Callable[
            [compute.SetTargetGlobalForwardingRuleRequest],
            compute.Operation]:
        stub = self._STUBS.get("set_target")
        if not stub:
            stub = self._STUBS["set_target"] = self._SetTarget(self._session, self._host, self._interceptor)

        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return stub # type: ignore

    def close(self):
        self._session.close()


__all__=(
    'GlobalForwardingRulesRestTransport',
)
