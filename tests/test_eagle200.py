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

            details = await conn.device_details(devices[0]["HardwareAddress"])

            query = await conn.device_query(
                devices[0]["HardwareAddress"],
                details[0]["Name"],
                details[0]["Variables"][0],
            )

            assert (
                query[0]["Variables"]["zigbee:InstantaneousDemand"] == "21.499 kW"
            )

            query = await conn.device_query(devices[0]["HardwareAddress"])

            assert (
                query[0]["Variables"]["zigbee:Message"] == "Hello, World!"
            )
