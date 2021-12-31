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
from google.cloud.compute_v1.services.reservations import ReservationsClient
from google.cloud.compute_v1.services.reservations import pagers
from google.cloud.compute_v1.services.reservations import transports
from google.cloud.compute_v1.types import compute
from google.oauth2 import service_account
import google.auth


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return "foo.googleapis.com" if ("localhost" in client.DEFAULT_ENDPOINT) else client.DEFAULT_ENDPOINT


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert ReservationsClient._get_default_mtls_endpoint(None) is None
    assert ReservationsClient._get_default_mtls_endpoint(api_endpoint) == api_mtls_endpoint
    assert ReservationsClient._get_default_mtls_endpoint(api_mtls_endpoint) == api_mtls_endpoint
    assert ReservationsClient._get_default_mtls_endpoint(sandbox_endpoint) == sandbox_mtls_endpoint
    assert ReservationsClient._get_default_mtls_endpoint(sandbox_mtls_endpoint) == sandbox_mtls_endpoint
    assert ReservationsClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi


@pytest.mark.parametrize("client_class", [
    ReservationsClient,
])
def test_reservations_client_from_service_account_info(client_class):
    creds = ga_credentials.AnonymousCredentials()
    with mock.patch.object(service_account.Credentials, 'from_service_account_info') as factory:
        factory.return_value = creds
        info = {"valid": True}
        client = client_class.from_service_account_info(info)
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == 'compute.googleapis.com:443'


@pytest.mark.parametrize("transport_class,transport_name", [
    (transports.ReservationsRestTransport, "rest"),
])
def test_reservations_client_service_account_always_use_jwt(transport_class, transport_name):
    with mock.patch.object(service_account.Credentials, 'with_always_use_jwt_access', create=True) as use_jwt:
        creds = service_account.Credentials(None, None, None)
        transport = transport_class(credentials=creds, always_use_jwt_access=True)
        use_jwt.assert_called_once_with(True)

    with mock.patch.object(service_account.Credentials, 'with_always_use_jwt_access', create=True) as use_jwt:
        creds = service_account.Credentials(None, None, None)
        transport = transport_class(credentials=creds, always_use_jwt_access=False)
        use_jwt.assert_not_called()


@pytest.mark.parametrize("client_class", [
    ReservationsClient,
])
def test_reservations_client_from_service_account_file(client_class):
    creds = ga_credentials.AnonymousCredentials()
    with mock.patch.object(service_account.Credentials, 'from_service_account_file') as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == 'compute.googleapis.com:443'


def test_reservations_client_get_transport_class():
    transport = ReservationsClient.get_transport_class()
    available_transports = [
        transports.ReservationsRestTransport,
    ]
    assert transport in available_transports

    transport = ReservationsClient.get_transport_class("rest")
    assert transport == transports.ReservationsRestTransport


@pytest.mark.parametrize("client_class,transport_class,transport_name", [
    (ReservationsClient, transports.ReservationsRestTransport, "rest"),
])
@mock.patch.object(ReservationsClient, "DEFAULT_ENDPOINT", modify_default_endpoint(ReservationsClient))
def test_reservations_client_client_options(client_class, transport_class, transport_name):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(ReservationsClient, 'get_transport_class') as gtc:
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials()
        )
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(ReservationsClient, 'get_transport_class') as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, '__init__') as patched:
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
        with mock.patch.object(transport_class, '__init__') as patched:
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
        with mock.patch.object(transport_class, '__init__') as patched:
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
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}):
        with pytest.raises(ValueError):
            client = client_class(transport=transport_name)

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, '__init__') as patched:
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

@pytest.mark.parametrize("client_class,transport_class,transport_name,use_client_cert_env", [
    (ReservationsClient, transports.ReservationsRestTransport, "rest", "true"),
    (ReservationsClient, transports.ReservationsRestTransport, "rest", "false"),
])
@mock.patch.object(ReservationsClient, "DEFAULT_ENDPOINT", modify_default_endpoint(ReservationsClient))
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_reservations_client_mtls_env_auto(client_class, transport_class, transport_name, use_client_cert_env):
    # This tests the endpoint autoswitch behavior. Endpoint is autoswitched to the default
    # mtls endpoint, if GOOGLE_API_USE_CLIENT_CERTIFICATE is "true" and client cert exists.

    # Check the case client_cert_source is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}):
        options = client_options.ClientOptions(client_cert_source=client_cert_source_callback)
        with mock.patch.object(transport_class, '__init__') as patched:
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
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}):
        with mock.patch.object(transport_class, '__init__') as patched:
            with mock.patch('google.auth.transport.mtls.has_default_client_cert_source', return_value=True):
                with mock.patch('google.auth.transport.mtls.default_client_cert_source', return_value=client_cert_source_callback):
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
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}):
        with mock.patch.object(transport_class, '__init__') as patched:
            with mock.patch("google.auth.transport.mtls.has_default_client_cert_source", return_value=False):
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


@pytest.mark.parametrize("client_class,transport_class,transport_name", [
    (ReservationsClient, transports.ReservationsRestTransport, "rest"),
])
def test_reservations_client_client_options_scopes(client_class, transport_class, transport_name):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(
        scopes=["1", "2"],
    )
    with mock.patch.object(transport_class, '__init__') as patched:
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

@pytest.mark.parametrize("client_class,transport_class,transport_name", [
    (ReservationsClient, transports.ReservationsRestTransport, "rest"),
])
def test_reservations_client_client_options_credentials_file(client_class, transport_class, transport_name):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(
        credentials_file="credentials.json"
    )
    with mock.patch.object(transport_class, '__init__') as patched:
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


