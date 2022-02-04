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
from google.api_core import rest_streaming
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

from .base import SnapshotsTransport, DEFAULT_CLIENT_INFO as BASE_DEFAULT_CLIENT_INFO


DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
    gapic_version=BASE_DEFAULT_CLIENT_INFO.gapic_version,
    grpc_version=None,
    rest_version=requests_version,
)


class SnapshotsRestInterceptor:
    """Interceptor for Snapshots.

    Interceptors are used to manipulate requests, request metadata, and responses
    in arbitrary ways.
    Example use cases include:
    * Logging
    * Verifying requests according to service or custom semantics
    * Stripping extraneous information from responses

    These use cases and more can be enabled by injecting an
    instance of a custom subclass when constructing the SnapshotsRestTransport.

    .. code-block:
        class MyCustomSnapshotsInterceptor(SnapshotsRestInterceptor):
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

            def pre_get_iam_policy(request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_get_iam_policy(response):
                logging.log(f"Received response: {response}")

            def pre_list(request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_list(response):
                logging.log(f"Received response: {response}")

            def pre_set_iam_policy(request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_set_iam_policy(response):
                logging.log(f"Received response: {response}")

            def pre_set_labels(request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_set_labels(response):
                logging.log(f"Received response: {response}")

            def pre_test_iam_permissions(request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_test_iam_permissions(response):
                logging.log(f"Received response: {response}")

        transport = SnapshotsRestTransport(interceptor=MyCustomSnapshotsInterceptor())
        client = SnapshotsClient(transport=transport)


    """
    def pre_delete(self, request: compute.DeleteSnapshotRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[compute.DeleteSnapshotRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for delete

        Override in a subclass to manipulate the request or metadata
        before they are sent to the Snapshots server.
        """
        return request, metadata

    def post_delete(self, response: compute.Operation) -> compute.Operation:
        """Post-rpc interceptor for delete

        Override in a subclass to manipulate the response
        after it is returned by the Snapshots server but before
        it is returned to user code.
        """
        return response

    def pre_get(self, request: compute.GetSnapshotRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[compute.GetSnapshotRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get

        Override in a subclass to manipulate the request or metadata
        before they are sent to the Snapshots server.
        """
        return request, metadata

    def post_get(self, response: compute.Snapshot) -> compute.Snapshot:
        """Post-rpc interceptor for get

        Override in a subclass to manipulate the response
        after it is returned by the Snapshots server but before
        it is returned to user code.
        """
        return response

    def pre_get_iam_policy(self, request: compute.GetIamPolicySnapshotRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[compute.GetIamPolicySnapshotRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_iam_policy

        Override in a subclass to manipulate the request or metadata
        before they are sent to the Snapshots server.
        """
        return request, metadata

    def post_get_iam_policy(self, response: compute.Policy) -> compute.Policy:
        """Post-rpc interceptor for get_iam_policy

        Override in a subclass to manipulate the response
        after it is returned by the Snapshots server but before
        it is returned to user code.
        """
        return response

    def pre_list(self, request: compute.ListSnapshotsRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[compute.ListSnapshotsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list

        Override in a subclass to manipulate the request or metadata
        before they are sent to the Snapshots server.
        """
        return request, metadata

    def post_list(self, response: compute.SnapshotList) -> compute.SnapshotList:
        """Post-rpc interceptor for list

        Override in a subclass to manipulate the response
        after it is returned by the Snapshots server but before
        it is returned to user code.
        """
        return response

    def pre_set_iam_policy(self, request: compute.SetIamPolicySnapshotRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[compute.SetIamPolicySnapshotRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for set_iam_policy

        Override in a subclass to manipulate the request or metadata
        before they are sent to the Snapshots server.
        """
        return request, metadata

    def post_set_iam_policy(self, response: compute.Policy) -> compute.Policy:
        """Post-rpc interceptor for set_iam_policy

        Override in a subclass to manipulate the response
        after it is returned by the Snapshots server but before
        it is returned to user code.
        """
        return response

    def pre_set_labels(self, request: compute.SetLabelsSnapshotRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[compute.SetLabelsSnapshotRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for set_labels

        Override in a subclass to manipulate the request or metadata
        before they are sent to the Snapshots server.
        """
        return request, metadata

    def post_set_labels(self, response: compute.Operation) -> compute.Operation:
        """Post-rpc interceptor for set_labels

        Override in a subclass to manipulate the response
        after it is returned by the Snapshots server but before
        it is returned to user code.
        """
        return response

    def pre_test_iam_permissions(self, request: compute.TestIamPermissionsSnapshotRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[compute.TestIamPermissionsSnapshotRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for test_iam_permissions

        Override in a subclass to manipulate the request or metadata
        before they are sent to the Snapshots server.
        """
        return request, metadata

    def post_test_iam_permissions(self, response: compute.TestPermissionsResponse) -> compute.TestPermissionsResponse:
        """Post-rpc interceptor for test_iam_permissions

        Override in a subclass to manipulate the response
        after it is returned by the Snapshots server but before
        it is returned to user code.
        """
        return response


@dataclasses.dataclass
class SnapshotsRestStub:
    _session: AuthorizedSession
    _host: str
    _interceptor: SnapshotsRestInterceptor


class SnapshotsRestTransport(SnapshotsTransport):
    """REST backend transport for Snapshots.

    The Snapshots API.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends JSON representations of protocol buffers over HTTP/1.1
    """
    _STUBS: Dict[str, SnapshotsRestStub] = {}

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
            interceptor: Optional[SnapshotsRestInterceptor] = None,
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
        self._interceptor = interceptor or SnapshotsRestInterceptor()
        self._prep_wrapped_messages(client_info)

    class _Delete(SnapshotsRestStub):
        def __hash__(self):
            return hash("Delete")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, str] =  {
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {k: v for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items() if k not in message_dict}

        def __call__(self,
                request: compute.DeleteSnapshotRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: float=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> compute.Operation:
            r"""Call the delete method over HTTP.

            Args:
                request (~.compute.DeleteSnapshotRequest):
                    The request object. A request message for
                Snapshots.Delete. See the method
                description for details.

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
                'uri': '/compute/v1/projects/{project}/global/snapshots/{snapshot}',
            },
            ]
            request, metadata = self._interceptor.pre_delete(request, metadata)
            request_kwargs = compute.DeleteSnapshotRequest.to_dict(request)
            transcoded_request = path_template.transcode(
                http_options, **request_kwargs)

            uri = transcoded_request['uri']
            method = transcoded_request['method']

            # Jsonify the query params
            query_params = json.loads(compute.DeleteSnapshotRequest.to_json(
                compute.DeleteSnapshotRequest(transcoded_request['query_params']),
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

    class _Get(SnapshotsRestStub):
        def __hash__(self):
            return hash("Get")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, str] =  {
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {k: v for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items() if k not in message_dict}

        def __call__(self,
                request: compute.GetSnapshotRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: float=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> compute.Snapshot:
            r"""Call the get method over HTTP.

            Args:
                request (~.compute.GetSnapshotRequest):
                    The request object. A request message for Snapshots.Get.
                See the method description for details.

                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.compute.Snapshot:
                    Represents a Persistent Disk Snapshot
                resource. You can use snapshots to back
                up data on a regular interval. For more
                information, read Creating persistent
                disk snapshots.

            """

            http_options: List[Dict[str, str]] = [{
                'method': 'get',
                'uri': '/compute/v1/projects/{project}/global/snapshots/{snapshot}',
            },
            ]
            request, metadata = self._interceptor.pre_get(request, metadata)
            request_kwargs = compute.GetSnapshotRequest.to_dict(request)
            transcoded_request = path_template.transcode(
                http_options, **request_kwargs)

            uri = transcoded_request['uri']
            method = transcoded_request['method']

            # Jsonify the query params
            query_params = json.loads(compute.GetSnapshotRequest.to_json(
                compute.GetSnapshotRequest(transcoded_request['query_params']),
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
            resp = compute.Snapshot.from_json(
                response.content,
                ignore_unknown_fields=True
            )
            resp = self._interceptor.post_get(resp)
            return resp

    class _GetIamPolicy(SnapshotsRestStub):
        def __hash__(self):
            return hash("GetIamPolicy")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, str] =  {
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {k: v for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items() if k not in message_dict}

        def __call__(self,
                request: compute.GetIamPolicySnapshotRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: float=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> compute.Policy:
            r"""Call the get iam policy method over HTTP.

            Args:
                request (~.compute.GetIamPolicySnapshotRequest):
                    The request object. A request message for
                Snapshots.GetIamPolicy. See the method
                description for details.

                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.compute.Policy:
                    An Identity and Access Management (IAM) policy, which
                specifies access controls for Google Cloud resources. A
                ``Policy`` is a collection of ``bindings``. A
                ``binding`` binds one or more ``members`` to a single
                ``role``. Members can be user accounts, service
                accounts, Google groups, and domains (such as G Suite).
                A ``role`` is a named list of permissions; each ``role``
                can be an IAM predefined role or a user-created custom
                role. For some types of Google Cloud resources, a
                ``binding`` can also specify a ``condition``, which is a
                logical expression that allows access to a resource only
                if the expression evaluates to ``true``. A condition can
                add constraints based on attributes of the request, the
                resource, or both. To learn which resources support
                conditions in their IAM policies, see the `IAM
                documentation <https://cloud.google.com/iam/help/conditions/resource-policies>`__.
                **JSON example:** { "bindings": [ { "role":
                "roles/resourcemanager.organizationAdmin", "members": [
                "user:mike@example.com", "group:admins@example.com",
                "domain:google.com",
                "serviceAccount:my-project-id@appspot.gserviceaccount.com"
                ] }, { "role":
                "roles/resourcemanager.organizationViewer", "members": [
                "user:eve@example.com" ], "condition": { "title":
                "expirable access", "description": "Does not grant
                access after Sep 2020", "expression": "request.time <
                timestamp('2020-10-01T00:00:00.000Z')", } } ], "etag":
                "BwWWja0YfJA=", "version": 3 } **YAML example:**
                bindings: - members: - user:mike@example.com -
                group:admins@example.com - domain:google.com -
                serviceAccount:my-project-id@appspot.gserviceaccount.com
                role: roles/resourcemanager.organizationAdmin - members:
                - user:eve@example.com role:
                roles/resourcemanager.organizationViewer condition:
                title: expirable access description: Does not grant
                access after Sep 2020 expression: request.time <
                timestamp('2020-10-01T00:00:00.000Z') etag: BwWWja0YfJA=
                version: 3 For a description of IAM and its features,
                see the `IAM
                documentation <https://cloud.google.com/iam/docs/>`__.

            """

            http_options: List[Dict[str, str]] = [{
                'method': 'get',
                'uri': '/compute/v1/projects/{project}/global/snapshots/{resource}/getIamPolicy',
            },
            ]
            request, metadata = self._interceptor.pre_get_iam_policy(request, metadata)
            request_kwargs = compute.GetIamPolicySnapshotRequest.to_dict(request)
            transcoded_request = path_template.transcode(
                http_options, **request_kwargs)

            uri = transcoded_request['uri']
            method = transcoded_request['method']

            # Jsonify the query params
            query_params = json.loads(compute.GetIamPolicySnapshotRequest.to_json(
                compute.GetIamPolicySnapshotRequest(transcoded_request['query_params']),
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
            resp = compute.Policy.from_json(
                response.content,
                ignore_unknown_fields=True
            )
            resp = self._interceptor.post_get_iam_policy(resp)
            return resp

    class _List(SnapshotsRestStub):
        def __hash__(self):
            return hash("List")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, str] =  {
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {k: v for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items() if k not in message_dict}

        def __call__(self,
                request: compute.ListSnapshotsRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: float=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> compute.SnapshotList:
            r"""Call the list method over HTTP.

            Args:
                request (~.compute.ListSnapshotsRequest):
                    The request object. A request message for Snapshots.List.
                See the method description for details.

                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.compute.SnapshotList:
                    Contains a list of Snapshot
                resources.

            """

            http_options: List[Dict[str, str]] = [{
                'method': 'get',
                'uri': '/compute/v1/projects/{project}/global/snapshots',
            },
            ]
            request, metadata = self._interceptor.pre_list(request, metadata)
            request_kwargs = compute.ListSnapshotsRequest.to_dict(request)
            transcoded_request = path_template.transcode(
                http_options, **request_kwargs)

            uri = transcoded_request['uri']
            method = transcoded_request['method']

            # Jsonify the query params
            query_params = json.loads(compute.ListSnapshotsRequest.to_json(
                compute.ListSnapshotsRequest(transcoded_request['query_params']),
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
            resp = compute.SnapshotList.from_json(
                response.content,
                ignore_unknown_fields=True
            )
            resp = self._interceptor.post_list(resp)
            return resp

    class _SetIamPolicy(SnapshotsRestStub):
        def __hash__(self):
            return hash("SetIamPolicy")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, str] =  {
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {k: v for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items() if k not in message_dict}

        def __call__(self,
                request: compute.SetIamPolicySnapshotRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: float=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> compute.Policy:
            r"""Call the set iam policy method over HTTP.

            Args:
                request (~.compute.SetIamPolicySnapshotRequest):
                    The request object. A request message for
                Snapshots.SetIamPolicy. See the method
                description for details.

                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.compute.Policy:
                    An Identity and Access Management (IAM) policy, which
                specifies access controls for Google Cloud resources. A
                ``Policy`` is a collection of ``bindings``. A
                ``binding`` binds one or more ``members`` to a single
                ``role``. Members can be user accounts, service
                accounts, Google groups, and domains (such as G Suite).
                A ``role`` is a named list of permissions; each ``role``
                can be an IAM predefined role or a user-created custom
                role. For some types of Google Cloud resources, a
                ``binding`` can also specify a ``condition``, which is a
                logical expression that allows access to a resource only
                if the expression evaluates to ``true``. A condition can
                add constraints based on attributes of the request, the
                resource, or both. To learn which resources support
                conditions in their IAM policies, see the `IAM
                documentation <https://cloud.google.com/iam/help/conditions/resource-policies>`__.
                **JSON example:** { "bindings": [ { "role":
                "roles/resourcemanager.organizationAdmin", "members": [
                "user:mike@example.com", "group:admins@example.com",
                "domain:google.com",
                "serviceAccount:my-project-id@appspot.gserviceaccount.com"
                ] }, { "role":
                "roles/resourcemanager.organizationViewer", "members": [
                "user:eve@example.com" ], "condition": { "title":
                "expirable access", "description": "Does not grant
                access after Sep 2020", "expression": "request.time <
                timestamp('2020-10-01T00:00:00.000Z')", } } ], "etag":
                "BwWWja0YfJA=", "version": 3 } **YAML example:**
                bindings: - members: - user:mike@example.com -
                group:admins@example.com - domain:google.com -
                serviceAccount:my-project-id@appspot.gserviceaccount.com
                role: roles/resourcemanager.organizationAdmin - members:
                - user:eve@example.com role:
                roles/resourcemanager.organizationViewer condition:
                title: expirable access description: Does not grant
                access after Sep 2020 expression: request.time <
                timestamp('2020-10-01T00:00:00.000Z') etag: BwWWja0YfJA=
                version: 3 For a description of IAM and its features,
                see the `IAM
                documentation <https://cloud.google.com/iam/docs/>`__.

            """

            http_options: List[Dict[str, str]] = [{
                'method': 'post',
                'uri': '/compute/v1/projects/{project}/global/snapshots/{resource}/setIamPolicy',
                'body': 'global_set_policy_request_resource',
            },
            ]
            request, metadata = self._interceptor.pre_set_iam_policy(request, metadata)
            request_kwargs = compute.SetIamPolicySnapshotRequest.to_dict(request)
            transcoded_request = path_template.transcode(
                http_options, **request_kwargs)

            # Jsonify the request body
            body = compute.GlobalSetPolicyRequest.to_json(
                compute.GlobalSetPolicyRequest(transcoded_request['body']),                including_default_value_fields=False,
                use_integers_for_enums=False
            )
            uri = transcoded_request['uri']
            method = transcoded_request['method']

            # Jsonify the query params
            query_params = json.loads(compute.SetIamPolicySnapshotRequest.to_json(
                compute.SetIamPolicySnapshotRequest(transcoded_request['query_params']),
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
            resp = compute.Policy.from_json(
                response.content,
                ignore_unknown_fields=True
            )
            resp = self._interceptor.post_set_iam_policy(resp)
            return resp

    class _SetLabels(SnapshotsRestStub):
        def __hash__(self):
            return hash("SetLabels")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, str] =  {
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {k: v for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items() if k not in message_dict}

        def __call__(self,
                request: compute.SetLabelsSnapshotRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: float=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> compute.Operation:
            r"""Call the set labels method over HTTP.

            Args:
                request (~.compute.SetLabelsSnapshotRequest):
                    The request object. A request message for
                Snapshots.SetLabels. See the method
                description for details.

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
                'uri': '/compute/v1/projects/{project}/global/snapshots/{resource}/setLabels',
                'body': 'global_set_labels_request_resource',
            },
            ]
            request, metadata = self._interceptor.pre_set_labels(request, metadata)
            request_kwargs = compute.SetLabelsSnapshotRequest.to_dict(request)
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
            query_params = json.loads(compute.SetLabelsSnapshotRequest.to_json(
                compute.SetLabelsSnapshotRequest(transcoded_request['query_params']),
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

    class _TestIamPermissions(SnapshotsRestStub):
        def __hash__(self):
            return hash("TestIamPermissions")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, str] =  {
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {k: v for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items() if k not in message_dict}

        def __call__(self,
                request: compute.TestIamPermissionsSnapshotRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: float=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> compute.TestPermissionsResponse:
            r"""Call the test iam permissions method over HTTP.

            Args:
                request (~.compute.TestIamPermissionsSnapshotRequest):
                    The request object. A request message for
                Snapshots.TestIamPermissions. See the
                method description for details.

                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.compute.TestPermissionsResponse:

            """

            http_options: List[Dict[str, str]] = [{
                'method': 'post',
                'uri': '/compute/v1/projects/{project}/global/snapshots/{resource}/testIamPermissions',
                'body': 'test_permissions_request_resource',
            },
            ]
            request, metadata = self._interceptor.pre_test_iam_permissions(request, metadata)
            request_kwargs = compute.TestIamPermissionsSnapshotRequest.to_dict(request)
            transcoded_request = path_template.transcode(
                http_options, **request_kwargs)

            # Jsonify the request body
            body = compute.TestPermissionsRequest.to_json(
                compute.TestPermissionsRequest(transcoded_request['body']),                including_default_value_fields=False,
                use_integers_for_enums=False
            )
            uri = transcoded_request['uri']
            method = transcoded_request['method']

            # Jsonify the query params
            query_params = json.loads(compute.TestIamPermissionsSnapshotRequest.to_json(
                compute.TestIamPermissionsSnapshotRequest(transcoded_request['query_params']),
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
            resp = compute.TestPermissionsResponse.from_json(
                response.content,
                ignore_unknown_fields=True
            )
            resp = self._interceptor.post_test_iam_permissions(resp)
            return resp

    @property
    def delete(self) -> Callable[
            [compute.DeleteSnapshotRequest],
            compute.Operation]:
        stub = self._STUBS.get("delete")
        if not stub:
            stub = self._STUBS["delete"] = self._Delete(self._session, self._host, self._interceptor)

        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return stub # type: ignore

    @property
    def get(self) -> Callable[
            [compute.GetSnapshotRequest],
            compute.Snapshot]:
        stub = self._STUBS.get("get")
        if not stub:
            stub = self._STUBS["get"] = self._Get(self._session, self._host, self._interceptor)

        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return stub # type: ignore

    @property
    def get_iam_policy(self) -> Callable[
            [compute.GetIamPolicySnapshotRequest],
            compute.Policy]:
        stub = self._STUBS.get("get_iam_policy")
        if not stub:
            stub = self._STUBS["get_iam_policy"] = self._GetIamPolicy(self._session, self._host, self._interceptor)

        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return stub # type: ignore

    @property
    def list(self) -> Callable[
            [compute.ListSnapshotsRequest],
            compute.SnapshotList]:
        stub = self._STUBS.get("list")
        if not stub:
            stub = self._STUBS["list"] = self._List(self._session, self._host, self._interceptor)

        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return stub # type: ignore

    @property
    def set_iam_policy(self) -> Callable[
            [compute.SetIamPolicySnapshotRequest],
            compute.Policy]:
        stub = self._STUBS.get("set_iam_policy")
        if not stub:
            stub = self._STUBS["set_iam_policy"] = self._SetIamPolicy(self._session, self._host, self._interceptor)

        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return stub # type: ignore

    @property
    def set_labels(self) -> Callable[
            [compute.SetLabelsSnapshotRequest],
            compute.Operation]:
        stub = self._STUBS.get("set_labels")
        if not stub:
            stub = self._STUBS["set_labels"] = self._SetLabels(self._session, self._host, self._interceptor)

        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return stub # type: ignore

    @property
    def test_iam_permissions(self) -> Callable[
            [compute.TestIamPermissionsSnapshotRequest],
            compute.TestPermissionsResponse]:
        stub = self._STUBS.get("test_iam_permissions")
        if not stub:
            stub = self._STUBS["test_iam_permissions"] = self._TestIamPermissions(self._session, self._host, self._interceptor)

        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return stub # type: ignore

    def close(self):
        self._session.close()


__all__=(
    'SnapshotsRestTransport',
)
