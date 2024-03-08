# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

import unittest

from charm import HTTPRequestLegoK8s
from ops.model import ActiveStatus, BlockedStatus
from ops.testing import Harness
from parameterized import parameterized


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(HTTPRequestLegoK8s)
        self.harness.set_can_connect("lego", True)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    def test_given_email_is_valid_when_config_changed_then_status_is_active(self):
        self.harness.update_config(
            {
                "email": "example@email.com",
                "httpreq_endpoint": "http://dummy.url.com",
            }
        )
        self.harness.evaluate_status()
        self.assertEqual(self.harness.model.unit.status, ActiveStatus())

    def test_given_email_is_invalid_when_config_changed_then_status_is_blocked(self):
        self.harness.update_config(
            {
                "email": "invalid-email",
                "httpreq_endpoint": "http://dummy.url.com",
            }
        )
        self.harness.evaluate_status()
        self.assertEqual(self.harness.model.unit.status, BlockedStatus("Invalid email address"))

    @parameterized.expand(
        [
            (
                "HTTPREQ_ENDPOINT",
                {
                    "email": "example@email.com",
                    "httpreq_endpoint": "dummy.url.com",
                },
            ),
            (
                "HTTPREQ_ENDPOINT",
                {
                    "email": "example@email.com",
                    "httpreq_endpoint": "@BADdummy",
                },
            ),
            (
                "HTTPREQ_ENDPOINT",
                {
                    "email": "example@email.com",
                    "httpreq_endpoint": "ftp://dummy.url.com",
                },
            ),
        ]
    )
    def test_given_bad_urls_when_config_changed_then_status_is_blocked(self, option, config):
        self.harness.update_config(config)
        self.harness.evaluate_status()
        self.assertEqual(
            self.harness.model.unit.status,
            BlockedStatus("HTTPREQ_ENDPOINT must be a valid HTTP or HTTPS URL."),
        )

    def test_optional_config_provided_then_status_is_active(self):
        self.harness.update_config(
            {
                "email": "example@email.com",
                "httpreq_endpoint": "http://dummy.url.com",
                "httpreq_http_timeout": 5,
                "httpreq_mode": "RAW",
                "httpreq_password": "qwerty123",
                "httpreq_polling_interval": 30,
                "httpreq_propagation_timeout": 10,
                "httpreq_username": "bob",
            }
        )
        self.harness.evaluate_status()
        self.assertEqual(self.harness.model.unit.status, ActiveStatus())

    def test_optional_config_provided_then_plugin_config_is_correct(self):
        self.harness.update_config(
            {
                "email": "example@email.com",
                "httpreq_endpoint": "http://dummy.url.com",
                "httpreq_http_timeout": 5,
                "httpreq_mode": "RAW",
                "httpreq_password": "qwerty123",
                "httpreq_polling_interval": 30,
                "httpreq_propagation_timeout": 10,
                "httpreq_username": "bob",
            }
        )
        self.harness.evaluate_status()
        self.assertEqual(
            self.harness.charm._plugin_config,
            {
                "HTTPREQ_ENDPOINT": "http://dummy.url.com",
                "HTTPREQ_HTTP_TIMEOUT": "5",
                "HTTPREQ_MODE": "RAW",
                "HTTPREQ_PASSWORD": "qwerty123",
                "HTTPREQ_POLLING_INTERVAL": "30",
                "HTTPREQ_PROPAGATION_TIMEOUT": "10",
                "HTTPREQ_USERNAME": "bob",
            },
        )

    def test_invalid_mode_config_provided_then_status_is_blocked(self):
        self.harness.update_config(
            {
                "email": "example@email.com",
                "httpreq_endpoint": "http://dummy.url.com",
                "httpreq_mode": "MAGIC",
            }
        )
        self.harness.evaluate_status()
        self.assertEqual(
            self.harness.model.unit.status,
            BlockedStatus("HTTPREQ_MODE must be RAW or not provided."),
        )
