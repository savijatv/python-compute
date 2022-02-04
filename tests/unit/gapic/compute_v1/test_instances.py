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
import os
import mock

import grpc
from grpc.experimental import aio
from collections.abc import Iterable
import json
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule

from requests import Response
from requests import Request, PreparedRequest
from requests.sessions import Session

from google.api_core import client_options
from google.api_core import exceptions as core_exceptions
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.api_core import path_template
from google.auth import credentials as ga_credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.compute_v1.services.instances import InstancesClient
from google.cloud.compute_v1.services.instances import pagers
from google.cloud.compute_v1.services.instances import transports
from google.cloud.compute_v1.types import compute
from google.oauth2 import service_account
import google.auth


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return (
        "foo.googleapis.com"
        if ("localhost" in client.DEFAULT_ENDPOINT)
        else client.DEFAULT_ENDPOINT
    )


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert InstancesClient._get_default_mtls_endpoint(None) is None
    assert InstancesClient._get_default_mtls_endpoint(api_endpoint) == api_mtls_endpoint
    assert (
        InstancesClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        InstancesClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        InstancesClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert InstancesClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi


@pytest.mark.parametrize("client_class", [InstancesClient,])
def test_instances_client_from_service_account_info(client_class):
    creds = ga_credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_info"
    ) as factory:
        factory.return_value = creds
        info = {"valid": True}
        client = client_class.from_service_account_info(info)
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == "compute.googleapis.com:443"


@pytest.mark.parametrize(
    "transport_class,transport_name", [(transports.InstancesRestTransport, "rest"),]
)
def test_instances_client_service_account_always_use_jwt(
    transport_class, transport_name
):
    with mock.patch.object(
        service_account.Credentials, "with_always_use_jwt_access", create=True
    ) as use_jwt:
        creds = service_account.Credentials(None, None, None)
        transport = transport_class(credentials=creds, always_use_jwt_access=True)
        use_jwt.assert_called_once_with(True)

    with mock.patch.object(
        service_account.Credentials, "with_always_use_jwt_access", create=True
    ) as use_jwt:
        creds = service_account.Credentials(None, None, None)
        transport = transport_class(credentials=creds, always_use_jwt_access=False)
        use_jwt.assert_not_called()


@pytest.mark.parametrize("client_class", [InstancesClient,])
def test_instances_client_from_service_account_file(client_class):
    creds = ga_credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == "compute.googleapis.com:443"


def test_instances_client_get_transport_class():
    transport = InstancesClient.get_transport_class()
    available_transports = [
        transports.InstancesRestTransport,
    ]
    assert transport in available_transports

    transport = InstancesClient.get_transport_class("rest")
    assert transport == transports.InstancesRestTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [(InstancesClient, transports.InstancesRestTransport, "rest"),],
)
@mock.patch.object(
    InstancesClient, "DEFAULT_ENDPOINT", modify_default_endpoint(InstancesClient)
)
def test_instances_client_client_options(client_class, transport_class, transport_name):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(InstancesClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=ga_credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(InstancesClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(transport=transport_name, client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(transport=transport_name)
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(transport=transport_name)
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError):
            client = client_class(transport=transport_name)

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError):
            client = client_class(transport=transport_name)

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,use_client_cert_env",
    [
        (InstancesClient, transports.InstancesRestTransport, "rest", "true"),
        (InstancesClient, transports.InstancesRestTransport, "rest", "false"),
    ],
)
@mock.patch.object(
    InstancesClient, "DEFAULT_ENDPOINT", modify_default_endpoint(InstancesClient)
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_instances_client_mtls_env_auto(
    client_class, transport_class, transport_name, use_client_cert_env
):
    # This tests the endpoint autoswitch behavior. Endpoint is autoswitched to the default
    # mtls endpoint, if GOOGLE_API_USE_CLIENT_CERTIFICATE is "true" and client cert exists.

    # Check the case client_cert_source is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        options = client_options.ClientOptions(
            client_cert_source=client_cert_source_callback
        )
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(client_options=options, transport=transport_name)

            if use_client_cert_env == "false":
                expected_client_cert_source = None
                expected_host = client.DEFAULT_ENDPOINT
            else:
                expected_client_cert_source = client_cert_source_callback
                expected_host = client.DEFAULT_MTLS_ENDPOINT

            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=expected_host,
                scopes=None,
                client_cert_source_for_mtls=expected_client_cert_source,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
            )

    # Check the case ADC client cert is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=True,
            ):
                with mock.patch(
                    "google.auth.transport.mtls.default_client_cert_source",
                    return_value=client_cert_source_callback,
                ):
                    if use_client_cert_env == "false":
                        expected_host = client.DEFAULT_ENDPOINT
                        expected_client_cert_source = None
                    else:
                        expected_host = client.DEFAULT_MTLS_ENDPOINT
                        expected_client_cert_source = client_cert_source_callback

                    patched.return_value = None
                    client = client_class(transport=transport_name)
                    patched.assert_called_once_with(
                        credentials=None,
                        credentials_file=None,
                        host=expected_host,
                        scopes=None,
                        client_cert_source_for_mtls=expected_client_cert_source,
                        quota_project_id=None,
                        client_info=transports.base.DEFAULT_CLIENT_INFO,
                        always_use_jwt_access=True,
                    )

    # Check the case client_cert_source and ADC client cert are not provided.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=False,
            ):
                patched.return_value = None
                client = client_class(transport=transport_name)
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client.DEFAULT_ENDPOINT,
                    scopes=None,
                    client_cert_source_for_mtls=None,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                    always_use_jwt_access=True,
                )


@pytest.mark.parametrize("client_class", [InstancesClient])
@mock.patch.object(
    InstancesClient, "DEFAULT_ENDPOINT", modify_default_endpoint(InstancesClient)
)
def test_instances_client_get_mtls_endpoint_and_cert_source(client_class):
    mock_client_cert_source = mock.Mock()

    # Test the case GOOGLE_API_USE_CLIENT_CERTIFICATE is "true".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        mock_api_endpoint = "foo"
        options = client_options.ClientOptions(
            client_cert_source=mock_client_cert_source, api_endpoint=mock_api_endpoint
        )
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source(
            options
        )
        assert api_endpoint == mock_api_endpoint
        assert cert_source == mock_client_cert_source

    # Test the case GOOGLE_API_USE_CLIENT_CERTIFICATE is "false".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "false"}):
        mock_client_cert_source = mock.Mock()
        mock_api_endpoint = "foo"
        options = client_options.ClientOptions(
            client_cert_source=mock_client_cert_source, api_endpoint=mock_api_endpoint
        )
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source(
            options
        )
        assert api_endpoint == mock_api_endpoint
        assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
        assert api_endpoint == client_class.DEFAULT_ENDPOINT
        assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
        assert api_endpoint == client_class.DEFAULT_MTLS_ENDPOINT
        assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "auto" and default cert doesn't exist.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        with mock.patch(
            "google.auth.transport.mtls.has_default_client_cert_source",
            return_value=False,
        ):
            api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
            assert api_endpoint == client_class.DEFAULT_ENDPOINT
            assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "auto" and default cert exists.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        with mock.patch(
            "google.auth.transport.mtls.has_default_client_cert_source",
            return_value=True,
        ):
            with mock.patch(
                "google.auth.transport.mtls.default_client_cert_source",
                return_value=mock_client_cert_source,
            ):
                (
                    api_endpoint,
                    cert_source,
                ) = client_class.get_mtls_endpoint_and_cert_source()
                assert api_endpoint == client_class.DEFAULT_MTLS_ENDPOINT
                assert cert_source == mock_client_cert_source


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [(InstancesClient, transports.InstancesRestTransport, "rest"),],
)
def test_instances_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(scopes=["1", "2"],)
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,grpc_helpers",
    [(InstancesClient, transports.InstancesRestTransport, "rest", None),],
)
def test_instances_client_client_options_credentials_file(
    client_class, transport_class, transport_name, grpc_helpers
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")

    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
        )


