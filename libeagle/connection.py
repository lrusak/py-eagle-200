# SPDX-License-Identifier: GPL-2.0-only

# from libeagle.errors import *

import urllib.parse
import urllib.request

import logging

import xml.etree.ElementTree as etree

logger = logging.getLogger()

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
        self._hostname = hostname
        self._username = username
        self._password = password
        self._port = port

        global logger

        logger.setLevel(logging.DEBUG) if debug else logger.setLevel(logging.INFO)
        self._debug = debug
        self._url = self._getUrl()
        self._opener = self._getOpener()

    def setHostname(self, hostname):
        self._hostname = hostname
        self._url = self._getUrl()
        self._opener = self._getOpener()

    def setUsername(self, username):
        self._username = username
        self._opener = self._getOpener()

    def setPassword(self, password):
        self._password = password
        self._opener = self._getOpener()

    def setPort(self, port):
        self._port = port
        self._url = self._getUrl()
        self._opener = self._getOpener()

    def setDebug(self, debug):
        logger.setLevel(logging.DEBUG) if debug else logger.setLevel(logging.INFO)
        self._debug = debug

    hostname = property(lambda s: s._hostname, setHostname)
    username = property(lambda s: s._username, setUsername)
    password = property(lambda s: s._password, setPassword)
    port = property(lambda s: s._port, setPort)
    debug = property(lambda s: s._debug, setDebug)

    def device_list(self):
        """
        Returns the device list
        """

        root = etree.Element("Command")
        etree.SubElement(root, "Name").text = "device_list"
        values = etree.tostring(root)

        logger.debug(f"POST data: {etree.tostring(root).decode()}")

        req = self._getRequest(values)
        res = self._doRequest(req)
        xml = etree.fromstring(res)

        logger.debug(f"return data: {etree.tostring(xml).decode()}")

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

        logger.debug(f"POST data: {etree.tostring(root).decode()}")

        req = self._getRequest(values)
        res = self._doRequest(req)
        xml = etree.fromstring(res)

        logger.debug(f"return data: {etree.tostring(xml).decode()}")

        '''
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
        '''
        data = []
        components = xml.find("Components")
        for component in components.iter("Component"):

            map = {"Name": "", "FixedId": ""}

            for key in map:
                map[key] = component.findtext(key)

            map["Variables"] = []

            variables = component.find("Variables")
            for variable in variables.iter("Variable"):
                map["Variables"].append(variable.text)

            data.append(map)

        return data

    def device_query(self, address, component_name=None, variable_name=None):
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
            etree.SubElement(components, 'All').text = 'Y'

        elif component_name is not None and variable_name is not None:
            component = etree.SubElement(components, "Component")
            etree.SubElement(component, "Name").text = component_name

            variables = etree.SubElement(component, "Variables")
            variable = etree.SubElement(variables, "Variable")
            etree.SubElement(variable, "Name").text = variable_name

        else:
            raise Exception("Must provide name and value or neither")

        values = etree.tostring(root)

        logger.debug(f"POST data: {etree.tostring(root).decode()}")

        req = self._getRequest(values)
        res = self._doRequest(req)
        xml = etree.fromstring(res)

        logger.debug(f"return data: {etree.tostring(xml).decode()}")

        data = []

        components = xml.find("Components")
        for component in components.iter("Component"):

          map = { "Name": "", "FixedId": "" }

          for key in map:
              map[key] = component.findtext(key)

          variables = component.find("Variables")
          map["Variables"] = {}

          for variable in variables.iter("Variable"):
              key = variable.findtext("Name")
              value = variable.findtext("Value")

              map["Variables"][key] = value

          data.append(map)

        return data

    def _getUrl(self):
        url = "http://%s:%d/cgi-bin/post_manager" % (self._hostname, self._port)

        logger.debug(f"URL: {url}")

        return url

    def _getOpener(self):
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

        password_mgr.add_password(None, self._url, self._username, self._password)
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

        opener = urllib.request.build_opener(handler)
        urllib.request.install_opener(opener)

        return opener

    def _getRequest(self, values):
        headers = {"Content-type": "text/xml"}

        logger.debug(f"data: {values.decode()}")

        req = urllib.request.Request(self._url, values, headers)

        logger.debug(f"custom headers: {req.headers}")

        return req

    def _doRequest(self, req):
        try:
            res = self._opener.open(req)
            logger.debug(f"default headers: {req.unredirected_hdrs}")

        except urllib.error.HTTPError as e:
            raise e

        return res.read().decode()

