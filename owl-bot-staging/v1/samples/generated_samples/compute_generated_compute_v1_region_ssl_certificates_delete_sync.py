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
# Generated code. DO NOT EDIT!
#
# Snippet for Delete
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-compute


# [START compute_generated_compute_v1_RegionSslCertificates_Delete_sync]
from google.cloud import compute_v1


def sample_delete():
    # Create a client
    client = compute_v1.RegionSslCertificatesClient()

    # Initialize request argument(s)
    request = compute_v1.DeleteRegionSslCertificateRequest(
        project="project_value",
        region="region_value",
        ssl_certificate="ssl_certificate_value",
    )

    # Make the request
    response = client.delete(request=request)

    # Handle response
    print(response)

# [END compute_generated_compute_v1_RegionSslCertificates_Delete_sync]
