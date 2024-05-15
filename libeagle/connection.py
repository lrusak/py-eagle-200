# SPDX-License-Identifier: GPL-2.0-only

import aiohttp

import logging

import xml.etree.ElementTree as etree

from types import TracebackType
from typing import (
    Optional,
    Type,
)


class Connection(object):
    def __init__(self, hostname, username, password, port=80, debug=False):
        """
        This will create a connection to your eagle-200

        hostname:str        The hostname for your eagle device.
        username:str        The username to use for the connection (cloud id).
        password:str        The password to use for the connection (install code).
        port:int            The port to use for the connection (This is only needed for testing)
        debug:bool          Enable debug logging
        """

        self.logger = logging.getLogger()

        if debug:
            self.logger.setLevel(logging.DEBUG)

        url = f"http://{hostname}:{port}"

        headers = {"Content-type": "text/xml"}

        auth = aiohttp.BasicAuth(username, password)

        self.session = aiohttp.ClientSession(url, headers=headers, auth=auth)

    def __enter__(self) -> None:
        raise TypeError("Use async with instead")

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        pass

    async def __aenter__(self) -> "Connection":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.session.close()

    async def device_list(self) -> list[dict]:
        """
        Returns the device list
        """

        root = etree.Element("Command")
        etree.SubElement(root, "Name").text = "device_list"
        values = etree.tostring(root)

        self.logger.debug(f"POST data: {etree.tostring(root).decode()}")

        try:
            res = await self._doRequest(values)
        except Exception as e:
            self.logger.error(e)
            return []

        xml = etree.fromstring(res)

        self.logger.debug(f"return data: {etree.tostring(xml).decode()}")

        data = []
        for device in xml.iter("Device"):

            device_data = {detail.tag: detail.text for detail in device.iter()}
            data.append(device_data)

        return data

    async def device_details(self, address) -> dict:
        """
        Returns the device details for a given hardware address

        address:str the hardware address of the device
        """

        root = etree.Element("Command")
        etree.SubElement(root, "Name").text = "device_details"
        device_details = etree.SubElement(root, "DeviceDetails")
        etree.SubElement(device_details, "HardwareAddress").text = address
        values = etree.tostring(root)

        self.logger.debug(f"POST data: {etree.tostring(root).decode()}")

        try:
            res = await self._doRequest(values)
        except Exception as e:
            self.logger.error(e)
            return {}

        xml = etree.fromstring(res)

        self.logger.debug(f"return data: {etree.tostring(xml).decode()}")

        details = {"Components": []}

        device_details = xml.find("DeviceDetails")
        for detail in device_details.iter():
            details[detail.tag] = detail.text

        for component in xml.findall("Component"):

            component_data = {}

            for detail in component.iter():

                if detail.tag == "Variables":
                    component_data["Variables"] = []
                    for variable in component.iter():
                        component_data["Components"]["Variables"].append(variable.text)
                else:
                    component_data[detail.tag] = detail.text

                details["Components"].append(component_data)

        return details

    async def device_query(
        self, address, component_name=None, variable_name=None
    ) -> dict:
        """
        Returns the device query for a given hardware address, name, and variable

        address:str the hardware address of the device to query
        name:str [optional] the name of the component to query
        value:str [optional] the variable to query
        """

        root = etree.Element("Command")
        etree.SubElement(root, "Name").text = "device_query"
        device_details = etree.SubElement(root, "DeviceDetails")
        etree.SubElement(device_details, "HardwareAddress").text = address

        components = etree.SubElement(root, "Components")

        if component_name is None and variable_name is None:
            etree.SubElement(components, "All").text = "Y"

        elif component_name is not None and variable_name is not None:
            component = etree.SubElement(components, "Component")
            etree.SubElement(component, "Name").text = component_name

            variables = etree.SubElement(component, "Variables")
            variable = etree.SubElement(variables, "Variable")
            etree.SubElement(variable, "Name").text = variable_name

        else:
            raise Exception("Must provide name and value or neither")

        values = etree.tostring(root)

        self.logger.debug(f"POST data: {etree.tostring(root).decode()}")

        try:
            res = await self._doRequest(values)
        except Exception as e:
            self.logger.error(e)
            return []

        xml = etree.fromstring(res)

        self.logger.debug(f"return data: {etree.tostring(xml).decode()}")

        query = {"Components": []}

        device_details = xml.find("DeviceDetails")
        for detail in device_details.iter():
            query[detail.tag] = detail.text

        for component in xml.findall("Component"):

            component_data = {}

            for detail in component.iter():

                if detail.tag == "Variables":
                    component_data["Variables"] = []

                    for variable in detail.iter("Variable"):
                        key = variable.findtext("Name")
                        value = variable.findtext("Value")
                        component_data["Variables"][key] = value
                else:
                    component_data[detail.tag] = detail.text

                query["Components"].append(component_data)

        return query

    async def _doRequest(self, values) -> bytes:
        async with self.session.post("/cgi-bin/post_manager", data=values) as response:
            response.raise_for_status()

            return await response.content.read()