@pytest.mark.parametrize(
    "request_type", [compute.AddAccessConfigInstanceRequest, dict,]
)
def test_add_access_config_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["access_config_resource"] = {
        "external_ipv6": "external_ipv6_value",
        "external_ipv6_prefix_length": 2837,
        "kind": "kind_value",
        "name": "name_value",
        "nat_i_p": "nat_i_p_value",
        "network_tier": "network_tier_value",
        "public_ptr_domain_name": "public_ptr_domain_name_value",
        "set_public_ptr": True,
        "type_": "type__value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.add_access_config_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_add_access_config_unary_rest_required_fields(
    request_type=compute.AddAccessConfigInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["network_interface"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped
    assert "networkInterface" not in jsonified_request

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).add_access_config._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "networkInterface" in jsonified_request
    assert jsonified_request["networkInterface"] == request_init["network_interface"]

    jsonified_request["instance"] = "instance_value"
    jsonified_request["networkInterface"] = "network_interface_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).add_access_config._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("network_interface", "request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "networkInterface" in jsonified_request
    assert jsonified_request["networkInterface"] == "network_interface_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.add_access_config_unary(request)

            expected_params = [
                ("networkInterface", "",),
            ]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_add_access_config_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.add_access_config._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("networkInterface", "requestId",))
        & set(
            ("accessConfigResource", "instance", "networkInterface", "project", "zone",)
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_add_access_config_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_add_access_config"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_add_access_config"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.AddAccessConfigInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.add_access_config_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_add_access_config_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.AddAccessConfigInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["access_config_resource"] = {
        "external_ipv6": "external_ipv6_value",
        "external_ipv6_prefix_length": 2837,
        "kind": "kind_value",
        "name": "name_value",
        "nat_i_p": "nat_i_p_value",
        "network_tier": "network_tier_value",
        "public_ptr_domain_name": "public_ptr_domain_name_value",
        "set_public_ptr": True,
        "type_": "type__value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.add_access_config_unary(request)


def test_add_access_config_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            network_interface="network_interface_value",
            access_config_resource=compute.AccessConfig(
                external_ipv6="external_ipv6_value"
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.add_access_config_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/addAccessConfig"
            % client.transport._host,
            args[1],
        )


def test_add_access_config_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.add_access_config_unary(
            compute.AddAccessConfigInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            network_interface="network_interface_value",
            access_config_resource=compute.AccessConfig(
                external_ipv6="external_ipv6_value"
            ),
        )


def test_add_access_config_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.AddResourcePoliciesInstanceRequest, dict,]
)
def test_add_resource_policies_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_add_resource_policies_request_resource"] = {
        "resource_policies": ["resource_policies_value_1", "resource_policies_value_2"]
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.add_resource_policies_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_add_resource_policies_unary_rest_required_fields(
    request_type=compute.AddResourcePoliciesInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).add_resource_policies._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).add_resource_policies._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.add_resource_policies_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_add_resource_policies_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.add_resource_policies._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",))
        & set(
            (
                "instance",
                "instancesAddResourcePoliciesRequestResource",
                "project",
                "zone",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_add_resource_policies_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_add_resource_policies"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_add_resource_policies"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.AddResourcePoliciesInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.add_resource_policies_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_add_resource_policies_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.AddResourcePoliciesInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_add_resource_policies_request_resource"] = {
        "resource_policies": ["resource_policies_value_1", "resource_policies_value_2"]
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.add_resource_policies_unary(request)


def test_add_resource_policies_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_add_resource_policies_request_resource=compute.InstancesAddResourcePoliciesRequest(
                resource_policies=["resource_policies_value"]
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.add_resource_policies_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/addResourcePolicies"
            % client.transport._host,
            args[1],
        )


def test_add_resource_policies_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.add_resource_policies_unary(
            compute.AddResourcePoliciesInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_add_resource_policies_request_resource=compute.InstancesAddResourcePoliciesRequest(
                resource_policies=["resource_policies_value"]
            ),
        )


def test_add_resource_policies_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.AggregatedListInstancesRequest, dict,]
)
def test_aggregated_list_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.InstanceAggregatedList(
            id="id_value",
            kind="kind_value",
            next_page_token="next_page_token_value",
            self_link="self_link_value",
            unreachables=["unreachables_value"],
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.InstanceAggregatedList.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.aggregated_list(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.AggregatedListPager)
    assert response.id == "id_value"
    assert response.kind == "kind_value"
    assert response.next_page_token == "next_page_token_value"
    assert response.self_link == "self_link_value"
    assert response.unreachables == ["unreachables_value"]


def test_aggregated_list_rest_required_fields(
    request_type=compute.AggregatedListInstancesRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["project"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).aggregated_list._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["project"] = "project_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).aggregated_list._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "filter",
            "include_all_scopes",
            "max_results",
            "order_by",
            "page_token",
            "return_partial_success",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.InstanceAggregatedList()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.InstanceAggregatedList.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.aggregated_list(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_aggregated_list_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.aggregated_list._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "filter",
                "includeAllScopes",
                "maxResults",
                "orderBy",
                "pageToken",
                "returnPartialSuccess",
            )
        )
        & set(("project",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_aggregated_list_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_aggregated_list"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_aggregated_list"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.InstanceAggregatedList.to_json(
            compute.InstanceAggregatedList()
        )

        request = compute.AggregatedListInstancesRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.InstanceAggregatedList

        client.aggregated_list(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_aggregated_list_rest_bad_request(
    transport: str = "rest", request_type=compute.AggregatedListInstancesRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.aggregated_list(request)


def test_aggregated_list_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.InstanceAggregatedList()

        # get arguments that satisfy an http rule for this method
        sample_request = {"project": "sample1"}

        # get truthy value for each flattened field
        mock_args = dict(project="project_value",)
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.InstanceAggregatedList.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.aggregated_list(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/aggregated/instances"
            % client.transport._host,
            args[1],
        )


def test_aggregated_list_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.aggregated_list(
            compute.AggregatedListInstancesRequest(), project="project_value",
        )


def test_aggregated_list_rest_pager(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            compute.InstanceAggregatedList(
                items={
                    "a": compute.InstancesScopedList(),
                    "b": compute.InstancesScopedList(),
                    "c": compute.InstancesScopedList(),
                },
                next_page_token="abc",
            ),
            compute.InstanceAggregatedList(items={}, next_page_token="def",),
            compute.InstanceAggregatedList(
                items={"g": compute.InstancesScopedList(),}, next_page_token="ghi",
            ),
            compute.InstanceAggregatedList(
                items={
                    "h": compute.InstancesScopedList(),
                    "i": compute.InstancesScopedList(),
                },
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(compute.InstanceAggregatedList.to_json(x) for x in response)
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {"project": "sample1"}

        pager = client.aggregated_list(request=sample_request)

        assert isinstance(pager.get("a"), compute.InstancesScopedList)
        assert pager.get("h") is None

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, tuple) for i in results)
        for result in results:
            assert isinstance(result, tuple)
            assert tuple(type(t) for t in result) == (str, compute.InstancesScopedList)

        assert pager.get("a") is None
        assert isinstance(pager.get("h"), compute.InstancesScopedList)

        pages = list(client.aggregated_list(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize("request_type", [compute.AttachDiskInstanceRequest, dict,])
def test_attach_disk_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["attached_disk_resource"] = {
        "auto_delete": True,
        "boot": True,
        "device_name": "device_name_value",
        "disk_encryption_key": {
            "kms_key_name": "kms_key_name_value",
            "kms_key_service_account": "kms_key_service_account_value",
            "raw_key": "raw_key_value",
            "rsa_encrypted_key": "rsa_encrypted_key_value",
            "sha256": "sha256_value",
        },
        "disk_size_gb": 1261,
        "guest_os_features": [{"type_": "type__value"}],
        "index": 536,
        "initialize_params": {
            "description": "description_value",
            "disk_name": "disk_name_value",
            "disk_size_gb": 1261,
            "disk_type": "disk_type_value",
            "labels": {},
            "on_update_action": "on_update_action_value",
            "provisioned_iops": 1740,
            "resource_policies": [
                "resource_policies_value_1",
                "resource_policies_value_2",
            ],
            "source_image": "source_image_value",
            "source_image_encryption_key": {
                "kms_key_name": "kms_key_name_value",
                "kms_key_service_account": "kms_key_service_account_value",
                "raw_key": "raw_key_value",
                "rsa_encrypted_key": "rsa_encrypted_key_value",
                "sha256": "sha256_value",
            },
            "source_snapshot": "source_snapshot_value",
            "source_snapshot_encryption_key": {
                "kms_key_name": "kms_key_name_value",
                "kms_key_service_account": "kms_key_service_account_value",
                "raw_key": "raw_key_value",
                "rsa_encrypted_key": "rsa_encrypted_key_value",
                "sha256": "sha256_value",
            },
        },
        "interface": "interface_value",
        "kind": "kind_value",
        "licenses": ["licenses_value_1", "licenses_value_2"],
        "mode": "mode_value",
        "shielded_instance_initial_state": {
            "dbs": [{"content": "content_value", "file_type": "file_type_value"}],
            "dbxs": [{"content": "content_value", "file_type": "file_type_value"}],
            "keks": [{"content": "content_value", "file_type": "file_type_value"}],
            "pk": {"content": "content_value", "file_type": "file_type_value"},
        },
        "source": "source_value",
        "type_": "type__value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.attach_disk_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_attach_disk_unary_rest_required_fields(
    request_type=compute.AttachDiskInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).attach_disk._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).attach_disk._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("force_attach", "request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.attach_disk_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_attach_disk_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.attach_disk._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("forceAttach", "requestId",))
        & set(("attachedDiskResource", "instance", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_attach_disk_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_attach_disk"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_attach_disk"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.AttachDiskInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.attach_disk_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_attach_disk_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.AttachDiskInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["attached_disk_resource"] = {
        "auto_delete": True,
        "boot": True,
        "device_name": "device_name_value",
        "disk_encryption_key": {
            "kms_key_name": "kms_key_name_value",
            "kms_key_service_account": "kms_key_service_account_value",
            "raw_key": "raw_key_value",
            "rsa_encrypted_key": "rsa_encrypted_key_value",
            "sha256": "sha256_value",
        },
        "disk_size_gb": 1261,
        "guest_os_features": [{"type_": "type__value"}],
        "index": 536,
        "initialize_params": {
            "description": "description_value",
            "disk_name": "disk_name_value",
            "disk_size_gb": 1261,
            "disk_type": "disk_type_value",
            "labels": {},
            "on_update_action": "on_update_action_value",
            "provisioned_iops": 1740,
            "resource_policies": [
                "resource_policies_value_1",
                "resource_policies_value_2",
            ],
            "source_image": "source_image_value",
            "source_image_encryption_key": {
                "kms_key_name": "kms_key_name_value",
                "kms_key_service_account": "kms_key_service_account_value",
                "raw_key": "raw_key_value",
                "rsa_encrypted_key": "rsa_encrypted_key_value",
                "sha256": "sha256_value",
            },
            "source_snapshot": "source_snapshot_value",
            "source_snapshot_encryption_key": {
                "kms_key_name": "kms_key_name_value",
                "kms_key_service_account": "kms_key_service_account_value",
                "raw_key": "raw_key_value",
                "rsa_encrypted_key": "rsa_encrypted_key_value",
                "sha256": "sha256_value",
            },
        },
        "interface": "interface_value",
        "kind": "kind_value",
        "licenses": ["licenses_value_1", "licenses_value_2"],
        "mode": "mode_value",
        "shielded_instance_initial_state": {
            "dbs": [{"content": "content_value", "file_type": "file_type_value"}],
            "dbxs": [{"content": "content_value", "file_type": "file_type_value"}],
            "keks": [{"content": "content_value", "file_type": "file_type_value"}],
            "pk": {"content": "content_value", "file_type": "file_type_value"},
        },
        "source": "source_value",
        "type_": "type__value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.attach_disk_unary(request)


def test_attach_disk_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            attached_disk_resource=compute.AttachedDisk(auto_delete=True),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.attach_disk_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/attachDisk"
            % client.transport._host,
            args[1],
        )


def test_attach_disk_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.attach_disk_unary(
            compute.AttachDiskInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            attached_disk_resource=compute.AttachedDisk(auto_delete=True),
        )


def test_attach_disk_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.BulkInsertInstanceRequest, dict,])
def test_bulk_insert_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2"}
    request_init["bulk_insert_instance_resource_resource"] = {
        "count": 553,
        "instance_properties": {
            "advanced_machine_features": {
                "enable_nested_virtualization": True,
                "threads_per_core": 1689,
            },
            "can_ip_forward": True,
            "confidential_instance_config": {"enable_confidential_compute": True},
            "description": "description_value",
            "disks": [
                {
                    "auto_delete": True,
                    "boot": True,
                    "device_name": "device_name_value",
                    "disk_encryption_key": {
                        "kms_key_name": "kms_key_name_value",
                        "kms_key_service_account": "kms_key_service_account_value",
                        "raw_key": "raw_key_value",
                        "rsa_encrypted_key": "rsa_encrypted_key_value",
                        "sha256": "sha256_value",
                    },
                    "disk_size_gb": 1261,
                    "guest_os_features": [{"type_": "type__value"}],
                    "index": 536,
                    "initialize_params": {
                        "description": "description_value",
                        "disk_name": "disk_name_value",
                        "disk_size_gb": 1261,
                        "disk_type": "disk_type_value",
                        "labels": {},
                        "on_update_action": "on_update_action_value",
                        "provisioned_iops": 1740,
                        "resource_policies": [
                            "resource_policies_value_1",
                            "resource_policies_value_2",
                        ],
                        "source_image": "source_image_value",
                        "source_image_encryption_key": {
                            "kms_key_name": "kms_key_name_value",
                            "kms_key_service_account": "kms_key_service_account_value",
                            "raw_key": "raw_key_value",
                            "rsa_encrypted_key": "rsa_encrypted_key_value",
                            "sha256": "sha256_value",
                        },
                        "source_snapshot": "source_snapshot_value",
                        "source_snapshot_encryption_key": {
                            "kms_key_name": "kms_key_name_value",
                            "kms_key_service_account": "kms_key_service_account_value",
                            "raw_key": "raw_key_value",
                            "rsa_encrypted_key": "rsa_encrypted_key_value",
                            "sha256": "sha256_value",
                        },
                    },
                    "interface": "interface_value",
                    "kind": "kind_value",
                    "licenses": ["licenses_value_1", "licenses_value_2"],
                    "mode": "mode_value",
                    "shielded_instance_initial_state": {
                        "dbs": [
                            {"content": "content_value", "file_type": "file_type_value"}
                        ],
                        "dbxs": [
                            {"content": "content_value", "file_type": "file_type_value"}
                        ],
                        "keks": [
                            {"content": "content_value", "file_type": "file_type_value"}
                        ],
                        "pk": {
                            "content": "content_value",
                            "file_type": "file_type_value",
                        },
                    },
                    "source": "source_value",
                    "type_": "type__value",
                }
            ],
            "guest_accelerators": [
                {
                    "accelerator_count": 1805,
                    "accelerator_type": "accelerator_type_value",
                }
            ],
            "labels": {},
            "machine_type": "machine_type_value",
            "metadata": {
                "fingerprint": "fingerprint_value",
                "items": [{"key": "key_value", "value": "value_value"}],
                "kind": "kind_value",
            },
            "min_cpu_platform": "min_cpu_platform_value",
            "network_interfaces": [
                {
                    "access_configs": [
                        {
                            "external_ipv6": "external_ipv6_value",
                            "external_ipv6_prefix_length": 2837,
                            "kind": "kind_value",
                            "name": "name_value",
                            "nat_i_p": "nat_i_p_value",
                            "network_tier": "network_tier_value",
                            "public_ptr_domain_name": "public_ptr_domain_name_value",
                            "set_public_ptr": True,
                            "type_": "type__value",
                        }
                    ],
                    "alias_ip_ranges": [
                        {
                            "ip_cidr_range": "ip_cidr_range_value",
                            "subnetwork_range_name": "subnetwork_range_name_value",
                        }
                    ],
                    "fingerprint": "fingerprint_value",
                    "ipv6_access_configs": [
                        {
                            "external_ipv6": "external_ipv6_value",
                            "external_ipv6_prefix_length": 2837,
                            "kind": "kind_value",
                            "name": "name_value",
                            "nat_i_p": "nat_i_p_value",
                            "network_tier": "network_tier_value",
                            "public_ptr_domain_name": "public_ptr_domain_name_value",
                            "set_public_ptr": True,
                            "type_": "type__value",
                        }
                    ],
                    "ipv6_access_type": "ipv6_access_type_value",
                    "ipv6_address": "ipv6_address_value",
                    "kind": "kind_value",
                    "name": "name_value",
                    "network": "network_value",
                    "network_i_p": "network_i_p_value",
                    "nic_type": "nic_type_value",
                    "queue_count": 1197,
                    "stack_type": "stack_type_value",
                    "subnetwork": "subnetwork_value",
                }
            ],
            "private_ipv6_google_access": "private_ipv6_google_access_value",
            "reservation_affinity": {
                "consume_reservation_type": "consume_reservation_type_value",
                "key": "key_value",
                "values": ["values_value_1", "values_value_2"],
            },
            "resource_policies": [
                "resource_policies_value_1",
                "resource_policies_value_2",
            ],
            "scheduling": {
                "automatic_restart": True,
                "location_hint": "location_hint_value",
                "min_node_cpus": 1379,
                "node_affinities": [
                    {
                        "key": "key_value",
                        "operator": "operator_value",
                        "values": ["values_value_1", "values_value_2"],
                    }
                ],
                "on_host_maintenance": "on_host_maintenance_value",
                "preemptible": True,
            },
            "service_accounts": [
                {"email": "email_value", "scopes": ["scopes_value_1", "scopes_value_2"]}
            ],
            "shielded_instance_config": {
                "enable_integrity_monitoring": True,
                "enable_secure_boot": True,
                "enable_vtpm": True,
            },
            "tags": {
                "fingerprint": "fingerprint_value",
                "items": ["items_value_1", "items_value_2"],
            },
        },
        "location_policy": {"locations": {}},
        "min_count": 972,
        "name_pattern": "name_pattern_value",
        "per_instance_properties": {},
        "source_instance_template": "source_instance_template_value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.bulk_insert_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_bulk_insert_unary_rest_required_fields(
    request_type=compute.BulkInsertInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).bulk_insert._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).bulk_insert._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.bulk_insert_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_bulk_insert_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.bulk_insert._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",))
        & set(("bulkInsertInstanceResourceResource", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_bulk_insert_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_bulk_insert"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_bulk_insert"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.BulkInsertInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.bulk_insert_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_bulk_insert_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.BulkInsertInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2"}
    request_init["bulk_insert_instance_resource_resource"] = {
        "count": 553,
        "instance_properties": {
            "advanced_machine_features": {
                "enable_nested_virtualization": True,
                "threads_per_core": 1689,
            },
            "can_ip_forward": True,
            "confidential_instance_config": {"enable_confidential_compute": True},
            "description": "description_value",
            "disks": [
                {
                    "auto_delete": True,
                    "boot": True,
                    "device_name": "device_name_value",
                    "disk_encryption_key": {
                        "kms_key_name": "kms_key_name_value",
                        "kms_key_service_account": "kms_key_service_account_value",
                        "raw_key": "raw_key_value",
                        "rsa_encrypted_key": "rsa_encrypted_key_value",
                        "sha256": "sha256_value",
                    },
                    "disk_size_gb": 1261,
                    "guest_os_features": [{"type_": "type__value"}],
                    "index": 536,
                    "initialize_params": {
                        "description": "description_value",
                        "disk_name": "disk_name_value",
                        "disk_size_gb": 1261,
                        "disk_type": "disk_type_value",
                        "labels": {},
                        "on_update_action": "on_update_action_value",
                        "provisioned_iops": 1740,
                        "resource_policies": [
                            "resource_policies_value_1",
                            "resource_policies_value_2",
                        ],
                        "source_image": "source_image_value",
                        "source_image_encryption_key": {
                            "kms_key_name": "kms_key_name_value",
                            "kms_key_service_account": "kms_key_service_account_value",
                            "raw_key": "raw_key_value",
                            "rsa_encrypted_key": "rsa_encrypted_key_value",
                            "sha256": "sha256_value",
                        },
                        "source_snapshot": "source_snapshot_value",
                        "source_snapshot_encryption_key": {
                            "kms_key_name": "kms_key_name_value",
                            "kms_key_service_account": "kms_key_service_account_value",
                            "raw_key": "raw_key_value",
                            "rsa_encrypted_key": "rsa_encrypted_key_value",
                            "sha256": "sha256_value",
                        },
                    },
                    "interface": "interface_value",
                    "kind": "kind_value",
                    "licenses": ["licenses_value_1", "licenses_value_2"],
                    "mode": "mode_value",
                    "shielded_instance_initial_state": {
                        "dbs": [
                            {"content": "content_value", "file_type": "file_type_value"}
                        ],
                        "dbxs": [
                            {"content": "content_value", "file_type": "file_type_value"}
                        ],
                        "keks": [
                            {"content": "content_value", "file_type": "file_type_value"}
                        ],
                        "pk": {
                            "content": "content_value",
                            "file_type": "file_type_value",
                        },
                    },
                    "source": "source_value",
                    "type_": "type__value",
                }
            ],
            "guest_accelerators": [
                {
                    "accelerator_count": 1805,
                    "accelerator_type": "accelerator_type_value",
                }
            ],
            "labels": {},
            "machine_type": "machine_type_value",
            "metadata": {
                "fingerprint": "fingerprint_value",
                "items": [{"key": "key_value", "value": "value_value"}],
                "kind": "kind_value",
            },
            "min_cpu_platform": "min_cpu_platform_value",
            "network_interfaces": [
                {
                    "access_configs": [
                        {
                            "external_ipv6": "external_ipv6_value",
                            "external_ipv6_prefix_length": 2837,
                            "kind": "kind_value",
                            "name": "name_value",
                            "nat_i_p": "nat_i_p_value",
                            "network_tier": "network_tier_value",
                            "public_ptr_domain_name": "public_ptr_domain_name_value",
                            "set_public_ptr": True,
                            "type_": "type__value",
                        }
                    ],
                    "alias_ip_ranges": [
                        {
                            "ip_cidr_range": "ip_cidr_range_value",
                            "subnetwork_range_name": "subnetwork_range_name_value",
                        }
                    ],
                    "fingerprint": "fingerprint_value",
                    "ipv6_access_configs": [
                        {
                            "external_ipv6": "external_ipv6_value",
                            "external_ipv6_prefix_length": 2837,
                            "kind": "kind_value",
                            "name": "name_value",
                            "nat_i_p": "nat_i_p_value",
                            "network_tier": "network_tier_value",
                            "public_ptr_domain_name": "public_ptr_domain_name_value",
                            "set_public_ptr": True,
                            "type_": "type__value",
                        }
                    ],
                    "ipv6_access_type": "ipv6_access_type_value",
                    "ipv6_address": "ipv6_address_value",
                    "kind": "kind_value",
                    "name": "name_value",
                    "network": "network_value",
                    "network_i_p": "network_i_p_value",
                    "nic_type": "nic_type_value",
                    "queue_count": 1197,
                    "stack_type": "stack_type_value",
                    "subnetwork": "subnetwork_value",
                }
            ],
            "private_ipv6_google_access": "private_ipv6_google_access_value",
            "reservation_affinity": {
                "consume_reservation_type": "consume_reservation_type_value",
                "key": "key_value",
                "values": ["values_value_1", "values_value_2"],
            },
            "resource_policies": [
                "resource_policies_value_1",
                "resource_policies_value_2",
            ],
            "scheduling": {
                "automatic_restart": True,
                "location_hint": "location_hint_value",
                "min_node_cpus": 1379,
                "node_affinities": [
                    {
                        "key": "key_value",
                        "operator": "operator_value",
                        "values": ["values_value_1", "values_value_2"],
                    }
                ],
                "on_host_maintenance": "on_host_maintenance_value",
                "preemptible": True,
            },
            "service_accounts": [
                {"email": "email_value", "scopes": ["scopes_value_1", "scopes_value_2"]}
            ],
            "shielded_instance_config": {
                "enable_integrity_monitoring": True,
                "enable_secure_boot": True,
                "enable_vtpm": True,
            },
            "tags": {
                "fingerprint": "fingerprint_value",
                "items": ["items_value_1", "items_value_2"],
            },
        },
        "location_policy": {"locations": {}},
        "min_count": 972,
        "name_pattern": "name_pattern_value",
        "per_instance_properties": {},
        "source_instance_template": "source_instance_template_value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.bulk_insert_unary(request)


def test_bulk_insert_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {"project": "sample1", "zone": "sample2"}

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            bulk_insert_instance_resource_resource=compute.BulkInsertInstanceResource(
                count=553
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.bulk_insert_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/bulkInsert"
            % client.transport._host,
            args[1],
        )


def test_bulk_insert_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.bulk_insert_unary(
            compute.BulkInsertInstanceRequest(),
            project="project_value",
            zone="zone_value",
            bulk_insert_instance_resource_resource=compute.BulkInsertInstanceResource(
                count=553
            ),
        )


def test_bulk_insert_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.DeleteInstanceRequest, dict,])
def test_delete_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.delete_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_delete_unary_rest_required_fields(request_type=compute.DeleteInstanceRequest):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "delete",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.delete_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.delete._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",)) & set(("instance", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_delete"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_delete"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.DeleteInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.delete_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_delete_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.DeleteInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.delete_unary(request)


def test_delete_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value", zone="zone_value", instance="instance_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.delete_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}"
            % client.transport._host,
            args[1],
        )


def test_delete_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_unary(
            compute.DeleteInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
        )


def test_delete_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.DeleteAccessConfigInstanceRequest, dict,]
)
def test_delete_access_config_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.delete_access_config_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_delete_access_config_unary_rest_required_fields(
    request_type=compute.DeleteAccessConfigInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["access_config"] = ""
    request_init["instance"] = ""
    request_init["network_interface"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped
    assert "accessConfig" not in jsonified_request
    assert "networkInterface" not in jsonified_request

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_access_config._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "accessConfig" in jsonified_request
    assert jsonified_request["accessConfig"] == request_init["access_config"]
    assert "networkInterface" in jsonified_request
    assert jsonified_request["networkInterface"] == request_init["network_interface"]

    jsonified_request["accessConfig"] = "access_config_value"
    jsonified_request["instance"] = "instance_value"
    jsonified_request["networkInterface"] = "network_interface_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_access_config._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        ("access_config", "network_interface", "request_id",)
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "accessConfig" in jsonified_request
    assert jsonified_request["accessConfig"] == "access_config_value"
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "networkInterface" in jsonified_request
    assert jsonified_request["networkInterface"] == "network_interface_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.delete_access_config_unary(request)

            expected_params = [
                ("accessConfig", "",),
                ("networkInterface", "",),
            ]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_access_config_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.delete_access_config._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("accessConfig", "networkInterface", "requestId",))
        & set(("accessConfig", "instance", "networkInterface", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_access_config_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_delete_access_config"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_delete_access_config"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.DeleteAccessConfigInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.delete_access_config_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_delete_access_config_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.DeleteAccessConfigInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.delete_access_config_unary(request)


def test_delete_access_config_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            access_config="access_config_value",
            network_interface="network_interface_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.delete_access_config_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/deleteAccessConfig"
            % client.transport._host,
            args[1],
        )


def test_delete_access_config_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_access_config_unary(
            compute.DeleteAccessConfigInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            access_config="access_config_value",
            network_interface="network_interface_value",
        )


def test_delete_access_config_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.DetachDiskInstanceRequest, dict,])
def test_detach_disk_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.detach_disk_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_detach_disk_unary_rest_required_fields(
    request_type=compute.DetachDiskInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["device_name"] = ""
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped
    assert "deviceName" not in jsonified_request

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).detach_disk._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "deviceName" in jsonified_request
    assert jsonified_request["deviceName"] == request_init["device_name"]

    jsonified_request["deviceName"] = "device_name_value"
    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).detach_disk._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("device_name", "request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "deviceName" in jsonified_request
    assert jsonified_request["deviceName"] == "device_name_value"
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.detach_disk_unary(request)

            expected_params = [
                ("deviceName", "",),
            ]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_detach_disk_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.detach_disk._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("deviceName", "requestId",))
        & set(("deviceName", "instance", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_detach_disk_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_detach_disk"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_detach_disk"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.DetachDiskInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.detach_disk_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_detach_disk_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.DetachDiskInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.detach_disk_unary(request)


def test_detach_disk_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            device_name="device_name_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.detach_disk_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/detachDisk"
            % client.transport._host,
            args[1],
        )


def test_detach_disk_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.detach_disk_unary(
            compute.DetachDiskInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            device_name="device_name_value",
        )


def test_detach_disk_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.GetInstanceRequest, dict,])
def test_get_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Instance(
            can_ip_forward=True,
            cpu_platform="cpu_platform_value",
            creation_timestamp="creation_timestamp_value",
            deletion_protection=True,
            description="description_value",
            fingerprint="fingerprint_value",
            hostname="hostname_value",
            id=205,
            kind="kind_value",
            label_fingerprint="label_fingerprint_value",
            last_start_timestamp="last_start_timestamp_value",
            last_stop_timestamp="last_stop_timestamp_value",
            last_suspended_timestamp="last_suspended_timestamp_value",
            machine_type="machine_type_value",
            min_cpu_platform="min_cpu_platform_value",
            name="name_value",
            private_ipv6_google_access="private_ipv6_google_access_value",
            resource_policies=["resource_policies_value"],
            satisfies_pzs=True,
            self_link="self_link_value",
            start_restricted=True,
            status="status_value",
            status_message="status_message_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Instance.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Instance)
    assert response.can_ip_forward is True
    assert response.cpu_platform == "cpu_platform_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.deletion_protection is True
    assert response.description == "description_value"
    assert response.fingerprint == "fingerprint_value"
    assert response.hostname == "hostname_value"
    assert response.id == 205
    assert response.kind == "kind_value"
    assert response.label_fingerprint == "label_fingerprint_value"
    assert response.last_start_timestamp == "last_start_timestamp_value"
    assert response.last_stop_timestamp == "last_stop_timestamp_value"
    assert response.last_suspended_timestamp == "last_suspended_timestamp_value"
    assert response.machine_type == "machine_type_value"
    assert response.min_cpu_platform == "min_cpu_platform_value"
    assert response.name == "name_value"
    assert response.private_ipv6_google_access == "private_ipv6_google_access_value"
    assert response.resource_policies == ["resource_policies_value"]
    assert response.satisfies_pzs is True
    assert response.self_link == "self_link_value"
    assert response.start_restricted is True
    assert response.status == "status_value"
    assert response.status_message == "status_message_value"
    assert response.zone == "zone_value"


def test_get_rest_required_fields(request_type=compute.GetInstanceRequest):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Instance()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Instance.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("instance", "project", "zone",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_get"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_get"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Instance.to_json(compute.Instance())

        request = compute.GetInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Instance

        client.get(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()


def test_get_rest_bad_request(
    transport: str = "rest", request_type=compute.GetInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get(request)


def test_get_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Instance()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value", zone="zone_value", instance="instance_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Instance.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}"
            % client.transport._host,
            args[1],
        )


def test_get_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get(
            compute.GetInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
        )


def test_get_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.GetEffectiveFirewallsInstanceRequest, dict,]
)
def test_get_effective_firewalls_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.InstancesGetEffectiveFirewallsResponse()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.InstancesGetEffectiveFirewallsResponse.to_json(
            return_value
        )
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_effective_firewalls(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.InstancesGetEffectiveFirewallsResponse)


def test_get_effective_firewalls_rest_required_fields(
    request_type=compute.GetEffectiveFirewallsInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["network_interface"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped
    assert "networkInterface" not in jsonified_request

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_effective_firewalls._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "networkInterface" in jsonified_request
    assert jsonified_request["networkInterface"] == request_init["network_interface"]

    jsonified_request["instance"] = "instance_value"
    jsonified_request["networkInterface"] = "network_interface_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_effective_firewalls._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("network_interface",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "networkInterface" in jsonified_request
    assert jsonified_request["networkInterface"] == "network_interface_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.InstancesGetEffectiveFirewallsResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.InstancesGetEffectiveFirewallsResponse.to_json(
                return_value
            )
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_effective_firewalls(request)

            expected_params = [
                ("networkInterface", "",),
            ]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_effective_firewalls_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_effective_firewalls._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("networkInterface",))
        & set(("instance", "networkInterface", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_effective_firewalls_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_get_effective_firewalls"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_get_effective_firewalls"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.InstancesGetEffectiveFirewallsResponse.to_json(
            compute.InstancesGetEffectiveFirewallsResponse()
        )

        request = compute.GetEffectiveFirewallsInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.InstancesGetEffectiveFirewallsResponse

        client.get_effective_firewalls(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_effective_firewalls_rest_bad_request(
    transport: str = "rest", request_type=compute.GetEffectiveFirewallsInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_effective_firewalls(request)


def test_get_effective_firewalls_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.InstancesGetEffectiveFirewallsResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            network_interface="network_interface_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.InstancesGetEffectiveFirewallsResponse.to_json(
            return_value
        )

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get_effective_firewalls(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/getEffectiveFirewalls"
            % client.transport._host,
            args[1],
        )


def test_get_effective_firewalls_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_effective_firewalls(
            compute.GetEffectiveFirewallsInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            network_interface="network_interface_value",
        )


def test_get_effective_firewalls_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.GetGuestAttributesInstanceRequest, dict,]
)
def test_get_guest_attributes_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.GuestAttributes(
            kind="kind_value",
            query_path="query_path_value",
            self_link="self_link_value",
            variable_key="variable_key_value",
            variable_value="variable_value_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.GuestAttributes.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_guest_attributes(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.GuestAttributes)
    assert response.kind == "kind_value"
    assert response.query_path == "query_path_value"
    assert response.self_link == "self_link_value"
    assert response.variable_key == "variable_key_value"
    assert response.variable_value == "variable_value_value"


def test_get_guest_attributes_rest_required_fields(
    request_type=compute.GetGuestAttributesInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_guest_attributes._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_guest_attributes._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("query_path", "variable_key",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.GuestAttributes()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.GuestAttributes.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_guest_attributes(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_guest_attributes_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_guest_attributes._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("queryPath", "variableKey",)) & set(("instance", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_guest_attributes_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_get_guest_attributes"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_get_guest_attributes"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.GuestAttributes.to_json(
            compute.GuestAttributes()
        )

        request = compute.GetGuestAttributesInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.GuestAttributes

        client.get_guest_attributes(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_guest_attributes_rest_bad_request(
    transport: str = "rest", request_type=compute.GetGuestAttributesInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_guest_attributes(request)


def test_get_guest_attributes_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.GuestAttributes()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value", zone="zone_value", instance="instance_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.GuestAttributes.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get_guest_attributes(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/getGuestAttributes"
            % client.transport._host,
            args[1],
        )


def test_get_guest_attributes_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_guest_attributes(
            compute.GetGuestAttributesInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
        )


def test_get_guest_attributes_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.GetIamPolicyInstanceRequest, dict,])
def test_get_iam_policy_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "resource": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Policy(etag="etag_value", iam_owned=True, version=774,)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Policy.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_iam_policy(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Policy)
    assert response.etag == "etag_value"
    assert response.iam_owned is True
    assert response.version == 774


def test_get_iam_policy_rest_required_fields(
    request_type=compute.GetIamPolicyInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["project"] = ""
    request_init["resource"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_iam_policy._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["project"] = "project_value"
    jsonified_request["resource"] = "resource_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_iam_policy._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("options_requested_policy_version",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "resource" in jsonified_request
    assert jsonified_request["resource"] == "resource_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Policy()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Policy.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_iam_policy(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_iam_policy_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_iam_policy._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("optionsRequestedPolicyVersion",)) & set(("project", "resource", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_iam_policy_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_get_iam_policy"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_get_iam_policy"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Policy.to_json(compute.Policy())

        request = compute.GetIamPolicyInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Policy

        client.get_iam_policy(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_iam_policy_rest_bad_request(
    transport: str = "rest", request_type=compute.GetIamPolicyInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "resource": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_iam_policy(request)


def test_get_iam_policy_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Policy()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "resource": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value", zone="zone_value", resource="resource_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Policy.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get_iam_policy(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{resource}/getIamPolicy"
            % client.transport._host,
            args[1],
        )


def test_get_iam_policy_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_iam_policy(
            compute.GetIamPolicyInstanceRequest(),
            project="project_value",
            zone="zone_value",
            resource="resource_value",
        )


def test_get_iam_policy_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.GetScreenshotInstanceRequest, dict,])
def test_get_screenshot_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Screenshot(contents="contents_value", kind="kind_value",)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Screenshot.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_screenshot(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Screenshot)
    assert response.contents == "contents_value"
    assert response.kind == "kind_value"


def test_get_screenshot_rest_required_fields(
    request_type=compute.GetScreenshotInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_screenshot._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_screenshot._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Screenshot()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Screenshot.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_screenshot(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_screenshot_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_screenshot._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("instance", "project", "zone",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_screenshot_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_get_screenshot"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_get_screenshot"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Screenshot.to_json(compute.Screenshot())

        request = compute.GetScreenshotInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Screenshot

        client.get_screenshot(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_screenshot_rest_bad_request(
    transport: str = "rest", request_type=compute.GetScreenshotInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_screenshot(request)


def test_get_screenshot_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Screenshot()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value", zone="zone_value", instance="instance_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Screenshot.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get_screenshot(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/screenshot"
            % client.transport._host,
            args[1],
        )


def test_get_screenshot_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_screenshot(
            compute.GetScreenshotInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
        )


def test_get_screenshot_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.GetSerialPortOutputInstanceRequest, dict,]
)
def test_get_serial_port_output_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.SerialPortOutput(
            contents="contents_value",
            kind="kind_value",
            next_=542,
            self_link="self_link_value",
            start=558,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.SerialPortOutput.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_serial_port_output(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.SerialPortOutput)
    assert response.contents == "contents_value"
    assert response.kind == "kind_value"
    assert response.next_ == 542
    assert response.self_link == "self_link_value"
    assert response.start == 558


def test_get_serial_port_output_rest_required_fields(
    request_type=compute.GetSerialPortOutputInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_serial_port_output._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_serial_port_output._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("port", "start",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.SerialPortOutput()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.SerialPortOutput.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_serial_port_output(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_serial_port_output_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_serial_port_output._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("port", "start",)) & set(("instance", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_serial_port_output_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_get_serial_port_output"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_get_serial_port_output"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.SerialPortOutput.to_json(
            compute.SerialPortOutput()
        )

        request = compute.GetSerialPortOutputInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.SerialPortOutput

        client.get_serial_port_output(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_serial_port_output_rest_bad_request(
    transport: str = "rest", request_type=compute.GetSerialPortOutputInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_serial_port_output(request)


def test_get_serial_port_output_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.SerialPortOutput()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value", zone="zone_value", instance="instance_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.SerialPortOutput.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get_serial_port_output(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/serialPort"
            % client.transport._host,
            args[1],
        )


def test_get_serial_port_output_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_serial_port_output(
            compute.GetSerialPortOutputInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
        )


def test_get_serial_port_output_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.GetShieldedInstanceIdentityInstanceRequest, dict,]
)
def test_get_shielded_instance_identity_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.ShieldedInstanceIdentity(kind="kind_value",)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.ShieldedInstanceIdentity.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_shielded_instance_identity(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.ShieldedInstanceIdentity)
    assert response.kind == "kind_value"


def test_get_shielded_instance_identity_rest_required_fields(
    request_type=compute.GetShieldedInstanceIdentityInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_shielded_instance_identity._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_shielded_instance_identity._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.ShieldedInstanceIdentity()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.ShieldedInstanceIdentity.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_shielded_instance_identity(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_shielded_instance_identity_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_shielded_instance_identity._get_unset_required_fields(
        {}
    )
    assert set(unset_fields) == (set(()) & set(("instance", "project", "zone",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_shielded_instance_identity_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_get_shielded_instance_identity"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_get_shielded_instance_identity"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.ShieldedInstanceIdentity.to_json(
            compute.ShieldedInstanceIdentity()
        )

        request = compute.GetShieldedInstanceIdentityInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.ShieldedInstanceIdentity

        client.get_shielded_instance_identity(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_shielded_instance_identity_rest_bad_request(
    transport: str = "rest",
    request_type=compute.GetShieldedInstanceIdentityInstanceRequest,
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_shielded_instance_identity(request)


def test_get_shielded_instance_identity_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.ShieldedInstanceIdentity()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value", zone="zone_value", instance="instance_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.ShieldedInstanceIdentity.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get_shielded_instance_identity(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/getShieldedInstanceIdentity"
            % client.transport._host,
            args[1],
        )


def test_get_shielded_instance_identity_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_shielded_instance_identity(
            compute.GetShieldedInstanceIdentityInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
        )


def test_get_shielded_instance_identity_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.InsertInstanceRequest, dict,])
def test_insert_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2"}
    request_init["instance_resource"] = {
        "advanced_machine_features": {
            "enable_nested_virtualization": True,
            "threads_per_core": 1689,
        },
        "can_ip_forward": True,
        "confidential_instance_config": {"enable_confidential_compute": True},
        "cpu_platform": "cpu_platform_value",
        "creation_timestamp": "creation_timestamp_value",
        "deletion_protection": True,
        "description": "description_value",
        "disks": [
            {
                "auto_delete": True,
                "boot": True,
                "device_name": "device_name_value",
                "disk_encryption_key": {
                    "kms_key_name": "kms_key_name_value",
                    "kms_key_service_account": "kms_key_service_account_value",
                    "raw_key": "raw_key_value",
                    "rsa_encrypted_key": "rsa_encrypted_key_value",
                    "sha256": "sha256_value",
                },
                "disk_size_gb": 1261,
                "guest_os_features": [{"type_": "type__value"}],
                "index": 536,
                "initialize_params": {
                    "description": "description_value",
                    "disk_name": "disk_name_value",
                    "disk_size_gb": 1261,
                    "disk_type": "disk_type_value",
                    "labels": {},
                    "on_update_action": "on_update_action_value",
                    "provisioned_iops": 1740,
                    "resource_policies": [
                        "resource_policies_value_1",
                        "resource_policies_value_2",
                    ],
                    "source_image": "source_image_value",
                    "source_image_encryption_key": {
                        "kms_key_name": "kms_key_name_value",
                        "kms_key_service_account": "kms_key_service_account_value",
                        "raw_key": "raw_key_value",
                        "rsa_encrypted_key": "rsa_encrypted_key_value",
                        "sha256": "sha256_value",
                    },
                    "source_snapshot": "source_snapshot_value",
                    "source_snapshot_encryption_key": {
                        "kms_key_name": "kms_key_name_value",
                        "kms_key_service_account": "kms_key_service_account_value",
                        "raw_key": "raw_key_value",
                        "rsa_encrypted_key": "rsa_encrypted_key_value",
                        "sha256": "sha256_value",
                    },
                },
                "interface": "interface_value",
                "kind": "kind_value",
                "licenses": ["licenses_value_1", "licenses_value_2"],
                "mode": "mode_value",
                "shielded_instance_initial_state": {
                    "dbs": [
                        {"content": "content_value", "file_type": "file_type_value"}
                    ],
                    "dbxs": [
                        {"content": "content_value", "file_type": "file_type_value"}
                    ],
                    "keks": [
                        {"content": "content_value", "file_type": "file_type_value"}
                    ],
                    "pk": {"content": "content_value", "file_type": "file_type_value"},
                },
                "source": "source_value",
                "type_": "type__value",
            }
        ],
        "display_device": {"enable_display": True},
        "fingerprint": "fingerprint_value",
        "guest_accelerators": [
            {"accelerator_count": 1805, "accelerator_type": "accelerator_type_value"}
        ],
        "hostname": "hostname_value",
        "id": 205,
        "kind": "kind_value",
        "label_fingerprint": "label_fingerprint_value",
        "labels": {},
        "last_start_timestamp": "last_start_timestamp_value",
        "last_stop_timestamp": "last_stop_timestamp_value",
        "last_suspended_timestamp": "last_suspended_timestamp_value",
        "machine_type": "machine_type_value",
        "metadata": {
            "fingerprint": "fingerprint_value",
            "items": [{"key": "key_value", "value": "value_value"}],
            "kind": "kind_value",
        },
        "min_cpu_platform": "min_cpu_platform_value",
        "name": "name_value",
        "network_interfaces": [
            {
                "access_configs": [
                    {
                        "external_ipv6": "external_ipv6_value",
                        "external_ipv6_prefix_length": 2837,
                        "kind": "kind_value",
                        "name": "name_value",
                        "nat_i_p": "nat_i_p_value",
                        "network_tier": "network_tier_value",
                        "public_ptr_domain_name": "public_ptr_domain_name_value",
                        "set_public_ptr": True,
                        "type_": "type__value",
                    }
                ],
                "alias_ip_ranges": [
                    {
                        "ip_cidr_range": "ip_cidr_range_value",
                        "subnetwork_range_name": "subnetwork_range_name_value",
                    }
                ],
                "fingerprint": "fingerprint_value",
                "ipv6_access_configs": [
                    {
                        "external_ipv6": "external_ipv6_value",
                        "external_ipv6_prefix_length": 2837,
                        "kind": "kind_value",
                        "name": "name_value",
                        "nat_i_p": "nat_i_p_value",
                        "network_tier": "network_tier_value",
                        "public_ptr_domain_name": "public_ptr_domain_name_value",
                        "set_public_ptr": True,
                        "type_": "type__value",
                    }
                ],
                "ipv6_access_type": "ipv6_access_type_value",
                "ipv6_address": "ipv6_address_value",
                "kind": "kind_value",
                "name": "name_value",
                "network": "network_value",
                "network_i_p": "network_i_p_value",
                "nic_type": "nic_type_value",
                "queue_count": 1197,
                "stack_type": "stack_type_value",
                "subnetwork": "subnetwork_value",
            }
        ],
        "private_ipv6_google_access": "private_ipv6_google_access_value",
        "reservation_affinity": {
            "consume_reservation_type": "consume_reservation_type_value",
            "key": "key_value",
            "values": ["values_value_1", "values_value_2"],
        },
        "resource_policies": ["resource_policies_value_1", "resource_policies_value_2"],
        "satisfies_pzs": True,
        "scheduling": {
            "automatic_restart": True,
            "location_hint": "location_hint_value",
            "min_node_cpus": 1379,
            "node_affinities": [
                {
                    "key": "key_value",
                    "operator": "operator_value",
                    "values": ["values_value_1", "values_value_2"],
                }
            ],
            "on_host_maintenance": "on_host_maintenance_value",
            "preemptible": True,
        },
        "self_link": "self_link_value",
        "service_accounts": [
            {"email": "email_value", "scopes": ["scopes_value_1", "scopes_value_2"]}
        ],
        "shielded_instance_config": {
            "enable_integrity_monitoring": True,
            "enable_secure_boot": True,
            "enable_vtpm": True,
        },
        "shielded_instance_integrity_policy": {"update_auto_learn_policy": True},
        "start_restricted": True,
        "status": "status_value",
        "status_message": "status_message_value",
        "tags": {
            "fingerprint": "fingerprint_value",
            "items": ["items_value_1", "items_value_2"],
        },
        "zone": "zone_value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.insert_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_insert_unary_rest_required_fields(request_type=compute.InsertInstanceRequest):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).insert._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).insert._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id", "source_instance_template",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.insert_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_insert_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.insert._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId", "sourceInstanceTemplate",))
        & set(("instanceResource", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_insert_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_insert"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_insert"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.InsertInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.insert_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_insert_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.InsertInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2"}
    request_init["instance_resource"] = {
        "advanced_machine_features": {
            "enable_nested_virtualization": True,
            "threads_per_core": 1689,
        },
        "can_ip_forward": True,
        "confidential_instance_config": {"enable_confidential_compute": True},
        "cpu_platform": "cpu_platform_value",
        "creation_timestamp": "creation_timestamp_value",
        "deletion_protection": True,
        "description": "description_value",
        "disks": [
            {
                "auto_delete": True,
                "boot": True,
                "device_name": "device_name_value",
                "disk_encryption_key": {
                    "kms_key_name": "kms_key_name_value",
                    "kms_key_service_account": "kms_key_service_account_value",
                    "raw_key": "raw_key_value",
                    "rsa_encrypted_key": "rsa_encrypted_key_value",
                    "sha256": "sha256_value",
                },
                "disk_size_gb": 1261,
                "guest_os_features": [{"type_": "type__value"}],
                "index": 536,
                "initialize_params": {
                    "description": "description_value",
                    "disk_name": "disk_name_value",
                    "disk_size_gb": 1261,
                    "disk_type": "disk_type_value",
                    "labels": {},
                    "on_update_action": "on_update_action_value",
                    "provisioned_iops": 1740,
                    "resource_policies": [
                        "resource_policies_value_1",
                        "resource_policies_value_2",
                    ],
                    "source_image": "source_image_value",
                    "source_image_encryption_key": {
                        "kms_key_name": "kms_key_name_value",
                        "kms_key_service_account": "kms_key_service_account_value",
                        "raw_key": "raw_key_value",
                        "rsa_encrypted_key": "rsa_encrypted_key_value",
                        "sha256": "sha256_value",
                    },
                    "source_snapshot": "source_snapshot_value",
                    "source_snapshot_encryption_key": {
                        "kms_key_name": "kms_key_name_value",
                        "kms_key_service_account": "kms_key_service_account_value",
                        "raw_key": "raw_key_value",
                        "rsa_encrypted_key": "rsa_encrypted_key_value",
                        "sha256": "sha256_value",
                    },
                },
                "interface": "interface_value",
                "kind": "kind_value",
                "licenses": ["licenses_value_1", "licenses_value_2"],
                "mode": "mode_value",
                "shielded_instance_initial_state": {
                    "dbs": [
                        {"content": "content_value", "file_type": "file_type_value"}
                    ],
                    "dbxs": [
                        {"content": "content_value", "file_type": "file_type_value"}
                    ],
                    "keks": [
                        {"content": "content_value", "file_type": "file_type_value"}
                    ],
                    "pk": {"content": "content_value", "file_type": "file_type_value"},
                },
                "source": "source_value",
                "type_": "type__value",
            }
        ],
        "display_device": {"enable_display": True},
        "fingerprint": "fingerprint_value",
        "guest_accelerators": [
            {"accelerator_count": 1805, "accelerator_type": "accelerator_type_value"}
        ],
        "hostname": "hostname_value",
        "id": 205,
        "kind": "kind_value",
        "label_fingerprint": "label_fingerprint_value",
        "labels": {},
        "last_start_timestamp": "last_start_timestamp_value",
        "last_stop_timestamp": "last_stop_timestamp_value",
        "last_suspended_timestamp": "last_suspended_timestamp_value",
        "machine_type": "machine_type_value",
        "metadata": {
            "fingerprint": "fingerprint_value",
            "items": [{"key": "key_value", "value": "value_value"}],
            "kind": "kind_value",
        },
        "min_cpu_platform": "min_cpu_platform_value",
        "name": "name_value",
        "network_interfaces": [
            {
                "access_configs": [
                    {
                        "external_ipv6": "external_ipv6_value",
                        "external_ipv6_prefix_length": 2837,
                        "kind": "kind_value",
                        "name": "name_value",
                        "nat_i_p": "nat_i_p_value",
                        "network_tier": "network_tier_value",
                        "public_ptr_domain_name": "public_ptr_domain_name_value",
                        "set_public_ptr": True,
                        "type_": "type__value",
                    }
                ],
                "alias_ip_ranges": [
                    {
                        "ip_cidr_range": "ip_cidr_range_value",
                        "subnetwork_range_name": "subnetwork_range_name_value",
                    }
                ],
                "fingerprint": "fingerprint_value",
                "ipv6_access_configs": [
                    {
                        "external_ipv6": "external_ipv6_value",
                        "external_ipv6_prefix_length": 2837,
                        "kind": "kind_value",
                        "name": "name_value",
                        "nat_i_p": "nat_i_p_value",
                        "network_tier": "network_tier_value",
                        "public_ptr_domain_name": "public_ptr_domain_name_value",
                        "set_public_ptr": True,
                        "type_": "type__value",
                    }
                ],
                "ipv6_access_type": "ipv6_access_type_value",
                "ipv6_address": "ipv6_address_value",
                "kind": "kind_value",
                "name": "name_value",
                "network": "network_value",
                "network_i_p": "network_i_p_value",
                "nic_type": "nic_type_value",
                "queue_count": 1197,
                "stack_type": "stack_type_value",
                "subnetwork": "subnetwork_value",
            }
        ],
        "private_ipv6_google_access": "private_ipv6_google_access_value",
        "reservation_affinity": {
            "consume_reservation_type": "consume_reservation_type_value",
            "key": "key_value",
            "values": ["values_value_1", "values_value_2"],
        },
        "resource_policies": ["resource_policies_value_1", "resource_policies_value_2"],
        "satisfies_pzs": True,
        "scheduling": {
            "automatic_restart": True,
            "location_hint": "location_hint_value",
            "min_node_cpus": 1379,
            "node_affinities": [
                {
                    "key": "key_value",
                    "operator": "operator_value",
                    "values": ["values_value_1", "values_value_2"],
                }
            ],
            "on_host_maintenance": "on_host_maintenance_value",
            "preemptible": True,
        },
        "self_link": "self_link_value",
        "service_accounts": [
            {"email": "email_value", "scopes": ["scopes_value_1", "scopes_value_2"]}
        ],
        "shielded_instance_config": {
            "enable_integrity_monitoring": True,
            "enable_secure_boot": True,
            "enable_vtpm": True,
        },
        "shielded_instance_integrity_policy": {"update_auto_learn_policy": True},
        "start_restricted": True,
        "status": "status_value",
        "status_message": "status_message_value",
        "tags": {
            "fingerprint": "fingerprint_value",
            "items": ["items_value_1", "items_value_2"],
        },
        "zone": "zone_value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.insert_unary(request)


def test_insert_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {"project": "sample1", "zone": "sample2"}

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance_resource=compute.Instance(
                advanced_machine_features=compute.AdvancedMachineFeatures(
                    enable_nested_virtualization=True
                )
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.insert_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances"
            % client.transport._host,
            args[1],
        )


def test_insert_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.insert_unary(
            compute.InsertInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance_resource=compute.Instance(
                advanced_machine_features=compute.AdvancedMachineFeatures(
                    enable_nested_virtualization=True
                )
            ),
        )


def test_insert_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.ListInstancesRequest, dict,])
def test_list_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.InstanceList(
            id="id_value",
            kind="kind_value",
            next_page_token="next_page_token_value",
            self_link="self_link_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.InstanceList.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.list(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListPager)
    assert response.id == "id_value"
    assert response.kind == "kind_value"
    assert response.next_page_token == "next_page_token_value"
    assert response.self_link == "self_link_value"


def test_list_rest_required_fields(request_type=compute.ListInstancesRequest):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        ("filter", "max_results", "order_by", "page_token", "return_partial_success",)
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.InstanceList()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.InstanceList.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.list(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("filter", "maxResults", "orderBy", "pageToken", "returnPartialSuccess",))
        & set(("project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_list"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_list"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.InstanceList.to_json(compute.InstanceList())

        request = compute.ListInstancesRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.InstanceList

        client.list(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()


def test_list_rest_bad_request(
    transport: str = "rest", request_type=compute.ListInstancesRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.list(request)


def test_list_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.InstanceList()

        # get arguments that satisfy an http rule for this method
        sample_request = {"project": "sample1", "zone": "sample2"}

        # get truthy value for each flattened field
        mock_args = dict(project="project_value", zone="zone_value",)
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.InstanceList.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.list(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances"
            % client.transport._host,
            args[1],
        )


def test_list_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list(
            compute.ListInstancesRequest(), project="project_value", zone="zone_value",
        )


def test_list_rest_pager(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            compute.InstanceList(
                items=[compute.Instance(), compute.Instance(), compute.Instance(),],
                next_page_token="abc",
            ),
            compute.InstanceList(items=[], next_page_token="def",),
            compute.InstanceList(items=[compute.Instance(),], next_page_token="ghi",),
            compute.InstanceList(items=[compute.Instance(), compute.Instance(),],),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(compute.InstanceList.to_json(x) for x in response)
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {"project": "sample1", "zone": "sample2"}

        pager = client.list(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, compute.Instance) for i in results)

        pages = list(client.list(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize("request_type", [compute.ListReferrersInstancesRequest, dict,])
def test_list_referrers_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.InstanceListReferrers(
            id="id_value",
            kind="kind_value",
            next_page_token="next_page_token_value",
            self_link="self_link_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.InstanceListReferrers.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.list_referrers(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListReferrersPager)
    assert response.id == "id_value"
    assert response.kind == "kind_value"
    assert response.next_page_token == "next_page_token_value"
    assert response.self_link == "self_link_value"


def test_list_referrers_rest_required_fields(
    request_type=compute.ListReferrersInstancesRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_referrers._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_referrers._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        ("filter", "max_results", "order_by", "page_token", "return_partial_success",)
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.InstanceListReferrers()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.InstanceListReferrers.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.list_referrers(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_referrers_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_referrers._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("filter", "maxResults", "orderBy", "pageToken", "returnPartialSuccess",))
        & set(("instance", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_referrers_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_list_referrers"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_list_referrers"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.InstanceListReferrers.to_json(
            compute.InstanceListReferrers()
        )

        request = compute.ListReferrersInstancesRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.InstanceListReferrers

        client.list_referrers(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_list_referrers_rest_bad_request(
    transport: str = "rest", request_type=compute.ListReferrersInstancesRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.list_referrers(request)


def test_list_referrers_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.InstanceListReferrers()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value", zone="zone_value", instance="instance_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.InstanceListReferrers.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.list_referrers(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/referrers"
            % client.transport._host,
            args[1],
        )


def test_list_referrers_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_referrers(
            compute.ListReferrersInstancesRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
        )


def test_list_referrers_rest_pager(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            compute.InstanceListReferrers(
                items=[compute.Reference(), compute.Reference(), compute.Reference(),],
                next_page_token="abc",
            ),
            compute.InstanceListReferrers(items=[], next_page_token="def",),
            compute.InstanceListReferrers(
                items=[compute.Reference(),], next_page_token="ghi",
            ),
            compute.InstanceListReferrers(
                items=[compute.Reference(), compute.Reference(),],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(compute.InstanceListReferrers.to_json(x) for x in response)
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        pager = client.list_referrers(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, compute.Reference) for i in results)

        pages = list(client.list_referrers(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type", [compute.RemoveResourcePoliciesInstanceRequest, dict,]
)
def test_remove_resource_policies_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_remove_resource_policies_request_resource"] = {
        "resource_policies": ["resource_policies_value_1", "resource_policies_value_2"]
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.remove_resource_policies_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_remove_resource_policies_unary_rest_required_fields(
    request_type=compute.RemoveResourcePoliciesInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).remove_resource_policies._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).remove_resource_policies._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.remove_resource_policies_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_remove_resource_policies_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.remove_resource_policies._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",))
        & set(
            (
                "instance",
                "instancesRemoveResourcePoliciesRequestResource",
                "project",
                "zone",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_remove_resource_policies_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_remove_resource_policies"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_remove_resource_policies"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.RemoveResourcePoliciesInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.remove_resource_policies_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_remove_resource_policies_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.RemoveResourcePoliciesInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_remove_resource_policies_request_resource"] = {
        "resource_policies": ["resource_policies_value_1", "resource_policies_value_2"]
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.remove_resource_policies_unary(request)


def test_remove_resource_policies_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_remove_resource_policies_request_resource=compute.InstancesRemoveResourcePoliciesRequest(
                resource_policies=["resource_policies_value"]
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.remove_resource_policies_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/removeResourcePolicies"
            % client.transport._host,
            args[1],
        )


def test_remove_resource_policies_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.remove_resource_policies_unary(
            compute.RemoveResourcePoliciesInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_remove_resource_policies_request_resource=compute.InstancesRemoveResourcePoliciesRequest(
                resource_policies=["resource_policies_value"]
            ),
        )


def test_remove_resource_policies_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.ResetInstanceRequest, dict,])
def test_reset_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.reset_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_reset_unary_rest_required_fields(request_type=compute.ResetInstanceRequest):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).reset._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).reset._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.reset_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_reset_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.reset._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",)) & set(("instance", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_reset_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_reset"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_reset"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.ResetInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.reset_unary(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()


def test_reset_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.ResetInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.reset_unary(request)


def test_reset_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value", zone="zone_value", instance="instance_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.reset_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/reset"
            % client.transport._host,
            args[1],
        )


def test_reset_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.reset_unary(
            compute.ResetInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
        )


def test_reset_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.SendDiagnosticInterruptInstanceRequest, dict,]
)
def test_send_diagnostic_interrupt_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.SendDiagnosticInterruptInstanceResponse()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.SendDiagnosticInterruptInstanceResponse.to_json(
            return_value
        )
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.send_diagnostic_interrupt(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.SendDiagnosticInterruptInstanceResponse)


def test_send_diagnostic_interrupt_rest_required_fields(
    request_type=compute.SendDiagnosticInterruptInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).send_diagnostic_interrupt._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).send_diagnostic_interrupt._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.SendDiagnosticInterruptInstanceResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.SendDiagnosticInterruptInstanceResponse.to_json(
                return_value
            )
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.send_diagnostic_interrupt(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_send_diagnostic_interrupt_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.send_diagnostic_interrupt._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("instance", "project", "zone",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_send_diagnostic_interrupt_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_send_diagnostic_interrupt"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_send_diagnostic_interrupt"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.SendDiagnosticInterruptInstanceResponse.to_json(
            compute.SendDiagnosticInterruptInstanceResponse()
        )

        request = compute.SendDiagnosticInterruptInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.SendDiagnosticInterruptInstanceResponse

        client.send_diagnostic_interrupt(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_send_diagnostic_interrupt_rest_bad_request(
    transport: str = "rest", request_type=compute.SendDiagnosticInterruptInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.send_diagnostic_interrupt(request)


def test_send_diagnostic_interrupt_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.SendDiagnosticInterruptInstanceResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value", zone="zone_value", instance="instance_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.SendDiagnosticInterruptInstanceResponse.to_json(
            return_value
        )

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.send_diagnostic_interrupt(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/sendDiagnosticInterrupt"
            % client.transport._host,
            args[1],
        )


def test_send_diagnostic_interrupt_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.send_diagnostic_interrupt(
            compute.SendDiagnosticInterruptInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
        )


def test_send_diagnostic_interrupt_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.SetDeletionProtectionInstanceRequest, dict,]
)
def test_set_deletion_protection_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "resource": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.set_deletion_protection_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_set_deletion_protection_unary_rest_required_fields(
    request_type=compute.SetDeletionProtectionInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["project"] = ""
    request_init["resource"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_deletion_protection._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["project"] = "project_value"
    jsonified_request["resource"] = "resource_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_deletion_protection._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("deletion_protection", "request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "resource" in jsonified_request
    assert jsonified_request["resource"] == "resource_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.set_deletion_protection_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_set_deletion_protection_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.set_deletion_protection._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("deletionProtection", "requestId",))
        & set(("project", "resource", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_set_deletion_protection_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_set_deletion_protection"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_set_deletion_protection"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.SetDeletionProtectionInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.set_deletion_protection_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_set_deletion_protection_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.SetDeletionProtectionInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "resource": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.set_deletion_protection_unary(request)


def test_set_deletion_protection_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "resource": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value", zone="zone_value", resource="resource_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.set_deletion_protection_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{resource}/setDeletionProtection"
            % client.transport._host,
            args[1],
        )


def test_set_deletion_protection_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_deletion_protection_unary(
            compute.SetDeletionProtectionInstanceRequest(),
            project="project_value",
            zone="zone_value",
            resource="resource_value",
        )


def test_set_deletion_protection_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.SetDiskAutoDeleteInstanceRequest, dict,]
)
def test_set_disk_auto_delete_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.set_disk_auto_delete_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_set_disk_auto_delete_unary_rest_required_fields(
    request_type=compute.SetDiskAutoDeleteInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["auto_delete"] = False
    request_init["device_name"] = ""
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped
    assert "autoDelete" not in jsonified_request
    assert "deviceName" not in jsonified_request

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_disk_auto_delete._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "autoDelete" in jsonified_request
    assert jsonified_request["autoDelete"] == request_init["auto_delete"]
    assert "deviceName" in jsonified_request
    assert jsonified_request["deviceName"] == request_init["device_name"]

    jsonified_request["autoDelete"] = True
    jsonified_request["deviceName"] = "device_name_value"
    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_disk_auto_delete._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("auto_delete", "device_name", "request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "autoDelete" in jsonified_request
    assert jsonified_request["autoDelete"] == True
    assert "deviceName" in jsonified_request
    assert jsonified_request["deviceName"] == "device_name_value"
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.set_disk_auto_delete_unary(request)

            expected_params = [
                ("autoDelete", False,),
                ("deviceName", "",),
            ]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_set_disk_auto_delete_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.set_disk_auto_delete._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("autoDelete", "deviceName", "requestId",))
        & set(("autoDelete", "deviceName", "instance", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_set_disk_auto_delete_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_set_disk_auto_delete"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_set_disk_auto_delete"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.SetDiskAutoDeleteInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.set_disk_auto_delete_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_set_disk_auto_delete_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.SetDiskAutoDeleteInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.set_disk_auto_delete_unary(request)


def test_set_disk_auto_delete_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            auto_delete=True,
            device_name="device_name_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.set_disk_auto_delete_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/setDiskAutoDelete"
            % client.transport._host,
            args[1],
        )


def test_set_disk_auto_delete_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_disk_auto_delete_unary(
            compute.SetDiskAutoDeleteInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            auto_delete=True,
            device_name="device_name_value",
        )


def test_set_disk_auto_delete_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.SetIamPolicyInstanceRequest, dict,])
def test_set_iam_policy_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "resource": "sample3"}
    request_init["zone_set_policy_request_resource"] = {
        "bindings": [
            {
                "binding_id": "binding_id_value",
                "condition": {
                    "description": "description_value",
                    "expression": "expression_value",
                    "location": "location_value",
                    "title": "title_value",
                },
                "members": ["members_value_1", "members_value_2"],
                "role": "role_value",
            }
        ],
        "etag": "etag_value",
        "policy": {
            "audit_configs": [
                {
                    "audit_log_configs": [
                        {
                            "exempted_members": [
                                "exempted_members_value_1",
                                "exempted_members_value_2",
                            ],
                            "ignore_child_exemptions": True,
                            "log_type": "log_type_value",
                        }
                    ],
                    "exempted_members": [
                        "exempted_members_value_1",
                        "exempted_members_value_2",
                    ],
                    "service": "service_value",
                }
            ],
            "bindings": [
                {
                    "binding_id": "binding_id_value",
                    "condition": {
                        "description": "description_value",
                        "expression": "expression_value",
                        "location": "location_value",
                        "title": "title_value",
                    },
                    "members": ["members_value_1", "members_value_2"],
                    "role": "role_value",
                }
            ],
            "etag": "etag_value",
            "iam_owned": True,
            "rules": [
                {
                    "action": "action_value",
                    "conditions": [
                        {
                            "iam": "iam_value",
                            "op": "op_value",
                            "svc": "svc_value",
                            "sys": "sys_value",
                            "values": ["values_value_1", "values_value_2"],
                        }
                    ],
                    "description": "description_value",
                    "ins": ["ins_value_1", "ins_value_2"],
                    "log_configs": [
                        {
                            "cloud_audit": {
                                "authorization_logging_options": {
                                    "permission_type": "permission_type_value"
                                },
                                "log_name": "log_name_value",
                            },
                            "counter": {
                                "custom_fields": [
                                    {"name": "name_value", "value": "value_value"}
                                ],
                                "field": "field_value",
                                "metric": "metric_value",
                            },
                            "data_access": {"log_mode": "log_mode_value"},
                        }
                    ],
                    "not_ins": ["not_ins_value_1", "not_ins_value_2"],
                    "permissions": ["permissions_value_1", "permissions_value_2"],
                }
            ],
            "version": 774,
        },
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Policy(etag="etag_value", iam_owned=True, version=774,)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Policy.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.set_iam_policy(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Policy)
    assert response.etag == "etag_value"
    assert response.iam_owned is True
    assert response.version == 774


def test_set_iam_policy_rest_required_fields(
    request_type=compute.SetIamPolicyInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["project"] = ""
    request_init["resource"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_iam_policy._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["project"] = "project_value"
    jsonified_request["resource"] = "resource_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_iam_policy._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "resource" in jsonified_request
    assert jsonified_request["resource"] == "resource_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Policy()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Policy.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.set_iam_policy(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_set_iam_policy_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.set_iam_policy._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(()) & set(("project", "resource", "zone", "zoneSetPolicyRequestResource",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_set_iam_policy_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_set_iam_policy"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_set_iam_policy"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Policy.to_json(compute.Policy())

        request = compute.SetIamPolicyInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Policy

        client.set_iam_policy(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_set_iam_policy_rest_bad_request(
    transport: str = "rest", request_type=compute.SetIamPolicyInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "resource": "sample3"}
    request_init["zone_set_policy_request_resource"] = {
        "bindings": [
            {
                "binding_id": "binding_id_value",
                "condition": {
                    "description": "description_value",
                    "expression": "expression_value",
                    "location": "location_value",
                    "title": "title_value",
                },
                "members": ["members_value_1", "members_value_2"],
                "role": "role_value",
            }
        ],
        "etag": "etag_value",
        "policy": {
            "audit_configs": [
                {
                    "audit_log_configs": [
                        {
                            "exempted_members": [
                                "exempted_members_value_1",
                                "exempted_members_value_2",
                            ],
                            "ignore_child_exemptions": True,
                            "log_type": "log_type_value",
                        }
                    ],
                    "exempted_members": [
                        "exempted_members_value_1",
                        "exempted_members_value_2",
                    ],
                    "service": "service_value",
                }
            ],
            "bindings": [
                {
                    "binding_id": "binding_id_value",
                    "condition": {
                        "description": "description_value",
                        "expression": "expression_value",
                        "location": "location_value",
                        "title": "title_value",
                    },
                    "members": ["members_value_1", "members_value_2"],
                    "role": "role_value",
                }
            ],
            "etag": "etag_value",
            "iam_owned": True,
            "rules": [
                {
                    "action": "action_value",
                    "conditions": [
                        {
                            "iam": "iam_value",
                            "op": "op_value",
                            "svc": "svc_value",
                            "sys": "sys_value",
                            "values": ["values_value_1", "values_value_2"],
                        }
                    ],
                    "description": "description_value",
                    "ins": ["ins_value_1", "ins_value_2"],
                    "log_configs": [
                        {
                            "cloud_audit": {
                                "authorization_logging_options": {
                                    "permission_type": "permission_type_value"
                                },
                                "log_name": "log_name_value",
                            },
                            "counter": {
                                "custom_fields": [
                                    {"name": "name_value", "value": "value_value"}
                                ],
                                "field": "field_value",
                                "metric": "metric_value",
                            },
                            "data_access": {"log_mode": "log_mode_value"},
                        }
                    ],
                    "not_ins": ["not_ins_value_1", "not_ins_value_2"],
                    "permissions": ["permissions_value_1", "permissions_value_2"],
                }
            ],
            "version": 774,
        },
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.set_iam_policy(request)


def test_set_iam_policy_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Policy()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "resource": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            resource="resource_value",
            zone_set_policy_request_resource=compute.ZoneSetPolicyRequest(
                bindings=[compute.Binding(binding_id="binding_id_value")]
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Policy.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.set_iam_policy(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{resource}/setIamPolicy"
            % client.transport._host,
            args[1],
        )


def test_set_iam_policy_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_iam_policy(
            compute.SetIamPolicyInstanceRequest(),
            project="project_value",
            zone="zone_value",
            resource="resource_value",
            zone_set_policy_request_resource=compute.ZoneSetPolicyRequest(
                bindings=[compute.Binding(binding_id="binding_id_value")]
            ),
        )


def test_set_iam_policy_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.SetLabelsInstanceRequest, dict,])
def test_set_labels_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_set_labels_request_resource"] = {
        "label_fingerprint": "label_fingerprint_value",
        "labels": {},
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.set_labels_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_set_labels_unary_rest_required_fields(
    request_type=compute.SetLabelsInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_labels._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_labels._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.set_labels_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_set_labels_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.set_labels._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",))
        & set(("instance", "instancesSetLabelsRequestResource", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_set_labels_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_set_labels"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_set_labels"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.SetLabelsInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.set_labels_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_set_labels_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.SetLabelsInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_set_labels_request_resource"] = {
        "label_fingerprint": "label_fingerprint_value",
        "labels": {},
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.set_labels_unary(request)


def test_set_labels_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_set_labels_request_resource=compute.InstancesSetLabelsRequest(
                label_fingerprint="label_fingerprint_value"
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.set_labels_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/setLabels"
            % client.transport._host,
            args[1],
        )


def test_set_labels_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_labels_unary(
            compute.SetLabelsInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_set_labels_request_resource=compute.InstancesSetLabelsRequest(
                label_fingerprint="label_fingerprint_value"
            ),
        )


def test_set_labels_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.SetMachineResourcesInstanceRequest, dict,]
)
def test_set_machine_resources_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_set_machine_resources_request_resource"] = {
        "guest_accelerators": [
            {"accelerator_count": 1805, "accelerator_type": "accelerator_type_value"}
        ]
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.set_machine_resources_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_set_machine_resources_unary_rest_required_fields(
    request_type=compute.SetMachineResourcesInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_machine_resources._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_machine_resources._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.set_machine_resources_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_set_machine_resources_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.set_machine_resources._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",))
        & set(
            (
                "instance",
                "instancesSetMachineResourcesRequestResource",
                "project",
                "zone",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_set_machine_resources_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_set_machine_resources"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_set_machine_resources"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.SetMachineResourcesInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.set_machine_resources_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_set_machine_resources_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.SetMachineResourcesInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_set_machine_resources_request_resource"] = {
        "guest_accelerators": [
            {"accelerator_count": 1805, "accelerator_type": "accelerator_type_value"}
        ]
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.set_machine_resources_unary(request)


def test_set_machine_resources_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_set_machine_resources_request_resource=compute.InstancesSetMachineResourcesRequest(
                guest_accelerators=[compute.AcceleratorConfig(accelerator_count=1805)]
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.set_machine_resources_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/setMachineResources"
            % client.transport._host,
            args[1],
        )


def test_set_machine_resources_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_machine_resources_unary(
            compute.SetMachineResourcesInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_set_machine_resources_request_resource=compute.InstancesSetMachineResourcesRequest(
                guest_accelerators=[compute.AcceleratorConfig(accelerator_count=1805)]
            ),
        )


def test_set_machine_resources_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.SetMachineTypeInstanceRequest, dict,])
def test_set_machine_type_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_set_machine_type_request_resource"] = {
        "machine_type": "machine_type_value"
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.set_machine_type_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_set_machine_type_unary_rest_required_fields(
    request_type=compute.SetMachineTypeInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_machine_type._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_machine_type._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.set_machine_type_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_set_machine_type_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.set_machine_type._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",))
        & set(
            ("instance", "instancesSetMachineTypeRequestResource", "project", "zone",)
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_set_machine_type_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_set_machine_type"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_set_machine_type"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.SetMachineTypeInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.set_machine_type_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_set_machine_type_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.SetMachineTypeInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_set_machine_type_request_resource"] = {
        "machine_type": "machine_type_value"
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.set_machine_type_unary(request)


def test_set_machine_type_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_set_machine_type_request_resource=compute.InstancesSetMachineTypeRequest(
                machine_type="machine_type_value"
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.set_machine_type_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/setMachineType"
            % client.transport._host,
            args[1],
        )


def test_set_machine_type_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_machine_type_unary(
            compute.SetMachineTypeInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_set_machine_type_request_resource=compute.InstancesSetMachineTypeRequest(
                machine_type="machine_type_value"
            ),
        )


def test_set_machine_type_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.SetMetadataInstanceRequest, dict,])
def test_set_metadata_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["metadata_resource"] = {
        "fingerprint": "fingerprint_value",
        "items": [{"key": "key_value", "value": "value_value"}],
        "kind": "kind_value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.set_metadata_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_set_metadata_unary_rest_required_fields(
    request_type=compute.SetMetadataInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_metadata._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_metadata._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.set_metadata_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_set_metadata_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.set_metadata._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",)) & set(("instance", "metadataResource", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_set_metadata_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_set_metadata"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_set_metadata"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.SetMetadataInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.set_metadata_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_set_metadata_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.SetMetadataInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["metadata_resource"] = {
        "fingerprint": "fingerprint_value",
        "items": [{"key": "key_value", "value": "value_value"}],
        "kind": "kind_value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.set_metadata_unary(request)


def test_set_metadata_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            metadata_resource=compute.Metadata(fingerprint="fingerprint_value"),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.set_metadata_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/setMetadata"
            % client.transport._host,
            args[1],
        )


def test_set_metadata_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_metadata_unary(
            compute.SetMetadataInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            metadata_resource=compute.Metadata(fingerprint="fingerprint_value"),
        )


def test_set_metadata_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.SetMinCpuPlatformInstanceRequest, dict,]
)
def test_set_min_cpu_platform_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_set_min_cpu_platform_request_resource"] = {
        "min_cpu_platform": "min_cpu_platform_value"
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.set_min_cpu_platform_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_set_min_cpu_platform_unary_rest_required_fields(
    request_type=compute.SetMinCpuPlatformInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_min_cpu_platform._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_min_cpu_platform._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.set_min_cpu_platform_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_set_min_cpu_platform_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.set_min_cpu_platform._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",))
        & set(
            (
                "instance",
                "instancesSetMinCpuPlatformRequestResource",
                "project",
                "zone",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_set_min_cpu_platform_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_set_min_cpu_platform"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_set_min_cpu_platform"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.SetMinCpuPlatformInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.set_min_cpu_platform_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_set_min_cpu_platform_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.SetMinCpuPlatformInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_set_min_cpu_platform_request_resource"] = {
        "min_cpu_platform": "min_cpu_platform_value"
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.set_min_cpu_platform_unary(request)


def test_set_min_cpu_platform_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_set_min_cpu_platform_request_resource=compute.InstancesSetMinCpuPlatformRequest(
                min_cpu_platform="min_cpu_platform_value"
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.set_min_cpu_platform_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/setMinCpuPlatform"
            % client.transport._host,
            args[1],
        )


def test_set_min_cpu_platform_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_min_cpu_platform_unary(
            compute.SetMinCpuPlatformInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_set_min_cpu_platform_request_resource=compute.InstancesSetMinCpuPlatformRequest(
                min_cpu_platform="min_cpu_platform_value"
            ),
        )


def test_set_min_cpu_platform_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.SetSchedulingInstanceRequest, dict,])
def test_set_scheduling_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["scheduling_resource"] = {
        "automatic_restart": True,
        "location_hint": "location_hint_value",
        "min_node_cpus": 1379,
        "node_affinities": [
            {
                "key": "key_value",
                "operator": "operator_value",
                "values": ["values_value_1", "values_value_2"],
            }
        ],
        "on_host_maintenance": "on_host_maintenance_value",
        "preemptible": True,
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.set_scheduling_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_set_scheduling_unary_rest_required_fields(
    request_type=compute.SetSchedulingInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_scheduling._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_scheduling._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.set_scheduling_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_set_scheduling_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.set_scheduling._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",))
        & set(("instance", "project", "schedulingResource", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_set_scheduling_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_set_scheduling"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_set_scheduling"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.SetSchedulingInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.set_scheduling_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_set_scheduling_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.SetSchedulingInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["scheduling_resource"] = {
        "automatic_restart": True,
        "location_hint": "location_hint_value",
        "min_node_cpus": 1379,
        "node_affinities": [
            {
                "key": "key_value",
                "operator": "operator_value",
                "values": ["values_value_1", "values_value_2"],
            }
        ],
        "on_host_maintenance": "on_host_maintenance_value",
        "preemptible": True,
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.set_scheduling_unary(request)


def test_set_scheduling_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            scheduling_resource=compute.Scheduling(automatic_restart=True),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.set_scheduling_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/setScheduling"
            % client.transport._host,
            args[1],
        )


def test_set_scheduling_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_scheduling_unary(
            compute.SetSchedulingInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            scheduling_resource=compute.Scheduling(automatic_restart=True),
        )


def test_set_scheduling_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.SetServiceAccountInstanceRequest, dict,]
)
def test_set_service_account_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_set_service_account_request_resource"] = {
        "email": "email_value",
        "scopes": ["scopes_value_1", "scopes_value_2"],
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.set_service_account_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_set_service_account_unary_rest_required_fields(
    request_type=compute.SetServiceAccountInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_service_account._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_service_account._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.set_service_account_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_set_service_account_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.set_service_account._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",))
        & set(
            (
                "instance",
                "instancesSetServiceAccountRequestResource",
                "project",
                "zone",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_set_service_account_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_set_service_account"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_set_service_account"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.SetServiceAccountInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.set_service_account_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_set_service_account_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.SetServiceAccountInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_set_service_account_request_resource"] = {
        "email": "email_value",
        "scopes": ["scopes_value_1", "scopes_value_2"],
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.set_service_account_unary(request)


def test_set_service_account_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_set_service_account_request_resource=compute.InstancesSetServiceAccountRequest(
                email="email_value"
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.set_service_account_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/setServiceAccount"
            % client.transport._host,
            args[1],
        )


def test_set_service_account_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_service_account_unary(
            compute.SetServiceAccountInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_set_service_account_request_resource=compute.InstancesSetServiceAccountRequest(
                email="email_value"
            ),
        )


def test_set_service_account_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.SetShieldedInstanceIntegrityPolicyInstanceRequest, dict,]
)
def test_set_shielded_instance_integrity_policy_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["shielded_instance_integrity_policy_resource"] = {
        "update_auto_learn_policy": True
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.set_shielded_instance_integrity_policy_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_set_shielded_instance_integrity_policy_unary_rest_required_fields(
    request_type=compute.SetShieldedInstanceIntegrityPolicyInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_shielded_instance_integrity_policy._get_unset_required_fields(
        jsonified_request
    )
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_shielded_instance_integrity_policy._get_unset_required_fields(
        jsonified_request
    )
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "patch",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.set_shielded_instance_integrity_policy_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_set_shielded_instance_integrity_policy_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.set_shielded_instance_integrity_policy._get_unset_required_fields(
        {}
    )
    assert set(unset_fields) == (
        set(("requestId",))
        & set(
            ("instance", "project", "shieldedInstanceIntegrityPolicyResource", "zone",)
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_set_shielded_instance_integrity_policy_unary_rest_interceptors(
    null_interceptor,
):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor,
        "post_set_shielded_instance_integrity_policy",
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor,
        "pre_set_shielded_instance_integrity_policy",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.SetShieldedInstanceIntegrityPolicyInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.set_shielded_instance_integrity_policy_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_set_shielded_instance_integrity_policy_unary_rest_bad_request(
    transport: str = "rest",
    request_type=compute.SetShieldedInstanceIntegrityPolicyInstanceRequest,
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["shielded_instance_integrity_policy_resource"] = {
        "update_auto_learn_policy": True
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.set_shielded_instance_integrity_policy_unary(request)


def test_set_shielded_instance_integrity_policy_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            shielded_instance_integrity_policy_resource=compute.ShieldedInstanceIntegrityPolicy(
                update_auto_learn_policy=True
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.set_shielded_instance_integrity_policy_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/setShieldedInstanceIntegrityPolicy"
            % client.transport._host,
            args[1],
        )


def test_set_shielded_instance_integrity_policy_unary_rest_flattened_error(
    transport: str = "rest",
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_shielded_instance_integrity_policy_unary(
            compute.SetShieldedInstanceIntegrityPolicyInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            shielded_instance_integrity_policy_resource=compute.ShieldedInstanceIntegrityPolicy(
                update_auto_learn_policy=True
            ),
        )


def test_set_shielded_instance_integrity_policy_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.SetTagsInstanceRequest, dict,])
def test_set_tags_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["tags_resource"] = {
        "fingerprint": "fingerprint_value",
        "items": ["items_value_1", "items_value_2"],
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.set_tags_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_set_tags_unary_rest_required_fields(
    request_type=compute.SetTagsInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_tags._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).set_tags._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.set_tags_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_set_tags_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.set_tags._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",)) & set(("instance", "project", "tagsResource", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_set_tags_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_set_tags"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_set_tags"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.SetTagsInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.set_tags_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_set_tags_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.SetTagsInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["tags_resource"] = {
        "fingerprint": "fingerprint_value",
        "items": ["items_value_1", "items_value_2"],
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.set_tags_unary(request)


def test_set_tags_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            tags_resource=compute.Tags(fingerprint="fingerprint_value"),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.set_tags_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/setTags"
            % client.transport._host,
            args[1],
        )


def test_set_tags_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_tags_unary(
            compute.SetTagsInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            tags_resource=compute.Tags(fingerprint="fingerprint_value"),
        )


def test_set_tags_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.SimulateMaintenanceEventInstanceRequest, dict,]
)
def test_simulate_maintenance_event_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.simulate_maintenance_event_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_simulate_maintenance_event_unary_rest_required_fields(
    request_type=compute.SimulateMaintenanceEventInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).simulate_maintenance_event._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).simulate_maintenance_event._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.simulate_maintenance_event_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_simulate_maintenance_event_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.simulate_maintenance_event._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("instance", "project", "zone",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_simulate_maintenance_event_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_simulate_maintenance_event"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_simulate_maintenance_event"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.SimulateMaintenanceEventInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.simulate_maintenance_event_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_simulate_maintenance_event_unary_rest_bad_request(
    transport: str = "rest",
    request_type=compute.SimulateMaintenanceEventInstanceRequest,
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.simulate_maintenance_event_unary(request)


def test_simulate_maintenance_event_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value", zone="zone_value", instance="instance_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.simulate_maintenance_event_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/simulateMaintenanceEvent"
            % client.transport._host,
            args[1],
        )


def test_simulate_maintenance_event_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.simulate_maintenance_event_unary(
            compute.SimulateMaintenanceEventInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
        )


def test_simulate_maintenance_event_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.StartInstanceRequest, dict,])
def test_start_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.start_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_start_unary_rest_required_fields(request_type=compute.StartInstanceRequest):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).start._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).start._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.start_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_start_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.start._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",)) & set(("instance", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_start_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_start"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_start"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.StartInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.start_unary(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()


def test_start_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.StartInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.start_unary(request)


def test_start_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value", zone="zone_value", instance="instance_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.start_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/start"
            % client.transport._host,
            args[1],
        )


def test_start_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.start_unary(
            compute.StartInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
        )


def test_start_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.StartWithEncryptionKeyInstanceRequest, dict,]
)
def test_start_with_encryption_key_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_start_with_encryption_key_request_resource"] = {
        "disks": [
            {
                "disk_encryption_key": {
                    "kms_key_name": "kms_key_name_value",
                    "kms_key_service_account": "kms_key_service_account_value",
                    "raw_key": "raw_key_value",
                    "rsa_encrypted_key": "rsa_encrypted_key_value",
                    "sha256": "sha256_value",
                },
                "source": "source_value",
            }
        ]
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.start_with_encryption_key_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_start_with_encryption_key_unary_rest_required_fields(
    request_type=compute.StartWithEncryptionKeyInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).start_with_encryption_key._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).start_with_encryption_key._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.start_with_encryption_key_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_start_with_encryption_key_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.start_with_encryption_key._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",))
        & set(
            (
                "instance",
                "instancesStartWithEncryptionKeyRequestResource",
                "project",
                "zone",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_start_with_encryption_key_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_start_with_encryption_key"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_start_with_encryption_key"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.StartWithEncryptionKeyInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.start_with_encryption_key_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_start_with_encryption_key_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.StartWithEncryptionKeyInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instances_start_with_encryption_key_request_resource"] = {
        "disks": [
            {
                "disk_encryption_key": {
                    "kms_key_name": "kms_key_name_value",
                    "kms_key_service_account": "kms_key_service_account_value",
                    "raw_key": "raw_key_value",
                    "rsa_encrypted_key": "rsa_encrypted_key_value",
                    "sha256": "sha256_value",
                },
                "source": "source_value",
            }
        ]
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.start_with_encryption_key_unary(request)


def test_start_with_encryption_key_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_start_with_encryption_key_request_resource=compute.InstancesStartWithEncryptionKeyRequest(
                disks=[
                    compute.CustomerEncryptionKeyProtectedDisk(
                        disk_encryption_key=compute.CustomerEncryptionKey(
                            kms_key_name="kms_key_name_value"
                        )
                    )
                ]
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.start_with_encryption_key_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/startWithEncryptionKey"
            % client.transport._host,
            args[1],
        )


def test_start_with_encryption_key_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.start_with_encryption_key_unary(
            compute.StartWithEncryptionKeyInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instances_start_with_encryption_key_request_resource=compute.InstancesStartWithEncryptionKeyRequest(
                disks=[
                    compute.CustomerEncryptionKeyProtectedDisk(
                        disk_encryption_key=compute.CustomerEncryptionKey(
                            kms_key_name="kms_key_name_value"
                        )
                    )
                ]
            ),
        )


def test_start_with_encryption_key_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.StopInstanceRequest, dict,])
def test_stop_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.stop_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_stop_unary_rest_required_fields(request_type=compute.StopInstanceRequest):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).stop._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).stop._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.stop_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_stop_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.stop._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",)) & set(("instance", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_stop_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_stop"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_stop"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.StopInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.stop_unary(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()


def test_stop_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.StopInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.stop_unary(request)


def test_stop_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value", zone="zone_value", instance="instance_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.stop_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/stop"
            % client.transport._host,
            args[1],
        )


def test_stop_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.stop_unary(
            compute.StopInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
        )


def test_stop_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.TestIamPermissionsInstanceRequest, dict,]
)
def test_test_iam_permissions_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "resource": "sample3"}
    request_init["test_permissions_request_resource"] = {
        "permissions": ["permissions_value_1", "permissions_value_2"]
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.TestPermissionsResponse(
            permissions=["permissions_value"],
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.TestPermissionsResponse.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.test_iam_permissions(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.TestPermissionsResponse)
    assert response.permissions == ["permissions_value"]


def test_test_iam_permissions_rest_required_fields(
    request_type=compute.TestIamPermissionsInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["project"] = ""
    request_init["resource"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).test_iam_permissions._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["project"] = "project_value"
    jsonified_request["resource"] = "resource_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).test_iam_permissions._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "resource" in jsonified_request
    assert jsonified_request["resource"] == "resource_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.TestPermissionsResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.TestPermissionsResponse.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.test_iam_permissions(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_test_iam_permissions_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.test_iam_permissions._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(())
        & set(("project", "resource", "testPermissionsRequestResource", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_test_iam_permissions_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_test_iam_permissions"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_test_iam_permissions"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.TestPermissionsResponse.to_json(
            compute.TestPermissionsResponse()
        )

        request = compute.TestIamPermissionsInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.TestPermissionsResponse

        client.test_iam_permissions(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_test_iam_permissions_rest_bad_request(
    transport: str = "rest", request_type=compute.TestIamPermissionsInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "resource": "sample3"}
    request_init["test_permissions_request_resource"] = {
        "permissions": ["permissions_value_1", "permissions_value_2"]
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.test_iam_permissions(request)


def test_test_iam_permissions_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.TestPermissionsResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "resource": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            resource="resource_value",
            test_permissions_request_resource=compute.TestPermissionsRequest(
                permissions=["permissions_value"]
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.TestPermissionsResponse.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.test_iam_permissions(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{resource}/testIamPermissions"
            % client.transport._host,
            args[1],
        )


def test_test_iam_permissions_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.test_iam_permissions(
            compute.TestIamPermissionsInstanceRequest(),
            project="project_value",
            zone="zone_value",
            resource="resource_value",
            test_permissions_request_resource=compute.TestPermissionsRequest(
                permissions=["permissions_value"]
            ),
        )


def test_test_iam_permissions_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize("request_type", [compute.UpdateInstanceRequest, dict,])
def test_update_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instance_resource"] = {
        "advanced_machine_features": {
            "enable_nested_virtualization": True,
            "threads_per_core": 1689,
        },
        "can_ip_forward": True,
        "confidential_instance_config": {"enable_confidential_compute": True},
        "cpu_platform": "cpu_platform_value",
        "creation_timestamp": "creation_timestamp_value",
        "deletion_protection": True,
        "description": "description_value",
        "disks": [
            {
                "auto_delete": True,
                "boot": True,
                "device_name": "device_name_value",
                "disk_encryption_key": {
                    "kms_key_name": "kms_key_name_value",
                    "kms_key_service_account": "kms_key_service_account_value",
                    "raw_key": "raw_key_value",
                    "rsa_encrypted_key": "rsa_encrypted_key_value",
                    "sha256": "sha256_value",
                },
                "disk_size_gb": 1261,
                "guest_os_features": [{"type_": "type__value"}],
                "index": 536,
                "initialize_params": {
                    "description": "description_value",
                    "disk_name": "disk_name_value",
                    "disk_size_gb": 1261,
                    "disk_type": "disk_type_value",
                    "labels": {},
                    "on_update_action": "on_update_action_value",
                    "provisioned_iops": 1740,
                    "resource_policies": [
                        "resource_policies_value_1",
                        "resource_policies_value_2",
                    ],
                    "source_image": "source_image_value",
                    "source_image_encryption_key": {
                        "kms_key_name": "kms_key_name_value",
                        "kms_key_service_account": "kms_key_service_account_value",
                        "raw_key": "raw_key_value",
                        "rsa_encrypted_key": "rsa_encrypted_key_value",
                        "sha256": "sha256_value",
                    },
                    "source_snapshot": "source_snapshot_value",
                    "source_snapshot_encryption_key": {
                        "kms_key_name": "kms_key_name_value",
                        "kms_key_service_account": "kms_key_service_account_value",
                        "raw_key": "raw_key_value",
                        "rsa_encrypted_key": "rsa_encrypted_key_value",
                        "sha256": "sha256_value",
                    },
                },
                "interface": "interface_value",
                "kind": "kind_value",
                "licenses": ["licenses_value_1", "licenses_value_2"],
                "mode": "mode_value",
                "shielded_instance_initial_state": {
                    "dbs": [
                        {"content": "content_value", "file_type": "file_type_value"}
                    ],
                    "dbxs": [
                        {"content": "content_value", "file_type": "file_type_value"}
                    ],
                    "keks": [
                        {"content": "content_value", "file_type": "file_type_value"}
                    ],
                    "pk": {"content": "content_value", "file_type": "file_type_value"},
                },
                "source": "source_value",
                "type_": "type__value",
            }
        ],
        "display_device": {"enable_display": True},
        "fingerprint": "fingerprint_value",
        "guest_accelerators": [
            {"accelerator_count": 1805, "accelerator_type": "accelerator_type_value"}
        ],
        "hostname": "hostname_value",
        "id": 205,
        "kind": "kind_value",
        "label_fingerprint": "label_fingerprint_value",
        "labels": {},
        "last_start_timestamp": "last_start_timestamp_value",
        "last_stop_timestamp": "last_stop_timestamp_value",
        "last_suspended_timestamp": "last_suspended_timestamp_value",
        "machine_type": "machine_type_value",
        "metadata": {
            "fingerprint": "fingerprint_value",
            "items": [{"key": "key_value", "value": "value_value"}],
            "kind": "kind_value",
        },
        "min_cpu_platform": "min_cpu_platform_value",
        "name": "name_value",
        "network_interfaces": [
            {
                "access_configs": [
                    {
                        "external_ipv6": "external_ipv6_value",
                        "external_ipv6_prefix_length": 2837,
                        "kind": "kind_value",
                        "name": "name_value",
                        "nat_i_p": "nat_i_p_value",
                        "network_tier": "network_tier_value",
                        "public_ptr_domain_name": "public_ptr_domain_name_value",
                        "set_public_ptr": True,
                        "type_": "type__value",
                    }
                ],
                "alias_ip_ranges": [
                    {
                        "ip_cidr_range": "ip_cidr_range_value",
                        "subnetwork_range_name": "subnetwork_range_name_value",
                    }
                ],
                "fingerprint": "fingerprint_value",
                "ipv6_access_configs": [
                    {
                        "external_ipv6": "external_ipv6_value",
                        "external_ipv6_prefix_length": 2837,
                        "kind": "kind_value",
                        "name": "name_value",
                        "nat_i_p": "nat_i_p_value",
                        "network_tier": "network_tier_value",
                        "public_ptr_domain_name": "public_ptr_domain_name_value",
                        "set_public_ptr": True,
                        "type_": "type__value",
                    }
                ],
                "ipv6_access_type": "ipv6_access_type_value",
                "ipv6_address": "ipv6_address_value",
                "kind": "kind_value",
                "name": "name_value",
                "network": "network_value",
                "network_i_p": "network_i_p_value",
                "nic_type": "nic_type_value",
                "queue_count": 1197,
                "stack_type": "stack_type_value",
                "subnetwork": "subnetwork_value",
            }
        ],
        "private_ipv6_google_access": "private_ipv6_google_access_value",
        "reservation_affinity": {
            "consume_reservation_type": "consume_reservation_type_value",
            "key": "key_value",
            "values": ["values_value_1", "values_value_2"],
        },
        "resource_policies": ["resource_policies_value_1", "resource_policies_value_2"],
        "satisfies_pzs": True,
        "scheduling": {
            "automatic_restart": True,
            "location_hint": "location_hint_value",
            "min_node_cpus": 1379,
            "node_affinities": [
                {
                    "key": "key_value",
                    "operator": "operator_value",
                    "values": ["values_value_1", "values_value_2"],
                }
            ],
            "on_host_maintenance": "on_host_maintenance_value",
            "preemptible": True,
        },
        "self_link": "self_link_value",
        "service_accounts": [
            {"email": "email_value", "scopes": ["scopes_value_1", "scopes_value_2"]}
        ],
        "shielded_instance_config": {
            "enable_integrity_monitoring": True,
            "enable_secure_boot": True,
            "enable_vtpm": True,
        },
        "shielded_instance_integrity_policy": {"update_auto_learn_policy": True},
        "start_restricted": True,
        "status": "status_value",
        "status_message": "status_message_value",
        "tags": {
            "fingerprint": "fingerprint_value",
            "items": ["items_value_1", "items_value_2"],
        },
        "zone": "zone_value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.update_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_update_unary_rest_required_fields(request_type=compute.UpdateInstanceRequest):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        ("minimal_action", "most_disruptive_allowed_action", "request_id",)
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "put",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.update_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_update_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.update._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("minimalAction", "mostDisruptiveAllowedAction", "requestId",))
        & set(("instance", "instanceResource", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_update_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_update"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_update"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.UpdateInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.update_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_update_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.UpdateInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["instance_resource"] = {
        "advanced_machine_features": {
            "enable_nested_virtualization": True,
            "threads_per_core": 1689,
        },
        "can_ip_forward": True,
        "confidential_instance_config": {"enable_confidential_compute": True},
        "cpu_platform": "cpu_platform_value",
        "creation_timestamp": "creation_timestamp_value",
        "deletion_protection": True,
        "description": "description_value",
        "disks": [
            {
                "auto_delete": True,
                "boot": True,
                "device_name": "device_name_value",
                "disk_encryption_key": {
                    "kms_key_name": "kms_key_name_value",
                    "kms_key_service_account": "kms_key_service_account_value",
                    "raw_key": "raw_key_value",
                    "rsa_encrypted_key": "rsa_encrypted_key_value",
                    "sha256": "sha256_value",
                },
                "disk_size_gb": 1261,
                "guest_os_features": [{"type_": "type__value"}],
                "index": 536,
                "initialize_params": {
                    "description": "description_value",
                    "disk_name": "disk_name_value",
                    "disk_size_gb": 1261,
                    "disk_type": "disk_type_value",
                    "labels": {},
                    "on_update_action": "on_update_action_value",
                    "provisioned_iops": 1740,
                    "resource_policies": [
                        "resource_policies_value_1",
                        "resource_policies_value_2",
                    ],
                    "source_image": "source_image_value",
                    "source_image_encryption_key": {
                        "kms_key_name": "kms_key_name_value",
                        "kms_key_service_account": "kms_key_service_account_value",
                        "raw_key": "raw_key_value",
                        "rsa_encrypted_key": "rsa_encrypted_key_value",
                        "sha256": "sha256_value",
                    },
                    "source_snapshot": "source_snapshot_value",
                    "source_snapshot_encryption_key": {
                        "kms_key_name": "kms_key_name_value",
                        "kms_key_service_account": "kms_key_service_account_value",
                        "raw_key": "raw_key_value",
                        "rsa_encrypted_key": "rsa_encrypted_key_value",
                        "sha256": "sha256_value",
                    },
                },
                "interface": "interface_value",
                "kind": "kind_value",
                "licenses": ["licenses_value_1", "licenses_value_2"],
                "mode": "mode_value",
                "shielded_instance_initial_state": {
                    "dbs": [
                        {"content": "content_value", "file_type": "file_type_value"}
                    ],
                    "dbxs": [
                        {"content": "content_value", "file_type": "file_type_value"}
                    ],
                    "keks": [
                        {"content": "content_value", "file_type": "file_type_value"}
                    ],
                    "pk": {"content": "content_value", "file_type": "file_type_value"},
                },
                "source": "source_value",
                "type_": "type__value",
            }
        ],
        "display_device": {"enable_display": True},
        "fingerprint": "fingerprint_value",
        "guest_accelerators": [
            {"accelerator_count": 1805, "accelerator_type": "accelerator_type_value"}
        ],
        "hostname": "hostname_value",
        "id": 205,
        "kind": "kind_value",
        "label_fingerprint": "label_fingerprint_value",
        "labels": {},
        "last_start_timestamp": "last_start_timestamp_value",
        "last_stop_timestamp": "last_stop_timestamp_value",
        "last_suspended_timestamp": "last_suspended_timestamp_value",
        "machine_type": "machine_type_value",
        "metadata": {
            "fingerprint": "fingerprint_value",
            "items": [{"key": "key_value", "value": "value_value"}],
            "kind": "kind_value",
        },
        "min_cpu_platform": "min_cpu_platform_value",
        "name": "name_value",
        "network_interfaces": [
            {
                "access_configs": [
                    {
                        "external_ipv6": "external_ipv6_value",
                        "external_ipv6_prefix_length": 2837,
                        "kind": "kind_value",
                        "name": "name_value",
                        "nat_i_p": "nat_i_p_value",
                        "network_tier": "network_tier_value",
                        "public_ptr_domain_name": "public_ptr_domain_name_value",
                        "set_public_ptr": True,
                        "type_": "type__value",
                    }
                ],
                "alias_ip_ranges": [
                    {
                        "ip_cidr_range": "ip_cidr_range_value",
                        "subnetwork_range_name": "subnetwork_range_name_value",
                    }
                ],
                "fingerprint": "fingerprint_value",
                "ipv6_access_configs": [
                    {
                        "external_ipv6": "external_ipv6_value",
                        "external_ipv6_prefix_length": 2837,
                        "kind": "kind_value",
                        "name": "name_value",
                        "nat_i_p": "nat_i_p_value",
                        "network_tier": "network_tier_value",
                        "public_ptr_domain_name": "public_ptr_domain_name_value",
                        "set_public_ptr": True,
                        "type_": "type__value",
                    }
                ],
                "ipv6_access_type": "ipv6_access_type_value",
                "ipv6_address": "ipv6_address_value",
                "kind": "kind_value",
                "name": "name_value",
                "network": "network_value",
                "network_i_p": "network_i_p_value",
                "nic_type": "nic_type_value",
                "queue_count": 1197,
                "stack_type": "stack_type_value",
                "subnetwork": "subnetwork_value",
            }
        ],
        "private_ipv6_google_access": "private_ipv6_google_access_value",
        "reservation_affinity": {
            "consume_reservation_type": "consume_reservation_type_value",
            "key": "key_value",
            "values": ["values_value_1", "values_value_2"],
        },
        "resource_policies": ["resource_policies_value_1", "resource_policies_value_2"],
        "satisfies_pzs": True,
        "scheduling": {
            "automatic_restart": True,
            "location_hint": "location_hint_value",
            "min_node_cpus": 1379,
            "node_affinities": [
                {
                    "key": "key_value",
                    "operator": "operator_value",
                    "values": ["values_value_1", "values_value_2"],
                }
            ],
            "on_host_maintenance": "on_host_maintenance_value",
            "preemptible": True,
        },
        "self_link": "self_link_value",
        "service_accounts": [
            {"email": "email_value", "scopes": ["scopes_value_1", "scopes_value_2"]}
        ],
        "shielded_instance_config": {
            "enable_integrity_monitoring": True,
            "enable_secure_boot": True,
            "enable_vtpm": True,
        },
        "shielded_instance_integrity_policy": {"update_auto_learn_policy": True},
        "start_restricted": True,
        "status": "status_value",
        "status_message": "status_message_value",
        "tags": {
            "fingerprint": "fingerprint_value",
            "items": ["items_value_1", "items_value_2"],
        },
        "zone": "zone_value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.update_unary(request)


def test_update_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instance_resource=compute.Instance(
                advanced_machine_features=compute.AdvancedMachineFeatures(
                    enable_nested_virtualization=True
                )
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.update_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}"
            % client.transport._host,
            args[1],
        )


def test_update_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_unary(
            compute.UpdateInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            instance_resource=compute.Instance(
                advanced_machine_features=compute.AdvancedMachineFeatures(
                    enable_nested_virtualization=True
                )
            ),
        )


def test_update_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.UpdateAccessConfigInstanceRequest, dict,]
)
def test_update_access_config_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["access_config_resource"] = {
        "external_ipv6": "external_ipv6_value",
        "external_ipv6_prefix_length": 2837,
        "kind": "kind_value",
        "name": "name_value",
        "nat_i_p": "nat_i_p_value",
        "network_tier": "network_tier_value",
        "public_ptr_domain_name": "public_ptr_domain_name_value",
        "set_public_ptr": True,
        "type_": "type__value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.update_access_config_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_update_access_config_unary_rest_required_fields(
    request_type=compute.UpdateAccessConfigInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["network_interface"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped
    assert "networkInterface" not in jsonified_request

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_access_config._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "networkInterface" in jsonified_request
    assert jsonified_request["networkInterface"] == request_init["network_interface"]

    jsonified_request["instance"] = "instance_value"
    jsonified_request["networkInterface"] = "network_interface_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_access_config._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("network_interface", "request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "networkInterface" in jsonified_request
    assert jsonified_request["networkInterface"] == "network_interface_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.update_access_config_unary(request)

            expected_params = [
                ("networkInterface", "",),
            ]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_update_access_config_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.update_access_config._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("networkInterface", "requestId",))
        & set(
            ("accessConfigResource", "instance", "networkInterface", "project", "zone",)
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_update_access_config_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_update_access_config"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_update_access_config"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.UpdateAccessConfigInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.update_access_config_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_update_access_config_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.UpdateAccessConfigInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["access_config_resource"] = {
        "external_ipv6": "external_ipv6_value",
        "external_ipv6_prefix_length": 2837,
        "kind": "kind_value",
        "name": "name_value",
        "nat_i_p": "nat_i_p_value",
        "network_tier": "network_tier_value",
        "public_ptr_domain_name": "public_ptr_domain_name_value",
        "set_public_ptr": True,
        "type_": "type__value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.update_access_config_unary(request)


def test_update_access_config_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            network_interface="network_interface_value",
            access_config_resource=compute.AccessConfig(
                external_ipv6="external_ipv6_value"
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.update_access_config_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/updateAccessConfig"
            % client.transport._host,
            args[1],
        )


def test_update_access_config_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_access_config_unary(
            compute.UpdateAccessConfigInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            network_interface="network_interface_value",
            access_config_resource=compute.AccessConfig(
                external_ipv6="external_ipv6_value"
            ),
        )


def test_update_access_config_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.UpdateDisplayDeviceInstanceRequest, dict,]
)
def test_update_display_device_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["display_device_resource"] = {"enable_display": True}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.update_display_device_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_update_display_device_unary_rest_required_fields(
    request_type=compute.UpdateDisplayDeviceInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_display_device._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_display_device._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "patch",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.update_display_device_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_update_display_device_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.update_display_device._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("requestId",))
        & set(("displayDeviceResource", "instance", "project", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_update_display_device_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_update_display_device"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_update_display_device"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.UpdateDisplayDeviceInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.update_display_device_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_update_display_device_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.UpdateDisplayDeviceInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["display_device_resource"] = {"enable_display": True}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.update_display_device_unary(request)


def test_update_display_device_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            display_device_resource=compute.DisplayDevice(enable_display=True),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.update_display_device_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/updateDisplayDevice"
            % client.transport._host,
            args[1],
        )


def test_update_display_device_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_display_device_unary(
            compute.UpdateDisplayDeviceInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            display_device_resource=compute.DisplayDevice(enable_display=True),
        )


def test_update_display_device_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.UpdateNetworkInterfaceInstanceRequest, dict,]
)
def test_update_network_interface_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["network_interface_resource"] = {
        "access_configs": [
            {
                "external_ipv6": "external_ipv6_value",
                "external_ipv6_prefix_length": 2837,
                "kind": "kind_value",
                "name": "name_value",
                "nat_i_p": "nat_i_p_value",
                "network_tier": "network_tier_value",
                "public_ptr_domain_name": "public_ptr_domain_name_value",
                "set_public_ptr": True,
                "type_": "type__value",
            }
        ],
        "alias_ip_ranges": [
            {
                "ip_cidr_range": "ip_cidr_range_value",
                "subnetwork_range_name": "subnetwork_range_name_value",
            }
        ],
        "fingerprint": "fingerprint_value",
        "ipv6_access_configs": [
            {
                "external_ipv6": "external_ipv6_value",
                "external_ipv6_prefix_length": 2837,
                "kind": "kind_value",
                "name": "name_value",
                "nat_i_p": "nat_i_p_value",
                "network_tier": "network_tier_value",
                "public_ptr_domain_name": "public_ptr_domain_name_value",
                "set_public_ptr": True,
                "type_": "type__value",
            }
        ],
        "ipv6_access_type": "ipv6_access_type_value",
        "ipv6_address": "ipv6_address_value",
        "kind": "kind_value",
        "name": "name_value",
        "network": "network_value",
        "network_i_p": "network_i_p_value",
        "nic_type": "nic_type_value",
        "queue_count": 1197,
        "stack_type": "stack_type_value",
        "subnetwork": "subnetwork_value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.update_network_interface_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_update_network_interface_unary_rest_required_fields(
    request_type=compute.UpdateNetworkInterfaceInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["network_interface"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped
    assert "networkInterface" not in jsonified_request

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_network_interface._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "networkInterface" in jsonified_request
    assert jsonified_request["networkInterface"] == request_init["network_interface"]

    jsonified_request["instance"] = "instance_value"
    jsonified_request["networkInterface"] = "network_interface_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_network_interface._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("network_interface", "request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "networkInterface" in jsonified_request
    assert jsonified_request["networkInterface"] == "network_interface_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "patch",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.update_network_interface_unary(request)

            expected_params = [
                ("networkInterface", "",),
            ]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_update_network_interface_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.update_network_interface._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("networkInterface", "requestId",))
        & set(
            (
                "instance",
                "networkInterface",
                "networkInterfaceResource",
                "project",
                "zone",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_update_network_interface_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_update_network_interface"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_update_network_interface"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.UpdateNetworkInterfaceInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.update_network_interface_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_update_network_interface_unary_rest_bad_request(
    transport: str = "rest", request_type=compute.UpdateNetworkInterfaceInstanceRequest
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["network_interface_resource"] = {
        "access_configs": [
            {
                "external_ipv6": "external_ipv6_value",
                "external_ipv6_prefix_length": 2837,
                "kind": "kind_value",
                "name": "name_value",
                "nat_i_p": "nat_i_p_value",
                "network_tier": "network_tier_value",
                "public_ptr_domain_name": "public_ptr_domain_name_value",
                "set_public_ptr": True,
                "type_": "type__value",
            }
        ],
        "alias_ip_ranges": [
            {
                "ip_cidr_range": "ip_cidr_range_value",
                "subnetwork_range_name": "subnetwork_range_name_value",
            }
        ],
        "fingerprint": "fingerprint_value",
        "ipv6_access_configs": [
            {
                "external_ipv6": "external_ipv6_value",
                "external_ipv6_prefix_length": 2837,
                "kind": "kind_value",
                "name": "name_value",
                "nat_i_p": "nat_i_p_value",
                "network_tier": "network_tier_value",
                "public_ptr_domain_name": "public_ptr_domain_name_value",
                "set_public_ptr": True,
                "type_": "type__value",
            }
        ],
        "ipv6_access_type": "ipv6_access_type_value",
        "ipv6_address": "ipv6_address_value",
        "kind": "kind_value",
        "name": "name_value",
        "network": "network_value",
        "network_i_p": "network_i_p_value",
        "nic_type": "nic_type_value",
        "queue_count": 1197,
        "stack_type": "stack_type_value",
        "subnetwork": "subnetwork_value",
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.update_network_interface_unary(request)


def test_update_network_interface_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            network_interface="network_interface_value",
            network_interface_resource=compute.NetworkInterface(
                access_configs=[
                    compute.AccessConfig(external_ipv6="external_ipv6_value")
                ]
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.update_network_interface_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/updateNetworkInterface"
            % client.transport._host,
            args[1],
        )


def test_update_network_interface_unary_rest_flattened_error(transport: str = "rest"):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_network_interface_unary(
            compute.UpdateNetworkInterfaceInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            network_interface="network_interface_value",
            network_interface_resource=compute.NetworkInterface(
                access_configs=[
                    compute.AccessConfig(external_ipv6="external_ipv6_value")
                ]
            ),
        )


def test_update_network_interface_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type", [compute.UpdateShieldedInstanceConfigInstanceRequest, dict,]
)
def test_update_shielded_instance_config_unary_rest(request_type):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["shielded_instance_config_resource"] = {
        "enable_integrity_monitoring": True,
        "enable_secure_boot": True,
        "enable_vtpm": True,
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
            client_operation_id="client_operation_id_value",
            creation_timestamp="creation_timestamp_value",
            description="description_value",
            end_time="end_time_value",
            http_error_message="http_error_message_value",
            http_error_status_code=2374,
            id=205,
            insert_time="insert_time_value",
            kind="kind_value",
            name="name_value",
            operation_group_id="operation_group_id_value",
            operation_type="operation_type_value",
            progress=885,
            region="region_value",
            self_link="self_link_value",
            start_time="start_time_value",
            status=compute.Operation.Status.DONE,
            status_message="status_message_value",
            target_id=947,
            target_link="target_link_value",
            user="user_value",
            zone="zone_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.update_shielded_instance_config_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == "client_operation_id_value"
    assert response.creation_timestamp == "creation_timestamp_value"
    assert response.description == "description_value"
    assert response.end_time == "end_time_value"
    assert response.http_error_message == "http_error_message_value"
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == "insert_time_value"
    assert response.kind == "kind_value"
    assert response.name == "name_value"
    assert response.operation_group_id == "operation_group_id_value"
    assert response.operation_type == "operation_type_value"
    assert response.progress == 885
    assert response.region == "region_value"
    assert response.self_link == "self_link_value"
    assert response.start_time == "start_time_value"
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == "status_message_value"
    assert response.target_id == 947
    assert response.target_link == "target_link_value"
    assert response.user == "user_value"
    assert response.zone == "zone_value"


def test_update_shielded_instance_config_unary_rest_required_fields(
    request_type=compute.UpdateShieldedInstanceConfigInstanceRequest,
):
    transport_class = transports.InstancesRestTransport

    request_init = {}
    request_init["instance"] = ""
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(
        request_type.to_json(
            request, including_default_value_fields=False, use_integers_for_enums=False
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_shielded_instance_config._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["instance"] = "instance_value"
    jsonified_request["project"] = "project_value"
    jsonified_request["zone"] = "zone_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_shielded_instance_config._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("request_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "instance" in jsonified_request
    assert jsonified_request["instance"] == "instance_value"
    assert "project" in jsonified_request
    assert jsonified_request["project"] == "project_value"
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == "zone_value"

    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "patch",
                "query_params": request_init,
            }
            transcode_result["body"] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.update_shielded_instance_config_unary(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_update_shielded_instance_config_unary_rest_unset_required_fields():
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.update_shielded_instance_config._get_unset_required_fields(
        {}
    )
    assert set(unset_fields) == (
        set(("requestId",))
        & set(("instance", "project", "shieldedInstanceConfigResource", "zone",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_update_shielded_instance_config_unary_rest_interceptors(null_interceptor):
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.InstancesRestInterceptor(),
    )
    client = InstancesClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.InstancesRestInterceptor, "post_update_shielded_instance_config"
    ) as post, mock.patch.object(
        transports.InstancesRestInterceptor, "pre_update_shielded_instance_config"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()

        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": None,
            "query_params": {},
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = compute.Operation.to_json(compute.Operation())

        request = compute.UpdateShieldedInstanceConfigInstanceRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = compute.Operation

        client.update_shielded_instance_config_unary(
            request, metadata=[("key", "val"), ("cephalopod", "squid"),]
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_update_shielded_instance_config_unary_rest_bad_request(
    transport: str = "rest",
    request_type=compute.UpdateShieldedInstanceConfigInstanceRequest,
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"project": "sample1", "zone": "sample2", "instance": "sample3"}
    request_init["shielded_instance_config_resource"] = {
        "enable_integrity_monitoring": True,
        "enable_secure_boot": True,
        "enable_vtpm": True,
    }
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.update_shielded_instance_config_unary(request)


def test_update_shielded_instance_config_unary_rest_flattened():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "project": "sample1",
            "zone": "sample2",
            "instance": "sample3",
        }

        # get truthy value for each flattened field
        mock_args = dict(
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            shielded_instance_config_resource=compute.ShieldedInstanceConfig(
                enable_integrity_monitoring=True
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.update_shielded_instance_config_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/compute/v1/projects/{project}/zones/{zone}/instances/{instance}/updateShieldedInstanceConfig"
            % client.transport._host,
            args[1],
        )


def test_update_shielded_instance_config_unary_rest_flattened_error(
    transport: str = "rest",
):
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_shielded_instance_config_unary(
            compute.UpdateShieldedInstanceConfigInstanceRequest(),
            project="project_value",
            zone="zone_value",
            instance="instance_value",
            shielded_instance_config_resource=compute.ShieldedInstanceConfig(
                enable_integrity_monitoring=True
            ),
        )


def test_update_shielded_instance_config_unary_rest_error():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = InstancesClient(
            credentials=ga_credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = InstancesClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide an api_key and a transport instance.
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = InstancesClient(client_options=options, transport=transport,)

    # It is an error to provide an api_key and a credential.
    options = mock.Mock()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = InstancesClient(
            client_options=options, credentials=ga_credentials.AnonymousCredentials()
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = InstancesClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.InstancesRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    client = InstancesClient(transport=transport)
    assert client.transport is transport


@pytest.mark.parametrize("transport_class", [transports.InstancesRestTransport,])
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(google.auth, "default") as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()


def test_instances_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(core_exceptions.DuplicateCredentialArgs):
        transport = transports.InstancesTransport(
            credentials=ga_credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_instances_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.compute_v1.services.instances.transports.InstancesTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.InstancesTransport(
            credentials=ga_credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "add_access_config",
        "add_resource_policies",
        "aggregated_list",
        "attach_disk",
        "bulk_insert",
        "delete",
        "delete_access_config",
        "detach_disk",
        "get",
        "get_effective_firewalls",
        "get_guest_attributes",
        "get_iam_policy",
        "get_screenshot",
        "get_serial_port_output",
        "get_shielded_instance_identity",
        "insert",
        "list",
        "list_referrers",
        "remove_resource_policies",
        "reset",
        "send_diagnostic_interrupt",
        "set_deletion_protection",
        "set_disk_auto_delete",
        "set_iam_policy",
        "set_labels",
        "set_machine_resources",
        "set_machine_type",
        "set_metadata",
        "set_min_cpu_platform",
        "set_scheduling",
        "set_service_account",
        "set_shielded_instance_integrity_policy",
        "set_tags",
        "simulate_maintenance_event",
        "start",
        "start_with_encryption_key",
        "stop",
        "test_iam_permissions",
        "update",
        "update_access_config",
        "update_display_device",
        "update_network_interface",
        "update_shielded_instance_config",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    with pytest.raises(NotImplementedError):
        transport.close()


def test_instances_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.compute_v1.services.instances.transports.InstancesTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.InstancesTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=None,
            default_scopes=(
                "https://www.googleapis.com/auth/compute",
                "https://www.googleapis.com/auth/cloud-platform",
            ),
            quota_project_id="octopus",
        )


def test_instances_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(google.auth, "default", autospec=True) as adc, mock.patch(
        "google.cloud.compute_v1.services.instances.transports.InstancesTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.InstancesTransport()
        adc.assert_called_once()


def test_instances_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        InstancesClient()
        adc.assert_called_once_with(
            scopes=None,
            default_scopes=(
                "https://www.googleapis.com/auth/compute",
                "https://www.googleapis.com/auth/cloud-platform",
            ),
            quota_project_id=None,
        )


def test_instances_http_transport_client_cert_source_for_mtls():
    cred = ga_credentials.AnonymousCredentials()
    with mock.patch(
        "google.auth.transport.requests.AuthorizedSession.configure_mtls_channel"
    ) as mock_configure_mtls_channel:
        transports.InstancesRestTransport(
            credentials=cred, client_cert_source_for_mtls=client_cert_source_callback
        )
        mock_configure_mtls_channel.assert_called_once_with(client_cert_source_callback)


def test_instances_host_no_port():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="compute.googleapis.com"
        ),
    )
    assert client.transport._host == "compute.googleapis.com:443"


def test_instances_host_with_port():
    client = InstancesClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="compute.googleapis.com:8000"
        ),
    )
    assert client.transport._host == "compute.googleapis.com:8000"


def test_common_billing_account_path():
    billing_account = "squid"
    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = InstancesClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "clam",
    }
    path = InstancesClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = InstancesClient.parse_common_billing_account_path(path)
    assert expected == actual


def test_common_folder_path():
    folder = "whelk"
    expected = "folders/{folder}".format(folder=folder,)
    actual = InstancesClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "octopus",
    }
    path = InstancesClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = InstancesClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "oyster"
    expected = "organizations/{organization}".format(organization=organization,)
    actual = InstancesClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "nudibranch",
    }
    path = InstancesClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = InstancesClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "cuttlefish"
    expected = "projects/{project}".format(project=project,)
    actual = InstancesClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "mussel",
    }
    path = InstancesClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = InstancesClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "winkle"
    location = "nautilus"
    expected = "projects/{project}/locations/{location}".format(
        project=project, location=location,
    )
    actual = InstancesClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "scallop",
        "location": "abalone",
    }
    path = InstancesClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = InstancesClient.parse_common_location_path(path)
    assert expected == actual


def test_client_with_default_client_info():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.InstancesTransport, "_prep_wrapped_messages"
    ) as prep:
        client = InstancesClient(
            credentials=ga_credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.InstancesTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = InstancesClient.get_transport_class()
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)


def test_transport_close():
    transports = {
        "rest": "_session",
    }

    for transport, close_name in transports.items():
        client = InstancesClient(
            credentials=ga_credentials.AnonymousCredentials(), transport=transport
        )
        with mock.patch.object(
            type(getattr(client.transport, close_name)), "close"
        ) as close:
            with client:
                close.assert_not_called()
            close.assert_called_once()


def test_client_ctx():
    transports = [
        "rest",
    ]
    for transport in transports:
        client = InstancesClient(
            credentials=ga_credentials.AnonymousCredentials(), transport=transport
        )
        # Test client calls underlying transport.
        with mock.patch.object(type(client.transport), "close") as close:
            close.assert_not_called()
            with client:
                pass
            close.assert_called()


@pytest.mark.parametrize(
    "client_class,transport_class",
    [(InstancesClient, transports.InstancesRestTransport),],
)
def test_api_key_credentials(client_class, transport_class):
    with mock.patch.object(
        google.auth._default, "get_api_key_credentials", create=True
    ) as get_api_key_credentials:
        mock_cred = mock.Mock()
        get_api_key_credentials.return_value = mock_cred
        options = client_options.ClientOptions()
        options.api_key = "api_key"
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(client_options=options)
            patched.assert_called_once_with(
                credentials=mock_cred,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
            )
