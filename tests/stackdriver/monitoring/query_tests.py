# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.

from __future__ import absolute_import
import datetime
import mock
import unittest

from google.cloud.monitoring_v3.query import Query as BaseQuery

import google.auth
import google.datalab
import google.datalab.stackdriver.monitoring as gcm


PROJECT = 'my-project'
METRIC_TYPE = 'compute.googleapis.com/instance/cpu/utilization'
RESOURCE_TYPE = 'gce_instance'
INSTANCE_NAMES = ['instance-1', 'instance-2']
INSTANCE_ZONES = ['us-east1-a', 'us-east1-b']
INSTANCE_IDS = ['1234567890123456789', '9876543210987654321']


class TestCases(unittest.TestCase):

  def setUp(self):
    creds = mock.Mock(spec=google.auth.credentials.Credentials)
    self.context = google.datalab.Context(PROJECT, creds)

  @mock.patch('google.datalab.Context.default')
  def test_constructor_minimal(self, mock_context_default):
    mock_context_default.return_value = self.context

    query = gcm.Query()

    self.assertEqual(query._filter.metric_type, BaseQuery.DEFAULT_METRIC_TYPE)

    self.assertIsNone(query._start_time)
    self.assertIsNone(query._end_time)

    self.assertEqual(query._per_series_aligner, 0)
    self.assertEqual(query._alignment_period_seconds, 0)
    self.assertEqual(query._cross_series_reducer, 0)
    self.assertEqual(query._group_by_fields, ())

  def test_constructor_maximal(self):
    UPTIME_METRIC = 'compute.googleapis.com/instance/uptime'
    T1 = datetime.datetime(2016, 4, 7, 2, 30, 30)
    DAYS, HOURS, MINUTES = 1, 2, 3
    T0 = T1 - datetime.timedelta(days=DAYS, hours=HOURS, minutes=MINUTES)

    query = gcm.Query(UPTIME_METRIC,
                      end_time=T1, days=DAYS, hours=HOURS, minutes=MINUTES,
                      context=self.context)

    self.assertEqual(query._filter.metric_type, UPTIME_METRIC)

    self.assertEqual(query._start_time, T0)
    self.assertEqual(query._end_time, T1)

    self.assertEqual(query._per_series_aligner, 0)
    self.assertEqual(query._alignment_period_seconds, 0)
    self.assertEqual(query._cross_series_reducer, 0)
    self.assertEqual(query._group_by_fields, ())

  @mock.patch('google.datalab.stackdriver.monitoring.Query.iter')
  def test_metadata(self, mock_query_iter):
    query = gcm.Query(METRIC_TYPE, hours=1, context=self.context)
    query_metadata = query.metadata()

    mock_query_iter.assert_called_once_with(headers_only=True)
    self.assertIsInstance(query_metadata, gcm.QueryMetadata)
    self.assertEqual(query_metadata.metric_type, METRIC_TYPE)
