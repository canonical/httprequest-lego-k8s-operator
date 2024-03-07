#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.


import logging
from pathlib import Path

import pytest
import yaml
from pytest_operator.plugin import OpsTest

logger = logging.getLogger(__name__)

METADATA = yaml.safe_load(Path("./metadata.yaml").read_text())
APP_NAME = METADATA["name"]

TLS_REQUIRER_CHARM_NAME = "tls-certificates-requirer"
GRAFANA_AGENT_CHARM_NAME = "grafana-agent-k8s"


async def deploy_grafana_agent(ops_test: OpsTest):
    """Deploy grafana agent charm."""
    assert ops_test.model
    await ops_test.model.deploy(
        GRAFANA_AGENT_CHARM_NAME,
        application_name=GRAFANA_AGENT_CHARM_NAME,
        channel="stable",
    )


@pytest.fixture(scope="module")
@pytest.mark.abort_on_fail
async def build_and_deploy(ops_test: OpsTest):
    """Build the charm-under-test and deploy it."""
    charm = await ops_test.build_charm(".")
    resources = {"lego-image": METADATA["resources"]["lego-image"]["upstream-source"]}
    assert ops_test.model
    await ops_test.model.deploy(
        charm,
        resources=resources,
        application_name=APP_NAME,
        series="jammy",
        config={
            "email": "example@email.com",
            "httpreq_endpoint": "http://dummy.url.com",
        },
    )
    await ops_test.model.deploy(
        TLS_REQUIRER_CHARM_NAME,
        application_name=TLS_REQUIRER_CHARM_NAME,
        channel="edge",
    )


@pytest.mark.abort_on_fail
async def test_given_charm_is_built_when_deployed_then_status_is_active(
    ops_test: OpsTest,
    build_and_deploy,
):
    assert ops_test.model
    await ops_test.model.wait_for_idle(
        apps=[APP_NAME],
        status="active",
        timeout=1000,
    )


@pytest.mark.xfail(
    reason="The charm will fail requesting a certificate from the ACME server, \
        because http_req is invalid and will be blocked."
)
async def test_given_tls_requirer_is_deployed_and_related_then_status_is_active(
    ops_test: OpsTest,
    build_and_deploy,
):
    assert ops_test.model
    await ops_test.model.integrate(
        relation1=f"{APP_NAME}:certificates", relation2=f"{TLS_REQUIRER_CHARM_NAME}"
    )
    await ops_test.model.wait_for_idle(
        apps=[APP_NAME],
        status="active",
        timeout=1000,
    )


async def test_given_grafana_agent_when_integrate_then_status_is_active(
    ops_test: OpsTest,
    build_and_deploy,
):
    await deploy_grafana_agent(ops_test)
    assert ops_test.model
    await ops_test.model.integrate(
        relation1=f"{APP_NAME}:logging", relation2=GRAFANA_AGENT_CHARM_NAME
    )
    await ops_test.model.wait_for_idle(
        apps=[APP_NAME],
        status="active",
        timeout=1000,
    )
