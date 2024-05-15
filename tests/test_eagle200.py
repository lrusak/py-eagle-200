# SPDX-License-Identifier: GPL-2.0-only

import pytest
from flask import url_for

import libeagle
from tests.simulator import eagle200sim

from urllib.parse import urlsplit

@pytest.fixture(scope="session", autouse=True)
def app():
    app = eagle200sim.create_app()
    return app


@pytest.mark.usefixtures("live_server")
class TestLiveServer:

    @pytest.mark.asyncio
    async def test_eagle200(self):

        url = urlsplit(url_for("process_request", _external=True))

        async with libeagle.Connection(url.hostname, "0077dd", "6e61a3a94882eef9", port=url.port, debug=True) as conn:

            devices = await conn.device_list()

            assert len(devices) > 0

            for device in devices:
                assert "HardwareAddress" in device

                details = await conn.device_details(device["HardwareAddress"])

                assert len(details) > 0

                assert "Name" in details
                assert "HardwareAddress" in details
                assert "Components" in details

                for detail in details["Components"]:
                    assert "Name" in detail
                    assert "Variables" in detail
                    assert len(detail["Variables"]) > 0
                    assert "zigbee:InstantaneousDemand" in detail["Variables"]

                    query = await conn.device_query(
                        device["HardwareAddress"],
                        detail["Name"],
                        "zigbee:InstantaneousDemand",
                    )

                    assert len(query) > 0
                    assert "Name" in query
                    assert "HardwareAddress" in query
                    assert "Components" in query

                    for component in query["Components"]:

                        assert "Variables" in component
                        assert "zigbee:InstantaneousDemand" in component["Variables"]

                        assert (
                            component["Variables"]["zigbee:InstantaneousDemand"] == "21.499 kW"
                        )

                query = await conn.device_query(device["HardwareAddress"])

                assert len(query) > 0
                assert "Name" in query
                assert "HardwareAddress" in query
                assert "Components" in query

                for component in query["Components"]:

                    assert "Variables" in component
                    assert "zigbee:Message" in component["Variables"]

                    assert (
                        component["Variables"]["zigbee:Message"] == "Hello, World!"
                    )