@pytest.mark.parametrize("request_type", [
  compute.AggregatedListReservationsRequest,
  dict,
])
def test_aggregated_list_rest(request_type, transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    # Send a request that will satisfy transcoding
    request = compute.AggregatedListReservationsRequest({'project': 'sample1'})

    with mock.patch.object(type(client.transport._session), 'request') as req:
        return_value = compute.ReservationAggregatedList(
              id='id_value',
              kind='kind_value',
              next_page_token='next_page_token_value',
              self_link='self_link_value',
              unreachables=['unreachables_value'],
        )
        req.return_value = Response()
        req.return_value.status_code = 500
        req.return_value.request = PreparedRequest()
        json_return_value = compute.ReservationAggregatedList.to_json(return_value)
        req.return_value._content = json_return_value.encode("UTF-8")
        with pytest.raises(core_exceptions.GoogleAPIError):
            # We only care that the correct exception is raised when putting
            # the request over the wire, so an empty request is fine.
            client.aggregated_list(request)


@pytest.mark.parametrize("request_type", [
    compute.AggregatedListReservationsRequest,
    dict,
])
def test_aggregated_list_rest(request_type):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1'}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.ReservationAggregatedList(
              id='id_value',
              kind='kind_value',
              next_page_token='next_page_token_value',
              self_link='self_link_value',
              unreachables=['unreachables_value'],
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.ReservationAggregatedList.to_json(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        response = client.aggregated_list(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.AggregatedListPager)
    assert response.id == 'id_value'
    assert response.kind == 'kind_value'
    assert response.next_page_token == 'next_page_token_value'
    assert response.self_link == 'self_link_value'
    assert response.unreachables == ['unreachables_value']


def test_aggregated_list_rest_required_fields(request_type=compute.AggregatedListReservationsRequest):
    transport_class = transports.ReservationsRestTransport

    request_init = {}
    request_init["project"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(request_type.to_json(
        request,
        including_default_value_fields=False,
        use_integers_for_enums=False
        ))

    # verify fields with default values are dropped
    assert "project" not in jsonified_request

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).aggregated_list._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "project" in jsonified_request
    assert jsonified_request["project"] == request_init["project"]

    jsonified_request["project"] = 'project_value'

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).aggregated_list._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == 'project_value'

    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.ReservationAggregatedList()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "get",
                'query_params': request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.ReservationAggregatedList.to_json(return_value)
            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value

            response = client.aggregated_list(request)

            expected_params = [
                (
                    "project",
                    "",
                ),
            ]
            actual_params = req.call_args.kwargs['params']
            assert expected_params == actual_params


def test_aggregated_list_rest_bad_request(transport: str = 'rest', request_type=compute.AggregatedListReservationsRequest):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1'}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.aggregated_list(request)


def test_aggregated_list_rest_flattened():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.ReservationAggregatedList()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.ReservationAggregatedList.to_json(return_value)

        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value

        # get arguments that satisfy an http rule for this method
        sample_request = {'project': 'sample1'}

        # get truthy value for each flattened field
        mock_args = dict(
            project='project_value',
        )
        mock_args.update(sample_request)
        client.aggregated_list(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("https://%s/compute/v1/projects/{project}/aggregated/reservations" % client.transport._host, args[1])


def test_aggregated_list_rest_flattened_error(transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.aggregated_list(
            compute.AggregatedListReservationsRequest(),
            project='project_value',
        )


def test_aggregated_list_rest_pager(transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        #with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            compute.ReservationAggregatedList(
                items={
                    'a':compute.ReservationsScopedList(),
                    'b':compute.ReservationsScopedList(),
                    'c':compute.ReservationsScopedList(),
                },
                next_page_token='abc',
            ),
            compute.ReservationAggregatedList(
                items={},
                next_page_token='def',
            ),
            compute.ReservationAggregatedList(
                items={
                    'g':compute.ReservationsScopedList(),
                },
                next_page_token='ghi',
            ),
            compute.ReservationAggregatedList(
                items={
                    'h':compute.ReservationsScopedList(),
                    'i':compute.ReservationsScopedList(),
                },
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(compute.ReservationAggregatedList.to_json(x) for x in response)
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode('UTF-8')
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {'project': 'sample1'}

        pager = client.aggregated_list(request=sample_request)

        assert isinstance(pager.get('a'), compute.ReservationsScopedList)
        assert pager.get('h') is None

        results = list(pager)
        assert len(results) == 6
        assert all(
            isinstance(i, tuple)
                for i in results)
        for result in results:
            assert isinstance(result, tuple)
            assert tuple(type(t) for t in result) == (str, compute.ReservationsScopedList)

        assert pager.get('a') is None
        assert isinstance(pager.get('h'), compute.ReservationsScopedList)

        pages = list(client.aggregated_list(request=sample_request).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.parametrize("request_type", [
  compute.DeleteReservationRequest,
  dict,
])
def test_delete_unary_rest(request_type, transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    # Send a request that will satisfy transcoding
    request = compute.DeleteReservationRequest({'project': 'sample1', 'zone': 'sample2', 'reservation': 'sample3'})

    with mock.patch.object(type(client.transport._session), 'request') as req:
        return_value = compute.Operation(
              client_operation_id='client_operation_id_value',
              creation_timestamp='creation_timestamp_value',
              description='description_value',
              end_time='end_time_value',
              http_error_message='http_error_message_value',
              http_error_status_code=2374,
              id=205,
              insert_time='insert_time_value',
              kind='kind_value',
              name='name_value',
              operation_group_id='operation_group_id_value',
              operation_type='operation_type_value',
              progress=885,
              region='region_value',
              self_link='self_link_value',
              start_time='start_time_value',
              status=compute.Operation.Status.DONE,
              status_message='status_message_value',
              target_id=947,
              target_link='target_link_value',
              user='user_value',
              zone='zone_value',
        )
        req.return_value = Response()
        req.return_value.status_code = 500
        req.return_value.request = PreparedRequest()
        json_return_value = compute.Operation.to_json(return_value)
        req.return_value._content = json_return_value.encode("UTF-8")
        with pytest.raises(core_exceptions.GoogleAPIError):
            # We only care that the correct exception is raised when putting
            # the request over the wire, so an empty request is fine.
            client.delete_unary(request)


@pytest.mark.parametrize("request_type", [
    compute.DeleteReservationRequest,
    dict,
])
def test_delete_unary_rest(request_type):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2', 'reservation': 'sample3'}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
              client_operation_id='client_operation_id_value',
              creation_timestamp='creation_timestamp_value',
              description='description_value',
              end_time='end_time_value',
              http_error_message='http_error_message_value',
              http_error_status_code=2374,
              id=205,
              insert_time='insert_time_value',
              kind='kind_value',
              name='name_value',
              operation_group_id='operation_group_id_value',
              operation_type='operation_type_value',
              progress=885,
              region='region_value',
              self_link='self_link_value',
              start_time='start_time_value',
              status=compute.Operation.Status.DONE,
              status_message='status_message_value',
              target_id=947,
              target_link='target_link_value',
              user='user_value',
              zone='zone_value',
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        response = client.delete_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == 'client_operation_id_value'
    assert response.creation_timestamp == 'creation_timestamp_value'
    assert response.description == 'description_value'
    assert response.end_time == 'end_time_value'
    assert response.http_error_message == 'http_error_message_value'
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == 'insert_time_value'
    assert response.kind == 'kind_value'
    assert response.name == 'name_value'
    assert response.operation_group_id == 'operation_group_id_value'
    assert response.operation_type == 'operation_type_value'
    assert response.progress == 885
    assert response.region == 'region_value'
    assert response.self_link == 'self_link_value'
    assert response.start_time == 'start_time_value'
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == 'status_message_value'
    assert response.target_id == 947
    assert response.target_link == 'target_link_value'
    assert response.user == 'user_value'
    assert response.zone == 'zone_value'


def test_delete_unary_rest_required_fields(request_type=compute.DeleteReservationRequest):
    transport_class = transports.ReservationsRestTransport

    request_init = {}
    request_init["project"] = ""
    request_init["reservation"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(request_type.to_json(
        request,
        including_default_value_fields=False,
        use_integers_for_enums=False
        ))

    # verify fields with default values are dropped
    assert "project" not in jsonified_request
    assert "reservation" not in jsonified_request
    assert "zone" not in jsonified_request

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).delete._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "project" in jsonified_request
    assert jsonified_request["project"] == request_init["project"]
    assert "reservation" in jsonified_request
    assert jsonified_request["reservation"] == request_init["reservation"]
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == request_init["zone"]

    jsonified_request["project"] = 'project_value'
    jsonified_request["reservation"] = 'reservation_value'
    jsonified_request["zone"] = 'zone_value'

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).delete._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == 'project_value'
    assert "reservation" in jsonified_request
    assert jsonified_request["reservation"] == 'reservation_value'
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == 'zone_value'

    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "delete",
                'query_params': request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value

            response = client.delete_unary(request)

            expected_params = [
                (
                    "project",
                    "",
                ),
                (
                    "reservation",
                    "",
                ),
                (
                    "zone",
                    "",
                ),
            ]
            actual_params = req.call_args.kwargs['params']
            assert expected_params == actual_params


def test_delete_unary_rest_bad_request(transport: str = 'rest', request_type=compute.DeleteReservationRequest):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2', 'reservation': 'sample3'}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.delete_unary(request)


def test_delete_unary_rest_flattened():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value

        # get arguments that satisfy an http rule for this method
        sample_request = {'project': 'sample1', 'zone': 'sample2', 'reservation': 'sample3'}

        # get truthy value for each flattened field
        mock_args = dict(
            project='project_value',
            zone='zone_value',
            reservation='reservation_value',
        )
        mock_args.update(sample_request)
        client.delete_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("https://%s/compute/v1/projects/{project}/zones/{zone}/reservations/{reservation}" % client.transport._host, args[1])


def test_delete_unary_rest_flattened_error(transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_unary(
            compute.DeleteReservationRequest(),
            project='project_value',
            zone='zone_value',
            reservation='reservation_value',
        )


def test_delete_unary_rest_error():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest'
    )

@pytest.mark.parametrize("request_type", [
  compute.GetReservationRequest,
  dict,
])
def test_get_rest(request_type, transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    # Send a request that will satisfy transcoding
    request = compute.GetReservationRequest({'project': 'sample1', 'zone': 'sample2', 'reservation': 'sample3'})

    with mock.patch.object(type(client.transport._session), 'request') as req:
        return_value = compute.Reservation(
              commitment='commitment_value',
              creation_timestamp='creation_timestamp_value',
              description='description_value',
              id=205,
              kind='kind_value',
              name='name_value',
              satisfies_pzs=True,
              self_link='self_link_value',
              specific_reservation_required=True,
              status='status_value',
              zone='zone_value',
        )
        req.return_value = Response()
        req.return_value.status_code = 500
        req.return_value.request = PreparedRequest()
        json_return_value = compute.Reservation.to_json(return_value)
        req.return_value._content = json_return_value.encode("UTF-8")
        with pytest.raises(core_exceptions.GoogleAPIError):
            # We only care that the correct exception is raised when putting
            # the request over the wire, so an empty request is fine.
            client.get(request)


@pytest.mark.parametrize("request_type", [
    compute.GetReservationRequest,
    dict,
])
def test_get_rest(request_type):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2', 'reservation': 'sample3'}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Reservation(
              commitment='commitment_value',
              creation_timestamp='creation_timestamp_value',
              description='description_value',
              id=205,
              kind='kind_value',
              name='name_value',
              satisfies_pzs=True,
              self_link='self_link_value',
              specific_reservation_required=True,
              status='status_value',
              zone='zone_value',
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Reservation.to_json(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        response = client.get(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Reservation)
    assert response.commitment == 'commitment_value'
    assert response.creation_timestamp == 'creation_timestamp_value'
    assert response.description == 'description_value'
    assert response.id == 205
    assert response.kind == 'kind_value'
    assert response.name == 'name_value'
    assert response.satisfies_pzs is True
    assert response.self_link == 'self_link_value'
    assert response.specific_reservation_required is True
    assert response.status == 'status_value'
    assert response.zone == 'zone_value'


def test_get_rest_required_fields(request_type=compute.GetReservationRequest):
    transport_class = transports.ReservationsRestTransport

    request_init = {}
    request_init["project"] = ""
    request_init["reservation"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(request_type.to_json(
        request,
        including_default_value_fields=False,
        use_integers_for_enums=False
        ))

    # verify fields with default values are dropped
    assert "project" not in jsonified_request
    assert "reservation" not in jsonified_request
    assert "zone" not in jsonified_request

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).get._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "project" in jsonified_request
    assert jsonified_request["project"] == request_init["project"]
    assert "reservation" in jsonified_request
    assert jsonified_request["reservation"] == request_init["reservation"]
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == request_init["zone"]

    jsonified_request["project"] = 'project_value'
    jsonified_request["reservation"] = 'reservation_value'
    jsonified_request["zone"] = 'zone_value'

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).get._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == 'project_value'
    assert "reservation" in jsonified_request
    assert jsonified_request["reservation"] == 'reservation_value'
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == 'zone_value'

    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Reservation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "get",
                'query_params': request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Reservation.to_json(return_value)
            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value

            response = client.get(request)

            expected_params = [
                (
                    "project",
                    "",
                ),
                (
                    "reservation",
                    "",
                ),
                (
                    "zone",
                    "",
                ),
            ]
            actual_params = req.call_args.kwargs['params']
            assert expected_params == actual_params


def test_get_rest_bad_request(transport: str = 'rest', request_type=compute.GetReservationRequest):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2', 'reservation': 'sample3'}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get(request)


def test_get_rest_flattened():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Reservation()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Reservation.to_json(return_value)

        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value

        # get arguments that satisfy an http rule for this method
        sample_request = {'project': 'sample1', 'zone': 'sample2', 'reservation': 'sample3'}

        # get truthy value for each flattened field
        mock_args = dict(
            project='project_value',
            zone='zone_value',
            reservation='reservation_value',
        )
        mock_args.update(sample_request)
        client.get(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("https://%s/compute/v1/projects/{project}/zones/{zone}/reservations/{reservation}" % client.transport._host, args[1])


def test_get_rest_flattened_error(transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get(
            compute.GetReservationRequest(),
            project='project_value',
            zone='zone_value',
            reservation='reservation_value',
        )


def test_get_rest_error():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest'
    )

@pytest.mark.parametrize("request_type", [
  compute.GetIamPolicyReservationRequest,
  dict,
])
def test_get_iam_policy_rest(request_type, transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    # Send a request that will satisfy transcoding
    request = compute.GetIamPolicyReservationRequest({'project': 'sample1', 'zone': 'sample2', 'resource': 'sample3'})

    with mock.patch.object(type(client.transport._session), 'request') as req:
        return_value = compute.Policy(
              etag='etag_value',
              iam_owned=True,
              version=774,
        )
        req.return_value = Response()
        req.return_value.status_code = 500
        req.return_value.request = PreparedRequest()
        json_return_value = compute.Policy.to_json(return_value)
        req.return_value._content = json_return_value.encode("UTF-8")
        with pytest.raises(core_exceptions.GoogleAPIError):
            # We only care that the correct exception is raised when putting
            # the request over the wire, so an empty request is fine.
            client.get_iam_policy(request)


@pytest.mark.parametrize("request_type", [
    compute.GetIamPolicyReservationRequest,
    dict,
])
def test_get_iam_policy_rest(request_type):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2', 'resource': 'sample3'}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Policy(
              etag='etag_value',
              iam_owned=True,
              version=774,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Policy.to_json(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        response = client.get_iam_policy(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Policy)
    assert response.etag == 'etag_value'
    assert response.iam_owned is True
    assert response.version == 774


def test_get_iam_policy_rest_required_fields(request_type=compute.GetIamPolicyReservationRequest):
    transport_class = transports.ReservationsRestTransport

    request_init = {}
    request_init["project"] = ""
    request_init["resource"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(request_type.to_json(
        request,
        including_default_value_fields=False,
        use_integers_for_enums=False
        ))

    # verify fields with default values are dropped
    assert "project" not in jsonified_request
    assert "resource" not in jsonified_request
    assert "zone" not in jsonified_request

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).get_iam_policy._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "project" in jsonified_request
    assert jsonified_request["project"] == request_init["project"]
    assert "resource" in jsonified_request
    assert jsonified_request["resource"] == request_init["resource"]
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == request_init["zone"]

    jsonified_request["project"] = 'project_value'
    jsonified_request["resource"] = 'resource_value'
    jsonified_request["zone"] = 'zone_value'

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).get_iam_policy._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == 'project_value'
    assert "resource" in jsonified_request
    assert jsonified_request["resource"] == 'resource_value'
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == 'zone_value'

    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Policy()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "get",
                'query_params': request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Policy.to_json(return_value)
            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value

            response = client.get_iam_policy(request)

            expected_params = [
                (
                    "project",
                    "",
                ),
                (
                    "resource",
                    "",
                ),
                (
                    "zone",
                    "",
                ),
            ]
            actual_params = req.call_args.kwargs['params']
            assert expected_params == actual_params


def test_get_iam_policy_rest_bad_request(transport: str = 'rest', request_type=compute.GetIamPolicyReservationRequest):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2', 'resource': 'sample3'}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_iam_policy(request)


def test_get_iam_policy_rest_flattened():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Policy()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Policy.to_json(return_value)

        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value

        # get arguments that satisfy an http rule for this method
        sample_request = {'project': 'sample1', 'zone': 'sample2', 'resource': 'sample3'}

        # get truthy value for each flattened field
        mock_args = dict(
            project='project_value',
            zone='zone_value',
            resource='resource_value',
        )
        mock_args.update(sample_request)
        client.get_iam_policy(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("https://%s/compute/v1/projects/{project}/zones/{zone}/reservations/{resource}/getIamPolicy" % client.transport._host, args[1])


def test_get_iam_policy_rest_flattened_error(transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_iam_policy(
            compute.GetIamPolicyReservationRequest(),
            project='project_value',
            zone='zone_value',
            resource='resource_value',
        )


def test_get_iam_policy_rest_error():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest'
    )

@pytest.mark.parametrize("request_type", [
  compute.InsertReservationRequest,
  dict,
])
def test_insert_unary_rest(request_type, transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    # Send a request that will satisfy transcoding
    request = compute.InsertReservationRequest({'project': 'sample1', 'zone': 'sample2'})

    with mock.patch.object(type(client.transport._session), 'request') as req:
        return_value = compute.Operation(
              client_operation_id='client_operation_id_value',
              creation_timestamp='creation_timestamp_value',
              description='description_value',
              end_time='end_time_value',
              http_error_message='http_error_message_value',
              http_error_status_code=2374,
              id=205,
              insert_time='insert_time_value',
              kind='kind_value',
              name='name_value',
              operation_group_id='operation_group_id_value',
              operation_type='operation_type_value',
              progress=885,
              region='region_value',
              self_link='self_link_value',
              start_time='start_time_value',
              status=compute.Operation.Status.DONE,
              status_message='status_message_value',
              target_id=947,
              target_link='target_link_value',
              user='user_value',
              zone='zone_value',
        )
        req.return_value = Response()
        req.return_value.status_code = 500
        req.return_value.request = PreparedRequest()
        json_return_value = compute.Operation.to_json(return_value)
        req.return_value._content = json_return_value.encode("UTF-8")
        with pytest.raises(core_exceptions.GoogleAPIError):
            # We only care that the correct exception is raised when putting
            # the request over the wire, so an empty request is fine.
            client.insert_unary(request)


@pytest.mark.parametrize("request_type", [
    compute.InsertReservationRequest,
    dict,
])
def test_insert_unary_rest(request_type):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2'}
    request_init["reservation_resource"] = {'commitment': 'commitment_value', 'creation_timestamp': 'creation_timestamp_value', 'description': 'description_value', 'id': 205, 'kind': 'kind_value', 'name': 'name_value', 'satisfies_pzs': True, 'self_link': 'self_link_value', 'specific_reservation': {'count': 553, 'in_use_count': 1291, 'instance_properties': {'guest_accelerators': [{'accelerator_count': 1805, 'accelerator_type': 'accelerator_type_value'}], 'local_ssds': [{'disk_size_gb': 1261, 'interface': 'interface_value'}], 'location_hint': 'location_hint_value', 'machine_type': 'machine_type_value', 'min_cpu_platform': 'min_cpu_platform_value'}}, 'specific_reservation_required': True, 'status': 'status_value', 'zone': 'zone_value'}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
              client_operation_id='client_operation_id_value',
              creation_timestamp='creation_timestamp_value',
              description='description_value',
              end_time='end_time_value',
              http_error_message='http_error_message_value',
              http_error_status_code=2374,
              id=205,
              insert_time='insert_time_value',
              kind='kind_value',
              name='name_value',
              operation_group_id='operation_group_id_value',
              operation_type='operation_type_value',
              progress=885,
              region='region_value',
              self_link='self_link_value',
              start_time='start_time_value',
              status=compute.Operation.Status.DONE,
              status_message='status_message_value',
              target_id=947,
              target_link='target_link_value',
              user='user_value',
              zone='zone_value',
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        response = client.insert_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == 'client_operation_id_value'
    assert response.creation_timestamp == 'creation_timestamp_value'
    assert response.description == 'description_value'
    assert response.end_time == 'end_time_value'
    assert response.http_error_message == 'http_error_message_value'
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == 'insert_time_value'
    assert response.kind == 'kind_value'
    assert response.name == 'name_value'
    assert response.operation_group_id == 'operation_group_id_value'
    assert response.operation_type == 'operation_type_value'
    assert response.progress == 885
    assert response.region == 'region_value'
    assert response.self_link == 'self_link_value'
    assert response.start_time == 'start_time_value'
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == 'status_message_value'
    assert response.target_id == 947
    assert response.target_link == 'target_link_value'
    assert response.user == 'user_value'
    assert response.zone == 'zone_value'


def test_insert_unary_rest_required_fields(request_type=compute.InsertReservationRequest):
    transport_class = transports.ReservationsRestTransport

    request_init = {}
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(request_type.to_json(
        request,
        including_default_value_fields=False,
        use_integers_for_enums=False
        ))

    # verify fields with default values are dropped
    assert "project" not in jsonified_request
    assert "zone" not in jsonified_request

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).insert._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "project" in jsonified_request
    assert jsonified_request["project"] == request_init["project"]
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == request_init["zone"]

    jsonified_request["project"] = 'project_value'
    jsonified_request["zone"] = 'zone_value'

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).insert._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == 'project_value'
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == 'zone_value'

    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "post",
                'query_params': request_init,
            }
            transcode_result['body'] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value

            response = client.insert_unary(request)

            expected_params = [
                (
                    "project",
                    "",
                ),
                (
                    "zone",
                    "",
                ),
            ]
            actual_params = req.call_args.kwargs['params']
            assert expected_params == actual_params


def test_insert_unary_rest_bad_request(transport: str = 'rest', request_type=compute.InsertReservationRequest):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2'}
    request_init["reservation_resource"] = {'commitment': 'commitment_value', 'creation_timestamp': 'creation_timestamp_value', 'description': 'description_value', 'id': 205, 'kind': 'kind_value', 'name': 'name_value', 'satisfies_pzs': True, 'self_link': 'self_link_value', 'specific_reservation': {'count': 553, 'in_use_count': 1291, 'instance_properties': {'guest_accelerators': [{'accelerator_count': 1805, 'accelerator_type': 'accelerator_type_value'}], 'local_ssds': [{'disk_size_gb': 1261, 'interface': 'interface_value'}], 'location_hint': 'location_hint_value', 'machine_type': 'machine_type_value', 'min_cpu_platform': 'min_cpu_platform_value'}}, 'specific_reservation_required': True, 'status': 'status_value', 'zone': 'zone_value'}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.insert_unary(request)


def test_insert_unary_rest_flattened():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value

        # get arguments that satisfy an http rule for this method
        sample_request = {'project': 'sample1', 'zone': 'sample2'}

        # get truthy value for each flattened field
        mock_args = dict(
            project='project_value',
            zone='zone_value',
            reservation_resource=compute.Reservation(commitment='commitment_value'),
        )
        mock_args.update(sample_request)
        client.insert_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("https://%s/compute/v1/projects/{project}/zones/{zone}/reservations" % client.transport._host, args[1])


def test_insert_unary_rest_flattened_error(transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.insert_unary(
            compute.InsertReservationRequest(),
            project='project_value',
            zone='zone_value',
            reservation_resource=compute.Reservation(commitment='commitment_value'),
        )


def test_insert_unary_rest_error():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest'
    )

@pytest.mark.parametrize("request_type", [
  compute.ListReservationsRequest,
  dict,
])
def test_list_rest(request_type, transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    # Send a request that will satisfy transcoding
    request = compute.ListReservationsRequest({'project': 'sample1', 'zone': 'sample2'})

    with mock.patch.object(type(client.transport._session), 'request') as req:
        return_value = compute.ReservationList(
              id='id_value',
              kind='kind_value',
              next_page_token='next_page_token_value',
              self_link='self_link_value',
        )
        req.return_value = Response()
        req.return_value.status_code = 500
        req.return_value.request = PreparedRequest()
        json_return_value = compute.ReservationList.to_json(return_value)
        req.return_value._content = json_return_value.encode("UTF-8")
        with pytest.raises(core_exceptions.GoogleAPIError):
            # We only care that the correct exception is raised when putting
            # the request over the wire, so an empty request is fine.
            client.list(request)


@pytest.mark.parametrize("request_type", [
    compute.ListReservationsRequest,
    dict,
])
def test_list_rest(request_type):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2'}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.ReservationList(
              id='id_value',
              kind='kind_value',
              next_page_token='next_page_token_value',
              self_link='self_link_value',
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.ReservationList.to_json(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        response = client.list(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListPager)
    assert response.id == 'id_value'
    assert response.kind == 'kind_value'
    assert response.next_page_token == 'next_page_token_value'
    assert response.self_link == 'self_link_value'


def test_list_rest_required_fields(request_type=compute.ListReservationsRequest):
    transport_class = transports.ReservationsRestTransport

    request_init = {}
    request_init["project"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(request_type.to_json(
        request,
        including_default_value_fields=False,
        use_integers_for_enums=False
        ))

    # verify fields with default values are dropped
    assert "project" not in jsonified_request
    assert "zone" not in jsonified_request

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).list._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "project" in jsonified_request
    assert jsonified_request["project"] == request_init["project"]
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == request_init["zone"]

    jsonified_request["project"] = 'project_value'
    jsonified_request["zone"] = 'zone_value'

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).list._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == 'project_value'
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == 'zone_value'

    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.ReservationList()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "get",
                'query_params': request_init,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.ReservationList.to_json(return_value)
            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value

            response = client.list(request)

            expected_params = [
                (
                    "project",
                    "",
                ),
                (
                    "zone",
                    "",
                ),
            ]
            actual_params = req.call_args.kwargs['params']
            assert expected_params == actual_params


def test_list_rest_bad_request(transport: str = 'rest', request_type=compute.ListReservationsRequest):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2'}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.list(request)


def test_list_rest_flattened():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.ReservationList()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.ReservationList.to_json(return_value)

        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value

        # get arguments that satisfy an http rule for this method
        sample_request = {'project': 'sample1', 'zone': 'sample2'}

        # get truthy value for each flattened field
        mock_args = dict(
            project='project_value',
            zone='zone_value',
        )
        mock_args.update(sample_request)
        client.list(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("https://%s/compute/v1/projects/{project}/zones/{zone}/reservations" % client.transport._host, args[1])


def test_list_rest_flattened_error(transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list(
            compute.ListReservationsRequest(),
            project='project_value',
            zone='zone_value',
        )


def test_list_rest_pager(transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        #with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            compute.ReservationList(
                items=[
                    compute.Reservation(),
                    compute.Reservation(),
                    compute.Reservation(),
                ],
                next_page_token='abc',
            ),
            compute.ReservationList(
                items=[],
                next_page_token='def',
            ),
            compute.ReservationList(
                items=[
                    compute.Reservation(),
                ],
                next_page_token='ghi',
            ),
            compute.ReservationList(
                items=[
                    compute.Reservation(),
                    compute.Reservation(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(compute.ReservationList.to_json(x) for x in response)
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode('UTF-8')
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {'project': 'sample1', 'zone': 'sample2'}

        pager = client.list(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, compute.Reservation)
                for i in results)

        pages = list(client.list(request=sample_request).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.parametrize("request_type", [
  compute.ResizeReservationRequest,
  dict,
])
def test_resize_unary_rest(request_type, transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    # Send a request that will satisfy transcoding
    request = compute.ResizeReservationRequest({'project': 'sample1', 'zone': 'sample2', 'reservation': 'sample3'})

    with mock.patch.object(type(client.transport._session), 'request') as req:
        return_value = compute.Operation(
              client_operation_id='client_operation_id_value',
              creation_timestamp='creation_timestamp_value',
              description='description_value',
              end_time='end_time_value',
              http_error_message='http_error_message_value',
              http_error_status_code=2374,
              id=205,
              insert_time='insert_time_value',
              kind='kind_value',
              name='name_value',
              operation_group_id='operation_group_id_value',
              operation_type='operation_type_value',
              progress=885,
              region='region_value',
              self_link='self_link_value',
              start_time='start_time_value',
              status=compute.Operation.Status.DONE,
              status_message='status_message_value',
              target_id=947,
              target_link='target_link_value',
              user='user_value',
              zone='zone_value',
        )
        req.return_value = Response()
        req.return_value.status_code = 500
        req.return_value.request = PreparedRequest()
        json_return_value = compute.Operation.to_json(return_value)
        req.return_value._content = json_return_value.encode("UTF-8")
        with pytest.raises(core_exceptions.GoogleAPIError):
            # We only care that the correct exception is raised when putting
            # the request over the wire, so an empty request is fine.
            client.resize_unary(request)


@pytest.mark.parametrize("request_type", [
    compute.ResizeReservationRequest,
    dict,
])
def test_resize_unary_rest(request_type):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2', 'reservation': 'sample3'}
    request_init["reservations_resize_request_resource"] = {'specific_sku_count': 1920}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation(
              client_operation_id='client_operation_id_value',
              creation_timestamp='creation_timestamp_value',
              description='description_value',
              end_time='end_time_value',
              http_error_message='http_error_message_value',
              http_error_status_code=2374,
              id=205,
              insert_time='insert_time_value',
              kind='kind_value',
              name='name_value',
              operation_group_id='operation_group_id_value',
              operation_type='operation_type_value',
              progress=885,
              region='region_value',
              self_link='self_link_value',
              start_time='start_time_value',
              status=compute.Operation.Status.DONE,
              status_message='status_message_value',
              target_id=947,
              target_link='target_link_value',
              user='user_value',
              zone='zone_value',
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        response = client.resize_unary(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Operation)
    assert response.client_operation_id == 'client_operation_id_value'
    assert response.creation_timestamp == 'creation_timestamp_value'
    assert response.description == 'description_value'
    assert response.end_time == 'end_time_value'
    assert response.http_error_message == 'http_error_message_value'
    assert response.http_error_status_code == 2374
    assert response.id == 205
    assert response.insert_time == 'insert_time_value'
    assert response.kind == 'kind_value'
    assert response.name == 'name_value'
    assert response.operation_group_id == 'operation_group_id_value'
    assert response.operation_type == 'operation_type_value'
    assert response.progress == 885
    assert response.region == 'region_value'
    assert response.self_link == 'self_link_value'
    assert response.start_time == 'start_time_value'
    assert response.status == compute.Operation.Status.DONE
    assert response.status_message == 'status_message_value'
    assert response.target_id == 947
    assert response.target_link == 'target_link_value'
    assert response.user == 'user_value'
    assert response.zone == 'zone_value'


def test_resize_unary_rest_required_fields(request_type=compute.ResizeReservationRequest):
    transport_class = transports.ReservationsRestTransport

    request_init = {}
    request_init["project"] = ""
    request_init["reservation"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(request_type.to_json(
        request,
        including_default_value_fields=False,
        use_integers_for_enums=False
        ))

    # verify fields with default values are dropped
    assert "project" not in jsonified_request
    assert "reservation" not in jsonified_request
    assert "zone" not in jsonified_request

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).resize._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "project" in jsonified_request
    assert jsonified_request["project"] == request_init["project"]
    assert "reservation" in jsonified_request
    assert jsonified_request["reservation"] == request_init["reservation"]
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == request_init["zone"]

    jsonified_request["project"] = 'project_value'
    jsonified_request["reservation"] = 'reservation_value'
    jsonified_request["zone"] = 'zone_value'

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).resize._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == 'project_value'
    assert "reservation" in jsonified_request
    assert jsonified_request["reservation"] == 'reservation_value'
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == 'zone_value'

    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Operation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "post",
                'query_params': request_init,
            }
            transcode_result['body'] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Operation.to_json(return_value)
            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value

            response = client.resize_unary(request)

            expected_params = [
                (
                    "project",
                    "",
                ),
                (
                    "reservation",
                    "",
                ),
                (
                    "zone",
                    "",
                ),
            ]
            actual_params = req.call_args.kwargs['params']
            assert expected_params == actual_params


def test_resize_unary_rest_bad_request(transport: str = 'rest', request_type=compute.ResizeReservationRequest):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2', 'reservation': 'sample3'}
    request_init["reservations_resize_request_resource"] = {'specific_sku_count': 1920}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.resize_unary(request)


def test_resize_unary_rest_flattened():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Operation()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Operation.to_json(return_value)

        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value

        # get arguments that satisfy an http rule for this method
        sample_request = {'project': 'sample1', 'zone': 'sample2', 'reservation': 'sample3'}

        # get truthy value for each flattened field
        mock_args = dict(
            project='project_value',
            zone='zone_value',
            reservation='reservation_value',
            reservations_resize_request_resource=compute.ReservationsResizeRequest(specific_sku_count=1920),
        )
        mock_args.update(sample_request)
        client.resize_unary(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("https://%s/compute/v1/projects/{project}/zones/{zone}/reservations/{reservation}/resize" % client.transport._host, args[1])


def test_resize_unary_rest_flattened_error(transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.resize_unary(
            compute.ResizeReservationRequest(),
            project='project_value',
            zone='zone_value',
            reservation='reservation_value',
            reservations_resize_request_resource=compute.ReservationsResizeRequest(specific_sku_count=1920),
        )


def test_resize_unary_rest_error():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest'
    )

@pytest.mark.parametrize("request_type", [
  compute.SetIamPolicyReservationRequest,
  dict,
])
def test_set_iam_policy_rest(request_type, transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    # Send a request that will satisfy transcoding
    request = compute.SetIamPolicyReservationRequest({'project': 'sample1', 'zone': 'sample2', 'resource': 'sample3'})

    with mock.patch.object(type(client.transport._session), 'request') as req:
        return_value = compute.Policy(
              etag='etag_value',
              iam_owned=True,
              version=774,
        )
        req.return_value = Response()
        req.return_value.status_code = 500
        req.return_value.request = PreparedRequest()
        json_return_value = compute.Policy.to_json(return_value)
        req.return_value._content = json_return_value.encode("UTF-8")
        with pytest.raises(core_exceptions.GoogleAPIError):
            # We only care that the correct exception is raised when putting
            # the request over the wire, so an empty request is fine.
            client.set_iam_policy(request)


@pytest.mark.parametrize("request_type", [
    compute.SetIamPolicyReservationRequest,
    dict,
])
def test_set_iam_policy_rest(request_type):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2', 'resource': 'sample3'}
    request_init["zone_set_policy_request_resource"] = {'bindings': [{'binding_id': 'binding_id_value', 'condition': {'description': 'description_value', 'expression': 'expression_value', 'location': 'location_value', 'title': 'title_value'}, 'members': ['members_value_1', 'members_value_2'], 'role': 'role_value'}], 'etag': 'etag_value', 'policy': {'audit_configs': [{'audit_log_configs': [{'exempted_members': ['exempted_members_value_1', 'exempted_members_value_2'], 'ignore_child_exemptions': True, 'log_type': 'log_type_value'}], 'exempted_members': ['exempted_members_value_1', 'exempted_members_value_2'], 'service': 'service_value'}], 'bindings': [{'binding_id': 'binding_id_value', 'condition': {'description': 'description_value', 'expression': 'expression_value', 'location': 'location_value', 'title': 'title_value'}, 'members': ['members_value_1', 'members_value_2'], 'role': 'role_value'}], 'etag': 'etag_value', 'iam_owned': True, 'rules': [{'action': 'action_value', 'conditions': [{'iam': 'iam_value', 'op': 'op_value', 'svc': 'svc_value', 'sys': 'sys_value', 'values': ['values_value_1', 'values_value_2']}], 'description': 'description_value', 'ins': ['ins_value_1', 'ins_value_2'], 'log_configs': [{'cloud_audit': {'authorization_logging_options': {'permission_type': 'permission_type_value'}, 'log_name': 'log_name_value'}, 'counter': {'custom_fields': [{'name': 'name_value', 'value': 'value_value'}], 'field': 'field_value', 'metric': 'metric_value'}, 'data_access': {'log_mode': 'log_mode_value'}}], 'not_ins': ['not_ins_value_1', 'not_ins_value_2'], 'permissions': ['permissions_value_1', 'permissions_value_2']}], 'version': 774}}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Policy(
              etag='etag_value',
              iam_owned=True,
              version=774,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Policy.to_json(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        response = client.set_iam_policy(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.Policy)
    assert response.etag == 'etag_value'
    assert response.iam_owned is True
    assert response.version == 774


def test_set_iam_policy_rest_required_fields(request_type=compute.SetIamPolicyReservationRequest):
    transport_class = transports.ReservationsRestTransport

    request_init = {}
    request_init["project"] = ""
    request_init["resource"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(request_type.to_json(
        request,
        including_default_value_fields=False,
        use_integers_for_enums=False
        ))

    # verify fields with default values are dropped
    assert "project" not in jsonified_request
    assert "resource" not in jsonified_request
    assert "zone" not in jsonified_request

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).set_iam_policy._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "project" in jsonified_request
    assert jsonified_request["project"] == request_init["project"]
    assert "resource" in jsonified_request
    assert jsonified_request["resource"] == request_init["resource"]
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == request_init["zone"]

    jsonified_request["project"] = 'project_value'
    jsonified_request["resource"] = 'resource_value'
    jsonified_request["zone"] = 'zone_value'

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).set_iam_policy._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == 'project_value'
    assert "resource" in jsonified_request
    assert jsonified_request["resource"] == 'resource_value'
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == 'zone_value'

    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.Policy()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "post",
                'query_params': request_init,
            }
            transcode_result['body'] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.Policy.to_json(return_value)
            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value

            response = client.set_iam_policy(request)

            expected_params = [
                (
                    "project",
                    "",
                ),
                (
                    "resource",
                    "",
                ),
                (
                    "zone",
                    "",
                ),
            ]
            actual_params = req.call_args.kwargs['params']
            assert expected_params == actual_params


def test_set_iam_policy_rest_bad_request(transport: str = 'rest', request_type=compute.SetIamPolicyReservationRequest):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2', 'resource': 'sample3'}
    request_init["zone_set_policy_request_resource"] = {'bindings': [{'binding_id': 'binding_id_value', 'condition': {'description': 'description_value', 'expression': 'expression_value', 'location': 'location_value', 'title': 'title_value'}, 'members': ['members_value_1', 'members_value_2'], 'role': 'role_value'}], 'etag': 'etag_value', 'policy': {'audit_configs': [{'audit_log_configs': [{'exempted_members': ['exempted_members_value_1', 'exempted_members_value_2'], 'ignore_child_exemptions': True, 'log_type': 'log_type_value'}], 'exempted_members': ['exempted_members_value_1', 'exempted_members_value_2'], 'service': 'service_value'}], 'bindings': [{'binding_id': 'binding_id_value', 'condition': {'description': 'description_value', 'expression': 'expression_value', 'location': 'location_value', 'title': 'title_value'}, 'members': ['members_value_1', 'members_value_2'], 'role': 'role_value'}], 'etag': 'etag_value', 'iam_owned': True, 'rules': [{'action': 'action_value', 'conditions': [{'iam': 'iam_value', 'op': 'op_value', 'svc': 'svc_value', 'sys': 'sys_value', 'values': ['values_value_1', 'values_value_2']}], 'description': 'description_value', 'ins': ['ins_value_1', 'ins_value_2'], 'log_configs': [{'cloud_audit': {'authorization_logging_options': {'permission_type': 'permission_type_value'}, 'log_name': 'log_name_value'}, 'counter': {'custom_fields': [{'name': 'name_value', 'value': 'value_value'}], 'field': 'field_value', 'metric': 'metric_value'}, 'data_access': {'log_mode': 'log_mode_value'}}], 'not_ins': ['not_ins_value_1', 'not_ins_value_2'], 'permissions': ['permissions_value_1', 'permissions_value_2']}], 'version': 774}}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.set_iam_policy(request)


def test_set_iam_policy_rest_flattened():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.Policy()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.Policy.to_json(return_value)

        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value

        # get arguments that satisfy an http rule for this method
        sample_request = {'project': 'sample1', 'zone': 'sample2', 'resource': 'sample3'}

        # get truthy value for each flattened field
        mock_args = dict(
            project='project_value',
            zone='zone_value',
            resource='resource_value',
            zone_set_policy_request_resource=compute.ZoneSetPolicyRequest(bindings=[compute.Binding(binding_id='binding_id_value')]),
        )
        mock_args.update(sample_request)
        client.set_iam_policy(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("https://%s/compute/v1/projects/{project}/zones/{zone}/reservations/{resource}/setIamPolicy" % client.transport._host, args[1])


def test_set_iam_policy_rest_flattened_error(transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_iam_policy(
            compute.SetIamPolicyReservationRequest(),
            project='project_value',
            zone='zone_value',
            resource='resource_value',
            zone_set_policy_request_resource=compute.ZoneSetPolicyRequest(bindings=[compute.Binding(binding_id='binding_id_value')]),
        )


def test_set_iam_policy_rest_error():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest'
    )

@pytest.mark.parametrize("request_type", [
  compute.TestIamPermissionsReservationRequest,
  dict,
])
def test_test_iam_permissions_rest(request_type, transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    # Send a request that will satisfy transcoding
    request = compute.TestIamPermissionsReservationRequest({'project': 'sample1', 'zone': 'sample2', 'resource': 'sample3'})

    with mock.patch.object(type(client.transport._session), 'request') as req:
        return_value = compute.TestPermissionsResponse(
              permissions=['permissions_value'],
        )
        req.return_value = Response()
        req.return_value.status_code = 500
        req.return_value.request = PreparedRequest()
        json_return_value = compute.TestPermissionsResponse.to_json(return_value)
        req.return_value._content = json_return_value.encode("UTF-8")
        with pytest.raises(core_exceptions.GoogleAPIError):
            # We only care that the correct exception is raised when putting
            # the request over the wire, so an empty request is fine.
            client.test_iam_permissions(request)


@pytest.mark.parametrize("request_type", [
    compute.TestIamPermissionsReservationRequest,
    dict,
])
def test_test_iam_permissions_rest(request_type):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2', 'resource': 'sample3'}
    request_init["test_permissions_request_resource"] = {'permissions': ['permissions_value_1', 'permissions_value_2']}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.TestPermissionsResponse(
              permissions=['permissions_value'],
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.TestPermissionsResponse.to_json(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        response = client.test_iam_permissions(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, compute.TestPermissionsResponse)
    assert response.permissions == ['permissions_value']


def test_test_iam_permissions_rest_required_fields(request_type=compute.TestIamPermissionsReservationRequest):
    transport_class = transports.ReservationsRestTransport

    request_init = {}
    request_init["project"] = ""
    request_init["resource"] = ""
    request_init["zone"] = ""
    request = request_type(request_init)
    jsonified_request = json.loads(request_type.to_json(
        request,
        including_default_value_fields=False,
        use_integers_for_enums=False
        ))

    # verify fields with default values are dropped
    assert "project" not in jsonified_request
    assert "resource" not in jsonified_request
    assert "zone" not in jsonified_request

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).test_iam_permissions._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "project" in jsonified_request
    assert jsonified_request["project"] == request_init["project"]
    assert "resource" in jsonified_request
    assert jsonified_request["resource"] == request_init["resource"]
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == request_init["zone"]

    jsonified_request["project"] = 'project_value'
    jsonified_request["resource"] = 'resource_value'
    jsonified_request["zone"] = 'zone_value'

    unset_fields = transport_class(credentials=ga_credentials.AnonymousCredentials()).test_iam_permissions._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "project" in jsonified_request
    assert jsonified_request["project"] == 'project_value'
    assert "resource" in jsonified_request
    assert jsonified_request["resource"] == 'resource_value'
    assert "zone" in jsonified_request
    assert jsonified_request["zone"] == 'zone_value'

    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(request_init)

    # Designate an appropriate value for the returned response.
    return_value = compute.TestPermissionsResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "post",
                'query_params': request_init,
            }
            transcode_result['body'] = {}
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = compute.TestPermissionsResponse.to_json(return_value)
            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value

            response = client.test_iam_permissions(request)

            expected_params = [
                (
                    "project",
                    "",
                ),
                (
                    "resource",
                    "",
                ),
                (
                    "zone",
                    "",
                ),
            ]
            actual_params = req.call_args.kwargs['params']
            assert expected_params == actual_params


def test_test_iam_permissions_rest_bad_request(transport: str = 'rest', request_type=compute.TestIamPermissionsReservationRequest):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {'project': 'sample1', 'zone': 'sample2', 'resource': 'sample3'}
    request_init["test_permissions_request_resource"] = {'permissions': ['permissions_value_1', 'permissions_value_2']}
    request = request_type(request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.test_iam_permissions(request)


def test_test_iam_permissions_rest_flattened():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = compute.TestPermissionsResponse()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = compute.TestPermissionsResponse.to_json(return_value)

        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value

        # get arguments that satisfy an http rule for this method
        sample_request = {'project': 'sample1', 'zone': 'sample2', 'resource': 'sample3'}

        # get truthy value for each flattened field
        mock_args = dict(
            project='project_value',
            zone='zone_value',
            resource='resource_value',
            test_permissions_request_resource=compute.TestPermissionsRequest(permissions=['permissions_value']),
        )
        mock_args.update(sample_request)
        client.test_iam_permissions(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("https://%s/compute/v1/projects/{project}/zones/{zone}/reservations/{resource}/testIamPermissions" % client.transport._host, args[1])


def test_test_iam_permissions_rest_flattened_error(transport: str = 'rest'):
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.test_iam_permissions(
            compute.TestIamPermissionsReservationRequest(),
            project='project_value',
            zone='zone_value',
            resource='resource_value',
            test_permissions_request_resource=compute.TestPermissionsRequest(permissions=['permissions_value']),
        )


def test_test_iam_permissions_rest_error():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest'
    )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.ReservationsRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ReservationsClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.ReservationsRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ReservationsClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.ReservationsRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ReservationsClient(
            client_options={"scopes": ["1", "2"]},
            transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.ReservationsRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    client = ReservationsClient(transport=transport)
    assert client.transport is transport


@pytest.mark.parametrize("transport_class", [
    transports.ReservationsRestTransport,
])
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(google.auth, 'default') as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()


def test_reservations_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(core_exceptions.DuplicateCredentialArgs):
        transport = transports.ReservationsTransport(
            credentials=ga_credentials.AnonymousCredentials(),
            credentials_file="credentials.json"
        )


def test_reservations_base_transport():
    # Instantiate the base transport.
    with mock.patch('google.cloud.compute_v1.services.reservations.transports.ReservationsTransport.__init__') as Transport:
        Transport.return_value = None
        transport = transports.ReservationsTransport(
            credentials=ga_credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        'aggregated_list',
        'delete',
        'get',
        'get_iam_policy',
        'insert',
        'list',
        'resize',
        'set_iam_policy',
        'test_iam_permissions',
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    with pytest.raises(NotImplementedError):
        transport.close()


def test_reservations_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(google.auth, 'load_credentials_from_file', autospec=True) as load_creds, mock.patch('google.cloud.compute_v1.services.reservations.transports.ReservationsTransport._prep_wrapped_messages') as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.ReservationsTransport(
            credentials_file="credentials.json",
            quota_project_id="octopus",
        )
        load_creds.assert_called_once_with("credentials.json",
            scopes=None,
            default_scopes=(
            'https://www.googleapis.com/auth/compute',
            'https://www.googleapis.com/auth/cloud-platform',
),
            quota_project_id="octopus",
        )


def test_reservations_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(google.auth, 'default', autospec=True) as adc, mock.patch('google.cloud.compute_v1.services.reservations.transports.ReservationsTransport._prep_wrapped_messages') as Transport:
        Transport.return_value = None
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.ReservationsTransport()
        adc.assert_called_once()


def test_reservations_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, 'default', autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        ReservationsClient()
        adc.assert_called_once_with(
            scopes=None,
            default_scopes=(
            'https://www.googleapis.com/auth/compute',
            'https://www.googleapis.com/auth/cloud-platform',
),
            quota_project_id=None,
        )


def test_reservations_http_transport_client_cert_source_for_mtls():
    cred = ga_credentials.AnonymousCredentials()
    with mock.patch("google.auth.transport.requests.AuthorizedSession.configure_mtls_channel") as mock_configure_mtls_channel:
        transports.ReservationsRestTransport (
            credentials=cred,
            client_cert_source_for_mtls=client_cert_source_callback
        )
        mock_configure_mtls_channel.assert_called_once_with(client_cert_source_callback)


def test_reservations_host_no_port():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(api_endpoint='compute.googleapis.com'),
    )
    assert client.transport._host == 'compute.googleapis.com:443'


def test_reservations_host_with_port():
    client = ReservationsClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(api_endpoint='compute.googleapis.com:8000'),
    )
    assert client.transport._host == 'compute.googleapis.com:8000'


def test_common_billing_account_path():
    billing_account = "squid"
    expected = "billingAccounts/{billing_account}".format(billing_account=billing_account, )
    actual = ReservationsClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "clam",
    }
    path = ReservationsClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = ReservationsClient.parse_common_billing_account_path(path)
    assert expected == actual

def test_common_folder_path():
    folder = "whelk"
    expected = "folders/{folder}".format(folder=folder, )
    actual = ReservationsClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "octopus",
    }
    path = ReservationsClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = ReservationsClient.parse_common_folder_path(path)
    assert expected == actual

def test_common_organization_path():
    organization = "oyster"
    expected = "organizations/{organization}".format(organization=organization, )
    actual = ReservationsClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "nudibranch",
    }
    path = ReservationsClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = ReservationsClient.parse_common_organization_path(path)
    assert expected == actual

def test_common_project_path():
    project = "cuttlefish"
    expected = "projects/{project}".format(project=project, )
    actual = ReservationsClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "mussel",
    }
    path = ReservationsClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = ReservationsClient.parse_common_project_path(path)
    assert expected == actual

def test_common_location_path():
    project = "winkle"
    location = "nautilus"
    expected = "projects/{project}/locations/{location}".format(project=project, location=location, )
    actual = ReservationsClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "scallop",
        "location": "abalone",
    }
    path = ReservationsClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = ReservationsClient.parse_common_location_path(path)
    assert expected == actual


def test_client_with_default_client_info():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(transports.ReservationsTransport, '_prep_wrapped_messages') as prep:
        client = ReservationsClient(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(transports.ReservationsTransport, '_prep_wrapped_messages') as prep:
        transport_class = ReservationsClient.get_transport_class()
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)


def test_transport_close():
    transports = {
        "rest": "_session",
    }

    for transport, close_name in transports.items():
        client = ReservationsClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport
        )
        with mock.patch.object(type(getattr(client.transport, close_name)), "close") as close:
            with client:
                close.assert_not_called()
            close.assert_called_once()

def test_client_ctx():
    transports = [
        'rest',
    ]
    for transport in transports:
        client = ReservationsClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport
        )
        # Test client calls underlying transport.
        with mock.patch.object(type(client.transport), "close") as close:
            close.assert_not_called()
            with client:
                pass
            close.assert_called()
