# SPDX-License-Identifier: GPL-2.0-only

import threading

import pytest
from flask import url_for

import libeagle
from tests.simulator import eagle200sim

import json

import re

@pytest.fixture(scope="session", autouse=True)
def app():
    app = eagle200sim.create_app()
    return app


@pytest.mark.usefixtures("live_server")
class TestLiveServer:
    def test_eagle200(self):

        url = url_for("process_request", _external=True)
        port = int(re.search(":([0-9]+)/", url)[1])

        conn = libeagle.Connection("localhost", "0077dd", "6e61a3a94882eef9", port=port, debug=True)

        devices = conn.device_list()
        print(json.dumps(devices, indent=4))

        details = conn.device_details(devices["DeviceList"]["Device"]["HardwareAddress"])
        print(json.dumps(details, indent=4))

        query = conn.device_query(
            devices["DeviceList"]["Device"]["HardwareAddress"],
            details["Device"]["Components"]["Component"]["Name"],
            details["Device"]["Components"]["Component"]["Variables"]["Variable"][0],
        )

        print(json.dumps(query, indent=4))

        assert (
            query["Device"]["Components"]["Component"]["Variables"]["Variable"]["Value"] == "21.499 kW"
        )

        query = conn.device_query(devices["DeviceList"]["Device"]["HardwareAddress"])
        print(json.dumps(query, indent=4))

        for x in query["Device"]["Components"]["Component"]["Variables"]["Variable"]:
            if (x["Name"] == "zigbee:Message"):
                assert (
                    x["Value"] == "Hello, World!"
                )
