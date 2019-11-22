# SPDX-License-Identifier: GPL-2.0-only

# from libeagle.errors import *

import urllib.parse
import urllib.request
from pprint import pprint

from lxml import etree


class Connection(object):
    def __init__(self, hostname, username, password, port=80):
        """
        This will create a connection to your eagle-200

        hostname:str        The hostname for your eagle device.
        username:str        The username to use for the connection.
        password:str        The password to use for the connection.
        """
        self._hostname = hostname
        self._username = username
        self._password = password
        self._port = port

    def setHostname(self, hostname):
        self._hostname = hostname

    def setUsername(self, username):
        self._username = username

    def setPassword(self, password):
        self._password = password

    def setPort(self, port):
        self._port = port

    hostname = property(lambda s: s._hostname, setHostname)
    username = property(lambda s: s._username, setUsername)
    password = property(lambda s: s._password, setPassword)
    port = property(lambda s: s._port, setPort)

    def device_list(self):
        """
        Returns the device list
        """

        root = etree.Element("Command")
        etree.SubElement(root, "Name").text = "device_list"
        values = etree.tostring(root)

        # print(etree.tostring(root, pretty_print=True).decode())

        req = self._getRequest(values)
        res = self._doRequest(req)
        xml = etree.fromstring(res)

        data = []
        for device in xml.iter("Device"):

            map = {
                "HardwareAddress": "",
                "Manufacturer": "",
                "ModelId": "",
                "Protocol": "",
                "LastContact": "",
                "ConnectionStatus": "",
                "NetworkAddress": "",
            }

            for key in map:
                map[key] = device.findtext(key)

            data.append(map)

        return data

    def device_details(self, address):
        """
        Returns the device details for a given hardware address

        address:str the hardware address of the device
        """

        root = etree.Element("Command")
        etree.SubElement(root, "Name").text = "device_details"
        device_details = etree.SubElement(root, "DeviceDetails")
        etree.SubElement(device_details, "HardwareAddress").text = address
        values = etree.tostring(root)

        # print(etree.tostring(root, pretty_print=True).decode())

        req = self._getRequest(values)
        res = self._doRequest(req)
        xml = etree.fromstring(res)

        # print(etree.tostring(xml, pretty_print=True).decode())

        data = {}
        for detail in xml.iter("DeviceDetails"):

            map = {
                "Name": "",
                "HardwareAddress": "",
                "Protocol": "",
                "Manufacturer": "",
                "ModelId": "",
            }

            for key in map:
                map[key] = detail.findtext(key)

            data = map

        components = xml.find("Components")
        component = components.find("Component")

        map = {"Name": "", "FixedId": ""}

        for key in map:
            map[key] = component.findtext(key)

        data["Components"] = map
        data["Components"]["Variables"] = []

        variables = component.find("Variables")
        for variable in variables.iter("Variable"):
            data["Components"]["Variables"].append(variable.text)

        return data

    def device_query(self, address, component_name, variable_name):
        """
        Returns the device query for a given hardware address, name, and variable

        address:str the hardware address of the device to query
        name:str the name of the component to query
        value:str the variable to query
        """

        root = etree.Element("Command")
        etree.SubElement(root, "Name").text = "device_query"
        device_details = etree.SubElement(root, "DeviceDetails")
        etree.SubElement(device_details, "HardwareAddress").text = address

        components = etree.SubElement(root, "Components")
        component = etree.SubElement(components, "Component")
        etree.SubElement(component, "Name").text = component_name

        variables = etree.SubElement(component, "Variables")
        variable = etree.SubElement(variables, "Variable")
        etree.SubElement(variable, "Name").text = variable_name

        # etree.SubElement(components, 'All').text = 'Y'

        values = etree.tostring(root)

        # print(etree.tostring(root, pretty_print=True).decode())

        req = self._getRequest(values)
        res = self._doRequest(req)
        xml = etree.fromstring(res)

        # print(etree.tostring(xml, pretty_print=True).decode())

        data = {}

        components = xml.find("Components")
        component = components.find("Component")

        map = {"Name": "", "FixedId": ""}

        for key in map:
            map[key] = component.findtext(key)

        data["Components"] = map

        variables = component.find("Variables")
        variable = variables.find("Variable")
        key = variable.findtext("Name")
        value = variable.findtext("Value")

        data["Components"]["Variables"] = {key: value}

        return data

    def _getRequest(self, values):
        if self._hostname.find("://") != -1:
            url = self._hostname
        else:
            url = "http://%s:%d" % (self._hostname, self._port)

        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

        password_mgr.add_password(None, url, self._username, self._password)
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(handler)
        urllib.request.install_opener(opener)

        headers = {"Content-type": "text/xml"}

        data = values
        # pprint(url)
        # pprint(data)
        # pprint(headers)
        req = urllib.request.Request(url, data, headers)

        return req

    def _doRequest(self, req):
        try:
            res = urllib.request.urlopen(req)

        except urllib.error.HTTPError as e:
            raise e

        return res.read().decode("utf-8")
