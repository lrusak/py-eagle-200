# SPDX-License-Identifier: GPL-2.0-only

import threading
from pprint import pprint

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
    def test_eagle200(self):

        url = urlsplit(url_for("process_request", _external=True))

        conn = libeagle.Connection(url.hostname, "0077dd", "6e61a3a94882eef9", port=url.port, debug=True)

        devices = conn.device_list()
        pprint(devices)

        details = conn.device_details(devices[0]["HardwareAddress"])
        pprint(details)

        query = conn.device_query(
            devices[0]["HardwareAddress"],
            details[0]["Name"],
            details[0]["Variables"][0],
        )
        pprint(query)

        assert (
            query[0]["Variables"]["zigbee:InstantaneousDemand"] == "21.499 kW"
        )

        query = conn.device_query(devices[0]["HardwareAddress"])
        pprint(query)

        assert (
            query[0]["Variables"]["zigbee:Message"] == "Hello, World!"
        )
