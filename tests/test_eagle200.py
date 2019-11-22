# SPDX-License-Identifier: GPL-2.0-only

import threading
from pprint import pprint

import pytest
from flask import url_for

import libeagle
from tests.simulator import eagle200sim


@pytest.fixture
def app():
    app = eagle200sim.create_app()
    return app


@pytest.mark.usefixtures("live_server")
class TestLiveServer:
    def test_eagle200(self):

        conn = libeagle.Connection(
            url_for("process_request", _external=True), "test", "1234"
        )

        devices = conn.device_list()
        pprint(devices)

        details = conn.device_details(devices[0]["HardwareAddress"])
        pprint(details)

        query = conn.device_query(
            details["HardwareAddress"],
            details["Components"]["Name"],
            details["Components"]["Variables"][0],
        )
        pprint(query)

        assert (
            query["Components"]["Variables"]["zigbee:InstantaneousDemand"]
            == "21.499 kW"
        )
