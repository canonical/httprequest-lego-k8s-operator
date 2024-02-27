#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Retrieves certificates from an ACME server using the HTTP Request dns provider."""

import logging
from typing import Dict
from urllib.parse import urlparse

from charms.lego_base_k8s.v0.lego_client import AcmeClient  # type: ignore[import]
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus

logger = logging.getLogger(__name__)


class HTTPRequestLegoK8s(AcmeClient):
    """Main class that is instantiated every time an event occurs."""

    def __init__(self, *args):
        """Uses the lego_client library to manage events."""
        super().__init__(*args, plugin="httpreq")
        self.framework.observe(self.on.config_changed, self._on_config_changed)

    @property
    def _httpreq_endpoint(self) -> str:
        """Returns HTTP Request endpoint from config."""
        return self.model.config.get("httpreq_endpoint")

    @property
    def _httpreq_mode(self) -> str:
        """Returns HTTP Request mode from config."""
        return self.model.config.get("httpreq_mode")

    @property
    def _httpreq_http_timeout(self) -> str:
        """Returns HTTP Request http timeout from config."""
        return str(self.model.config.get("httpreq_http_timeout"))

    @property
    def _httpreq_password(self) -> str:
        """Returns HTTP Request password from config."""
        return self.model.config.get("httpreq_password")

    @property
    def _httpreq_polling_interval(self) -> str:
        """Returns HTTP Request polling interval from config."""
        return str(self.model.config.get("httpreq_polling_interval"))

    @property
    def _httpreq_propagation_timeout(self) -> str:
        """Returns HTTP Request propagation timeout from config."""
        return str(self.model.config.get("httpreq_propagation_timeout"))

    @property
    def _httpreq_username(self) -> str:
        """Returns HTTP Request username from config."""
        return self.model.config.get("httpreq_username")

    @property
    def _plugin_config(self) -> Dict[str, str]:
        """Plugin specific additional configuration for the command."""
        additional_config = {
            "HTTPREQ_ENDPOINT": self._httpreq_endpoint,
        }
        if self._httpreq_http_timeout:
            additional_config["HTTPREQ_HTTP_TIMEOUT"] = self._httpreq_http_timeout
        if self._httpreq_mode:
            additional_config["HTTPREQ_MODE"] = self._httpreq_mode
        if self._httpreq_password:
            additional_config["HTTPREQ_PASSWORD"] = self._httpreq_password
        if self._httpreq_polling_interval:
            additional_config["HTTPREQ_POLLING_INTERVAL"] = self._httpreq_polling_interval
        if self._httpreq_propagation_timeout:
            additional_config["HTTPREQ_PROPAGATION_TIMEOUT"] = self._httpreq_propagation_timeout
        if self._httpreq_username:
            additional_config["HTTPREQ_USERNAME"] = self._httpreq_username
        return additional_config

    def _on_config_changed(self, _) -> None:
        """Handles config-changed events."""
        if not self._validate_httpreq_config():
            return
        if not self.validate_generic_acme_config():
            return
        self.unit.status = ActiveStatus()

    def _validate_httpreq_config(self) -> bool:
        """Checks whether required config options are set.

        Returns:
            bool: True/False
        """
        try:
            url = urlparse(self._httpreq_endpoint)
            if url.scheme not in ["http", "https"]:
                self.unit.status = BlockedStatus(
                    "HTTPREQ_ENDPOINT must be a valid HTTP or HTTPS URL."
                )
                return False
        except ValueError:
            self.unit.status = BlockedStatus("HTTPREQ_ENDPOINT must be a valid HTTP or HTTPS URL.")
            return False
        if self._httpreq_mode and self._httpreq_mode != "RAW":
            self.unit.status = BlockedStatus("HTTPREQ_MODE must be RAW or not provided.")
            return False
        return True


if __name__ == "__main__":  # pragma: nocover
    main(HTTPRequestLegoK8s)
